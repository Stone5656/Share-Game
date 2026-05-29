"""pygameによるオセロ盤面の描画処理を定義します。"""

import pygame

from src.othello.board import Board
from src.othello.constants import (
    BLACK_STONE_COLOR,
    BOARD_COLOR,
    BOARD_SIZE,
    ColorRGB,
    GRID_COLOR,
    GRID_LINE_WIDTH,
    LEGAL_MOVE_MARKER_COLOR,
    LEGAL_MOVE_MARKER_RADIUS,
    LEGAL_MOVE_MARKER_WIDTH,
    RESULT_BACKGROUND_ALPHA,
    RESULT_BACKGROUND_COLOR,
    RESULT_FONT_SIZE,
    RESULT_TEXT_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SQUARE_SIZE,
    STONE_MARGIN,
    WHITE_STONE_COLOR,
)
from src.othello.game_enums import Cell
from src.othello.game_types import BoardPosition, LegalMove
from loguru import logger


class BoardRenderer:
    """pygameのSurfaceにオセロ盤面と石を描画します。

    描画処理をBoardから分離することで、将来的にCPU、通信対戦、
    テスト、別UIなどから同じ盤面ロジックを再利用しやすくします。
    """

    def __init__(self, surface: pygame.Surface) -> None:
        """描画クラスを初期化します。

        Args:
            surface: 描画先となるpygameのSurface。
        """
        self.surface: pygame.Surface = surface
        self.result_font: pygame.font.Font = pygame.font.Font(
            None,
            RESULT_FONT_SIZE,
        )

        logger.debug("BoardRendererを初期化しました。")

    def draw(
        self,
        board: Board,
        legal_moves: tuple[LegalMove, ...],
        result_text: str | None,
    ) -> None:
        """盤面、石、合法手マーカー、結果テキストを描画します。

        Args:
            board: 描画対象の盤面状態。
            legal_moves: 描画対象の合法手一覧。
            result_text: ゲーム結果の表示文字列。

        Returns:
            None.
        """
        self.surface.fill(BOARD_COLOR)
        self._draw_grid()
        self._draw_stones(board)
        self._draw_legal_moves(legal_moves)
        self._draw_result_text(result_text)

    def _draw_grid(self) -> None:
        """縦線と横線を描画して8x8のグリッドを作成します。

        Returns:
            None.
        """
        for index in range(BOARD_SIZE + 1):
            position: int = index * SQUARE_SIZE

            self._draw_vertical_line(position)
            self._draw_horizontal_line(position)

    def _draw_vertical_line(self, x: int) -> None:
        """縦方向のグリッド線を1本描画します。

        Args:
            x: 線を描画するX座標。

        Returns:
            None.
        """
        pygame.draw.line(
            self.surface,
            GRID_COLOR,
            (x, 0),
            (x, SCREEN_HEIGHT),
            width=GRID_LINE_WIDTH,
        )

    def _draw_horizontal_line(self, y: int) -> None:
        """横方向のグリッド線を1本描画します。

        Args:
            y: 線を描画するY座標。

        Returns:
            None.
        """
        pygame.draw.line(
            self.surface,
            GRID_COLOR,
            (0, y),
            (SCREEN_WIDTH, y),
            width=GRID_LINE_WIDTH,
        )

    def _draw_stones(self, board: Board) -> None:
        """空でないマスに石を描画します。

        Args:
            board: 石を描画する対象の盤面状態。

        Returns:
            None.
        """
        for position, cell in board.iter_cells():
            if cell is Cell.EMPTY:
                continue

            self._draw_stone(position, cell)

    def _draw_stone(self, pos: BoardPosition, cell: Cell) -> None:
        """指定されたマスに石を1つ描画します。

        Args:
            pos: 石を描画する盤面位置。
            cell: 石の色を表すCell値。Cell.EMPTYは渡さない想定。

        Returns:
            None.
        """
        color: ColorRGB = self._get_stone_color(cell)
        center: tuple[int, int] = self._get_square_center(pos)
        radius: int = SQUARE_SIZE // 2 - STONE_MARGIN

        pygame.draw.circle(
            self.surface,
            color,
            center,
            radius,
        )

    def _draw_legal_moves(self, legal_moves: tuple[LegalMove, ...]) -> None:
        """合法手の位置にマーカーを描画します。

        Args:
            legal_moves: 描画対象の合法手一覧。

        Returns:
            None.
        """
        for legal_move in legal_moves:
            self._draw_legal_move_marker(legal_move.position)

    def _draw_legal_move_marker(self, position: BoardPosition) -> None:
        """指定された位置に合法手マーカーを描画します。

        Args:
            position: 合法手マーカーを描画する盤面位置。

        Returns:
            None.
        """
        center: tuple[int, int] = self._get_square_center(position)

        pygame.draw.circle(
            self.surface,
            LEGAL_MOVE_MARKER_COLOR,
            center,
            LEGAL_MOVE_MARKER_RADIUS,
            width=LEGAL_MOVE_MARKER_WIDTH,
        )

    def _draw_result_text(self, result_text: str | None) -> None:
        """ゲーム結果テキストを中央に描画します。

        Args:
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
        self.surface.blit(overlay, (0, 0))

        text_surface: pygame.Surface = self.result_font.render(
            result_text,
            True,
            RESULT_TEXT_COLOR,
        )
        text_rect: pygame.Rect = text_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        self.surface.blit(text_surface, text_rect)

    def _get_stone_color(self, cell: Cell) -> ColorRGB:
        """Cell値を描画用のRGB色に変換します。

        Args:
            cell: 石の色を表すCell値。

        Returns:
            石の描画に使用するRGB色。

        Raises:
            ValueError: Cell.EMPTYが渡された場合。
        """
        match cell:
            case Cell.WHITE:
                return WHITE_STONE_COLOR

            case Cell.BLACK:
                return BLACK_STONE_COLOR

            case Cell.EMPTY:
                raise ValueError("Cell.EMPTYには石の色がありません。")

    def _get_square_center(self, pos: BoardPosition) -> tuple[int, int]:
        """指定されたマスの中心座標を計算します。

        Args:
            pos: 中心座標を計算する盤面位置。

        Returns:
            マス中心のX座標とY座標。
        """
        center_x: int = pos.col * SQUARE_SIZE + SQUARE_SIZE // 2
        center_y: int = pos.row * SQUARE_SIZE + SQUARE_SIZE // 2

        return center_x, center_y
