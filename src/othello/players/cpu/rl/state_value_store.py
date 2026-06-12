"""盤面状態ごとの価値と訪問回数をJSONファイルへ保存します。"""

import json
from pathlib import Path

from loguru import logger

from src.othello.training.training_shard import (
    StateValueEntry,
    load_version_2_shard,
)


class StateValueStore:
    """盤面状態ごとの価値をJSONファイルへ保存・読み込みします。"""

    def __init__(self, file_path: Path) -> None:
        """状態価値テーブルの保存先を設定します。

        Args:
            file_path: 状態価値JSONファイルのパス。
        """
        self._path = file_path
        self._states: dict[str, StateValueEntry] = {}

    @property
    def state_count(self) -> int:
        """記憶している状態数を返します。"""
        return len(self._states)

    def get_value(self, key: str) -> float:
        """状態キーに対応する価値を返します。

        Args:
            key: 参照する状態キー。

        Returns:
            記憶済みの価値。未知状態では0.0。
        """
        return self._states.get(key, StateValueEntry(0.0, 0)).value

    def get_visits(self, key: str) -> int:
        """状態キーに対応する訪問回数を返します。

        Args:
            key: 参照する状態キー。

        Returns:
            記憶済みの訪問回数。未知状態では0。
        """
        return self._states.get(key, StateValueEntry(0.0, 0)).visits

    def set_value(self, key: str, value: float) -> None:
        """状態キーに対応する価値を設定します。

        Args:
            key: 更新する状態キー。
            value: 新しい状態価値。
        """
        self._states[key] = StateValueEntry(value, self.get_visits(key))

    def set_entry(self, key: str, entry: StateValueEntry) -> None:
        """状態キーに対応するEntry全体を設定します。

        Args:
            key: 更新する状態キー。
            entry: 新しい状態価値と訪問回数。
        """
        self._states[key] = entry

    def increment_visits(self, key: str) -> None:
        """状態キーの訪問回数を1増やします。

        Args:
            key: 訪問回数を増やす状態キー。
        """
        self._states[key] = StateValueEntry(
            self.get_value(key),
            self.get_visits(key) + 1,
        )

    def iter_entries(self) -> tuple[tuple[str, StateValueEntry], ...]:
        """状態価値Entryのスナップショットを返します。"""
        return tuple(self._states.items())

    def load(self) -> None:
        """JSONファイルから状態価値テーブルを読み込みます。"""
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            version = payload.get("version", 1)
            if version == 2:
                self._states = load_version_2_shard(self._path)
            elif version == 1:
                self._states = self._load_version_1(payload)
            else:
                raise ValueError("未対応の状態価値versionです。")
        except OSError, ValueError, TypeError, json.JSONDecodeError:
            self._states = {}
            logger.warning(
                "状態価値テーブル読み込み失敗。空テーブルを使用: path={}",
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
        payload = {
            "version": 2,
            "states": {
                key: {"value": entry.value, "visits": entry.visits}
                for key, entry in self._states.items()
            },
        }
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

    def _load_version_1(self, payload: object) -> dict[str, StateValueEntry]:
        """旧version 1形式をvisits=1として読み込みます。"""
        if not isinstance(payload, dict):
            raise ValueError("状態価値payloadが不正です。")
        raw_values = payload.get("values")
        if not isinstance(raw_values, dict):
            raise ValueError("valuesはオブジェクトである必要があります。")
        return {
            str(key): StateValueEntry(float(value), 1)
            for key, value in raw_values.items()
        }
