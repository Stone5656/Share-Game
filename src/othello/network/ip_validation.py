"""TCP通信で使用するIPアドレス検証処理を定義します。"""

from ipaddress import ip_address


def validate_ip_address(value: str) -> str:
    """IPアドレス文字列を検証して返します。

    Args:
        value: 検証対象のIPアドレス文字列。

    Returns:
        検証済みのIPアドレス文字列。

    Raises:
        ValueError: IPアドレスとして不正な場合。
    """
    try:
        ip_address(value)
    except ValueError as exc:
        raise ValueError("hostは有効なIPアドレスで指定してください。") from exc

    return value
