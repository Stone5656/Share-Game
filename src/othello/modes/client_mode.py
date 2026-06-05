"""TCPクライアントとして動作する黒側プレイヤーのモードを定義します。"""

from queue import Empty

from loguru import logger
import pygame

from src.othello.config import NetworkConfig
from src.othello.constants import CLIENT_COLOR
from src.othello.core.board import Board
from src.othello.core.game_engine import GameEngine
from src.othello.core.game_enums import Cell, GameStatus
from src.othello.core.game_types import BoardPosition, PlayerAction, PlayerContext
from src.othello.core.rules import LegalMoveScanner
from src.othello.network.client import OthelloTcpClient
from src.othello.network.protocol import (
    OthelloCommand,
    OthelloMessage,
    create_hit_message,
    create_pass_message,
)
from src.othello.players.local_human_player import LocalHumanPlayer
from src.othello.players.remote_human_player import RemoteHumanPlayer
from src.othello.ui.render import BoardRenderer


class ClientMode:
    """TCPクライアントとして動作する黒側プレイヤーのモードです。"""

    def __init__(self, surface: pygame.Surface, network_config: NetworkConfig) -> None:
        """クライアントモードを初期化します。

        Args:
            surface: 描画先Surface。
            network_config: TCP通信設定。
        """
        self.board: Board = Board()
        self.engine: GameEngine = GameEngine(
            board=self.board,
            current_player=Cell.BLACK,
            legal_move_scanner=LegalMoveScanner(),
        )
        self.renderer: BoardRenderer = BoardRenderer(surface)
        self.local_player: LocalHumanPlayer = LocalHumanPlayer(CLIENT_COLOR)
        self.remote_player: RemoteHumanPlayer = RemoteHumanPlayer(Cell.WHITE)
        self.client: OthelloTcpClient = OthelloTcpClient(network_config)
        self.game_ready: bool = False

        self.client.start()
        logger.info("Client / Blackを開始しました。")

    def handle_event(self, event: pygame.event.Event) -> None:
        """クライアントモードの入力イベントを処理します。

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
        """クライアントモードの通信とゲーム状態を更新します。

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

        context: PlayerContext = PlayerContext(
            current_player=self.engine.current_player,
            legal_moves=self.engine.legal_moves,
        )
        action: PlayerAction | None = self.local_player.select_action(context)

        if action is None or action.position is None:
            return

        if self.engine.apply_move(action.position):
            self.client.send_message(create_hit_message(action.position))
            logger.info("HIT送信: position={}", action.position)
            self._log_game_over_if_needed()

    def draw(self) -> None:
        """クライアントモード画面を描画します。

        Returns:
            None.
        """
        self.renderer.draw(
            self.board,
            self._get_legal_move_positions(),
            self.engine.get_result_text(),
        )

    def close(self) -> None:
        """クライアントモードを終了します。

        Returns:
            None.
        """
        self.client.close()
        logger.info("ClientModeを終了しました。")

    def _process_network_messages(self) -> None:
        """TCPクライアントの受信Queueを処理します。

        Returns:
            None.
        """
        while True:
            try:
                message: OthelloMessage = self.client.incoming_queue.get_nowait()
            except Empty:
                return

            match message.command:
                case OthelloCommand.OK:
                    self.game_ready = True
                    logger.info("OK受信によりゲーム可能状態になりました。")

                case OthelloCommand.HIT:
                    logger.info("HIT受信: message={}", message)
                    if not self._is_network_ready():
                        logger.warning("ゲーム準備前のHITを破棄しました: message={}", message)
                        continue

                    self._apply_remote_hit(message)

                case OthelloCommand.PASS:
                    logger.info("PASS受信: message={}", message)
                    if not self._is_network_ready():
                        logger.warning("ゲーム準備前のPASSを破棄しました: message={}", message)
                        continue

                    self._apply_remote_pass()

                case OthelloCommand.START:
                    logger.info("START受信: message={}", message)

    def _apply_remote_hit(self, message: OthelloMessage) -> None:
        """受信したHITを検証し、盤面へ反映します。

        Args:
            message: 受信したHITメッセージ。

        Returns:
            None.
        """
        if message.row is None or message.col is None:
            logger.warning("非合法HIT受信: rowまたはcolがありません。")
            return

        position: BoardPosition = BoardPosition(row=message.row, col=message.col)
        self.remote_player.receive_hit(position)
        context: PlayerContext = PlayerContext(
            current_player=self.engine.current_player,
            legal_moves=self.engine.legal_moves,
        )
        action: PlayerAction | None = self.remote_player.select_action(context)

        if action is None or action.position is None:
            logger.warning("非合法HIT受信: position={}", position)
            return

        if not self.engine.apply_move(action.position):
            logger.warning("非合法HIT受信: position={}", position)
            return

        logger.info("HIT受信を盤面へ反映しました: position={}", position)
        self._log_game_over_if_needed()

    def _apply_remote_pass(self) -> None:
        """受信したPASSを検証し、盤面へ反映します。

        Returns:
            None.
        """
        self.remote_player.receive_pass()
        context: PlayerContext = PlayerContext(
            current_player=self.engine.current_player,
            legal_moves=self.engine.legal_moves,
        )
        action: PlayerAction | None = self.remote_player.select_action(context)

        if action is None or not action.is_pass:
            logger.warning("PASS受信を反映できませんでした。")
            return

        if self.engine.apply_pass(self.remote_player.color):
            logger.info("PASS受信を盤面へ反映しました: player={}", self.remote_player.color.name)
            self._log_game_over_if_needed()

    def _send_and_apply_pass(self) -> None:
        """自分のPASSを送信して盤面へ反映します。

        Returns:
            None.
        """
        player: Cell = self.local_player.color

        if self.engine.apply_pass(player):
            self.client.send_message(create_pass_message())
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

        OK受信済みを優先しますが、別実装のサーバがOKを返さない場合でも、
        TCP接続が確立済みであればClient / Blackの初手を許可します。

        Returns:
            対局入力を始められる通信状態であればTrue。
        """
        return self.game_ready or self.client.is_connected

    def _log_input_block_reason(self) -> None:
        """ローカルクリックが拒否された理由をログ出力します。

        Returns:
            None.
        """
        if not self._is_network_ready():
            logger.info(
                "通信準備前のクリックを無視しました: connected={}, ok_received={}",
                self.client.is_connected,
                self.game_ready,
            )
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
