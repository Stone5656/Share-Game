"""PDF仕様に基づくオセロTCPサーバを定義します。"""

import socket
import threading
from queue import Queue

from loguru import logger

from src.othello.config import NetworkConfig
from src.othello.network.protocol import (
    OthelloCommand,
    OthelloMessage,
    create_ok_message,
)
from src.othello.network.transport import SocketTransport


class OthelloTcpServer:
    """PDF仕様に基づくオセロTCPサーバです。"""

    def __init__(self, config: NetworkConfig) -> None:
        """TCPサーバを初期化します。

        Args:
            config: TCP通信設定。
        """
        self.config: NetworkConfig = config
        self.incoming_queue: Queue[OthelloMessage] = Queue()
        self._server_sock: socket.socket | None = None
        self._transport: SocketTransport | None = None
        self._closed: bool = False
        self._accept_thread: threading.Thread | None = None
        self._recv_thread: threading.Thread | None = None

    def start(self) -> None:
        """TCPサーバの待ち受けを開始します。

        Returns:
            None.
        """
        server_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.config.host, self.config.port))
        server_sock.listen(1)
        self._server_sock = server_sock

        self._accept_thread = threading.Thread(
            target=self._accept_client,
            daemon=True,
            name="othello-server-accept",
        )
        self._accept_thread.start()

        logger.info(
            "サーバ待ち受け開始: host={}, port={}",
            self.config.host,
            self.config.port,
        )

    def send_message(self, message: OthelloMessage) -> None:
        """接続済みクライアントへメッセージを送信します。

        Args:
            message: 送信する通信メッセージ。

        Returns:
            None.
        """
        if self._transport is None:
            logger.warning(
                "クライアント未接続のため送信できません: message={}",
                message,
            )
            return

        self._transport.send_message(message)
        logger.info("{}送信: message={}", message.command.value, message)

    def close(self) -> None:
        """サーバsocketと通信用socketを閉じます。

        Returns:
            None.
        """
        self._closed = True

        if self._transport is not None:
            self._transport.close()

        if self._server_sock is not None:
            try:
                self._server_sock.close()
            except OSError:
                logger.exception("サーバsocket close中にエラーが発生しました。")

        logger.info("TCPサーバを終了しました。")

    def _accept_client(self) -> None:
        """クライアント接続をacceptします。

        Returns:
            None.
        """
        if self._server_sock is None:
            return

        try:
            client_sock, address = self._server_sock.accept()
        except OSError:
            if not self._closed:
                logger.exception("クライアントaccept中にエラーが発生しました。")
            return

        if self._closed:
            client_sock.close()
            return

        logger.info("接続成功: address={}", address)
        self._transport = SocketTransport(client_sock)
        self._recv_thread = threading.Thread(
            target=self._recv_messages_forever,
            daemon=True,
            name="othello-server-recv",
        )
        self._recv_thread.start()

    def _recv_messages_forever(self) -> None:
        """切断されるまでメッセージを受信し続けます。

        Returns:
            None.
        """
        while not self._closed and self._transport is not None:
            message: OthelloMessage | None = self._transport.recv_message()

            if message is None:
                break

            self.incoming_queue.put(message)
            logger.info("{}受信: message={}", message.command.value, message)

            if message.command is OthelloCommand.START:
                logger.info("START受信")
                self.send_message(create_ok_message())
                logger.info("OK送信")

        logger.info("サーバ受信スレッドを終了しました。")
