"""開始画面の描画とボタン選択処理を定義します。"""

import pygame
from loguru import logger

from src.othello.config import AppState, NetworkConfig
from src.othello.constants import (
    BOARD_COLOR,
    RESULT_TEXT_COLOR,
    SCREEN_WIDTH,
)
from src.othello.core.game_enums import CpuStrategyKind
from src.othello.ui.button import Button
from src.othello.ui.start_screen_layout import (
    create_cpu_strategy_buttons,
    create_mode_buttons,
)


class StartScreen:
    """Local / Server / Client を選択する開始画面です。"""

    def __init__(self, network_config: NetworkConfig) -> None:
        """開始画面を初期化します。

        Args:
            network_config: TCP通信設定。
        """
        self.network_config: NetworkConfig = network_config
        self.title_font: pygame.font.Font = pygame.font.Font(None, 72)
        self.button_font: pygame.font.Font = pygame.font.Font(None, 23)
        self.status_font: pygame.font.Font = pygame.font.Font(None, 26)
        self.section_font: pygame.font.Font = pygame.font.Font(None, 30)
        self.selected_cpu_strategy: CpuStrategyKind = CpuStrategyKind.GREEDY
        self.buttons: dict[AppState, Button] = create_mode_buttons(network_config)
        self.cpu_strategy_buttons: dict[CpuStrategyKind, Button] = (
            create_cpu_strategy_buttons()
        )
        logger.info(
            "CPU戦略を選択しました: strategy={}",
            self.selected_cpu_strategy.name,
        )

    def handle_event(self, event: pygame.event.Event) -> AppState | None:
        """開始画面のイベントを処理します。

        Args:
            event: pygameイベント。

        Returns:
            選択されたAppState。未選択ならNone。
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        mouse_pos: tuple[int, int] = event.pos

        for strategy_kind, button in self.cpu_strategy_buttons.items():
            if button.is_clicked(mouse_pos):
                self.selected_cpu_strategy = strategy_kind
                logger.info(
                    "CPU戦略を変更しました: strategy={}",
                    strategy_kind.name,
                )
                return None

        for state, button in self.buttons.items():
            if button.is_clicked(mouse_pos):
                logger.info("開始画面ボタンが選択されました: label={}", button.label)
                return state

        return None

    def draw(self, surface: pygame.Surface) -> None:
        """開始画面を描画します。

        Args:
            surface: 描画先Surface。

        Returns:
            None.
        """
        surface.fill(BOARD_COLOR)
        self._draw_title(surface)
        self._draw_network_config(surface)
        self._draw_section_titles(surface)
        self._draw_selected_cpu_strategy(surface)

        for button in self.buttons.values():
            button.draw(surface, self.button_font)

        for button in self.cpu_strategy_buttons.values():
            button.draw(surface, self.button_font)

    def _draw_title(self, surface: pygame.Surface) -> None:
        """開始画面タイトルを描画します。

        Args:
            surface: 描画先Surface。

        Returns:
            None.
        """
        title_surface: pygame.Surface = self.title_font.render(
            "Othello",
            True,
            RESULT_TEXT_COLOR,
        )
        title_rect: pygame.Rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surface, title_rect)

    def _draw_network_config(self, surface: pygame.Surface) -> None:
        """現在のTCP通信設定を描画します。

        Args:
            surface: 描画先Surface。

        Returns:
            None.
        """
        text_surface: pygame.Surface = self.status_font.render(
            f"Network: {self.network_config.host}:{self.network_config.port}",
            True,
            RESULT_TEXT_COLOR,
        )
        text_rect: pygame.Rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
        surface.blit(text_surface, text_rect)

    def _draw_section_titles(self, surface: pygame.Surface) -> None:
        """モード選択とCPU戦略選択の見出しを描画します。

        Args:
            surface: 描画先Surface。

        Returns:
            None.
        """
        for text, center_x in (("Game Mode", 160), ("CPU Strategy", 470)):
            text_surface: pygame.Surface = self.section_font.render(
                text,
                True,
                RESULT_TEXT_COLOR,
            )
            text_rect: pygame.Rect = text_surface.get_rect(center=(center_x, 195))
            surface.blit(text_surface, text_rect)

    def _draw_selected_cpu_strategy(self, surface: pygame.Surface) -> None:
        """選択中のCPU戦略を描画します。

        Args:
            surface: 描画先Surface。

        Returns:
            None.
        """
        selected_name: str = self.cpu_strategy_buttons[
            self.selected_cpu_strategy
        ].label.removeprefix("CPU Strategy: ")
        text_surface: pygame.Surface = self.status_font.render(
            f"Selected CPU Strategy: {selected_name}",
            True,
            RESULT_TEXT_COLOR,
        )
        text_rect: pygame.Rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 590))
        surface.blit(text_surface, text_rect)
