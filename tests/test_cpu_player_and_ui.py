"""CpuPlayerの戦略委譲と開始画面の選択処理をテストします。"""

import unittest

import pygame

from src.othello.config import NetworkConfig
from src.othello.core.game_enums import Cell, CpuStrategyKind
from src.othello.core.game_types import BoardPosition, LegalMove, PlayerContext
from src.othello.players.cpu.cpu_strategy import CpuStrategy
from src.othello.players.cpu_player import CpuPlayer
from src.othello.ui.start_screen import StartScreen


class RecordingStrategy:
    """呼び出し状況を記録するテスト用CPU戦略です。"""

    def __init__(self, selected_move: LegalMove) -> None:
        """テスト用戦略を初期化します。"""
        self.selected_move = selected_move
        self.received_context: PlayerContext | None = None

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        return "Recording"

    def select_move(self, context: PlayerContext) -> LegalMove | None:
        """受け取った状況を記録して固定の合法手を返します。"""
        self.received_context = context
        return self.selected_move


class CpuPlayerAndUiTest(unittest.TestCase):
    """CpuPlayerと開始画面のCPU戦略選択を確認します。"""

    @classmethod
    def setUpClass(cls) -> None:
        """pygameのフォント機能を初期化します。"""
        pygame.font.init()

    @classmethod
    def tearDownClass(cls) -> None:
        """pygameのフォント機能を終了します。"""
        pygame.font.quit()

    def test_cpu_player_delegates_move_selection_to_strategy(self) -> None:
        """CpuPlayerは手選択を注入された戦略へ委譲します。"""
        move = LegalMove(BoardPosition(2, 3), (BoardPosition(3, 3),))
        context = PlayerContext(Cell.BLACK, (move,))
        strategy = RecordingStrategy(move)
        typed_strategy: CpuStrategy = strategy
        player = CpuPlayer(Cell.BLACK, strategy=typed_strategy, think_seconds=0)

        self.assertIsNone(player.select_action(context))
        action = player.select_action(context)

        self.assertIs(strategy.received_context, context)
        self.assertIsNotNone(action)
        self.assertEqual(action.position if action else None, move.position)

    def test_start_screen_updates_selected_cpu_strategy(self) -> None:
        """CPU戦略ボタンのクリックで選択中戦略を更新します。"""
        screen = StartScreen(NetworkConfig("127.0.0.1", 5555))
        button = screen.cpu_strategy_buttons[CpuStrategyKind.TABULAR_STATE_VALUE]
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=button.rect.center,
        )

        selected_state = screen.handle_event(event)

        self.assertIsNone(selected_state)
        self.assertIs(
            screen.selected_cpu_strategy,
            CpuStrategyKind.TABULAR_STATE_VALUE,
        )
        self.assertFalse(hasattr(screen, "learning_training_control"))


if __name__ == "__main__":
    unittest.main()
