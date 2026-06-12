"""盤面記憶型CPUをself-playで学習するCLIを定義します。"""

import argparse
from pathlib import Path

from loguru import logger

from src.othello.logger import setup_logger
from src.othello.players.cpu.rl.self_play_trainer import SelfPlayTrainer
from src.othello.players.cpu.rl.training_config import TabularTrainingConfig

SUPPORTED_STRATEGY = "tabular-state-value"


def main() -> None:
    """学習CLIのエントリーポイントです。"""
    setup_logger()
    args = _parse_args()
    config = TabularTrainingConfig(
        games=args.games,
        learning_rate=args.learning_rate,
        gamma=args.gamma,
        epsilon=args.epsilon,
        state_values_path=args.state_values_path,
        save_every=args.save_every,
    )
    logger.info("training CLI開始")
    logger.info(
        "CLI引数: strategy={}, games={}, learning_rate={}, gamma={}, "
        "epsilon={}, state_values_path={}, save_every={}",
        args.strategy,
        config.games,
        config.learning_rate,
        config.gamma,
        config.epsilon,
        config.state_values_path,
        config.save_every,
    )
    SelfPlayTrainer().train(config)
    logger.info(
        "training CLI終了: strategy={}, games={}, path={}",
        args.strategy,
        config.games,
        config.state_values_path,
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
    parser.add_argument("--learning-rate", type=_positive_float, default=0.1)
    parser.add_argument("--gamma", type=_unit_interval, default=0.95)
    parser.add_argument("--epsilon", type=_unit_interval, default=0.1)
    parser.add_argument(
        "--state-values-path",
        type=Path,
        default=Path("data/othello_state_values.json"),
    )
    parser.add_argument("--save-every", type=_positive_int, default=1)
    return parser.parse_args()


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
