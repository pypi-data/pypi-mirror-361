import numpy as np


# source: https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
def unit_vector(vector):
    """
    Normalize a vector to unit length

    Parameters
    ----------
    vector : array_like
        The vector to normalize

    Returns
    -------
    unit : np.ndarray
        The unit vector of the input vector.

    Examples
    --------
    >>> unit_vector(np.array([1, 0, 0]))
    array([1., 0., 0.])

    >>> unit_vector(np.array([0, 4, 0]))
    array([0., 1., 0.])

    >>> unit_vector(np.array([3, 6, -2]))
    array([ 0.42857143,  0.85714286, -0.28571429])
    """
    return np.asarray(vector) / np.linalg.norm(vector, axis=0)


def angle_between(v1, v2):
    """
    Returns the angle in radians between vectors 'v1' and 'v2'

    Parameters
    ----------
    v1 : array_like
        First vector
    v2 : array_like
        Second vector

    Returns
    -------
    angle : float
        The angle (in radians) between the vectors

    Examples
    --------
    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966

    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0

    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    """
    v1_u = unit_vector(np.asarray(v1).T).T
    v2_u = unit_vector(np.asarray(v2).T).T

    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
