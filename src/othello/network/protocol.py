"""PDF仕様に基づくオセロTCP通信メッセージを定義します。"""

from dataclasses import dataclass
from enum import Enum
import json
from collections.abc import Mapping
from typing import TypeAlias, cast

from src.othello.core.game_types import BoardPosition

JsonValue: TypeAlias = str | int | None
JsonObject: TypeAlias = Mapping[str, object]


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
        return {
            "command": self.command,
            "col": self.col,
            "row": self.row,
        }


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
    payload: OthelloPayload = OthelloPayload(
        command=message.command.value,
        col=message.col,
        row=message.row,
    )
    return json.dumps(payload.to_mapping()).encode("utf-8")


def decode_message(data: bytes) -> OthelloMessage:
    """JSON bytesをOthelloMessageへ変換します。

    Args:
        data: 受信したJSON bytes。

    Returns:
        復元されたオセロ通信メッセージ。

    Raises:
        ValueError: メッセージ形式が不正な場合。
    """
    payload: OthelloPayload = _decode_payload(data)
    command: OthelloCommand = _decode_command(payload.command)

    col: int | None = payload.col
    row: int | None = payload.row

    if command is OthelloCommand.HIT and (col is None or row is None):
        raise ValueError("HITメッセージにはcolとrowが必要です。")

    return OthelloMessage(command=command, col=col, row=row)


def _decode_payload(data: bytes) -> OthelloPayload:
    """JSON bytesをOthelloPayloadへ変換します。

    Args:
        data: 受信したJSON bytes。

    Returns:
        OthelloPayload。

    Raises:
        ValueError: JSONまたはpayload形式が不正な場合。
    """
    json_object: JsonObject = _load_json_object(data)
    return OthelloPayload(
        command=_read_required_str(json_object, "command"),
        col=_read_optional_int(json_object, "col"),
        row=_read_optional_int(json_object, "row"),
    )


def _decode_command(command_value: str) -> OthelloCommand:
    """文字列から通信コマンドを復元します。

    Args:
        command_value: 通信コマンド文字列。

    Returns:
        通信コマンド。

    Raises:
        ValueError: commandが不正な場合。
    """
    try:
        return OthelloCommand(command_value)
    except ValueError as exc:
        raise ValueError("未対応のcommandです。") from exc


def _load_json_object(data: bytes) -> JsonObject:
    """JSON bytesを型検証済みのMappingへ変換します。

    Args:
        data: 受信したJSON bytes。

    Returns:
        文字列キーを持つJSONオブジェクト。

    Raises:
        ValueError: JSONまたはオブジェクト形式が不正な場合。
    """
    try:
        loaded: object = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("メッセージ形式が不正です。") from exc

    if not isinstance(loaded, Mapping):
        raise ValueError("メッセージpayloadはMappingである必要があります。")

    raw_mapping: Mapping[object, object] = cast(Mapping[object, object], loaded)

    if not all(isinstance(key, str) for key in raw_mapping.keys()):
        raise ValueError("メッセージpayloadのキーは文字列である必要があります。")

    return cast(JsonObject, raw_mapping)


def _read_required_str(json_object: JsonObject, key: str) -> str:
    """JSONオブジェクトから必須文字列値を読み取ります。

    Args:
        json_object: 読み取り対象のJSONオブジェクト。
        key: 読み取るキー。

    Returns:
        文字列値。

    Raises:
        ValueError: 値が文字列でない場合。
    """
    value: object | None = json_object.get(key)

    if not isinstance(value, str):
        raise ValueError(f"{key}は文字列である必要があります。")

    return value


def _read_optional_int(json_object: JsonObject, key: str) -> int | None:
    """JSONオブジェクトから任意の整数値を読み取ります。

    Args:
        json_object: 読み取り対象のJSONオブジェクト。
        key: 読み取るキー。

    Returns:
        int値またはNone。

    Raises:
        ValueError: 値が整数またはNoneでない場合。
    """
    value: object | None = json_object.get(key)

    if value is None:
        return None

    if type(value) is int:
        return value

    raise ValueError(f"{key}は整数またはNoneである必要があります。")
