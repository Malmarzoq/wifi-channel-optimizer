import time
from datetime import datetime
from config.settings import (
    ALL_CHANNELS, COOLDOWN_MINUTES, VERIFICATION_DELAY, TX_RETRIES_ABORT_THRESHOLD
)
from tools.router_tools import RouterTools
from memory.state_memory import AgentMemory

class WifiAgentHarness:
    def __init__(self, logger):
        self.log = logger
        self.memory = AgentMemory()

    def evaluate_and_act(self):
        current_ch = RouterTools.get_current_channel()
        if current_ch is None:
            self.log("⚠️ تعذر الاتصال بالراوتر أو قراءة القناة الحالية.")
            return

        stats = RouterTools.scan_spectrum()

        # 1. حساب مستوى التداخل لجميع القنوات من 1 إلى 13 بالكامل
        scores = {ch: RouterTools.calculate_interference(stats, ch) for ch in ALL_CHANNELS}
        
        # 2. تحديد القناة الأقل تداخلاً
        best_ch = min(scores, key=scores.get)

        score_curr = scores.get(current_ch, RouterTools.calculate_interference(stats, current_ch))
        score_best = scores[best_ch]

        # 3. صياغة التقرير الشامل لجميع القنوات (1 إلى 13)
        active_summary = [f"Ch{c}:{len(stats[c]['rssis'])}APs({int(scores[c])})" for c in ALL_CHANNELS]
        self.log(f"📡 القناة الحالية: {current_ch} (تداخل: {int(score_curr)}) | الأفضل: {best_ch} (تداخل: {int(score_best)})")
        self.log(f"📊 الرصد الشامل (1-13): {' | '.join(active_summary)}")

        if best_ch == current_ch:
            self.log(f"✨ القناة الحالية ({current_ch}) هي الأنسب. لا يلزم أي إجراء.")
            return

        is_cd, elapsed = self.memory.is_cooldown_active(COOLDOWN_MINUTES)
        if is_cd:
            self.log(f"⏳ فترة الأمان نشطة ({int(elapsed)}/{COOLDOWN_MINUTES} دقيقة). تم الإبقاء على Channel {current_ch}.")
            return

        # 4. فحص نسبة التحسن للتبديل (25% على الأقل)
        if score_curr > 0 and score_best < (score_curr * 0.75):
            improvement_pct = int((1 - score_best / score_curr) * 100)
            self.log(f"🎯 تقرر التبديل إلى Channel {best_ch} بنسبة تحسن متوقعة: {improvement_pct}%")

            counters_before = RouterTools.get_interface_counters()
            success = RouterTools.apply_channel(best_ch)

            if not success:
                self.log(f"❌ فشل تطبيق القناة الجديدة {best_ch}.")
                self.memory.record_decision(current_ch, best_ch, "Failed applying channel", False)
                return

            # حلقة التحقق اللاحق (Closed-Loop Verification)
            self.log(f"⏱️ فحص استقرار التردد الجديد لمدة {VERIFICATION_DELAY} ثانية...")
            time.sleep(VERIFICATION_DELAY)

            counters_after = RouterTools.get_interface_counters()
            delta_retries = counters_after["txretries"] - counters_before["txretries"]

            # التراجع التلقائي في حال رصد أخطاء إرسال مرتفعة
            if delta_retries > TX_RETRIES_ABORT_THRESHOLD:
                self.log(f"🚨 تدهور مفاجئ في الأداء (Retries: +{delta_retries})! جاري التراجع التلقائي (Rollback) إلى Channel {current_ch}...")
                RouterTools.apply_channel(current_ch)
                self.memory.record_decision(best_ch, current_ch, "Rollback: High Packet Retries", True, delta_retries)
                return

            self.log(f"✅ تم تأكيد استقرار التردد على Channel {best_ch} (Retries Delta: {delta_retries}).")
            self.memory.record_decision(current_ch, best_ch, f"Successful switch (improved {improvement_pct}%)", True, delta_retries)
        else:
            self.log(f"ℹ️ الفرق في التداخل غير جوهري بين {current_ch} و {best_ch}. البقاء على التردد الحالي أفضل للاستقرار.")
