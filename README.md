# SCEMAS – Smart City Environmental Monitoring & Alert System (Frontend)

SCEMAS (Smart City Environmental Monitoring & Alert System) is a platform designed to monitor environmental data, generate alerts, and provide actionable insights for smart city infrastructure.

This repository contains the frontend application, providing an intuitive user interface for interacting with the system.

## Prerequisites

Make sure you have the following installed:

- Python (3.9+ recommended)
- pip (Python package manager)
- Virtual environment support (venv)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/BilalM04/SCEMAS-frontend.git
cd SCEMAS-frontend
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure secrets

Create a `secrets.toml` file inside the `.streamlit` directory and add the following configuration:

```toml
FIREBASE_API_KEY = ""
FIREBASE_AUTH_DOMAIN = ""
FIREBASE_PROJECT_ID = ""
FIREBASE_STORAGE_BUCKET = ""
FIREBASE_MESSAGING_SENDER_ID = ""
FIREBASE_APP_ID = ""
BACKEND_BASE_URL = ""
```

> ⚠️ Keep this file private and do not commit it to version control.

### 5. Run the application

```bash
streamlit run app.py
```
