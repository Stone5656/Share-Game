"""強化学習を構成する各コンポーネントをテストします。"""

import json
import tempfile
import unittest
from pathlib import Path

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.core.move_simulator import simulate_move
from src.othello.core.rules import LegalMoveScanner
from src.othello.players.cpu.rl.feature_extractor import (
    BoardFeatures,
    FeatureExtractor,
)
from src.othello.players.cpu.rl.td_evaluator import TdEvaluator
from src.othello.players.cpu.rl.training_config import TrainingConfig
from src.othello.players.cpu.rl.weight_store import WeightStore


class RlComponentsTest(unittest.TestCase):
    """特徴抽出、TD更新、重み保存を確認します。"""

    def test_initial_board_features_are_balanced(self) -> None:
        """初期盤面は全差分特徴量が0になります。"""
        features = FeatureExtractor().extract(Board(), Cell.BLACK)

        self.assertEqual(features.values, (1.0, 0.0, 0.0, 0.0, 0.0, 0.0))

    def test_simulate_move_does_not_modify_original_board(self) -> None:
        """仮想着手は元盤面を変更しません。"""
        board = Board()
        legal_move = LegalMoveScanner().find_legal_moves(board, Cell.BLACK)[0]

        simulated = simulate_move(board, Cell.BLACK, legal_move)

        self.assertIs(board.get_cell(legal_move.position), Cell.EMPTY)
        self.assertIs(simulated.get_cell(legal_move.position), Cell.BLACK)

    def test_td_update_uses_terminal_reward(self) -> None:
        """終局状態では次状態価値0としてTD更新します。"""
        config = TrainingConfig(0.1, 0.95, 0.0, "unused.json")
        evaluator = TdEvaluator((0.0,) * 6, config)

        evaluator.update(
            BoardFeatures((1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
            reward=1.0,
            next_features=None,
        )

        self.assertAlmostEqual(evaluator.weights[0], 0.1)
        self.assertEqual(evaluator.weights[1:], (0.0,) * 5)

    def test_weight_store_recovers_from_broken_json(self) -> None:
        """壊れたJSONは初期重みへ復旧します。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "weights.json"
            path.write_text("{broken", encoding="utf-8")
            store = WeightStore(str(path), (0.0,) * 6)

            self.assertEqual(store.load(), (0.0,) * 6)

    def test_weight_store_saves_expected_shape(self) -> None:
        """重みをversion付きJSON形式で保存します。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "weights.json"
            weights = (0.0, 0.1, -0.2, 0.5, 0.3, 0.1)
            WeightStore(str(path), (0.0,) * 6).save(weights)

            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {"version": 1, "weights": list(weights)},
            )


if __name__ == "__main__":
    unittest.main()
