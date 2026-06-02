import math

from core.base_exercise import BaseExercise


class BicepsCurlDetector(BaseExercise):
    """
    Detects biceps curl repetitions and evaluates exercise form.

    Features:
    - Rep counting
    - Elbow drift detection
    - Body swing detection
    - Form score calculation
    """

    UP_THRESHOLD = 50
    DOWN_THRESHOLD = 160

    MIN_VISIBILITY = 0.7
    ELBOW_DRIFT_TOLERANCE = 0.06
    SWING_THRESHOLD = 15

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15

    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16

    LEFT_HIP = 23
    RIGHT_HIP = 24

    STABLE = "STABLE"
    DRIFTING = "ELBOW DRIFTING"

    NO_SWING = "NO SWING"
    SWINGING = "SWINGING"

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        # Select the arm with better visibility
        left_visibility = landmarks[self.LEFT_ELBOW].visibility
        right_visibility = landmarks[self.RIGHT_ELBOW].visibility

        if left_visibility >= right_visibility:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST

        # Check landmark visibility
        key_landmarks_visible = all(
            landmarks[idx].visibility > self.MIN_VISIBILITY
            for idx in (shoulder_idx, elbow_idx, wrist_idx)
        )

        if not key_landmarks_visible:
            return {
                "reps": self.reps,
                "stage": self.stage,
                "elbow_angle": 0,
                "shoulder_status": "NOT VISIBLE",
                "swing_status": "NOT VISIBLE",
                "form_score": 0,
            }

        # Calculate elbow angle
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        # Rep counting logic
        if elbow_angle <= self.UP_THRESHOLD:
            self.stage = "up"

        elif (
            elbow_angle >= self.DOWN_THRESHOLD
            and self.stage == "up"
        ):
            self.stage = "down"
            self.reps += 1

        # Elbow drift detection
        shoulder_x = landmarks[shoulder_idx].x
        elbow_x = landmarks[elbow_idx].x

        elbow_drift = abs(elbow_x - shoulder_x)

        if elbow_drift <= self.ELBOW_DRIFT_TOLERANCE:
            shoulder_status = self.STABLE
        else:
            shoulder_status = self.DRIFTING

        # Body swing detection
        shoulder_mid_x = (
            landmarks[self.LEFT_SHOULDER].x
            + landmarks[self.RIGHT_SHOULDER].x
        ) / 2

        shoulder_mid_y = (
            landmarks[self.LEFT_SHOULDER].y
            + landmarks[self.RIGHT_SHOULDER].y
        ) / 2

        hip_mid_x = (
            landmarks[self.LEFT_HIP].x
            + landmarks[self.RIGHT_HIP].x
        ) / 2

        hip_mid_y = (
            landmarks[self.LEFT_HIP].y
            + landmarks[self.RIGHT_HIP].y
        ) / 2

        dx = shoulder_mid_x - hip_mid_x
        dy = shoulder_mid_y - hip_mid_y

        torso_angle = self._safe_angle(dx, dy)

        if torso_angle <= self.SWING_THRESHOLD:
            swing_status = self.NO_SWING
        else:
            swing_status = self.SWINGING

        # Form Score
        form_score = 100

        if shoulder_status == self.DRIFTING:
            form_score -= 20

        if swing_status == self.SWINGING:
            form_score -= 20

        form_score = max(form_score, 0)

        return {
            "reps": self.reps,
            "stage": self.stage,
            "elbow_angle": int(elbow_angle),
            "shoulder_status": shoulder_status,
            "swing_status": swing_status,
            "form_score": form_score,
        }

    @staticmethod
    def _safe_angle(dx: float, dy: float) -> float:
        if dy == 0:
            return 0.0

        return math.degrees(
            math.atan2(abs(dx), abs(dy))
        )