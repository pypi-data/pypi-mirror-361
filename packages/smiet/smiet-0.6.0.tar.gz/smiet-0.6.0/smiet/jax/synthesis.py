from __future__ import annotations

import logging
import os
from functools import partial
from typing_extensions import Self, Tuple, Union

import h5py
import jax

jax.config.update("jax_enable_x64", True)

import numpy as np
import jax.numpy as jnp

from .io import BaseShower, SlicedShower
from smiet import units
from jax_radio_tools import spherical_to_cartesian, geo_ce_to_vB_vvB_v
from jax_radio_tools.atmosphere import Atmosphere
from .utilities.geometry import angle_between
from .utilities.batched_interpolation import batched_interp1d


def amplitude_function(
    params: jax.typing.ArrayLike,
    frequencies: jax.typing.ArrayLike,
    d_noise: float = 0.0,
) -> jax.Array:
    """
    Calculate the amplitude frequency spectrum corresponding to the parameters `params`.

    Parameters
    ----------
    params : jax.typing.ArrayLike
        The spectral parameters. If it is a multidimensional array, the first dimension must contain the parameters.
    frequencies : jax.typing.ArrayLike
        The values of the frequencies to evaluate - remove central frequency beforehand!
    d_noise : float, default=0.0
        The noise floor level

    Returns
    -------
    The evaluated amplitude frequency spectrum with shape VIEW x FREQ x SLICES
    """
    if len(params.shape) == 1:
        params = params.reshape((params.shape[0], 1))
    return (
        params[0, :, None, :]
        * jnp.exp(
            params[1, :, None, :] * frequencies[None, :, None]
            + params[2, :, None, :] * frequencies[None, :, None] ** 2
        )
        + d_noise
    )


# @jax.jit
def get_spectra(
    xmax: float,
    spectral_coeffs: jax.typing.ArrayLike,
    grammages: jax.typing.ArrayLike,
    frequencies: list,
) -> jax.typing.ArrayLike:
    r"""
    Retrieve the amplitude spectra at the specified frequencies, for a given :math:`\Delta X_{max}`.

    Parameters
    ----------
    xmax : float
        The maximum of the atmospheric depth in g/cm^2
    spectral_coeffs : jax.typing.ArrayLike
        the spectral coefficients stored with shape
        {GEO, CE} x VIEW x FREQ
    grammages : jax.typing.ArrayLike
        an array of atmospheric depths in g/cm^2
    frequencies : list
        The list of frequencies at which to evaluate the spectra (after filtering)

    Returns
    -------
    spectrum : jax.typing.ArrayLik
        the amplitude spectrum in shape
        {GEo x CE} x VIEW x FREQ x SLICES
    """
    # expand dimensions for grammage to VIEW x FREQ x SLICES x {GEO, CE}
    gram = jnp.expand_dims(grammages, axis=(0, 1, 3))
    # NB: flip in the spectral parameters is necessary since
    # jnp.polyval evaluates from from the HIGHEST power,
    # whereas np.polynomial.polynomial.polyval evaluates from
    # the LOWEST power.
    # since the amplitude function follows the structure from the
    # numpy code, we need another flip after evaluating the polynomial
    spectral_params = jnp.flip(
        jnp.polyval(jnp.flip(spectral_coeffs.T)[:, :, :, None, :], gram - xmax),
        axis=(0, 1),
    )  # 3 x viewing angles x SLICES x {GEO, CE}

    frequencies = jnp.array(frequencies)

    spectra = spectral_params[0, :, None, :, :] * jnp.exp(
        spectral_params[1, :, None, :, :] * frequencies[None, :, None, None]
        + spectral_params[2, :, None, :, :] * frequencies[None, :, None, None] ** 2
    )
    return jnp.moveaxis(spectra, 3, 0)


@partial(jax.jit, static_argnames=["outshape"])
def get_correction_factors(
    spectral_params: jax.typing.ArrayLike,
    ant_v_angles: jax.typing.ArrayLike,
    v_angles_grid: list,
    outshape: tuple,
) -> jax.Array:
    r"""
    Get the correction factors from the spectral parameters.

    Parameters
    ----------
    spectral_params : jax.typing.ArrayLike
        the spectral parameters for the geomagnetic and charge excess emission
        in shape {GEO x CE} x VIEW x FREQ x SLICES
    ant_v_angles : jax.typing.ArrayLike
        the viewing angles for the particular geometry & atmosphere
    v_angles_grid : list, static
        the grid of viewing angles used for interpolation
    outshape : tuple, static
        the shape for the correction factor array
        shape should be {GEO x CE} x ANTS x FREQ x SLICES

    Returns
    -------
    correction_factors : jax.typing.ArrayLike
        the corrections factors in shape
        {GEO x CE} x ANTS x FREQ x SLICES
    """
    # calculate the correction factors
    # shape is {GEO x CE} x ANTS x FREQ x SLICES
    correction_factors = jnp.zeros(outshape)

    for icomp, comp in enumerate(spectral_params):
        # Temporary fix for bad viewing angles in large freq range
        # Here we take log for more accurate interpolation (after taking abs to avoid -log values)
        corr_fact = jnp.log(
                jnp.where(jnp.abs(comp[:-2]) <= 1e-20, 1.0, jnp.abs(1.0 / comp[:-2]))
            ) 

        # interpolate over viewing angles
        correction_factors = correction_factors.at[icomp, ...].set(
            jnp.exp(
                batched_interp1d(jnp.array(ant_v_angles), jnp.array(v_angles_grid[:-2]), corr_fact)
            )
        )

    return correction_factors


class TemplateSynthesis:
    """Class to manage the template synthesis."""

    def __init__(self: Self, atm_model: int = 17, freq_ar: list = None, gdas_file : Union[str, None] = None) -> None:
        self.logger = logging.getLogger(
            "smiet.jax.synthesis.TemplateSynthesis"
        )
        self.atm = Atmosphere(model=atm_model, observation_level=0.0, gdas_file=gdas_file)

        # spectral parameters
        self.has_spectral_coefficients = None
        self.spectral_params = None
        self.viewing_angles = None

        # frequency properties
        self.frequency_range = None
        self.frequencies = None
        self.freq_range_mask = None
        self.truncated_frequencies = None
        self.n_samples = None  # time bins, not frequency bins
        self.delta_t = None

        # antenna properties
        self.ant_names = None
        self.ant_time_axes = None
        self.ant_positions_ground = None
        self.ant_positions_vvB = None
        self.n_antennas = None

        # slice properties
        self.template_information = None
        self.grammages = None
        self.nr_slices = None

        # read spectral parameters from file
        # NB: divide by units.MHz since the base unit system is based on nanoseconds
        # and again, its assumed that the units are applied when using frequencies
        if freq_ar is not None:
            spectral_filename = f"spectral_parameters_{int(freq_ar[0]/units.MHz)}_{int(freq_ar[1]/units.MHz)}_{int(freq_ar[2]/units.MHz)}.hdf5"
            self.read_spectral_file(spectral_filename)

    def read_spectral_file(self: Self, filename: str) -> None:
        """
        Read spectral parameters from a file with `filename` in the spectral_parameters/ directory.

        Parameters
        ----------
        filename : str
           The name of the spectral parameters file
        """
        path_to_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "spectral_parameters", filename
        )

        if not os.path.exists(path_to_file):
            raise FileNotFoundError(
                f"Filename {filename} does not exist in the spectral_parameters/ directory."
                "Did you provide the correct frequency range?"
            )

        # read spectral parmaeters from hdf5 file
        with h5py.File(path_to_file) as spectral_file:
            self.frequency_range = tuple(
                spectral_file["/Metadata/Frequency_MHz"][:] * units.MHz
            )
            self.viewing_angles = np.array(spectral_file["/Metadata/ViewingAngles"][:])

            geo = np.array(spectral_file["SpectralFitParams/GEO"][:])
            ce = np.array(spectral_file["SpectralFitParams/CE_LIN"][:])
            # ce = np.array(spectral_file["SpectralFitParams/CE"][:])
            # self.spectral_params[2, ...] = np.array(
            #     spectral_file["SpectralFitParams/CE_LIN"][:]
            # )

            self.spectral_coeffs = np.array([geo, ce])

            self.has_spectral_coefficients = True

        self.logger.debug(f"Loaded in the spectral coefficients from {filename}")

    def _initialise_antennas(self: Self, shower: SlicedShower) -> None:
        """
        Initialise the parameters for the antenna.

        This is just a convenience function to make the make_template function look better.

        Parameters
        ----------
        shower : SlicedShower
            The sliced shower object conatining antennas information
        """
        self.ant_names = list(shower.ant_names)
        self.atm.obs_lvl = shower.core[2] / units.cm  # (need to convert from internal units to m)
        self.n_antennas = len(self.ant_names)

        # convert position to NRR CS, with shape ANT x 3
        self.ant_positions_ground = shower.ant_positions_ground
        self.ant_positions_vvB = shower.get_antennas_showerplane()

        # Calculate frequencies from shower
        self.delta_t = shower.delta_t
        self.frequencies = np.fft.rfftfreq(shower.trace_length, d=shower.delta_t)

        # # get time axes, with shape ANT x SAMPLES
        self.ant_time_axes = shower.trace_times

        # finally store the number of samples that we have
        self.n_samples = shower.trace_length

    def make_template(self: Self, origin: SlicedShower) -> None:
        """
        Process a ``SlicedShower`` into a template.

        Parameters
        ----------
        origin : smiet.jax.io.sliced_shower.SlicedShower
            The origin shower
        """
        if not self.has_spectral_coefficients:
            raise RuntimeError(
                "Please make sure the spectral coefficients are loaded before making a template"
            )

        # initialise all antenna parameters
        self._initialise_antennas(origin)

        # self.logger.info(f"Using CE_LIN for synthesis: {ce_linear}")

        # initialise parameters
        self.freq_range_mask = np.logical_and(
            self.frequency_range[0] <= self.frequencies,
            self.frequencies <= self.frequency_range[1],
        )
        self.truncated_frequencies = (
            self.frequencies[self.freq_range_mask] - self.frequency_range[2]
        )

        # gather shower parameters to compute the relevant shower properties
        self.grammages = origin.grammages
        self.nr_slices = origin.nr_slices

        # computing shower properties (distance, correction factors, normalisation factors)
        # we compute these first since they are static and need not be computed repeatedly
        # in future implementations
        ant_viewing_angles, ant_distances_origin = (
            self._calculate_distance_viewing_angles(origin.zenith, origin.azimuth, origin.core)
        )
        norm_factors_origin = self._calculate_normalisation_factor(origin)
        # remove slices with few particles
        norm_factors_origin = np.where(
            origin.long_profile < 0.001 * origin.nmax, 0, norm_factors_origin
        )

        spectral_params_origin = self._get_spectra(origin.xmax)
        correction_factors_origin = self._get_correction_factors(
            spectral_params_origin, ant_viewing_angles
        )

        # set inverse of normalisation factor to zero where particles are too small so as to not process those slices
        norm_factors_origin_inv = np.where(
            norm_factors_origin == 0, 0.0, 1.0 / norm_factors_origin
        )

        # get traces from the origin shower
        # {GEO, CE} x ANT x SAMPLES x SLICES
        geo_origin, ce_origin = origin.get_traces_geoce()
        origin_traces = np.array([geo_origin, ce_origin])

        # RFFT traces to frequency domain, half of traces (+1) due to taking only the real part of FT
        # {GEO, CE} x ANT x FREQ x SLICES
        origin_traces_fft = np.fft.rfft(origin_traces, norm="ortho", axis=2)
        origin_traces_fft *= (
            ant_distances_origin[None, :, None, :]
            * norm_factors_origin_inv[:, None, None, :]
        )

        # amplitude and phase arrays
        # {GEO, CE} x ANTENNAS x FREQUENCIES x SLICES
        self.amplitudes = np.abs(origin_traces_fft) * correction_factors_origin
        self.phases = np.angle(origin_traces_fft)

        # store the shower properties in template_information
        self.template_information = {
            "zenith": origin.zenith,  # in radians
            "azimuth": origin.azimuth,  # in radians
            "magnetic_field_vector" : origin.magnetic_field_vector,  # in Gauss
            "xmax": origin.xmax,
            "nmax": origin.nmax,
            "x0" : origin.x0,
            "lmbda_params" : origin.lmbda_params,
            "geomagnetic_angle": origin.geomagnetic_angle,
            "core" : origin.core,
            "long_profile" : origin.long_profile,
        }

    def _get_spectra(self: Self, xmax: float) -> jax.Array:
        """
        Wrap the JAX jitted function for the computation of the spectra.

        Parameters
        ----------
        xmax : float
            the atmospheric depth at shower maximum
        """
        return jax.jit(get_spectra)(
            xmax,
            self.spectral_coeffs,
            self.grammages,
            list(self.truncated_frequencies),
        )

    def _get_correction_factors(
        self: Self,
        spectral_params: jax.typing.ArrayLike,
        ant_viewing_angles: jax.typing.ArrayLike,
    ) -> jax.Array:
        """
        Wrap the JAX jitted function to get the correction factors.

        Parameters
        ----------
        spectral_params : jax.typing.ArrayLike
            the computed spectral parameters
        ant_viewing_angles : jax.typing.ArrayLike
            the viewing angles for this particular shower

        Returns
        -------
        the correction factors
        """
        corr_fact_shape = (
            2,
            len(self.ant_names),
            len(self.truncated_frequencies),
            self.nr_slices,
        )
        correction_factors = jnp.zeros(
            (
                2,
                len(self.ant_names),
                len(self.frequencies),
                self.nr_slices,
            )
        )
        correction_factors = correction_factors.at[..., self.freq_range_mask, :].set(
            get_correction_factors(
                spectral_params,
                ant_viewing_angles,
                self.viewing_angles,
                corr_fact_shape,
            )
        )
        return correction_factors

    def map_template(self: Self, target: BaseShower) -> jax.Array:
        """
        Map the template to a target profile, represented in a target BaseShower.

        Calculates the trace for every antenna present in the template.

        Parameters
        ----------
        target :  smiet.jax.io.base_shower.BaseShower
            The target BaseShower object, containing the longitudinal profile,
            zenith, azimuth, geomagnetic angle, xmax and nmax

        Returns
        -------
        total_synth : jax.Array
            The synthesised geomagnetic & charge-excess trace for all antennas.
            Shape is {GEO, CE} x ANT x SAMPLES
        """
        # some assertions
        # TODO: figure out how to apply JIT with this

        # # # 1st assert to ensure that the slice width are the same
        # assert (
        #     target.slice_grammage == jnp.diff(self.grammages)[0]
        # ), f"slice width must be the same between origin : {jnp.diff(self.grammages)} and target : {target.slicing_grammage} shower."

        # # second assertion: to ensure that the number of slices between
        # # target and origin are the same
        # assert (
        #     target.nr_slices == self.nr_slices
        # ), f"Number of slices between target {target.nr_slices} and origin {self.nr_slices} must be equal!"

        # computing shower properties (distance, correction factors, normalisation factors)
        # we compute these first since they are static and need not be computed repeatedly
        # in future implementations
        ant_viewing_angles, ant_distances_target = (
            self._calculate_distance_viewing_angles(target.zenith, target.azimuth, target.core)
        )
        norm_factors_target = self._calculate_normalisation_factor(target)
        # remove slices with few particles
        norm_factors_target = jnp.where(
            target.long_profile < 0.001 * target.nmax, 0, norm_factors_target
        )

        spectral_params_target = self._get_spectra(target.xmax)
        correction_factors_target = self._get_correction_factors(
            spectral_params_target, ant_viewing_angles
        )

        # same shape as amplitudes, {GEO, CE} x ANT x FREQ x SLICES
        target_amplitudes = (
            self.amplitudes
            * norm_factors_target[:, None, None, :]
            / ant_distances_target[None, :, None, :]
        )

        # take into account corresction factors
        target_amplitudes /= jnp.where(
            correction_factors_target == 0, 1.0, correction_factors_target
        )

        synthesised_traces = jnp.fft.irfft(
            target_amplitudes * jnp.exp(1j * self.phases),
            norm="ortho",
            axis=2,  # inverse FFT on frequency axis
        )  # shape same as sliced traces, {GEO, CE} x ANT x SAMPLES x SLICES

        # total synthesised trace is the sum over all slices
        total_synth = jnp.sum(
            synthesised_traces,
            axis=-1,
        )

        return total_synth

    def _calculate_distance_viewing_angles(
        self: Self,
        zenith: float,
        azimuth: float,
        core : np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Calculate the viewing angles of the saved antenna's with respect to the slice, as well as their distance to this slice.

        Parameters
        ----------
        zenith : float
            the zenith angle in radians
        azimuth : float
            the azumithal angle in radians.

        Return
        ------
        vangles, distances : np.ndarray
            tuple of viewing angles (units in Cherenkov angle) and distances (units of m)
            for all antennas
        """
        # set the observation level based on the last entry ofg the core
        self.atm.obs_lvl = core[2] / units.cm  # (need to convert from internal units to m)
        # geometric distance from each slice, shape of ANT x SLICES x 3
        dis_from_slices = jnp.expand_dims(
            self.atm.get_geometric_distance_grammage(self.grammages, zenith / units.rad)
            * units.m,
            axis=(0, 2),
        )

        # shower axis as a unit vector, also with shape of ANT x SLICES x 3
        unit_shower_axis = jnp.expand_dims(
            spherical_to_cartesian(zenith / units.rad, azimuth / units.rad), axis=(0, 1)
        )

        # slices as vectors, shape with ANT x SLICES x 3
        slice_vectors = unit_shower_axis * dis_from_slices

        # shape of ANT x SLICES x 3, need to expand antenna positions since
        # only defined as ANT x 3
        slice_to_ant_vectors = self.ant_positions_ground[:, None, :] - (slice_vectors + jnp.expand_dims(core, axis=(0,1)))

        # viewing angles and distances returns ANTs x SLICES
        vangles = (
            angle_between(slice_to_ant_vectors, -1 * slice_vectors)
            / self.atm.get_cherenkov_angle(self.grammages, zenith / units.rad)[None, :]
            * units.rad
        )
        distances = jnp.linalg.norm(slice_to_ant_vectors, axis=-1)

        return vangles, distances

    def _calculate_normalisation_factor(self: Self, shower: BaseShower) -> np.ndarray:
        """
        Calculate the normalisation factor based on the atmospheric properties.

        Parameters
        ----------
        shower :  smiet.jax.io.base_shower.BaseShower
            the shower object containing the geometry (zenith, azimuth), geomagnetic angle
            and the longitudinal profile (nparts_per_slice)
        """
        # normalisation factors
        # first entry for normlisation of geomagnetic emission using geomagnetic angle / density
        # second entry same for C-E emission, which is just sin(cherenkov angle)
        # also expand dimensions of nparts per slice to get shape of {GEO,CE} x SLICES
        norm_factors = jnp.array(
            [
                jnp.sin(shower.geomagnetic_angle)
                / self.atm.get_density(self.grammages, shower.zenith / units.rad),
                jnp.sin(
                    self.atm.get_cherenkov_angle(
                        self.grammages, shower.zenith / units.rad
                    )
                    * units.rad
                ),
            ]
        ) * jnp.expand_dims(shower.long_profile, axis=0)

        self.logger.debug("Computed normalisation factors")

        return norm_factors

    def save_template(
        self: Self,
        template_file: str = "default_template.h5",
        save_dir: str = os.path.join(os.path.dirname(__file__), "..", "templates"),
    ) -> None:
        """
        Save the internal state of the synthesis class to disk.

        Parameters
        ----------
        template_file : str, default='default_template.h5'
            the file to save the template into
        save_dir : str, default='smiet/templates'
            the directory to save the template into
        """
        with h5py.File(os.path.join(save_dir, template_file), "w") as f:
            prop_grp = f.create_group("shower")
            prop_grp.create_dataset("zenith", data=self.template_information["zenith"])
            prop_grp.create_dataset(
                "azimuth", data=self.template_information["azimuth"]
            )
            prop_grp.create_dataset(
                "magnetic_field_vector", data=self.template_information["magnetic_field_vector"]
            )
            prop_grp.create_dataset(
                "geomagnetic_angle", data=self.template_information["geomagnetic_angle"]
            )
            prop_grp.create_dataset("xmax", data=self.template_information["xmax"])
            prop_grp.create_dataset("nmax", data=self.template_information["nmax"])
            prop_grp.create_dataset("x0", data=self.template_information["x0"])
            prop_grp.create_dataset("lmbda_params", data=self.template_information["lmbda_params"])
            prop_grp.create_dataset("core", data=self.template_information["core"])
            prop_grp.create_dataset("long_profile", data=self.template_information["long_profile"])

            ant_grp = f.create_group("antennas")
            ant_grp.create_dataset("ant_names", data=self.ant_names)
            ant_grp.create_dataset("ant_positions_ground", data=self.ant_positions_ground)
            ant_grp.create_dataset("ant_positions_vvB", data=self.ant_positions_vvB)
            ant_grp.create_dataset("ant_time_axes", data=self.ant_time_axes)

            freq_grp = f.create_group("frequencies")
            freq_grp.create_dataset("frequency_range", data=self.frequency_range)
            freq_grp.create_dataset("frequencies", data=self.frequencies)
            freq_grp.create_dataset("frequency_mask", data=self.freq_range_mask)
            freq_grp.create_dataset("trunc_frequency", data=self.truncated_frequencies)
            freq_grp.create_dataset("n_samples", data=self.n_samples)

            spect_grp = f.create_group("spect_params")
            spect_grp.create_dataset("spectral_coeffs", data=self.spectral_coeffs)
            spect_grp.create_dataset("viewing_angles", data=self.viewing_angles)

            slice_grp = f.create_group("atm_slice")
            slice_grp.create_dataset("grammages", data=self.grammages)
            slice_grp.create_dataset("nr_slices", data=self.nr_slices)

            templ_grp = f.create_group("template")
            templ_grp.create_dataset("amplitudes", data=self.amplitudes)
            templ_grp.create_dataset("phases", data=self.phases)

    def truncate_atmosphere(self : Self, starting_grammage : float = 200) -> None:
        """
        Truncate the starting point of the atmosphere grid, and subsequent arrays used for 
        the synthesis process.

        Parameters
        ----------
        starting_grammage : float, default=200
            the grammage in which we want to start the atmospheric grid,
            i.e. where we want to truncate from.
        
        Returns
        -------
        None, but all objects related to the slices will be truncated.
        """
        truncated_gram_idces = jnp.argwhere(self.grammages > starting_grammage)
        self.amplitudes = jnp.squeeze(self.amplitudes[...,truncated_gram_idces], axis=-1)
        self.phases = jnp.squeeze(self.phases[...,truncated_gram_idces], axis=-1)
        self.grammages = jnp.squeeze(self.grammages[truncated_gram_idces], axis=-1)
        self.nr_slices = len(self.grammages)

    def load_template(
        self: Self,
        template_file: str = "default_template.h5",
        save_dir: str = os.path.join(os.path.dirname(__file__), "..", "templates"),
    ) -> None:
        """
        Load the template from a saved state, as done by save_template().

        Parameters
        ----------
        template_file : str, default='default_template.h5'
            the file to save the template into
        save_dir : str, default='smiet/templates'
            the directory to save the template into
        """
        file_path = os.path.join(save_dir, template_file)
        # verify that the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Template file {file_path} does not exist.")

        with h5py.File(file_path, "r") as f:
            self.ant_names = f["antennas/ant_names"][()]
            self.ant_positions_ground = f["antennas/ant_positions_ground"][()]
            self.ant_positions_vvB = f["antennas/ant_positions_vvB"][()]
            self.ant_time_axes = f["antennas/ant_time_axes"][()]
            self.n_antennas = len(self.ant_names)

            self.frequency_range = f["frequencies/frequency_range"][()]
            self.frequencies = f["frequencies/frequencies"][()]
            self.freq_range_mask = f["frequencies/frequency_mask"][()]
            self.truncated_frequencies = f["frequencies/trunc_frequency"][()]
            self.n_samples = f["frequencies/n_samples"][()]

            self.spectral_coeffs = f["spect_params/spectral_coeffs"][()]
            self.viewing_angles = f["spect_params/viewing_angles"][()]

            self.grammages = f["atm_slice/grammages"][()]
            self.nr_slices = f["atm_slice/nr_slices"][()]

            self.amplitudes = f["template/amplitudes"][()]
            self.phases = f["template/phases"][()]

            self.template_information = {
                "zenith": f["shower/zenith"][()],
                "azimuth": f["shower/azimuth"][()],
                "magnetic_field_vector" : f["shower/magnetic_field_vector"][()],
                "geomagnetic_angle": f["shower/geomagnetic_angle"][()],
                "xmax": f["shower/xmax"][()],
                "nmax": f["shower/nmax"][()],
                "x0": f["shower/x0"][()],
                "lmbda_params": f["shower/lmbda_params"][()],
                "core" : f["shower/core"][()],
                "long_profile" : f["shower/long_profile"][()]
            }

    def get_time_axis(self: Self) -> jax.Array:
        """
        Get the time axis for all antennas.

        Returns
        -------
        time_axis : np.ndarray
            The time axis for each antenna, shaped as (# antennas, # time samples)

        """
        return self.ant_time_axes

    def get_ant_names(self: Self) -> list[str]:
        """
        Get the names of all internal antennas.

        Returns
        -------
        ant_names : list of str

        """
        return self.ant_names
