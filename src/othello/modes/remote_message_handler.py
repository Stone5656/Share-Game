"""Remoteから受信したHIT/PASSの反映処理を定義します。"""

from dataclasses import dataclass

from loguru import logger

from src.othello.core.game_engine import GameEngine
from src.othello.core.game_types import BoardPosition, PlayerAction, PlayerContext
from src.othello.network.protocol import OthelloMessage
from src.othello.players.remote_human_player import RemoteHumanPlayer


@dataclass
class RemoteMessageHandler:
    """Remote側プレイヤーのHIT/PASSをGameEngineへ反映します。"""

    engine: GameEngine
    remote_player: RemoteHumanPlayer

    def apply_hit(self, message: OthelloMessage) -> bool:
        """受信したHITを検証し、盤面へ反映します。

        Args:
            message: 受信したHITメッセージ。

        Returns:
            反映できた場合はTrue。
        """
        if message.row is None or message.col is None:
            logger.warning("非合法HIT受信: rowまたはcolがありません。")
            return False

        position: BoardPosition = BoardPosition(row=message.row, col=message.col)
        self.remote_player.receive_hit(position)
        action: PlayerAction | None = self.remote_player.select_action(
            self._create_context()
        )

        if action is None or action.position is None:
            logger.warning("非合法HIT受信: position={}", position)
            return False

        if not self.engine.apply_move(action.position):
            logger.warning("非合法HIT受信: position={}", position)
            return False

        logger.info("HIT受信を盤面へ反映しました: position={}", position)
        return True

    def apply_pass(self) -> bool:
        """受信したPASSを検証し、盤面へ反映します。

        Returns:
            反映できた場合はTrue。
        """
        self.remote_player.receive_pass()
        action: PlayerAction | None = self.remote_player.select_action(
            self._create_context()
        )

        if action is None or not action.is_pass:
            logger.warning("PASS受信を反映できませんでした。")
            return False

        if self.engine.apply_pass(self.remote_player.color):
            logger.info(
                "PASS受信を盤面へ反映しました: player={}",
                self.remote_player.color.name,
            )
            return True

        return False

    def _create_context(self) -> PlayerContext:
        """現在のGameEngine状態からPlayerContextを作成します。

        Returns:
            PlayerContext。
        """
        return PlayerContext(
            current_player=self.engine.current_player,
            legal_moves=self.engine.legal_moves,
        )
