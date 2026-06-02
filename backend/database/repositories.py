from typing import Dict, List, Optional, Any
from database.db_manager import DBManager
import sqlite3


class UserRepository:
    """
    Handles user management database operations.
    """

    @staticmethod
    def create_user(username: str, password_hash: str, email: str) -> Optional[int]:
        """Creates a new user record. Returns the new user's ID or None on failure."""
        try:
            with DBManager.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                    (username, password_hash, email)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Username or Email already exists
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a user by their ID."""
        with DBManager.get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user by their username."""
        with DBManager.get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_profile(user_id: int, height: float, weight: float, daily_rep_goal: int) -> bool:
        """Updates profile metrics for the user."""
        try:
            with DBManager.get_connection() as conn:
                conn.execute(
                    "UPDATE users SET height = ?, weight = ?, daily_rep_goal = ? WHERE id = ?",
                    (height, weight, daily_rep_goal, user_id)
                )
                conn.commit()
                return True
        except Exception:
            return False


class WorkoutRepository:
    """
    Handles logging and querying workout sessions.
    """

    @staticmethod
    def create_workout(user_id: int, exercise_name: str, reps: int, avg_form_score: float, duration_seconds: int) -> Optional[int]:
        """Logs a completed workout session and returns the log ID."""
        with DBManager.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO workouts (user_id, exercise_name, reps, avg_form_score, duration_seconds) VALUES (?, ?, ?, ?, ?)",
                (user_id, exercise_name, reps, avg_form_score, duration_seconds)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_workouts_by_user(user_id: int) -> List[Dict[str, Any]]:
        """Retrieves the history of all workouts for a user, ordered by date descending."""
        with DBManager.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM workouts WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def get_workout_analytics(user_id: int) -> Dict[str, Any]:
        """Generates summary statistics for a user's workout dashboard."""
        with DBManager.get_connection() as conn:
            # Overall statistics
            totals = conn.execute(
                """
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(reps) as total_reps,
                    AVG(avg_form_score) as overall_avg_score,
                    SUM(duration_seconds) as total_duration_seconds
                FROM workouts 
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchone()

            # Exercise distribution breakdown
            breakdown = conn.execute(
                """
                SELECT 
                    exercise_name,
                    COUNT(*) as sessions,
                    SUM(reps) as reps,
                    AVG(avg_form_score) as avg_score
                FROM workouts 
                WHERE user_id = ? 
                GROUP BY exercise_name
                """,
                (user_id,)
            ).fetchall()

            # Goal achievement: Sum reps done today
            today_reps = conn.execute(
                """
                SELECT SUM(reps) as reps 
                FROM workouts 
                WHERE user_id = ? AND date(created_at) = date('now')
                """,
                (user_id,)
            ).fetchone()

            return {
                "total_sessions": totals["total_sessions"] or 0,
                "total_reps": totals["total_reps"] or 0,
                "overall_avg_score": round(totals["overall_avg_score"] or 0.0, 1),
                "total_duration_minutes": round((totals["total_duration_seconds"] or 0) / 60.0, 1),
                "exercise_breakdown": [dict(b) for b in breakdown],
                "today_reps": today_reps["reps"] or 0
            }


class FeedbackRepository:
    """
    Logs specific AI coaching feedback snippets generated during workouts.
    """

    @staticmethod
    def create_feedback(workout_id: int, feedback_text: str) -> None:
        """Stores a form correction or general feedback item for reference."""
        with DBManager.get_connection() as conn:
            conn.execute(
                "INSERT INTO feedback_history (workout_id, feedback_text) VALUES (?, ?)",
                (workout_id, feedback_text)
            )
            conn.commit()

    @staticmethod
    def get_feedback_by_workout(workout_id: int) -> List[str]:
        """Retrieves all feedback logs generated during a particular workout session."""
        with DBManager.get_connection() as conn:
            rows = conn.execute(
                "SELECT feedback_text FROM feedback_history WHERE workout_id = ? ORDER BY timestamp ASC",
                (workout_id,)
            ).fetchall()
            return [r["feedback_text"] for r in rows]
