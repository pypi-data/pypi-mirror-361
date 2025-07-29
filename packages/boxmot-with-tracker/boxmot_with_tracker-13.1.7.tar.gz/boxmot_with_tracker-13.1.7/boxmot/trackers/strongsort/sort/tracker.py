# Mikel Broström 🔥 Yolo Tracking 🧾 AGPL-3.0 license

from __future__ import absolute_import

import numpy as np

from boxmot.motion.cmc import get_cmc_method
from boxmot.trackers.strongsort.sort import iou_matching, linear_assignment
from boxmot.trackers.strongsort.sort.track import Track
from boxmot.utils.matching import chi2inv95


class Tracker:
    """
    This is the multi-target tracker.
    Parameters
    ----------
    metric : nn_matching.NearestNeighborDistanceMetric
        A distance metric for measurement-to-track association.
    max_age : int
        Maximum number of missed misses before a track is deleted.
    n_init : int
        Number of consecutive detections before the track is confirmed. The
        track state is set to `Deleted` if a miss occurs within the first
        `n_init` frames.
    Attributes
    ----------
    metric : nn_matching.NearestNeighborDistanceMetric
        The distance metric used for measurement to track association.
    max_age : int
        Maximum number of missed misses before a track is deleted.
    n_init : int
        Number of frames that a track remains in initialization phase.
    tracks : List[Track]
        The list of active tracks at the current time step.
    """

    GATING_THRESHOLD = np.sqrt(chi2inv95[4])

    def __init__(
        self,
        metric,
        max_iou_dist=0.9,
        max_age=30,
        n_init=3,
        _lambda=0,
        ema_alpha=0.9,
        mc_lambda=0.995,
    ):
        self.metric = metric
        self.max_iou_dist = max_iou_dist
        self.max_age = max_age
        self.n_init = n_init
        self._lambda = _lambda
        self.ema_alpha = ema_alpha
        self.mc_lambda = mc_lambda

        self.tracks = []
        self._next_id = 1
        self.cmc = get_cmc_method("ecc")()

    def predict(self):
        """Propagate track state distributions one time step forward.

        This function should be called once every time step, before `update`.
        """
        for track in self.tracks:
            track.predict()

    def increment_ages(self):
        for track in self.tracks:
            track.increment_age()
            track.mark_missed()

    def update(self, detections):
        """Perform measurement update and track management.

        Parameters
        ----------
        detections : List[deep_sort.detection.Detection]
            A list of detections at the current time step.

        """
        # Run matching cascade.
        matches, unmatched_tracks, unmatched_detections = self._match(detections)
        
        # 打印匹配结果的详细信息
        print(f"=== Tracker匹配结果 ===")
        print(f"matches (轨迹索引, 检测索引): {matches}")
        print(f"unmatched_tracks (未匹配轨迹索引): {unmatched_tracks}")
        print(f"unmatched_detections (未匹配检测索引): {unmatched_detections}")
        print(f"总检测数: {len(detections)}, 总轨迹数: {len(self.tracks)}")
        print(f"匹配对数: {len(matches)}, 未匹配轨迹数: {len(unmatched_tracks)}, 未匹配检测数: {len(unmatched_detections)}")
        
        # 打印每个匹配对的详细信息
        if matches:
            print("--- 匹配对详情 ---")
            for track_idx, detection_idx in matches:
                track = self.tracks[track_idx]
                detection = detections[detection_idx]
                print(f"  轨迹[{track_idx}] ID={track.id} <-> 检测[{detection_idx}] conf={detection.conf:.3f} cls={detection.cls}")
        
        # 打印未匹配轨迹的详细信息
        if unmatched_tracks:
            print("--- 未匹配轨迹详情 ---")
            for track_idx in unmatched_tracks:
                track = self.tracks[track_idx]
                state_name = {1: 'Tentative', 2: 'Confirmed', 3: 'Deleted'}.get(track.state, 'Unknown')
                print(f"  轨迹[{track_idx}] ID={track.id}, state={state_name}, time_since_update={track.time_since_update}")
        
        # 打印未匹配检测的详细信息
        if unmatched_detections:
            print("--- 未匹配检测详情 ---")
            for detection_idx in unmatched_detections:
                detection = detections[detection_idx]
                print(f"  检测[{detection_idx}] conf={detection.conf:.3f} cls={detection.cls} det_ind={detection.det_ind}")
        print("=" * 50)

        # Update track set.
        for track_idx, detection_idx in matches:
            self.tracks[track_idx].update(detections[detection_idx])
        for track_idx in unmatched_tracks:
            self.tracks[track_idx].mark_missed()
        for detection_idx in unmatched_detections:
            self._initiate_track(detections[detection_idx])
        self.tracks = [t for t in self.tracks if not t.is_deleted()]

        print(f"------- update track set done: self.tracks len: {len(self.tracks)} -------") 
        for track in self.tracks:
            print(f"track id: {track.id}, time_since_update: {track.time_since_update}")

        # Update distance metric.
        active_targets = [t.id for t in self.tracks if t.is_confirmed()]
        features, targets = [], []
        for track in self.tracks:
            if not track.is_confirmed():
                continue
            features += track.features
            targets += [track.id for _ in track.features]
        self.metric.partial_fit(
            np.asarray(features), np.asarray(targets), active_targets
        )

        print(f"------- update distance metric done: self.tracks len: {len(self.tracks)} -------") 

    def _match(self, detections):
        def gated_metric(tracks, dets, track_indices, detection_indices):
            features = np.array([dets[i].feat for i in detection_indices])
            targets = np.array([tracks[i].id for i in track_indices])
            cost_matrix = self.metric.distance(features, targets)
            cost_matrix = linear_assignment.gate_cost_matrix(
                cost_matrix,
                tracks,
                dets,
                track_indices,
                detection_indices,
                self.mc_lambda,
            )

            return cost_matrix

        # Split track set into confirmed and unconfirmed tracks.
        confirmed_tracks = [i for i, t in enumerate(self.tracks) if t.is_confirmed()]
        unconfirmed_tracks = [i for i, t in enumerate(self.tracks) if not t.is_confirmed()]

        # Associate confirmed tracks using appearance features.
        matches_a, unmatched_tracks_a, unmatched_detections = linear_assignment.matching_cascade(
            gated_metric,
            self.metric.matching_threshold,
            self.max_age,
            self.tracks,
            detections,
            confirmed_tracks,
        )

        # Associate remaining tracks together with unconfirmed tracks using IOU.
        iou_track_candidates = unconfirmed_tracks + [
            k for k in unmatched_tracks_a if self.tracks[k].time_since_update == 1
        ]
        unmatched_tracks_a = [
            k for k in unmatched_tracks_a if self.tracks[k].time_since_update != 1
        ]

        matches_b, unmatched_tracks_b, unmatched_detections = linear_assignment.min_cost_matching(
            iou_matching.iou_cost,
            self.max_iou_dist,
            self.tracks,
            detections,
            iou_track_candidates,
            unmatched_detections,
        )

        matches = matches_a + matches_b
        unmatched_tracks = list(set(unmatched_tracks_a + unmatched_tracks_b))
        return matches, unmatched_tracks, unmatched_detections

    def _initiate_track(self, detection):
        self.tracks.append(
            Track(
                detection,
                self._next_id,
                self.n_init,
                self.max_age,
                self.ema_alpha,
            )
        )
        self._next_id += 1
