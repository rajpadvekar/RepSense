from core.base_exercise import BaseExercise


class PushUpDetector(BaseExercise):
    """
    Detects push-ups and evaluates form.

    Features:
    - Rep counting
    - Body alignment detection
    - Hip sag/pike detection
    - Form score calculation
    """

    DOWN_THRESHOLD = 90
    UP_THRESHOLD = 160

    MIN_VISIBILITY = 0.7
    HIP_SAG_TOLERANCE = 0.08

    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15

    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16

    LEFT_HIP = 23
    RIGHT_HIP = 24

    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28

    STRAIGHT = "STRAIGHT"
    SLIGHT_BEND = "SLIGHT BEND"
    POOR_FORM = "POOR FORM"

    LEVEL = "LEVEL"
    SAGGING = "SAGGING"
    PIKED_UP = "PIKED UP"

    def __init__(self):
        super().__init__()

    def reset(self) -> None:
        self.reps = 0
        self.stage = None

    def process(self, landmarks) -> dict:
        # Select side with better visibility
        left_vis = landmarks[self.LEFT_ELBOW].visibility
        right_vis = landmarks[self.RIGHT_ELBOW].visibility

        if left_vis >= right_vis:
            shoulder_idx = self.LEFT_SHOULDER
            elbow_idx = self.LEFT_ELBOW
            wrist_idx = self.LEFT_WRIST
            hip_idx = self.LEFT_HIP
            ankle_idx = self.LEFT_ANKLE
        else:
            shoulder_idx = self.RIGHT_SHOULDER
            elbow_idx = self.RIGHT_ELBOW
            wrist_idx = self.RIGHT_WRIST
            hip_idx = self.RIGHT_HIP
            ankle_idx = self.RIGHT_ANKLE

        # Visibility check
        key_landmarks_visible = all(
            landmarks[idx].visibility > self.MIN_VISIBILITY
            for idx in (
                shoulder_idx,
                elbow_idx,
                wrist_idx,
                hip_idx,
                ankle_idx,
            )
        )

        if not key_landmarks_visible:
            return {
                "reps": self.reps,
                "stage": self.stage,
                "elbow_angle": 0,
                "body_alignment": "NOT VISIBLE",
                "hip_status": "NOT VISIBLE",
                "form_score": 0,
            }

        # Elbow angle
        elbow_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, elbow_idx),
            self.get_point(landmarks, wrist_idx),
        )

        # Body alignment
        body_angle = self.calculate_angle(
            self.get_point(landmarks, shoulder_idx),
            self.get_point(landmarks, hip_idx),
            self.get_point(landmarks, ankle_idx),
        )

        # Rep counting
        if elbow_angle <= self.DOWN_THRESHOLD:
            self.stage = "down"

        elif (
            elbow_angle >= self.UP_THRESHOLD
            and self.stage == "down"
        ):
            self.stage = "up"
            self.reps += 1

        # Body alignment status
        if body_angle >= 160:
            body_alignment = self.STRAIGHT

        elif body_angle >= 140:
            body_alignment = self.SLIGHT_BEND

        else:
            body_alignment = self.POOR_FORM

        # Hip position analysis
        shoulder_y = landmarks[shoulder_idx].y
        hip_y = landmarks[hip_idx].y
        ankle_y = landmarks[ankle_idx].y

        expected_hip_y = (
            shoulder_y + ankle_y
        ) / 2

        hip_deviation = (
            hip_y - expected_hip_y
        )

        if abs(hip_deviation) <= self.HIP_SAG_TOLERANCE:
            hip_status = self.LEVEL

        elif hip_deviation > self.HIP_SAG_TOLERANCE:
            hip_status = self.SAGGING

        else:
            hip_status = self.PIKED_UP

        # Form Score
        form_score = 100

        if body_alignment == self.POOR_FORM:
            form_score -= 25

        elif body_alignment == self.SLIGHT_BEND:
            form_score -= 10

        if hip_status == self.SAGGING:
            form_score -= 20

        elif hip_status == self.PIKED_UP:
            form_score -= 15

        form_score = max(form_score, 0)

        return {
            "reps": self.reps,
            "stage": self.stage,
            "elbow_angle": int(elbow_angle),
            "body_angle": int(body_angle),
            "body_alignment": body_alignment,
            "hip_status": hip_status,
            "form_score": form_score,
        }