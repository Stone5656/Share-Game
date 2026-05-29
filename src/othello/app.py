"""pygameアプリケーションの初期化、イベント処理、メインループを定義します。"""

from loguru import logger
import pygame

from src.othello.board import Board
from src.othello.constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from src.othello.game_engine import GameEngine
from src.othello.game_enums import Cell, GameStatus
from src.othello.game_types import PlayerAction, PlayerContext
from src.othello.player_controller import PlayerController
from src.othello.players import LocalHumanPlayer
from src.othello.render import BoardRenderer
from src.othello.rules import LegalMoveScanner


class OthelloApp:
    """pygameの初期化、イベント処理、メインループを管理します。"""

    def __init__(self) -> None:
        """pygame、ウィンドウ、盤面、描画クラスを初期化します。"""
        pygame.init()

        self.screen: pygame.Surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.board: Board = Board()
        self.engine: GameEngine = GameEngine(
            board=self.board,
            current_player=Cell.BLACK,
            legal_move_scanner=LegalMoveScanner(),
        )
        self.renderer: BoardRenderer = BoardRenderer(self.screen)
        self.players: dict[Cell, PlayerController] = {
            Cell.BLACK: LocalHumanPlayer(Cell.BLACK),
            Cell.WHITE: LocalHumanPlayer(Cell.WHITE),
        }
        self.running: bool = True

        pygame.display.set_caption(WINDOW_TITLE)

        logger.info(
            "初期手番を設定しました: current_player={}, legal_move_count={}",
            self.engine.current_player.name,
            len(self.engine.legal_moves),
        )

        logger.info(
            "OthelloAppを初期化しました: screen={}x{}, fps={}",
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            FPS,
        )

    def run(self) -> None:
        """ユーザーがウィンドウを閉じるまでアプリケーションを実行します。

        Returns:
            None.
        """
        logger.info("アプリケーションループを開始しました。")

        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

        self._shutdown()

    def _handle_events(self) -> None:
        """pygameのイベントキューからイベントを取り出して処理します。

        Returns:
            None.
        """
        for event in pygame.event.get():
            self._handle_event(event)

    def _handle_event(self, event: pygame.event.Event) -> None:
        """pygameイベントを種類ごとに振り分けます。

        今後、キーボード入力、マウス入力、独自イベントなどが増える想定のため、
        ifではなくmatchを使用しています。

        Args:
            event: pygameのイベントオブジェクト。

        Returns:
            None.
        """
        match event.type:
            case pygame.QUIT:
                logger.info("終了イベントを受け取りました。")
                self.running = False

            case pygame.KEYDOWN | pygame.MOUSEBUTTONDOWN:
                current_player: PlayerController = self._get_current_player()
                current_player.handle_event(event)

            case _:
                # 現段階では、ウィンドウ移動やマウス移動などの細かいイベントは無視します。
                # これらをDEBUG出力するとログ量が多くなりすぎるため、必要になるまで記録しません。
                pass

    def _update(self) -> None:
        """現在手番のPlayerから行動を受け取り、ゲーム状態へ反映します。

        Returns:
            None.
        """
        if self.engine.status is GameStatus.GAME_OVER:
            return

        current_player: PlayerController = self._get_current_player()

        context: PlayerContext = PlayerContext(
            current_player=self.engine.current_player,
            legal_moves=self.engine.legal_moves,
        )

        action: PlayerAction | None = current_player.select_action(context)

        if action is None:
            return

        self.engine.apply_move(action.position)

    def _get_current_player(self) -> PlayerController:
        """現在手番に対応するPlayerControllerを返します。

        Returns:
            現在手番のPlayerController。
        """
        return self.players[self.engine.current_player]

    def _draw(self) -> None:
        """現在のフレームを描画します。

        Returns:
            None.
        """
        self.renderer.draw(
            self.board,
            self.engine.legal_moves,
            self.engine.get_result_text(),
        )
        pygame.display.flip()

    def _shutdown(self) -> None:
        """pygameを終了し、終了ログを出力します。

        Returns:
            None.
        """
        pygame.quit()
        logger.info("アプリケーションを終了しました。")
