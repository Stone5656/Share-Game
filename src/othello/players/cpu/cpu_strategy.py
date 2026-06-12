"""CPUの手選択アルゴリズム共通インターフェースを定義します。"""

from typing import Protocol

from src.othello.core.game_types import LegalMove, PlayerContext


class CpuStrategy(Protocol):
    """CPUの手選択アルゴリズムを表す共通インターフェースです。"""

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        ...

    def select_move(self, context: PlayerContext) -> LegalMove | None:
        """現在の状況から合法手を1つ選択します。

        Args:
            context: CPUが手を選ぶために必要な情報。

        Returns:
            選択した合法手。合法手がない場合はNone。
        """
        ...
