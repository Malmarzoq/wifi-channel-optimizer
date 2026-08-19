import unittest
from unittest.mock import Mock, patch

import tools.router_tools as router_module
from tools.router_tools import RouterTools


class RouterToolsTests(unittest.TestCase):
    @patch("tools.router_tools.paramiko.SSHClient")
    def test_ssh_connection_uses_configured_port(self, ssh_client_factory):
        ssh_client = ssh_client_factory.return_value
        stdout = Mock()
        stdout.read.return_value = b"ok"
        ssh_client.exec_command.return_value = (None, stdout, None)

        with patch.multiple(
            router_module,
            ROUTER_IP="192.0.2.1",
            USERNAME="test-user",
            PASSWORD="test-password",
            SSH_PORT=2222,
            SSH_KNOWN_HOSTS="",
        ):
            result = RouterTools.execute_ssh("echo ok")

        self.assertEqual(result, "ok")
        ssh_client.connect.assert_called_once_with(
            "192.0.2.1",
            port=2222,
            username="test-user",
            password="test-password",
            timeout=15,
        )


if __name__ == "__main__":
    unittest.main()
