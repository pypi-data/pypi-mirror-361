import enum
from typing import Annotated, Sequence, Tuple, overload

from numpy.typing import ArrayLike


Curvature: EFeatureID = EFeatureID.Curvature

class EFeatureID(enum.Enum):
    Linearity = 0

    Planarity = 1

    Scattering = 2

    VerticalityPGEOF = 3

    Normal_x = 4

    Normal_y = 5

    Normal_z = 6

    Length = 7

    Surface = 8

    Volume = 9

    Curvature = 10

    K_optimal = 11

    Verticality = 12

    Eigentropy = 13

Eigentropy: EFeatureID = EFeatureID.Eigentropy

K_optimal: EFeatureID = EFeatureID.K_optimal

Length: EFeatureID = EFeatureID.Length

Linearity: EFeatureID = EFeatureID.Linearity

Normal_x: EFeatureID = EFeatureID.Normal_x

Normal_y: EFeatureID = EFeatureID.Normal_y

Normal_z: EFeatureID = EFeatureID.Normal_z

Planarity: EFeatureID = EFeatureID.Planarity

Scattering: EFeatureID = EFeatureID.Scattering

Surface: EFeatureID = EFeatureID.Surface

Verticality: EFeatureID = EFeatureID.Verticality

VerticalityPGEOF: EFeatureID = EFeatureID.VerticalityPGEOF

Volume: EFeatureID = EFeatureID.Volume

def compute_features(xyz: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], nn: Annotated[ArrayLike, dict(dtype='uint32', writable=False, shape=(None))], nn_ptr: Annotated[ArrayLike, dict(dtype='uint32', writable=False, shape=(None))], k_min: int = 1, verbose: bool = False) -> Annotated[ArrayLike, dict(dtype='float32', shape=(None, 11))]:
    """
    Compute a set of geometric features for a point cloud from a precomputed list of neighbors.

    * The following features are computed:
    - linearity
    - planarity
    - scattering
    - verticality
    - normal vector (oriented towards positive z-coordinates)
    - length
    - surface
    - volume
    - curvature
    :param xyz: The point cloud. A numpy array of shape (n, 3).
    :param nn: Integer 1D array. Flattened neighbor indices. Make sure those are all positive,
    '-1' indices will either crash or silently compute incorrect features.
    :param nn_ptr: [n_points+1] Integer 1D array. Pointers wrt 'nn'. More specifically, the neighbors of point 'i'
    are 'nn[nn_ptr[i]:nn_ptr[i + 1]]'.
    :param k_min: Minimum number of neighbors to consider for features computation. If a point has less,
    its features will be a set of '0' values.
    :param verbose: Whether computation progress should be printed out
    :return: the geometric features associated with each point's neighborhood in a (num_points, features_count) numpy array.
    """

def compute_features_multiscale(xyz: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], nn: Annotated[ArrayLike, dict(dtype='uint32', writable=False, shape=(None))], nn_ptr: Annotated[ArrayLike, dict(dtype='uint32', writable=False, shape=(None))], k_scales: Sequence[int], verbose: bool = False) -> Annotated[ArrayLike, dict(dtype='float32', shape=(None, None, 11))]:
    """
    Compute a set of geometric features for a point cloud in a multiscale fashion.

    * The following features are computed:
    - linearity
    - planarity
    - scattering
    - verticality
    - normal vector (oriented towards positive z-coordinates)
    - length
    - surface
    - volume
    - curvature

    :param xyz: The point cloud. A numpy array of shape (n, 3).
    :param nn: Integer 1D array. Flattened neighbor indices. Make sure those are all positive,
    '-1' indices will either crash or silently compute incorrect features.
    :param nn_ptr: [n_points+1] Integer 1D array. Pointers wrt 'nn'. More specifically, the neighbors of point 'i'
    are 'nn[nn_ptr[i]:nn_ptr[i + 1]]'.
    :param k_scale: Array of number of neighbors to consider for features computation. If a at a given scale, a point has
    less features will be a set of '0' values.
    :param verbose: Whether computation progress should be printed out
    :return: Geometric features associated with each point's neighborhood in a (num_points, features_count, n_scales)
    numpy array.
    """

def compute_features_optimal(xyz: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], nn: Annotated[ArrayLike, dict(dtype='uint32', writable=False, shape=(None))], nn_ptr: Annotated[ArrayLike, dict(dtype='uint32', writable=False, shape=(None))], k_min: int = 1, k_step: int = 1, k_min_search: int = 1, verbose: bool = False) -> Annotated[ArrayLike, dict(dtype='float32', shape=(None, 12))]:
    """
    Compute a set of geometric features for a point cloud using the optimal neighborhood selection described in
    http://lareg.ensg.eu/labos/matis/pdf/articles_revues/2015/isprs_wjhm_15.pdf

    * The following features are computed:
    - linearity
    - planarity
    - scattering
    - verticality
    - normal vector (oriented towards positive z-coordinates)
    - length
    - surface
    - volume
    - curvature
    - optimal_nn
    :param xyz: the point cloud
    :param nn: Integer 1D array. Flattened neighbor indices. Make sure those are all positive,
    '-1' indices will either crash or silently compute incorrect features.
    :param nn_ptr: [n_points+1] Integer 1D array. Pointers wrt 'nn'. More specifically, the neighbors of point 'i'
    are 'nn[nn_ptr[i]:nn_ptr[i + 1]]'.
    :param k_min: Minimum number of neighbors to consider for features computation. If a point has less,
    its features will be a set of '0' values.
    :param k_step: Step size to take when searching for the optimal neighborhood, size for each point following
    Weinmann, 2015
    :param k_min_search: Minimum neighborhood size at which to start when searching for the optimal neighborhood size for
    each point. It is advised to use a value of 10 or higher, for geometric features robustness.
    :param verbose: Whether computation progress should be printed out
    :return: Geometric features associated with each point's neighborhood in a (num_points, features_count) numpy array.
    """

@overload
def compute_features_selected(xyz: Annotated[ArrayLike, dict(dtype='float64', writable=False, shape=(None, 3), order='None')], search_radius: float, max_knn: int, selected_features: Sequence[EFeatureID]) -> Annotated[ArrayLike, dict(dtype='float64', shape=(None, None))]:
    """
    Compute a selected set of geometric features for a point cloud via radius search.

    This function aims to mimick the behavior of jakteristics and provide an efficient way
    to compute a limited set of features (double precision version).

    :param xyz: the point cloud. A numpy array of shape (n, 3).
    :param search_radius: the search radius. A numpy array of shape (n, 3).
    :param max_knn: the maximum number of neighbors to fetch inside the sphere. The central point is included. Fixing a
    reasonable max number of neighbors prevents running OOM for large radius/dense point clouds.
    :param selected_features: List of selected features. See EFeatureID
    :return: Geometric features associated with each point's neighborhood in a (num_points, features_count) numpy array.
    """

@overload
def compute_features_selected(xyz: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], search_radius: float, max_knn: int, selected_features: Sequence[EFeatureID]) -> Annotated[ArrayLike, dict(dtype='float32', shape=(None, None))]:
    """
    Compute a selected set of geometric features for a point cloud via radius search.

    This function aims to mimic the behavior of jakteristics and provide an efficient way
    to compute a limited set of features (float precision version).

    :param xyz: the point cloud
    :param search_radius: the search radius.
    :param max_knn: the maximum number of neighbors to fetch inside the sphere. The central point is included. Fixing a
    reasonable max number of neighbors prevents running OOM for large radius/dense point clouds.
    :param selected_features: List of selected features. See EFeatureID
    :return: Geometric features associated with each point's neighborhood in a (num_points, features_count) numpy array.
    """

def knn_search(data: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], query: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], knn: int) -> Tuple[Annotated[ArrayLike, dict(dtype='uint32', shape=(None, None))], Annotated[ArrayLike, dict(dtype='float32', shape=(None, None))]]:
    """
    Given two point clouds, compute for each point present in one of the point cloud 
    the N closest points in the other point cloud

    It should be faster than scipy.spatial.KDTree for this task.

    :param data: the reference point cloud. A numpy array of shape (n, 3).
    :param query: the point cloud used for the queries. A numpy array of shape (n, 3).
    :param knn: the number of neighbors to take into account for each point.
    :return: a pair of arrays, both of size (n_points x knn), the first one contains the indices of each neighbor, the
    second one the square distances between the query point and each of its neighbors.
    """

def radius_search(data: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], query: Annotated[ArrayLike, dict(dtype='float32', writable=False, shape=(None, 3), order='None')], search_radius: float, max_knn: int) -> Tuple[Annotated[ArrayLike, dict(dtype='int32', shape=(None, None))], Annotated[ArrayLike, dict(dtype='float32', shape=(None, None))]]:
    """
    Search for the points within a specified sphere in a point cloud.

    It could be a fallback replacement for FRNN into SuperPointTransformer code base.
    It should be faster than scipy.spatial.KDTree for this task.

    :param data: the reference point cloud. A numpy array of shape (n, 3).
    :param query: the point cloud used for the queries (sphere centers). A numpy array of shape (n, 3).
    :param search_radius: the search radius.
    :param max_knn: the maximum number of neighbors to fetch inside the radius. The central point is included. Fixing a
    reasonable max number of neighbors prevents running OOM for large radius/dense point clouds.
    :return: a pair of arrays, both of size (n_points x knn), the first one contains the 'indices' of each neighbor,
    the second one the 'square_distances' between the query point and each neighbor. Point having a number of neighbors <
    'max_knn' inside the 'search_radius' will have their 'indices' and and 'square_distances' filled respectively with
    '-1' and 'O' for any missing neighbor.
    """
