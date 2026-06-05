"""オセロの盤面状態を管理します。"""

from collections.abc import Iterator

from loguru import logger

from src.othello.constants import BOARD_SIZE, INITIAL_STONES
from src.othello.core.game_enums import Cell
from src.othello.core.game_types import BoardPosition


class Board:
    """オセロの盤面状態を管理します。

    このクラスはpygame、描画、マウス入力、CPU、通信処理を扱いません。
    8x8のマス状態だけを保持します。

    Attributes:
        cells: 8x8の盤面状態を表す二次元リスト。
    """

    def __init__(self) -> None:
        """空の盤面を作成し、オセロの初期配置を設定します。"""
        self.cells: list[list[Cell]] = self._create_empty_cells()
        self._setup_initial_position()

        logger.debug("盤面を初期化しました。")

    def _create_empty_cells(self) -> list[list[Cell]]:
        """空の8x8盤面を作成します。

        Returns:
            すべてのマスがCell.EMPTYで埋められた二次元リスト。
        """
        return [[Cell.EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def _setup_initial_position(self) -> None:
        """オセロの初期配置として中央4マスに石を配置します。

        Returns:
            None.
        """
        for pos, cell in INITIAL_STONES:
            self.cells[pos.row][pos.col] = cell
            logger.debug(
                "初期石を配置しました: row={}, col={}, cell={}",
                pos.row,
                pos.col,
                cell.name,
            )

    def get_cell(self, pos: BoardPosition) -> Cell:
        """指定されたマスの状態を返します。

        Args:
            pos: 盤面の位置。

        Returns:
            指定された位置のCell値。
        """
        return self.cells[pos.row][pos.col]

    def set_cell(self, row: int, col: int, cell: Cell) -> None:
        """指定されたマスにCell値を設定します。

        Args:
            row: 盤面の行インデックス。
            col: 盤面の列インデックス。
            cell: 設定するCell値。

        Returns:
            None.
        """
        self.cells[row][col] = cell

    def set_all_cells(self, cells: tuple[tuple[Cell, ...], ...]) -> None:
        """盤面全体を指定されたCell配列で上書きします。

        Args:
            cells: 新しい盤面状態。

        Returns:
            None.
        """
        for row_index, row in enumerate(cells):
            for col_index, cell in enumerate(row):
                self.set_cell(row_index, col_index, cell)

    def iter_cells(self) -> Iterator[tuple[BoardPosition, Cell]]:
        """盤面上のすべてのマスを位置情報付きで反復します。

        Yields:
            BoardPosition、Cell値のタプル。
        """
        for row, line in enumerate(self.cells):
            for col, cell in enumerate(line):
                yield BoardPosition(row, col), cell
