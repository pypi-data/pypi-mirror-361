Module structure
================

The module contains two classes related to the template synthesis algorithm:
``TemplateSynthesis`` and ``SliceSynthesis``. The latter is not meant to be used directly, but is used
internally by the former. The ``TemplateSynthesis`` class is the main class of the module and it the
one which should be used to perform the synthesis.

It also has several classes which make it easy to load in CoREAS simulations stored as `HDF5` files.
These are the ``SlicedShower`` and the ``SlicedShowerCherenkov`` classes. They are both subclasses of
the ``CoreasShower`` class, which itself is a subclass of the ``Shower``  and the ``CoreasHDF5`` classes.
These each implement one of the two core aspects of air shower simulations.

For all the coordinate system transformations and other operations, we rely on the
`radiotools <https://c-glaser.de/physics/radiotools/>`_ package.

.. versionchanged:: 0.5 Antenna positions are stored in internal coordinate system

    Since v0.5 all positions in the Shower (sub)classes are stored in our internal coordinate system.

.. versionadded:: 0.6 Added CoreasShower class

    The ``CoreasShower`` class was added to more easily integrate CoREAS simulations into analyses
    with the SMIET software.

Reading in CoREAS simulations
-----------------------------

Shower
^^^^^^

The ``Shower`` class is supposed to be the most minimal representation of an air shower.
When mapping a template to a target, the latter should be a ``Shower`` object. All other
shower-related classes (listed hereafter) are subclasses of this class and can thus also
be used as targets for mapping.

An air shower is represented by its core position, the shower geometry, longitudinal profile
and the atmosphere, which is stored as an ``radiotools.atmosphere.models.Atmosphere`` object.
It can also store a magnetic field, with which it can create a ``radiotools.coordinates.cstrafo``
object to transform from one coordinate system to another. When setting the longitudinal profile,
a Gaisser-Hillas profile is automatically fitted to find the shower maximum and other parameters
of the shower profile.

One intersting feature of the ``Shower`` class is the ``Shower.copy_settings()`` function. With
this function, you can easily copy over the geometry, core position, atmosphere and magnetic field
from another shower in which you can then store other longitudinal profiles for synthesis.

.. code-block::

    from smiet.numpy import Shower, SlicedShower

    origin = SlicedShower(
        "/path/to/simulation/file"
    )

    target = Shower()
    target.copy_settings(origin)
    target.long = np.stack(
        origin.long[:, 0],  # take the grammage values from the origin to be consistent
        np.random.rand(1000)  # this is the sum of e- and e+ (the longitudinal profile)
    ) # Here you can set any longitudinal profile you want, but is has to have shape (slices, 2)

CoreasShower
^^^^^^^^^^^^

The ``CoreasShower`` class is a base class for all CoREAS simulations stored in `HDF5` files. It
is a subclass of ``CoreasHDF5`` which is a class meant to facilitate the interaction with the
CoREAS `HDF5` files. It uses this functionality to populate the attributes it inherits from the
``Shower`` class, to create an object which makes it easier to work with the antenna traces of
the CoREAS simulation. Specifically, it has the ability to return a ``radiotools.coordinates.cstrafo``
object based on the shower geometry, which makes it easy to transform the antenna positions to
for example the shower plane.

.. code-block::

    from smiet.numpy import CoreasShower

    origin = CoreasShower(
        "/path/to/simulation/file"
    )

    # Get the coordinate transformation object
    transformer = origin.get_transformer()

    # Transform the antenna positions to the shower plane
    ant_positions_showerplane = transformer.transform(origin.antenna_array['position'])

This class, as well as those that inherit from it, also create an ``radiotools.atmosphere.models.Atmosphere``
object that represents the atmosphere used in the simulation, if possible. To do this, it reads
in the atmospheric model number from the simulation settings. If this number is present in the
``radiotools.atmosphere.models.atm_models`` dictionary (i.e. one of the predefined models), then
the ``Atmosphere`` object is created and stored as the ``atmosphere`` attribute.

.. tip::
    Another way to create a custom atmosphere object, is to manipulate the ``radiotools.atmosphere.models.atm_models``
    dictionary. For example, if you used a simulation with custom ATMA, ATMB and ATMC values, you can
    add these values to the dictionary with the model number you used in the simulation (this is most
    likely 10). If you do this before creating the ``CoreasShower`` object, the ``Atmosphere`` object
    will be created with the custom values.

Another option is to pass the a GDAS file to constructor, via the ``gdas_file`` keyword. This
will always take precedence over the atmospheric model number in the simulation settings. From
the file, the atmospheric model parameters are read as well as the refractive index profile
(this is handled by the ``radiotools`` package).

.. danger::
    When the model number is not defined in ``radiotools`` and no GDAS file is provided, the
    ``atmosphere`` attribute will be set to ``None``. This will lead to issues when using
    this shower as an origin for template synthesis, as the ``TemplateSynthesis`` class
    expects the ``atmosphere`` attribute to be set.

.. code-block::

    from smiet.numpy import CoreasShower

    # Create a CoreasShower object with a GDAS file
    origin = CoreasShower(
        "/path/to/simulation/file",
        gdas_file="/path/to/gdas/file"
    )

    # Access the atmosphere object
    atmosphere = origin.atmosphere

    # Print the atmospheric model number
    print(atmosphere.model_number)

SlicedShower
^^^^^^^^^^^^

A sliced CoREAS simulation is one which is set up such that each antenna has its radio signal split
into the contributions coming from different atmospheric slices. The width of these slices should be
a constant (in atmospheric depth) and the number of slices should be the same for each antenna. In
CoREAS v1.4 this behaviour is achieved by adding multiple copies of the same physical antenna on the
ground, but configure each to only accept emission from a certain atmospheric depth range. This is done
using the `slantdepth` keyword. For more information, please refer to the
`CoREAS documentation <https://web.iap.kit.edu/huege/downloads/coreas-manual.pdf>`_.

The ``SlicedShower`` class is meant to be used with simulations where each slice is configured with
the same antennas on the ground. This is the standard for template synthesis. When reading in the
CoREAS `HDF5` file, the magnetic field, core, geometry and longitudinal profile are retrieved and stored
as attributes. The antenna names are retrieved and stored in the ``ant_names`` attribute. Here it is
important to note that the antenna names are assumed to be in the format ``{name}x{atmospheric_depth}``.
To find all the unique antenna names, the antenna names are split on the ``x`` character and the first
element is stored in a set, which is eventually stored as the ``ant_names`` attribute.

.. important::
    The antenna names are assumed to be in the format ``{antenna_name}x{atmospheric_depth}``. This is
    naming scheme is used by the :doc:`CORSIKA tools<../corsika/corsika_index>` in this package.

.. code-block::

    from smiet.numpy import SlicedShower

    origin = SlicedShower(
        "/path/to/simulation/file"
    )

    print(origin.antenna_names)

Apart from the name, the antenna position is also retrieved and stored in the ``ant_dict`` attribute.
This is done by looping over all unique antenna names and reading the position of the antenna configured
for atmospheric depth 5 g/cm2 (i.e. ``x5`` is appended to the antenna name to find the entry in the `HDF5`
file).

.. todo::
    Remove the hardcoded slice value of 5 for the antenna positions.

The number of slices present in a ``SlicedShower`` is then calculated as the number of observers in
the `HDF5` file divided by the number of unique antenna names. This is stored in the ``nr_slices``
attribute.

.. code-block::

    from smiet.numpy import SlicedShower

    shower = SlicedShower(
         "/path/to/simulation/file"
    )

    # Access trace from single slice
    my_ant = list(shower.antenna_names)[0]
    my_slice = 500  # g/cm2
    trace_slice = shower.get_trace_slice("antenna_name", 500)

    # Get complete trace for an antenna
    trace_all_slices = shower.get_trace(my_ant)

SlicedCherenkovShower
^^^^^^^^^^^^^^^^^^^^^

It is also possible to set up simulations where each slice has antennas placed at the same
viewing angle in units of local Cherenkov angle. As the Cherenkov angle is dependent on the atmospheric
depth, this implies a different set of antennas for each slice. It can be useful to opt for this
approach when checking the validity of the template synthesis algorithm or to recalculate the spectral
parameters. For these simulations the ``SlicedShowerCherenkov`` class can be used. It essentially lifts
some of the assumptions made in ``SlicedShower`` about the naming of the antennas. This does result in
slightly more memory consumption and a longer loading time.

An atmospheric slice
--------------------

In the NumPy version of the template synthesis package, a single slice of the atmosphere is represented
by a class called ``SliceSynthesis``. Its responsibility is to keep track of all the slice specific
variables, such as the atmospheric depth of the slice, the viewing angles of antennas with respect to
this slice and the amplitude/phase spectra of the radio signal in this slice.

.. warning::
    While it can be very useful to interact with the ``SliceSynthesis`` class directly for debugging,
    we advise against relying on it for scripting purposes. It does not exist in the JAX implementation,
    which makes scripts who rely on this class not easily portable. Instead, we recommend using the
    convenience functions provided by the ``TemplateSynthesis`` class to retrieve slice specific
    variables.

The ``SliceSynthesis`` class stores all its variables in a structured NumPy array, which can be accessed
through its ``antenna_parameters`` property. Two of the fields in this array are `distance` and `viewing_angle`.
These hold the distance from the slice to each antenna and the viewing angle of each antenna, respectively.
Note that these values are updated during the template generation **and** the mapping process, so be sure
to check which steps have been run before interpreting these values.

The other fields of the array contain the amplitude and phase spectra for the geomagnetic and charge-
excess components of the radio signal. These are normalised with respect to the shower geometry. For
the amplitude this means scaling with distance as well as some other factors. There is also the
normalisation using the spectral parameters, interpolated to the viewing angle of the antenna.

.. math::

    A_{\text{geo}} &= \left( \frac{a_{\text{geo}} \cdot N_{\text{slice}} \cdot \sin(\alpha_{\text{GEO}})}{d_{\text{slice}} \cdot \rho_{\text{slice}}} \right) \cdot \exp\left[b_{\text{geo}}(f - f_0) + c_{\text{geo}}(f - f_0)^2\right] \\
    A_{\text{ce}} &=  \left( \frac{a_{\text{ce}} \cdot N_{\text{slice}} \cdot \sin(\theta_C)}{d_{\text{slice}}} \right) \cdot \exp\left[b_{\text{ce}}(f - f_0)\right] \\

The phases are adapted by adding a linear phase gradient corresponding to the arrival time of the
signal as calculated using the shower geometry. The arrival time is calculated using the distance :math:`D`
from the slice to the ground along the shower axis and the distance :math:`L` from the slice to antenna,
corrected by the effective refractive index :math:`n_{eff}`.

.. math::

    t_{obs} &= \frac{ L \times n_{eff} - D }{ c } \\
    \phi &= \phi + 2 \pi f t_{obs}

Here :math:`c` is the speed of light in vacuum. During the template generation this correction
essentially moves the peak of the pulse to the very first time bin. Then, when mapping to a target,
the peak is moved back to expected time bin based on its geometry.

Synthesising an entire shower
-----------------------------

The ``TemplateSynthesis`` class stores all the slices of the origin shower, each represented by a
``SliceSynthesis`` object, in a list. Furthermore, it acts a central location for all the information
that is shared between the slices, such as the atmospheric model, the shower geometry, the antenna
positions, the valid frequencies and the spectral parameters which are currently loaded.
When creating a template (or loading one from disk) all these attributes are linked to the slices
in the list.

.. attention::
    As Python does not really have the concept of pointers, the attributes of the ``TemplateSynthesis``
    object do **not** serve as the source of truth for the shared variables. This is to say, if you
    update for example the atmosphere of the ``TemplateSynthesis`` object, the slices will not
    automatically receive this update. They will still hold references to the original atmosphere.

Creating a template
^^^^^^^^^^^^^^^^^^^

An origin ``SlicedShower`` can be processed into a template using the ``TemplateSynthesis.make_template()``
method. This can take up to a few minutes, depending on the number of slices and the number of antennas in
the shower. This is why we recommend to save the template to disk after it has been created, so that it can
be reused later without having to recompute it. This can be achieved using the
``TemplateSynthesis.save_template()`` method. Later on, a ``TemplateSynthesis`` object can load the template
using the ``TemplateSynthesis.load_template()`` method.

.. important::
    When saving a template, only some components of the atmosphere are saved. As a result, a GDAS
    atmosphere can currently not be stored. When loading a template which was generated with a
    GDAS atmosphere, you need to provide the GDAS file again. This is done by passing the ``gdas_file``
    keyword to the ``TemplateSynthesis.load_template()`` method.

.. code-block::

    from smiet.numpy import TemplateSynthesis, SlicedShower

    origin = SlicedShower(
        "/path/to/simulation/file",
        gdas_file="/path/to/gdas/file"  # Optional, if you want to use a GDAS atmosphere
    )

    synthesis = TemplateSynthesis(freq_ar=[30, 500, 100])
    synthesis.make_template(origin)

    # Save the template to disk
    synthesis.save_template(save_dir="/path/to/save/directory")

Mapping a template to a target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once a template has been created, it can be mapped to a target shower using the ``TemplateSynthesis.map_template()``
method. This method will take the template and map it onto a target ``Shower`` object. The target shower should
therefore at least have the core position, shower geometry, atmosphere and magnetic field set, as well as a
longitudinal profile.

.. code-block::

    from smiet.numpy import TemplateSynthesis, Shower, geo_ce_to_e
    # Load the template from disk
    synthesis = TemplateSynthesis.load_template(
        "/path/to/template/file.npz"
        gdas_file="/path/to/gdas/file"  # If the template was created with a GDAS atmosphere, you need to load it again here
    )

    # Create a target shower
    target = Shower()
    target.copy_settings(origin)  # Copy geometry etc. from the origin shower

    # Set a custom longitudinal profile
    target.long = np.stack(
        origin.long[:, 0],  # take the grammage values from the origin to be consistent
        np.random.rand(1000)  # this is the sum of e- and e+ (the longitudinal profile)
    )

    # Map the template to the target shower
    geo, ce = synthesis.map_template(target)

    # Transform geo and ce back to 3D electric field
    e_field = geo_ce_to_e(geo, ce, *synthesis.antenna_information["position_showerplane"].T)