"""開始画面から非同期self-play学習を実行します。"""

import threading

import pygame
from loguru import logger

from src.othello.constants import RESULT_TEXT_COLOR
from src.othello.players.cpu.rl.self_play_trainer import SelfPlayTrainer
from src.othello.ui.button import Button


class LearningTrainingControl:
    """self-play学習ボタンと実行状態を管理します。"""

    def __init__(self) -> None:
        """学習ボタンと初期状態を作成します。"""
        self.button = Button(
            rect=pygame.Rect(20, 480, 280, 44),
            label="Train Learning CPU: 10 games",
        )
        self.status = "Training: idle"
        self._thread: threading.Thread | None = None

    def handle_click(self, mouse_pos: tuple[int, int]) -> bool:
        """学習ボタンのクリックを処理します。

        Args:
            mouse_pos: クリック座標。

        Returns:
            学習ボタンがクリックされた場合はTrue。
        """
        if not self.button.is_clicked(mouse_pos):
            return False
        if self._thread is not None and self._thread.is_alive():
            logger.info("self-play学習は既に実行中です。")
            return True

        self.status = "Training: running 10 games"
        self._thread = threading.Thread(
            target=self._train,
            daemon=True,
            name="othello-self-play",
        )
        self._thread.start()
        return True

    def draw(
        self,
        surface: pygame.Surface,
        button_font: pygame.font.Font,
        status_font: pygame.font.Font,
    ) -> None:
        """学習ボタンと実行状態を描画します。

        Args:
            surface: 描画先Surface。
            button_font: ボタン用フォント。
            status_font: 状態表示用フォント。
        """
        self.button.draw(surface, button_font)
        status_surface = status_font.render(
            self.status,
            True,
            RESULT_TEXT_COLOR,
        )
        status_rect = status_surface.get_rect(center=(320, 610))
        surface.blit(status_surface, status_rect)

    def _train(self) -> None:
        """別スレッドで10局のself-play学習を実行します。"""
        try:
            trainer = SelfPlayTrainer()
            trainer.train(10)
        except Exception:
            self.status = "Training: failed"
            logger.exception("self-play学習に失敗しました。")
            return

        self.status = "Training: completed 10 games"
