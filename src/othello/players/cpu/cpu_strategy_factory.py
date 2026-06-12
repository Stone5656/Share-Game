"""CPU戦略種別から戦略インスタンスを作成します。"""

from src.othello.core.game_enums import CpuStrategyKind
from src.othello.players.cpu.corner_priority_strategy import (
    CornerPriorityCpuStrategy,
)
from src.othello.players.cpu.cpu_strategy import CpuStrategy
from src.othello.players.cpu.greedy_strategy import GreedyCpuStrategy
from src.othello.players.cpu.learning_weighted_strategy import (
    LearningWeightedCpuStrategy,
)
from src.othello.players.cpu.random_strategy import RandomCpuStrategy
from src.othello.players.cpu.weighted_board_strategy import WeightedBoardCpuStrategy


def create_cpu_strategy(kind: CpuStrategyKind) -> CpuStrategy:
    """CPU戦略種別からCPU戦略インスタンスを作成します。

    Args:
        kind: CPU戦略種別。

    Returns:
        対応するCPU戦略。
    """
    match kind:
        case CpuStrategyKind.RANDOM:
            return RandomCpuStrategy()
        case CpuStrategyKind.GREEDY:
            return GreedyCpuStrategy()
        case CpuStrategyKind.CORNER_PRIORITY:
            return CornerPriorityCpuStrategy()
        case CpuStrategyKind.WEIGHTED_BOARD:
            return WeightedBoardCpuStrategy()
        case CpuStrategyKind.LEARNING_WEIGHTED:
            return LearningWeightedCpuStrategy()

    raise ValueError(f"未対応のCPU戦略種別です: {kind}")
