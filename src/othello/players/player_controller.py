"""プレイヤー操作主体の共通インターフェースを定義します。"""

from typing import Protocol

import pygame

from src.othello.core.game_enums import Cell, PlayerKind
from src.othello.core.game_types import PlayerAction, PlayerContext


class PlayerController(Protocol):
    """手を選択する主体を表す共通インターフェースです。

    LocalHuman、CPU、Remoteなどの実装を差し替えるために使用します。
    """

    @property
    def color(self) -> Cell:
        """担当する石色を返します。"""

    @property
    def kind(self) -> PlayerKind:
        """プレイヤー種別を返します。"""

    def handle_event(self, event: pygame.event.Event) -> None:
        """pygameイベントを受け取ります。

        Args:
            event: pygameのイベントオブジェクト。

        Returns:
            None.
        """

    def select_action(self, context: PlayerContext) -> PlayerAction | None:
        """現在の状況から行動を選択します。

        Args:
            context: 手を選ぶために必要な情報。

        Returns:
            行動が決まっていればPlayerAction、まだ決まっていなければNone。
        """
