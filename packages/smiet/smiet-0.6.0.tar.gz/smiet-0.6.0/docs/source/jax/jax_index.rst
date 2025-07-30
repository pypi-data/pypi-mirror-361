JAX module
==========

The JAX module of template synthesis is perpetually similar to that of the NumPy version, however it gains additional functionalities as it is written with the JAX language framework:

- It is able to run on GPUs and TPUs, which can significantly speed up the synthesis process.
- It can automatically differentiate through the synthesis process, which can be useful for optimization tasks such as massive parameter reconstructions or machine learning applications.
- It can be used with JAX's just-in-time compilation (JIT) to further speed up the synthesis process.
- It can be used with JAX's automatic vectorization (vmap, pmap) to efficiently process batches of data.

The JAX version of the template synthesis package is considered the experimental version. It is not as well tested as the NumPy version and may have some bugs or limitations. However, it is actively being developed and improved. 

**For most general purposes, the NumPy version is sufficient, and use the JAX version only if massive performance gain is necessary.**

To use this version, please install using the following command:

.. code-block::

    pip install -U template-synthesis[jax]


which will install the following (additional) packages necessary for the JAX version:

- ``jax``
- ``jaxlib``
- ``jax_radio_tools``

More information about the module structure can be found in the :doc:`module_structure` documentation.

.. toctree::
    :maxdepth: 2

    module_structure
    difference_with_numpy
    package_documentation