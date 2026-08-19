import re
import time
import paramiko
from config.settings import (
    ROUTER_IP, USERNAME, PASSWORD, WIFI_IFACE, SSH_KNOWN_HOSTS, ALL_CHANNELS, OVERLAP_WEIGHTS
)

class RouterTools:
    """أدوات التحكم والاستعلام المباشر من الراوتر"""

    @staticmethod
    def execute_ssh(command, timeout=15):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        if SSH_KNOWN_HOSTS:
            ssh.load_host_keys(SSH_KNOWN_HOSTS)
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            ssh.connect(ROUTER_IP, username=USERNAME, password=PASSWORD, timeout=timeout)
            _, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            ssh.close()
            return output
        except Exception:
            return None

    @classmethod
    def get_current_channel(cls):
        out = cls.execute_ssh(f"wl -i {WIFI_IFACE} channel")
        if out:
            match = re.search(r"channel\s+(\d+)", out, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    @classmethod
    def scan_spectrum(cls):
        cls.execute_ssh(f"wl -i {WIFI_IFACE} scan")
        time.sleep(4.0)
        scan_data = cls.execute_ssh(f"wl -i {WIFI_IFACE} scanresults")

        stats = {ch: {"rssis": [], "noises": [], "snrs": []} for ch in ALL_CHANNELS}
        if not scan_data:
            return stats

        blocks = re.split(r"(?:SSID:|BSSID:)", scan_data)
        for block in blocks[1:]:
            ch_m = re.search(r"Channel:\s*(\d+)", block, re.IGNORECASE)
            rssi_m = re.search(r"RSSI:\s*(-?\d+)\s*dBm", block, re.IGNORECASE)
            noise_m = re.search(r"noise:\s*(-?\d+)\s*dBm", block, re.IGNORECASE)
            snr_m = re.search(r"SNR:\s*(\d+)\s*dB", block, re.IGNORECASE)

            if ch_m and rssi_m:
                ch = int(ch_m.group(1))
                rssi = int(rssi_m.group(1))
                if ch in stats:
                    stats[ch]["rssis"].append(rssi)
                    if noise_m:
                        stats[ch]["noises"].append(int(noise_m.group(1)))
                    if snr_m:
                        stats[ch]["snrs"].append(int(snr_m.group(1)))
        return stats

    @classmethod
    def get_interface_counters(cls):
        """فحص عدادات أخطاء الإرسال للتحقق من جودة القناة"""
        out = cls.execute_ssh(f"wl -i {WIFI_IFACE} counters")
        counters = {"txretries": 0, "txerrors": 0}
        if out:
            tx_retry = re.search(r"txretrie\w*\s+(\d+)", out, re.IGNORECASE)
            tx_err = re.search(r"txerror\w*\s+(\d+)", out, re.IGNORECASE)
            if tx_retry:
                counters["txretries"] = int(tx_retry.group(1))
            if tx_err:
                counters["txerrors"] = int(tx_err.group(1))
        return counters

    @classmethod
    def apply_channel(cls, channel):
        # محاولة التبديل المباشر
        cmd_direct = f"wl -i {WIFI_IFACE} down && wl -i {WIFI_IFACE} chanspec {channel}/20 && wl -i {WIFI_IFACE} up"
        cls.execute_ssh(cmd_direct)
        time.sleep(3)

        if cls.get_current_channel() == channel:
            cls.execute_ssh(f"nvram set wl0_channel={channel} && nvram set wl0_chanspec={channel} && nvram commit")
            return True

        # المحاولة الاحتياطية
        cmd_service = f"nvram set wl0_channel={channel} && nvram set wl0_chanspec={channel} && nvram commit && service restart_wireless"
        cls.execute_ssh(cmd_service)
        time.sleep(8)
        return cls.get_current_channel() == channel

    @staticmethod
    def calculate_interference(stats, target_ch):
        total_score = 0.0
        for ch in ALL_CHANNELS:
            delta = abs(target_ch - ch)
            w = OVERLAP_WEIGHTS.get(delta, 0.0)
            if w > 0:
                c_rssis = stats[ch]["rssis"]
                count = len(c_rssis)
                if count > 0:
                    max_rssi = max(c_rssis)
                    linear_power = 10 ** ((max_rssi + 100) / 10)
                    total_score += w * count * linear_power
        return total_score
