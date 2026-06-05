"""ゲーム結果の判定と表示文字列を定義します。"""

from src.othello.core.game_enums import Cell, GameStatus


def determine_winner(black_count: int, white_count: int) -> Cell | None:
    """石数から勝者を判定します。

    Args:
        black_count: 黒石数。
        white_count: 白石数。

    Returns:
        勝者のCell。引き分けの場合はNone。
    """
    if black_count > white_count:
        return Cell.BLACK

    if white_count > black_count:
        return Cell.WHITE

    return None


def create_result_text(status: GameStatus, winner: Cell | None) -> str | None:
    """ゲーム結果の表示文字列を作成します。

    Args:
        status: ゲーム進行状態。
        winner: 勝者。引き分けの場合はNone。

    Returns:
        ゲーム終了時は結果文字列。ゲーム中はNone。
    """
    if status is not GameStatus.GAME_OVER:
        return None

    if winner is Cell.BLACK:
        return "Black Win"

    if winner is Cell.WHITE:
        return "White Win"

    return "Draw"
