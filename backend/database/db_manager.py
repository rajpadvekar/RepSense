import os
import sqlite3
from sqlite3 import Connection

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repsense.db")


class DBManager:
    """
    Manages SQLite database connections and table initialization.
    """

    @staticmethod
    def get_connection() -> Connection:
        """
        Creates and returns a connection to the database.
        Returns rows as sqlite3.Row objects for field-name accessibility.
        """
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @classmethod
    def init_db(cls) -> None:
        """
        Initializes the database schema. Creates tables if they do not exist.
        """
        # Ensure database directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        with cls.get_connection() as conn:
            # 1. Users Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    height REAL,
                    weight REAL,
                    daily_rep_goal INTEGER DEFAULT 50,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Workouts Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    exercise_name TEXT NOT NULL,
                    reps INTEGER NOT NULL,
                    avg_form_score REAL NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)

            # 3. Feedback History Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workout_id INTEGER NOT NULL,
                    feedback_text TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(workout_id) REFERENCES workouts(id) ON DELETE CASCADE
                );
            """)

            conn.commit()
        print(f"Database successfully initialized at {DB_PATH}")


if __name__ == "__main__":
    DBManager.init_db()
