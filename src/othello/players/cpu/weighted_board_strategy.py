"""盤面位置の重みを使用するCPU戦略を定義します。"""

from typing import Final

from src.othello.core.game_types import LegalMove, PlayerContext

POSITION_WEIGHTS: Final[tuple[tuple[int, ...], ...]] = (
    (100, -20, 10, 5, 5, 10, -20, 100),
    (-20, -50, -2, -2, -2, -2, -50, -20),
    (10, -2, 3, 2, 2, 3, -2, 10),
    (5, -2, 2, 1, 1, 2, -2, 5),
    (5, -2, 2, 1, 1, 2, -2, 5),
    (10, -2, 3, 2, 2, 3, -2, 10),
    (-20, -50, -2, -2, -2, -2, -50, -20),
    (100, -20, 10, 5, 5, 10, -20, 100),
)


class WeightedBoardCpuStrategy:
    """盤面位置の重みと反転石数で合法手を評価するCPU戦略です。"""

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        return "Weighted Board"

    def select_move(self, context: PlayerContext) -> LegalMove | None:
        """盤面位置の重みが最大の合法手を選択します。

        同点の場合は、反転できる石数が多い手を優先します。

        Args:
            context: CPUが手を選ぶために必要な情報。

        Returns:
            選択した合法手。合法手がない場合はNone。
        """
        if not context.legal_moves:
            return None

        return max(context.legal_moves, key=self._evaluate_move)

    def _evaluate_move(self, move: LegalMove) -> tuple[int, int]:
        """合法手を盤面位置の重みと反転石数で評価します。

        Args:
            move: 評価する合法手。

        Returns:
            盤面位置の重みと反転石数のタプル。
        """
        position = move.position
        return (
            POSITION_WEIGHTS[position.row][position.col],
            len(move.flippable_positions),
        )
