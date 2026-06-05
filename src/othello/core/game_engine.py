"""オセロのゲーム進行と盤面更新を管理します。"""

from dataclasses import dataclass, field

from loguru import logger

from src.othello.core.board import Board
from src.othello.core.game_enums import Cell, GameStatus
from src.othello.core.game_result import create_result_text, determine_winner
from src.othello.core.game_types import BoardPosition, LegalMove
from src.othello.core.move_applier import flip_stones, place_stone
from src.othello.core.player_color import get_opponent
from src.othello.core.rules import LegalMoveScanner
from src.othello.core.stone_counter import count_stones


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
        self._finish_if_both_players_have_no_moves()

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

        place_stone(self.board, legal_move, self.current_player)
        flip_stones(self.board, legal_move, self.current_player)
        self._advance_turn_after_move()

        return True

    def apply_pass(self, player: Cell) -> bool:
        """指定プレイヤーのパスを適用します。

        Args:
            player: パスするプレイヤー。

        Returns:
            パスが適用できた場合はTrue。
        """
        if self.status is GameStatus.GAME_OVER:
            logger.warning("ゲーム終了後のパスは無視します: player={}", player.name)
            return False

        if player is not self.current_player:
            logger.warning(
                "現在手番ではないためパスできません: player={}, current_player={}",
                player.name,
                self.current_player.name,
            )
            return False

        if self.legal_moves:
            logger.warning(
                "合法手があるためパスできません: player={}, legal_move_count={}",
                player.name,
                len(self.legal_moves),
            )
            return False

        logger.info("パスを適用しました: player={}", player.name)
        self.current_player = get_opponent(self.current_player)
        self.legal_moves = self.find_legal_moves()

        if self.legal_moves:
            logger.info(
                "パス後の手番を設定しました: current_player={}, legal_move_count={}",
                self.current_player.name,
                len(self.legal_moves),
            )
            return True

        self._finish_game()
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

    def _advance_turn_after_move(self) -> None:
        """次の手番へ進めます。

        次のプレイヤーに合法手がなければ、明示PASSを待てる状態にします。
        両者とも合法手がなければゲーム終了にします。

        Returns:
            None.
        """
        self.current_player = get_opponent(self.current_player)
        self.legal_moves = self.find_legal_moves()

        if self.legal_moves:
            logger.info(
                "手番を交代しました: current_player={}, legal_move_count={}",
                self.current_player.name,
                len(self.legal_moves),
            )
            return

        if self._opponent_has_legal_moves():
            logger.info(
                "合法手がないためパス待ちです: current_player={}",
                self.current_player.name,
            )
            return

        self._finish_game()

    def _finish_if_both_players_have_no_moves(self) -> None:
        """両者とも合法手がない場合にゲーム終了へ進めます。

        Returns:
            None.
        """
        if self.legal_moves:
            return

        if self._opponent_has_legal_moves():
            return

        self._finish_game()

    def _finish_game(self) -> None:
        """ゲーム終了状態へ進め、勝者を決定します。

        Returns:
            None.
        """
        self.status = GameStatus.GAME_OVER
        self.black_count, self.white_count = count_stones(self.board)
        self.winner = determine_winner(self.black_count, self.white_count)
        logger.info(
            "両者とも合法手がないためゲーム終了です: "
            "black_count={}, white_count={}, result={}",
            self.black_count,
            self.white_count,
            self.get_result_text(),
        )

    def _opponent_has_legal_moves(self) -> bool:
        """相手プレイヤーに合法手があるかを返します。

        Returns:
            相手プレイヤーに合法手があればTrue。
        """
        original_player: Cell = self.current_player
        self.current_player = get_opponent(self.current_player)
        opponent_legal_moves: tuple[LegalMove, ...] = self.find_legal_moves()
        self.current_player = original_player
        self.legal_moves = self.find_legal_moves()

        return bool(opponent_legal_moves)

    def get_result_text(self) -> str | None:
        """ゲーム結果の表示文字列を返します。

        Returns:
            ゲーム終了時は結果文字列。ゲーム中はNone。
        """
        return create_result_text(self.status, self.winner)
