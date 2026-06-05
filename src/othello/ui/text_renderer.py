"""pygameによるテキスト描画処理を定義します。"""

import pygame

from src.othello.constants import (
    RESULT_BACKGROUND_ALPHA,
    RESULT_BACKGROUND_COLOR,
    RESULT_FONT_SIZE,
    RESULT_TEXT_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class ResultTextRenderer:
    """ゲーム結果テキストを描画します。"""

    def __init__(self) -> None:
        """結果テキスト描画クラスを初期化します。"""
        self.font: pygame.font.Font = pygame.font.Font(None, RESULT_FONT_SIZE)

    def draw(self, surface: pygame.Surface, result_text: str | None) -> None:
        """ゲーム結果テキストを中央に描画します。

        Args:
            surface: 描画先Surface。
            result_text: 描画するゲーム結果文字列。

        Returns:
            None.
        """
        if result_text is None:
            return

        overlay: pygame.Surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA,
        )
        overlay.fill((*RESULT_BACKGROUND_COLOR, RESULT_BACKGROUND_ALPHA))
        surface.blit(overlay, (0, 0))

        text_surface: pygame.Surface = self.font.render(
            result_text,
            True,
            RESULT_TEXT_COLOR,
        )
        text_rect: pygame.Rect = text_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        surface.blit(text_surface, text_rect)
