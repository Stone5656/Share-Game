"""盤面状態ごとの価値をJSONファイルへ保存します。"""

import json
from pathlib import Path

from loguru import logger


class StateValueStore:
    """盤面状態ごとの価値をJSONファイルへ保存・読み込みします。"""

    def __init__(self, file_path: Path) -> None:
        """状態価値テーブルの保存先を設定します。

        Args:
            file_path: 状態価値JSONファイルのパス。
        """
        self._path = file_path
        self._values: dict[str, float] = {}

    @property
    def state_count(self) -> int:
        """記憶している状態数を返します。"""
        return len(self._values)

    def get_value(self, key: str) -> float:
        """状態キーに対応する価値を返します。

        Args:
            key: 参照する状態キー。

        Returns:
            記憶済みの価値。未知状態では0.0。
        """
        return self._values.get(key, 0.0)

    def set_value(self, key: str, value: float) -> None:
        """状態キーに対応する価値を設定します。

        Args:
            key: 更新する状態キー。
            value: 新しい状態価値。
        """
        self._values[key] = value

    def load(self) -> None:
        """JSONファイルから状態価値テーブルを読み込みます。"""
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            raw_values = payload["values"]
            if not isinstance(raw_values, dict):
                raise ValueError("valuesはオブジェクトである必要があります。")
            self._values = {str(key): float(value) for key, value in raw_values.items()}
        except OSError, ValueError, TypeError, KeyError, json.JSONDecodeError:
            self._values = {}
            logger.warning(
                "状態価値テーブル読み込み失敗。空テーブルを使用します: path={}",
                self._path,
            )
            return

        logger.info(
            "状態価値テーブル読み込み: path={}, state_count={}",
            self._path,
            self.state_count,
        )

    def save(self) -> None:
        """状態価値テーブルを一時ファイル経由でJSONへ保存します。"""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self._path.with_suffix(f"{self._path.suffix}.tmp")
        payload = {"version": 1, "values": self._values}
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary_path.replace(self._path)
        logger.info(
            "状態価値テーブル保存: path={}, state_count={}",
            self._path,
            self.state_count,
        )
