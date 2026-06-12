"""盤面記憶型CPU戦略とself-play trainingをテストします。"""

import tempfile
import unittest
from pathlib import Path

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.core.game_types import PlayerContext
from src.othello.core.move_simulator import simulate_move
from src.othello.core.rules import LegalMoveScanner
from src.othello.players.cpu.rl.board_state_key import BoardStateKeyFactory
from src.othello.players.cpu.rl.self_play_trainer import SelfPlayTrainer
from src.othello.players.cpu.rl.state_value_store import StateValueStore
from src.othello.players.cpu.rl.training_config import TabularTrainingConfig
from src.othello.players.cpu.tabular_state_value_strategy import (
    TabularStateValueCpuStrategy,
)


class TabularTrainingTest(unittest.TestCase):
    """次盤面評価とCLI向けself-play保存を確認します。"""

    def test_strategy_selects_highest_value_next_board(self) -> None:
        """探索率0では次盤面の状態価値が最大の手を選択します。"""
        with tempfile.TemporaryDirectory() as directory:
            config = TabularTrainingConfig(
                games=1,
                epsilon=0.0,
                state_values_path=Path(directory) / "values.json",
            )
            store = StateValueStore(config.state_values_path)
            board = Board()
            moves = LegalMoveScanner().find_legal_moves(board, Cell.BLACK)
            preferred_move = moves[-1]
            preferred_board = simulate_move(board, Cell.BLACK, preferred_move)
            preferred_key = BoardStateKeyFactory().create_key(
                preferred_board,
                Cell.BLACK,
            )
            store.set_value(preferred_key, 1.0)
            strategy = TabularStateValueCpuStrategy(config=config, store=store)

            selected = strategy.select_move(PlayerContext(Cell.BLACK, moves, board))

            self.assertEqual(selected, preferred_move)

    def test_self_play_saves_state_values_to_configured_path(self) -> None:
        """self-playは指定された保存先へ状態価値を書き込みます。"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "custom-values.json"
            config = TabularTrainingConfig(
                games=1,
                epsilon=0.1,
                state_values_path=path,
                save_every=1,
            )

            SelfPlayTrainer().train(config)

            store = StateValueStore(path)
            store.load()
            self.assertTrue(path.exists())
            self.assertGreater(store.state_count, 0)


if __name__ == "__main__":
    unittest.main()
