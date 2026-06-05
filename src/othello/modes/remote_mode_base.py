"""Remote対戦モードの共通制御を定義します。"""

import pygame
from loguru import logger

from src.othello.core.board import Board
from src.othello.core.game_engine import GameEngine
from src.othello.core.game_enums import Cell, GameStatus
from src.othello.core.game_types import BoardPosition, PlayerAction, PlayerContext
from src.othello.core.rules import LegalMoveScanner
from src.othello.modes.remote_message_handler import RemoteMessageHandler
from src.othello.network.protocol import (
    OthelloMessage,
    create_hit_message,
    create_pass_message,
)
from src.othello.players.player_controller import PlayerController
from src.othello.players.remote_human_player import RemoteHumanPlayer
from src.othello.ui.render import BoardRenderer


class RemoteModeBase:
    """TCP Remote対戦モードの共通処理を提供します。"""

    def __init__(
        self,
        surface: pygame.Surface,
        local_player: PlayerController,
        remote_color: Cell,
    ) -> None:
        """Remote対戦モードの共通状態を初期化します。

        Args:
            surface: 描画先Surface。
            local_player: 自分側のプレイヤー。
            remote_color: 相手側プレイヤーの石色。
        """
        self.board: Board = Board()
        self.engine: GameEngine = GameEngine(
            board=self.board,
            current_player=Cell.BLACK,
            legal_move_scanner=LegalMoveScanner(),
        )
        self.renderer: BoardRenderer = BoardRenderer(surface)
        self.local_player: PlayerController = local_player
        self.remote_player: RemoteHumanPlayer = RemoteHumanPlayer(remote_color)
        self.remote_message_handler: RemoteMessageHandler = RemoteMessageHandler(
            engine=self.engine,
            remote_player=self.remote_player,
        )
        self.game_ready: bool = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """ローカル入力イベントを処理します。

        Args:
            event: pygameイベント。

        Returns:
            None.
        """
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if not self._can_local_player_act():
            self._log_input_block_reason()
            return

        self.local_player.handle_event(event)

    def update(self) -> None:
        """通信とゲーム状態を更新します。

        Returns:
            None.
        """
        self._process_network_messages()

        if self.engine.status is GameStatus.GAME_OVER or not self._is_network_ready():
            return

        if self.engine.current_player is not self.local_player.color:
            return

        if not self.engine.legal_moves:
            self._send_and_apply_pass()
            return

        context: PlayerContext = self._create_player_context()
        action: PlayerAction | None = self.local_player.select_action(context)

        if action is None:
            return

        if action.is_pass:
            self._send_and_apply_pass()
            return

        if action.position is None:
            return

        if self.engine.apply_move(action.position):
            self._send_message(create_hit_message(action.position))
            logger.info("HIT送信: position={}", action.position)
            self._log_game_over_if_needed()

    def draw(self) -> None:
        """Remote対戦画面を描画します。

        Returns:
            None.
        """
        self.renderer.draw(
            self.board,
            self._get_legal_move_positions(),
            self.engine.get_result_text(),
        )

    def _apply_remote_hit(self, message: OthelloMessage) -> None:
        """受信したHITを盤面へ反映します。

        Args:
            message: 受信したHITメッセージ。

        Returns:
            None.
        """
        if self.remote_message_handler.apply_hit(message):
            self._log_game_over_if_needed()

    def _apply_remote_pass(self) -> None:
        """受信したPASSを盤面へ反映します。

        Returns:
            None.
        """
        if self.remote_message_handler.apply_pass():
            self._log_game_over_if_needed()

    def _send_and_apply_pass(self) -> None:
        """自分のPASSを送信して盤面へ反映します。

        Returns:
            None.
        """
        player: Cell = self.local_player.color

        if self.engine.apply_pass(player):
            self._send_message(create_pass_message())
            logger.info("PASS送信: player={}", player.name)
            self._log_game_over_if_needed()

    def _can_local_player_act(self) -> bool:
        """ローカルプレイヤーが入力できる状態かを返します。

        Returns:
            入力可能であればTrue。
        """
        return (
            self._is_network_ready()
            and self.engine.status is not GameStatus.GAME_OVER
            and self.engine.current_player is self.local_player.color
            and bool(self.engine.legal_moves)
        )

    def _is_network_ready(self) -> bool:
        """対局入力を始められる通信状態かを返します。

        Returns:
            対局入力を始められる通信状態であればTrue。
        """
        return self.game_ready

    def _log_input_block_reason(self) -> None:
        """ローカルクリックが拒否された理由をログ出力します。

        Returns:
            None.
        """
        if not self._is_network_ready():
            logger.info("通信準備前のクリックを無視しました。")
            return

        if self.engine.status is GameStatus.GAME_OVER:
            logger.info("ゲーム終了後のクリックを無視しました。")
            return

        if self.engine.current_player is not self.local_player.color:
            logger.info(
                "手番ではないクリック: local_color={}, current_player={}",
                self.local_player.color.name,
                self.engine.current_player.name,
            )
            return

        if not self.engine.legal_moves:
            logger.info(
                "合法手がないためクリックを無視しました: local_color={}",
                self.local_player.color.name,
            )

    def _create_player_context(self) -> PlayerContext:
        """現在のGameEngine状態からPlayerContextを作成します。

        Returns:
            PlayerContext。
        """
        return PlayerContext(
            current_player=self.engine.current_player,
            legal_moves=self.engine.legal_moves,
        )

    def _get_legal_move_positions(self) -> tuple[BoardPosition, ...]:
        """描画用の合法手位置一覧を返します。

        Returns:
            ローカル手番の合法手位置タプル。相手手番では空タプル。
        """
        if self.engine.current_player is not self.local_player.color:
            return tuple()

        return tuple(legal_move.position for legal_move in self.engine.legal_moves)

    def _log_game_over_if_needed(self) -> None:
        """ゲーム終了時にログ出力します。

        Returns:
            None.
        """
        if self.engine.status is GameStatus.GAME_OVER:
            logger.info("ゲーム終了: result={}", self.engine.get_result_text())

    def _process_network_messages(self) -> None:
        """受信済みネットワークメッセージを処理します。"""
        raise NotImplementedError

    def _send_message(self, message: OthelloMessage) -> None:
        """ネットワークメッセージを送信します。"""
        raise NotImplementedError
