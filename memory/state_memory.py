import json
from datetime import datetime
from pathlib import Path

class AgentMemory:
    def __init__(self, history_limit=20, state_file=None):
        self.history_limit = history_limit
        self.history = []
        self.state_file = Path(state_file) if state_file else None
        self.last_switch_time = datetime.min
        self._load_state()

    def record_decision(self, from_ch, to_ch, reason, success, delta_retries=0):
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from_channel": from_ch,
            "to_channel": to_ch,
            "reason": reason,
            "success": success,
            "delta_retries": delta_retries
        }
        self.history.append(record)
        if len(self.history) > self.history_limit:
            self.history.pop(0)

        if success:
            self.last_switch_time = datetime.now()
            self._save_state()

    def is_cooldown_active(self, cooldown_minutes):
        elapsed = (datetime.now() - self.last_switch_time).total_seconds() / 60.0
        return elapsed < cooldown_minutes, elapsed

    def _load_state(self):
        if not self.state_file:
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
            timestamp = data.get("last_switch_time")
            if timestamp:
                self.last_switch_time = datetime.fromisoformat(timestamp)
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return

    def _save_state(self):
        if not self.state_file:
            return

        payload = {"last_switch_time": self.last_switch_time.isoformat()}
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file = self.state_file.with_suffix(f"{self.state_file.suffix}.tmp")
            with temp_file.open("w", encoding="utf-8") as file:
                json.dump(payload, file)
            temp_file.replace(self.state_file)
        except OSError:
            return
