"""異なるCPU戦略間のRemote対局をテストします。"""

import socket
import time
import unittest

import pygame

from src.othello.config import NetworkConfig
from src.othello.core.game_enums import CpuStrategyKind, GameStatus
from src.othello.modes.client_mode import ClientMode
from src.othello.modes.server_mode import ServerMode
from src.othello.players.cpu_player import CpuPlayer


def _find_available_port() -> int:
    """ローカルTCPで利用可能なポート番号を取得します。"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class RemoteCpuMatchTest(unittest.TestCase):
    """CPU戦略名を通信せずRemote CPU対局が完走することを確認します。"""

    @classmethod
    def setUpClass(cls) -> None:
        """pygameのフォント機能を初期化します。"""
        pygame.font.init()

    @classmethod
    def tearDownClass(cls) -> None:
        """pygameのフォント機能を終了します。"""
        pygame.font.quit()

    def test_remote_cpu_match_finishes_with_existing_protocol(self) -> None:
        """Weighted Board対RandomのRemote対局を完走させます。"""
        config = NetworkConfig("127.0.0.1", _find_available_port())
        surface = pygame.Surface((640, 640))
        server = ServerMode(
            surface,
            config,
            use_cpu=True,
            cpu_strategy_kind=CpuStrategyKind.WEIGHTED_BOARD,
        )
        client = ClientMode(
            surface,
            config,
            use_cpu=True,
            cpu_strategy_kind=CpuStrategyKind.RANDOM,
        )

        try:
            self.assertIsInstance(server.local_player, CpuPlayer)
            self.assertIsInstance(client.local_player, CpuPlayer)
            server.local_player.think_seconds = 0
            client.local_player.think_seconds = 0
            deadline = time.monotonic() + 10

            while time.monotonic() < deadline:
                server.update()
                client.update()

                if (
                    server.engine.status is GameStatus.GAME_OVER
                    and client.engine.status is GameStatus.GAME_OVER
                ):
                    break

                time.sleep(0.001)

            self.assertIs(server.engine.status, GameStatus.GAME_OVER)
            self.assertIs(client.engine.status, GameStatus.GAME_OVER)
            self.assertEqual(server.board.cells, client.board.cells)
        finally:
            client.close()
            server.close()


if __name__ == "__main__":
    unittest.main()
