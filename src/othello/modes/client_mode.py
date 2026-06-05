"""TCPクライアントとして動作する黒側プレイヤーのモードを定義します。"""

from queue import Empty

import pygame
from loguru import logger

from src.othello.config import NetworkConfig
from src.othello.constants import CLIENT_COLOR
from src.othello.core.game_enums import Cell
from src.othello.modes.remote_mode_base import RemoteModeBase
from src.othello.network.client import OthelloTcpClient
from src.othello.network.protocol import OthelloCommand, OthelloMessage
from src.othello.players.cpu_player import CpuPlayer
from src.othello.players.local_human_player import LocalHumanPlayer
from src.othello.players.player_controller import PlayerController


class ClientMode(RemoteModeBase):
    """TCPクライアントとして動作する黒側プレイヤーのモードです。"""

    def __init__(
        self,
        surface: pygame.Surface,
        network_config: NetworkConfig,
        use_cpu: bool = False,
    ) -> None:
        """クライアントモードを初期化します。

        Args:
            surface: 描画先Surface。
            network_config: TCP通信設定。
            use_cpu: クライアント側黒プレイヤーをCPUにする場合はTrue。
        """
        super().__init__(
            surface=surface,
            local_player=self._create_local_player(use_cpu),
            remote_color=Cell.WHITE,
        )
        self.client: OthelloTcpClient = OthelloTcpClient(network_config)
        self.client.start()
        logger.info("Client / Blackを開始しました: use_cpu={}", use_cpu)

    def close(self) -> None:
        """クライアントモードを終了します。

        Returns:
            None.
        """
        self.client.close()
        logger.info("ClientModeを終了しました。")

    def _process_network_messages(self) -> None:
        """TCPクライアントの受信Queueを処理します。

        Returns:
            None.
        """
        while True:
            try:
                message: OthelloMessage = self.client.incoming_queue.get_nowait()
            except Empty:
                return

            match message.command:
                case OthelloCommand.OK:
                    self.game_ready = True
                    logger.info("OK受信によりゲーム可能状態になりました。")

                case OthelloCommand.HIT:
                    logger.info("HIT受信: message={}", message)
                    if not self._is_network_ready():
                        logger.warning("ゲーム準備前のHITを破棄しました: {}", message)
                        continue

                    self._apply_remote_hit(message)

                case OthelloCommand.PASS:
                    logger.info("PASS受信: message={}", message)
                    if not self._is_network_ready():
                        logger.warning("ゲーム準備前のPASSを破棄しました: {}", message)
                        continue

                    self._apply_remote_pass()

                case OthelloCommand.START:
                    logger.info("START受信: message={}", message)

    def _is_network_ready(self) -> bool:
        """対局入力を始められる通信状態かを返します。

        Returns:
            対局入力を始められる通信状態であればTrue。
        """
        return self.game_ready or self.client.is_connected

    def _log_input_block_reason(self) -> None:
        """ローカルクリックが拒否された理由をログ出力します。

        Returns:
            None.
        """
        if not self._is_network_ready():
            logger.info(
                "通信準備前のクリックを無視しました: connected={}, ok_received={}",
                self.client.is_connected,
                self.game_ready,
            )
            return

        super()._log_input_block_reason()

    def _send_message(self, message: OthelloMessage) -> None:
        """Serverへネットワークメッセージを送信します。

        Args:
            message: 送信する通信メッセージ。

        Returns:
            None.
        """
        self.client.send_message(message)

    def _create_local_player(self, use_cpu: bool) -> PlayerController:
        """クライアント側の黒プレイヤーを作成します。

        Args:
            use_cpu: CPUプレイヤーを使う場合はTrue。

        Returns:
            クライアント側黒プレイヤー。
        """
        if use_cpu:
            return CpuPlayer(CLIENT_COLOR)

        return LocalHumanPlayer(CLIENT_COLOR)
