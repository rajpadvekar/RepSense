from typing import Dict, List, Any, Optional
from database.repositories import WorkoutRepository, FeedbackRepository


class WorkoutService:
    """
    Manages exercise sessions logging, feedback registration, and workout analytics.
    """

    @staticmethod
    def log_workout(
        user_id: int,
        exercise_name: str,
        reps: int,
        avg_form_score: float,
        duration_seconds: int,
        feedback_list: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Logs a completed workout session to history. Saves associated form feedback corrections.
        """
        if reps < 0 or avg_form_score < 0 or duration_seconds < 0:
            return None

        workout_id = WorkoutRepository.create_workout(
            user_id=user_id,
            exercise_name=exercise_name,
            reps=reps,
            avg_form_score=avg_form_score,
            duration_seconds=duration_seconds
        )

        if workout_id and feedback_list:
            for item in feedback_list:
                FeedbackRepository.create_feedback(workout_id, item)

        return workout_id

    @staticmethod
    def get_workout_history(user_id: int) -> List[Dict[str, Any]]:
        """
        Returns list of all workouts for the user.
        """
        return WorkoutRepository.get_workouts_by_user(user_id)

    @staticmethod
    def get_dashboard_analytics(user_id: int) -> Dict[str, Any]:
        """
        Calculates and gathers all statistics required for the frontend Dashboard page.
        """
        return WorkoutRepository.get_workout_analytics(user_id)

    @staticmethod
    def get_workout_feedbacks(workout_id: int) -> List[str]:
        """
        Retrieves specific posture errors logged for a session.
        """
        return FeedbackRepository.get_feedback_by_workout(workout_id)
