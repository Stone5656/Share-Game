"""1 worker分のself-play trainingを実行します。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from src.othello.logger import setup_logger
from src.othello.players.cpu.rl.self_play_trainer import SelfPlayTrainer
from src.othello.players.cpu.rl.training_config import TabularTrainingConfig

if TYPE_CHECKING:
    from loguru import Record


@dataclass(frozen=True)
class WorkerTrainingConfig:
    """1 worker分のtraining設定を表します。"""

    worker_id: int
    games: int
    learning_rate: float
    gamma: float
    epsilon: float
    output_path: Path
    save_every: int
    seed: int
    log_level: str
    debug: bool
    quiet: bool
    progress_interval: int


def run_training_worker(config: WorkerTrainingConfig) -> Path:
    """1 worker分のself-play trainingを実行します。

    Args:
        config: worker固有のゲーム数、seed、出力先。

    Returns:
        作成したshardファイルのパス。
    """
    console_level = _resolve_console_level(config.log_level, config.debug, config.quiet)
    setup_logger(
        console_level=console_level,
        file_level="DEBUG" if config.debug else config.log_level,
        enable_file_debug=config.debug,
        log_filter=None if config.debug else _is_training_log,
    )
    random.seed(config.seed)
    logger.info(
        "[worker={}] worker開始: games={}, seed={}, output={}",
        config.worker_id,
        config.games,
        config.seed,
        config.output_path,
    )
    training_config = TabularTrainingConfig(
        games=config.games,
        learning_rate=config.learning_rate,
        gamma=config.gamma,
        epsilon=config.epsilon,
        state_values_path=config.output_path,
        save_every=config.save_every,
    )
    try:
        SelfPlayTrainer().train(
            training_config,
            worker_id=config.worker_id,
            progress_interval=config.progress_interval,
        )
    except Exception:
        logger.exception("[worker={}] training継続不能", config.worker_id)
        raise
    logger.info(
        "[worker={}] worker終了: output={}",
        config.worker_id,
        config.output_path,
    )
    return config.output_path


def _resolve_console_level(log_level: str, debug: bool, quiet: bool) -> str:
    """CLIフラグからworkerのコンソールログレベルを決定します。"""
    if quiet:
        return "WARNING"
    if debug:
        return "DEBUG"
    return log_level


def _is_training_log(record: Record) -> bool:
    """training進捗として表示するログレコードかを返します。"""
    allowed_names = (
        "src.othello.train",
        "src.othello.training",
        "src.othello.players.cpu.rl.self_play_trainer",
        "src.othello.players.cpu.rl.state_value_store",
    )
    name = record["name"]
    return name is not None and name.startswith(allowed_names)
