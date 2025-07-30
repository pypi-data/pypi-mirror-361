import logging

import h5py
import numpy as np

import radiotools.atmosphere.models as models

from .base_shower import Shower, CoreasHDF5
from smiet import units


class CoreasShower(Shower, CoreasHDF5):
    """
    A class to read in a CoREAS shower from an HDF5 file.

    Whereas the :class:`smiet.numpy.io.CoreasHDF5` class provides the basic functionality to
    read in the settings and the shower data from a CoREAS HDF5 file, this class extends it to provide
    with the functionality from the :class:`smiet.numpy.io.Shower` class. This allows you to
    interact with the antennas more easily, as the positions are more readily accessible. Also, the
    geometry is included such that a coordinate transformation object can be created from the shower.

    Parameters
    ----------
    file_path : str
        The path to the CoREAS HDF5 file
    gdas_file : str, optional
        If provided, the atmosphere will be created using this GDAS file. This will take
        precedence over the atmosphere model specified in the simulation settings.
    """
    def __init__(self, file_path, gdas_file=None):
        CoreasHDF5.__init__(self, file_path)
        Shower.__init__(self)

        self.logger = logging.getLogger("smiet.numpy.io.CoreasShower")

        # Read in the shower settings from the HDF5 file
        self.magnet = self.corsika_settings['magnetic_field']
        self.geometry = (self.corsika_settings['zenith'], self.corsika_settings['azimuth'])
        self.core = self.coreas_settings['core_coordinate']
        self.long = self.get_long_profile()

        # Check if we can create the atmosphere
        if gdas_file is not None:
            self.logger.info(f"Creating non-curved Atmosphere object with GDAS file {gdas_file}")
            self.atmosphere = models.Atmosphere(
                gdas_file=gdas_file,
                curved=False
            )
        elif self.corsika_settings['atmosphere_model'] in models.atm_models.keys():
            self.logger.info(
                f"Creating non-curved Atmosphere object with model {self.corsika_settings['atmosphere_model']} and"
                f"refractive index at sea level n0={self.coreas_settings['n0']}"
            )
            self.atmosphere = models.Atmosphere(
                model = self.corsika_settings['atmosphere_model'],
                n0 = self.coreas_settings['n0'],
                curved=False
            )
        else:
            self.logger.error(
                f"Atmosphere model {self.corsika_settings['atmosphere_model']} not supported. "
                "Please provide a valid atmosphere model or a GDAS file."
            )

        # To be assigned later
        self.antenna_names = None
        self.antenna_array = None
        self._trace_length = None

        with h5py.File(self._file) as file:
            self._read_antennas(file)

    def _read_antennas(self, file):
        # If the antenna names have already been set (in child class for example),
        # this function should not be executed
        if self.antenna_names is not None:
            return

        self.logger.info(f"Reading antennas from {file.name}...")

        self.antenna_names = set(file["CoREAS/observers"])

        self._trace_length = len(
            file["CoREAS"]["observers"][
                f"{next(iter(self.antenna_names))}"
            ]
        )

        # Create the antenna array, which is a structured array containing the name and position of each antenna
        self._make_antenna_array({
            ant_name: file["CoREAS/observers"][ant_name].attrs["position"] * units.cm
            for ant_name in self.antenna_names
        })

        # And sort it, such that the order is always the same
        self._sort_antenna_array()

    def _make_antenna_array(self, observers_pos: dict):
        self.antenna_array = np.zeros(
            len(self.antenna_names),
            dtype=np.dtype([
                ('name', 'U20'),
                ('position', 'f8', 3),
            ])
        )
        for idx, ant in enumerate(observers_pos.items()):
            self.antenna_array[idx] = (
                ant[0],
                ant[1],
            )

        # Convert positions to our CS
        self.antenna_array['position'] = self.antenna_array['position'][:, [1, 0, 2]]
        self.antenna_array['position'][:, 0] *= -1  # west -> east

    def _sort_antenna_array(self):
        """
        Sort the antenna array by distance to the core.

        This function ensures that the order of the ``antenna_array`` is always the same when reading in
        a particular shower.
        """
        distance_to_core = np.linalg.norm(
            (self.core - self.antenna_array['position']), axis=-1
        )

        first_axis = self.antenna_array['position'][:, 0]

        # Round the distance_to_core to be sure to recognise the rings of starshape,
        # even with small numerical errors. Sort by distance, using first axis as
        # the tie-breaker
        self.antenna_array = self.antenna_array[np.lexsort((first_axis, np.round(distance_to_core, 2)))]

    def get_antenna_position(self, ant_names):
        """
        Get the position of the antennas in `ant_names` on the ground.

        The position is returned in our coordinate system, where the x-axis points to the magnetic east,
        the y-axis to the magnetic north and the z-axis up.

        Parameters
        ----------
        ant_names : str or list of str
            Either a single antenna names or a list of antenna names for which to retrieve the positions.
            All names must be present in ``SlicedShower.antenna_names``!

        Returns
        -------
        antenna_ground : np.ndarray
            The positions of the antennas in `ant_names`.
        """
        if isinstance(ant_names, (str, np.str_)):
            antenna_ground = self.antenna_array['position'][self.antenna_array['name'] == ant_names]
        else:
            antenna_idx = [np.nonzero(self.antenna_array['name'] == ant_name)[0][0] for ant_name in ant_names]
            antenna_ground = self.antenna_array['position'][antenna_idx]

        return antenna_ground

    def get_antenna_position_showerplane(self, ant_names):
        r"""
        Get the position of the antennas in `ant_names` in the shower plane.

        The shower plane coordinate system is that from ``radiotools``,
        so the x-axis points along the :math:`\vec{v} \times \vec{B}` direction,
        the y-axis along :math:`\vec{v} \times ( \vec{v} \times \vec{B} )`
        direction and the z-axis along :math:`\vec{v}`.

        Parameters
        ----------
        ant_names : str or list of str
            Either a single antenna names or a list of antenna names for which to retrieve the positions.
            All names must be present in ``SlicedShower.antenna_names``!

        Returns
        -------
        antenna_showerplane : np.ndarray
            The position of the antennas in the shower plane.
        """
        transformer = self.get_transformer()

        antenna_ground = self.get_antenna_position(ant_names)  # shape (n_antennas, 3)
        antenna_showerplane = transformer.transform_to_vxB_vxvxB(antenna_ground, core=self.core)

        return antenna_showerplane
