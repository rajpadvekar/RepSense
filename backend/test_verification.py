import os
import sys
import unittest

# Ensure the backend directory is in path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


class TestRepSenseArchitecture(unittest.TestCase):
    """
    Verification suite to test core RepSense functions and module integrations.
    """

    def test_1_imports(self) -> None:
        """Verify all service and core modules import without ModuleNotFoundError."""
        try:
            from database.db_manager import DBManager
            from database.repositories import UserRepository, WorkoutRepository, FeedbackRepository
            from services.auth_service import AuthService
            from services.workout_service import WorkoutService
            from services.ai_coach_service import AICoachService
            from core.base_exercise import BaseExercise
            from core.video_processor import VideoProcessor
            vp = VideoProcessor()
            vp.set_exercise("Squats")
            
            from views.planner import show_planner
            
            self.assertTrue(True)
            print("[SUCCESS] All architecture imports resolved successfully.")
        except ImportError as e:
            self.fail(f"Import validation failed: {e}")
        except Exception as e:
            self.fail(f"VideoProcessor instantiation failed: {e}")

    def test_2_database_initialization(self) -> None:
        """Verify SQLite DB manager can initialize tables and build connections."""
        try:
            from database.db_manager import DBManager
            DBManager.init_db()
            conn = DBManager.get_connection()
            cursor = conn.cursor()
            
            # Check for table presence
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cursor.fetchall()]
            
            self.assertIn("users", tables)
            self.assertIn("workouts", tables)
            self.assertIn("feedback_history", tables)
            
            conn.close()
            print("[SUCCESS] SQLite database manager and table schema verified successfully.")
        except Exception as e:
            self.fail(f"Database validation failed: {e}")

    def test_3_mock_landmarks_detectors(self) -> None:
        """Feed mock coordinates to all five exercise detectors to test angle/process logic."""
        try:
            from detectors.bicep_curls import BicepsCurlDetector
            from detectors.squat import SquatDetector
            from detectors.pushups import PushUpDetector
            from detectors.lunges import LungesDetector
            from detectors.shoulder_press import ShoulderPressDetector

            # Create mock MediaPipe landmark objects
            class MockLandmark:
                def __init__(self, x: float, y: float, visibility: float = 0.9):
                    self.x = x
                    self.y = y
                    self.visibility = visibility

            # Generate 33 mock landmarks
            mock_landmarks = [MockLandmark(0.5, 0.5) for _ in range(33)]

            # Test Bicep Curls
            curl = BicepsCurlDetector()
            res_curl = curl.process(mock_landmarks)
            self.assertIn("reps", res_curl)
            self.assertIn("form_score", res_curl)
            
            # Test Squat
            squat = SquatDetector()
            res_squat = squat.process(mock_landmarks)
            self.assertIn("reps", res_squat)
            self.assertIn("depth_status", res_squat)
            
            # Test Pushup
            pushup = PushUpDetector()
            res_pushup = pushup.process(mock_landmarks)
            self.assertIn("reps", res_pushup)
            self.assertIn("body_alignment", res_pushup)
            
            # Test Lunges
            lunge = LungesDetector()
            res_lunge = lunge.process(mock_landmarks)
            self.assertIn("reps", res_lunge)
            self.assertIn("balance_status", res_lunge)
            
            # Test Shoulder Press
            press = ShoulderPressDetector()
            res_press = press.process(mock_landmarks)
            self.assertIn("reps", res_press)
            self.assertIn("back_arch_status", res_press)

            print("[SUCCESS] All 5 exercise detectors processed mock landmarks successfully.")
        except Exception as e:
            self.fail(f"Detector processing validation failed: {e}")


if __name__ == "__main__":
    unittest.main()
