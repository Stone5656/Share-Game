"""オセロのゲームロジックで使用する値オブジェクトを定義します。"""

from dataclasses import dataclass

from src.othello.game_enums import Cell


@dataclass(frozen=True)
class BoardPosition:
    """盤面上の位置を表します。

    Attributes:
        row: 盤面の行インデックス。
        col: 盤面の列インデックス。
    """

    row: int
    col: int


@dataclass(frozen=True)
class Direction:
    """盤面走査に使用する方向を表します。

    Attributes:
        row_delta: 行方向の移動量。
        col_delta: 列方向の移動量。
    """

    row_delta: int
    col_delta: int


@dataclass(frozen=True)
class LegalMove:
    """合法手を表します。

    Attributes:
        position: 石を置ける位置。
        flippable_positions: その手で反転できる相手石の位置一覧。
    """

    position: BoardPosition
    flippable_positions: tuple[BoardPosition, ...]


@dataclass(frozen=True)
class PlayerAction:
    """プレイヤーが選択した行動を表します。

    Attributes:
        position: 石を置く位置。
    """

    position: BoardPosition


@dataclass(frozen=True)
class PlayerContext:
    """プレイヤーが手を選ぶために必要な情報を表します。

    Attributes:
        current_player: 現在の手番プレイヤー。
        legal_moves: 現在の手番プレイヤーが選択できる合法手一覧。
    """

    current_player: Cell
    legal_moves: tuple[LegalMove, ...]
