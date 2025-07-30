import numpy as np


def get_perpendicular_vectors(v):
    """
    Given a vector, return two orthogonal unit vectors.
    """
    if np.abs(v[0]) > np.abs(v[1]):
        v_perp1 = np.array([-v[2], 0, v[0]])
    else:
        v_perp1 = np.array([0, -v[2], v[1]])

    v_perp1 /= np.linalg.norm(v_perp1)
    v_perp2 = np.cross(v, v_perp1)
    v_perp2 /= np.linalg.norm(v_perp2)

    return v_perp1, v_perp2
