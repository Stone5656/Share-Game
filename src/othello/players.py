"""プレイヤー操作主体の実装を定義します。"""

from dataclasses import dataclass, field

from loguru import logger
import pygame

from src.othello.constants import BOARD_SIZE, SQUARE_SIZE
from src.othello.game_enums import Cell, PlayerKind
from src.othello.game_types import (
    BoardPosition,
    LegalMove,
    PlayerAction,
    PlayerContext,
)


@dataclass
class LocalHumanPlayer:
    """ローカル人間プレイヤーを表します。

    マウスクリック位置を盤面座標へ変換し、合法手であればPlayerActionを返します。
    """

    color: Cell
    kind: PlayerKind = PlayerKind.LOCAL_HUMAN
    _clicked_position: BoardPosition | None = field(default=None, init=False)

    def handle_event(self, event: pygame.event.Event) -> None:
        """マウスクリックイベントを受け取ります。

        Args:
            event: pygameのイベントオブジェクト。

        Returns:
            None.
        """
        match event.type:
            case pygame.MOUSEBUTTONDOWN:
                if event.button != 1:
                    logger.debug(
                        "左クリック以外のため選択しません: color={}, button={}",
                        self.color.name,
                        event.button,
                    )
                    return

                self._clicked_position = self._convert_mouse_pos_to_board_position(
                    event.pos
                )
                logger.debug(
                    "クリック位置を盤面座標へ変換しました: color={}, position={}",
                    self.color.name,
                    self._clicked_position,
                )

            case _:
                pass

    def select_action(self, context: PlayerContext) -> PlayerAction | None:
        """クリックされた位置が合法手なら行動を返します。

        Args:
            context: 手を選ぶために必要な情報。

        Returns:
            合法手が選択されていればPlayerAction、それ以外はNone。
        """
        if self._clicked_position is None:
            return None

        selected_position: BoardPosition | None = self._clicked_position
        self._clicked_position = None

        if selected_position is None:
            return None

        if not self._is_legal_position(selected_position, context.legal_moves):
            logger.debug(
                "非合法手がクリックされました: color={}, position={}",
                self.color.name,
                selected_position,
            )
            return None

        logger.info(
            "合法手が選択されました: color={}, position={}",
            self.color.name,
            selected_position,
        )

        return PlayerAction(position=selected_position)

    def _convert_mouse_pos_to_board_position(
        self,
        mouse_pos: tuple[int, int],
    ) -> BoardPosition | None:
        """マウス座標を盤面座標へ変換します。

        Args:
            mouse_pos: マウス座標。

        Returns:
            盤面内であればBoardPosition、盤面外であればNone。
        """
        mouse_x, mouse_y = mouse_pos
        row: int = mouse_y // SQUARE_SIZE
        col: int = mouse_x // SQUARE_SIZE

        if not self._is_inside_board(row, col):
            return None

        return BoardPosition(row=row, col=col)

    def _is_inside_board(self, row: int, col: int) -> bool:
        """指定座標が盤面内かを返します。

        Args:
            row: 盤面の行インデックス。
            col: 盤面の列インデックス。

        Returns:
            指定座標が盤面内であればTrue。
        """
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def _is_legal_position(
        self,
        position: BoardPosition,
        legal_moves: tuple[LegalMove, ...],
    ) -> bool:
        """指定位置が合法手に含まれるかを返します。

        Args:
            position: 確認対象の盤面位置。
            legal_moves: 現在の合法手一覧。

        Returns:
            指定位置が合法手であればTrue。
        """
        return any(legal_move.position == position for legal_move in legal_moves)
