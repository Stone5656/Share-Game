"""強化学習の設定値を定義します。"""

from dataclasses import dataclass


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
