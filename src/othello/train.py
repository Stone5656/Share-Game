"""盤面記憶型CPUをself-playで学習するCLIを定義します。"""

import argparse
from pathlib import Path

from loguru import logger

from src.othello.logger import setup_logger
from src.othello.training.parallel_trainer import (
    ParallelSelfPlayTrainer,
    ParallelTrainingConfig,
)

SUPPORTED_STRATEGY = "tabular-state-value"


def main() -> None:
    """学習CLIのエントリーポイントです。"""
    args = _parse_args()
    console_level = _resolve_console_level(args)
    setup_logger(
        console_level=console_level,
        file_level="DEBUG" if args.debug else args.log_level,
        enable_file_debug=args.debug,
    )
    config = ParallelTrainingConfig(
        games=args.games,
        workers=args.workers,
        output_dir=args.output_dir,
        learning_rate=args.learning_rate,
        gamma=args.gamma,
        epsilon=args.epsilon,
        save_every=args.save_every,
        seed=args.seed,
        log_level=args.log_level,
        debug=args.debug,
        quiet=args.quiet,
        progress_interval=args.progress_interval,
    )
    logger.info("training CLI開始")
    logger.info(
        "CLI引数: strategy={}, games={}, workers={}, output_dir={}, "
        "learning_rate={}, gamma={}, epsilon={}, save_every={}, seed={}, "
        "log_level={}, debug={}, quiet={}, progress_interval={}",
        args.strategy,
        config.games,
        config.workers,
        config.output_dir,
        config.learning_rate,
        config.gamma,
        config.epsilon,
        config.save_every,
        config.seed,
        config.log_level,
        config.debug,
        config.quiet,
        config.progress_interval,
    )
    shard_paths = ParallelSelfPlayTrainer().train(config)
    logger.info(
        "training CLI終了: strategy={}, games={}, shards={}",
        args.strategy,
        config.games,
        shard_paths,
    )


def _parse_args() -> argparse.Namespace:
    """学習CLI引数を解析します。

    Returns:
        検証済みのコマンドライン引数。
    """
    parser = argparse.ArgumentParser(
        description="オセロの盤面記憶型CPUをself-playで学習します。"
    )
    parser.add_argument(
        "--strategy",
        required=True,
        choices=(SUPPORTED_STRATEGY,),
        help="学習するCPU戦略。",
    )
    parser.add_argument("--games", type=_positive_int, default=100)
    parser.add_argument("--workers", type=_positive_int, default=1)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/training_shards"),
    )
    parser.add_argument("--learning-rate", type=_positive_float, default=0.1)
    parser.add_argument("--gamma", type=_unit_interval, default=0.95)
    parser.add_argument("--epsilon", type=_unit_interval, default=0.1)
    parser.add_argument("--save-every", type=_positive_int, default=100)
    parser.add_argument("--seed", type=int)
    parser.add_argument(
        "--log-level",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="INFO",
    )
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--progress-interval", type=_positive_int, default=100)
    return parser.parse_args()


def _resolve_console_level(args: argparse.Namespace) -> str:
    """CLIフラグからコンソールログレベルを決定します。"""
    if args.quiet:
        return "WARNING"
    if args.debug:
        return "DEBUG"
    return args.log_level


def _positive_int(value: str) -> int:
    """1以上の整数へ変換します。"""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("1以上の整数を指定してください。")
    return parsed


def _positive_float(value: str) -> float:
    """0より大きい浮動小数点数へ変換します。"""
    parsed = float(value)
    if parsed <= 0.0:
        raise argparse.ArgumentTypeError("0より大きい値を指定してください。")
    return parsed


def _unit_interval(value: str) -> float:
    """0.0から1.0の浮動小数点数へ変換します。"""
    parsed = float(value)
    if not 0.0 <= parsed <= 1.0:
        raise argparse.ArgumentTypeError("0.0から1.0の値を指定してください。")
    return parsed


if __name__ == "__main__":
    main()
