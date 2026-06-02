from core.base_exercise import BaseExercise


class SquatDetector(BaseExercise):
    """
    Detects squats and evaluates form.

    Features:
    - Rep counting
    - Squat depth analysis
    - Back posture monitoring
    - Form scoring
    """

    DOWN_THRESHOLD = 100
    UP_THRESHOLD = 160

    MIN_VISIBILITY = 0.7

    LEFT_HIP = 23
    LEFT_KNEE = 25
    LEFT_ANKLE = 27

    RIGHT_HIP = 24
    RIGHT_KNEE = 26
    RIGHT_ANKLE = 28

    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    GOOD_DEPTH = "GOOD DEPTH"
    TOO_HIGH = "TOO HIGH"
    STANDING = "STANDING"

    GOOD_POSTURE = "GOOD POSTURE"
    LEANING_FORWARD = "LEANING FORWARD"

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        # Calculate knee angles
        left_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.LEFT_HIP),
            self.get_point(landmarks, self.LEFT_KNEE),
            self.get_point(landmarks, self.LEFT_ANKLE),
        )

        right_knee_angle = self.calculate_angle(
            self.get_point(landmarks, self.RIGHT_HIP),
            self.get_point(landmarks, self.RIGHT_KNEE),
            self.get_point(landmarks, self.RIGHT_ANKLE),
        )

        # Select side with better visibility
        left_vis = landmarks[self.LEFT_KNEE].visibility
        right_vis = landmarks[self.RIGHT_KNEE].visibility

        if left_vis >= right_vis:
            knee_angle = left_knee_angle
            hip_idx = self.LEFT_HIP
            knee_idx = self.LEFT_KNEE
            ankle_idx = self.LEFT_ANKLE
            shoulder_idx = self.LEFT_SHOULDER
        else:
            knee_angle = right_knee_angle
            hip_idx = self.RIGHT_HIP
            knee_idx = self.RIGHT_KNEE
            ankle_idx = self.RIGHT_ANKLE
            shoulder_idx = self.RIGHT_SHOULDER

        # Visibility check
        key_landmarks_visible = all(
            landmarks[idx].visibility >= self.MIN_VISIBILITY
            for idx in (
                hip_idx,
                knee_idx,
                ankle_idx,
                shoulder_idx,
            )
        )

        if not key_landmarks_visible:
            return {
                "reps": self.reps,
                "stage": self.stage,
                "knee_angle": 0,
                "back_angle": 0,
                "depth_status": "NOT VISIBLE",
                "posture_status": "NOT VISIBLE",
                "form_score": 0,
            }

        # Back angle
        back_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, knee_idx),
        )

        # Rep counting
        if knee_angle <= self.DOWN_THRESHOLD:
            self.stage = "down"

        elif (
            knee_angle >= self.UP_THRESHOLD
            and self.stage == "down"
        ):
            self.stage = "up"
            self.reps += 1

        # Depth analysis
        if self.stage == "down":
            if knee_angle <= self.DOWN_THRESHOLD:
                depth_status = self.GOOD_DEPTH
            else:
                depth_status = self.TOO_HIGH

        elif self.stage == "up":
            depth_status = self.STANDING

        else:
            depth_status = "N/A"

        # Back posture analysis
        if back_angle >= 150:
            posture_status = self.GOOD_POSTURE
        else:
            posture_status = self.LEANING_FORWARD

        # Form Score
        form_score = 100

        if depth_status == self.TOO_HIGH:
            form_score -= 20

        if posture_status == self.LEANING_FORWARD:
            form_score -= 20

        form_score = max(form_score, 0)

        return {
            "reps": self.reps,
            "stage": self.stage,
            "knee_angle": int(knee_angle),
            "back_angle": int(back_angle),
            "depth_status": depth_status,
            "posture_status": posture_status,
            "form_score": form_score,
        }