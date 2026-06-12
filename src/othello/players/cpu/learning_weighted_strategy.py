"""TD学習する線形盤面評価CPU戦略を定義します。"""

import random
from dataclasses import dataclass, field

from loguru import logger

from src.othello.core.game_enums import Cell
from src.othello.core.game_result import GameResult
from src.othello.core.game_types import LegalMove, PlayerContext
from src.othello.core.move_simulator import simulate_move
from src.othello.players.cpu.rl.feature_extractor import (
    FEATURE_COUNT,
    BoardFeatures,
    FeatureExtractor,
)
from src.othello.players.cpu.rl.td_evaluator import TdEvaluator
from src.othello.players.cpu.rl.training_config import (
    DEFAULT_TRAINING_CONFIG,
    TrainingConfig,
)
from src.othello.players.cpu.rl.weight_store import WeightStore

INITIAL_WEIGHTS: tuple[float, ...] = (0.0,) * FEATURE_COUNT


@dataclass(frozen=True)
class TrainingStep:
    """1手分の学習履歴を表します。

    Attributes:
        player: 手番プレイヤー。
        features: 着手前の特徴量。
    """

    player: Cell
    features: BoardFeatures


@dataclass
class LearningWeightedCpuStrategy:
    """強化学習で更新される重みに基づいて手を選択するCPU戦略です。"""

    config: TrainingConfig = DEFAULT_TRAINING_CONFIG
    _feature_extractor: FeatureExtractor = field(init=False)
    _weight_store: WeightStore = field(init=False)
    _evaluator: TdEvaluator = field(init=False)
    _history: dict[Cell, list[TrainingStep]] = field(init=False)

    def __post_init__(self) -> None:
        """特徴抽出器、重み保存、TD評価器を初期化します。"""
        self._feature_extractor = FeatureExtractor()
        self._weight_store = WeightStore(
            self.config.weight_file_path,
            INITIAL_WEIGHTS,
        )
        self._evaluator = TdEvaluator(self._weight_store.load(), self.config)
        self._history = {Cell.BLACK: [], Cell.WHITE: []}
        logger.info(
            "学習CPU戦略を選択しました: epsilon={}, weights={}",
            self.config.epsilon,
            self._evaluator.weights,
        )

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        return "Learning Weighted"

    @property
    def weights(self) -> tuple[float, ...]:
        """現在の学習重みを返します。"""
        return self._evaluator.weights

    def select_move(self, context: PlayerContext) -> LegalMove | None:
        """現在の合法手からε-greedyで着手を選択します。

        Args:
            context: CPUが手を選ぶために必要な情報。

        Returns:
            選択した合法手。合法手がない場合はNone。

        Raises:
            ValueError: PlayerContextに盤面が含まれていない場合。
        """
        if not context.legal_moves:
            return None
        if context.board is None:
            raise ValueError("学習CPUの手選択には盤面が必要です。")

        current_features = self._feature_extractor.extract(
            context.board,
            context.current_player,
        )
        self._history[context.current_player].append(
            TrainingStep(context.current_player, current_features)
        )

        if random.random() < self.config.epsilon:
            selected_move = random.choice(context.legal_moves)
            logger.debug(
                "学習CPUが探索手を選択しました: player={}, position={}",
                context.current_player.name,
                selected_move.position,
            )
            return selected_move

        selected_move, best_value = self._select_best_move(context)
        logger.debug(
            "学習CPUが評価最大手を選択しました: player={}, value={}, position={}",
            context.current_player.name,
            best_value,
            selected_move.position,
        )
        return selected_move

    def on_game_finished(self, result: GameResult) -> None:
        """対局結果を使って履歴をTD(0)更新し、重みを保存します。

        Args:
            result: 終了した対局の結果。
        """
        logger.info(
            "学習CPUが対局結果を受信しました: winner={}, black={}, white={}",
            result.winner.name if result.winner is not None else None,
            result.black_count,
            result.white_count,
        )
        for player in (Cell.BLACK, Cell.WHITE):
            reward = self._get_reward(player, result.winner)
            logger.info("学習報酬: player={}, reward={}", player.name, reward)
            self._update_player_history(player, reward)

        self._weight_store.save(self._evaluator.weights)
        logger.info("学習後の重み: weights={}", self._evaluator.weights)
        self._history = {Cell.BLACK: [], Cell.WHITE: []}

    def _select_best_move(
        self,
        context: PlayerContext,
    ) -> tuple[LegalMove, float]:
        """評価値が最大の合法手と評価値を返します。"""
        if context.board is None:
            raise ValueError("学習CPUの手選択には盤面が必要です。")

        evaluated_moves = (
            (
                move,
                self._evaluator.evaluate(
                    self._feature_extractor.extract(
                        simulate_move(context.board, context.current_player, move),
                        context.current_player,
                    )
                ),
            )
            for move in context.legal_moves
        )
        return max(evaluated_moves, key=lambda item: item[1])

    def _update_player_history(self, player: Cell, reward: float) -> None:
        """指定プレイヤーの状態系列を終局側から更新します。"""
        steps = self._history[player]
        next_features: BoardFeatures | None = None

        for index, step in enumerate(reversed(steps)):
            step_reward = reward if index == 0 else 0.0
            self._evaluator.update(
                step.features,
                step_reward,
                next_features,
            )
            next_features = step.features

    def _get_reward(self, player: Cell, winner: Cell | None) -> float:
        """勝敗から指定プレイヤーの報酬を返します。"""
        if winner is None:
            return 0.0
        return 1.0 if winner is player else -1.0
