from core.base_exercise import BaseExercise


class ShoulderPressDetector(BaseExercise):
    """
    AI Shoulder Press Detector

    Tracks:
    - Rep Count
    - Elbow Extension
    - Back Posture
    - Form Score
    - Coaching Feedback
    """

    # Movement Thresholds
    UP_THRESHOLD = 160
    DOWN_THRESHOLD = 90

    # Visibility Threshold
    MIN_VISIBILITY = 0.7

    # Left Side Landmarks
    LEFT_SHOULDER = 11
    LEFT_ELBOW = 13
    LEFT_WRIST = 15
    LEFT_HIP = 23
    LEFT_KNEE = 25

    # Right Side Landmarks
    RIGHT_SHOULDER = 12
    RIGHT_ELBOW = 14
    RIGHT_WRIST = 16
    RIGHT_HIP = 24
    RIGHT_KNEE = 26

    def __init__(self):
        super().__init__()
        self.reset()

    def reset(self) -> None:
        """Reset exercise state."""
        self.reps = 0
        self.stage = None

    def _select_side(self, landmarks):
        """
        Select the side with better landmark visibility.
        """

        left_visibility = landmarks[self.LEFT_ELBOW].visibility
        right_visibility = landmarks[self.RIGHT_ELBOW].visibility

        if left_visibility >= right_visibility:
            return {
                "shoulder": self.LEFT_SHOULDER,
                "elbow": self.LEFT_ELBOW,
                "wrist": self.LEFT_WRIST,
                "hip": self.LEFT_HIP,
                "knee": self.LEFT_KNEE,
            }

        return {
            "shoulder": self.RIGHT_SHOULDER,
            "elbow": self.RIGHT_ELBOW,
            "wrist": self.RIGHT_WRIST,
            "hip": self.RIGHT_HIP,
            "knee": self.RIGHT_KNEE,
        }

    def _calculate_elbow_angle(self, landmarks, side):
        return self.calculate_angle(
            self.get_point(landmarks, side["shoulder"]),
            self.get_point(landmarks, side["elbow"]),
            self.get_point(landmarks, side["wrist"]),
        )

    def _calculate_back_angle(self, landmarks, side):
        return self.calculate_angle(
            self.get_point(landmarks, side["shoulder"]),
            self.get_point(landmarks, side["hip"]),
            self.get_point(landmarks, side["knee"]),
        )

    def _landmarks_visible(self, landmarks, side):
        return (
            landmarks[side["shoulder"]].visibility > self.MIN_VISIBILITY
            and landmarks[side["elbow"]].visibility > self.MIN_VISIBILITY
            and landmarks[side["wrist"]].visibility > self.MIN_VISIBILITY
        )

    def _update_rep_count(self, elbow_angle):
        """
        Shoulder Press Rep Logic

        Top Position -> Arms Extended
        Bottom Position -> Arms Lowered
        """

        if elbow_angle > self.UP_THRESHOLD:
            self.stage = "up"

        elif elbow_angle < self.DOWN_THRESHOLD and self.stage == "up":
            self.stage = "down"
            self.reps += 1

    def _get_extension_status(self, elbow_angle):
        if elbow_angle >= self.UP_THRESHOLD:
            return "FULL EXTENSION"

        if elbow_angle >= 130:
            return "NEARLY EXTENDED"

        if elbow_angle >= self.DOWN_THRESHOLD:
            return "PRESSING"

        return "START POSITION"

    def _get_back_posture_status(self, back_angle):
        if back_angle >= 160:
            return "Neutral"

        if back_angle >= 140:
            return "Slight Arch"

        return "Excessive Arch"

    def _generate_feedback(
        self,
        extension_status,
        back_arch_status,
    ):
        feedback = []

        if extension_status != "FULL EXTENSION":
            feedback.append(
                "Extend your arms fully at the top of the movement."
            )

        if back_arch_status == "Slight Arch":
            feedback.append(
                "Keep your core engaged throughout the press."
            )

        elif back_arch_status == "Excessive Arch":
            feedback.append(
                "Avoid excessive lower-back arching. Brace your core."
            )

        if not feedback:
            feedback.append("Excellent form. Keep it up!")

        return feedback

    def _calculate_form_score(
        self,
        extension_status,
        back_arch_status,
    ):
        score = 100

        if extension_status == "NEARLY EXTENDED":
            score -= 5

        elif extension_status in (
            "PRESSING",
            "START POSITION",
        ):
            score -= 15

        if back_arch_status == "Slight Arch":
            score -= 10

        elif back_arch_status == "Excessive Arch":
            score -= 25

        return max(score, 0)

    def process(self, landmarks) -> dict:
        """
        Main Processing Function
        """

        side = self._select_side(landmarks)

        elbow_angle = self._calculate_elbow_angle(
            landmarks,
            side,
        )

        back_angle = self._calculate_back_angle(
            landmarks,
            side,
        )

        if self._landmarks_visible(landmarks, side):
            self._update_rep_count(elbow_angle)

        extension_status = self._get_extension_status(
            elbow_angle
        )

        back_arch_status = self._get_back_posture_status(
            back_angle
        )

        form_score = self._calculate_form_score(
            extension_status,
            back_arch_status,
        )

        feedback = self._generate_feedback(
            extension_status,
            back_arch_status,
        )

        return {
            "reps": self.reps,
            "stage": self.stage,
            "elbow_angle": int(elbow_angle),
            "back_angle": int(back_angle),
            "extension_status": extension_status,
            "back_arch_status": back_arch_status,
            "form_score": form_score,
            "feedback": feedback,
        }