import random
from datetime import datetime
from collections import deque

# Protocols and ports to simulate realistic traffic
PROTOCOLS = ["TCP", "UDP", "HTTP", "HTTPS", "DNS", "FTP", "SSH"]
PORTS = [22, 53, 80, 443, 8080, 3306, 21, 25]
STATUSES = ["OK", "OK", "OK", "FAILED_LOGIN", "BLOCKED", "OK", "TIMEOUT"]

# Simulated IPs — a mix of internal and external
INTERNAL_IPS = [f"192.168.1.{i}" for i in range(1, 11)]
EXTERNAL_IPS = ["45.33.32.156", "198.51.100.7", "203.0.113.42", "185.220.101.5"]
ALL_IPS = INTERNAL_IPS + EXTERNAL_IPS

# Persistent in-memory log store (last 500 entries)
log_store: deque = deque(maxlen=500)


def _make_log() -> dict:
    src_ip = random.choice(ALL_IPS)
    dst_ip = random.choice(INTERNAL_IPS)
    return {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": random.choice(PROTOCOLS),
        "port": random.choice(PORTS),
        "bytes": random.randint(64, 9000),
        "status": random.choice(STATUSES),
    }


def generate_logs(count: int = 20) -> list[dict]:
    """Generate `count` new simulated log entries and persist them."""
    new_logs = [_make_log() for _ in range(count)]
    log_store.extend(new_logs)
    return new_logs


def get_all_logs() -> list[dict]:
    """Return all persisted logs (most recent first)."""
    return list(reversed(log_store))


def get_traffic_summary() -> dict:
    """Aggregate stats for the dashboard chart."""
    logs = list(log_store)
    protocol_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    total_bytes = 0

    for log in logs:
        protocol_counts[log["protocol"]] = protocol_counts.get(log["protocol"], 0) + 1
        status_counts[log["status"]] = status_counts.get(log["status"], 0) + 1
        total_bytes += log["bytes"]

    return {
        "total_logs": len(logs),
        "total_bytes": total_bytes,
        "protocol_counts": protocol_counts,
        "status_counts": status_counts,
    }