"""複数processによるself-play trainingを定義します。"""

import os
import secrets
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from src.othello.training.worker_runner import (
    WorkerTrainingConfig,
    run_training_worker,
)


@dataclass(frozen=True)
class ParallelTrainingConfig:
    """並列self-play training設定を表します。"""

    games: int
    workers: int
    output_dir: Path
    learning_rate: float
    gamma: float
    epsilon: float
    save_every: int
    seed: int | None
    log_level: str = "INFO"
    debug: bool = False
    quiet: bool = False
    progress_interval: int = 100


class ParallelSelfPlayTrainer:
    """複数プロセスでself-play trainingを実行します。"""

    def train(self, config: ParallelTrainingConfig) -> tuple[Path, ...]:
        """複数workerでself-playを実行します。

        Args:
            config: 全ゲーム数、worker数、出力先を含む設定。

        Returns:
            workerが作成したshardファイル一覧。
        """
        self._validate_config(config)
        active_workers = min(config.workers, config.games)
        cpu_count = os.cpu_count() or 1
        if config.workers > cpu_count:
            logger.warning(
                "worker数がCPU数を超えています: workers={}, cpu_count={}",
                config.workers,
                cpu_count,
            )
        if active_workers < config.workers:
            logger.warning(
                "ゲーム数よりworker数が多いためworker数を縮小: active_workers={}",
                active_workers,
            )

        config.output_dir.mkdir(parents=True, exist_ok=True)
        worker_configs = self._create_worker_configs(config, active_workers)
        logger.info(
            "parallel training開始: games={}, workers={}, output_dir={}",
            config.games,
            active_workers,
            config.output_dir,
        )
        for worker_config in worker_configs:
            logger.info(
                "worker割当: worker={}, games={}, output={}",
                worker_config.worker_id,
                worker_config.games,
                worker_config.output_path,
            )

        if active_workers == 1:
            paths = (run_training_worker(worker_configs[0]),)
        else:
            with ProcessPoolExecutor(max_workers=active_workers) as executor:
                paths = tuple(executor.map(run_training_worker, worker_configs))

        logger.info(
            "parallel training終了: workers={}, shard_count={}",
            active_workers,
            len(paths),
        )
        return paths

    def _create_worker_configs(
        self,
        config: ParallelTrainingConfig,
        worker_count: int,
    ) -> tuple[WorkerTrainingConfig, ...]:
        """全ゲーム数をworkerへ均等に分配します。"""
        base_games, remainder = divmod(config.games, worker_count)
        base_seed = config.seed
        if base_seed is None:
            base_seed = secrets.randbits(32)

        return tuple(
            WorkerTrainingConfig(
                worker_id=worker_id,
                games=base_games + int(worker_id < remainder),
                learning_rate=config.learning_rate,
                gamma=config.gamma,
                epsilon=config.epsilon,
                output_path=config.output_dir / f"state_values_worker_{worker_id}.json",
                save_every=config.save_every,
                seed=base_seed + worker_id,
                log_level=config.log_level,
                debug=config.debug,
                quiet=config.quiet,
                progress_interval=config.progress_interval,
            )
            for worker_id in range(worker_count)
        )

    def _validate_config(self, config: ParallelTrainingConfig) -> None:
        """並列training設定を検証します。"""
        if config.games < 1:
            raise ValueError("gamesは1以上で指定してください。")
        if config.workers < 1:
            raise ValueError("workersは1以上で指定してください。")
        if config.save_every < 1:
            raise ValueError("save_everyは1以上で指定してください。")
        if config.progress_interval < 1:
            raise ValueError("progress_intervalは1以上で指定してください。")
