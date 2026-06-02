import math
from abc import ABC, abstractmethod


class BaseExercise(ABC):
    """
    Base class for all exercise detectors.

    Provides:
    - Rep tracking
    - Stage tracking
    - Angle calculations
    - Landmark utilities
    """

    def __init__(self):
        self.reps = 0
        self.stage = None

    @staticmethod
    def calculate_angle(a, b, c) -> float:
        """
        Calculates the angle ABC in degrees.
        """

        ax, ay = a[0] - b[0], a[1] - b[1]
        cx, cy = c[0] - b[0], c[1] - b[1]

        dot_product = ax * cx + ay * cy

        mag_a = math.hypot(ax, ay)
        mag_c = math.hypot(cx, cy)

        if mag_a == 0 or mag_c == 0:
            return 0.0

        cos_angle = dot_product / (mag_a * mag_c)

        # Clamp for numerical stability
        cos_angle = max(-1.0, min(1.0, cos_angle))

        return math.degrees(
            math.acos(cos_angle)
        )

    @staticmethod
    def get_point(landmarks, idx):
        """
        Returns (x, y) coordinates of a landmark.
        """

        point = landmarks[idx]

        return (
            point.x,
            point.y,
        )

    def reset(self) -> None:
        """
        Reset exercise state.
        """

        self.reps = 0
        self.stage = None

    @abstractmethod
    def process(self, landmarks) -> dict:
        """
        Process MediaPipe landmarks and return exercise metrics.
        """
        raise NotImplementedError