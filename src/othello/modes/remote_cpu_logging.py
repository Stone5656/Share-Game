"""Remote対戦におけるローカルCPUのログ出力を定義します。"""

from loguru import logger

from src.othello.core.game_types import BoardPosition
from src.othello.players.cpu_player import CpuPlayer
from src.othello.players.player_controller import PlayerController


def log_local_hit(
    local_player: PlayerController,
    position: BoardPosition,
) -> None:
    """ローカルプレイヤーのHIT送信をログ出力します。

    Args:
        local_player: HITを送信したローカルプレイヤー。
        position: 着手位置。
    """
    if isinstance(local_player, CpuPlayer):
        logger.info(
            "CPU HIT送信: color={}, strategy={}, position={}",
            local_player.color.name,
            local_player.strategy.name,
            position,
        )
        return

    logger.info("HIT送信: position={}", position)


def log_local_pass(local_player: PlayerController) -> None:
    """ローカルプレイヤーのPASS送信をログ出力します。

    Args:
        local_player: PASSを送信したローカルプレイヤー。
    """
    if isinstance(local_player, CpuPlayer):
        logger.info(
            "CPU合法手なし: color={}, strategy={}",
            local_player.color.name,
            local_player.strategy.name,
        )
        logger.info(
            "CPU PASS送信: color={}, strategy={}",
            local_player.color.name,
            local_player.strategy.name,
        )
        return

    logger.info("PASS送信: player={}", local_player.color.name)


def get_cpu_strategy_name(local_player: PlayerController) -> str | None:
    """ローカルCPUの戦略名を返します。

    Args:
        local_player: 戦略名を確認するローカルプレイヤー。

    Returns:
        CPUの場合は戦略名、人間の場合はNone。
    """
    if isinstance(local_player, CpuPlayer):
        return local_player.strategy.name

    return None
