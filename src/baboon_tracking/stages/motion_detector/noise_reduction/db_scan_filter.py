"""
Takes the DBSCAN Labeled set and the 2d frame, then returns
the corrected frame and labels array
"""
from sklearn.cluster import DBSCAN
import cv2
import numpy as np
from baboon_tracking.decorators.save_result import save_result
from baboon_tracking.decorators.show_result import show_result
from baboon_tracking.mixins.moving_foreground_mixin import MovingForegroundMixin
from baboon_tracking.models.frame import Frame
from pipeline import Stage
from pipeline.decorators import stage
from pipeline.stage_result import StageResult


@show_result
@save_result
@stage("moving_foreground")
class DbScanFilter(Stage, MovingForegroundMixin):
    """
    Takes the DBSCAN Labeled set and the 2d frame, then returns
    the corrected frame and labels array
    """

    def __init__(self, moving_foreground: MovingForegroundMixin) -> None:
        Stage.__init__(self)
        MovingForegroundMixin.__init__(self)

        self._moving_foreground = moving_foreground

    def _eliminate_noise(self, labels_array, frame_2d):
        """
        Takes the DBSCAN Labeled set and the 2d frame, then returns
        the corrected frame and labels array
        """
        frame_2d = np.delete(frame_2d, np.where(labels_array == -1), axis=0)
        labels_array = np.delete(labels_array, np.where(labels_array == -1), axis=0)

        return frame_2d, labels_array

    def execute(self) -> StageResult:
        moving_foreground = self._moving_foreground.moving_foreground
        two_d_frame = moving_foreground.get_frame()

        x, y = np.where(two_d_frame == 255)
        image = np.zeros((len(x), 2))
        image[:, 0] = x
        image[:, 1] = y

        # creates clusters and eliminates noise from labels and 2dframe
        dbscan = DBSCAN(eps=3, min_samples=5).fit(image)
        labels = dbscan.labels_
        image, _ = self._eliminate_noise(labels, image)
        image = image.astype(np.uint32)
        noiseless_frame = np.zeros_like(two_d_frame)
        noiseless_frame[image[:, 0], image[:, 1]] = 255

        # applies dilate filter and saves the residual frame
        kernel = np.ones((5, 5), np.uint8)
        self.moving_foreground = Frame(
            cv2.dilate(noiseless_frame, kernel, iterations=1),
            moving_foreground.get_frame_number(),
        )

        return StageResult(True, True)
