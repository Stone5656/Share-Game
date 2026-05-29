"""Loguruの設定を定義します。"""

import sys

from loguru import logger

from src.othello.constants import LOG_DIR, LOG_FILE_PATH


def setup_logger() -> None:
    """Loguruの出力先を設定します。

    標準のLoguruハンドラを削除し、このアプリケーション用の
    コンソール出力とファイル出力を明示的に設定します。

    Returns:
        None.
    """
    LOG_DIR.mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stderr,
        level="INFO",
        colorize=True,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level:<8}</level> | "
            "<cyan>{message}</cyan>"
        ),
    )

    logger.add(
        LOG_FILE_PATH,
        level="DEBUG",
        rotation="1 MB",
        retention="7 days",
        encoding="utf-8",
        colorize=False,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level:<8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
    )
