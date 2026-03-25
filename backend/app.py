from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, field_validator

from .auth import (
    authenticate, create_jwt, verify_jwt,
    is_locked_out, record_failed_attempt, get_failed_count,
)
from .crypto import encrypt_message, decrypt_message, get_key
from .logs import generate_logs, get_all_logs, get_traffic_summary
from .detection import detect_suspicious, get_all_alerts

app = FastAPI(title="SecURe API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    return forwarded.split(",")[0] if forwarded else request.client.host


def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing token")
    payload = verify_jwt(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


# ── Schemas ───────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class MessageRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v


class LogRequest(BaseModel):
    count: int = 20

    @field_validator("count")
    @classmethod
    def valid_count(cls, v: int) -> int:
        if not (1 <= v <= 200):
            raise ValueError("count must be between 1 and 200")
        return v


# ── Auth routes ───────────────────────────────────────────────────────────────

@app.post("/login")
def login(data: LoginRequest, request: Request):
    ip = get_client_ip(request)

    if is_locked_out(ip):
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed attempts. Try again in 60 seconds."
        )

    if authenticate(data.username, data.password):
        token = create_jwt(data.username)
        return {"status": "success", "token": token, "username": data.username}

    record_failed_attempt(ip)
    attempts_left = max(0, 5 - get_failed_count(ip))
    raise HTTPException(
        status_code=401,
        detail=f"Invalid credentials. {attempts_left} attempt(s) remaining."
    )


# ── Log & detection routes ────────────────────────────────────────────────────

@app.post("/logs/generate")
def trigger_generate(data: LogRequest, _=Depends(require_auth)):
    """Generate new simulated traffic logs and run detection on them."""
    new_logs = generate_logs(count=data.count)
    new_alerts = detect_suspicious(new_logs)
    return {
        "generated": len(new_logs),
        "new_alerts": len(new_alerts),
        "alerts": new_alerts,
    }


@app.get("/logs")
def fetch_logs(_=Depends(require_auth)):
    """Return all persisted logs, most recent first."""
    return {"logs": get_all_logs()}


@app.get("/alerts")
def fetch_alerts(_=Depends(require_auth)):
    """Return all generated security alerts."""
    return {"alerts": get_all_alerts()}


@app.get("/dashboard")
def dashboard(_=Depends(require_auth)):
    """Aggregated stats for the overview chart."""
    return get_traffic_summary()


# ── Encryption routes ─────────────────────────────────────────────────────────

@app.get("/key")
def key(_=Depends(require_auth)):
    return {"key": get_key()}


@app.post("/encrypt")
def encrypt(data: MessageRequest, _=Depends(require_auth)):
    return {"encrypted": encrypt_message(data.message)}


@app.post("/decrypt")
def decrypt(data: MessageRequest, _=Depends(require_auth)):
    try:
        return {"decrypted": decrypt_message(data.message)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}