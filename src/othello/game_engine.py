"""オセロのゲーム進行と盤面更新を管理します。"""

from dataclasses import dataclass, field

from loguru import logger

from src.othello.board import Board
from src.othello.game_enums import Cell, GameStatus
from src.othello.game_types import BoardPosition, LegalMove
from src.othello.rules import LegalMoveScanner


@dataclass
class GameEngine:
    """オセロのゲーム進行と盤面更新を管理します。

    石を置く、裏返す、ターン交代、パス、ゲーム終了判定を担当します。
    pygameイベントや描画は扱いません。
    """

    board: Board
    current_player: Cell
    legal_move_scanner: LegalMoveScanner
    status: GameStatus = field(default=GameStatus.PLAYING, init=False)
    legal_moves: tuple[LegalMove, ...] = field(default_factory=tuple, init=False)
    winner: Cell | None = field(default=None, init=False)
    black_count: int = field(default=0, init=False)
    white_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """初期化後のゲーム状態を設定します。"""
        self.legal_moves = self.find_legal_moves()
        self._pass_or_finish_if_needed()

        logger.info(
            "ゲームエンジンを初期化しました: current_player={}, legal_move_count={}",
            self.current_player.name,
            len(self.legal_moves),
        )

    def find_legal_moves(self) -> tuple[LegalMove, ...]:
        """現在の手番プレイヤーの合法手を返します。

        Returns:
            合法手のタプル。
        """
        return self.legal_move_scanner.find_legal_moves(
            self.board,
            self.current_player,
        )

    def apply_move(self, position: BoardPosition) -> bool:
        """指定位置に石を置き、反転処理とターン交代を行います。

        Args:
            position: 石を置く位置。

        Returns:
            着手が成功した場合はTrue。
        """
        if self.status is GameStatus.GAME_OVER:
            logger.warning("ゲーム終了後の着手は無視します: position={}", position)
            return False

        legal_move: LegalMove | None = self._find_matching_legal_move(position)

        if legal_move is None:
            logger.warning("非合法手のため着手できません: position={}", position)
            return False

        self._place_stone(legal_move)
        self._flip_stones(legal_move)
        self._advance_turn()

        return True

    def _find_matching_legal_move(self, position: BoardPosition) -> LegalMove | None:
        """指定位置に一致する合法手を返します。

        Args:
            position: 探索対象の盤面位置。

        Returns:
            一致する合法手があればLegalMove、なければNone。
        """
        for legal_move in self.legal_moves:
            if legal_move.position == position:
                return legal_move

        return None

    def _place_stone(self, legal_move: LegalMove) -> None:
        """合法手の位置に現在の手番プレイヤーの石を置きます。

        Args:
            legal_move: 適用する合法手。

        Returns:
            None.
        """
        self.board.set_cell(
            legal_move.position.row,
            legal_move.position.col,
            self.current_player,
        )

        logger.info(
            "石を配置しました: player={}, position={}",
            self.current_player.name,
            legal_move.position,
        )

    def _flip_stones(self, legal_move: LegalMove) -> None:
        """合法手に含まれる反転対象の石を裏返します。

        Args:
            legal_move: 適用する合法手。

        Returns:
            None.
        """
        for position in legal_move.flippable_positions:
            self.board.set_cell(position.row, position.col, self.current_player)

        logger.info(
            "石を反転しました: player={}, flip_count={}",
            self.current_player.name,
            len(legal_move.flippable_positions),
        )

    def _advance_turn(self) -> None:
        """次の手番へ進めます。

        次のプレイヤーに合法手がなければパスします。
        両者とも合法手がなければゲーム終了にします。

        Returns:
            None.
        """
        self.current_player = self._get_opponent(self.current_player)
        self.legal_moves = self.find_legal_moves()

        if self.legal_moves:
            logger.info(
                "手番を交代しました: current_player={}, legal_move_count={}",
                self.current_player.name,
                len(self.legal_moves),
            )
            return

        self._pass_or_finish_if_needed()

    def _pass_or_finish_if_needed(self) -> None:
        """合法手がない場合にパスまたはゲーム終了を処理します。

        Returns:
            None.
        """
        if self.legal_moves:
            return

        logger.info("合法手がないためパスします: player={}", self.current_player.name)

        self.current_player = self._get_opponent(self.current_player)
        self.legal_moves = self.find_legal_moves()

        if self.legal_moves:
            logger.info(
                "パス後の手番を設定しました: current_player={}, legal_move_count={}",
                self.current_player.name,
                len(self.legal_moves),
            )
            return

        self.status = GameStatus.GAME_OVER
        self._determine_winner()
        logger.info(
            "両者とも合法手がないためゲーム終了です: black_count={}, white_count={}, result={}",
            self.black_count,
            self.white_count,
            self.get_result_text(),
        )

    def get_result_text(self) -> str | None:
        """ゲーム結果の表示文字列を返します。

        Returns:
            ゲーム終了時は結果文字列。ゲーム中はNone。
        """
        if self.status is not GameStatus.GAME_OVER:
            return None

        if self.winner is Cell.BLACK:
            return "Black Win"

        if self.winner is Cell.WHITE:
            return "White Win"

        return "Draw"

    def _determine_winner(self) -> None:
        """盤面の石数から勝者を判定します。

        Returns:
            None.
        """
        self.black_count, self.white_count = self._count_stones()

        if self.black_count > self.white_count:
            self.winner = Cell.BLACK
            return

        if self.white_count > self.black_count:
            self.winner = Cell.WHITE
            return

        self.winner = None

    def _count_stones(self) -> tuple[int, int]:
        """盤面上の黒石と白石の数を返します。

        Returns:
            黒石数と白石数のタプル。
        """
        black_count: int = 0
        white_count: int = 0

        for _position, cell in self.board.iter_cells():
            if cell is Cell.BLACK:
                black_count += 1
                continue

            if cell is Cell.WHITE:
                white_count += 1

        return black_count, white_count

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
