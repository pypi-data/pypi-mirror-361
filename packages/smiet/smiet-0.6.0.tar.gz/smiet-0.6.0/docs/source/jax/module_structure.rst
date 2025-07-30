Module structure
================

The main module of the JAX version of template synthesis (unlike the NumPy Version) only consists of the ``TemplateSynthesis`` class. 

.. note::

    All arrays are defined through ``jax.numpy``, which has almost identical API as the usual ``numpy``. There are some differences, which you can find in `JAX NumPy documentation <https://docs.jax.dev/en/latest/jax.numpy.html>`_.

    To import ``jax.numpy``, use the following command:

    .. code-block::

        import jax.numpy as jnp

    and now you can use ``jnp`` instead of ``np`` in your code.


Reading in showers
------------------

There are two main modules in which one can use to read in showers:

BaseShower
^^^^^^^^^^

The ``BaseShower`` class is the abstract base class for all shower readers. It provides the basic functionality to read in showers and access their properties. This class is not meant to be used directly, but rather as a base class for other shower readers. 

There are a few parameters that need to be set, which are incidentally used in the ``TemplateSynthesis`` class. These parameters are:

- ``xmax``: The maximum depth of the shower in g/cm^2.
- ``nmax``: The maximum number of particles in the shower.
- ``zenith``: The zenith angle of the shower in radians.
- ``azimuth``: The azimuth angle of the shower in radians.
- ``magnetic_field_vector``: The magnetic field vector of the observation site in the NuRadioReco unit convention.
- ``core``: The core position of the shower in the NuRadioReco unit convention.


Example:

.. code-block::

    import jax.numpy as jnp
    from smiet.jax.io import BaseShower as Shower

    # define atmospheric slices
    atm_slices = jnp.arange(0, 1110, 5)

    # define parameters to set
    parameters = {
    "xmax" : 800,
    "nmax" : 1e9,
    "zenith" : 0.0,
    "azimuth" : 0.0,
    "magnetic_field_vector" : jnp.array([0.0, 1.0, 1.0]),
    "core" : jnp.array([0.0, 0.0, 0.0]),
    }

    shower = Shower()
    shower.set_parameters(atm_slices, parameters)

    # to set the longitudinal profile, need to 
    # define it separately
    long_profile = some_longitudinal_profile_function(atm_slices)
    shower.set_longitudinal_profile(long_profile)

SlicedShower
^^^^^^^^^^^^

This inherited class is used to read in showers that are sliced into atmospheric slices. This, similar to the ``SlicedShower`` class in the NumPy version, allows the reader to generate origin showers which are used to generate the template. 

To initialise the ``SlicedShower`` class, a pre-simulated CoREAS simulation generated from :ref:`corsika_filegeneration` is required. To initialise the shower, the following command can be used:

.. code-block::

    from smiet.jax.io import SlicedShower

    sliced_shower = SlicedShower(
        file_path="path/to/simulation/file",
        gdas_file="path/to/gdas/file",
    )

Where the GDAS atmospheric file can optionally be passed as an additional argument for a more realistic atmospheric model.

Initialisation
~~~~~~~~~~~~~~

Initialising the ``SlicedShower`` object does the following:

1. Reads in the CoREAS simulation file and extracts the relevant information (e.g. the shower profile, the electric field, etc.). 
2. Reads in the GDAS file (if provided) or a standard US atmospheric model into the ``Atmosphere`` object in ``jax_radio_tools``. 
3. Convert all relevant properties into standard NuRadioReco units, which is the convention used in this code. Here, a transformer ``self.transformer`` is defined based on the geometry and magnetic field of the shower. 
4. Sort all antennas based on increasing radius and azimuth (in that order). This is done to consistently match antennas defined in the origin shower with those defined through other means (e.g. from standard CoREAS simulations).

The resulting electric field traces for all antennas, positions, and slices can be accessed via the ``self.trace_slices`` attribute.

Accessing shower properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following properties of the shower can be accessed, which can be useful in different scenarios:

.. code-block::

    # electric field traces in on-sky coordinates
    traces_onsky = sliced_shower.trace_slices

    # electric field traces in geomagnetic & CR emission
    traces_geoce = sliced_shower.get_traces_geoce()

    # time axis of the electric field traces
    trace_times = sliced_shower.trace_times

    # antenna positions in ground plane
    ant_positions_ground = sliced_shower.ant_positions_ground

    # antenna positions in shower plane
    ant_positions_shower = sliced_shower.get_antennas_showerplane()

    # distance of each antenna to the shower core
    ant_distances = sliced_shower.dis_to_core


In addition, all properties as defined in the ``BaseShower`` class can be accessed. This includes the zenith and azimuth angles, the core position, the magnetic field vector, the maximum depth of the shower, and the longitudinal profile itself.


Applying cuts to the sliced traces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As we now store everything in a single array, using the full array may not only be suboptimal but also unnecessary for most cases. Therefore, we provide a functionality to apply some cuts to the trace. These functions include:

- resampling: the trace will be resampled from the default sampling rate of 1 GHz to the desired sampling rate. This is done by using the JAXified version of the ``resample`` function from the ``scipy.signal`` module. 
- filtering: the trace is filtered to the desired frequency bandwidth (in MHz) using a simple box filter function after zeropadding the trace.
  
Example:

.. code-block::

    sliced_shower.apply_trace_cuts(
        f_min: float = 30 * units.MHz,
        f_max: float = 80 * units.MHz,
        delta_t: float = 2 * units.ns,
        t_window : float = 500 * units.ns, # not used
        sample_axis: int = 2,
        sample_time_axis: int = 1,
    )

where ``sample_axis`` and ``sample_time_axis`` are the axis in which the samples lie within the array of traces. The default values are set to 2 and 1, respectively, and need not be modified otherwise.


CoreasShower
^^^^^^^^^^^^

This is the main reader for CoREAS simulations, as it is the most common format used in the community. The ``CoreasShower`` class is a subclass of the ``BaseShower`` class and provides similar functionality as the ``SlicedShower`` class.

To initialise the ``CoreasShower`` class, a pre-simulated CoREAS simulation generated from :ref:`corsika_filegeneration` is required. To initialise the shower, the following command can be used:

.. code-block::

    from smiet.jax.io import CoreasShower

    coreas_shower = CoreasShower(
        file_path="path/to/simulation/file",
    )

Initialisation
~~~~~~~~~~~~~~

Initialising the ``CoreasShower`` object does the following:

1. Reads in the CoREAS simulation file and extracts the relevant information (e.g. the shower profile, the electric field, etc.). 
2. Convert all relevant properties into standard NuRadioReco units, which is the convention used in this code. Here, a transformer ``self.transformer`` is defined based on the geometry and magnetic field of the shower. 
3. Sort all antennas based on increasing radius and azimuth (in that order). This is done to consistently match antennas defined in the origin shower with those defined through other means (e.g. from standard CoREAS simulations).

The resulting electric field traces for all antennas and positions can be accessed via the ``self.efield_traces`` attribute.

Accessing shower properties
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most properties follow those from the ``SlicedShower`` class, except for the electric field traces themselves (which are now not sliced). They can be accessed as such:

.. code-block::

    # electric field traces in on-sky coordinates
    traces_onsky = coreas_shower.efield_traces


Applying cuts to the CoREAS traces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to the ``SlicedShower`` class, the ``CoreasShower`` class provides a functionality to apply some cuts to the trace. See above for details.


Making a Template
-----------------

We are finally ready to make a template. The ``TemplateSynthesis`` class is the main class to use for this. It takes a ``BaseShower`` object as input and generates a template based on the shower properties.

The template is generated by using the ``make_template`` method, which takes a ``SlicedShower`` object to generate a template. This template can be stored as a HDF5 file using the ``save_template`` method. The template can be loaded again using the ``load_template`` method.

Example to generate a template for a given shower within a frequency bandwidth of 30-80 MHz with a timing resolution of 2 ns:

.. code-block::

    from smiet.jax import TemplateSynthesis, SlicedShower

    # create a template object
    template = TemplateSynthesis(
        freq_ar=[30, 80, 50] * units.MHz,
    )

    # initialise the sliced shower
    sliced_shower = SlicedShower(
        file_path="path/to/simulation/file",
        gdas_file="path/to/gdas/file",
    )
    # apply cuts 
    sliced_shower.apply_trace_cuts(
        f_min=30 * units.MHz,
        f_max=80 * units.MHz,
        delta_t=2 * units.ns,
    )

    # make the template
    template.make_template(sliced_shower)

    # save the template
    template.save_template("some_template.hdf5")

    # load the template
    new_template = TemplateSynthesis(
        freq_ar=[30, 80, 50] * units.MHz,
    )
    new_template.load_template("some_template.hdf5")

Mapping the template
--------------------

The generated template can be used to synthesise the electric field traces for all given antenna positions,
given any shower defined (and inherited from) the ``BaseShower`` class.

.. note::

    When using ``CoreasShower`` showers, it is important to map the grammage steps (and therefore the
    longitudinal profile) to those from the origin shower, as the grammage steps may not be the same in the
    CoREAS simulation. This can be done by using the ``transform_profile_to_origin`` method of the
    ``CoreasShower`` class.

Example:

.. code-block::

    from smiet.jax import TemplateSynthesis, Shower, CoREASHDF5

    # create a template object
    template = TemplateSynthesis(
        freq_ar=[30 * units.MHz, 80 * units.MHz, 50 * units.MHz]
    )

    # load the pre-defined template from before
    template.load_template("some_template.hdf5", save_dir="/path/to/templates")

    # define an arbitrary shower as before
    shower = Shower()
    shower.set_parameters(template.grammages, parameters)
    # set the longitudinal profile
    long_profile = some_longitudinal_profile_function(template.grammages)
    shower.set_longitudinal_profile(long_profile)

    # OR: use a simulated shower
    shower = CoreasShower("path/to/simulation/file.hdf5")
    # apply cuts 
    shower.apply_trace_cuts(
        f_min=30 * units.MHz,
        f_max=80 * units.MHz,
        delta_t=2 * units.ns,
    )
    # transform the profile to the origin shower
    # pass in the grammage from the origin shower
    shower.transform_profile_to_origin(template.grammages)

    # map the template to the shower
    mapped_traces = template.map_template(shower)

The mapped traces will return the electric field traces for all antennas in the shower,
which can be used for further analysis.
