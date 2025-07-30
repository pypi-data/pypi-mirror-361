A User's Guide to Template Synthesis
====================================

Here we give a general overview of how the template synthesis method works. It is not meant as an in-depth
description of the algorithm, but rather as a guide to help you understand how to use the package. In
:doc:`ts_algorithm` we describe the algorithm on a high-level. For more details, please refer to the
publications mentioned on the homepage of the package.

In order to use template synthesis, you will probably want to generate your own origin showers,
although some examples are provided for download in the demo folder. Some guidance and general tips
on how to do this can be found in :doc:`ts_origin_showers`. Once you have an origin shower, you can
follow the steps in :doc:`ts_workflow` to synthesise a shower.

The synthesised traces are returned in the geomagnetic and charge-excess emission. If you want to treat these
traces in the vxB and vxvxB coordinate system, you can use the functionality described in :doc:`ts_treatment_of_vxB`.

.. toctree::
    ts_algorithm
    ts_origin_showers
    ts_workflow
    ts_treatment_of_vxB
