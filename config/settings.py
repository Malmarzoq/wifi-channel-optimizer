import os
from pathlib import Path

# رقم الإصدار
__version__ = "1.1.1"

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# قراءة ملف .env محلياً إن وُجد
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# بيانات الاتصال
ROUTER_IP = os.getenv("ROUTER_IP", "192.168.1.1")
USERNAME = os.getenv("ROUTER_USER", "admin")
PASSWORD = os.getenv("ROUTER_PASS", "YOUR_ROUTER_PASSWORD_HERE")
WIFI_IFACE = os.getenv("WIFI_IFACE", "eth6")
try:
    SSH_PORT = int(os.getenv("SSH_PORT", "22"))
except ValueError as exc:
    raise ValueError("SSH_PORT must be a number between 1 and 65535.") from exc
if not 1 <= SSH_PORT <= 65535:
    raise ValueError("SSH_PORT must be a number between 1 and 65535.")
# Optional path to a dedicated known_hosts file; system known_hosts is used when empty.
SSH_KNOWN_HOSTS = os.getenv("SSH_KNOWN_HOSTS", "")
NVRAM_RADIO = os.getenv("NVRAM_RADIO", "wl0")
DRY_RUN = os.getenv("DRY_RUN", "true").strip().lower() in {"1", "true", "yes", "on"}

# مسارات وسجلات
LOG_FILE = os.path.join(str(BASE_DIR), "wifi_agent.log")
STATE_FILE = Path(os.getenv("STATE_FILE", str(BASE_DIR / ".wifi_agent_state.json")))

# إعدادات التشغيل والحماية
CHECK_INTERVAL_SECONDS = 900      # الفاصل الزمني بين الفحوصات (15 دقيقة)
COOLDOWN_MINUTES = 60            # فترة التهدئة لمنع تكرار التبديل
VERIFICATION_DELAY = 60          # مهلة التحقق من الاستقرار بعد التبديل (بالثواني)
TX_RETRIES_ABORT_THRESHOLD = 500  # سقف تكرار محاولة إرسال الحزم غير المستلمة قبل إلغاء العملية

ALL_CHANNELS = list(range(1, 14))
OVERLAP_WEIGHTS = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.3, 4: 0.1}
