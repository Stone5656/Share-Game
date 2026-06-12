"""盤面から線形評価用の特徴量を抽出します。"""

from dataclasses import dataclass
from typing import Final

from src.othello.constants import BOARD_SIZE
from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.core.player_color import get_opponent
from src.othello.core.rules import LegalMoveScanner
from src.othello.players.cpu.weighted_board_strategy import POSITION_WEIGHTS

FEATURE_COUNT: Final[int] = 6


@dataclass(frozen=True)
class BoardFeatures:
    """盤面評価に使用する特徴量を表します。

    Attributes:
        values: 特徴量ベクトル。
    """

    values: tuple[float, ...]


class FeatureExtractor:
    """盤面状態から強化学習用の特徴量を抽出します。"""

    def __init__(self) -> None:
        """合法手走査器を初期化します。"""
        self._legal_move_scanner = LegalMoveScanner()

    def extract(self, board: Board, player: Cell) -> BoardFeatures:
        """指定プレイヤー視点の特徴量を抽出します。

        Args:
            board: 評価対象の盤面。
            player: 評価視点のプレイヤー。

        Returns:
            特徴量ベクトル。
        """
        opponent = get_opponent(player)
        player_count = 0
        opponent_count = 0
        player_corners = 0
        opponent_corners = 0
        player_edges = 0
        opponent_edges = 0
        weighted_score = 0

        for position, cell in board.iter_cells():
            if cell is Cell.EMPTY:
                continue

            sign = 1 if cell is player else -1
            player_count += int(cell is player)
            opponent_count += int(cell is opponent)
            weighted_score += sign * POSITION_WEIGHTS[position.row][position.col]

            if self._is_corner(position.row, position.col):
                player_corners += int(cell is player)
                opponent_corners += int(cell is opponent)
            elif self._is_edge(position.row, position.col):
                player_edges += int(cell is player)
                opponent_edges += int(cell is opponent)

        player_moves = self._legal_move_scanner.find_legal_moves(board, player)
        opponent_moves = self._legal_move_scanner.find_legal_moves(board, opponent)
        return BoardFeatures(
            values=(
                1.0,
                (player_count - opponent_count) / 64.0,
                (len(player_moves) - len(opponent_moves)) / 32.0,
                (player_corners - opponent_corners) / 4.0,
                (player_edges - opponent_edges) / 24.0,
                weighted_score / 400.0,
            )
        )

    def _is_corner(self, row: int, col: int) -> bool:
        """指定座標が角かを返します。"""
        last = BOARD_SIZE - 1
        return row in (0, last) and col in (0, last)

    def _is_edge(self, row: int, col: int) -> bool:
        """指定座標が角以外の辺かを返します。"""
        last = BOARD_SIZE - 1
        return row in (0, last) or col in (0, last)
