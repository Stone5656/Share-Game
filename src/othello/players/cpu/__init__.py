"""CPUの手選択アルゴリズムを扱うパッケージです。"""

from src.othello.players.cpu.cpu_strategy import CpuStrategy
from src.othello.players.cpu.cpu_strategy_factory import create_cpu_strategy

__all__ = ["CpuStrategy", "create_cpu_strategy"]
