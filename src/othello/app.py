"""pygameアプリケーションの初期化、イベント委譲、メインループを定義します。"""

from typing import Protocol

import pygame
from loguru import logger

from src.othello.config import AppState, NetworkConfig
from src.othello.constants import (
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WINDOW_TITLE,
)
from src.othello.modes.client_mode import ClientMode
from src.othello.modes.local_mode import LocalMode
from src.othello.modes.server_mode import ServerMode
from src.othello.ui.start_screen import StartScreen


class GameMode(Protocol):
    """OthelloAppが委譲するゲームモードの共通インターフェースです。"""

    def handle_event(self, event: pygame.event.Event) -> None:
        """pygameイベントを処理します。

        Args:
            event: pygameイベント。

        Returns:
            None.
        """

    def update(self) -> None:
        """モードの状態を更新します。

        Returns:
            None.
        """

    def draw(self) -> None:
        """モードの画面を描画します。

        Returns:
            None.
        """

    def close(self) -> None:
        """モードを終了します。

        Returns:
            None.
        """


class OthelloApp:
    """pygameの初期化、開始画面、モード委譲、終了処理を管理します。"""

    def __init__(self, network_config: NetworkConfig) -> None:
        """pygame、ウィンドウ、開始画面を初期化します。

        Args:
            network_config: TCP通信設定。
        """
        pygame.init()

        self.screen: pygame.Surface = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.app_state: AppState = AppState.START_SCREEN
        self.network_config: NetworkConfig = network_config
        self.start_screen: StartScreen = StartScreen(self.network_config)
        self.current_mode: GameMode | None = None

        pygame.display.set_caption(WINDOW_TITLE)
        logger.info("開始画面表示")
        logger.info(
            "TCP通信設定を適用しました: host={}, port={}",
            self.network_config.host,
            self.network_config.port,
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
        """pygameイベントを取得して現在状態へ委譲します。

        Returns:
            None.
        """
        for event in pygame.event.get():
            self._handle_event(event)

    def _handle_event(self, event: pygame.event.Event) -> None:
        """pygameイベントを処理します。

        Args:
            event: pygameイベント。

        Returns:
            None.
        """
        if event.type == pygame.QUIT:
            logger.info("終了イベントを受け取りました。")
            self.running = False
            return

        if self.app_state is AppState.START_SCREEN:
            selected_state: AppState | None = self.start_screen.handle_event(event)

            if selected_state is not None:
                self._start_selected_mode(selected_state)
            return

        if self.current_mode is not None:
            self.current_mode.handle_event(event)

    def _update(self) -> None:
        """現在のモード状態を更新します。

        Returns:
            None.
        """
        if self.current_mode is not None:
            self.current_mode.update()

    def _draw(self) -> None:
        """現在の画面を描画します。

        Returns:
            None.
        """
        if self.app_state is AppState.START_SCREEN:
            self.start_screen.draw(self.screen)
        elif self.current_mode is not None:
            self.current_mode.draw()

        pygame.display.flip()

    def _start_selected_mode(self, selected_state: AppState) -> None:
        """開始画面で選択されたモードを開始します。

        Args:
            selected_state: 開始するアプリケーション状態。

        Returns:
            None.
        """
        match selected_state:
            case AppState.LOCAL_GAME:
                logger.info("Local選択")
                self.current_mode = LocalMode(self.screen)

            case AppState.SERVER_GAME:
                logger.info("Server選択")
                self.current_mode = ServerMode(self.screen, self.network_config)

            case AppState.CLIENT_GAME:
                logger.info("Client選択")
                self.current_mode = ClientMode(self.screen, self.network_config)

            case AppState.SERVER_CPU_GAME:
                selected_strategy = self.start_screen.selected_cpu_strategy
                logger.info(
                    "Remote CPU vs CPU開始: role=Server, color=WHITE, strategy={}",
                    selected_strategy.name,
                )
                self.current_mode = ServerMode(
                    self.screen,
                    self.network_config,
                    use_cpu=True,
                    cpu_strategy_kind=selected_strategy,
                )

            case AppState.CLIENT_CPU_GAME:
                selected_strategy = self.start_screen.selected_cpu_strategy
                logger.info(
                    "Remote CPU vs CPU開始: role=Client, color=BLACK, strategy={}",
                    selected_strategy.name,
                )
                self.current_mode = ClientMode(
                    self.screen,
                    self.network_config,
                    use_cpu=True,
                    cpu_strategy_kind=selected_strategy,
                )

            case AppState.START_SCREEN:
                logger.info("開始画面へ戻ります。")
                self.current_mode = None

        self.app_state = selected_state

    def _shutdown(self) -> None:
        """現在モードとpygameを終了し、終了ログを出力します。

        Returns:
            None.
        """
        if self.current_mode is not None:
            self.current_mode.close()

        pygame.quit()
        logger.info("アプリ終了")
