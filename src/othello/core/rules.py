"""オセロの合法手判定ロジックを定義します。"""

from loguru import logger

from src.othello.constants import BOARD_SIZE, DIRECTIONS
from src.othello.core.board import Board
from src.othello.core.game_enums import Cell
from src.othello.core.game_types import BoardPosition, Direction, LegalMove


class LegalMoveScanner:
    """現在の手番プレイヤーが置ける位置を走査します。"""

    def find_legal_moves(
        self,
        board: Board,
        current_player: Cell,
    ) -> tuple[LegalMove, ...]:
        """現在の手番プレイヤーの合法手一覧を返します。

        Args:
            board: 走査対象の盤面。
            current_player: 現在の手番プレイヤー。

        Returns:
            合法手のタプル。
        """
        logger.debug(
            "合法手走査を開始します: current_player={}",
            current_player.name,
        )

        legal_moves: list[LegalMove] = []

        for position, _cell in board.iter_cells():
            legal_move: LegalMove | None = self._find_legal_move_at(
                board,
                position,
                current_player,
            )

            if legal_move is None:
                continue

            legal_moves.append(legal_move)

        logger.info(
            "合法手走査が完了しました: current_player={}, legal_move_count={}",
            current_player.name,
            len(legal_moves),
        )

        return tuple(legal_moves)

    def _find_legal_move_at(
        self,
        board: Board,
        position: BoardPosition,
        current_player: Cell,
    ) -> LegalMove | None:
        """指定された位置が合法手であれば合法手情報を返します。

        Args:
            board: 走査対象の盤面。
            position: 走査対象の盤面位置。
            current_player: 現在の手番プレイヤー。

        Returns:
            合法手であればLegalMove。合法手でなければNone。
        """
        if board.get_cell(position) is not Cell.EMPTY:
            return None

        flippable_positions: list[BoardPosition] = []

        for direction in DIRECTIONS:
            flippable_positions.extend(
                self._find_flippable_positions(
                    board,
                    position,
                    direction,
                    current_player,
                )
            )

        if not flippable_positions:
            return None

        logger.debug(
            "合法手を検出しました: row={}, col={}, flip_count={}",
            position.row,
            position.col,
            len(flippable_positions),
        )

        return LegalMove(
            position=position,
            flippable_positions=tuple(flippable_positions),
        )

    def _find_flippable_positions(
        self,
        board: Board,
        start_position: BoardPosition,
        direction: Direction,
        current_player: Cell,
    ) -> tuple[BoardPosition, ...]:
        """指定方向に反転可能な相手石の位置一覧を返します。

        Args:
            board: 走査対象の盤面。
            start_position: 石を置く候補位置。
            direction: 走査方向。
            current_player: 現在の手番プレイヤー。

        Returns:
            反転可能な相手石の位置タプル。
        """
        opponent: Cell = self._get_opponent(current_player)
        current_row: int = start_position.row + direction.row_delta
        current_col: int = start_position.col + direction.col_delta
        candidates: list[BoardPosition] = []

        while self._is_inside_board(BoardPosition(current_row, current_col)):
            cell: Cell = board.get_cell(BoardPosition(current_row, current_col))

            if cell is opponent:
                candidates.append(BoardPosition(current_row, current_col))
                current_row += direction.row_delta
                current_col += direction.col_delta
                continue

            if cell is current_player:
                return tuple(candidates) if candidates else tuple()

            return tuple()

        return tuple()

    def _is_inside_board(self, position: BoardPosition) -> bool:
        """指定された位置が盤面内であるかを返します。

        Args:
            position: 確認する盤面位置。


        Returns:
            指定された位置が盤面内であればTrue。
        """
        return 0 <= position.row < BOARD_SIZE and 0 <= position.col < BOARD_SIZE

    def _get_opponent(self, current_player: Cell) -> Cell:
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
