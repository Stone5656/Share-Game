"""pygame-ceを使用したオセロアプリケーションのエントリーポイントです。"""

from loguru import logger

from src.othello.app import OthelloApp
from src.othello.logger import setup_logger


def main() -> None:
    """アプリケーションのエントリーポイントです。

    Returns:
        None.
    """
    setup_logger()
    logger.info("アプリ起動")

    app: OthelloApp = OthelloApp()
    app.run()


if __name__ == "__main__":
    main()
