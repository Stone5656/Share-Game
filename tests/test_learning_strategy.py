"""Learning Weighted戦略とself-play学習をテストします。"""

import tempfile
import unittest
from pathlib import Path

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.core.game_result import GameResult
from src.othello.core.game_types import PlayerContext
from src.othello.core.rules import LegalMoveScanner
from src.othello.players.cpu.learning_weighted_strategy import (
    LearningWeightedCpuStrategy,
)
from src.othello.players.cpu.rl.linear_self_play_trainer import (
    LinearSelfPlayTrainer,
)
from src.othello.players.cpu.rl.training_config import TrainingConfig


class LearningStrategyTest(unittest.TestCase):
    """学習戦略の手選択、更新、self-playを確認します。"""

    def test_strategy_updates_and_saves_weights(self) -> None:
        """終局通知で重みを更新してJSONへ保存します。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "weights.json"
            config = TrainingConfig(0.01, 0.95, 0.0, str(path))
            strategy = LearningWeightedCpuStrategy(config)
            board = Board()
            legal_moves = LegalMoveScanner().find_legal_moves(board, Cell.BLACK)

            selected = strategy.select_move(
                PlayerContext(Cell.BLACK, legal_moves, board)
            )
            strategy.on_game_finished(GameResult(40, 24, Cell.BLACK))

            self.assertIn(selected, legal_moves)
            self.assertTrue(path.exists())
            self.assertNotEqual(strategy.weights, (0.0,) * 6)

    def test_self_play_finishes_and_saves_weights(self) -> None:
        """self-playを1局完走して重みを保存します。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "weights.json"
            config = TrainingConfig(0.01, 0.95, 0.1, str(path))
            trainer = LinearSelfPlayTrainer(config)

            trainer.train(1)

            self.assertTrue(path.exists())
            self.assertEqual(len(trainer.weights), 6)


if __name__ == "__main__":
    unittest.main()
