from core.base_exercise import BaseExercise


class LungesDetector(BaseExercise):
    """
    Detects lunges and evaluates form.

    Features:
    - Rep counting
    - Front knee angle tracking
    - Torso posture monitoring
    - Balance detection
    - Form scoring
    """

    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160

    MIN_VISIBILITY = 0.7
    BALANCE_TOLERANCE = 0.10

    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27

    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    BALANCED = "BALANCED"
    OFF_BALANCE = "OFF BALANCE"

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        # Left knee angle
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE),
        )

        # Right knee angle
        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE),
        )

        # Determine front leg
        if left_knee_angle <= right_knee_angle:
            front_knee_angle = left_knee_angle
            front_hip_idx = self.LEFT_HIP
            front_knee_idx = self.LEFT_KNEE
            front_ankle_idx = self.LEFT_ANKLE
            shoulder_idx = self.LEFT_SHOULDER
        else:
            front_knee_angle = right_knee_angle
            front_hip_idx = self.RIGHT_HIP
            front_knee_idx = self.RIGHT_KNEE
            front_ankle_idx = self.RIGHT_ANKLE
            shoulder_idx = self.RIGHT_SHOULDER

        # Visibility check
        key_landmarks_visible = all(
            landmarks[idx].visibility > self.MIN_VISIBILITY
            for idx in (
                front_hip_idx,
                front_knee_idx,
                front_ankle_idx,
            )
        )

        if not key_landmarks_visible:
            return {
                "reps": self.reps,
                "stage": self.stage,
                "front_knee_angle": 0,
                "torso_angle": 0,
                "balance_status": "NOT VISIBLE",
                "form_score": 0,
            }

        # Rep counting
        if front_knee_angle <= self.DOWN_THRESHOLD:
            self.stage = "down"

        elif (
            front_knee_angle >= self.UP_THRESHOLD
            and self.stage == "down"
        ):
            self.stage = "up"
            self.reps += 1

        # Torso posture
        torso_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, front_hip_idx),
            self.get_point(landmarks, front_knee_idx),
        )

        # Balance detection
        shoulder_mid_x = (
            landmarks[self.LEFT_SHOULDER].x
            + landmarks[self.RIGHT_SHOULDER].x
        ) / 2

        hip_mid_x = (
            landmarks[self.LEFT_HIP].x
            + landmarks[self.RIGHT_HIP].x
        ) / 2

        lateral_offset = abs(
            shoulder_mid_x - hip_mid_x
        )

        if lateral_offset <= self.BALANCE_TOLERANCE:
            balance_status = self.BALANCED
        else:
            balance_status = self.OFF_BALANCE

        # Form Score
        form_score = 100

        if balance_status == self.OFF_BALANCE:
            form_score -= 20

        if torso_angle < 140:
            form_score -= 15

        form_score = max(form_score, 0)

        return {
            "reps": self.reps,
            "stage": self.stage,
            "front_knee_angle": int(front_knee_angle),
            "torso_angle": int(torso_angle),
            "balance_status": balance_status,
            "form_score": form_score,
        }