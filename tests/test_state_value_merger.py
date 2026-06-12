"""version 2状態価値shardのmerge処理をテストします。"""

import json
import tempfile
import unittest
from pathlib import Path

from src.othello.players.cpu.rl.state_value_store import StateValueStore
from src.othello.training.state_value_merger import StateValueMerger


def _write_shard(
    path: Path,
    states: dict[str, dict[str, float | int]],
) -> None:
    """テスト用version 2 shardを書き込みます。"""
    path.write_text(
        json.dumps({"version": 2, "states": states}),
        encoding="utf-8",
    )


class StateValueMergerTest(unittest.TestCase):
    """訪問回数による加重平均と不正ファイル処理を確認します。"""

    def test_merges_values_by_visit_weighted_average(self) -> None:
        """同一状態は訪問回数による加重平均で統合します。"""
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory) / "shards"
            input_dir.mkdir()
            output_path = Path(directory) / "merged.json"
            _write_shard(
                input_dir / "worker_0.json",
                {
                    "shared": {"value": 0.5, "visits": 2},
                    "zero": {"value": 9.0, "visits": 0},
                },
            )
            _write_shard(
                input_dir / "worker_1.json",
                {"shared": {"value": -0.25, "visits": 6}},
            )

            result = StateValueMerger().merge(input_dir, output_path)

            store = StateValueStore(output_path)
            store.load()
            self.assertAlmostEqual(store.get_value("shared"), -0.0625)
            self.assertEqual(store.get_visits("shared"), 8)
            self.assertEqual(store.get_value("zero"), 0.0)
            self.assertEqual(store.get_visits("zero"), 0)
            self.assertEqual(result.loaded_shards, 2)
            self.assertEqual(result.state_count, 2)

    def test_skips_invalid_json_and_version(self) -> None:
        """壊れたJSONとversion 1ファイルをスキップします。"""
        with tempfile.TemporaryDirectory() as directory:
            input_dir = Path(directory) / "shards"
            input_dir.mkdir()
            output_path = Path(directory) / "merged.json"
            (input_dir / "broken.json").write_text("{broken", encoding="utf-8")
            (input_dir / "version_1.json").write_text(
                json.dumps({"version": 1, "values": {}}),
                encoding="utf-8",
            )

            result = StateValueMerger().merge(input_dir, output_path)

            self.assertEqual(result.loaded_shards, 0)
            self.assertEqual(result.skipped_files, 2)
            self.assertEqual(result.state_count, 0)


if __name__ == "__main__":
    unittest.main()
