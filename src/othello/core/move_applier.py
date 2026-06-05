"""合法手の石配置と反転処理を定義します。"""

from loguru import logger

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.core.game_types import LegalMove


def place_stone(board: Board, legal_move: LegalMove, current_player: Cell) -> None:
    """合法手の位置に現在の手番プレイヤーの石を置きます。

    Args:
        board: 更新対象の盤面。
        legal_move: 適用する合法手。
        current_player: 現在の手番プレイヤー。

    Returns:
        None.
    """
    board.set_cell(
        legal_move.position.row,
        legal_move.position.col,
        current_player,
    )
    logger.info(
        "石を配置しました: player={}, position={}",
        current_player.name,
        legal_move.position,
    )


def flip_stones(board: Board, legal_move: LegalMove, current_player: Cell) -> None:
    """合法手に含まれる反転対象の石を裏返します。

    Args:
        board: 更新対象の盤面。
        legal_move: 適用する合法手。
        current_player: 現在の手番プレイヤー。

    Returns:
        None.
    """
    for position in legal_move.flippable_positions:
        board.set_cell(position.row, position.col, current_player)

    logger.info(
        "石を反転しました: player={}, flip_count={}",
        current_player.name,
        len(legal_move.flippable_positions),
    )
