"""CPU戦略へ対局ライフサイクルを通知します。"""

from src.othello.core.game_result import GameResult
from src.othello.players.cpu.cpu_strategy import GameFinishedCpuStrategy
from src.othello.players.cpu_player import CpuPlayer
from src.othello.players.player_controller import PlayerController


def notify_game_finished(
    player: PlayerController,
    result: GameResult,
) -> None:
    """対応するCPU戦略へ対局結果を通知します。

    Args:
        player: 結果を通知するプレイヤー。
        result: 終了した対局の結果。
    """
    if not isinstance(player, CpuPlayer):
        return

    if isinstance(player.strategy, GameFinishedCpuStrategy):
        player.strategy.on_game_finished(result)
