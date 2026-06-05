"""オセロゲームで使用するEnumを定義します。"""

from enum import Enum, auto


class Cell(Enum):
    """オセロ盤面の1マスの状態を表します。"""

    EMPTY = auto()
    WHITE = auto()
    BLACK = auto()


class PlayerKind(Enum):
    """プレイヤーの操作主体を表します。"""

    LOCAL_HUMAN = auto()
    CPU = auto()
    REMOTE_HUMAN = auto()
    REMOTE_CPU = auto()


class GameStatus(Enum):
    """ゲームの進行状態を表します。"""

    PLAYING = auto()
    GAME_OVER = auto()
