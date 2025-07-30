import os, shutil
import numpy as np
import h5py
from typing import Union

import radiotools.helper as hp
from radiotools.atmosphere.models import Atmosphere

from smiet import units
from smiet.corsika.generate_file_contents import (
    generate_list_file, generate_reas_file, generate_inp_file,
    generate_list_file_cherenkov,
    generate_list_file_from_positions,
)

import logging
logger = logging.getLogger("smiet.corsika.write_simulation")


__all__ = [
    "generate_simulation",
    "generate_simulation_from_hdf5",
    "write_simulation_to_file",
    "sample_primary_energy",
    "sample_zenith_angle",
    "sample_azimuth_angle",
]


CORSIKA_PARTICLE_CODES = {
    'proton': 14,
    'helium': 402,
    'carbon': 1206,
    'silicon': 2814,
    'iron': 5626,
}


# Functions to generate all files for a single simulation


def generate_simulation(
    sim_nr,
    sim_primary,
    sim_cores,
    sim_zenith=None,
    sim_azimuth=None,
    sim_energy=None,
    slice_gram=5.0 * units.g / units.cm2,
    magnetic_field='lofar',
    thinning=1e-7,
    atmosphere=17,
    core=None,
    radii=None,
    nr_of_arms=1,
    cherenkov=False,
):
    """
    Prepare the contents for the INP, LIST and REAS files for a sliced MPI simulation,
    with a star shape pattern for the antenna layout.

    One can choose to project the antennas along the shower axis or along the viewing angle by
    setting the `cherenkov` option. If this is set to True, the `radii` parameter will be interpreted
    as a list of viewing angles expressed as multiples of the slice Cherenkov angle. Otherwise,
    the `radii` parameter should be the list of radii to use in the star shape
    (use this option to generate origin showers).

    The magnetic field vector can be taken from the `radiotools.helper` module, by passing a string
    as the `magnetic_field` parameter. This variable is passed on to the
    `radiotools.helper.get_magnetic_field_vector` function. But to be consistent with the
    CORSIKA definition where the magnetic field has no East-West component, the vector x-component
    is set to zero. This ensures the simulated antennas are indeed on the (vx)vxB axis.

    The primary particle can be specified as a string, which will be converted to the corresponding
    CORSIKA particle code. As of June 2025, only proton, helium, carbon, silicon and iron primaries
    are supported (this is limited by the CORSIKA_PARTICLE_CODES dictionary).

    Parameters
    ----------
    sim_nr : int
        The number of the simulation.
    sim_primary : {'proton', 'helium', 'carbon', 'silicon', 'iron'}
        The primary particle to inject
    sim_cores : int
        The number of cores the simulation will be run on
    sim_zenith : float, optional
        The zenith angle. If not provided, the angle will be drawn from `sample_zenith_angle`.
    sim_azimuth : float, optional
        The azimuth angle. If not provided, the angle will be drawn from `sample_azimuth_angle`.
    sim_energy : float, optional
        The energy of the simulation. If not provided, the energy will be drawn from `sample_primary_energy`.
    core : list of float, default=[0, 0, 0] * units.m
        The core to use in the simulation
    slice_gram : float, default=5.0 * units.g / units.cm2
        The thickness of the atmospheric slices
    radii : list of float, default=None
        The radii of the starshape, passed to `smiet.corsika.generate_list_file`
    nr_of_arms: int, default=1
        The number of arms in the star shape pattern. This is passed to `smiet.corsika.generate_list_file`.
    cherenkov : bool, default=False
        If True, interpret `radii` as multiples of slice Cherenkov radius, and calculate antenna radii per slice
    magnetic_field : np.ndarray or str, default='lofar'
        If a string, the name of the site from which to take the magnetic field vector (using radiotools.helper).
        Otherwise, this is interpreted as the magnetic field vector (in internal units).
    thinning : float, default=1e-7
        The thinning level to use
    atmosphere : int or str, default=17
        The CORSIKA atmosphere identifier. If a string, the path to the GDAS atmosphere file.
    """
    assert sim_primary in CORSIKA_PARTICLE_CODES, f'Primary {sim_primary} not supported!'

    if core is None:
        core = np.array([0.0, 0.0, 0.0]) * units.m

    sim_zenith = sample_zenith_angle()[0] if sim_zenith is None else sim_zenith
    sim_azimuth = sample_azimuth_angle()[0] if sim_azimuth is None else sim_azimuth
    sim_primary_energy = (
        sample_primary_energy()[0] if sim_energy is None else sim_energy
    )

    atm = Atmosphere(atmosphere, curved=False)
    grammage_ground = atm.get_distance_xmax(
        sim_zenith / units.rad, 0.0, observation_level=core[2] / units.m
    )
    slice_gram /= units.g / units.cm2
    grammage_slices = np.arange(
        0.0, (grammage_ground // slice_gram + 1) * slice_gram + 1, slice_gram
    )
    grammage_slices *= units.g / units.cm2

    if type(magnetic_field) is str:
        magnetic_field_vector = hp.get_magnetic_field_vector(magnetic_field) * np.array([0, 1, 1]) * units.gauss
    else:
        magnetic_field_vector = np.asarray(magnetic_field)

    inp_file = generate_inp_file(
        sim_nr,
        sim_zenith,
        sim_azimuth,
        sim_primary_energy,
        obs_lev=core[2],
        primary=CORSIKA_PARTICLE_CODES[sim_primary],
        n_cores=sim_cores,
        thin=thinning,
        atm=atmosphere,
        magnet=magnetic_field_vector,
        slicing=slice_gram
        * (units.g / units.cm2),  # make sure it is passed in internal units!
    )
    if cherenkov:
        list_file = generate_list_file_cherenkov(
            sim_zenith,
            sim_azimuth,
            grammage_slices,
            atm,
            radii,
            magnet_vector=magnetic_field_vector,
            core=core,
            number_of_arms=nr_of_arms,
        )
    else:
        list_file = generate_list_file(
            sim_zenith,
            sim_azimuth,
            grammage_slices,
            magnet_vector=magnetic_field_vector,
            core=core,
            radii=radii,
            number_of_arms=nr_of_arms,
        )
    reas_file = generate_reas_file(sim_nr, core=core)

    return inp_file, list_file, reas_file

def generate_simulation_from_hdf5(
    base_sim_file: str,
    sim_nr: int,
    sim_cores: int,
    sim_primary: Union[str, int, None] = None,
    sim_energy: Union[float, None] = None,
    slice_gram: float = 5.0 * units.g / units.cm2,
    atm_file : Union[str, None]=None,
):
    """
    Generate simulation files for an origin shower from an existing coreas simulation.

    The geometry, primary particle type and energy are taken from the `base_sim_file`
    simulation, as well as the observation level, magnetic field and thinning level.
    If there is no GDAS atmosphere file provided, the atmosphere model number
    is also taken from the `base_sim_file`.

    Parameters
    ----------
    base_sim_file : str
        Path to the HDF5 simulation file on which we base the new simulation.
    sim_nr : int
        The number of the new simulation.
    sim_cores : int
        The number of cores the simulation will be run on
    sim_primary: str or int, default=None
        If provided, the primary particle type to use in the new simulation.
        If a string, the type is converted to the CORSIKA identification code using
        `CORSIKA_PARTICLE_CODES` dictionary. In this case the particle needs to be
        supported (see the documentation of :func:`generate_simulation`). Can also
        be an integer, in which case it is used as the CORSIKA particle code directly.
        If None, the primary particle type will be taken from the `base_sim_file`.
    sim_energy: float, default=None
        If provided, the primary energy to use in the new simulation. Otherwise,
        the energy will be taken from the `base_sim_file`.
    slice_gram : float, default=5.0 * units.g / units.cm2,
        The thickness of the atmospheric slices
    atm_file : str, default=None
        The path to the GDAS atmosphere file. If None, the atmosphere model number
        from the `base_sim_file` will be used instead, and an atmosphere file will not be used.
    """
    logger.info(f"Generating simulation from existing simulation {base_sim_file}")

    coreas_h5_reader = h5py.File(base_sim_file, "r")

    # extract the relevant parameters
    # NOTE: always make sure to read from "inputs" and not "CoREAS" attributes
    # since those are not used in the new coreas version
    sim_zenith = coreas_h5_reader["inputs"].attrs["THETAP"][0] * units.deg
    # 270 shift required since it is being applied in the inp file generator
    sim_azimuth = (coreas_h5_reader["inputs"].attrs["PHIP"][0] + 270.0) * units.deg

    sim_primary_energy = coreas_h5_reader["inputs"].attrs["ERANGE"][0] * units.GeV if sim_energy is None else sim_energy
    if sim_primary is None:
        sim_primary = int(coreas_h5_reader["inputs"].attrs["PRMPAR"])
    elif isinstance(sim_primary, str):
        sim_primary = CORSIKA_PARTICLE_CODES[sim_primary]

    sim_obs_lev = coreas_h5_reader["inputs"].attrs["OBSLEV"] * units.cm
    sim_thinning = coreas_h5_reader["inputs"].attrs["THIN"][0]

    # read in the atmosphere file as a GDAS file if it is not None
    if atm_file is not None:
        sim_atmosphere = atm_file
    else:
        sim_atmosphere = int(coreas_h5_reader["inputs"].attrs["ATMOD"])

    # for magnetic field vector, the input file generator reads [1, -2]
    # so we need to append a zero element in the first entry, then
    # negate the last element
    sim_magnetic_field_vector = np.zeros(3)
    sim_magnetic_field_vector[1:] = (
        coreas_h5_reader["inputs"].attrs["MAGNET"] * units.microtesla
    )
    sim_magnetic_field_vector[2] *= -1

    # Generate INP file
    inp_file = generate_inp_file(
        sim_nr,
        sim_zenith,
        sim_azimuth,
        sim_primary_energy,
        obs_lev=sim_obs_lev,
        primary=sim_primary,
        n_cores=sim_cores,
        thin=sim_thinning,
        atm=sim_atmosphere,
        magnet=sim_magnetic_field_vector,
        slicing=slice_gram,  # make sure it is passed in internal units!
    )

    # for generating the lst file, we need to first get the grammage slices
    atm = Atmosphere(sim_atmosphere, curved=False)

    grammage_ground = atm.get_distance_xmax(
        sim_zenith / units.rad,0.0,
        observation_level=sim_obs_lev / units.m,
    )
    slice_gram /= units.g / units.cm2
    grammage_slices = np.arange(
        0.0, (grammage_ground // slice_gram + 1) * slice_gram + 1, slice_gram
    )
    grammage_slices *= units.g / units.cm2

    # generate the LIST file
    ant_positions = np.asarray([
        obs.attrs["position"] for obs in coreas_h5_reader["CoREAS"]["observers"].values()
    ])
    ant_positions = ant_positions[:, [1, 0, 2]]
    ant_positions[:, 0] *= -1  # flip West to East to match NRR definition

    list_file = generate_list_file_from_positions(ant_positions, grammage_slices)

    # generate the REAS file
    coreas_attrs = coreas_h5_reader["CoREAS"].attrs

    core = np.array([
        -coreas_attrs["CoreCoordinateWest"],
        coreas_attrs["CoreCoordinateNorth"],
        coreas_attrs["CoreCoordinateVertical"],
    ])

    reas_file = generate_reas_file(
        sim_nr,
        n=coreas_attrs["GroundLevelRefractiveIndex"],
        time_res=coreas_attrs["TimeResolution"] * units.s,
        time_bound=coreas_attrs["AutomaticTimeBoundaries"] * units.s,
        core=core * units.cm,
    )

    # close the reader
    coreas_h5_reader.close()

    return inp_file, list_file, reas_file


def write_simulation_to_file(
    inp_file, list_file, reas_file, sim_directory="./", reset = False
):
    """
    Write the provided contents of the INP, LIST and REAS files for a single simulation to the files
    in a directory named after the simulation number.

    The directory will be created in the `sim_directory` path, and will be named `SIMXXXXXX`, where
    the last six digits are the simulation number. This is retrieved from the INP file contents, as
    the first line of the file. The function will fail if the directory already exists, unless
    `reset` is set to True, in which case the directory will be removed and re-created.

    Parameters
    ----------
    inp_file : list
        The contents of the INP file
    list_file : list
        The contents of the LIST file
    reas_file : list
        The contents of the REAS file
    sim_directory : str, default='./'
        The path to the directory where the simulation directory will be made, in which all files are written
    reset : bool, default=False
        whether to delete the simulation directory or not
    """
    sim_nr = int(inp_file[0].split(" ")[-1][:-1])

    sim_directory = os.path.join(sim_directory, f"SIM{sim_nr:06d}")

    if os.path.exists(sim_directory):
        if reset:
            logger.warning(f"Removing and re-making simulation directory {sim_directory}")
            shutil.rmtree(sim_directory)
            os.mkdir(sim_directory)
        else:
            raise FileExistsError(
                "Directory for simulation already exists! Aborting..."
            )
    else:
        os.mkdir(sim_directory)

    with open(f"{sim_directory}/SIM{sim_nr:06d}.inp", "w+") as file:
        file.writelines(inp_file)

    with open(f"{sim_directory}/SIM{sim_nr:06d}.list", "w+") as file:
        file.writelines(list_file)

    with open(f"{sim_directory}/SIM{sim_nr:06d}.reas", "w+") as file:
        file.writelines(reas_file)


# Function to sample input parameters


def sample_primary_energy(exp_range=(8, 10), size=1):
    r"""
    Sample a single primary energy from log-uniform distribution, between the exponents given
    by `exp_range`. For example, using the default settings, calling this function will generate
    a value between :math:`10^{8}` and :math:`10^{10}` GeV.

    Parameters
    ----------
    exp_range : tuple, default=(8, 10)
        The lower and upper exponent of the energy range in GeV to sample from
    size : int, default=1
        The number of energies to retrieve

    Returns
    -------
    primary_energy : list of float
        Primary energy (in internal units), as an array of length `size`
    """
    primary_energy_exp = np.random.uniform(*exp_range, size=size)  # random exponent in GeV

    return 10**primary_energy_exp * units.GeV


def sample_zenith_angle(range=(0, 90), size=1, uniformity="sin2"):
    r"""
    Sample the zenith angle from some distribution normalised with the solid angle.
    The names of the distributions refer to the variable in which they are uniform.

    Parameters
    ----------
    range : tuple, default=(0, 90)
        The lower and upper zenith angle in degrees (endpoints exclude
    size : int, default=1
        The number of angles to samples
    uniformity : {'sin2', 'sin', 'cos'}
        The distribution to use to sample the zenith angle

    Returns
    -------
    zenith_angle : list of float
        Sampled zenith angles (in internal units), as an array of length `size`

    Notes
    -----
    The names of the distributions refer to the variable in which they are uniform,
    in the sense that if you sampled using 'sin2' (the default), the zenith angle
    distribution will look uniform if binned in :math:`sin^2(\theta)`.
    """
    rng = np.random.default_rng()

    possible_theta = np.arange(*range, 0.001)[
        1:-2
    ]  # exclude 0 and 90 degrees to avoid problems with sin and division
    possible_theta *= units.deg

    if uniformity == "sin":
        # Probability distribution = sin(theta), normalised
        my_p = np.cos(possible_theta)
        my_p /= np.sum(my_p)
    elif uniformity == "sin2":
        my_p = np.sin(2 * possible_theta)
        my_p /= np.sum(my_p)
    elif uniformity == "cos-1":
        # return np.arccos(1 - rng.random(size=size))
        my_p = np.sin(possible_theta)
        my_p /= np.sum(my_p)

    return rng.choice(possible_theta, p=my_p, size=size) * units.deg


def sample_azimuth_angle(range=(0, 360), size=1):
    """
    Sample the azimuth angle within the given range, from a uniform distribution.

    Parameters
    ----------
    range : tuple, default=(0, 360)
        The lower and upper azimuth angle in degrees
    size : int, default=1
        The number of angles to samples

    Returns
    -------
    azimuth_angle : list of float
        Sampled azimuth angles (in internal units), as an array of length `size`
    """
    rng = np.random.default_rng()

    return rng.uniform(*range, size=size) * units.deg
