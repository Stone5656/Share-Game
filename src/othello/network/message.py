"""PDF仕様の通信メッセージ型を定義します。"""

from collections.abc import Mapping
from dataclasses import dataclass

from src.othello.core.game_types import BoardPosition
from src.othello.network.commands import OthelloCommand

type JsonValue = str | int | None


@dataclass(frozen=True)
class OthelloMessage:
    """PDF仕様に基づくオセロ通信メッセージを表します。

    Attributes:
        command: 通信コマンド。
        col: 石を置いた列。不要な場合はNone。
        row: 石を置いた行。不要な場合はNone。
    """

    command: OthelloCommand
    col: int | None = None
    row: int | None = None


@dataclass(frozen=True)
class OthelloPayload:
    """PDF仕様のJSON辞書形状を表す内部payloadです。

    Attributes:
        command: JSON上の通信コマンド文字列。
        col: 石を置いた列。不要または未指定の場合はNone。
        row: 石を置いた行。不要または未指定の場合はNone。
    """

    command: str
    col: int | None = None
    row: int | None = None

    def to_mapping(self) -> Mapping[str, JsonValue]:
        """JSON変換用のMappingへ変換します。

        Returns:
            PDF仕様に基づくJSON用Mapping。
        """
        return {"command": self.command, "col": self.col, "row": self.row}


def create_start_message() -> OthelloMessage:
    """STARTメッセージを作成します。

    Returns:
        STARTメッセージ。
    """
    return OthelloMessage(command=OthelloCommand.START)


def create_ok_message() -> OthelloMessage:
    """OKメッセージを作成します。

    Returns:
        OKメッセージ。
    """
    return OthelloMessage(command=OthelloCommand.OK)


def create_hit_message(position: BoardPosition) -> OthelloMessage:
    """HITメッセージを作成します。

    Args:
        position: 石を置いた位置。

    Returns:
        HITメッセージ。
    """
    return OthelloMessage(
        command=OthelloCommand.HIT,
        col=position.col,
        row=position.row,
    )


def create_pass_message() -> OthelloMessage:
    """PASSメッセージを作成します。

    Returns:
        PASSメッセージ。
    """
    return OthelloMessage(command=OthelloCommand.PASS)
