"""オセロのプレイヤー操作主体を扱うパッケージです。"""

from src.othello.players.local_human_player import LocalHumanPlayer
from src.othello.players.remote_human_player import RemoteHumanPlayer

__all__ = ["LocalHumanPlayer", "RemoteHumanPlayer"]
