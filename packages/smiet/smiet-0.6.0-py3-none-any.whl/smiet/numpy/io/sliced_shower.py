import logging

import h5py
import numpy as np

from typing_extensions import Self, Tuple, Union

from ..utilities import e_to_geo_ce
from .coreas_shower import CoreasShower
from smiet import units


class SlicedShower(CoreasShower):
    """
    This class can be used to read in an HDF5 file of sliced CoREAS simulation.

    It can read in the traces of all slices for a given antenna and return them in a Numpy array.
    Note that the implementation assumes that the antenna's in each slice have the same physical position
    and are named identically apart from a suffix 'xN', where N is the grammage at the **bottom** of the slice.
    The antenna names are inferred by splitting the antenna names on the 'x' character, taking the first part
    and adding them all to a set to removes doubles.
    The number of slices is then calculated as the number of observers in the file, divided by the number of
    unique antenna names (i.e. the length of the set).
    Finally, the antenna positions are added to a structured array by looping over all unique antenna names,
    adding `x{slice_grammage}` (of which the value is inferred from the longitudinal profiel) at the end and
    looking at the position attribute. This structured array is then sorted by distance to the core, to ensure
    consistency across read-ins.

    Parameters
    ----------
    file_path : str
        The path to the HDF5 file
    gdas_file : str, optional
        GDAS file to be used for the Atmosphere object. See :obj:`smiet.numpy.coreas_shower.CoreasShower`
        for more info.

    Attributes
    ----------
    antenna_names : set
        The set of all antenna names present in this shower
    antenna_array : np.ndarray
        A structured array containing for each antenna the name and position on ground.
        It contains the fields 'name' and 'position'.
    nr_of_slices : int
        The number of slices in the shower
    """
    def __init__(self, file_path, gdas_file=None):
        # Set self.antenna_names to something other than None, to avoid reading in the antennas in the parents init
        self.antenna_names = set()
        super().__init__(file_path, gdas_file=gdas_file)

        self.logger = logging.getLogger("smiet.numpy.io.SlicedShower")

        with h5py.File(self._file) as file:
            self._read_antennas(file)

            # Do not use the GH parameter from Shower fit, but rather those from the file
            # in order: [N, X0, Xmax, p0, p1, p2] (p0,p1,p2 are the polynomial coefficients in denominator for lambda)
            self._GH_parameters = file["atmosphere"].attrs["Gaisser-Hillas-Fit"]

            # Count number of slices
            self.nr_of_slices = len(file["CoREAS"]["observers"].keys()) // len(self.antenna_names)

    def _read_antennas(self, file):
        self.logger.info(f"Reading antennas from {file.name}...")

        # Extract antenna information
        self.antenna_names = set(
            [key.split("x")[0] for key in file["CoREAS"]["observers"].keys()]
        )

        # Trace length can be longer than coreas settings
        self._trace_length = len(
            file["CoREAS"]["observers"][
                f"{next(iter(self.antenna_names))}x{int(self._slice_grammage)}"
            ]
        )

        # Create the antenna array, which is a structured array containing the name and position of each antenna
        self._make_antenna_array({
            ant_name: file["CoREAS/observers"][f"{ant_name}x{int(self.slice_grammage)}"].attrs["position"] * units.cm
            for ant_name in self.antenna_names
        })

        # And sort the antennas, such that the order is always the same
        self._sort_antenna_array()

    def get_trace(
        self: Self, ant_name: str, return_start_time: bool = False
    ) -> Union[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Get the traces from all slices for a given antenna, in GEO/CE components.

        Notes
        -----
        The traces are converted to GEO/CE components.

        Parameters
        ----------
        ant_name : str
            The name of the antenna. Must be the same as the key in the HDF5!
        return_start_time : bool, default=False
            If True, an array containing the time of the first sample of each slice is returned

        Returns
        -------
        traces_geo : np.ndarray
            The geomagnetic traces, shaped as (slices, samples)
        traces_ce : np.ndarray
            The charge-excess traces, shaped as (slices, samples)
        traces_start_times : np.ndarray (returned only if return_start_times is True)
            The time of the first sample of each trace
        """
        if ant_name not in self.antenna_names:
            raise ValueError(f"Antenna name {ant_name} is not present in shower")

        traces_geo = np.zeros((self.nr_of_slices, self._trace_length))
        traces_ce = np.zeros((self.nr_of_slices, self._trace_length))
        traces_start_times = np.zeros((self.nr_of_slices,))
        for i_slice in range(self.nr_of_slices):
            g_slice = (i_slice + 1) * int(self._slice_grammage)
            traces_geo[i_slice], traces_ce[i_slice], traces_start_times[i_slice] = self.get_trace_slice(
                ant_name, g_slice, return_start_time=True
            )

        if return_start_time:
            return traces_geo, traces_ce, traces_start_times

        return traces_geo, traces_ce

    def get_trace_slice(self, ant_name, slice_value, return_start_time=False):
        """
        Similar to :func:`get_trace`, but only gets the traces for a single slice in GEO/CE components.

        Parameters
        ----------
        slice_value : int
            The grammage of the slice. Must exist in the HDF5.
        ant_name : str
            The name of the antenna. Must be the same as the key in the HDF5!
        return_start_time : bool, default=False
            If True, an array containing the time of the first sample of each slice is returned

        Returns
        -------
        trace_geo : np.ndarray
            The geomagnetic trace
        trace_ce : np.ndarray
            The charge-excess trace
        trace_start_time : np.ndarray (returned only if return_start_times is True)
            The time of the first sample of the trace
        """
        if ant_name not in self.antenna_names:
            raise ValueError(f"Antenna name {ant_name} is not present in shower")

        transformer = self.get_transformer()
        trace_slice_ground, trace_time_axis = self.get_trace_raw(f'{ant_name}x{slice_value}')
        trace_slice_vvB = transformer.transform_to_vxB_vxvxB(trace_slice_ground).T

        # unit of pos does not matter, this is divided away
        antenna_vvB = self.get_antenna_position_showerplane(ant_name)
        trace_geo, trace_ce = e_to_geo_ce(trace_slice_vvB, *antenna_vvB[:2])

        if return_start_time:
            return trace_geo, trace_ce, trace_time_axis[0]

        return trace_geo, trace_ce

    def get_trace_slice_on_sky(self, ant_name, slice_value, return_start_time=False):
        """
        Similar to :func:`get_trace_slice`, but the traces are converted to on-sky components
        instead of GEO/CE components.

        Parameters
        ----------
        slice_value : int
            The grammage of the slice. Must exist in the HDF5.
        ant_name : str
            The name of the antenna. Must be the same as the key in the HDF5!
        return_start_time : bool, default=False
            If True, an array containing the time of the first sample of each slice is returned

        Returns
        -------
        trace_geo : np.ndarray
            The geomagnetic trace
        trace_ce : np.ndarray
            The charge-excess trace
        trace_start_time : np.ndarray (returned only if return_start_times is True)
            The time of the first sample of the trace
        """
        if ant_name not in self.antenna_names:
            raise ValueError(f"Antenna name {ant_name} is not present in shower")

        transformer = self.get_transformer()
        trace_slice_ground, trace_time_axis = self.get_trace_raw(f'{ant_name}x{slice_value}')
        trace_slice_on_sky = transformer.transform_from_ground_to_onsky(trace_slice_ground).T

        if return_start_time:
            return trace_slice_on_sky, trace_time_axis[0]

        return trace_slice_on_sky


class SlicedShowerCherenkov(CoreasShower):
    """
    This class can be used to read in an HDF5 file of sliced CoREAS simulation, where every slice has
    the same number of antennas.

    It differs from :obj:`SlicedShower` in that it does not assume that all observers have the same
    position. Rather, it only assumes that each slice has the same number of observers.
    The antenna names are taken to be all observer names in HDF5 (they are still stored in a set,
    but this should not change anything because the observer names in CoREAS should be unique).
    The ``antenna_array`` is created by looping over all antenna names and extracting the position attribute.
    It is also sorted by distance to the core, to ensure it is always the same when reading in a shower.
    To calculate the number of slices, it divides the number of observers by the number of observers
    whose name ends with the slice grammage extracted from the longitudinal profile.

    Its primary use case is for sliced simulation where the antennas where all place under the same
    Cherenkov angle in each slice.

    Parameters
    ----------
    file_path : str
        The path to the HDF5 file
    gdas_file : str, optional
        GDAS file to be used for the Atmosphere object. See :obj:`smiet.numpy.coreas_shower.CoreasShower`
        for more info.

    Attributes
    ----------
    antenna_names : set
        The set of all antenna names present in this shower
    antenna_array : np.ndarray
        A structured array containing for each antenna the name and position on ground.
        It contains the fields 'name' and 'position'.
    nr_of_slices : int
        The number of slices in the shower
    """
    def __init__(self, file_path, gdas_file=None):
        super().__init__(file_path, gdas_file=gdas_file)

        self.logger = logging.getLogger("smiet.numpy.io.SlicedShowerCherenkov")

        with h5py.File(self._file) as file:
            # Do not use the GH parameter from Shower fit, but rather those from the file
            self._GH_parameters = file["atmosphere"].attrs["Gaisser-Hillas-Fit"]

            # Count number of slices
            self.nr_of_slices = len(file["CoREAS"]["observers"].keys()) // len(
                [el for el in file["CoREAS"]["observers"].keys() if el.split('x')[1] == str(int(self.slice_grammage))])

    def get_trace_slice(self, ant_name, slice_gram=None, return_start_time=False):
        """
        Retrieves the traces for an observer and converts them to GEO/CE components.

        Parameters
        ----------
        ant_name : str
            The name of the observer as used in the HDF5 file
        slice_gram : None
            This variable  is not used, but is kept to mirror the method of SlicedShower,
            which allows this class to be used in TemplateSynthesis
        return_start_time : bool, default=False
            If True, an array containing the time of the first sample of each slice is returned

        Returns
        -------
        trace_geo : np.ndarray
            The geomagnetic trace
        trace_ce : np.ndarray
            The charge-excess trace
        trace_start_time : np.ndarray (returned only if return_start_times is True)
            The time of the first sample of the trace
        """
        if ant_name not in self.antenna_names:
            raise ValueError(f"Antenna name {ant_name} is not present in shower")

        transformer = self.get_transformer()
        trace_slice_ground, trace_time_axis = self.get_trace_raw(f'{ant_name}')
        trace_slice_showerplane = transformer.transform_to_vxB_vxvxB(trace_slice_ground).T

        # unit of pos does not matter, this is divided away
        antenna_showerplane = self.get_antenna_position_showerplane(ant_name)
        trace_geo, trace_ce = e_to_geo_ce(trace_slice_showerplane, *antenna_showerplane[:2])

        if return_start_time:
            return trace_geo, trace_ce, trace_time_axis[0]

        return trace_geo, trace_ce
