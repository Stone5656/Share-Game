"""PDF仕様メッセージのJSON encode/decode処理を定義します。"""

import json
from collections.abc import Mapping
from typing import cast

from src.othello.network.commands import OthelloCommand
from src.othello.network.message import OthelloMessage, OthelloPayload

type JsonObject = Mapping[str, object]


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

    if command is OthelloCommand.HIT and (payload.col is None or payload.row is None):
        raise ValueError("HITメッセージにはcolとrowが必要です。")

    return OthelloMessage(command=command, col=payload.col, row=payload.row)


def _decode_payload(data: bytes) -> OthelloPayload:
    """JSON bytesをOthelloPayloadへ変換します。

    Args:
        data: 受信したJSON bytes。

    Returns:
        OthelloPayload。
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
    """
    try:
        loaded: object = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("メッセージ形式が不正です。") from exc

    if not isinstance(loaded, Mapping):
        raise ValueError("メッセージpayloadはMappingである必要があります。")

    raw_mapping: Mapping[object, object] = cast(Mapping[object, object], loaded)

    if not all(isinstance(key, str) for key in raw_mapping):
        raise ValueError("メッセージpayloadのキーは文字列である必要があります。")

    return cast(JsonObject, raw_mapping)


def _read_required_str(json_object: JsonObject, key: str) -> str:
    """JSONオブジェクトから必須文字列値を読み取ります。

    Args:
        json_object: 読み取り対象のJSONオブジェクト。
        key: 読み取るキー。

    Returns:
        文字列値。
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
    """
    value: object | None = json_object.get(key)

    if value is None:
        return None

    if type(value) is int:
        return value

    raise ValueError(f"{key}は整数またはNoneである必要があります。")
