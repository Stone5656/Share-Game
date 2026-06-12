"""強化学習の重みをJSONファイルへ保存します。"""

import json
from pathlib import Path

from loguru import logger


class WeightStore:
    """強化学習の重みをJSONファイルに保存・読み込みします。"""

    def __init__(
        self,
        file_path: str,
        initial_weights: tuple[float, ...],
    ) -> None:
        """重み保存先と初期重みを設定します。

        Args:
            file_path: JSONファイルの保存先。
            initial_weights: 読み込み失敗時に使用する初期重み。
        """
        self._path = Path(file_path)
        self._initial_weights = initial_weights

    def load(self) -> tuple[float, ...]:
        """重みを読み込みます。

        Returns:
            読み込んだ重み。失敗時は初期重み。
        """
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            raw_weights = payload["weights"]
            weights = tuple(float(value) for value in raw_weights)
            if len(weights) != len(self._initial_weights):
                raise ValueError("重み数が特徴量数と一致しません。")
        except OSError, ValueError, TypeError, KeyError, json.JSONDecodeError:
            logger.warning(
                "重み読み込み失敗。初期重みを使用します: path={}",
                self._path,
            )
            return self._initial_weights

        logger.info("重み読み込み成功: path={}, weights={}", self._path, weights)
        return weights

    def save(self, weights: tuple[float, ...]) -> None:
        """重みを保存します。

        Args:
            weights: 保存する重み。
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "weights": list(weights)}
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("重み保存成功: path={}, weights={}", self._path, weights)
