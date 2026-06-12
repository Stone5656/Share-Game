"""CPUの軽量な強化学習処理を扱うパッケージです。"""

from src.othello.players.cpu.rl.training_config import (
    DEFAULT_TRAINING_CONFIG,
    TrainingConfig,
)

__all__ = ["DEFAULT_TRAINING_CONFIG", "TrainingConfig"]
