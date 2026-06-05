"""オセロアプリケーション全体で使用する定数を定義します。"""

from pathlib import Path
from typing import Final

from src.othello.core.game_enums import Cell
from src.othello.core.game_types import BoardPosition, Direction

ColorRGB = tuple[int, int, int]

BOARD_SIZE: Final[int] = 8
SQUARE_SIZE: Final[int] = 80

SCREEN_WIDTH: Final[int] = BOARD_SIZE * SQUARE_SIZE
SCREEN_HEIGHT: Final[int] = BOARD_SIZE * SQUARE_SIZE

FPS: Final[int] = 60

DEFAULT_HOST: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 5555
SERVER_COLOR: Final[Cell] = Cell.WHITE
CLIENT_COLOR: Final[Cell] = Cell.BLACK

BOARD_COLOR: Final[ColorRGB] = (34, 139, 34)
GRID_COLOR: Final[ColorRGB] = (0, 0, 0)
WHITE_STONE_COLOR: Final[ColorRGB] = (240, 240, 240)
BLACK_STONE_COLOR: Final[ColorRGB] = (20, 20, 20)
LEGAL_MOVE_MARKER_COLOR: Final[ColorRGB] = (200, 0, 0)
RESULT_TEXT_COLOR: Final[ColorRGB] = (255, 255, 255)
RESULT_BACKGROUND_COLOR: Final[ColorRGB] = (0, 0, 0)

GRID_LINE_WIDTH: Final[int] = 2
STONE_MARGIN: Final[int] = 8
LEGAL_MOVE_MARKER_RADIUS: Final[int] = 20
LEGAL_MOVE_MARKER_WIDTH: Final[int] = 5
RESULT_FONT_SIZE: Final[int] = 72
RESULT_BACKGROUND_ALPHA: Final[int] = 180

WINDOW_TITLE: Final[str] = "Othello"
LOG_DIR: Final[Path] = Path("logs")
LOG_FILE_PATH: Final[Path] = LOG_DIR / "othello.log"

INITIAL_STONES: Final[tuple[tuple[BoardPosition, Cell], ...]] = (
    (BoardPosition(3, 3), Cell.WHITE),
    (BoardPosition(3, 4), Cell.BLACK),
    (BoardPosition(4, 3), Cell.BLACK),
    (BoardPosition(4, 4), Cell.WHITE),
)

DIRECTIONS: Final[tuple[Direction, ...]] = (
    Direction(-1, -1),
    Direction(-1, 0),
    Direction(-1, 1),
    Direction(0, -1),
    Direction(0, 1),
    Direction(1, -1),
    Direction(1, 0),
    Direction(1, 1),
)
