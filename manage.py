"""
PulseCare Management Utility.
Provides CLI commands to run server, seed database, or execute tests.
"""

import sys
import os
import argparse
import uvicorn
import pytest

def main():
    parser = argparse.ArgumentParser(description="PulseCare EHR Management CLI")
    parser.add_argument("command", choices=["runserver", "seed", "test"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "runserver":
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    elif args.command == "seed":
        import asyncio
        from scripts.seed import seed_healthcare_database
        asyncio.run(seed_healthcare_database())
    elif args.command == "test":
        sys.exit(pytest.main(["tests/", "-v"]))

if __name__ == "__main__":
    main()
