import subprocess
import time
import sys

def run_bot():
    print("🚀 Starting Telegram Bot...")
    return subprocess.Popen([sys.executable, "app.py"])

def run_dashboard():
    print("📊 Starting Admin Dashboard (http://localhost:8000)...")
    return subprocess.Popen([sys.executable, "dashboard/main.py"])

if __name__ == "__main__":
    bot_proc = run_bot()
    dash_proc = run_dashboard()
    
    try:
        while True:
            time.sleep(1)
            if bot_proc.poll() is not None:
                print("⚠️ Bot process died. Restarting...")
                bot_proc = run_bot()
            if dash_proc.poll() is not None:
                print("⚠️ Dashboard process died. Restarting...")
                dash_proc = run_dashboard()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        bot_proc.terminate()
        dash_proc.terminate()
