from __future__ import annotations

import logging
import os
import time

import h5py
import numpy as np
import scipy.interpolate as intp
import radiotools.helper as hp

from radiotools.atmosphere.models import Atmosphere

from .io import Shower, SlicedShower
from .utilities import angle_between
from smiet import units


def amplitude_function(params, frequencies, d_noise=0.0):
    """
    Calculate the amplitude frequency spectrum corresponding to the parameters ``params``.

    Parameters
    ----------
    params : np.ndarray or list
        The spectral parameters. If it is a multidimensional array, the first dimension must contain the parameters.
    frequencies : np.ndarray
        The values of the frequencies to evaluate in MHz - remove central frequency beforehand!
    d_noise : float, default=0.0
        The noise floor level

    Returns
    -------
    The evaluated amplitude frequency spectrum
    """
    if len(params.shape) == 1:
        params = params.reshape((params.shape[0], 1))
    return params[0][:, np.newaxis] * np.exp(
        params[1][:, np.newaxis] * frequencies[np.newaxis, :] +
        params[2][:, np.newaxis] * frequencies[np.newaxis, :] ** 2
    ) + d_noise


class SliceSynthesis:
    """
    This class represents a single slice in the atmosphere in the template synthesis framework.

    Typically, the grammage value of the slice is set to be the grammage at the bottom of the slice.

    Parameters
    ----------
    slice_grammage : int
        The value of this slice, in g/cm2
    ce_linear : bool, default=True
        If True, use the linear variant for the CE corrections

    Attributes
    ----------
    grammage : int
        The grammage of the slice
    ce_linear : bool
        Whether to use the linear variant of the CE corrections

    Notes
    -----
    This class is prone to removal in other versions of the software, so users are discouraged
    to interact with it directly. Instead, users are encouraged to interface with slices through
    the :obj:`TemplateSynthesis` class, whose functionality is more stable.
    """

    def __init__(self, slice_grammage, ce_linear=True):
        self.logger = logging.getLogger("smiet.numpy.synthesis.SliceSynthesis")
        self.grammage = int(slice_grammage)  # g/cm2
        self.ce_linear = ce_linear

        # Internal variables
        self.__ant = None

        # Variables shared with other slices
        self._ant_info = None
        self._atm = None

        self._v_angles = None
        self._geo = None
        self._ce = None
        self._ce_lin = None

        self._frequencies = None
        self._frequency_range = None

    @property
    def antenna_parameters(self):
        """
        Dictionary containing the antenna properties relating to the slice.
        The keys are:

        * 'amplitude_geo' : the normalised geomagnetic amplitude spectrum
        * 'phase_geo' : the phase spectrum of the geomagnetic component
        * 'amplitude_ce' : the normalised charge-excess amplitude spectrum
        * 'phase_ce' : the phase spectrum of the charge-excess component
        * 'distance' : the distance of the antenna to the slice
        * 'viewing_angle' : the viewing angle of the antenna with respect to the slice
        """
        return self.__ant

    def _calculate_distance_viewing_angle(self, zenith, azimuth, core=np.array([0, 0, 0])):
        """
        Calculate the viewing angles of the saved antenna's with respect to the slice,
        as well as their distance to this slice. These are saved in the ``antenna_parameters`` attribute.

        Parameters
        ----------
        zenith : float
        azimuth : float
        core : np.ndarray, default=np.array([0, 0, 0])
        """
        d_xmax = self._atm.get_distance_xmax_geometric(
            zenith / units.rad, self.grammage, observation_level=core[2] / units.m
        ) * units.m

        unit_shower_axis = hp.spherical_to_cartesian(zenith / units.rad, azimuth / units.rad)
        slice_vector = unit_shower_axis * d_xmax

        slice_to_ant_vector = self._ant_info['position'] - (slice_vector + core)

        self.__ant['viewing_angle'] = (
                angle_between(slice_to_ant_vector, -1 * slice_vector) / self._calculate_cherenkov_angle(zenith)
        )
        self.__ant['distance'] = np.linalg.norm(slice_to_ant_vector, axis=-1)

    def _calculate_density_slice(self, zenith):
        """
        Calculate the atmospheric density in this slice given a zenith angle

        Parameters
        ----------
        zenith : float
            The zenith angle of the shower

        Returns
        -------
        density : float
            The density in g/cm3
        """
        return self._atm.get_density(zenith / units.rad, self.grammage)

    def _calculate_cherenkov_angle(self, zenith):
        """
        Calculate the local Cherenkov angle of the slice, using the refractive index, given a zenith angle.

        This function first calculates the height of the slice, and then uses the refractive index to calculate
        the local Cherenkov angle as

        .. math::
            \\theta_{\\text{Cherenkov}} = \\arccos\\left(\\frac{1}{n}\\right)

        Parameters
        ----------
        zenith : float
            The zenith angle of the shower

        Returns
        -------
        cherenkov_angle : float
            The Cherenkov angle (in internal units)
        """
        height_slice = self._atm.get_vertical_height(
            zenith / units.rad, self.grammage
        )

        return np.arccos(1 / self._atm.get_n(height_slice)) * units.rad

    def get_spectra(self, delta_xmax, freq):
        """
        Retrieve the amplitude spectra at the specified frequencies, for a given :math:`\\Delta X_{max}` .

        Parameters
        ----------
        delta_xmax : float
            The difference between the grammage of the slice and the shower :math:`X_{max}`.
        freq : np.ndarray
            The list of frequencies at which to evaluate the spectra

        Returns
        -------
        spectrum_geo : np.ndarray
            The evaluated geomagnetic amplitude frequency spectrum, shaped as (# viewing angles, # freq).
        spectrum_ce : np.ndarray
            The charge-excess spectrum
        spectrum_ce_lin : np.ndarray
            The charge-excess spectrum, but evaluated without the quadratic (``c``) component.
        """
        spectral_params_geo = np.polynomial.polynomial.polyval(delta_xmax, self._geo.T)  # 3 x viewing angles
        spectral_params_ce = np.polynomial.polynomial.polyval(delta_xmax, self._ce.T)
        spectral_params_ce_lin = np.polynomial.polynomial.polyval(delta_xmax, self._ce_lin.T)

        return (amplitude_function(spectral_params_geo, freq / units.MHz),
                amplitude_function(spectral_params_ce, freq / units.MHz),
                amplitude_function(spectral_params_ce_lin, freq / units.MHz))

    def create_interpolators(self, shower: Shower, frequencies):
        """
        Interpolate the correction factors to the amplitude spectrum at each frequency given in ``frequencies``.
        Depending on the value of the :py:attr:`SliceSynthesis.ce_linear` attribute, this method will interpolate
        either use the charge-excess spectra without the quadratic term (if True),
        or the full log-parabolic spectra (if False).

        Parameters
        ----------
        shower : smiet.numpy.io.Shower
            The Shower from which to use the parameters to evaluate the amplitude frequency spectra
        frequencies : np.ndarray
            The frequencies at which to evaluate the spectra, where the central frequency has already been removed

        Returns
        -------
        interpolator_geo : scipy.interpolate.interp1d
            Interpolator object for the geomagnetic component
        interpolator_ce : scipy.interpolate.interp1d
            Interpolator object for the charge-excess component
        """
        # We have our viewing angles. We need to make the coefficients that correspond to this imaginary antennas
        delta_xmax_origin = self.grammage - shower.xmax

        all_geo_correction = np.ones((len(self._v_angles), len(frequencies)))
        all_ce_correction = np.ones((len(self._v_angles), len(frequencies)))

        geo_origin, ce_origin, ce_lin_origin = self.get_spectra(delta_xmax_origin, frequencies)

        all_geo_correction /= np.where(np.abs(geo_origin) <= 1e-20, 1., geo_origin)

        if not self.ce_linear:
            all_ce_correction /= np.where(np.abs(ce_origin) <= 1e-20, 1., ce_origin)
        else:
            all_ce_correction /= np.where(np.abs(ce_lin_origin) <= 1e-20, 1., ce_lin_origin)

        return [
            intp.interp1d(
                self._v_angles[:-2], corr[:-2], axis=0,
                kind='linear', fill_value=(corr[0], corr[-3]), bounds_error=False  # assumes viewing angles are sorted!
            )
            for corr in [all_geo_correction, all_ce_correction]
        ]

    # noinspection PyTypeChecker
    def make_template(self, origin: SlicedShower):
        """
        Process a ``SlicedShower`` into a template.

        Parameters
        ----------
        origin : smiet.numpy.io.SlicedShower
            The origin shower
        """
        freq_range = np.logical_and(
            self._frequency_range[0] <= self._frequencies, self._frequencies <= self._frequency_range[1]
        )

        # Generate interpolators
        interpolators = self.create_interpolators(origin, self._frequencies[freq_range] - self._frequency_range[2])

        # Create antenna array for slice specific properties
        self.__ant = np.zeros(
            len(origin.antenna_names),
            dtype=np.dtype([
                ('amplitude_geo', 'f8', len(self._frequencies)),
                ('phase_geo', 'f8', len(self._frequencies)),
                ('amplitude_ce', 'f8', len(self._frequencies)),
                ('phase_ce', 'f8', len(self._frequencies)),
                ('distance', 'f4'),
                ('viewing_angle', 'f4'),
            ])
        )

        # Put the values from the origin in
        self._calculate_distance_viewing_angle(origin.zenith, origin.azimuth, core=origin.core)

        # Get normalisation coefficients
        geo_factor, ce_factor = self.get_normalisation_factors(origin)
        # -- if the slice has too few particles, don't process further
        if geo_factor == 0:
            return

        # TODO: can this be done without for-loop?
        for ind, ant in enumerate(self.__ant):
            geo_origin, ce_origin, start_origin = origin.get_trace_slice(
                self._ant_info[ind]['name'], self.grammage, return_start_time=True
            )

            geo = np.fft.rfft(geo_origin, norm='ortho')
            ce = np.fft.rfft(ce_origin, norm='ortho')

            geo /= geo_factor
            geo *= ant['distance']

            geo_correction = np.zeros_like(self._frequencies)
            geo_correction[freq_range] = interpolators[0](ant['viewing_angle'])

            ce /= ce_factor
            ce *= ant['distance']

            ce_correction = np.zeros_like(self._frequencies)
            ce_correction[freq_range] = interpolators[1](ant['viewing_angle'])

            ant['amplitude_geo'] = np.abs(geo) * geo_correction
            ant['phase_geo'] = np.angle(geo)

            ant['amplitude_ce'] = np.abs(ce) * ce_correction
            ant['phase_ce'] = np.angle(ce)

        # Adjust the phases such that the peak is at sample 0
        phase_adjustments = self.calculate_geometry_phase_shift(origin)
        self.__ant['phase_geo'] += phase_adjustments
        self.__ant['phase_ce'] += phase_adjustments

    def get_normalisation_factors(self, shower: Shower):
        """
        Calculate the template synthesis normalisation factors, to remove geometric and
        shower parameter dependencies.

        Parameters
        ----------
        shower : smiet.numpy.io.Shower
            The shower for which to calculate the normalisation factors.

        Returns
        -------
        geo_factor : float
            The normalisation factor for the geomagnetic component.
        ce_factor : float
            The normalisation factor for the charge-excess component.
        """
        j = int(self.grammage // shower.slice_grammage - 1)

        # -- particles in slice
        n_slice = shower.long[j, 1]

        # -- check if enough particles in the slice
        if n_slice < 0.001 * shower.nmax:
            self.logger.info(f"Slice at {self.grammage} g/cm2 contains too few particles, not using this one...")
            return 0, 0

        # -- geomagnetic angle
        geo_angle_origin = shower.geomagnetic_angle / units.rad

        # -- density slice
        density_slice_origin = self._calculate_density_slice(shower.zenith)
        # -- cherenkov angle of slice
        cherenkov_angle_origin = self._calculate_cherenkov_angle(shower.zenith) / units.rad

        geo_factor = (n_slice * np.sin(geo_angle_origin) / density_slice_origin)
        ce_factor = (n_slice * np.sin(cherenkov_angle_origin))

        return geo_factor, ce_factor

    def map_template(self, target: Shower):
        """
        Map the template to a target profile, represented in a target :obj:`Shower`.

        Calculates the trace for every antenna present in the template.
        The antennas are contained in the first dimension of the returned arrays.

        Parameters
        ----------
        target : smiet.numpy.io.Shower
            The target Shower object, containing the longitudinal profile

        Returns
        -------
        synthesised_geo : np.ndarray
            The geomagnetic trace for each antenna
        synthesised_ce : np.ndarray
            The charge-excess trace for each antenna

        """
        # Get valid frequency range
        freq_range = np.logical_and(
            self._frequency_range[0] <= self._frequencies, self._frequencies <= self._frequency_range[1]
        )

        # Generate interpolators
        interpolators = self.create_interpolators(target, self._frequencies[freq_range] - self._frequency_range[2])

        # Update antenna distances and viewing angles, assuming _ant_info['positions'] have been updated already
        self._calculate_distance_viewing_angle(target.zenith, target.azimuth, core=target.core)

        # Find phase adjustments for target geometry (this might roll over the pulse to the other side)
        phase_adjustments = self.calculate_geometry_phase_shift(target)

        # Correction factors based on target properties
        geo_factor, ce_factor = self.get_normalisation_factors(target)

        synthesised_geo = np.zeros((len(self.__ant), len(self._ant_info[0]['time_axis'])))
        synthesised_ce = np.zeros((len(self.__ant), len(self._ant_info[0]['time_axis'])))
        # TODO: can this be done without for-loop?
        for i, ant in enumerate(self.__ant):
            geo_abs, geo_phase = np.copy(ant['amplitude_geo']), np.copy(ant['phase_geo'])
            ce_abs, ce_phase = np.copy(ant['amplitude_ce']), np.copy(ant['phase_ce'])

            geo_phase -= phase_adjustments[i]
            ce_phase -= phase_adjustments[i]

            geo_correction = np.zeros_like(self._frequencies)
            geo_correction[freq_range] = interpolators[0](ant['viewing_angle'])

            geo_abs *= geo_factor
            geo_abs /= ant['distance']
            geo_abs /= np.where(geo_correction == 0, 1, geo_correction)  # avoid division by zero

            ce_correction = np.zeros_like(self._frequencies)
            ce_correction[freq_range] = interpolators[1](ant['viewing_angle'])

            ce_abs *= ce_factor
            ce_abs /= ant['distance']
            ce_abs /= np.where(ce_correction == 0, 1, ce_correction)

            synthesised_geo[i] = np.fft.irfft(geo_abs * np.exp(1j * geo_phase), norm='ortho')
            synthesised_ce[i] = np.fft.irfft(ce_abs * np.exp(1j * ce_phase), norm='ortho')

        return synthesised_geo, synthesised_ce

    def calculate_arrival_time(self, shower: Shower):
        """
        Calculate the expected arrival time in each loaded antenna, given a shower geometry.

        The antenna positions are calculated based on the loaded shower plane positions.
        These are projected to ground using the transformer from the provided `shower`.

        Parameters
        ----------
        shower: smiet.numpy.io.Shower
            The shower containing the geometry

        Returns
        -------
        observation_time : np.ndarray
            The arrival time (in internal units) in each antenna, shaped as (n_ant,)

        Notes
        -----
        The arrival time of the signal at an antenna depends both on the time it was emitted,
        which relates to the distance :math:`D` between the slice and the antenna, as well as
        the travel time of the radio signal :math:`L` from the slice to the antenna.

        .. math::
            t_{obs} = \\frac{ L \\times n - D }{ c }

        Because the shower front travels at nearly the speed of light, we do not need to correct
        the emission time :math:`D / c` with the index of refraction.
        """
        from scipy.constants import c as c_vacuum
        c = c_vacuum * units.m / units.s

        # Distance from slice to ground
        emission_distance = shower.atmosphere.get_distance_xmax_geometric(
            shower.zenith / units.rad, self.grammage, observation_level=shower.core[2] / units.m
        ) * units.m

        # Convert distance to vector pointing from core to slice
        slice_vector = shower.core + hp.spherical_to_cartesian(
            shower.zenith / units.rad, shower.azimuth / units.rad
        ) * emission_distance

        # Transform positions from shower plane
        ant_pos_ground = shower.get_transformer().transform_from_vxB_vxvxB_2D(
            self._ant_info['position_showerplane'], core=shower.core
        )

        # For every antenna, calculate the observation time = (slice_ant_distance * n_eff - emission_distance) / c
        observation_time = np.zeros_like(self._ant_info['name'], dtype=float)
        for idx, ant_pos in enumerate(ant_pos_ground):
            travel_distance = np.linalg.norm(slice_vector - ant_pos)
            travel_distance *= 1 + shower.atmosphere.get_effective_refractivity(
                shower.zenith / units.rad, emission_distance, ant_pos[2]
            )[0]

            observation_time[idx] = (travel_distance - emission_distance) / c

        return observation_time

    def calculate_geometry_phase_shift(self, shower: Shower):
        """
        Adjust the phase of the template to match the phase of the target geometry.

        Parameters
        ----------
        shower: smiet.numpy.io.Shower

        Returns
        -------
        phase_correction : np.ndarray
            The phase correction for each antenna, shaped as (n_ant, n_freq)
        """
        obs_time_difference = self.calculate_arrival_time(shower)
        phase_correction = 2 * np.pi * self._frequencies[np.newaxis, :] * obs_time_difference[:, np.newaxis]

        return phase_correction

    def serialise(self):
        """
        Prepare the slice to be saved to disk, collecting the necessary information into a dictionary.

        Returns
        -------
        data : dict
            The dictionary containing the necessary data to reconstruct the slice
        """
        data = {
            "ant": self.__ant,
            "slice_grammage": self.grammage,
            "ce_linear": self.ce_linear,
        }
        return data

    def deserialise(self, data_dict):
        """
        Create the instance from saved data dictionary, as produced by `serialise`.

        Parameters
        ----------
        data_dict : dict
            The data dictionary
        """
        self.__ant = data_dict['ant']
        self.grammage = data_dict['slice_grammage']
        self.ce_linear = data_dict['ce_linear']


class TemplateSynthesis:
    """
    This class is the main interface for synthesising pulses.

    The main workflow consists of creating an instance and reading in the spectral parameters
    from a particular file.
    Then one can pass a ``SlicedShower`` as an origin to the :meth:`TemplateSynthesis.make_template`
    method, which construct all the necessary arrays to perform the synthesis.
    To perform the synthesis, you then call the :meth:`TemplateSynthesis.map_template` method with a
    ``Shower`` instance, which should be equipped with a longitudinal profile and the parameters
    from the Gaisser-Hillas fit.

    Parameters
    ----------
    freq_ar : list, default=None
        If not None, the spectral file with the numbers corresponding to the first, second and
        third element of the list will be read in during initialisation.


    Attributes
    ----------
    has_spectral_coefficients : bool
        Whether the spectral coefficients have been loaded
    geo : np.ndarray
        The spectral coefficients for the geomagnetic component
    ce : np.ndarray
        The spectral coefficients for the charge-excess component
    ce_lin : np.ndarray
        The spectral coefficients for the charge-excess component, but without the quadratic parameter
    atm : radiotools.atmosphere.models.Atmosphere
        The atmosphere model from the origin shower, used to make the template
    viewing_angles : np.ndarray
        The viewing angles (in units of Cherenkov angle) for which we have the spectral coefficients
    frequencies : np.ndarray
        The frequencies corresponding to the Fourier transform of the origin
    frequency_range : tuple of float
        The minimum, maximum and central frequency for which the spectral parameters where fitted.
        This is read from the HDF5 file containing the spectral parameters.
    antenna_information : np.ndarray
        The antenna information, containing the time axis, position and name of each antenna
    template_information : dict
        The information about the template, such as the name, geometry, magnetisation, :math:`X_{max}`, core and creation time
    slices : list
        The list of slices in the template, each as a :obj:`SliceSynthesis` object
    slices_grammage : list
        The grammage at the bottom of each slice

    Notes
    -----
    It is implicitly assumed that the origin shower's longitudinal profile is sampled with the same step
    size as the antennas are configured to observe (i.e. if the antennas are set up to observer slices
    with a thickness of 5 g/cm2, the longitudinal profile should also be sampled with a step size of
    5 g/cm2 - which is set using the LONGI keyword in the CORSIKA input file).
    """

    def __init__(self, freq_ar: list = None) -> None:
        self.logger = logging.getLogger("smiet.numpy.synthesis.TemplateSynthesis")

        self.has_spectral_coefficients = None
        self.geo = None
        self.ce = None
        self.ce_lin = None

        self.atm = None
        self.viewing_angles = None
        self.frequency_range = None
        self.frequencies = None

        self.antenna_information = None
        self.template_information = None

        self.slices = []
        self.slices_grammage = []  # stores the grammages at the bottom of each slice

        if freq_ar is not None:
            spectral_filename = f'spectral_parameters_{int(freq_ar[0])}_{int(freq_ar[1])}_{int(freq_ar[2])}.hdf5'
            self.read_spectral_file(spectral_filename)

    def read_spectral_file(self, filename):
        """
        Read spectral parameters from a file with `filename` in the spectral_parameters/ directory.

        Parameters
        ----------
        filename : str
           The name of the spectral parameters file
        """
        path_to_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spectral_parameters', filename)

        if not os.path.exists(path_to_file):
            raise FileNotFoundError(
                f"Filename {filename} does not exist in the spectral_parameters/ directory."
                f"Did you provide the correct frequency range?"
            )

        with h5py.File(path_to_file) as spectral_file:
            self.viewing_angles = spectral_file['/Metadata/ViewingAngles'][:]
            self.frequency_range = tuple(spectral_file['/Metadata/Frequency_MHz'][:] * units.MHz)

            self.geo = spectral_file['SpectralFitParams/GEO'][:]
            self.ce = spectral_file['SpectralFitParams/CE'][:]
            self.ce_lin = spectral_file['SpectralFitParams/CE_LIN'][:]

            self.has_spectral_coefficients = True

        self.logger.debug(f"Loaded in the spectral coefficients from {filename}")

    def make_template(self, origin: SlicedShower, ce_linear=True):
        """
        Process a ``SlicedShower`` into a template.

        Parameters
        ----------
        origin : smiet.numpy.io.SlicedShower
            The origin shower
        ce_linear : bool, default=True
            Whether to use linear variant of the CE component correction
        """
        if not self.has_spectral_coefficients:
            raise RuntimeError("Please make sure the spectral coefficients are loaded before making a template")

        self.atm = origin.atmosphere  # get the Atmosphere from the shower
        if self.atm is None:
            raise RuntimeError(
                "The origin shower does not have an atmosphere set, cannot make template! "
                "Please set your own Atmosphere object to the origin shower before synthesising."
            )

        self.template_information = {
            "name": origin.name,
            "geometry": origin.geometry,
            "magnet": origin.magnet,
            "xmax": origin.xmax,
            "core": origin.core,
            "creation": time.asctime()
        }

        self.antenna_information = np.zeros(
            len(origin.antenna_names),
            dtype=np.dtype([
                ('time_axis', 'f8', origin.trace_length),
                ('position', 'f8', 3),
                ('position_showerplane', 'f8', 2),
                ('name', 'U20')
            ])
        )

        # Get the antenna names and their position from the origin
        self.antenna_information['name'] = origin.antenna_array['name']
        self.antenna_information['position'] = origin.antenna_array['position']
        self.antenna_information['position_showerplane'] = origin.get_transformer().transform_to_vxB_vxvxB(
            self.antenna_information['position'], core=origin.core
        )[:, :2]  # we do not care about the z-coordinate in the shower plane

        # Calculate frequencies from origin
        dt_res = origin.coreas_settings['time_resolution']
        self.frequencies = np.fft.rfftfreq(origin.trace_length, d=dt_res)

        # Load time axis
        for ant in self.antenna_information:
            _, _, start_origin = origin.get_trace_slice(
                ant['name'], int(origin.slice_grammage), return_start_time=True
            )
            ant['time_axis'] = np.arange(origin.trace_length) * dt_res + start_origin

        self.logger.info(f"Using CE_LIN for synthesis: {ce_linear}")

        for slice_ind, slice_val in enumerate(origin.long[:, 0]):
            # If the end of the slice is inside the ground, we do not add it to the template
            if slice_val > self.atm.get_xmax_from_distance(0.0, origin.zenith / units.rad,
                                                           observation_level=origin.core[2] / units.m):
                break

            my_slice = SliceSynthesis(slice_val, ce_linear=ce_linear)

            self.__link_slice_attributes(my_slice)

            my_slice.make_template(origin)

            self.slices.append(my_slice)
            self.slices_grammage.append(slice_val)

    def map_template(self, target: Shower):
        """
        Map the template to a target profile, represented in a target ``Shower``.

        Calculates the trace for every antenna present in the template.
        The antennas are contained in the first dimension of the returned arrays.
        If the `target` has not the same geometry of the template, the internal antenna positions
        are updated such to still have the same positions in the shower plane. It is recommended to
        only synthesise target showers with a lower zenith angle than the template, in which case
        the slices not present in the `target` will be cut.

        Parameters
        ----------
        target : smiet.numpy.io.Shower
            The target Shower object, containing the longitudinal profile

        Returns
        -------
        synthesised_geo : np.ndarray
            The synthesised geomagnetic trace in each antenna, shaped as (ant, samples)
        synthesised_ce : np.ndarray
            The synthesised charge-excess trace in each antenna, shaped as (ant, samples)

        Notes
        -----
        The synthesised traces are the sum of all slices in the template, each of which is mapped to
        the target. If the geometry of the target and origin are different, there will be a mismatch
        in slices. If the target has a lower zenith, it will have fewer slices than the template. In
        this case we simply cut these last few slices. If on the other hand the target has a higher
        zenith angle, there will be slices which the template does not contain. While the algorithm
        will still work, the results will probably not be accurate as there is simply less signal
        being accounted for.
        """
        # If target slicing is not the same as our template, the mapping will not work
        assert np.isclose(target.slice_grammage, self.slices_grammage[1] - self.slices_grammage[0]), \
            "Target slice grammage does match the template slice grammage"

        # Let's check if the geometry of the target is the same as the template
        max_slice_index = len(self.slices)
        template_zenith = self.template_information['geometry'][0]
        if target.zenith > template_zenith:
            self.logger.warning(
                f'Target zenith angle {target.zenith} is larger than the template zenith angle {template_zenith}. '
                f'This will probably lead to the last slices not being synthesised. '
            )

            self.__update_ant_positions(target)

        elif target.zenith < template_zenith:
            # Only use the slices which do not end up in the ground for the target
            max_slice_index = int(self.atm.get_xmax_from_distance(
                0.0, target.zenith / units.rad, observation_level=target.core[2] / units.m
            ) // target.slice_grammage)

            self.logger.info(
                f'Target zenith angle {target.zenith} is smaller than the template zenith angle {template_zenith}. '
                f'Only the first {max_slice_index} slices from the template will be used.'
            )

            self.__update_ant_positions(target)

        total_geo_synth = np.zeros_like(self.antenna_information['time_axis'])
        total_ce_synth = np.zeros_like(self.antenna_information['time_axis'])

        for my_slice in self.slices[:max_slice_index]:
            geo_synth, ce_synth = my_slice.map_template(target)

            total_geo_synth += geo_synth
            total_ce_synth += ce_synth

        return total_geo_synth, total_ce_synth

    def save_template(self, save_dir=None):
        """
        Save the internal state of the synthesis class to disk.

        Parameters
        ----------
        save_dir : str, default='smiet/templates'

        Returns
        -------
        status_code : int
            If successful, returns 0
        """
        if save_dir is None:
            save_dir = os.path.join(os.path.dirname(__file__), 'templates')

        save_file = os.path.join(save_dir, f"{self.template_information['name']}.npz")

        np.savez(
            save_file,
            template_information=self.template_information,
            ant_information=self.antenna_information,
            slice_information=[s.serialise() for s in self.slices],
            spectral_parameters=[self.geo, self.ce, self.ce_lin],
            viewing_angles=self.viewing_angles,
            frequencies=self.frequencies,
            frequency_range=self.frequency_range,
            atmosphere=[self.atm.model, self.atm.n0],
        )

        return 0

    def load_template(self, file_path, gdas_file=None):
        """
        Load the template from a saved state, as done by :meth:`save_template`.

        Parameters
        ----------
        file_path : str
            The path to the .npz archive containing the template.
        gdas_file : str, default=None
            If not None, the Atmosphere will be created using this GDAS file.
            Otherwise, the Atmosphere will be created using the model and n0 parameters
            stored in the template file. If the model number is not available in
            radiotools, this will crash.

        """
        archive = np.load(file_path, allow_pickle=True)

        self.template_information = archive['template_information'].item()  # convert back from np.ndarray to dict
        self.antenna_information = archive['ant_information']

        self.geo, self.ce, self.ce_lin = archive['spectral_parameters']
        self.has_spectral_coefficients = True

        self.viewing_angles = archive['viewing_angles']
        self.frequencies = archive['frequencies']
        self.frequency_range = tuple(archive['frequency_range'])

        # Create the atmosphere object
        # TODO: allow for curved atmosphere?
        if gdas_file is not None:
            self.atm = Atmosphere(curved=False, gdas_file=gdas_file)
        else:
            self.atm = Atmosphere(model=int(archive['atmosphere'][0]), n0=archive['atmosphere'][1], curved=False)

        all_slices = archive['slice_information']

        self.slices = []
        for data_slice in all_slices:
            my_slice = SliceSynthesis(0)

            # Load slice
            my_slice.deserialise(data_slice)

            self.__link_slice_attributes(my_slice)

            self.slices.append(my_slice)
            self.slices_grammage.append(my_slice.grammage)

        return 0

    def __link_slice_attributes(self, my_slice: SliceSynthesis):
        """
        Link the slice variables that are shared to the loaded attributes.

        To conserve

        Parameters
        ----------
        my_slice : SliceSynthesis
        """

        my_slice._v_angles = self.viewing_angles
        my_slice._geo = self.geo
        my_slice._ce = self.ce
        my_slice._ce_lin = self.ce_lin
        my_slice._ant_info = self.antenna_information
        my_slice._atm = self.atm
        my_slice._frequency_range = self.frequency_range
        my_slice._frequencies = self.frequencies

    def __update_ant_positions(self, target: Shower):
        """
        Update the internal antenna positions to the geometry of the target.

        When the target has a different geometry, the antenna positions are taken to be
        the same in the shower plane such that starshapes are preserved. Therefore, when
        changing the geometry the antenna positions are recalculated by taking the positions
        in the (new) shower plane and projecting them along the (new) shower axis to ground.

        Parameters
        ----------
        target: Shower
            The target shower, representing the new geometry
        """
        self.logger.info(
            f"Updating antenna positions to the new geometry with zenith {target.zenith / units.deg} deg,"
            f" azimuth {target.azimuth / units.deg} deg and magnet {target.magnet / units.gauss} Gauss"
        )

        transformer = target.get_transformer()
        self.antenna_information['position'] = transformer.transform_from_vxB_vxvxB_2D(
            self.antenna_information['position_showerplane'], core=target.core
        )

    def get_origin_shower(self):
        """
        Create a minimal ``Shower`` object from the template information.

        This function does not return the ``SlicedShower`` which was used to create the template.
        That one is not stored. Rather, the essential information such as geometry, core and magnetic
        field are stored in the :attr:`TemplateSynthesis.template_information` dictionary. This information
        is used to construct a minimal ``Shower`` object, which can be used for example to retrieve
        a transformer.

        Returns
        -------
        origin : smiet.numpy.io.Shower
            The minimal representation of the origin shower used to make the template
        """
        origin = Shower()

        origin.geometry = self.template_information['geometry']
        origin.core = self.template_information['core']
        origin.magnet = self.template_information['magnet']
        origin.atmosphere = self.atm

        origin._slice_grammage = self.slices_grammage[1] - self.slices_grammage[0]  # set the slicing grammage to avoid errors

        return origin

    def get_time_axis(self):
        """
        Get the time axis for all antennas.

        Returns
        -------
        time_axis : np.ndarray
            The time axis for each antenna, shaped as (# antennas, # time samples)
        """
        return self.antenna_information['time_axis']

    def get_antenna_names(self):
        """
        Get the names of all internal antennas.

        Returns
        -------
        antenna_names : list of str
        """
        return self.antenna_information['name']

    def slice_create_interpolators(self, my_slice_ind, shower: Shower, frequencies, use_ce_linear=None):
        """
        Get the interpolators for the corrections factors from the slice with index `my_slice_ind`.

        The `shower` and `frequencies` are passed in as an arguments to the
        :meth:`SliceSynthesis.create_interpolators` method.

        Parameters
        ----------
        my_slice_ind : int
            The index of the slice in the `TemplateSynthesis.slices` array. Should correspond to
            the grammage of the slice divided by the slice thickness minus one.
        shower : smiet.numpy.io.Shower
            The Shower from which to use the parameters to evaluate the amplitude frequency spectra
        frequencies : np.ndarray
            The frequencies to evaluate the amplitude frequency spectra
        use_ce_linear : bool, default=None
            If set, this can be used to override the `ce_linear` of the slice before evaluating the
            interpolators.If False, the charge-excess component spectra are evaluated using a log-parabola,
            i.e. with the `c` spectral parameter. If True, the component uses the linear variant.

        Returns
        -------
        interpolator_geo : `scipy.interpolate.interp1d`
            Interpolator object for the geomagnetic component
        interpolator_ce : `scipy.interpolate.interp1d`
            Interpolator object for the charge-excess component
        """

        my_slice: SliceSynthesis = self.slices[my_slice_ind]

        self.logger.info(f"Getting interpolators for slice with grammage {my_slice.grammage}")

        if use_ce_linear is not None:
            # Store the ce_linear value
            ce_linear_setting = my_slice.ce_linear
            # Override the value
            my_slice.ce_linear = use_ce_linear
            # Evaluate the interpolators
            interpolators = my_slice.create_interpolators(shower, frequencies)
            # Restore the original ce_linear
            my_slice.ce_linear = ce_linear_setting
        else:
            interpolators = my_slice.create_interpolators(shower, frequencies)

        return interpolators

    def slice_get_antenna_parameters(self, my_slice_ind):
        """
        Get the antenna array containing for each antenna the template amplitude and
        phase frequency spectra, for the geomagnetic and charge-excess components,
        as well as the distance and viewing angle.

        Note that these last variables are changed with the information from the
        target shower during the mapping process, so beware when looking at these
        numbers.

        The output is a structured array with the following fields:

        * name : the names of the antenna's
        * position : the position of the antenna's (in the NRR coordinate system)
        * amplitude_geo : the amplitude frequency spectra of the geomagnetic component
        * phase_geo : the phase frequency spectra of the geomagnetic component
        * amplitude_ce : the amplitude frequency spectra of the charge-excess component
        * phase_ce : the phase frequency spectra of the charge-excess component
        * distance : the distance from the slice to each antenna
        * viewing_angle : the viewing angle wrt to this slice of each antenna

        Parameters
        ----------
        my_slice_ind : int
            The index of the slice in the `TemplateSynthesis.slices` array

        Returns
        -------
        antenna_parameters : np.ndarray
            A structured array with the columns mentioned above
        """

        import numpy.lib.recfunctions as rfn

        my_slice: SliceSynthesis = self.slices[my_slice_ind]

        self.logger.info(f"Getting antenna parameters for slice with grammage {my_slice.grammage}")

        return rfn.merge_arrays([self.antenna_information[['name', 'position']], my_slice.antenna_parameters],
                                flatten=True, usemask=False)

    def slice_get_spectra(self, my_slice_ind, delta_xmax, frequencies):
        r"""
        Retrieve the amplitude spectra at the specified frequencies, for a given :math:`\Delta X_{max}` .

        The `delta_xmax` and `frequencies` parameters are passed on to the :meth:`SliceSynthesis.get_spectra`
        function.

        Parameters
        ----------
        my_slice_ind : int
            The index of the slice in the `TemplateSynthesis.slices` array
        delta_xmax : float
            The :math:`\Delta X_{max}` for which to evaluate the spectral functions
        frequencies : np.ndarray
            The list of frequencies at which to calculate the spectra

        Returns
        -------
        spectrum_geo : np.ndarray
            The evaluated geomagnetic amplitude frequency spectrum, shaped as (# viewing angles, # freq).
        spectrum_ce : np.ndarray
            The charge-excess spectrum
        spectrum_ce_lin : np.ndarray
            The charge-excess spectrum, but evaluated without the quadratic (`c`) component.
        """

        my_slice: SliceSynthesis = self.slices[my_slice_ind]

        self.logger.info(f"Getting spectra from slice with grammage {my_slice.grammage}")

        return my_slice.get_spectra(delta_xmax, frequencies)

    def slice_get_normalisation_factors(self, my_slice_ind, shower: Shower):
        r"""
        Calculate the template synthesis normalisation factors, to remove geometric and
        shower parameter dependencies, according to

        .. math::
            geo_{factor} = n_{slice} * \sin( \alpha_{GEO} ) / \rho_{slice}

            ce_{factor} = n_{slice} * \sin( \theta^{Ch}_{slice} )

        The ``shower`` parameter is used as argument to the :meth:`SliceSynthesis.get_normalisation_factors`.

        Parameters
        ----------
        my_slice_ind : int
            The index of the slice in the `TemplateSynthesis.slices` array
        shower : smiet.numpy.io.Shower
            The shower for which to calculate the normalisation factors.

        Returns
        -------
        geo_factor : float
            The normalisation factor for the geomagnetic component.
        ce_factor : float
            The normalisation factor for the charge-excess component.
        """

        my_slice: SliceSynthesis = self.slices[my_slice_ind]

        self.logger.info(f"Getting normalisation factors from slice with grammage {my_slice.grammage}")

        return my_slice.get_normalisation_factors(shower)

    def slice_map_template(self, my_slice_ind, target: Shower):
        """
        Map the template to a target profile, represented in a target Shower.
        Calculates the trace for every antenna present in the template.
        The antennas are contained in the first dimension of the returned arrays.

        Parameters
        ----------
        my_slice_ind : int
            The index of the slice in the `TemplateSynthesis.slices` array
        target : smiet.numpy.io.Shower
            The target Shower object, containing the longitudinal profile

        Returns
        -------
        synthesised_geo : np.ndarray
            The geomagnetic trace for each antenna
        synthesised_ce : np.ndarray
            The charge-excess trace for each antenna
        """

        my_slice: SliceSynthesis = self.slices[my_slice_ind]

        self.logger.info(f"Mapping template for slice with grammage {my_slice.grammage}")

        return my_slice.map_template(target)
