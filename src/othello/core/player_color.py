"""プレイヤー色に関する補助処理を定義します。"""

from src.othello.core.game_enums import Cell


def get_opponent(current_player: Cell) -> Cell:
    """現在の手番プレイヤーに対する相手の石色を返します。

    Args:
        current_player: 現在の手番プレイヤー。

    Returns:
        相手プレイヤーのCell値。

    Raises:
        ValueError: Cell.EMPTYが渡された場合。
    """
    match current_player:
        case Cell.BLACK:
            return Cell.WHITE

        case Cell.WHITE:
            return Cell.BLACK

        case Cell.EMPTY:
            raise ValueError("Cell.EMPTYはプレイヤーとして扱えません。")
