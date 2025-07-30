import jax
import jax.numpy as jnp

# Core interpolation with boundary handling
def linear_interp_with_bounds(x, xp, fp):
    # Find the right index for interpolation
    idx = jnp.searchsorted(xp, x, side='right') - 1
    idx = jnp.clip(idx, 0, len(xp) - 2)

    # Interpolation logic
    x0 = jnp.take(xp, idx)
    x1 = jnp.take(xp, idx + 1)
    y0 = jnp.take(fp, idx)
    y1 = jnp.take(fp, idx + 1)

    slope = (y1 - y0) / (x1 - x0)
    y = y0 + slope * (x - x0)

    # Clamp at boundaries
    y = jnp.where(x < xp[0], fp[0], y)
    y = jnp.where(x > xp[-1], fp[-1], y)
    return y


def batched_interp1d(x, xp, fp):
    """
    Batched linear interpolation with boundary handling.

    For left and right values, the values at the boundaries are used.

    Parameters
    ----------
    x : jnp.ndarray
        Input points to interpolate. Shape: (Nant, Nslice).
    xp : jnp.ndarray
        Points to interpolate at. Shape: (Ngrid,).
    fp : jnp.ndarray
        Function values at xp. Shape: (Ngrid, Nfreq, Nslice).

    Returns
    -------
    jnp.ndarray
        Interpolated values. Shape: (Nant, Nfreq, Nslice).
    """
    Nant, Nslice = x.shape
    Ngrid, Nfreq, _ = fp.shape

    # Function to interpolate over 1 slice and 1 freq
    def interp_fn(f, s):
        x_query = x[:, s]           # shape: (Nant,)
        values = fp[:, f, s]        # shape: (Ngrid,)
        return jax.vmap(linear_interp_with_bounds, in_axes=(0, None, None))(x_query, xp, values)  # → (Nant,)

    # Generate all (f, s) index pairs
    freq_idx = jnp.arange(Nfreq)
    slice_idx = jnp.arange(Nslice)

    # Vectorize over frequency and slice
    interp_fs = jax.vmap(
        lambda f: jax.vmap(
            lambda s: interp_fn(f, s)
        )(slice_idx)
    )(freq_idx)  # shape: (Nfreq, Nslice, Nant)

    # Reorder to (Nant, Nfreq, Nslice)
    return jnp.transpose(interp_fs, (2, 0, 1))