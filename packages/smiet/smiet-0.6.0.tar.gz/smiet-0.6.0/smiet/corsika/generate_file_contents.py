import os

import numpy as np
import radiotools.helper as hp

from radiotools.coordinatesystems import cstrafo

from smiet import units

import logging
logger = logging.getLogger("smiet.corsika.generate_file_contents")


# Functions to generate the individual files

def generate_inp_file(sim_nr, sim_zenith, sim_azimuth, sim_energy,
                      primary=14, direct='./',
                      magnet=(0.0, 0.186 * units.gauss, -0.456 * units.gauss), obs_lev=0.0 * units.m,
                      slicing=5 * units.g / units.cm2,
                      thin=1e-7, n_cores=10, atm=17):
    """
    Make an INP file for a CORSIKA run with CoREAS, using MPI.

    As CoREAS only supports a single shower per run, the `EVTNR` and `NSHOW` are set to 1.
    The shower zenith, azimuth and energy are fixed to the values provided.
    For the geometry, the NRR coordinate system is assumed (ie x-axis points east), which means
    that the provided azimuth is shifted by 90 degrees to convert to the CORSIKA system.
    The SEED values are randomly generated. For the USER variable, the login name is used (by
    evaluating `os.getlogin()`).

    Parameters
    ----------
    sim_nr : int
        The value for the RUNNR parameter
    sim_zenith : float
        The zenith of the shower (THETAP). Currently only using a fixed zenith is supported
    sim_azimuth : float
        The azimuth of the shower (PHIP + 270 deg). Currently only using a fixed azimuth is supported
    sim_energy : float
        The fixed energy to use for the simulation
    primary : int, default=14
        The CORSIKA identifier for the primary particle type. Default is 14 (proton).
    obs_lev : float, default=0.0 * units.m
        The observation level to use for the simulation (OBSLEV)
    magnet : tuple of float, default=(0.0, 18.6, -45.6) * units.gauss
        The components of the 3D magnetic field, provided in the NRR CS and internal units (MAGNET)
    direct : str, default='./'
        The directory for the particle output (DIRECT)
    atm : int or str, default=17
        If an integer, the CORSIKA identifier for the atmosphere (used for ATMOD).
        If a string, the name of the GDAS atmosphere file (used for ATMFILE)
    n_cores : int, default=10
        The number of cores over which the MPI simulation will run
    thin : float, default=1e-7
        The thinning level to use (THIN)
    slicing : float, default=5 * units.g / units.cm2
        The thickness of the atmospheric slices, to be used for the longitudinal profile (LONGI)

    Returns
    -------
    contents : list of str
        The contents to be written to the INP file
    """
    atm_line = f'ATMFILE {atm}\n' if type(atm) is str else f'ATMOD   {atm}\n'
    contents = [
        # Add run information
        f'RUNNR   {sim_nr}\n',
        f'EVTNR   1\n',
        f'NSHOW   1\n',
        f'{atm_line}',
        # Set SEED with random numbers (MPI option uses 6 seeds)
        f'SEED    {np.random.randint(1, 900000001)} 0 0\n',
        f'SEED    {np.random.randint(1, 900000001)} 0 0\n',
        f'SEED    {np.random.randint(1, 900000001)} 0 0\n',
        f'SEED    {np.random.randint(1, 900000001)} 0 0\n',
        f'SEED    {np.random.randint(1, 900000001)} 0 0\n',
        f'SEED    {np.random.randint(1, 900000001)} 0 0\n',
        # Set primary particle
        f'PRMPAR  {primary}\n',
        # Set fixed energy
        f'ERANGE  {sim_energy / units.GeV:.2f} {sim_energy / units.GeV:.2f}\n',
        f'ESLOPE  0.000E+00\n',
        f'ECUTS   3.000E-01 3.000E-01 4.010E-04 4.010E-04\n',
        # Add thinning, coupled to ERANGE
        f'THIN    {thin:.2e} {sim_energy / units.GeV * thin:.2e} 0.000E+00\n',
        f'THINH   1.000E+00 1.000E+02\n',
        # Control geometry
        f'THETAP  {sim_zenith / units.deg:.1f} {sim_zenith / units.deg:.1f}\n',
        f'PHIP    {-270. + sim_azimuth / units.deg:.1f} {-270. + sim_azimuth / units.deg:.1f}\n',
        f'MAGNET  {magnet[1] / units.microtesla:.2f} {-magnet[2] / units.microtesla:.2f}\n',
        f'OBSLEV  {obs_lev / units.cm:.2f}\n',
        # Electromagnetic interactions
        f'ELMFLG  T T\n',
        f'STEPFC  1.000E+00\n',
        f'RADNKG  5.000E+05\n',
        f'MUMULT  T\n',
        f'MUADDI  T\n',
        f'MAXPRT  1\n',
        f'ECTMAP  1.000E+5\n',
        # Particle output
        f'PAROUT  F F\n',
        f'DATBAS  F\n',
        f'LONGI   T {slicing / units.g * units.cm2:.1f} T T\n',
        # Coupling ERANGE with PARALLEL
        f'PARALLEL 1000 {sim_energy / units.GeV / n_cores / 100:.1e} 1 T\n',
        # User information
        f'USER    {os.getlogin()}\n',
        f'DIRECT  {direct}\n',
        # End the steering file
        f'EXIT\n'
    ]

    return contents


def generate_list_file(sim_zenith, sim_azimuth, slices_gram,
                       magnet_vector=None,
                       number_of_arms = 8,
                       core=None, radii=None):
    """
    Create a starshape pattern with 8 arms in the shower plane and project it to the ground along the shower axis.

    This result in the antennas from the same "circle" to have different
    viewing angles after being projected to the ground. The antennas are sliced according to
    the grammages specified, and in the LIST file the receivers are ordered by slice (which
    proves to be a couple of percent faster than ordering them by position).

    Parameters
    ----------
    sim_zenith : float
        The zenith angle of the shower, in the NRR coordinate system
    sim_azimuth : float
        The azimuth angle of the shower, in the NRR coordinate system
    slices_gram : list of float
        The grammages of the planes defining the slices, including both the first and last one.
    core : list of float, default=[0,0,0] * units.m
        The core of the simulated air shower
    magnet_vector : array of float, default=[0, 0.186, -0.456] * units.gauss
        The magnetic field vector used in the simulation, used to project the antennas from
        the shower plane to the ground
    radii : list of float, default=None
        The distances (in the showerplane) from the showeraxis on which to put the antennas
        If None, a default starshape is used.
    number_of_arms: int, default=8
        The number of arms to use for the star shape pattern

    Returns
    -------
    contents : list of str
        The lines to be written to the LIST file
    """
    if magnet_vector is None:
        magnet_vector = np.array([0., 0.186, -0.456]) * units.gauss
    if core is None:
        core = np.array([0., 0., 0.])
    if radii is None:
        radii = np.concatenate((
            [12.5 / 8, 12.5 / 4, 12.5 / 2],
            np.arange(12.5, 200, 12.5),
            np.arange(200, 300, 25),
            np.arange(300, 400, 50),
            np.arange(400, 501, 100)
        )) * units.m

    ant_positions = _calculate_antenna_positions(sim_zenith, sim_azimuth, radii, number_of_arms, magnet_vector, core)

    return generate_list_file_from_positions(ant_positions, slices_gram)


def _calculate_antenna_positions(sim_zenith, sim_azimuth, radii, number_of_arms, magnet_vector, core):
    if len(radii.shape) != 1:
        raise ValueError('Radii should be a 1D array')

    # Make coordinate transformer, taking into account transformation to radiotools CS
    transformer = cstrafo(
        sim_zenith / units.rad, sim_azimuth / units.rad,
        magnetic_field_vector=magnet_vector / units.gauss
    )

    logger.info(f"Number of antennas to simulate: {len(radii) * number_of_arms:d}")

    ant_position_vvB = np.zeros((len(radii) * number_of_arms, 3), dtype=float)
    radians_step = 2 * np.pi / number_of_arms
    for ind, r in enumerate(radii):
        for j in np.arange(number_of_arms):
            # v = 0
            vB = r * np.sin(j * radians_step)
            vvB = r * np.cos(j * radians_step)

            ant_position_vvB[int(ind * number_of_arms + j), :2] = [vB, vvB]

    ant_position = transformer.transform_from_vxB_vxvxB_2D(
        ant_position_vvB, core=core / units.m
    )

    ant_position /= units.cm  # put the positions in cm to write them to LIST file

    return ant_position

def generate_list_file_from_positions(ant_positions, slices_gram):
    """
    Generate a list file from a known antenna layout from existing simulations.

    The function simply adds one observer for every antenna position in `ant_positions`, for each
    slice in `slices_gram`. This can be used to generate list files from simulations that already
    exist for the sake of generating an origin shower with the same layout.

    Parameters
    ----------
    ant_positions : list of [list of float]
        list of antenna positions for each CoREAS observer.
    slices_gram : list of float
        The grammages of the planes defining the slices, including both the first and last one.

    Returns
    -------
    contents : list of str
        The lines to be written to the LIST file
    """
    contents = []

    slices_gram /= (units.g / units.cm2)  # put the grammages back into correct unit

    logger.info(f"Number of slices to simulate: {len(slices_gram)}")

    for slice_ind in range(len(slices_gram) - 1):
        
        for idx, ant in enumerate(ant_positions):
            ant_name = f'{int(ant[1] >= 0)}{int(abs(ant[1]) / 100)}_' \
                       f'{int(ant[0] <= 0)}{int(abs(ant[0]) / 100)}_{idx}'

            ant_line = 'AntennaPosition = '
            ant_line += f'{ant[1]:.1f} {-1 * ant[0]:.1f} {ant[2]:.1f} '  # here taking the values DIRECTLY, so NO TRANSFORM
            ant_line += ant_name + f'x{round(slices_gram[slice_ind + 1])} '
            ant_line += f'slantdepth {slices_gram[slice_ind]:.1f} {slices_gram[slice_ind + 1]:.1f} '
            ant_line += '\n'

            contents.append(ant_line)
        contents.append('\n')

    return contents


def generate_list_file_cherenkov(sim_zenith, sim_azimuth, slices_gram,
                                 atm, viewing_angle_fractions,
                                 number_of_arms = 8,
                                 magnet_vector=None, core=None):
    """
    Create a starshape pattern with 8 arms in the shower plane and project it to the ground,
    along the **viewing angle** under which antenna observes the slice. Note that this results

    Note that this results
    in different physical antennas on the ground for every slice! Therefore, this function
    should not be used to generate list files for origin showers. The antennas are sliced
    according to the grammages specified, and in the LIST file the receivers are ordered
    by slice (which proves to be a couple of percent faster than ordering them by position).

    Parameters
    ----------
    sim_zenith : float
        The zenith angle of the shower, in the NRR coordinate system
    sim_azimuth : float
        The azimuth angle of the shower, in the NRR coordinate system
    slices_gram : list of float
        The grammages of the planes defining the slices, including both the first and last one.
    atm : radiotools.atmosphere.models.Atmosphere
        The atmosphere model to use to map the antennas to the ground plane
    core : list of float, default=[0,0,0] * units.m
        The core of the simulated air shower
    magnet_vector : array of float, default=[0, 0.186, -0.456] * units.gauss
        The magnetic field vector used in the simulation, used to project the antennas from
        the shower plane to the ground
    viewing_angle_fractions : list of float
        The viewing angles (expressed as fractions of the local Cherenkov angle) under which to
        place the antennas.
    number_of_arms: int, default=8
        The number of arms to use for the star shape pattern

    Returns
    -------
    contents : list of str
        The lines to be written to the LIST file
    """
    if magnet_vector is None:
        magnet_vector = np.array([0., 0.186, -0.456]) * units.gauss
    if core is None:
        core = np.array([0., 0., 0.])
    if viewing_angle_fractions is None:
        raise ValueError('Viewing angle fractions should be provided')

    # Make radii per slice
    nr_of_slices = len(slices_gram) - 1

    # Create the contents
    contents = []

    # Make coordinate transformer, taking into account transformation to radiotools CS
    transformer = cstrafo(
        sim_zenith / units.rad, sim_azimuth / units.rad,
        magnetic_field_vector=magnet_vector / units.gauss
    )

    slices_gram /= (units.g / units.cm2)  # put the grammages back into correct unit

    for slice_ind in range(nr_of_slices):
        xslice = slices_gram[slice_ind + 1]

        height_slice = max(atm.get_vertical_height(sim_zenith / units.rad, xslice), 0.0)
        cherenkov_slice = np.arccos(1 / atm.get_n(height_slice))
        viewing_angles = cherenkov_slice * viewing_angle_fractions

        d_xmax = atm.get_distance_xmax_geometric(
            sim_zenith / units.rad, xslice, observation_level=0.0
        ) * units.m

        radii = d_xmax * np.tan(viewing_angles)

        ant_position_vvB = np.zeros((len(viewing_angle_fractions) * number_of_arms, 3), dtype=float)
        radians_step = 2 * np.pi / number_of_arms
        for ind, r in enumerate(radii):
            for j in np.arange(number_of_arms):
                # v = 0
                vB = r * np.cos(j * radians_step)
                vvB = r * np.sin(j * radians_step)

                ant_position_vvB[int(ind * number_of_arms + j), :2] = [vB, vvB]

        ant_position_ground = transformer.transform_from_vxB_vxvxB(
            ant_position_vvB, core=core / units.m
        )

        unit_shower_axis = hp.spherical_to_cartesian(sim_zenith / units.rad, sim_azimuth / units.rad)
        slice_vector = unit_shower_axis * d_xmax

        delta = ant_position_ground - slice_vector
        alpha = -ant_position_ground[:, 2] / delta[:, 2]

        ant_projected_ground = delta.T * alpha + ant_position_ground.T
        ant_projected_ground /= units.cm  # put the positions in cm to write them to LIST file

        for idx, ant in enumerate(ant_projected_ground.T):
            ant_name = f'{int(ant[1] >= 0)}{int(abs(ant[1]) / 100)}_' \
                       f'{int(ant[0] <= 0)}{int(abs(ant[0]) / 100)}_{idx}'

            ant_line = 'AntennaPosition = '
            ant_line += f'{ant[1]:.1f} {-1 * ant[0]:.1f} {ant[2]:.1f} '
            ant_line += ant_name + f'x{round(slices_gram[slice_ind + 1])} '
            ant_line += f'slantdepth {slices_gram[slice_ind]:.1f} {slices_gram[slice_ind + 1]:.1f} '
            ant_line += '\n'

            contents.append(ant_line)
        contents.append('\n')

    return contents


def generate_reas_file(event_number, n=1.000292,
                       time_res=2e-10 * units.s, time_bound=4e-7 * units.s,
                       core=None):
    """
    Generate the contents of the REAS file using the set of given input parameters.
    
    The contents are based on the CoREAS V1.4 software.

    Parameters
    ----------
    event_number : int
        The run number of the simulation
    n : float, default=1.000292
        The refractive index at sea level (GroundLevelRefractiveIndex)
    time_res : float, default=2e-10 * units.s
        The time resolution to use for the CoREAS simulation (TimeResolution)
    time_bound : float, default=4e-7 * units.s
        The time window to use for the CoREAS simulation (used with AutomaticTimeBoundaries)
    core : list of float, default=[0,0,0] * units.m
        The core of the simulated air shower, in the NRR coordinate system

    Returns
    -------
    contents : list of str
        The lines to be written to the REAS file
    """
    if core is None:
        core = [0., 0., 0.]

    corsika_core = [core[1], -1 * core[0], core[2]]

    contents = [
        '# CoREAS V1.4 by Tim Huege <tim.huege@kit.edu> with contributions by Marianne Ludwig and Clancy James - parameter file\n'
        '\n',
        '# parameters setting up the spatial observer configuration:',
        '\n',
        f'CoreCoordinateNorth = {corsika_core[0] / units.cm:.1f}     ; in cm\n',
        f'CoreCoordinateWest = {corsika_core[1] / units.cm:.1f}     ; in cm\n',
        f'CoreCoordinateVertical = {corsika_core[2] / units.cm:.1f}     ; in cm\n',
        '\n',
        '# parameters setting up the temporal observer configuration:\n',
        '\n',
        f'TimeResolution = {time_res / units.s:.2e}  				; in s\n',
        f'AutomaticTimeBoundaries = {time_bound / units.s:.2e}			; 0: off, x: automatic boundaries with width x in s\n',
        'TimeLowerBoundary = -1				; in s, only if AutomaticTimeBoundaries set to 0\n',
        'TimeUpperBoundary = 1				; in s, only if AutomaticTimeBoundaries set to 0\n',
        'ResolutionReductionScale = 0			; 0: off, x: decrease time resolution linearly every x cm in radius\n',
        '\n',
        "# parameters setting up the simulation functionality:\n",
        '\n',
        "GroundLevelRefractiveIndex = %.8f        ; specify refractive index at 0 m asl\n" % n,
        '\n',
        "# event information for Offline simulations:\n",
        '\n',
        "EventNumber = -1\n",
        "RunNumber = -1\n",
        "GPSSecs = 0\n",
        "GPSNanoSecs = 0\n",
        "CoreEastingOffline = 0.0                ; in meters\n",
        "CoreNorthingOffline = 0.0                ; in meters\n",
        "CoreVerticalOffline = 0.0                ; in meters\n",
        "OfflineCoordinateSystem = Reference\n",
        "RotationAngleForMagfieldDeclination = 0.0        ; in degrees\n",
        "Comment =\n",
        '\n',
        '# event information for your convenience and backwards compatibility with other software, these values are not used as input parameters for the simulation:'
        '\n'
        "CorsikaFilePath = ./\n",
        f"CorsikaParameterFile = SIM{event_number:06d}.inp\n",
    ]

    return contents
