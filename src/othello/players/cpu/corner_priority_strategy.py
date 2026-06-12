"""角を最優先するCPU戦略を定義します。"""

from typing import Final

from src.othello.constants import BOARD_SIZE
from src.othello.core.game_types import BoardPosition, LegalMove, PlayerContext
from src.othello.players.cpu.greedy_strategy import GreedyCpuStrategy

CORNER_POSITIONS: Final[frozenset[BoardPosition]] = frozenset(
    {
        BoardPosition(0, 0),
        BoardPosition(0, BOARD_SIZE - 1),
        BoardPosition(BOARD_SIZE - 1, 0),
        BoardPosition(BOARD_SIZE - 1, BOARD_SIZE - 1),
    }
)


class CornerPriorityCpuStrategy:
    """角があれば角を、なければ反転石数が最大の手を選ぶCPU戦略です。"""

    def __init__(self) -> None:
        """角がない場合に使用する戦略を初期化します。"""
        self._fallback_strategy: GreedyCpuStrategy = GreedyCpuStrategy()

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        return "Corner Priority"

    def select_move(self, context: PlayerContext) -> LegalMove | None:
        """角を優先して合法手を選択します。

        Args:
            context: CPUが手を選ぶために必要な情報。

        Returns:
            選択した合法手。合法手がない場合はNone。
        """
        for move in context.legal_moves:
            if move.position in CORNER_POSITIONS:
                return move

        return self._fallback_strategy.select_move(context)
