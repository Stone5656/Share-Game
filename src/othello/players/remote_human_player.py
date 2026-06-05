"""TCPで受信した相手プレイヤーの行動を扱います。"""

from dataclasses import dataclass, field

from loguru import logger
import pygame

from src.othello.core.game_enums import Cell, PlayerKind
from src.othello.core.game_types import (
    BoardPosition,
    LegalMove,
    PlayerAction,
    PlayerContext,
)


@dataclass
class RemoteHumanPlayer:
    """TCP経由で受け取った着手またはパスを扱うリモート人間プレイヤーです。"""

    color: Cell
    kind: PlayerKind = PlayerKind.REMOTE_HUMAN
    _pending_position: BoardPosition | None = field(default=None, init=False)
    _pending_pass: bool = field(default=False, init=False)

    def receive_hit(self, position: BoardPosition) -> None:
        """相手から受信したHIT位置を保存します。

        Args:
            position: 相手が石を置いた位置。

        Returns:
            None.
        """
        self._pending_position = position
        self._pending_pass = False
        logger.info(
            "HITをRemoteHumanPlayerへ保存しました: color={}, position={}",
            self.color.name,
            position,
        )

    def receive_pass(self) -> None:
        """相手から受信したPASSを保存します。

        Returns:
            None.
        """
        self._pending_position = None
        self._pending_pass = True
        logger.info("PASSをRemoteHumanPlayerへ保存しました: color={}", self.color.name)

    def handle_event(self, event: pygame.event.Event) -> None:
        """pygameイベントを受け取ります。

        RemoteHumanPlayerはTCP経由の行動だけを扱うため、pygameイベントは使用しません。

        Args:
            event: pygameのイベントオブジェクト。

        Returns:
            None.
        """
        return

    def select_action(self, context: PlayerContext) -> PlayerAction | None:
        """受信済みの行動が現在状況で有効であればPlayerActionを返します。

        Args:
            context: 手を選ぶために必要な情報。

        Returns:
            有効な行動が受信済みであればPlayerAction、それ以外はNone。
        """
        if context.current_player is not self.color:
            self._clear_pending_action()
            logger.warning(
                "手番ではないRemote行動を破棄しました: color={}, current_player={}",
                self.color.name,
                context.current_player.name,
            )
            return None

        if self._pending_pass:
            self._pending_pass = False
            return PlayerAction(is_pass=True)

        if self._pending_position is None:
            return None

        position: BoardPosition = self._pending_position
        self._pending_position = None

        if not self._is_legal_position(position, context.legal_moves):
            logger.warning(
                "非合法HIT受信のため破棄しました: color={}, position={}",
                self.color.name,
                position,
            )
            return None

        logger.info(
            "RemoteHumanPlayerがHITを選択しました: color={}, position={}",
            self.color.name,
            position,
        )
        return PlayerAction(position=position)

    def _clear_pending_action(self) -> None:
        """保留中のリモート行動を破棄します。

        Returns:
            None.
        """
        self._pending_position = None
        self._pending_pass = False

    def _is_legal_position(
        self,
        position: BoardPosition,
        legal_moves: tuple[LegalMove, ...],
    ) -> bool:
        """指定位置が合法手に含まれるかを返します。

        Args:
            position: 確認対象の盤面位置。
            legal_moves: 現在の合法手一覧。

        Returns:
            指定位置が合法手であればTrue。
        """
        return any(legal_move.position == position for legal_move in legal_moves)
