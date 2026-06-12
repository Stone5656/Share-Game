"""実盤面を変更せずに合法手を適用する処理を定義します。"""

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.core.game_types import LegalMove


def simulate_move(board: Board, player: Cell, legal_move: LegalMove) -> Board:
    """指定手を適用した仮想盤面を返します。

    Args:
        board: 複製元の盤面。
        player: 石を置くプレイヤー。
        legal_move: 仮想盤面へ適用する合法手。

    Returns:
        指定手を適用した新しい盤面。
    """
    simulated_board = Board()
    simulated_board.set_all_cells(
        tuple(
            tuple(board.cells[row][col] for col in range(len(board.cells[row])))
            for row in range(len(board.cells))
        )
    )
    simulated_board.set_cell(
        legal_move.position.row,
        legal_move.position.col,
        player,
    )

    for position in legal_move.flippable_positions:
        simulated_board.set_cell(position.row, position.col, player)

    return simulated_board
