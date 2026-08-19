import tempfile
import unittest
from pathlib import Path

import core.agent as agent_module
from core.agent import WifiAgentHarness
from memory.state_memory import AgentMemory
from tools.router_tools import RouterTools


def empty_stats():
    return {channel: {"rssis": [], "noises": [], "snrs": []} for channel in range(1, 14)}


class FakeRouter:
    def __init__(self, counters=(0, 0)):
        self.counters = iter(counters)
        self.applied_channels = []

    @staticmethod
    def get_current_channel():
        return 6

    @staticmethod
    def scan_spectrum():
        return empty_stats()

    @staticmethod
    def calculate_interference(_stats, channel):
        return {6: 100, 7: 10}.get(channel, 200)

    def get_interface_counters(self):
        return {"txretries": next(self.counters), "txerrors": 0}

    def apply_channel(self, channel):
        self.applied_channels.append(channel)
        return True


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.messages = []
        self.previous_dry_run = agent_module.DRY_RUN

    def tearDown(self):
        agent_module.DRY_RUN = self.previous_dry_run

    def test_dry_run_never_applies_a_channel_change(self):
        agent_module.DRY_RUN = True
        router = FakeRouter()
        agent = WifiAgentHarness(self.messages.append, memory=AgentMemory(), router_tools=router, sleep_fn=lambda _seconds: None)

        agent.evaluate_and_act()

        self.assertEqual(router.applied_channels, [])
        self.assertTrue(any("Dry run" in message for message in self.messages))

    def test_rollback_restores_the_previous_channel(self):
        agent_module.DRY_RUN = False
        router = FakeRouter(counters=(10, 600))
        agent = WifiAgentHarness(self.messages.append, memory=AgentMemory(), router_tools=router, sleep_fn=lambda _seconds: None)

        agent.evaluate_and_act()

        self.assertEqual(router.applied_channels, [7, 6])

    def test_cooldown_persists_across_restarts(self):
        with tempfile.TemporaryDirectory() as directory:
            state_file = Path(directory) / "agent-state.json"
            first_memory = AgentMemory(state_file=state_file)
            first_memory.record_decision(6, 7, "test", True)

            restored_memory = AgentMemory(state_file=state_file)
            active, _elapsed = restored_memory.is_cooldown_active(60)

        self.assertTrue(active)

    def test_interference_score_penalizes_an_overlapping_channel(self):
        stats = empty_stats()
        stats[6]["rssis"].append(-40)

        self.assertGreater(
            RouterTools.calculate_interference(stats, 6),
            RouterTools.calculate_interference(stats, 1),
        )
