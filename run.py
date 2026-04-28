import subprocess
import time
import sys
import os

def run_bot():
    print("[Bot] Starting Telegram Service...")
    return subprocess.Popen([sys.executable, "app.py"])

def run_api():
    print("[API] Starting Backend Services (http://localhost:8000)...")
    return subprocess.Popen([sys.executable, "api/main.py"])

def run_react():
    print("[UI] Starting React Dashboard (http://localhost:5174)...")
    # Using shell=True for npm on Windows
    return subprocess.Popen(["npm", "run", "dev"], cwd="web-dashboard", shell=True)

if __name__ == "__main__":
    processes = {
        "bot": run_bot(),
        "api": run_api(),
        "ui": run_react()
    }
    
    try:
        while True:
            time.sleep(2)
            for name, proc in processes.items():
                if proc.poll() is not None:
                    print(f"WARN: {name.upper()} process died. Restarting...")
                    if name == "bot": processes[name] = run_bot()
                    if name == "api": processes[name] = run_api()
                    if name == "ui": processes[name] = run_react()
    except KeyboardInterrupt:
        print("\nShutting down Eco-Track Ecosystem...")
        for proc in processes.values():
            proc.terminate()
