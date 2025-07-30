import logging
from typing_extensions import Self, Tuple, Union

import numpy as np
import h5py
import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp
from scipy.constants import c as c_vacuum

from smiet import units
from jax_radio_tools import trace_utils, shower_utils
from jax_radio_tools.atmosphere import Atmosphere
from jax_radio_tools.coordinate_transformations import (
    cstrafo,
    e_to_geo_ce,
    spherical_to_cartesian,
    conversion_fieldstrength_cgs_to_SI,
    get_normalized_angle
)
from .base_shower import BaseShower

logger = logging.getLogger("smiet.jax.io")


class SlicedShower(BaseShower):
    """
    Class to read in showers from each slice from CoREAS simulations, inherited from BaseShower.

    Parameters
    ----------
    file_path : str
        The filepath to the simulation to read.
    slicing_grammage : int, default=5
        The width between atmospheric slices in g/cm^2
    """

    def __init__(
        self: Self,
        file_path: str,
        slicing_grammage: int = 5,  # not used since its read from the file itself
        gdas_file : str = "",
    ) -> None:
        super().__init__()

        self.logger = logging.getLogger("smiet.jax.io.SlicedShower")

        self.__slice_gram = slicing_grammage  # g/cm2, TODO: change how to read this since its fixed from filepath  # Not used
        self.__file = file_path  # input file path

        self.__trace_length = None
        self.__delta_t = None

        self.ant_names = None
        self.ant_dict = {}

        self.ant_positions_ground = None

        self.__parse_hdf5(gdas_file=gdas_file)

    def __parse_hdf5(
        self: Self,
        gdas_file : str,
    ) -> None:
        file = h5py.File(self.__file)

        # longitudinal profile data
        long_data = file["atmosphere"]["NumberOfParticles"][:]

        grammages = long_data[:, 0]
        long_prof = np.sum(long_data[:, 2:4], axis=1)
        obs_lev = file["inputs"].attrs["OBSLEV"] * units.cm

        # if the ATMOD value is -1, then use gdas file as atmosphere
        if file["inputs"].attrs["ATMOD"] == -1:
            self.atm = Atmosphere(observation_level=obs_lev / units.m, gdas_file = gdas_file)
        else:
            self.atm = Atmosphere(
                model=file["inputs"].attrs["ATMOD"], observation_level=obs_lev / units.m
            )
        self.zenith = np.deg2rad(file["inputs"].attrs["THETAP"][0]) * units.rad

        # filter out grammages that will reach beyond earth
        grammage_lim_mask = grammages <= self.atm.get_xmax_from_distance(
            0.0,
            self.zenith / units.rad,
        )

        self.grammages = grammages[grammage_lim_mask]
        self.long_profile = long_prof[grammage_lim_mask]

        # Gaisser-Hillas parameters
        # in particular used to set nmax and xmax
        # in order: [N, X0, Xmax, p0, p1, p2] (p0,p1,p2 are the polynomial coefficients in denominator for lambda)
        GH_parameters = np.array(
            file["atmosphere"].attrs["Gaisser-Hillas-Fit"]
        )  # GH parameters from fit
        self.nmax = GH_parameters[0]
        self.x0 = GH_parameters[1]
        self.xmax = GH_parameters[2]
        self.lmbda_params = GH_parameters[3:]

        # convert GH parameter to LR
        lmbda = np.mean(
            GH_parameters[3]
            + GH_parameters[4] * self.grammages
            + GH_parameters[5] * self.grammages**2
        )
        self.L, self.R = shower_utils.convert_GH_to_LR(
            self.xmax, GH_parameters[1], lmbda
        )

        # observer properties
        self.ant_names = list(
            sorted(
                set([key.split("x")[0] for key in file["CoREAS"]["observers"].keys()])
            )
        )

        # antenna positions at the ground
        self.ant_positions_ground = np.array(
            [
                file["CoREAS"]["observers"][f"{ant_name}x{self.__slice_gram}"].attrs[
                    "position"
                ]
                * units.cm
                for ant_name in self.ant_names
            ]
        )  # antennas x 3

        # the observer data for each slice, containing both timing and trace information
        observer_slices = np.array(
            [
                [
                    file["CoREAS"]["observers"][f"{ant_name}x{int(gram):d}"][:]
                    for ant_name in self.ant_names
                ]
                for gram in self.grammages
            ]
        )  # slices x antennas x samples x 4

        # map it to the correct shape of
        # 4 x ANT x SAMPLES x SLICE as according to numpy version
        observer_slices = np.moveaxis(observer_slices, (0, 1, 2, 3), (3, 1, 2, 0))

        # divide into trace times & actual E-field slices
        # we also do not care about the time for each slice, since they arrive at the same time
        self.trace_times = (
            observer_slices[0, ..., 0] * units.s
        )  # shape of (Nant, Nsamples), not needed but keep incase
        self.trace_slices = observer_slices[
            1:, ...
        ]  # shape of (Npol, Nant, Nsamples, Nslices)

        self.trace_length = self.trace_slices.shape[2]

        # at this stage, convert the trace and antenna positions to NRR system
        # also get the zenith, azimuth, magnetic field, and simulation core
        self.__convert_to_NRR_and_get_props(file)
        self.__sort_antenna_indices()

        self.delta_t = float(file["CoREAS"].attrs["TimeResolution"]) * units.s

        file.close()

    def __convert_to_NRR_and_get_props(self: Self, file: h5py.File) -> None:
        """
        Perform all conversions from the CORSIKA system to NRR system, and get the zenith, azimuth, magnetic field, and core while we are at it.

        The following conventions hold:
        - CORSIKA : (MagNorth, West, Vertical), orientation in counter-clockwise, +z towards observer
        - NRR : (GeoEast, GeoNorth, Vertical), orientation in counter-clockwise, +z towards observer

        So the following conversions need to be performed:
        1. Convert positions & traces into [-y, x, z]
        2. Shift the azimuthal angle by 3 pi/2 (180 flip from West -> East plus N-> E due to convention of second coordinate)
        3. Generate the magnetic field vector from the inclination and the strength read from CORSIKA,
            appropriately transforming the magnetic field vector
        4. Get the simulation core, appropriately converted to NRR system
        5. Define transformer based on new azimuthal angle and magnetic field vector
        6. transform positions & traces from magnetic to geographic coordinates

        NB: 2 and 3 are taken from NRR/modules/io/coreas/coreas.py in refactor_coreas_v3 branch
        """
        # 1. converting from NEV -> ENV
        self.ant_positions_ground = self.ant_positions_ground[:, [1, 0, 2]]
        self.ant_positions_ground[:, 0] *= -1

        self.trace_slices = self.trace_slices[[1, 0, 2], ...]
        self.trace_slices[0, ...] *= -1
        self.trace_slices *= conversion_fieldstrength_cgs_to_SI  # convert traces from cgs to SI manually (due to electric charge shenanigans)

        # 2. shift azimuth into NRR coordinate system
        self.azimuth = get_normalized_angle(
            3 * np.pi / 2 + np.deg2rad(file["inputs"].attrs["PHIP"][0])
        ) * units.rad

        # 3. define magnetic field vector
        B_incl = np.arctan2(
            file["inputs"].attrs["MAGNET"][1], file["inputs"].attrs["MAGNET"][0]
        )
        B_strength = (
            np.sqrt(np.sum(file["inputs"].attrs["MAGNET"] ** 2))
            * units.micro
            * units.tesla
        )  # TODO: check why its microtesla in NRR

        self.magnetic_field_vector = B_strength * spherical_to_cartesian(
            np.pi / 2 + B_incl, np.pi / 2
        )

        # 4. get simulation core
        self.core = (
            np.array(
                [
                    -1 * file["CoREAS"].attrs["CoreCoordinateWest"],
                    file["CoREAS"].attrs["CoreCoordinateNorth"],
                    file["CoREAS"].attrs["CoreCoordinateVertical"],
                ]
            )
            * units.cm
        )
        # core vertical is FORCED to be at observation level here
        # TODO: add some warning about this?
        self.core[2] = file["inputs"].attrs["OBSLEV"] * units.cm

        # 4. define transformation container
        self.transformer = cstrafo(
            self.zenith / units.rad,
            self.azimuth / units.rad,
            magnetic_field_vector=self.magnetic_field_vector,
        )

        # 5. transform the position and traces from magnetic to geographic north
        # self.ant_positions_ground[:,2] = file["inputs"].attrs["OBSLEV"] * units.cm
        self.ant_positions_ground = (
            self.transformer.transform_from_magnetic_to_geographic(
                self.ant_positions_ground
            )
        )
        # NB: double transpose needed since last dimension must be the position vector, but we want to retain
        # the same shape as before
        self.trace_slices = self.transformer.transform_from_magnetic_to_geographic(
            self.trace_slices.T
        ).T

        # distance from the shower core
        self.dis_to_core = np.linalg.norm(
            (self.get_antennas_showerplane()[:,:2]), axis=-1
        )

    def __sort_antenna_indices(self: Self) -> None:
        """Sort the trace and antenna positions based on increasing distance from the core and azimuth."""

        # ordered_idces = self.get_ordering_indices(self.get_antennas_showerplane()[:,0], self.get_antennas_showerplane()[:,1])
        # print(ordered_idces)
        # sorting based on distance
        self.ant_positions_ground = self.ant_positions_ground[
            np.argsort(self.dis_to_core), :
        ]
        self.trace_slices = self.trace_slices[:, np.argsort(self.dis_to_core), :, :]
        self.trace_times = self.trace_times[np.argsort(self.dis_to_core), :]
        self.ant_names = list(self.ant_names[i] for i in np.argsort(self.dis_to_core))
        self.dis_to_core = np.sort(self.dis_to_core)
        # now sort it based on azimuth for each distance
        # NOTE: key assumption applied where it is sorted based on the fact that there are 8 arms
        # when we introduce interpolator we would not need this anymore
        n_ant_per_arm = len(self.dis_to_core) // 8

        # calculate the angles
        angles = np.arctan2(
            self.get_antennas_showerplane()[:, 1], self.get_antennas_showerplane()[:, 0]
        )
        angles = np.around(angles, 15)
        angles[angles < 0] += 2 * np.pi
        # get the indices in increasing order and shift by n_arms
        # then concatenate to get the indices
        ordered_idces = [
            np.argsort(angles[int(8 * iant) : int(8 * (iant + 1))]) + 8 * iant
            for iant in range(n_ant_per_arm)
        ]
        ordered_idces = np.array(np.concatenate(ordered_idces), dtype=int)

        # finally apply to the arrays
        self.ant_positions_ground = self.ant_positions_ground[ordered_idces, :]
        self.trace_slices = self.trace_slices[:, ordered_idces, :, :]
        self.trace_times = self.trace_times[ordered_idces, :]
        self.ant_names = list(self.ant_names[i] for i in ordered_idces)
        self.dis_to_core = self.dis_to_core[ordered_idces]

    @property
    def trace_length(self: Self) -> int:
        """
        Length of the trace.
        
        Returns
        -------
        trace_length : int
            The number of samples in the trace.
        """
        return self.__trace_length

    @property
    def delta_t(self: Self) -> float:
        """
        Time resolution of the trace.
        
        Returns
        -------
        delta_t : float
            The time resolution in ns.
        """
        return self.__delta_t

    @trace_length.setter
    def trace_length(self: Self, trace_length: int) -> None:
        self.__trace_length = trace_length

    @delta_t.setter
    def delta_t(self: Self, delta_t: float) -> None:
        self.__delta_t = delta_t

    @property
    def name(self: Self) -> str:
        return self.__file.split("/")[-1].split(".")[0]

    @staticmethod
    def get_geometry(file: h5py.File) -> Tuple[float, float]:
        """Retrieve the geometry (zenith, angle) in radians."""
        raise NotImplementedError(
            "Not used anymore since we read it in the new function above."
        )
        zenith = np.deg2rad(file["inputs"].attrs["THETAP"][0]) * units.rad
        # transform to NRR convention coordinate system
        # we neglect the magnetic declination dependence of the azimuth
        azimuth = (
            3 * np.pi / 2.0 + np.deg2rad(file["inputs"].attrs["PHIP"][0])
        ) * units.rad
        # azimuth = (
        #     file["inputs"].attrs["PHIP"][0] * units.deg - 90 * units.deg
        # )  # transform to radiotools coord
        return zenith, azimuth

    def get_antennas_showerplane(self: Self) -> np.ndarray:
        """
        Get the antenna positions in shower plane.
        
        Returns
        -------
        ant_position_vB_vvB : np.ndarray
            The antenna positions in the shower plane, transformed to the NRR system.
        """
        return self.transformer.transform_to_vxB_vxvxB(
            self.ant_positions_ground, core=self.core
        )

    def apply_trace_cuts(
        self: Self,
        f_min: float = 30 * units.MHz,
        f_max: float = 80 * units.MHz,
        delta_t: float = 2 * units.ns,
        sample_axis: int = 2,
        sample_time_axis: int = 1,
    ) -> None:
        """
        Preprocess the sliced traces before performing synthesis by filtering & resampling.

        This is used to reduce the number of samples that needs to be saved when performing the
        IFT reconstruction.

        Parameters
        ----------
        f_min : float
            The minimum frequency in which we want to filter the trace
        f_max : float
            The maximum frequency in which we want to filter the trace
        delta_t : float
            the timing resolution to downsample to
        sample_axis : int, default = 2
            the axis in which the samples are located in the trace array
        sample_time_axis : int, default = 1
            the axis in which the samples are located in the time array

        Returns
        -------
        None, it will zero-pad -> filter -> resample the trace slices for synthesis.
        """
        # ensure that no anti-aliasing effects come into play by filtering
        assert 1 / (2 * delta_t) >= f_max, (
            f"Timing resolution {delta_t:.2f} will result in anti-aliasing effects. Decrease resolution or increase maximum frequency."
        )
        # add zero padding to the traces and shift it to the middle of the trace
        # here we also filter and remove the padding
        traces_zero_padded, times_padded = trace_utils.zero_pad_traces(
            self.trace_slices,
            times=self.trace_times,
            sample_axis=sample_axis,
            sample_time_axis=sample_time_axis,
            trace_sampling=self.delta_t,
            ant_time_axis=0,
        )
        traces_filtered = trace_utils.filter_trace(
            traces_zero_padded, 
            f_min=f_min,
            f_max=f_max,
            trace_sampling=self.delta_t,
            sample_axis=sample_axis,
        )
        # now resample to the desired timing resolution
        self.trace_slices, self.trace_times = trace_utils.resample_trace(
            traces_filtered,
            dt_resample=delta_t,
            dt_sample=self.delta_t,
            times=times_padded,
            sample_axis=sample_axis,
            sample_time_axis=sample_time_axis,
        )
        # need to update delta_t, trace_length, and trace times accordintly
        self.delta_t = delta_t
        self.trace_length = self.trace_slices.shape[sample_axis]

    def get_traces_geoce(self: Self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get all traces for all antennas, separated by geomagnetic and charge-excess.

        Returns
        -------
        trace_geo : jax.Array
            The geomagnetic trace in shapes ANT x SAMPLES x SLICES
        trace_ce : jax.Array
            The charge-excess trace in shapes ANT x SAMPLES x SLICES
        """
        antennas_vvB = self.get_antennas_showerplane()

        # transform from ground -> shower plane
        # shape as SLICES x SAMPLES x ANT x POS
        trace_slice_vvB = self.transformer.transform_to_vxB_vxvxB(
            self.trace_slices.T, core=self.core
        )

        # unit of pos does not matter, this is divided away
        # make the dimension of antenna positions same as the trace for multiplication
        # shape returned as SLICES x SAMPLES x ANT for geo and ce
        trace_geo, trace_ce = e_to_geo_ce(
            trace_slice_vvB,
            antennas_vvB[None, None, :, 0],
            antennas_vvB[None, None, :, 1],
        )

        # finally transpose to get the right shape
        # of ANT x SAMPLES x SLICES
        trace_geo, trace_ce = trace_geo.T, trace_ce.T

        return trace_geo, trace_ce

    def get_traces_onsky(self: Self) -> np.ndarray:
        """
        Get all traces for all antennas in on-sky coordinates (i.e. [er, etheta, ephi]).

        Returns
        -------
        traces_onsky : np.ndarray
            the traces for all antenna and slices in [Er, Etheta, Ephi] coordinates.
            Here on-sky means that the +z points towards the observer.
        """
        return self.transformer.transform_from_ground_to_onsky(self.trace_slices.T).T

    def get_coreas_settings(self: Self) -> dict:
        """Get specific configurations from the CoREAS simulation that is useful for the synthesis.

        Returns
        -------
        coreas_settings : dict
            A dictionary containing important information about the configuration of the CoREAS simulation
        """
        file = h5py.File(self.__file)

        time_resolution = float(file["CoREAS"].attrs["TimeResolution"]) * units.s

        return {"time_resolution": time_resolution}

    def filter_trace(
        self: Self,
        trace: jax.typing.ArrayLike,
        f_min: float,
        f_max: float,
        trace_axis: int = 2,
    ) -> jax.Array:
        """
        Filter the trace until we get traces that match the frequency interval.

        This implementation only works consistently with a 1-D array, but a TODO would be
        to allow this to work with multidimensional arrays.

        NB: This is here just for backwards compatibility, but it need not be here

        Parameters
        ----------
        trace : np.ndarray
            The unfiltered electric field trace.
        f_min : float
            The minimum frequency in which we want to filter the trace
        f_max : float
            The maximum frequency in which we want to filter the trace
        trace_axis : int, default = 2
            the axis in which the samples are located in the trace array

        Returns
        -------
        filtered_trace : np.ndarray
            The trace that is filtered between the frequency range [f_min, f_max]
        """
        return trace_utils.filter_trace(
            trace,
            sample_axis=trace_axis,
            f_min=f_min,
            f_max=f_max,
            trace_sampling=self.delta_t,
        )
