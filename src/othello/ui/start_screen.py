"""開始画面の描画とボタン選択処理を定義します。"""

from loguru import logger
import pygame

from src.othello.config import AppState, NetworkConfig
from src.othello.constants import (
    BOARD_COLOR,
    RESULT_TEXT_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from src.othello.ui.button import Button


class StartScreen:
    """Local / Server / Client を選択する開始画面です。"""

    def __init__(self, network_config: NetworkConfig) -> None:
        """開始画面を初期化します。

        Args:
            network_config: TCP通信設定。
        """
        self.network_config: NetworkConfig = network_config
        self.title_font: pygame.font.Font = pygame.font.Font(None, 72)
        self.button_font: pygame.font.Font = pygame.font.Font(None, 36)
        self.status_font: pygame.font.Font = pygame.font.Font(None, 28)
        self.buttons: dict[AppState, Button] = self._create_buttons()

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

        for button in self.buttons.values():
            button.draw(surface, self.button_font)

    def _create_buttons(self) -> dict[AppState, Button]:
        """開始画面のボタンを作成します。

        Returns:
            AppStateごとのButton辞書。
        """
        button_width: int = 340
        button_height: int = 64
        start_y: int = 220
        gap: int = 28
        x: int = (SCREEN_WIDTH - button_width) // 2

        return {
            AppState.LOCAL_GAME: Button(
                rect=pygame.Rect(x, start_y, button_width, button_height),
                label="Local Player vs Player",
            ),
            AppState.SERVER_GAME: Button(
                rect=pygame.Rect(
                    x,
                    start_y + button_height + gap,
                    button_width,
                    button_height,
                ),
                label="Server / White",
            ),
            AppState.CLIENT_GAME: Button(
                rect=pygame.Rect(
                    x,
                    start_y + (button_height + gap) * 2,
                    button_width,
                    button_height,
                ),
                label="Client / Black",
            ),
        }

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
        title_rect: pygame.Rect = title_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5)
        )
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
        text_rect: pygame.Rect = text_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5 + 58)
        )
        surface.blit(text_surface, text_rect)
