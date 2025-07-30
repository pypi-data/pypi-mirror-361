"""Utility module to take care of transformations to shower plane etc."""

import jax

jax.config.update("jax_enable_x64", True)

import jax.numpy as jnp


def transform_traces_on_vxB(
        traces_geoce : jax.typing.ArrayLike,
        x : jax.typing.ArrayLike,
        y : jax.typing.ArrayLike,
        vxB_axis_mode : str = "replace"
) -> jax.Array:
    """
    Adjust the (synthesised) traces on the vxB axis.

    This function is meant to alter the traces on the vxB axis, as in the current
    version of the SMIET software the vxB axis cannot be synthesised. There are several
    strategies to handle this, and applying them should be facilitated by this function.

    Here it is assumed that the antennas are ordered with increasing phi, where phi=0 is oriented West.

    Parameters
    ----------
    traces_geoce : jax.typing.ArrayLike
        the synthesised traces in geomagnetic and charge-excess polarisation.
        Shape must be of NPOL x NANTS x NSAMPLES
    x : jax.typing.ArrayLike
        the antenna positions along the vxB axis, shaped as (NANTS,)
    y : jax.typing.ArrayLike
        the antenna positions along the vxvxB axis, shaped as (NANTS,)
    vxB_axis_mode : {"replace", "zero", "average"}
        Operation to perform on the vxB axis. If "replace" (the default), the traces from the
        vxvxB component will be copied over to the vxB component. If "zero", the vxB component
        will be set to zero.
    
    Returns
    -------
    traces_vB_vvB : jax.Array
        the synthesised traces in vB x vvB axis (shower plane)
    """
    # here the threshold cut is rather high, I am not sure why such a high cut is necessary
    # but it is somehow necessary for the antenna set I am using
    ant_at_vvB_axis = jnp.abs(x) < 5
    ant_at_vB_axis = jnp.abs(y) < 5

    if vxB_axis_mode == "replace":
        traces_geoce = traces_geoce.at[:,ant_at_vB_axis,:].set(traces_geoce[:,ant_at_vvB_axis,:])
    elif vxB_axis_mode == "zero":
        # for the vxB component, set to zero
        traces_geoce = traces_geoce.at[:,ant_at_vB_axis,:].set(0.0)
    elif vxB_axis_mode == "average":
        # for the vxB component, average the vxvxB and vxB components
        arm_idces = jnp.arange(0, len(x), 8, dtype=int)
        traces_geoce = traces_geoce.at[:,arm_idces,:].set(
            0.5 * (traces_geoce[:,arm_idces+1,:] + traces_geoce[:,arm_idces+7,:])
        )
        traces_geoce = traces_geoce.at[:,arm_idces+4,:].set(
            0.5 * (traces_geoce[:,arm_idces+3,:] + traces_geoce[:,arm_idces+5,:])
        )

    else:
        raise ValueError(f"Unknown vxB_axis_mode: {vxB_axis_mode}. Must be one of 'replace' or 'zero'.")

    return traces_geoce