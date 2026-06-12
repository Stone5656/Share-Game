"""CPU戦略の手選択基準をテストします。"""

import unittest

from src.othello.core.game_enums import Cell, CpuStrategyKind
from src.othello.core.game_types import BoardPosition, LegalMove, PlayerContext
from src.othello.players.cpu.corner_priority_strategy import (
    CornerPriorityCpuStrategy,
)
from src.othello.players.cpu.cpu_strategy_factory import create_cpu_strategy
from src.othello.players.cpu.greedy_strategy import GreedyCpuStrategy
from src.othello.players.cpu.random_strategy import RandomCpuStrategy
from src.othello.players.cpu.weighted_board_strategy import WeightedBoardCpuStrategy


def _move(row: int, col: int, flip_count: int) -> LegalMove:
    """テスト用の合法手を作成します。"""
    flips = tuple(BoardPosition(index, 0) for index in range(flip_count))
    return LegalMove(BoardPosition(row, col), flips)


def _context(*moves: LegalMove) -> PlayerContext:
    """テスト用のプレイヤー状況を作成します。"""
    return PlayerContext(Cell.BLACK, moves)


class CpuStrategyTest(unittest.TestCase):
    """CPU戦略ごとの評価基準を確認します。"""

    def test_random_selects_one_of_legal_moves(self) -> None:
        """Randomは合法手のいずれかを選択します。"""
        moves = (_move(2, 3, 1), _move(4, 5, 2))

        selected = RandomCpuStrategy().select_move(_context(*moves))

        self.assertIn(selected, moves)

    def test_greedy_selects_move_with_most_flips(self) -> None:
        """Greedyは反転石数が最大の手を選択します。"""
        few_flips = _move(2, 3, 1)
        many_flips = _move(4, 5, 4)

        selected = GreedyCpuStrategy().select_move(_context(few_flips, many_flips))

        self.assertEqual(selected, many_flips)

    def test_corner_priority_selects_corner_before_flip_count(self) -> None:
        """Corner Priorityは反転石数より角を優先します。"""
        many_flips = _move(3, 3, 7)
        corner = _move(0, 7, 1)

        selected = CornerPriorityCpuStrategy().select_move(_context(many_flips, corner))

        self.assertEqual(selected, corner)

    def test_corner_priority_falls_back_to_greedy(self) -> None:
        """Corner Priorityは角がなければ反転石数を優先します。"""
        few_flips = _move(2, 3, 1)
        many_flips = _move(4, 5, 4)

        selected = CornerPriorityCpuStrategy().select_move(
            _context(few_flips, many_flips)
        )

        self.assertEqual(selected, many_flips)

    def test_weighted_board_uses_flip_count_as_tiebreaker(self) -> None:
        """Weighted Boardは同じ位置評価なら反転石数を優先します。"""
        few_flips = _move(0, 2, 1)
        many_flips = _move(2, 0, 3)

        selected = WeightedBoardCpuStrategy().select_move(
            _context(few_flips, many_flips)
        )

        self.assertEqual(selected, many_flips)

    def test_strategies_return_none_without_legal_moves(self) -> None:
        """全戦略は合法手がなければNoneを返します。"""
        context = _context()

        for kind in CpuStrategyKind:
            with self.subTest(kind=kind):
                self.assertIsNone(create_cpu_strategy(kind).select_move(context))

    def test_factory_creates_all_strategy_kinds(self) -> None:
        """Factoryは全CPU戦略種別を生成します。"""
        expected_names = {
            CpuStrategyKind.RANDOM: "Random",
            CpuStrategyKind.GREEDY: "Greedy",
            CpuStrategyKind.CORNER_PRIORITY: "Corner Priority",
            CpuStrategyKind.WEIGHTED_BOARD: "Weighted Board",
            CpuStrategyKind.LEARNING_WEIGHTED: "Learning Weighted",
        }

        for kind, expected_name in expected_names.items():
            with self.subTest(kind=kind):
                self.assertEqual(create_cpu_strategy(kind).name, expected_name)


if __name__ == "__main__":
    unittest.main()
