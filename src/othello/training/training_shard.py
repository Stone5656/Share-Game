"""状態価値shardの型とJSON変換を定義します。"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StateValueEntry:
    """1つの状態価値と訪問回数を表します。

    Attributes:
        value: 状態価値。
        visits: 訪問回数。
    """

    value: float
    visits: int


def load_version_2_shard(path: Path) -> dict[str, StateValueEntry]:
    """version 2の状態価値shardを読み込みます。

    Args:
        path: 読み込むJSONファイル。

    Returns:
        状態キーごとの状態価値Entry。

    Raises:
        ValueError: JSON形式やversionが不正な場合。
        OSError: ファイルを読み込めない場合。
    """
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 2:
        raise ValueError("version 2のshardではありません。")

    raw_states = payload.get("states")
    if not isinstance(raw_states, dict):
        raise ValueError("statesはオブジェクトである必要があります。")

    entries: dict[str, StateValueEntry] = {}
    for key, raw_entry in raw_states.items():
        if not isinstance(key, str) or not isinstance(raw_entry, dict):
            raise ValueError("状態価値Entryの形式が不正です。")

        value = raw_entry.get("value")
        visits = raw_entry.get("visits")
        if not isinstance(value, int | float):
            raise ValueError("valueは数値である必要があります。")
        if type(visits) is not int or visits < 0:
            raise ValueError("visitsは0以上の整数である必要があります。")
        entries[key] = StateValueEntry(float(value), visits)

    return entries
