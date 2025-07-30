import logging

import h5py
import numpy as np

import radiotools.coordinatesystems

from radiotools import helper as hp
from scipy.constants import c as c_vacuum

from ..utilities import angle_between, bandpass_filter_trace
from smiet import units


class Shower:
    """
    The ``Shower`` class represents an air shower setup and evolution.

    It holds the geometric information for a shower, like the zenith/azimuth, as well as the longitudinal profile.
    Next to this, it can also store the magnetic field, the atmosphere in which it was simulated, and the core.
    These variables are used to calculate the `radiotools.coordinatesystems.cstrafo` object, which can be used
    to convert between different coordinate systems.
    The primary use case is to specify the target parameters for a shower in template synthesis.

    Attributes
    ----------
    atmosphere : radiotools.atmosphere.models.Atmosphere
        The atmosphere in which the shower was simulated
    core : np.ndarray
        The position of the core in the NRR coordinate system
    """

    def __init__(self):
        self.logger = logging.getLogger("smiet.numpy.io.Shower")

        self._long_profile = None
        self._geometry = None
        self._magnetic_field = None
        self._slice_grammage = None

        self.atmosphere = None
        self.core = [0, 0, 0]

        # To be computed
        self._GH_parameters = None
        self._transformer = None

    @property
    def xmax(self):
        """
        The :math:`X_{max}` of the shower. This is the result from fitting a GH to the longitudinal profile (not set manually).
        """
        if self._GH_parameters is not None:
            return self._GH_parameters[2]
        else:
            self.logger.error(
                "The Gaisser-Hillas parameters have not been set. You probably did not set the longitudinal profile yet."
            )

    @property
    def nmax(self):
        """
        The :math:`N_{max}` of the shower. This results from fitting a GH to the longitudinal profile (ie not set manually).
        """
        if self._GH_parameters is not None:
            return self._GH_parameters[0]
        else:
            self.logger.error(
                "The Gaisser-Hillas parameters have not been set. You probably did not set the longitudinal profile yet."
            )

    @property
    def magnet(self):
        """
        Magnetic field vector in the NRR coordinate system
        """
        if self._magnetic_field is not None:
            return self._magnetic_field
        else:
            self.logger.error("The magnetic field vector has not been set")

    @magnet.setter
    def magnet(self, magnet_field_vec):
        assert len(magnet_field_vec) == 3, "B-field vector must contain three components"

        self._magnetic_field = magnet_field_vec
        self._transformer = None  # reset the transformer to be recalculated

    @property
    def long(self):
        """
        The longitudinal profile of the shower. The first column contains the grammage,
        the second column the sum of positrons and electrons. When setting the longitudinal
        profile, it is supported to pass in the particle table from CORSIKA. This is checked
        by looking at the number of columns, ie the second dimension. If this is equal to 10,
        a CORSIKA particle table is assumed and the third and fourth columns are summed.
        Otherwise, the profile should have the shape (slices, 2).
        """
        if self._long_profile is not None:
            return self._long_profile
        else:
            self.logger.error("The longitudinal profile has not been set")

    @long.setter
    def long(self, profile: np.ndarray):
        new_slice_grammage = profile[1, 0] - profile[0, 0]
        if self._slice_grammage is not None:
            if self._slice_grammage != new_slice_grammage:
                raise ValueError("The slice grammage was changed")

        if profile.shape[1] == 10:
            self.logger.debug("Assuming CORSIKA particle table")

            self._long_profile = np.zeros((len(profile), 2))
            self._long_profile[:, 0] = profile[:, 0]
            self._long_profile[:, 1] = np.sum(profile[:, 2:4], axis=1)
        else:
            self.logger.debug("Assuming first column is grammage, second sum of e+ and e-")

            assert profile.shape[1] == 2, "Please provide two columns: the grammage, and sum of positrons/electrons"
            self._long_profile = profile

        self._slice_grammage = new_slice_grammage
        self._GH_parameters = self.fit_gaisser_hillas()

    @property
    def slice_grammage(self):
        """
        The (slant depth) step width with which the longitudinal profile is sampled.
        This is inferred from the longitudinal profile when that one is set.
        """
        if self._slice_grammage is not None:
            return self._slice_grammage
        else:
            self.logger.error("Slice thickness not yet set. Copy it from another shower or set a long profile.")

    @property
    def zenith(self):
        """
        The zenith angle of the shower (in internal units). Can be set using ``geometry``.
        """
        if self._geometry is not None:
            return self._geometry[0]
        else:
            self.logger.error("Geometry has not been set")

    @property
    def azimuth(self):
        """
        The azimuth angle of the shower (in internal units). Can be set using ``geometry``.
        """
        if self._geometry is not None:
            return self._geometry[1]
        else:
            self.logger.error("Geometry has not been set")

    @property
    def geometry(self):
        """
        Store the zenith and azimuth. These must be provided in the internal unit system!
        """
        if self._geometry is not None:
            return self._geometry
        else:
            self.logger.error("Geometry has not been set")

    @geometry.setter
    def geometry(self, geo):
        assert len(geo) == 2, "Please provide zenith and azimuth components in internal units"

        self._geometry = np.array(geo)
        self._transformer = None  # reset the transformer to be recalculated

    @property
    def geomagnetic_angle(self):
        """
        Calculate the angle between the magnetic field vector and the shower axis
        """
        shower_axis = hp.spherical_to_cartesian(*self.geometry / units.rad)

        return angle_between(self.magnet * -1, shower_axis)

    def fit_gaisser_hillas(self):
        """
        Fit a Gaisser-Hillas function to the currently loaded longitudinal profile,
        to determine the parameters like :math:`X_{max}` and :math:`N_{max}`.

        Returns
        -------
        popt : np.ndarray
            The parameters of the Gaisser-Hillas function, in the order [N, X0, Xmax, p0, p1, p2]
            (p0,p1,p2 are the polynomial coefficients in denominator for lambda)

        Notes
        -----
        The Gaisser-Hillas function is defined as:

        .. math::
            f(X) = N \\left( \\frac{X - X_0}{X_{max} - X_0} \\right)^{\\frac{X_{max} - X_0}{\\lambda}} \\exp\\left( \\frac{X_{max} - X}{\\lambda} \\right)
        """
        from scipy.optimize import curve_fit

        def gaisser_hillas(X, N, X0, Xmax, p0, p1=0, p2=0):
            l = p0 + p1 * X + p2 * X ** 2
            power = (Xmax - X0) / l

            if np.sum(l < 0):
                return np.inf

            if np.sum(power < 0):
                return np.inf

            if np.sum(power > 100):
                return np.inf

            result = np.zeros_like(X)
            mask = (X - X0) >= 0
            result[mask] = N * ((X[mask] - X0) / (Xmax - X0)) ** (power[mask]) * np.exp((Xmax - X[mask]) / l[mask])
            result = np.nan_to_num(result)

            return result

        popt = curve_fit(
            gaisser_hillas, self.long[:, 0], self.long[:, 1],
            p0=[self.long[:, 1].max(), 0, self.long[:, 0][self.long[:, 1].argmax()], 20],
            maxfev=3000
        )

        return popt[0]

    def get_transformer(self):
        """
        Get the transformer object from radiotools which can be used to convert between different coordinate systems.
        The transformer is cached, so that it is only calculated once. If the geometry or magnetic field vector gets
        updated, the transformer is reset.

        Returns
        -------
        transformer : radiotools.coordinatesystems.cstrafo
            The cstrafo object with the current geometry and magnetic field vector.
        """
        if self._transformer is None:
            self._transformer = radiotools.coordinatesystems.cstrafo(
                self.zenith / units.rad,
                self.azimuth / units.rad,
                magnetic_field_vector=self._magnetic_field,  # units of magnet don't matter, only direction
            )
        return self._transformer

    def copy_settings(self, other):
        """
        This convenience method allows to easily copy the settings from another Shower,
        which is useful when for example creating a target Shower.

        Parameters
        ----------
        other: Shower
            The Shower to copy the settings from.

        Notes
        -----
        The settings which are copied from the other shower are:

        * The geometry
        * The magnetic field vector
        * The simulation core
        * The slice grammage
        * The atmosphere
        """
        self.geometry = other.geometry
        self.magnet = other.magnet
        self.core = other.core
        self.atmosphere = other.atmosphere

        self._slice_grammage = other.slice_grammage


class CoreasHDF5:
    """
    The ``CoreasHDF5`` class is a base class for reading in HDF5 files produced by CoREAS.

    It extracts the settings used in the CoREAS simulation, like the time resolution and the core position.
    It also reads in settings from the CORSIKA part, such as the geometry and the magnetic field.
    These two are available as dictionaries in the ``coreas_settings`` and ``corsika_settings`` properties.
    Next to the settings, it is also possible to get in the longitudinal profile of the shower.
    Furthermore, the class offers a method to read in the time traces of an observer in the HDF5 file.

    Note that it returns all quantities in the NRR coordinate system, which is different from
    the CORSIKA coordinate system.

    Parameters
    ----------
    file_path : str
        The path to the CoREAS HDF5 file
    """
    def __init__(self, file_path):
        self._file = file_path
        self._coreas_settings = None
        self._corsika_settings = None
        self._trace_length = None

        self.logger = logging.getLogger("smiet.numpy.io.CoreasHDF5")

    @property
    def trace_length(self):
        """
        The number of samples in each time trace. This is calculated from the time boundaries
        (automatic or manual) and the time resolution of the simulation.
        """
        if self._trace_length is None:
            trace_length = int(
                self.coreas_settings["automatic_time_boundaries"] / self.coreas_settings['time_resolution']
            )
            if trace_length != 0:
                self._trace_length = trace_length
            else:  # if automatic time boundaries are not set, use manual time boundaries
                self._trace_length = int(
                    self.coreas_settings["manual_time_boundaries"] / self.coreas_settings['time_resolution']
                )
        return self._trace_length

    @property
    def coreas_settings(self):
        """
        Get the CoREAS configuration of this simulation. This is contained in a dictionary, with the following
        keys:

        * core_coordinate: The core position in the NRR coordinate system
        * time_resolution: The time resolution of the simulation
        * automatic_time_boundaries: The automatic time boundaries of the simulation
        * manual_time_boundaries: The manual time boundaries of the simulation
        * n0: The refractive index at sea level
        """
        if self._coreas_settings is None:
            self._coreas_settings = self.__get_coreas_settings()
        return self._coreas_settings

    @property
    def corsika_settings(self):
        """
        Get the CORSIKA configuration of this simulation. This is contained in a dictionary, with the following
        keys:

        * zenith: The zenith angle of the shower
        * azimuth: The azimuth angle of the shower
        * magnetic_field: The magnetic field vector in the NRR coordinate system
        * observation_level: The observation level of the shower
        * atmosphere_model: The atmosphere model used in the simulation
        * primary_particle: The primary particle used in the simulation
        * primary_energy: The energy of the primary particle
        * thinning_level: The thinning level used in the simulation
        """
        if self._corsika_settings is None:
            self._corsika_settings = self.__get_corsika_settings()
        return self._corsika_settings

    @property
    def name(self):
        """
        Get the name of the simulation, which is the filename without the extension.
        """
        return self._file.split("/")[-1].split(".")[0]

    def get_long_profile(self):
        """
        Get the longitudinal profile of the shower from the HDF5 file stored in the `self._file` attribute.

        The profile is read from the "NumberOfParticles" dataset, which sits in the "atmosphere" group.

        Returns
        -------
        long_profile: np.ndarray
            The longitudinal profile of the shower
        """
        with h5py.File(self._file) as file:
            long_profile = file["atmosphere"]["NumberOfParticles"][:]
        return long_profile

    def filter_trace(self, trace, f_min, f_max):
        """
        Filter a trace between `f_min` and `f_max` using the internal time resolution of the simulation.

        The function assumes the time samples are on the last axis, but if this dimension does not match
        the trace length it will check the other axes to see if any other dimension matches the trace length.
        The filter used is a straightforward bandpass filter, using the :func:`bandpass_filter_trace` function.

        Parameters
        ----------
        trace: np.ndarray
            The trace to filter. Can be multidimensional.
        f_min: float
            The lower frequency (in internal units)
        f_max: float
            The upper frequency (in internal units)

        Returns
        -------
        filtered_trace: np.ndarray
            The bandpass filtered trace
        """
        trace_axis = -1  # based on self.get_trace()
        if trace.shape[trace_axis] != self.trace_length:
            self.logger.warning(
                "Trace shape does not match recorded trace length along the last axis"
            )
            self.logger.info("Attempting to find the trace axis...")
            for shape_i in range(len(trace.shape)):
                if trace.shape[shape_i] == self.trace_length:
                    self.logger.info(f"Found axis {shape_i} which matches trace length!")
                    trace_axis = shape_i
                    break
        return bandpass_filter_trace(
            trace,
            self.coreas_settings["time_resolution"],
            f_min,
            f_max,
            sample_axis=trace_axis,
        )

    def __get_coreas_settings(self):
        with h5py.File(self._file) as file:
            time_resolution = file["CoREAS"].attrs["TimeResolution"] * units.s
            auto_trace_time_length = file['CoREAS'].attrs['AutomaticTimeBoundaries'] * units.s
            trace_time_length = (file["CoREAS"].attrs["TimeUpperBoundary"] - file["CoREAS"].attrs["TimeLowerBoundary"]) * units.s
            core = np.array([
                -1 * file["CoREAS"].attrs["CoreCoordinateWest"],
                file["CoREAS"].attrs["CoreCoordinateNorth"],
                file["CoREAS"].attrs["CoreCoordinateVertical"],
            ]) * units.cm
            n0 = file["CoREAS"].attrs["GroundLevelRefractiveIndex"]

        return {
            "core_coordinate": core,
            "time_resolution": time_resolution,
            "automatic_time_boundaries": auto_trace_time_length,
            "manual_time_boundaries": trace_time_length,
            "n0": n0,
        }

    def __get_corsika_settings(self):
        with h5py.File(self._file) as file:
            zenith = file["inputs"].attrs["THETAP"][0] * units.deg
            azimuth = file["inputs"].attrs["PHIP"][0] * units.deg - 90 * units.deg  # transform to radiotools coord
            magnet = np.array([
                0, file["inputs"].attrs["MAGNET"][0], -1 * file["inputs"].attrs["MAGNET"][1],
            ]) * units.microtesla
            obs_lev = file["inputs"].attrs["OBSLEV"] * units.m
            atm_model = file["inputs"].attrs["ATMOD"]
            primary = file["inputs"].attrs["PRMPAR"]
            energy = file["inputs"].attrs["ERANGE"][0] * units.GeV
            thinning = file["inputs"].attrs["THIN"][0]

        return {
            "zenith": zenith,
            "azimuth": azimuth,
            "magnetic_field": magnet,
            "observation_level": obs_lev,
            "atmosphere_model": atm_model,
            "primary_particle": primary,
            "primary_energy": energy,
            "thinning_level": thinning,
        }


    def get_trace_raw(self, observer_name):
        """
        Get the raw trace (as produced by CoREAS) from an observer in the HDF5.

        The trace is converted to the internal coordinate system before being returned.

        Parameters
        ----------
        observer_name : str
            The name of the observer as defined in the HDF5 file

        Returns
        -------
        trace_slice_ground : np.ndarray
            The raw trace (on the ground), shaped as (trace_length, 3).
        trace_time_array : np.ndarray
            The array containing the timings of the samples, shaped as (trace_length,).
            This is just the first column of the CoREAS output, converted to internal units.
        """
        with h5py.File(self._file) as file:
            try:
                trace_slice = file["CoREAS"]["observers"][f"{observer_name}"][:]  # samples x 4
                self.logger.debug(f"Successfully read in trace of observer {observer_name}")
            except KeyError:
                raise ValueError(f"Observer {observer_name} not present in the file")

            # Save trace start time
            trace_time_array = trace_slice[:, 0] * units.s

            # Convert CGS to internal units
            trace_slice *= c_vacuum * 1e2 * units.microvolt / units.m
            trace_slice_ground = np.array(
                [-trace_slice[:, 2], trace_slice[:, 1], trace_slice[:, 3]]
            )

        return trace_slice_ground, trace_time_array
