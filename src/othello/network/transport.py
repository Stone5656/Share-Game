"""socketを使ったOthelloMessage送受信処理を定義します。"""

import socket
from contextlib import suppress
from typing import Final

from loguru import logger

from src.othello.network.protocol import (
    OthelloMessage,
    decode_message,
    encode_message,
)

RECV_SIZE: Final[int] = 1024


class SocketTransport:
    """socketを使ってOthelloMessageを送受信する通信ラッパーです。"""

    def __init__(self, sock: socket.socket) -> None:
        """通信ラッパーを初期化します。

        Args:
            sock: 通信に使用するsocket。
        """
        self.sock: socket.socket = sock
        self._closed: bool = False

    def send_message(self, message: OthelloMessage) -> None:
        """OthelloMessageを送信します。

        Args:
            message: 送信する通信メッセージ。

        Returns:
            None.
        """
        if self._closed:
            logger.warning("socket close済みのため送信しません: message={}", message)
            return

        encoded_message: bytes = encode_message(message)
        logger.info("送信JSON: {}", _decode_bytes_for_log(encoded_message))

        try:
            self.sock.sendall(encoded_message)
        except OSError:
            logger.exception("メッセージ送信に失敗しました: message={}", message)
            self.close()
            return

        logger.debug("メッセージを送信しました: message={}", message)

    def recv_message(self) -> OthelloMessage | None:
        """OthelloMessageを受信します。

        Returns:
            受信できた場合はOthelloMessage、切断または失敗時はNone。
        """
        while not self._closed:
            try:
                data: bytes = self.sock.recv(RECV_SIZE)
            except OSError:
                logger.exception("メッセージ受信に失敗しました。")
                self.close()
                return None

            if not data:
                logger.info("socket切断を検出しました。")
                self.close()
                return None

            logger.info("受信JSON: {}", _decode_bytes_for_log(data))

            try:
                message: OthelloMessage = decode_message(data)
            except ValueError:
                logger.exception("不正なJSONメッセージを破棄しました: data={}", data)
                continue

            logger.debug("メッセージを受信しました: message={}", message)
            return message

        return None

    def close(self) -> None:
        """socketを閉じます。

        Returns:
            None.
        """
        if self._closed:
            return

        self._closed = True

        with suppress(OSError):
            self.sock.shutdown(socket.SHUT_RDWR)

        try:
            self.sock.close()
        except OSError:
            logger.exception("socket close中にエラーが発生しました。")

        logger.info("socket closeを完了しました。")


def _decode_bytes_for_log(data: bytes) -> str:
    """ログ出力用にbytesをUTF-8文字列へ変換します。

    Args:
        data: ログ出力対象のbytes。

    Returns:
        UTF-8として復元した文字列。復元できないバイトは置換文字にします。
    """
    return data.decode("utf-8", errors="replace")
