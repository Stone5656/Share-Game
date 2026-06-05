"""pygame-ceを使用したオセロアプリケーションのエントリーポイントです。"""

import argparse

from loguru import logger

from src.othello.app import OthelloApp
from src.othello.config import NetworkConfig
from src.othello.constants import DEFAULT_HOST, DEFAULT_PORT
from src.othello.logger import setup_logger


def main() -> None:
    """アプリケーションのエントリーポイントです。

    Returns:
        None.
    """
    args: argparse.Namespace = _parse_args()
    setup_logger()
    network_config: NetworkConfig = NetworkConfig(
        host=args.host,
        port=args.port,
    )

    logger.info(
        "アプリ起動: host={}, port={}",
        network_config.host,
        network_config.port,
    )

    app: OthelloApp = OthelloApp(network_config)
    app.run()


def _parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析します。

    Returns:
        解析済みの引数Namespace。
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="pygame-ceを使用したオセロゲームを起動します。"
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=(
            "TCP通信に使うIPアドレスを指定します。"
            "Clientでは接続先、Serverでは待ち受けアドレスとして使用します。"
        ),
    )
    parser.add_argument(
        "--port",
        type=_parse_port,
        default=DEFAULT_PORT,
        help="TCPポート番号を指定します。",
    )

    return parser.parse_args()


def _parse_port(value: str) -> int:
    """文字列のTCPポート番号をintへ変換します。

    Args:
        value: コマンドライン引数で指定されたポート番号。

    Returns:
        TCPポート番号。

    Raises:
        argparse.ArgumentTypeError: ポート番号が不正な場合。
    """
    try:
        port: int = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("portは整数で指定してください。") from exc

    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("portは1から65535の範囲で指定してください。")

    return port


if __name__ == "__main__":
    main()
