"""CPUの手選択アルゴリズム共通インターフェースを定義します。"""

from typing import Protocol, runtime_checkable

from src.othello.core.game_result import GameResult
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


@runtime_checkable
class GameFinishedCpuStrategy(Protocol):
    """対局終了結果を受け取るCPU戦略のインターフェースです。"""

    def on_game_finished(self, result: GameResult) -> None:
        """対局結果を戦略へ通知します。

        Args:
            result: 終了した対局の結果。
        """
        ...
