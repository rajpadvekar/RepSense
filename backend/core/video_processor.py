import threading
import cv2
import av
import mediapipe as mp
from typing import Optional, Dict, Any

# Import exercise detectors
from detectors.bicep_curls import BicepsCurlDetector
from detectors.squat import SquatDetector
from detectors.pushups import PushUpDetector
from detectors.lunges import LungesDetector
from detectors.shoulder_press import ShoulderPressDetector


class VideoProcessor:
    """
    A thread-safe video processor for streamlit-webrtc that runs pose estimation,
    overlays keypoints/skeleton, updates the active exercise detector,
    and returns metrics to the Streamlit UI.
    """

    def __init__(self) -> None:
        # Thread locks for safe access
        self.lock = threading.Lock()
        
        # MediaPipe Solutions
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Detector state
        self.active_exercise_name: Optional[str] = None
        self.detector: Optional[Any] = None
        
        # Live stats dictionary
        self.stats: Dict[str, Any] = {
            "reps": 0,
            "stage": "N/A",
            "form_score": 100,
            "feedback": "Position yourself in front of the camera.",
            "metrics": {}
        }

    def set_exercise(self, exercise_name: str) -> None:
        """
        Switches the active exercise detector. Thread-safe.
        """
        with self.lock:
            if self.active_exercise_name == exercise_name and self.detector is not None:
                return

            self.active_exercise_name = exercise_name
            name = exercise_name.lower().replace(" ", "_")

            if "squat" in name:
                self.detector = SquatDetector()
            elif "push" in name:
                self.detector = PushUpDetector()
            elif "curl" in name:
                self.detector = BicepsCurlDetector()
            elif "lunge" in name:
                self.detector = LungesDetector()
            elif "press" in name:
                self.detector = ShoulderPressDetector()
            else:
                self.detector = None

            # Reset the stats buffer for the new exercise
            self.stats = {
                "reps": 0,
                "stage": "N/A",
                "form_score": 100,
                "feedback": "Ready! Start your first rep.",
                "metrics": {}
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Retrieves the latest workout stats. Thread-safe.
        """
        with self.lock:
            return self.stats.copy()

    def reset_reps(self) -> None:
        """
        Resets the counter on the current detector. Thread-safe.
        """
        with self.lock:
            if self.detector:
                self.detector.reset()
            self.stats["reps"] = 0
            self.stats["stage"] = "N/A"
            self.stats["form_score"] = 100
            self.stats["feedback"] = "Counter reset."

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Processes incoming camera frame (runs MediaPipe + exercises logic + HUD overlay).
        """
        img = frame.to_ndarray(format="bgr24")
        
        # Mirror flip for natural webcam interaction
        img = cv2.flip(img, 1)
        h, w, _ = img.shape

        # Run MediaPipe Pose Estimation
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)

        if results.pose_landmarks:
            # Draw skeletal lines & keypoints on the image
            # Custom styling: Cyan joints with Amber bone lines
            self.mp_draw.draw_landmarks(
                img,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 212, 255), thickness=3, circle_radius=3),
                self.mp_draw.DrawingSpec(color=(245, 166, 35), thickness=2, circle_radius=2)
            )

            # Extract metrics via detector
            with self.lock:
                if self.detector:
                    try:
                        landmarks = results.pose_landmarks.landmark
                        # Run the exercise processing calculations
                        res = self.detector.process(landmarks)
                        
                        # Populate stats buffer
                        self.stats["reps"] = res.get("reps", 0)
                        self.stats["stage"] = res.get("stage", "N/A")
                        self.stats["form_score"] = res.get("form_score", 100)
                        
                        # Handle feedback messages (could be list or string)
                        raw_feedback = res.get("feedback", "Good form!")
                        if isinstance(raw_feedback, list):
                            self.stats["feedback"] = raw_feedback[0] if raw_feedback else "Keep it up!"
                        else:
                            # Map standard status messages for detectors without feedback arrays
                            self.stats["feedback"] = self._resolve_feedback(res)
                        
                        self.stats["metrics"] = res
                    except Exception as e:
                        print(f"Error executing detector pipeline: {e}")

            # Draw HUD Overlay directly on the frame (Premium look)
            reps = self.stats["reps"]
            stage = str(self.stats["stage"]).upper() if self.stats["stage"] else "N/A"
            score = self.stats["form_score"]
            feedback = self.stats["feedback"]

            # HUD Background Box
            cv2.rectangle(img, (20, 20), (320, 160), (15, 15, 15), -1)
            cv2.rectangle(img, (20, 20), (320, 160), (0, 212, 255), 1)

            # Text draws
            cv2.putText(img, f"EXERCISE: {str(self.active_exercise_name).upper()}", (35, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 212, 255), 1)
            cv2.putText(img, f"REPS: {reps}", (35, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, f"STAGE: {stage}", (35, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Color code form score
            score_color = (0, 255, 0) if score >= 85 else ((0, 165, 255) if score >= 70 else (0, 0, 255))
            cv2.putText(img, f"FORM SCORE: {score}%", (35, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, score_color, 1)

            # Floating feedback alert at the bottom of the screen
            feedback_bg_w = int(w * 0.8)
            start_x = int((w - feedback_bg_w) / 2)
            cv2.rectangle(img, (start_x, h - 60), (start_x + feedback_bg_w, h - 20), (10, 10, 10), -1)
            cv2.rectangle(img, (start_x, h - 60), (start_x + feedback_bg_w, h - 20), (245, 166, 35), 1)
            cv2.putText(img, f"COACH: {feedback}", (start_x + 15, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        else:
            with self.lock:
                self.stats["feedback"] = "Adjust camera. Skeleton not detected."

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    @staticmethod
    def _resolve_feedback(res: Dict[str, Any]) -> str:
        """
        Helper to map specific posture/form metrics into text prompts for HUD display.
        """
        # Biceps Curl
        if "shoulder_status" in res and res["shoulder_status"] == "ELBOW DRIFTING":
            return "Keep your elbows locked at your sides!"
        if "swing_status" in res and res["swing_status"] == "SWINGING":
            return "Stop swinging! Brace your core."

        # Squat
        if "depth_status" in res and res["depth_status"] == "TOO HIGH":
            return "Go lower! Aim for parallel depth."
        if "posture_status" in res and res["posture_status"] == "LEANING FORWARD":
            return "Keep your chest up! Avoid leaning forward."

        # Pushup
        if "body_alignment" in res and res["body_alignment"] == "POOR FORM":
            return "Straighten your body! Engaged spine."
        if "hip_status" in res and res["hip_status"] == "SAGGING":
            return "Lift your hips! Stop sagging."
        elif "hip_status" in res and res["hip_status"] == "PIKED UP":
            return "Lower your hips to form a straight line."

        # Lunge
        if "balance_status" in res and res["balance_status"] == "OFF BALANCE":
            return "Step straight to stabilize your balance."

        # Default fallback
        form_score = res.get("form_score", 100)
        if form_score >= 90:
            return "Looking great! Keep this pace."
        return "Focus on complete, controlled range of motion."
