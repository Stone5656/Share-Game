"""盤面記憶型CPUの状態キー、保存、TD更新をテストします。"""

import json
import tempfile
import unittest
from pathlib import Path

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.players.cpu.rl.board_state_key import BoardStateKeyFactory
from src.othello.players.cpu.rl.state_value_store import StateValueStore
from src.othello.players.cpu.rl.tabular_td_learner import TabularTdLearner


class TabularStateValueComponentsTest(unittest.TestCase):
    """状態価値テーブルの基礎コンポーネントを確認します。"""

    def test_board_state_key_contains_player_and_board(self) -> None:
        """状態キーには評価視点の色と64マスを含めます。"""
        key = BoardStateKeyFactory().create_key(Board(), Cell.BLACK)

        self.assertEqual(
            key,
            "BLACK:EEEEEEEE/EEEEEEEE/EEEEEEEE/EEEWBEEE/"
            "EEEBWEEE/EEEEEEEE/EEEEEEEE/EEEEEEEE",
        )

    def test_unknown_state_value_is_zero(self) -> None:
        """未知の盤面状態は0.0として扱います。"""
        store = StateValueStore(Path("unused.json"))

        self.assertEqual(store.get_value("unknown"), 0.0)

    def test_broken_json_recovers_with_empty_table(self) -> None:
        """壊れたJSONは空の状態価値テーブルへ復旧します。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "values.json"
            path.write_text("{broken", encoding="utf-8")
            store = StateValueStore(path)

            store.load()

            self.assertEqual(store.state_count, 0)
            self.assertEqual(store.get_value("unknown"), 0.0)

    def test_save_uses_expected_json_shape(self) -> None:
        """状態価値テーブルをversion付きJSONで保存します。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "values.json"
            store = StateValueStore(path)
            store.set_value("BLACK:state", 0.42)

            store.save()

            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"version": 1, "values": {"BLACK:state": 0.42}},
            )
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_tabular_td_update_uses_next_state_value(self) -> None:
        """TD(0)式で現在状態の価値を更新します。"""
        store = StateValueStore(Path("unused.json"))
        store.set_value("current", 0.2)
        store.set_value("next", 0.6)
        learner = TabularTdLearner(store, learning_rate=0.1, gamma=0.95)

        learner.update("current", reward=0.0, next_key="next")

        self.assertAlmostEqual(store.get_value("current"), 0.237)


if __name__ == "__main__":
    unittest.main()
