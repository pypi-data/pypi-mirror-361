Some notes on the CORSIKA file generation
=========================================

The ``generate_simulation`` function takes in 3 mandatory arguments: the number of the simulation,
the type of the primary particle as a string and the number of cores to use for MPI. The first two
are simply added to the INP file in the usual way. The third one is factored in to the `PARALLEL`
keyword, which is set equal to the primary energy in GeV divided by the number of cores, divided
by a 100.

.. tip::
    In case you do not want to wish to use MPI, you can set the number of cores to 1 and modify
    the contents of the INP file by removing the `PARALLEL` entry (which should be at index `[-4]`)
    from the list.

The zenith, azimuth and primary energy are all optional arguments to the function. If they are not
provided, the function will randomly sample these values from some distributions. For this, three
other functions are defined in the same module: ``sample_zenith_angle``, ``sample_azimuth_angle``
and ``sample_primary_energy``. These are equipped with same ranges wherein to sample. For the
zenith angle, the range is between 0 and 90 degrees. For the azimuth angle, the range is between
0 and 360 degrees. For the primary energy, the range is between :math:`10^{8}` and :math:`10^{10}`
GeV. If you wish to also randomly select values for these parameters but within other ranges, you
can these directly when calling ``generate_simulation``.

.. tip::
    To generate simulation input files with random zenith, azimuth and primary energy, you can
    use the ``sample_zenith_angle``, ``sample_azimuth_angle`` and ``sample_primary_energy``
    functions with the ranges you want. These values can then be passed to the
    ``generate_simulation`` function as arguments.

.. warning::
    If you pass in fixed values to the ``generate_simulation`` function, be sure to pass in the
    internal unit system. For example, if you want to set the zenith angle to 45 degrees, you
    should use `sim_zenith = 45 * units.deg`.

Other variables controlling the simulation are the magnetic field, the atmospheric model to use
and the thinning setting. The last two are an integer and a float respectively, as usual for a
CORSIKA input file. For the magnetic field you can either pass the vector itself (in internal
units of course) or a string. The string should be the name of an experimental site whose magnetic
field vector is part of the `radiotools <https://c-glaser.de/physics/radiotools/>`_ package. Note
that after retrieving the magnetic field vector from `radiotools`, the x-component (corresponding
to the East-West direction) is set to zero, to ensure the antennas are always placed on the shower
plane axes.

.. todo::
    Technically we should rotate the magnetic field around the z-axis using the vectors declination,
    but for most places on Earth this will not have considerable difference compared to simply
    ignoring the x-component.

Lastly, there are the variables controlling the antenna configuration. First of all, we have the
thickness of the atmospheric slices. Then there is also the core position to use, which also defines
the observation level of the simulation. Lastly the `radii` parameter is a list of floats, which
are interpreted depending on the value of the `cherenkov` parameter.

If the `cherenkov` parameter is set to `False`, which is the default, the `radii` are taken to be
the distances in the shower plane from the antennas to the core, on one arm. If not provided, this
defaults to a list of 26 distances which run from 1.5m to 500m. In this case, every slice will have
the same physical antennas on the ground.

.. note::
    The ``generate_simulation`` function generates antennas only on the :math:`\vec{v} \times \vec{v} \times \vec{B}`
    axis. If you want more arms of the star shape, you can easily achieve this by using the
    ``generate_list_file`` (or ``generate_list_file_cherenkov``) function directly. That one has
    a `number_of_arms` parameter, which controls the number of arms to generate. The function
    start with the first arm on the :math:`\vec{v} \times \vec{v} \times \vec{B}` axis and
    proceeds counterclockwise around the shower plane.

This is different from when `cherenkov` is set to `True`. In this case, the `radii` are interpreted
as viewing angles for every slice, where the viewing angle is a fraction of the slice Cherenkov
angle. Typically, the `radii` in this case are numbers between 0.01 and 5. As the Cherenkov angle is
different in every slice, this option will result in a different set of antenna locations for each
slice. This option is useful for testing and validating the template synthesis algorithm, as you can
readily simulate the necessary antennas to recalculate the spectral parameters.

.. caution::
    There is no proper default value for `radii` when using the `cherenkov` option, so make
    sure to pass a value to the parameter.