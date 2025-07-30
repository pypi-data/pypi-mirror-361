The template synthesis workflow
===============================

Here we describe the basics step needed to run a synthesis. The workflow is the same for both
the NumPy and JAX versions of the package, thanks to a consistent interface between the two.
Each package may offer additional features which are not described here, but rather in their
respective sections of the documentation.

Creating and storing a template
-------------------------------

The synthesis process is divided in two distinct steps, the template generation and the mapping.
After the generation step, which is by far the most computationally expensive, the template can
be stored to disk. It can then later be loaded to run the mapping process. The template is stored
as an `NPZ` archive in the Numpy version, and a HDF5 file in the JAX version.

To create the template, you should first read in the CoREAS HDF5 file using the ``SlicedShower``
class. This will take care of reading in all the traces for each slice in the simulation. This
object will be passed on to the template constructor.

We then create a ``TemplateSynthesis`` object. It exists in both version of the software, which is
why we recommend to always use this class in analysis scripts. This should make it easier to
switch between the two versions when desired. When creating the object we also pass the `freq_ar`
argument, which defines the frequency over which we will synthesise.

.. important::
    The corresponding spectral parameter file needs to present in the
    `smiet/spectral_parameters` directory. As of April 2025, the option for `freq_ar`
    are `[30, 80, 50]` and `[30, 500, 100]`.

To construct the template, we pass the ``SlicedShower`` object to the
``TemplateSynthesis.make_template`` method. This will create the template and store it in an
internal array. When creating the template we have the choice to use the quadratic component
in the parametrisation of the charge-excess traces (this is the :math:`c_{CE}` spectral parameter).
By default this is set to `False`, as the quadratic component does not appear to be necessary
for the charge-excess.

If you wish to store the template to disk, you can use the ``TemplateSynthesis.save_template``
method. It optionally takes a location where to store the template. If no location is provided,
the template will be stored in `smiet/templates` by default.

Synthesising an entire shower
-----------------------------

The ``TemplateSynthesis`` class makes it convenient to synthesise an entire shower. In order to do
this, we first need a representation of the target shower. For this one can use the ``Shower`` class.
This class can hold a longitudinal profile as well as the geometry, magnetic field and atmosphere.
We can set these attributes manually, or use the ``Shower.copy_settings`` method to copy them from
another ``Shower``.

.. note::
    The ``SlicedShower`` class is a child of the ``Shower`` class, so these settings can be copied
    from the ``SlicedShower`` object as well.

Once we have the target shower, we can pass it to the ``TemplateSynthesis.map_template`` method. From
this we retrieve an array of geomagnetic and charge-excess traces, one for each antenna which was
present in the origin.
