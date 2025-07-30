Treating synthesised traces for antennas along the vxB axis
============================================================

When creating a template from an origin shower, the electric fields are decoupled in the
geomagnetic and charge-excess components. This decoupling is performed in the shower plane,
where the polarisation patterns of both components are simple to describe as a function of
the antenna position. There is however an issue that arises for antennas that are placed along
the vxB axis. Since the decoupling of the electric field traces in the geomagnetic and
charge-excess components is performed as

.. math::

    E_\mathrm{GEO} = E_{vxvxB} \cdot \frac{x}{y} - E_{vxB} \; ,

    E_\mathrm{CE} = -1 E_{vxvxB} \frac{r}{y} \; ,

where :math:`E_\mathrm{GEO}` is the geomagnetic emission, :math:`E_\mathrm{CE}` is the charge-excess emission,
:math: `x, y` are the antenna positions in the shower plane, and :math:`r^2 = x^2 + y^2`.
On the vxB axis, the :math:`y` coordinate is zero, which leads to a division by zero and
therefore undefined values for the traces.

.. todo::
    Implement a more sophisticated decoupling of the electric field traces,
    which also works for antennas along the vxB axis.

Due to this relatively simple decomposition, there is no reasonable signal that can be expected on the
vxB axis in our synthesised signals. In order to still be able to use the vxB in analyses with SMIET,
we have provided a separate functionality to still generate signals on the vxB axis. Note that this
only works when the antenna positions are laid out in a starshape pattern.

When working with a starshape antenna layout, we can use the synthesised traces on the vxvxB axis
to generate traces on the vxB axis. Since we expect the geomagnetic and charge-excess emission to
be rotationally symmetric in strength, we can for example copy them over. This strategy is implemented
in the function :func:`smiet.numpy.utilities.transform_traces_on_vxB`, with the keyword argument
``vxB_axis_mode = "replace"``.

.. code-block:: python

    from smiet.numpy.utilities import transform_traces_on_vxB

    synthesis = TemplateSynthesis()
    # .....
    # perform synthesis 
    # .....
    synthesised_geo, synthesis_ce = synthesis.map_template(...)

    x, y = synthesis.antenna_information["position_showerplane"].T

    # transforming to vxB and vxvxB axis, treating the vxB axis accordingly
    synthesised_geo_vxB_treated, synthesised_ce_vxB_treated = transform_traces_on_vxB(
        synthesised_geo,
        synthesis_ce,
        x,
        y,
        vxB_axis_mode = "replace" # either "replace" or "zero" (default: "replace")
    )

This functionality also exists in the JAX version, :func:`smiet.jax.utilities.transform_traces_on_vxB`.

.. code-block:: python

    from smiet.jax.utilities import transform_traces_on_vxB

    # .....
    # perform synthesis 
    # .....
    synthesised_traces = ...

    x, y = synthesis.ant_positions_vvB[:,0], synthesis.ant_positions_vvB[:,1]

    # transforming to vxB and vxvxB axis,
    # treating the vxB axis accordingly
    synthesised_traces_vxB_treated = transform_traces_on_vxB(
        synthesised_traces,
        x,
        y,
        vxB_axis_mode = "replace" # either "replace", "zero" or "average" (default: "replace")
    )

The treatment of the vxB axis follows as such:
- If ``vxB_axis_mode = "replace"``, the traces on the vxB axis is replaced with the synthesised
  traces on the vxvxB axis. This is the default behaviour.
- If ``vxB_axis_mode = "zero"``, the traces on the vxB axis is set to zero.
- If ``vxB_axis_mode = "average"``, the traces on the vxB axis are set to an average of the
  synthesised traces on all other axes. As of July 2025 this option is only available in the
  JAX version of the function.

More functionalities to treat the synthesised traces in the vxB axis will be added in the future.
Please refer to the documentation of the function for more details.