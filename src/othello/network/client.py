"""PDF仕様に基づくオセロTCPクライアントを定義します。"""

from queue import Queue
import socket
import threading

from loguru import logger

from src.othello.config import NetworkConfig
from src.othello.network.protocol import OthelloMessage, create_start_message
from src.othello.network.transport import SocketTransport


class OthelloTcpClient:
    """PDF仕様に基づくオセロTCPクライアントです。"""

    def __init__(self, config: NetworkConfig) -> None:
        """TCPクライアントを初期化します。

        Args:
            config: TCP通信設定。
        """
        self.config: NetworkConfig = config
        self.incoming_queue: Queue[OthelloMessage] = Queue()
        self._transport: SocketTransport | None = None
        self._closed: bool = False
        self._connected: bool = False
        self._connect_thread: threading.Thread | None = None
        self._recv_thread: threading.Thread | None = None

    @property
    def is_connected(self) -> bool:
        """サーバとのTCP接続が確立済みかを返します。

        Returns:
            接続済みであればTrue。
        """
        return self._connected and not self._closed

    def start(self) -> None:
        """サーバへの接続処理を別スレッドで開始します。

        Returns:
            None.
        """
        self._connect_thread = threading.Thread(
            target=self._connect,
            daemon=True,
            name="othello-client-connect",
        )
        self._connect_thread.start()

        logger.info(
            "クライアント接続開始: host={}, port={}",
            self.config.host,
            self.config.port,
        )

    def send_message(self, message: OthelloMessage) -> None:
        """サーバへメッセージを送信します。

        Args:
            message: 送信する通信メッセージ。

        Returns:
            None.
        """
        if self._transport is None:
            logger.warning("サーバ未接続のため送信できません: message={}", message)
            return

        self._transport.send_message(message)
        logger.info("{}送信: message={}", message.command.value, message)

    def close(self) -> None:
        """サーバとのsocketを閉じます。

        Returns:
            None.
        """
        self._closed = True
        self._connected = False

        if self._transport is not None:
            self._transport.close()

        logger.info("TCPクライアントを終了しました。")

    def _connect(self) -> None:
        """サーバへ接続し、STARTを送信します。

        Returns:
            None.
        """
        sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.config.host, self.config.port))
        except OSError:
            logger.exception(
                "接続失敗: host={}, port={}",
                self.config.host,
                self.config.port,
            )
            sock.close()
            return

        if self._closed:
            sock.close()
            return

        logger.info(
            "接続成功: host={}, port={}",
            self.config.host,
            self.config.port,
        )
        self._transport = SocketTransport(sock)
        self._connected = True
        self._recv_thread = threading.Thread(
            target=self._recv_messages_forever,
            daemon=True,
            name="othello-client-recv",
        )
        self._recv_thread.start()

        self.send_message(create_start_message())
        logger.info("START送信")

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

        self._connected = False
        logger.info("クライアント受信スレッドを終了しました。")
