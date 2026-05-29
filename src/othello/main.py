"""pygame-ceを使用したオセロ盤面描画サンプル。

このモジュールでは、8x8のオセロ盤面と初期配置の石だけを描画します。
合法手判定、石の反転、CPU処理、通信対戦などのゲームルールは、
この段階ではまだ実装しません。

将来的に Player vs CPU、CPU vs CPU、Player vs Remote Player などを
追加しやすくするため、盤面状態、描画、イベント処理、アプリケーション
ループを分離しています。
"""

from loguru import logger

from src.othello.app import OthelloApp
from src.othello.logger import setup_logger


def main() -> None:
    """アプリケーションのエントリーポイントです。

    Returns:
        None.
    """
    setup_logger()

    logger.info("Othelloアプリケーションを起動します。")

    app: OthelloApp = OthelloApp()
    app.run()


if __name__ == "__main__":
    main()
