"""アプリケーション状態と起動設定を定義します。"""

from dataclasses import dataclass
from enum import Enum, auto


class AppState(Enum):
    """アプリケーション全体の状態を表します。"""

    START_SCREEN = auto()
    LOCAL_GAME = auto()
    SERVER_GAME = auto()
    CLIENT_GAME = auto()
    SERVER_CPU_GAME = auto()
    CLIENT_CPU_GAME = auto()


@dataclass(frozen=True)
class NetworkConfig:
    """TCP通信設定を表します。

    Attributes:
        host: 接続または待ち受けに使用するIPアドレス。
        port: TCPポート番号。
    """

    host: str
    port: int
