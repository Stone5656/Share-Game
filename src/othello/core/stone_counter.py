"""盤面上の石数カウント処理を定義します。"""

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell


def count_stones(board: Board) -> tuple[int, int]:
    """盤面上の黒石と白石の数を返します。

    Args:
        board: 集計対象の盤面。

    Returns:
        黒石数と白石数のタプル。
    """
    black_count: int = 0
    white_count: int = 0

    for _position, cell in board.iter_cells():
        if cell is Cell.BLACK:
            black_count += 1
            continue

        if cell is Cell.WHITE:
            white_count += 1

    return black_count, white_count
