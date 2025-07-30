.. _corsika_filegeneration:

Tools for CORSIKA/CoREAS
========================

In order to work with template synthesis, you will need to simulate origin showers with
CORSIKA. These are simulation which are set up in CoREAS to split the radio emission in
each antenna into multiple atmospheric depth bins. To easily produce the input files
required for these simulations, we provide some convenience functions in this module.

In the `write_simulation` submodule, the two main functions live: ``generate_simulation``
and ``write_simulation_to_file``. The first one generates the contents of the INP, LIST
and REAS file, using the chosen settings. If you so wish (for example because of the job
submission process on your compute cluster), you can modify the content before writing
it to files. When you are done, you can pass the three arguments to the second function,
which will write them to the files. The names of the files are taken from the simulation
number which is in the INP file.

.. toctree::
   :maxdepth: 3

   file_generation
   package_documentation
