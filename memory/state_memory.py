from datetime import datetime

class AgentMemory:
    def __init__(self, history_limit=20):
        self.history_limit = history_limit
        self.history = []
        self.last_switch_time = datetime.min

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

    def is_cooldown_active(self, cooldown_minutes):
        elapsed = (datetime.now() - self.last_switch_time).total_seconds() / 60.0
        return elapsed < cooldown_minutes, elapsed
