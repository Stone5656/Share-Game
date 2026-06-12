"""並列trainingのゲーム分配とworker出力をテストします。"""

import tempfile
import unittest
from pathlib import Path

from src.othello.training.parallel_trainer import (
    ParallelSelfPlayTrainer,
    ParallelTrainingConfig,
)
from src.othello.training.training_shard import load_version_2_shard


class ParallelTrainingTest(unittest.TestCase):
    """workerごとの独立shard生成を確認します。"""

    def test_single_worker_creates_version_2_shard(self) -> None:
        """workers=1でも独立したshardを生成します。"""
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "shards"
            config = ParallelTrainingConfig(
                games=1,
                workers=1,
                output_dir=output_dir,
                learning_rate=0.1,
                gamma=0.95,
                epsilon=0.1,
                save_every=1,
                seed=42,
                progress_interval=1,
            )

            paths = ParallelSelfPlayTrainer().train(config)

            self.assertEqual(
                paths,
                (output_dir / "state_values_worker_0.json",),
            )
            self.assertGreater(len(load_version_2_shard(paths[0])), 0)


if __name__ == "__main__":
    unittest.main()
