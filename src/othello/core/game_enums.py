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


class CpuStrategyKind(Enum):
    """CPUの手選択アルゴリズム種別を表します。"""

    RANDOM = auto()
    GREEDY = auto()
    CORNER_PRIORITY = auto()
    WEIGHTED_BOARD = auto()
    LEARNING_WEIGHTED = auto()
    TABULAR_STATE_VALUE = auto()


class GameStatus(Enum):
    """ゲームの進行状態を表します。"""

    PLAYING = auto()
    GAME_OVER = auto()
