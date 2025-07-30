Key Differences with NumPy version
===================================

Here we highlight the key differences between the JAX and NumPy versions of the template synthesis package, as there are some important differences in the implementation that one needs to consider when using either module.

1. The JAX version does not have a ``SliceSynthesis`` class. 


To fully utilize the potential of the JAX framework, we opt to store all slices in a single array. While this allows for better performance when mapping the template, this does mean that the ``TemplateSynthesis`` class is less flexible than the NumPy version. For example, it is not possible to access the amplitude and phase spectra of a single slice. Instead, one can access this through slice indexing. A more user-friendly method is in development. 

2. The JAX version can lead to memory overloads when using large arrays.

As JAX internally uses a just-in-time compilation (JIT) approach, it can lead to some memory issues when using large arrays. This is due to the fact that JAX will try to compile the function with the largest array size, which can lead to memory issues. To avoid this, we recommend to either use smaller arrays or use the available functionality ``apply_trace_cuts`` in the ``SlicedShower`` object to reduce the sample size which will further reduce the memory.


3. The JAX version does not include synthesis of the phase information.

While the NumPy version also synthesises the phase information through the arrival time, this is not yet implemented in the JAX version. As such the JAX version is limited to the amplitude synthesis only (and thus limited to a single geometry per sliced shower). This is a known limitation and will be implemented in a future version.


4. The JAX version relies on the following external modules:

   - ``jax``: The JAX library is used for automatic differentiation and GPU/TPU acceleration. This is the core of the JAX version which allows for the performance improvements. In particular, many functionalities are written in ``jax.numpy``, which is the numpy API for JAX.
   - ``jax_radio_tools`` : This is a library that provides tools for radio signal processing in JAX, similar to the already widely used ``radio_tools``.


5. All templates are stored via HDF5 files, while in the NumPy version they are stored as ``.npz`` files. 
   

   This is a more efficient way to store the templates, as HDF5 files are more efficient for large datasets, while the user-defined ``SlicedSynthesis`` objects are more easily stored via ``.npz`` files. The HDF5 files can be read using the ``h5py`` library, which is already included in the JAX version.

6. Syntactic differences

There are several naming conventions that differ between the JAX and NumPy versions. For example, the magnetic field vector is called ``magnet`` in the NumPy version whilst ``magnetic_field_vector`` in the JAX version. We plan to list all differences in the future, but for now, please refer to the package documentation for the most up-to-date information.