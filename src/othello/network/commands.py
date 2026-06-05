"""PDF仕様の通信コマンドを定義します。"""

from enum import Enum


class OthelloCommand(Enum):
    """PDF仕様のオセロ通信コマンドを表します。"""

    START = "START"
    OK = "OK"
    HIT = "HIT"
    PASS = "PASS"
