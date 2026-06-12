"""1 worker分のself-play trainingを実行します。"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

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


def run_training_worker(config: WorkerTrainingConfig) -> Path:
    """1 worker分のself-play trainingを実行します。

    Args:
        config: worker固有のゲーム数、seed、出力先。

    Returns:
        作成したshardファイルのパス。
    """
    _configure_worker_logger()
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
    SelfPlayTrainer().train(training_config)
    logger.info(
        "[worker={}] worker終了: output={}",
        config.worker_id,
        config.output_path,
    )
    return config.output_path


def _configure_worker_logger() -> None:
    """worker processのログをtraining関連のINFO以上へ限定します。"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        colorize=False,
        filter=_is_training_log,
        format="{time:HH:mm:ss} | {level:<8} | {message}",
    )


def _is_training_log(record: Record) -> bool:
    """training進捗として表示するログレコードかを返します。"""
    allowed_names = (
        "src.othello.training",
        "src.othello.players.cpu.rl.self_play_trainer",
        "src.othello.players.cpu.rl.state_value_store",
        "src.othello.players.cpu.tabular_state_value_strategy",
    )
    name = record["name"]
    return name is not None and name.startswith(allowed_names)
