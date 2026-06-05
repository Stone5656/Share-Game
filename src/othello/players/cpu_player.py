"""合法手から自動的に着手を選択するCPUプレイヤーを定義します。"""

import random
import time
from dataclasses import dataclass, field

from loguru import logger

from src.othello.core.game_enums import Cell, PlayerKind
from src.othello.core.game_types import LegalMove, PlayerAction, PlayerContext


@dataclass
class CpuPlayer:
    """CPUプレイヤーを表します。

    現在の合法手一覧から1手を選択し、PlayerActionとして返します。
    通信処理や盤面更新は行いません。
    """

    color: Cell
    kind: PlayerKind = PlayerKind.CPU
    think_seconds: float = 0.5
    _thinking_started_at: float | None = field(default=None, init=False)

    def handle_event(self, event: object) -> None:
        """CPUはpygameイベントを使用しません。

        Args:
            event: pygameイベント。

        Returns:
            None.
        """
        return None

    def select_action(self, context: PlayerContext) -> PlayerAction | None:
        """現在の合法手から着手を選択します。

        Args:
            context: 手を選ぶために必要な情報。

        Returns:
            着手可能で、思考時間が経過していればPlayerAction。
            まだ思考中、または合法手がなければNone。
        """
        if not context.legal_moves:
            self._thinking_started_at = None
            return None

        now: float = time.monotonic()

        if self._thinking_started_at is None:
            self._thinking_started_at = now
            logger.info("CPU思考を開始しました: color={}", self.color.name)
            return None

        if now - self._thinking_started_at < self.think_seconds:
            return None

        selected_move: LegalMove = random.choice(context.legal_moves)
        self._thinking_started_at = None
        logger.info(
            "CPUが着手を選択しました: color={}, position={}",
            self.color.name,
            selected_move.position,
        )
        return PlayerAction(position=selected_move.position)
