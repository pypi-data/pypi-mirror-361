Conventions in this package
===========================

We chose our conventions to align as much as possible with `NuRadio`_.

Coordinate system
-----------------

We use a right-handed coordinate system, with the z-axis pointing upwards. The x-axis points to
magnetic East and the y-axis to magnetic North. This is essentially the CORSIKA coordinate system
rotated by 90 degrees.

Furthermore, we also use arrival direction instead of travel direction. Hence, :math:`\phi = 0^{\circ}`
in our system means that the shower is _coming_ from the East, not travelling towards it. In the
same vein, :math:`\phi = -90^{\circ}` means that the shower is coming from the South (which in
CORSIKA would be azimuth equal to 0) and setting :math:`\phi = 90^{\circ}` implies that the shower
comes from North.

Units
-----

To keep track of the units in this package, we use the same unit system as `NuRadio`_.
Just like in that package we provide a `units` module that can be used to give each variable
physical units. Each input is multiplied by its corresponding unit. To retrieve a value in
a specific unit, you divide the output by the unit. For example, to retrieve a distance
in centimeters, you can divide the variable by `units.cm`. Of course the output will only
make sense if the the variable is divided by a unit of the same dimension.
The module is documented :doc:`here <apidoc/smiet.units>`.

.. caution::
    As of April 2025, there are two notable exceptions to the use of the unit system, both related
    to atmospheric grammages. The first is the longitudinal profiles of the ``Shower`` objects.
    The first column contains the grammages values, but these are not in the internal unit system.
    Rather they are in g/cm2 directly. The same goes for the grammage values of the ``SliceSynthesis``
    objects in the Numpy version of the package. The reason for this is that the g/cm2 unit is an
    awkward value, which makes it difficult to work with. Rather than adapting the internal unit
    system, which would make it incompatible with `NuRadio`_, we simply do not convert some values
    for now.

.. _NuRadio: https://nu-radio.github.io/NuRadioMC/main.html
