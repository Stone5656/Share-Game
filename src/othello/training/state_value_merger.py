"""複数の状態価値shardを訪問回数で加重平均します。"""

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from src.othello.players.cpu.rl.state_value_store import StateValueStore
from src.othello.training.training_shard import (
    StateValueEntry,
    load_version_2_shard,
)


@dataclass(frozen=True)
class MergeResult:
    """状態価値mergeの結果を表します。"""

    loaded_shards: int
    skipped_files: int
    state_count: int


class StateValueMerger:
    """version 2の状態価値shardを安全に統合します。"""

    def merge(self, input_dir: Path, output_path: Path) -> MergeResult:
        """入力ディレクトリ内のJSON shardを統合します。

        Args:
            input_dir: shardファイルを探索するディレクトリ。
            output_path: merge結果の保存先。

        Returns:
            読み込み数、スキップ数、状態数。
        """
        logger.info(
            "merge開始: input_dir={}, output={}",
            input_dir,
            output_path,
        )
        weighted_sums: dict[str, float] = {}
        visit_sums: dict[str, int] = {}
        loaded_shards = 0
        skipped_files = 0

        for path in sorted(input_dir.glob("*.json")):
            try:
                entries = load_version_2_shard(path)
            except OSError, ValueError:
                skipped_files += 1
                logger.warning("不正なshardをスキップ: path={}", path)
                continue

            loaded_shards += 1
            self._accumulate(entries, weighted_sums, visit_sums)

        store = StateValueStore(output_path)
        for key in weighted_sums.keys() | visit_sums.keys():
            visits = visit_sums.get(key, 0)
            value = weighted_sums.get(key, 0.0) / visits if visits else 0.0
            store.set_entry(key, StateValueEntry(value, visits))
        store.save()
        result = MergeResult(loaded_shards, skipped_files, store.state_count)
        logger.info(
            "merge終了: loaded_shards={}, skipped_files={}, state_count={}",
            result.loaded_shards,
            result.skipped_files,
            result.state_count,
        )
        return result

    def _accumulate(
        self,
        entries: dict[str, StateValueEntry],
        weighted_sums: dict[str, float],
        visit_sums: dict[str, int],
    ) -> None:
        """1 shard分の重み付き価値と訪問回数を加算します。"""
        for key, entry in entries.items():
            weighted_sums[key] = (
                weighted_sums.get(key, 0.0) + entry.value * entry.visits
            )
            visit_sums[key] = visit_sums.get(key, 0) + entry.visits
