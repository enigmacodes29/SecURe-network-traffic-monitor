import os
from cryptography.fernet import Fernet

# Load key from environment, or generate once and persist it.
# In production: store KEY in a .env file and NEVER regenerate.
_KEY_FILE = "fernet.key"


def _load_or_create_key() -> bytes:
    """Load key from disk so it survives server restarts."""
    env_key = os.getenv("FERNET_KEY")
    if env_key:
        return env_key.encode()

    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "rb") as f:
            return f.read()

    # First-time setup: generate and save
    key = Fernet.generate_key()
    with open(_KEY_FILE, "wb") as f:
        f.write(key)
    return key


_key = _load_or_create_key()
_cipher = Fernet(_key)


def get_key() -> str:
    return _key.decode()


def encrypt_message(message: str) -> str:
    return _cipher.encrypt(message.encode()).decode()


def decrypt_message(token: str) -> str:
    try:
        return _cipher.decrypt(token.encode()).decode()
    except Exception:
        raise ValueError("Decryption failed — invalid token or wrong key.")