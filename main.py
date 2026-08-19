import time
from datetime import datetime
from config.settings import CHECK_INTERVAL_SECONDS, LOG_FILE, __version__
from core.agent import WifiAgentHarness

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def main():
    log_message(f"🚀 بدء تشغيل Wi-Fi Autonomous Agent Harness v{__version__}...")
    agent = WifiAgentHarness(logger=log_message)

    while True:
        try:
            agent.evaluate_and_act()
        except Exception as e:
            log_message(f"❌ استثناء غير متوقع في الدورة: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
