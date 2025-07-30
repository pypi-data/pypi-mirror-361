import logging
from typing_extensions import Self, Tuple, Union

import numpy as np
import h5py
import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp
from scipy.constants import c as c_vacuum

from jax_radio_tools import units, trace_utils, shower_utils
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


class CoreasShower(BaseShower):
    """
    Class to read in showers from CoREAS simulations stored in HDF5 files.

    Parameters
    ----------
    file_path : str
        Path to the HDF5 file containing the CoREAS simulation data.
    """

    def __init__(
        self: Self, file_path: str
    ) -> None:
        super().__init__()
        self.__file = file_path  # input file path

        self.__trace_length = None
        self.__delta_t = None

        self.ant_names = None
        self.ant_dict = {}

        self.ant_positions_ground = None

        self.__parse_hdf5()

    def __parse_hdf5(
        self: Self,
    ) -> None:
        file = h5py.File(self.__file)

        # longitudinal profile data
        long_data = file["atmosphere"]["NumberOfParticles"][:]

        self.grammages = long_data[:, 0]
        self.long_profile = np.sum(long_data[:, 2:4], axis=1)

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

        # get (EM) energy
        self.energy = file["inputs"].attrs["ERANGE"][0] * units.GeV
        self.primary = file["inputs"].attrs["PRMPAR"]  # integer stored for convenience

        # antenna positions at the ground
        self.ant_positions_ground = np.array(
            [
                file["CoREAS"]["observers"][f"{ant_name}"].attrs["position"] * units.cm
                for ant_name in list(file["CoREAS"]["observers"].keys())
            ]
        )  # antennas x 3

        # the observer data containing both timing and trace information
        observers = np.array(
            [
                file["CoREAS"]["observers"][f"{ant_name}"][:]
                for ant_name in list(file["CoREAS"]["observers"].keys())
            ]
        )  # antennas x samples x 4

        # map it to the correct shape of 4 x ANT x SAMPLES
        observers = np.moveaxis(observers, (0, 1, 2), (1, 2, 0))

        # divide into trace times & actual E-field slices
        self.trace_times = observers[0, ...] * units.s  # (Nant, Nsamples)
        self.efield_traces = observers[1:, ...]  # (Npol, Nant, Nsamples)
        self.trace_length = self.efield_traces.shape[2]

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

        self.efield_traces = self.efield_traces[[1, 0, 2], ...]
        self.efield_traces[0, ...] *= -1
        self.efield_traces *= conversion_fieldstrength_cgs_to_SI  # convert traces from cgs to SI manually (due to electric charge shenanigans)

        # 2. shift azimuth into NRR coordinate system
        self.zenith = np.deg2rad(file["inputs"].attrs["THETAP"][0]) * units.rad
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

        # 4. define transformation container
        self.transformer = cstrafo(
            self.zenith / units.rad,
            self.azimuth / units.rad,
            magnetic_field_vector=self.magnetic_field_vector,
        )
         # core vertical is FORCED to be at observation level here
        # TODO: add some warning about this?
        self.core[2] = file["inputs"].attrs["OBSLEV"] * units.cm

        # 5. transform the position and traces from magnetic to geographic north
        # self.ant_positions_ground[:,2] = file["inputs"].attrs["OBSLEV"] * units.cm
        self.ant_positions_ground = (
            self.transformer.transform_from_magnetic_to_geographic(
                self.ant_positions_ground
            )
        )
        # NB: double transpose needed since last dimension must be the position vector, but we want to retain
        # the same shape as before
        self.efield_traces = self.transformer.transform_from_magnetic_to_geographic(
            self.efield_traces.T
        ).T

        self.efield_traces = self.transformer.transform_from_ground_to_onsky(
            self.efield_traces.T
        ).T

        # NOTE: FORCE r-component to be zero, since we do not use this and
        # this can impact the conversion of the traces to the on-sky coordinates
        # when comparing with template synthesis
        self.efield_traces = self.efield_traces.at[0, ...].set(0.0)

        # distance from the shower core
        self.dis_to_core = np.linalg.norm(
            (self.get_antennas_showerplane()[:,:2]), axis=-1
        )


    def __sort_antenna_indices(self: Self) -> None:
        """Sort the trace and antenna positions based on increasing distance from the core and azimuth."""
        # 7. finally sort based on increasing distance to core & increasing azimuth.
        # first sort based on increasing distance
        self.ant_positions_ground = self.ant_positions_ground[
            np.argsort(self.dis_to_core), :
        ]
        self.efield_traces = self.efield_traces[:, np.argsort(self.dis_to_core), :]
        self.trace_times = self.trace_times[np.argsort(self.dis_to_core), :]
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
        self.efield_traces = self.efield_traces[:, ordered_idces, :]
        self.trace_times = self.trace_times[ordered_idces, :]
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
    
    def get_efield_traces_vB_vvB(self : Self) -> np.ndarray:
        """
        Get the traces from traces at the ground to vB/vvB components.
        
        Returns
        -------
        traces_vB_vvB : np.ndarray
            The traces in the shower plane, transformed to vxB and vxvxB components.
            Shape is (2, Nant, Nsamples), where Nant is the number of antennas and Nsamples is the number of samples.
        """
        ant_position_vvB = self.get_antennas_showerplane()

        traces_ground = self.transformer.transform_from_onsky_to_ground(
            self.efield_traces.T
        ).T

        trace_vvB = self.transformer.transform_to_vxB_vxvxB(
            traces_ground.T, core=self.core
        ).T
        return trace_vvB

    def get_efield_traces_geoce(self: Self) -> np.ndarray:
        """
        Get the traces from traces at the ground to GEO/CE components.
        
        Returns
        -------
        traces_geo_ce : np.ndarray
            The traces in the shower plane, transformed to GEO and CE components.
            Shape is (2, Nant, Nsamples), where Nant is the number of antennas and Nsamples is the number of samples.
        """
        # transform antenna and trace to shower plane

        ant_position_vvB = self.get_antennas_showerplane()

        traces_ground = self.transformer.transform_from_onsky_to_ground(
            self.efield_traces.T
        ).T

        trace_vvB = self.transformer.transform_to_vxB_vxvxB(
            traces_ground.T, core=self.core
        )
        # now convert trace to respective components
        traces_geo, traces_ce = e_to_geo_ce(
            trace_vvB, ant_position_vvB[None, :, 0], ant_position_vvB[None, :, 1]
        )
        return np.array([traces_geo.T, traces_ce.T])
    
    def transform_profile_to_origin(self : Self, origin_grammages : jax.typing.ArrayLike) -> None:
        """
        Transform the longitudinal profile to match those of the origin shower.

        This is needed such that the grammages of the origin and target match.

        Parameters
        ----------
        origin_grammages : jax.typing.ArrayLike
            The grammages of the origin shower.
        """
        self.long_profile = jnp.interp(
            x=origin_grammages, xp=self.grammages, fp=self.long_profile
        )
        self.grammages = origin_grammages

    def remove_antennas(self, ant_idx_min : int = 0, ant_idx_max : int = 90) -> None:
        """
        Remove antennas from the data traces.

        Parameter:
        ----------
        ant_idx_min : float
            remove all antennas below this antenna index
        ant_idx_max : float
            remove all antennas above this antenna index
        """
        # d_core_mask = (self.dis_to_core > d_core_min) & (self.dis_to_core < d_core_max)
        d_core_mask = (np.indices(self.dis_to_core.shape)[0] >= ant_idx_min) & (np.indices(self.dis_to_core.shape)[0] < ant_idx_max)
        self.efield_traces = self.efield_traces[:, d_core_mask, :]
        self.trace_times = self.trace_times[d_core_mask, :]
        self.ant_positions_ground = self.ant_positions_ground[d_core_mask, :]
        self.dis_to_core = self.dis_to_core[d_core_mask]

    def apply_trace_cuts(
        self: Self,
        f_min : float = 30 * units.MHz,
        f_max : float = 80 * units.MHz,
        delta_t: float = 2 * units.ns,
        sample_axis: int = 2,
        sample_time_axis: int = 1,
    ) -> None:
        """
        Apply resampling, centering, timing windows, and filtering to the trace.

        Parameters
        ----------
        f_min : float, default=30MHz
            minimum frequency in MHz
        f_max : float, default=80MHz
            maximum frequency in MHz
        delta_t : float, default=2ns
            timing resolution in ns
        sample_axis : int, default=2
            the axis in which the samples are
        sample_time_axis : int, default=1
            the axis in which the sample times are
        """
        traces_zero_padded, times_padded = trace_utils.zero_pad_traces(
            self.efield_traces,
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
        # now downsample
        traces_resampled, times_resampled = trace_utils.resample_trace(
            traces_filtered,
            dt_resample=delta_t,
            dt_sample=self.delta_t,
            sample_axis=sample_axis,
            times=times_padded,
            sample_time_axis=sample_time_axis,
        )

        self.trace_length = traces_resampled.shape[sample_axis]
        self.delta_t = delta_t
        self.efield_traces = traces_resampled
        self.trace_times = times_resampled
