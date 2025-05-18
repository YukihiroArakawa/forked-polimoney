"""
ユーティリティ関数モジュール

政治資金収支報告書ダウンロードスクリプトで使用するユーティリティ関数を提供します。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from .config import YEAR_PATTERNS

# ロガーの設定
logger = logging.getLogger(__name__)


def setup_logger(log_level: str) -> None:
    """
    ロガーを設定する

    Args:
        log_level (str): ログレベル(DEBUG, INFO, WARNING, ERROR)

    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        error_msg = f"Invalid log level: {log_level}"
        raise TypeError(error_msg)

    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)

    # フォーマッタの設定
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    console_handler.setFormatter(formatter)

    # ハンドラの追加。既存のハンドラがあれば削除
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(console_handler)

    logger.debug("ロガーを設定しました。レベル: %s", log_level.upper())


def create_directory(directory: str | Path) -> bool:
    """
    ディレクトリを作成する(存在しない場合)

    Args:
        directory (Union[str, Path]): 作成するディレクトリのパス

    Returns:
        bool: 作成成功時はTrue、失敗時はFalse

    """
    try:
        path = Path(directory)
        # 既に存在する場合は成功とみなす
        if path.exists() and path.is_dir():
            logger.debug("ディレクトリは既に存在します: %s", directory)
            return True
        path.mkdir(parents=True, exist_ok=True)
        logger.debug("ディレクトリを作成しました: %s", directory)
    except (PermissionError, OSError) as e:
        logger.exception("ディレクトリの作成に失敗しました: %s", directory, exc_info=e)
        return False
    return True


def sanitize_filename(filename: str) -> str:
    """
    ファイル名を安全な形式に変換する

    Args:
        filename (str): 元のファイル名

    Returns:
        str: 安全な形式に変換されたファイル名

    """
    # 不正な文字を置換
    invalid_chars = r'[\\/*?:"<>|]'
    sanitized = re.sub(invalid_chars, "_", filename)

    # 長すぎる場合は切り詰め(Windows の制限は 255 文字)
    max_length = 240  # 拡張子や区切り文字のための余裕を持たせる
    if len(sanitized) > max_length:
        path = Path(sanitized)
        stem = path.stem
        suffix = path.suffix
        sanitized = stem[: max_length - len(suffix)] + suffix

    return sanitized


def extract_year_from_url(url: str) -> str | None:
    """
    URLから公表年を抽出する

    Args:
        url (str): 公表ページのURL

    Returns:
        str | None: 抽出された公表年(例: R5)、抽出できない場合はNone

    """
    # URLから年度を抽出するパターン
    for pattern in YEAR_PATTERNS:
        match = re.search(pattern, url)
        if match:
            # 令和X年分 の場合
            if len(match.groups()) == 1:
                year_num = int(match.group(1))
                return f"R{year_num}"
            # 令和X~Y年分 の場合は最新の年を使用
            multi_year_group_count = 2
            if len(match.groups()) == multi_year_group_count:
                year_num = max(int(match.group(1)), int(match.group(2)))
                return f"R{year_num}"

    # パターンにマッチしない場合はURLから年を推測
    # SS20241129 のような形式から年を推測(2024年の場合はR6)
    ss_match = re.search(r"SS(\d{4})", url)
    if ss_match:
        year = int(ss_match.group(1))
        reiwa_year = year - 2018  # 2019年が令和元年
        return f"R{reiwa_year}"

    logger.warning("URLから公表年を抽出できませんでした: %s", url)
    return None
