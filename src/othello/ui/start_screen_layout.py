"""開始画面のボタン配置を定義します。"""

import pygame

from src.othello.config import AppState, NetworkConfig
from src.othello.core.game_enums import CpuStrategyKind
from src.othello.ui.button import Button

BUTTON_WIDTH = 280
BUTTON_HEIGHT = 42
START_Y = 215
BUTTON_GAP = 7


def create_mode_buttons(network_config: NetworkConfig) -> dict[AppState, Button]:
    """ゲームモード選択ボタンを作成します。

    Args:
        network_config: TCP通信設定。

    Returns:
        AppStateごとのButton辞書。
    """
    labels = (
        (AppState.LOCAL_GAME, "Local Player vs Player"),
        (AppState.SERVER_GAME, "Server / White"),
        (AppState.CLIENT_GAME, "Client / Black"),
        (AppState.SERVER_CPU_GAME, "Server CPU / White"),
        (
            AppState.CLIENT_CPU_GAME,
            f"Client CPU / Black: {network_config.host}",
        ),
    )
    return {
        state: Button(
            rect=pygame.Rect(
                20,
                START_Y + (BUTTON_HEIGHT + BUTTON_GAP) * index,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
            ),
            label=label,
        )
        for index, (state, label) in enumerate(labels)
    }


def create_cpu_strategy_buttons() -> dict[CpuStrategyKind, Button]:
    """CPU戦略選択ボタンを作成します。

    Returns:
        CPU戦略種別ごとのButton辞書。
    """
    labels = (
        (CpuStrategyKind.RANDOM, "Random"),
        (CpuStrategyKind.GREEDY, "Greedy"),
        (CpuStrategyKind.CORNER_PRIORITY, "Corner Priority"),
        (CpuStrategyKind.WEIGHTED_BOARD, "Weighted Board"),
        (CpuStrategyKind.LEARNING_WEIGHTED, "Learning Weighted"),
        (CpuStrategyKind.TABULAR_STATE_VALUE, "Tabular State Value"),
    )
    return {
        kind: Button(
            rect=pygame.Rect(
                320,
                START_Y + (BUTTON_HEIGHT + BUTTON_GAP) * index,
                300,
                BUTTON_HEIGHT,
            ),
            label=f"CPU Strategy: {label}",
        )
        for index, (kind, label) in enumerate(labels)
    }
