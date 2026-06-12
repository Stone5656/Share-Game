"""状態価値shardを統合するCLI処理を定義します。"""

import argparse
from pathlib import Path

from loguru import logger

from src.othello.logger import setup_logger
from src.othello.training.state_value_merger import StateValueMerger


def main() -> None:
    """状態価値merge CLIのエントリーポイントです。"""
    setup_logger()
    args = _parse_args()
    logger.info(
        "状態価値merge CLI開始: input_dir={}, output={}",
        args.input_dir,
        args.output,
    )
    result = StateValueMerger().merge(args.input_dir, args.output)
    logger.info(
        "状態価値merge CLI終了: shards={}, skipped={}, states={}",
        result.loaded_shards,
        result.skipped_files,
        result.state_count,
    )


def _parse_args() -> argparse.Namespace:
    """merge CLI引数を解析します。"""
    parser = argparse.ArgumentParser(
        description="version 2の状態価値shardを訪問回数で統合します。"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="state_values_worker_*.jsonを含むディレクトリ。",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="統合後の状態価値JSON保存先。",
    )
    return parser.parse_args()
