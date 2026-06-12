"""盤面状態ごとの価値をTD(0)で更新します。"""

from loguru import logger

from src.othello.players.cpu.rl.state_value_store import StateValueStore


class TabularTdLearner:
    """盤面ごとの状態価値をTD(0)で更新します。"""

    def __init__(
        self,
        store: StateValueStore,
        learning_rate: float,
        gamma: float,
    ) -> None:
        """TD学習器を初期化します。

        Args:
            store: 更新対象の状態価値テーブル。
            learning_rate: 学習率。
            gamma: 将来価値の割引率。
        """
        self._store = store
        self._learning_rate = learning_rate
        self._gamma = gamma

    def update(
        self,
        current_key: str,
        reward: float,
        next_key: str | None,
    ) -> None:
        """TD(0)で状態価値を更新します。

        Args:
            current_key: 現在状態のキー。
            reward: 現在状態から得た報酬。
            next_key: 次状態のキー。終局状態ではNone。
        """
        current_value = self._store.get_value(current_key)
        next_value = 0.0 if next_key is None else self._store.get_value(next_key)
        delta = reward + self._gamma * next_value - current_value
        updated_value = current_value + self._learning_rate * delta
        self._store.set_value(current_key, updated_value)
        self._store.increment_visits(current_key)
        logger.debug(
            "Tabular TD更新: reward={}, current={}, next={}, delta={}, updated={}",
            reward,
            current_value,
            next_value,
            delta,
            updated_value,
        )
