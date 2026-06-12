"""盤面記憶型CPUのCLI向け自己対戦学習を定義します。"""

from loguru import logger

from src.othello.core.board import Board
from src.othello.core.game_engine import GameEngine
from src.othello.core.game_enums import Cell, GameStatus
from src.othello.core.game_types import PlayerContext
from src.othello.core.rules import LegalMoveScanner
from src.othello.players.cpu.rl.state_value_store import StateValueStore
from src.othello.players.cpu.rl.training_config import TabularTrainingConfig
from src.othello.players.cpu.tabular_state_value_strategy import (
    TabularStateValueCpuStrategy,
)


class SelfPlayTrainer:
    """CPU同士の自己対戦で状態価値の学習を進めます。"""

    def train(
        self,
        config: TabularTrainingConfig,
        *,
        worker_id: int = 0,
        progress_interval: int = 100,
    ) -> None:
        """指定設定に基づいて自己対戦学習を実行します。

        Args:
            config: 自己対戦回数とTD学習設定。
            worker_id: 進捗ログへ表示するworker番号。
            progress_interval: 進捗をINFO出力する対局間隔。
        """
        self._validate_config(config, progress_interval)
        store = StateValueStore(config.state_values_path)
        store.load()
        black_strategy = self._create_strategy(config, store)
        white_strategy = self._create_strategy(config, store)
        black_wins = 0
        white_wins = 0
        draws = 0

        logger.info(
            "self-play開始: worker={}, games={}, path={}",
            worker_id,
            config.games,
            config.state_values_path,
        )
        for game_number in range(1, config.games + 1):
            logger.debug(
                "self-playゲーム開始: worker={}, game={}/{}",
                worker_id,
                game_number,
                config.games,
            )
            engine = self._play_one_game(black_strategy, white_strategy)
            result = engine.get_game_result()
            black_strategy.on_game_finished(result)
            white_strategy.on_game_finished(result)
            if result.winner is Cell.BLACK:
                black_wins += 1
            elif result.winner is Cell.WHITE:
                white_wins += 1
            else:
                draws += 1
            logger.debug(
                "self-playゲーム終了: worker={}, game={}/{}, "
                "winner={}, black={}, white={}",
                worker_id,
                game_number,
                config.games,
                result.winner.name if result.winner is not None else None,
                result.black_count,
                result.white_count,
            )

            if game_number % config.save_every == 0:
                store.save()
            if game_number % progress_interval == 0 or game_number == config.games:
                logger.info(
                    "training進捗: worker={}, games={}/{}, black_win={}, "
                    "white_win={}, draw={}, states={}",
                    worker_id,
                    game_number,
                    config.games,
                    black_wins,
                    white_wins,
                    draws,
                    store.state_count,
                )

        if config.games % config.save_every != 0:
            store.save()
        logger.info(
            "self-play終了: worker={}, games={}, black_win={}, white_win={}, "
            "draw={}, state_count={}",
            worker_id,
            config.games,
            black_wins,
            white_wins,
            draws,
            store.state_count,
        )

    def _create_strategy(
        self,
        config: TabularTrainingConfig,
        store: StateValueStore,
    ) -> TabularStateValueCpuStrategy:
        """共有テーブルを使う学習戦略を作成します。"""
        return TabularStateValueCpuStrategy(
            config=config,
            learning_enabled=True,
            auto_save=False,
            store=store,
        )

    def _play_one_game(
        self,
        black_strategy: TabularStateValueCpuStrategy,
        white_strategy: TabularStateValueCpuStrategy,
    ) -> GameEngine:
        """盤面記憶型CPU同士の対局を1局実行します。"""
        board = Board()
        engine = GameEngine(
            board=board,
            current_player=Cell.BLACK,
            legal_move_scanner=LegalMoveScanner(),
        )
        strategies = {
            Cell.BLACK: black_strategy,
            Cell.WHITE: white_strategy,
        }

        while engine.status is GameStatus.PLAYING:
            if not engine.legal_moves:
                engine.apply_pass(engine.current_player)
                continue

            context = PlayerContext(
                current_player=engine.current_player,
                legal_moves=engine.legal_moves,
                board=board,
            )
            move = strategies[engine.current_player].select_move(context)
            if move is None:
                raise RuntimeError("合法手がある状態でCPUが手を選択しませんでした。")
            engine.apply_move(move.position)

        return engine

    def _validate_config(
        self,
        config: TabularTrainingConfig,
        progress_interval: int,
    ) -> None:
        """CLIから受け取った学習設定を検証します。"""
        if config.games < 1:
            raise ValueError("gamesは1以上で指定してください。")
        if config.save_every < 1:
            raise ValueError("save_everyは1以上で指定してください。")
        if progress_interval < 1:
            raise ValueError("progress_intervalは1以上で指定してください。")
        if not 0.0 <= config.epsilon <= 1.0:
            raise ValueError("epsilonは0.0から1.0で指定してください。")
