# SecURe: Network Security Monitoring Dashboard

## Overview
SecURe is a web-based system that monitors network activity and detects suspicious behavior such as unauthorized access attempts and abnormal traffic patterns. It combines logging, detection, authentication, and encryption within a single dashboard.

---

## Features
- Simulated network traffic logs  
- Detection of:
  - Failed login attempts (brute force)
  - Malicious IPs
  - Port scanning activity
  - Traffic spikes  
- User authentication using bcrypt and JWT  
- Encryption and decryption using Fernet  
- Dashboard with basic visualizations and alerts  

---

## Project Structure
```

network-security-dashboard/
├── backend/
├── frontend/
├── requirements.txt
└── README.md

````

---

## Setup

### Create virtual environment
```bash
py -3.11 -m venv venv
````

### Activate environment

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run backend

```bash
python -m uvicorn backend.app:app --reload --reload-dir backend
```

### Run frontend

Open:

```
frontend/login.html
```

---

## Notes

* Uses simulated data (not real network traffic)
* Intended for educational purposes


