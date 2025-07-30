.. Template Synthesis for Radio Emission from Air Showers documentation master file, created by
   sphinx-quickstart on Tue Mar 25 11:02:53 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SMIET: Synthesis Modelling In-air Emission using Templates
==========================================================

Welcome to the documentation of the ``SMIET`` package.
This package implements the template synthesis algorithm, which is described in short :doc:`here <template-synthesis/ts_index>`.
For more information, please refer to the following publications:

- "SMIET: Fast and accurate synthesis of radio pulses from extensive air shower using simulated templates",
  submitted to Astroparticle Physics, preprint available on `arXiv <https://arxiv.org/abs/2505.10459>`_ .
- "Proof of principle for template synthesis approach for the radio emission from vertical extensive air showers" in `Astroparticle Physics`_ .
- Proceedings of `ARENA22 <https://pos.sissa.it/424/052/>`_
- Proceedings of `ICRC23 <https://pos.sissa.it/444/216/>`_
- Proceedings of `ARENA24 <https://pos.sissa.it/470/046/>`_

.. _Astroparticle Physics: https://doi.org/10.1016/j.astropartphys.2023.102923

There are two different implementations of the template synthesis algorithm available in this package.
The first, and standard, implementation is based on `NumPy <https://numpy.org/>`_ .
This one contains several classes that make it easier to follow the steps taken during the synthesis process,
which can be useful to debug or understand certain features.
A second implementation based on `JAX <https://docs.jax.dev/en/latest/>`_ is also available.
This high-performance library is optimized for array computing, which speeds up the synthesis process.
It also allows for automatic differentiation, which allows users to slot this package into
machine learning applications or use it in a information field theory context.
As this version of the template synthesis package is optimized for performance, its code is more opaque.
We therefore recommend new users to first get acquainted with the NumPy version, before using the JAX implementation.

In order to work with template synthesis, you will need so-called sliced showers as inputs.
These are showers simulated with `CoREAS <https://huege.org/coreas/>`_ which are configured to
split the radio emission in each antenna into atmospheric depth bins.
Included in this package are functions to easily generate the necessary input files for these simulations.
These are in the :doc:`corsika <corsika/corsika_index>` module.
It is also possible to generate standard CoREAS simulation input files with functions in that module.

.. toctree::
   :maxdepth: 2
   :caption: Sections in this documentation:

   logging
   conventions_units
   template-synthesis/ts_index
   numpy/numpy_index
   jax/jax_index
   corsika/corsika_index
   changelog
