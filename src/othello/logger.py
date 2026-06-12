"""Loguruの設定を定義します。"""

import sys
from collections.abc import Callable
from typing import TYPE_CHECKING

from loguru import logger

from src.othello.constants import LOG_DIR, LOG_FILE_PATH

if TYPE_CHECKING:
    from loguru import Record

    LogFilter = Callable[[Record], bool]
else:
    LogFilter = Callable[..., bool]


def setup_logger(
    *,
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    enable_file_debug: bool = True,
    log_filter: LogFilter | None = None,
) -> None:
    """Loguruの出力先を設定します。

    標準のLoguruハンドラを削除し、このアプリケーション用の
    コンソール出力とファイル出力を明示的に設定します。

    Args:
        console_level: コンソール出力のログレベル。
        file_level: ファイル出力のログレベル。
        enable_file_debug: DEBUGを含むファイルログを有効にするか。
        log_filter: 出力対象を絞り込むLoguruフィルタ。
    """
    logger.remove()

    logger.add(
        sys.stderr,
        level=console_level,
        colorize=True,
        filter=log_filter,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level:<8}</level> | "
            "<cyan>{message}</cyan>"
        ),
    )

    if enable_file_debug:
        LOG_DIR.mkdir(exist_ok=True)
        logger.add(
            LOG_FILE_PATH,
            level=file_level,
            rotation="1 MB",
            retention="7 days",
            encoding="utf-8",
            colorize=False,
            filter=log_filter,
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "{level:<8} | "
                "{name}:{function}:{line} | "
                "{message}"
            ),
        )
