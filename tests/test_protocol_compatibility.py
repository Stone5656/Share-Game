"""CPU戦略追加後も通信プロトコルが不変であることをテストします。"""

import json
import unittest

from src.othello.core.game_types import BoardPosition
from src.othello.network.codec import encode_message
from src.othello.network.commands import OthelloCommand
from src.othello.network.message import create_hit_message


class ProtocolCompatibilityTest(unittest.TestCase):
    """通信コマンドとJSON形式の互換性を確認します。"""

    def test_command_set_is_unchanged(self) -> None:
        """通信コマンドはSTART、OK、HIT、PASSだけです。"""
        self.assertEqual(
            {command.value for command in OthelloCommand},
            {"START", "OK", "HIT", "PASS"},
        )

    def test_json_shape_is_unchanged(self) -> None:
        """通信JSONはcommand、col、rowだけを持ちます。"""
        encoded = encode_message(create_hit_message(BoardPosition(2, 3)))
        payload = json.loads(encoded)

        self.assertEqual(payload, {"command": "HIT", "col": 3, "row": 2})


if __name__ == "__main__":
    unittest.main()
