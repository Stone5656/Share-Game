"""TD(0)による線形盤面評価と重み更新を定義します。"""

from loguru import logger

from src.othello.players.cpu.rl.feature_extractor import BoardFeatures
from src.othello.players.cpu.rl.training_config import TrainingConfig


class TdEvaluator:
    """TD(0)で線形評価関数の重みを更新します。"""

    def __init__(
        self,
        weights: tuple[float, ...],
        config: TrainingConfig,
    ) -> None:
        """TD評価器を初期化します。

        Args:
            weights: 初期重み。
            config: 強化学習設定。
        """
        self._weights = list(weights)
        self._config = config

    @property
    def weights(self) -> tuple[float, ...]:
        """現在の重みを返します。"""
        return tuple(self._weights)

    def evaluate(self, features: BoardFeatures) -> float:
        """特徴量から盤面評価値を計算します。

        Args:
            features: 評価対象の特徴量。

        Returns:
            重みと特徴量の内積。
        """
        return sum(
            weight * feature
            for weight, feature in zip(
                self._weights,
                features.values,
                strict=True,
            )
        )

    def update(
        self,
        current_features: BoardFeatures,
        reward: float,
        next_features: BoardFeatures | None,
    ) -> None:
        """TD(0)で重みを更新します。

        Args:
            current_features: 現在状態の特徴量。
            reward: 現在状態から得た報酬。
            next_features: 次状態の特徴量。終局状態ではNone。
        """
        current_value = self.evaluate(current_features)
        next_value = 0.0 if next_features is None else self.evaluate(next_features)
        td_error = reward + self._config.gamma * next_value - current_value

        for index, feature in enumerate(current_features.values):
            self._weights[index] += self._config.learning_rate * td_error * feature

        logger.debug(
            "TD更新: reward={}, current_value={}, next_value={}, delta={}",
            reward,
            current_value,
            next_value,
            td_error,
        )
