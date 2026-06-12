"""盤面状態を状態価値テーブル用の文字列へ変換します。"""

from typing import Final

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell

CELL_SYMBOLS: Final[dict[Cell, str]] = {
    Cell.EMPTY: "E",
    Cell.BLACK: "B",
    Cell.WHITE: "W",
}


class BoardStateKeyFactory:
    """盤面状態を学習テーブル用のキーへ変換します。"""

    def create_key(self, board: Board, current_player: Cell) -> str:
        """盤面と評価視点のプレイヤーから状態キーを作成します。

        Args:
            board: キーへ変換する盤面。
            current_player: 状態価値を評価するプレイヤー。

        Returns:
            プレイヤー色と盤面文字列を結合した状態キー。

        Raises:
            ValueError: Cell.EMPTYが指定された場合。
        """
        if current_player is Cell.EMPTY:
            raise ValueError("Cell.EMPTYは状態キーのプレイヤーに指定できません。")

        rows = ("".join(CELL_SYMBOLS[cell] for cell in row) for row in board.cells)
        return f"{current_player.name}:{'/'.join(rows)}"
