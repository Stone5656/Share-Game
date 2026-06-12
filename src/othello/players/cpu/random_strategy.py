"""合法手からランダムに着手するCPU戦略を定義します。"""

import random

from src.othello.core.game_types import LegalMove, PlayerContext


class RandomCpuStrategy:
    """合法手からランダムに1手を選択するCPU戦略です。"""

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        return "Random"

    def select_move(self, context: PlayerContext) -> LegalMove | None:
        """合法手からランダムに1手を選択します。

        Args:
            context: CPUが手を選ぶために必要な情報。

        Returns:
            選択した合法手。合法手がない場合はNone。
        """
        if not context.legal_moves:
            return None

        return random.choice(context.legal_moves)
