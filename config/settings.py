import os
from pathlib import Path

# رقم الإصدار
__version__ = "1.0.0"

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

# مسارات وسجلات
LOG_FILE = os.path.join(str(BASE_DIR), "wifi_agent.log")

# محددات التشغيل والأمان
CHECK_INTERVAL_SECONDS = 900  # دورة الفحص كل 15 دقيقة
COOLDOWN_MINUTES = 60         # فترة أمان لمنع التبديل المتكرر
VERIFICATION_DELAY = 60       # زمن مراقبة الاستقرار بعد التبديل (بالثواني)
TX_RETRIES_ABORT_THRESHOLD = 500  # عتبة التراجع في حال حدوث أخطاء إرسال حادة

ALL_CHANNELS = list(range(1, 14))
OVERLAP_WEIGHTS = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.3, 4: 0.1}
