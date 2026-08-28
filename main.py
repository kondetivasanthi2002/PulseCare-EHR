"""
PulseCare EHR Main Application Launcher.
Root entrypoint to run the FastAPI application server.
"""

import sys
import os
import uvicorn

# Ensure current directory is on python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
