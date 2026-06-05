"""ローカル人間同士の対戦モードを定義します。"""

import pygame
from loguru import logger

from src.othello.core.board import Board
from src.othello.core.game_engine import GameEngine
from src.othello.core.game_enums import Cell, GameStatus
from src.othello.core.game_types import BoardPosition, PlayerAction, PlayerContext
from src.othello.core.rules import LegalMoveScanner
from src.othello.players.local_human_player import LocalHumanPlayer
from src.othello.players.player_controller import PlayerController
from src.othello.ui.render import BoardRenderer


class LocalMode:
    """ローカル人間同士の対戦モードです。"""

    def __init__(self, surface: pygame.Surface) -> None:
        """ローカル対戦モードを初期化します。

        Args:
            surface: 描画先Surface。
        """
        self.board: Board = Board()
        self.engine: GameEngine = GameEngine(
            board=self.board,
            current_player=Cell.BLACK,
            legal_move_scanner=LegalMoveScanner(),
        )
        self.renderer: BoardRenderer = BoardRenderer(surface)
        self.players: dict[Cell, PlayerController] = {
            Cell.BLACK: LocalHumanPlayer(Cell.BLACK),
            Cell.WHITE: LocalHumanPlayer(Cell.WHITE),
        }

        logger.info("Local Player vs Playerを開始しました。")

    def handle_event(self, event: pygame.event.Event) -> None:
        """ローカル対戦の入力イベントを処理します。

        Args:
            event: pygameイベント。

        Returns:
            None.
        """
        if self.engine.status is GameStatus.GAME_OVER:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.players[self.engine.current_player].handle_event(event)

    def update(self) -> None:
        """ローカル対戦のゲーム状態を更新します。

        Returns:
            None.
        """
        if self.engine.status is GameStatus.GAME_OVER:
            return

        if not self.engine.legal_moves:
            self._apply_local_pass()
            return

        current_player: PlayerController = self.players[self.engine.current_player]
        context: PlayerContext = PlayerContext(
            current_player=self.engine.current_player,
            legal_moves=self.engine.legal_moves,
        )
        action: PlayerAction | None = current_player.select_action(context)

        if action is None or action.position is None:
            return

        if self.engine.apply_move(action.position):
            self._log_game_over_if_needed()

    def draw(self) -> None:
        """ローカル対戦画面を描画します。

        Returns:
            None.
        """
        self.renderer.draw(
            self.board,
            self._get_legal_move_positions(),
            self.engine.get_result_text(),
        )

    def close(self) -> None:
        """ローカル対戦モードを終了します。

        Returns:
            None.
        """
        logger.info("LocalModeを終了しました。")

    def _apply_local_pass(self) -> None:
        """現在手番のローカルパスを適用します。

        Returns:
            None.
        """
        player: Cell = self.engine.current_player

        if self.engine.apply_pass(player):
            logger.info("パス: player={}", player.name)
            self._log_game_over_if_needed()

    def _get_legal_move_positions(self) -> tuple[BoardPosition, ...]:
        """描画用の合法手位置一覧を返します。

        Returns:
            合法手位置のタプル。
        """
        return tuple(legal_move.position for legal_move in self.engine.legal_moves)

    def _log_game_over_if_needed(self) -> None:
        """ゲーム終了時にログ出力します。

        Returns:
            None.
        """
        if self.engine.status is GameStatus.GAME_OVER:
            logger.info("ゲーム終了: result={}", self.engine.get_result_text())
