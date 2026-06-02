import hashlib
import uuid
from typing import Optional, Dict, Any
from database.repositories import UserRepository


class AuthService:
    """
    Business service to manage user registration, authentication, and profile updates.
    """

    @staticmethod
    def _hash_password(password: str, salt: Optional[str] = None) -> str:
        """
        Hashes the password with SHA-256 and salt.
        Returns the formatted string: "salt$hash".
        """
        if not salt:
            salt = uuid.uuid4().hex
        
        # Hash computation
        hash_obj = hashlib.sha256((salt + password).encode())
        pwd_hash = hash_obj.hexdigest()
        
        return f"{salt}${pwd_hash}"

    @classmethod
    def register_user(cls, username: str, password: str, email: str) -> Optional[int]:
        """
        Registers a new user. Handles password hashing.
        Returns the created user's ID, or None if the username/email is taken.
        """
        if not username or not password or not email:
            return None
            
        password_hash = cls._hash_password(password)
        return UserRepository.create_user(
            username=username.strip(),
            password_hash=password_hash,
            email=email.strip().lower()
        )

    @classmethod
    def login_user(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Validates login credentials.
        Returns the user record (excluding password hash) on success, or None on failure.
        """
        if not username or not password:
            return None

        user = UserRepository.get_user_by_username(username.strip())
        if not user:
            return None

        # Verify hashed password
        db_hash_str = user["password_hash"]
        try:
            salt, db_hash = db_hash_str.split("$")
            computed_hash_str = cls._hash_password(password, salt)
            _, computed_hash = computed_hash_str.split("$")
            
            if db_hash == computed_hash:
                # Return user record without the password hash
                user_copy = dict(user)
                user_copy.pop("password_hash", None)
                return user_copy
        except ValueError:
            # Bad hash format stored in DB
            pass

        return None

    @staticmethod
    def get_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves user profile information."""
        return UserRepository.get_user_by_id(user_id)

    @staticmethod
    def update_profile(user_id: int, height: float, weight: float, daily_rep_goal: int) -> bool:
        """Updates user profile variables (height, weight, daily goals)."""
        if height <= 0 or weight <= 0 or daily_rep_goal < 0:
            return False
        return UserRepository.update_profile(user_id, height, weight, daily_rep_goal)
