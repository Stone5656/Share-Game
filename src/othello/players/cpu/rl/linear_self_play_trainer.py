"""線形評価CPUの描画や通信を使わない自己対戦学習を定義します。"""

from loguru import logger

from src.othello.core.board import Board
from src.othello.core.game_engine import GameEngine
from src.othello.core.game_enums import Cell, GameStatus
from src.othello.core.game_types import PlayerContext
from src.othello.core.rules import LegalMoveScanner
from src.othello.players.cpu.learning_weighted_strategy import (
    LearningWeightedCpuStrategy,
)
from src.othello.players.cpu.rl.training_config import (
    DEFAULT_TRAINING_CONFIG,
    TrainingConfig,
)


class LinearSelfPlayTrainer:
    """線形評価CPU同士の自己対戦で学習を進めます。"""

    def __init__(
        self,
        config: TrainingConfig = DEFAULT_TRAINING_CONFIG,
    ) -> None:
        """自己対戦学習器を初期化します。

        Args:
            config: 強化学習設定。
        """
        self._strategy = LearningWeightedCpuStrategy(config)

    @property
    def weights(self) -> tuple[float, ...]:
        """現在の学習重みを返します。"""
        return self._strategy.weights

    def train(self, game_count: int) -> None:
        """指定回数の自己対戦を実行します。

        Args:
            game_count: 実行する自己対戦数。
        """
        if game_count < 1:
            raise ValueError("game_countは1以上で指定してください。")

        logger.info("線形評価self-play開始: game_count={}", game_count)
        for _game_index in range(game_count):
            self._play_one_game()
        logger.info(
            "線形評価self-play終了: game_count={}, weights={}",
            game_count,
            self._strategy.weights,
        )

    def _play_one_game(self) -> None:
        """自己対戦を1局実行します。"""
        board = Board()
        engine = GameEngine(
            board=board,
            current_player=Cell.BLACK,
            legal_move_scanner=LegalMoveScanner(),
        )

        while engine.status is GameStatus.PLAYING:
            if not engine.legal_moves:
                engine.apply_pass(engine.current_player)
                continue

            context = PlayerContext(
                current_player=engine.current_player,
                legal_moves=engine.legal_moves,
                board=board,
            )
            move = self._strategy.select_move(context)
            if move is None:
                raise RuntimeError("合法手がある状態でCPUが手を選択しませんでした。")
            engine.apply_move(move.position)

        self._strategy.on_game_finished(engine.get_game_result())
