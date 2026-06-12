"""反転石数を優先するCPU戦略を定義します。"""

from src.othello.core.game_types import LegalMove, PlayerContext


class GreedyCpuStrategy:
    """反転できる石数が最大の合法手を選択するCPU戦略です。"""

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        return "Greedy"

    def select_move(self, context: PlayerContext) -> LegalMove | None:
        """反転できる石数が最大の合法手を選択します。

        Args:
            context: CPUが手を選ぶために必要な情報。

        Returns:
            選択した合法手。合法手がない場合はNone。
        """
        if not context.legal_moves:
            return None

        return max(
            context.legal_moves,
            key=lambda move: len(move.flippable_positions),
        )
