import bcrypt
from datetime import datetime, timedelta
from collections import defaultdict
import jwt
import os

# In production, load from .env
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_in_prod")
JWT_EXPIRY_MINUTES = 60

# --- In-memory user store (replace with DB in production) ---
# Passwords are bcrypt hashed. This simulates "admin" / "password123"
_raw_users = {
    "admin": "password123",
    "analyst": "secure456",
}

USERS = {
    username: bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    for username, password in _raw_users.items()
}

# --- Failed login tracker (persistent across requests) ---
failed_attempts: dict[str, list[datetime]] = defaultdict(list)
LOCKOUT_THRESHOLD = 5
LOCKOUT_WINDOW_SECONDS = 60


def _clean_old_attempts(ip: str):
    """Remove attempts outside the tracking window."""
    cutoff = datetime.utcnow() - timedelta(seconds=LOCKOUT_WINDOW_SECONDS)
    failed_attempts[ip] = [t for t in failed_attempts[ip] if t > cutoff]


def is_locked_out(ip: str) -> bool:
    _clean_old_attempts(ip)
    return len(failed_attempts[ip]) >= LOCKOUT_THRESHOLD


def record_failed_attempt(ip: str):
    failed_attempts[ip].append(datetime.utcnow())


def get_failed_count(ip: str) -> int:
    _clean_old_attempts(ip)
    return len(failed_attempts[ip])


def authenticate(username: str, password: str) -> bool:
    hashed = USERS.get(username)
    if not hashed:
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_jwt(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None