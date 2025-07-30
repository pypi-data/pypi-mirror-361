Generating the origin showers
=============================

In order to generate the origin showers, we need to run CoREAS with the correct settings. This can
easily be achieved using the tools provided in the :doc:`corsika <../corsika/corsika_index>` module.

Currently we recommend to run simulations with about 20 antennas on the
:math:`\vec{v} \times \vec{v} \times \vec{B}` axis. This is a good number to apply interpolation on,
later on. However, with 250 slices, this results in 5000 configured observers in CoREAS. From our
testing, this number is way too high to be run on a single node (runtimes exceeded the limit of 10
days with :math:`10^{-7}` thinning).

.. tip::
    If you really need to run one node, we suggest running 4-6 antennas. This should keep the
    runtimes within 48-72 hours, which can still be acceptable for most computing clusters. Lowering
    the thinning will also help of course.

To resolve this issue, you can either use MPI (recommended, if you computing environment supports it) or
split the simulations into multiple runs with smaller antenna sets. There should also be a mode in CORSIKA
to mimic MPI by using a set of scripts that do this splitting automatically, but we have no experience
with using that module. The file generation functions from the :doc:`corsika <../corsika/corsika_index>`
module configure the settings required for MPI automatically.