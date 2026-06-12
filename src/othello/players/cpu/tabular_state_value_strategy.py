"""盤面状態ごとの記憶を使うCPU戦略を定義します。"""

import random
from dataclasses import dataclass, field

from loguru import logger

from src.othello.core.game_enums import Cell
from src.othello.core.game_result import GameResult
from src.othello.core.game_types import LegalMove, PlayerContext
from src.othello.core.move_simulator import simulate_move
from src.othello.players.cpu.rl.board_state_key import BoardStateKeyFactory
from src.othello.players.cpu.rl.state_value_store import StateValueStore
from src.othello.players.cpu.rl.tabular_td_learner import TabularTdLearner
from src.othello.players.cpu.rl.training_config import TabularTrainingConfig


@dataclass
class TabularStateValueCpuStrategy:
    """盤面ごとの記憶を使って手を選択するCPU戦略です。"""

    config: TabularTrainingConfig = TabularTrainingConfig()
    learning_enabled: bool = False
    auto_save: bool = False
    store: StateValueStore | None = None
    _key_factory: BoardStateKeyFactory = field(init=False)
    _learner: TabularTdLearner = field(init=False)
    _history: dict[Cell, list[str]] = field(init=False)

    def __post_init__(self) -> None:
        """状態価値テーブルとTD学習器を初期化します。"""
        self._key_factory = BoardStateKeyFactory()
        if self.store is None:
            self.store = StateValueStore(self.config.state_values_path)
            self.store.load()
        self._learner = TabularTdLearner(
            self.store,
            self.config.learning_rate,
            self.config.gamma,
        )
        self._history = {Cell.BLACK: [], Cell.WHITE: []}

    @property
    def name(self) -> str:
        """CPU戦略名を返します。"""
        return "Tabular State Value"

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
            raise ValueError("盤面記憶型CPUの手選択には盤面が必要です。")

        if self.learning_enabled:
            current_key = self._key_factory.create_key(
                context.board,
                context.current_player,
            )
            self._history[context.current_player].append(current_key)

        if random.random() < self.config.epsilon:
            selected_move = random.choice(context.legal_moves)
            logger.debug(
                "Tabular CPUが探索手を選択: player={}, position={}",
                context.current_player.name,
                selected_move.position,
            )
            return selected_move

        selected_move, value = self._select_best_move(context)
        logger.debug(
            "Tabular CPUが評価最大手を選択: player={}, value={}, position={}",
            context.current_player.name,
            value,
            selected_move.position,
        )
        return selected_move

    def on_game_finished(self, result: GameResult) -> None:
        """学習有効時に対局履歴をTD(0)で更新します。

        Args:
            result: 終了した対局の結果。
        """
        if not self.learning_enabled:
            return

        updated_state_count = 0
        for player in (Cell.BLACK, Cell.WHITE):
            reward = self._get_reward(player, result.winner)
            updated_state_count += self._update_history(player, reward)

        logger.info(
            "Tabular対局結果学習: winner={}, black={}, white={}, updated_states={}",
            result.winner.name if result.winner is not None else None,
            result.black_count,
            result.white_count,
            updated_state_count,
        )
        if self.auto_save and self.store is not None:
            self.store.save()
        self._history = {Cell.BLACK: [], Cell.WHITE: []}

    def _select_best_move(
        self,
        context: PlayerContext,
    ) -> tuple[LegalMove, float]:
        """次盤面の状態価値が最大の合法手を返します。"""
        if context.board is None or self.store is None:
            raise ValueError("盤面と状態価値テーブルが必要です。")

        evaluated_moves = (
            (
                move,
                self.store.get_value(
                    self._key_factory.create_key(
                        simulate_move(context.board, context.current_player, move),
                        context.current_player,
                    )
                ),
            )
            for move in context.legal_moves
        )
        return max(evaluated_moves, key=lambda item: item[1])

    def _update_history(self, player: Cell, reward: float) -> int:
        """指定プレイヤーの状態履歴を終局側から更新します。"""
        next_key: str | None = None
        history = self._history[player]

        for index, current_key in enumerate(reversed(history)):
            step_reward = reward if index == 0 else 0.0
            self._learner.update(current_key, step_reward, next_key)
            next_key = current_key

        return len(history)

    def _get_reward(self, player: Cell, winner: Cell | None) -> float:
        """勝敗から指定プレイヤーの報酬を返します。"""
        if winner is None:
            return 0.0
        return 1.0 if winner is player else -1.0
