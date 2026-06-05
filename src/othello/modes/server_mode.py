"""TCPサーバとして動作する白側プレイヤーのモードを定義します。"""

from queue import Empty

import pygame
from loguru import logger

from src.othello.config import NetworkConfig
from src.othello.constants import SERVER_COLOR
from src.othello.core.game_enums import Cell
from src.othello.modes.remote_mode_base import RemoteModeBase
from src.othello.network.protocol import OthelloCommand, OthelloMessage
from src.othello.network.server import OthelloTcpServer
from src.othello.players.cpu_player import CpuPlayer
from src.othello.players.local_human_player import LocalHumanPlayer
from src.othello.players.player_controller import PlayerController


class ServerMode(RemoteModeBase):
    """TCPサーバとして動作する白側プレイヤーのモードです。"""

    def __init__(
        self,
        surface: pygame.Surface,
        network_config: NetworkConfig,
        use_cpu: bool = False,
    ) -> None:
        """サーバモードを初期化します。

        Args:
            surface: 描画先Surface。
            network_config: TCP通信設定。
            use_cpu: サーバ側白プレイヤーをCPUにする場合はTrue。
        """
        super().__init__(
            surface=surface,
            local_player=self._create_local_player(use_cpu),
            remote_color=Cell.BLACK,
        )
        self.server: OthelloTcpServer = OthelloTcpServer(network_config)
        self.server.start()
        logger.info("Server / Whiteを開始しました: use_cpu={}", use_cpu)

    def close(self) -> None:
        """サーバモードを終了します。

        Returns:
            None.
        """
        self.server.close()
        logger.info("ServerModeを終了しました。")

    def _process_network_messages(self) -> None:
        """TCPサーバの受信Queueを処理します。

        Returns:
            None.
        """
        while True:
            try:
                message: OthelloMessage = self.server.incoming_queue.get_nowait()
            except Empty:
                return

            match message.command:
                case OthelloCommand.START:
                    self.game_ready = True
                    logger.info("START受信によりゲーム可能状態になりました。")

                case OthelloCommand.HIT:
                    logger.info("HIT受信: message={}", message)
                    if not self.game_ready:
                        logger.warning("ゲーム準備前のHITを破棄しました: {}", message)
                        continue

                    self._apply_remote_hit(message)

                case OthelloCommand.PASS:
                    logger.info("PASS受信: message={}", message)
                    if not self.game_ready:
                        logger.warning("ゲーム準備前のPASSを破棄しました: {}", message)
                        continue

                    self._apply_remote_pass()

                case OthelloCommand.OK:
                    logger.info("OK受信: message={}", message)

    def _send_message(self, message: OthelloMessage) -> None:
        """Clientへネットワークメッセージを送信します。

        Args:
            message: 送信する通信メッセージ。

        Returns:
            None.
        """
        self.server.send_message(message)

    def _create_local_player(self, use_cpu: bool) -> PlayerController:
        """サーバ側の白プレイヤーを作成します。

        Args:
            use_cpu: CPUプレイヤーを使う場合はTrue。

        Returns:
            サーバ側白プレイヤー。
        """
        if use_cpu:
            return CpuPlayer(SERVER_COLOR)

        return LocalHumanPlayer(SERVER_COLOR)
