"""開始画面で使用するボタンUIを定義します。"""

from dataclasses import dataclass

import pygame

from src.othello.constants import (
    BLACK_STONE_COLOR,
    GRID_COLOR,
    WHITE_STONE_COLOR,
)


@dataclass
class Button:
    """pygameの開始画面で使用するボタンを表します。

    Attributes:
        rect: ボタンの矩形。
        label: ボタンに表示する文字列。
    """

    rect: pygame.Rect
    label: str

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """ボタンを描画します。

        Args:
            surface: 描画先Surface。
            font: ラベル描画に使用するフォント。

        Returns:
            None.
        """
        pygame.draw.rect(surface, WHITE_STONE_COLOR, self.rect, border_radius=8)
        pygame.draw.rect(surface, GRID_COLOR, self.rect, width=2, border_radius=8)

        label_surface: pygame.Surface = font.render(
            self.label,
            True,
            BLACK_STONE_COLOR,
        )
        label_rect: pygame.Rect = label_surface.get_rect(center=self.rect.center)
        surface.blit(label_surface, label_rect)

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        """マウス座標がボタン内にあるかを返します。

        PDF仕様に合わせ、Rect.collidepoint((x, y)) を使用します。

        Args:
            mouse_pos: マウス座標。

        Returns:
            マウス座標がボタン内であればTrue。
        """
        return self.rect.collidepoint(mouse_pos)
