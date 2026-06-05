"""PDF仕様に基づくオセロTCP通信メッセージを定義します。"""

from dataclasses import dataclass
from enum import Enum
import json
from typing import Any

from src.othello.core.game_types import BoardPosition


class OthelloCommand(Enum):
    """PDF仕様のオセロ通信コマンドを表します。"""

    START = "START"
    OK = "OK"
    HIT = "HIT"
    PASS = "PASS"


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


def encode_message(message: OthelloMessage) -> bytes:
    """OthelloMessageをJSON bytesへ変換します。

    Args:
        message: 送信するオセロ通信メッセージ。

    Returns:
        UTF-8でエンコードされたJSON bytes。
    """
    payload: dict[str, str | int | None] = {
        "command": message.command.value,
        "col": message.col,
        "row": message.row,
    }
    return json.dumps(payload).encode("utf-8")


def decode_message(data: bytes) -> OthelloMessage:
    """JSON bytesをOthelloMessageへ変換します。

    Args:
        data: 受信したJSON bytes。

    Returns:
        復元されたオセロ通信メッセージ。

    Raises:
        ValueError: メッセージ形式が不正な場合。
    """
    try:
        payload: dict[str, Any] = json.loads(data.decode("utf-8"))
        command: OthelloCommand = OthelloCommand(payload["command"])
    except (json.JSONDecodeError, KeyError, UnicodeDecodeError, ValueError) as exc:
        raise ValueError("メッセージ形式が不正です。") from exc

    col: int | None = _to_optional_int(payload.get("col"))
    row: int | None = _to_optional_int(payload.get("row"))

    if command is OthelloCommand.HIT and (col is None or row is None):
        raise ValueError("HITメッセージにはcolとrowが必要です。")

    return OthelloMessage(command=command, col=col, row=row)


def _to_optional_int(value: Any) -> int | None:
    """任意の値をintまたはNoneへ変換します。

    Args:
        value: 変換対象の値。

    Returns:
        int値またはNone。
    """
    if value is None:
        return None

    return int(value)
