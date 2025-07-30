import subprocess
import sys
import time
import os
from pathlib import Path
from dotenv import load_dotenv
import confready 


CONFREADY_DIR = Path(confready.__file__).parent
FRONTEND_DIR = CONFREADY_DIR / "frontend"
BACKEND_DIR = CONFREADY_DIR / "server"
ENV_PATH = CONFREADY_DIR / "server"/ ".env"


REQUIRED_KEYS = ["TOGETHER_API_KEY", "OPENAI_API_KEY"]

def ensure_env_keys():
    env_vars = {}

    # Prompt for all keys
    for key in REQUIRED_KEYS:
        value = input(f"Enter value for {key}: ").strip()
        env_vars[key] = value

    # Load existing .env lines (if any)
    existing_lines = []
    if ENV_PATH.exists():
        with open(ENV_PATH, "r") as f:
            existing_lines = f.readlines()

    # Prepare updated lines
    new_lines = []
    seen_keys = set()

    for line in existing_lines:
        line_stripped = line.strip()
        if "=" not in line_stripped or line_stripped.startswith("#"):
            new_lines.append(line)
            continue

        key, _ = line_stripped.split("=", 1)
        if key in env_vars:
            new_lines.append(f"{key}={env_vars[key]}\n")
            seen_keys.add(key)
        else:
            new_lines.append(line)

    # Add any new keys that weren't already present
    for key, value in env_vars.items():
        if key not in seen_keys:
            new_lines.append(f"{key}={value}\n")

    # Write updated .env
    with open(ENV_PATH, "w") as f:
        f.writelines(new_lines)

    print(f"API keys saved to .env at {ENV_PATH}")
    load_dotenv(dotenv_path=ENV_PATH, override=True)


def run_backend():
    print("Starting Flask backend...")

    load_dotenv(dotenv_path=ENV_PATH, override=True)
    env = os.environ.copy()
    env["FLASK_APP"] = "app.py"
    
    return subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--port=8080"],
        cwd=str(BACKEND_DIR),
        env=env
    )


def run_frontend():
    if not (FRONTEND_DIR / "package.json").exists():
        print("Error: Frontend package.json not found.")
        sys.exit(1)

    print("Installing frontend dependencies (if needed)...")
    subprocess.run(["npm", "install"], cwd=str(FRONTEND_DIR), check=True)

    print("Starting React frontend...")
    return subprocess.Popen(["npm", "start"], cwd=str(FRONTEND_DIR))


def main():
    ensure_env_keys()

    backend_process = run_backend()
    time.sleep(3)  

    frontend_process = run_frontend()

    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Bye!")

if __name__ == "__main__":
    main()
