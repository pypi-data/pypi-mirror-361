# Mikel Broström 🔥 Yolo Tracking 🧾 AGPL-3.0 license

from __future__ import absolute_import

import numpy as np
from scipy.optimize import linear_sum_assignment

from boxmot.utils.matching import chi2inv95

INFTY_COST = 1e5


def min_cost_matching(
    distance_metric,
    max_distance,
    tracks,
    detections,
    track_indices=None,
    detection_indices=None,
):
    """Solve linear assignment problem.
    Parameters
    ----------
    distance_metric : Callable[List[Track], List[Detection], List[int], List[int]) -> ndarray
        The distance metric is given a list of tracks and detections as well as
        a list of N track indices and M detection indices. The metric should
        return the NxM dimensional cost matrix, where element (i, j) is the
        association cost between the i-th track in the given track indices and
        the j-th detection in the given detection_indices.
    max_distance : float
        Gating threshold. Associations with cost larger than this value are
        disregarded.
    tracks : List[track.Track]
        A list of predicted tracks at the current time step.
    detections : List[detection.Detection]
        A list of detections at the current time step.
    track_indices : List[int]
        List of track indices that maps rows in `cost_matrix` to tracks in
        `tracks` (see description above).
    detection_indices : List[int]
        List of detection indices that maps columns in `cost_matrix` to
        detections in `detections` (see description above).
    Returns
    -------
    (List[(int, int)], List[int], List[int])
        Returns a tuple with the following three entries:
        * A list of matched track and detection indices.
        * A list of unmatched track indices.
        * A list of unmatched detection indices.
    """
    print(f"------ min_cost_matching 函数开始执行 ------")
    print(f"max_distance: {max_distance}")
    
    if track_indices is None:
        track_indices = np.arange(len(tracks))
    if detection_indices is None:
        detection_indices = np.arange(len(detections))
    
    print(f"track_indices: {track_indices}")
    print(f"detection_indices: {detection_indices}")

    if len(detection_indices) == 0 or len(track_indices) == 0:
        print(f"------ 没有可匹配的轨迹或检测 ------")
        return [], track_indices, detection_indices  # Nothing to match.

    print(f"------ 准备调用 distance_metric ------")
    try:
        cost_matrix = distance_metric(tracks, detections, track_indices, detection_indices)
        print(f"------ distance_metric 执行完成 ------")
        print(f"cost_matrix shape: {cost_matrix.shape}")
    except Exception as e:
        print(f"------ distance_metric 发生异常: {e} ------")
        import traceback
        traceback.print_exc()
        raise e
    
    cost_matrix[cost_matrix > max_distance] = max_distance + 1e-5
    print(f"------ 准备调用 linear_sum_assignment ------")
    try:
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        print(f"------ linear_sum_assignment 执行完成 ------")
        print(f"row_indices: {row_indices}")
        print(f"col_indices: {col_indices}")
    except Exception as e:
        print(f"------ linear_sum_assignment 发生异常: {e} ------")
        import traceback
        traceback.print_exc()
        raise e

    matches, unmatched_tracks, unmatched_detections = [], [], []
    for col, detection_idx in enumerate(detection_indices):
        if col not in col_indices:
            unmatched_detections.append(detection_idx)
    for row, track_idx in enumerate(track_indices):
        if row not in row_indices:
            unmatched_tracks.append(track_idx)
    for row, col in zip(row_indices, col_indices):
        track_idx = track_indices[row]
        detection_idx = detection_indices[col]
        if cost_matrix[row, col] > max_distance:
            unmatched_tracks.append(track_idx)
            unmatched_detections.append(detection_idx)
        else:
            matches.append((track_idx, detection_idx))
    return matches, unmatched_tracks, unmatched_detections


def matching_cascade(
    distance_metric,
    max_distance,
    cascade_depth,
    tracks,
    detections,
    track_indices=None,
    detection_indices=None,
):
    """Run matching cascade.
    Parameters
    ----------
    distance_metric : Callable[List[Track], List[Detection], List[int], List[int]) -> ndarray
        The distance metric is given a list of tracks and detections as well as
        a list of N track indices and M detection indices. The metric should
        return the NxM dimensional cost matrix, where element (i, j) is the
        association cost between the i-th track in the given track indices and
        the j-th detection in the given detection indices.
    max_distance : float
        Gating threshold. Associations with cost larger than this value are
        disregarded.
    cascade_depth: int
        The cascade depth, should be se to the maximum track age.
    tracks : List[track.Track]
        A list of predicted tracks at the current time step.
    detections : List[detection.Detection]
        A list of detections at the current time step.
    track_indices : Optional[List[int]]
        List of track indices that maps rows in `cost_matrix` to tracks in
        `tracks` (see description above). Defaults to all tracks.
    detection_indices : Optional[List[int]]
        List of detection indices that maps columns in `cost_matrix` to
        detections in `detections` (see description above). Defaults to all
        detections.
    Returns
    -------
    (List[(int, int)], List[int], List[int])
        Returns a tuple with the following three entries:
        * A list of matched track and detection indices.
        * A list of unmatched track indices.
        * A list of unmatched detection indices.
    """
    print(f"------ matching_cascade 函数开始执行 ------")
    print(f"max_distance: {max_distance}, cascade_depth: {cascade_depth}")
    print(f"tracks count: {len(tracks)}, detections count: {len(detections)}")
    
    if track_indices is None:
        track_indices = list(range(len(tracks)))
    if detection_indices is None:
        detection_indices = list(range(len(detections)))
    
    print(f"track_indices: {track_indices}")
    print(f"detection_indices: {detection_indices}")

    unmatched_detections = detection_indices
    matches = []
    track_indices_l = [k for k in track_indices]
    
    print(f"------ 准备调用 min_cost_matching ------")
    try:
        matches_l, _, unmatched_detections = min_cost_matching(
            distance_metric,
            max_distance,
            tracks,
            detections,
            track_indices_l,
            unmatched_detections,
        )
        print(f"------ min_cost_matching 执行完成 ------")
        print(f"matches_l: {matches_l}")
    except Exception as e:
        print(f"------ min_cost_matching 发生异常: {e} ------")
        import traceback
        traceback.print_exc()
        raise e
    
    matches += matches_l
    unmatched_tracks = list(set(track_indices) - set(k for k, _ in matches))
    
    print(f"------ matching_cascade 函数执行完成 ------")
    print(f"final matches: {matches}")
    print(f"final unmatched_tracks: {unmatched_tracks}")
    print(f"final unmatched_detections: {unmatched_detections}")
    
    return matches, unmatched_tracks, unmatched_detections


def gate_cost_matrix(
    cost_matrix,
    tracks,
    detections,
    track_indices,
    detection_indices,
    mc_lambda,
    gated_cost=INFTY_COST,
    only_position=False,
):
    """Invalidate infeasible entries in cost matrix based on the state
    distributions obtained by Kalman filtering.
    Parameters
    ----------
    kf : The Kalman filter.
    cost_matrix : ndarray
        The NxM dimensional cost matrix, where N is the number of track indices
        and M is the number of detection indices, such that entry (i, j) is the
        association cost between `tracks[track_indices[i]]` and
        `detections[detection_indices[j]]`.
    tracks : List[track.Track]
        A list of predicted tracks at the current time step.
    detections : List[detection.Detection]
        A list of detections at the current time step.
    track_indices : List[int]
        List of track indices that maps rows in `cost_matrix` to tracks in
        `tracks` (see description above).
    detection_indices : List[int]
        List of detection indices that maps columns in `cost_matrix` to
        detections in `detections` (see description above).
    gated_cost : Optional[float]
        Entries in the cost matrix corresponding to infeasible associations are
        set this value. Defaults to a very large value.
    only_position : Optional[bool]
        If True, only the x, y position of the state distribution is considered
        during gating. Defaults to False.
    Returns
    -------
    ndarray
        Returns the modified cost matrix.
    """

    gating_threshold = chi2inv95[4]
    measurements = np.asarray([detections[i].to_xyah() for i in detection_indices])
    for row, track_idx in enumerate(track_indices):
        track = tracks[track_idx]
        gating_distance = track.kf.gating_distance(
            track.mean, track.covariance, measurements, only_position
        )
        cost_matrix[row, gating_distance > gating_threshold] = gated_cost
        cost_matrix[row] = (
            mc_lambda * cost_matrix[row] + (1 - mc_lambda) * gating_distance
        )
    return cost_matrix
