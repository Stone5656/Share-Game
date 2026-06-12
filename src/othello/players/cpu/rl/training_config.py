"""強化学習の設定値を定義します。"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingConfig:
    """強化学習の設定値を表します。

    Attributes:
        learning_rate: 重み更新の学習率。
        gamma: 将来報酬の割引率。
        epsilon: ε-greedyの探索率。
        weight_file_path: 重みJSONファイルの保存先。
    """

    learning_rate: float
    gamma: float
    epsilon: float
    weight_file_path: str


DEFAULT_TRAINING_CONFIG = TrainingConfig(
    learning_rate=0.01,
    gamma=0.95,
    epsilon=0.1,
    weight_file_path="data/othello_rl_weights.json",
)


@dataclass(frozen=True)
class TabularTrainingConfig:
    """盤面記憶型CPUの学習設定を表します。

    Attributes:
        games: 自己対戦の回数。
        learning_rate: 学習率。
        gamma: 割引率。
        epsilon: 探索率。
        state_values_path: 状態価値JSONの保存先。
        save_every: 何局ごとに保存するか。
    """

    games: int = 100
    learning_rate: float = 0.1
    gamma: float = 0.95
    epsilon: float = 0.1
    state_values_path: Path = Path("data/othello_state_values.json")
    save_every: int = 1
