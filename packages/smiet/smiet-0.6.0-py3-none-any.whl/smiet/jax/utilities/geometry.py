import jax
import jax.numpy as jnp


# source: https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
def unit_vector(vector : jax.typing.ArrayLike) -> jax.Array:
    """ Returns the unit vector of the vector.  """
    return vector / jnp.linalg.norm(vector, axis=0)


def angle_between(v1 : jax.typing.ArrayLike, v2 : jax.typing.ArrayLike) -> jax.Array:
    """ Returns the angle in radians between vectors 'v1' and 'v2' """
    if v1.shape[-1] != 3 or v2.shape[-1] != 3:
        raise ValueError("Lengths dont match. Last axis should be position")
    v1_u = unit_vector(v1.T).T
    v2_u = unit_vector(v2.T).T
    return jnp.arccos(jnp.clip(jnp.einsum("...i,...i-> ...", v1_u, v2_u), -1.0, 1.0))
