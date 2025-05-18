"""
robots.txtパーサーモジュール

Webサイトのrobots.txtファイルを解析し、アクセス可能かどうかを判断するクラスを提供します。
"""

from __future__ import annotations

import logging
import time
import urllib.robotparser
from urllib.parse import urlparse

# ロガーの設定
logger = logging.getLogger(__name__)


class RobotsChecker:
    """robots.txtチェッカークラス"""

    def __init__(self, user_agent: str) -> None:
        """
        初期化

        Args:
            user_agent: ユーザーエージェント

        """
        self.user_agent = user_agent
        self.parsers: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.last_checked: dict[str, float] = {}
        self.check_interval = 86400  # 1日(秒)

    def can_fetch(self, url: str) -> bool:
        """
        URLにアクセス可能かどうかを確認

        Args:
            url: 確認するURL

        Returns:
            bool: アクセス可能な場合はTrue、そうでない場合はFalse

        """
        # URLからドメイン部分を抽出
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # ドメインごとにRobotFileParserを管理
        if domain not in self.parsers or self._should_refresh(domain):
            self._init_parser(domain)

        # アクセス可能かどうかを確認
        try:
            can_fetch = self.parsers[domain].can_fetch(self.user_agent, url)
            if not can_fetch:
                logger.warning("robots.txtによりアクセスが禁止されています: %s", url)
        except OSError:
            logger.exception(
                "robots.txtの確認中にエラーが発生しました: %s",
                url,
            )

        return True

    def get_crawl_delay(self, url: str) -> float | None:
        """
        クロール遅延を取得

        Args:
            url: 確認するURL

        Returns:
            float | None: クロール遅延(秒)、設定されていない場合はNone

        """
        # URLからドメイン部分を抽出
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # ドメインごとにRobotFileParserを管理
        if domain not in self.parsers or self._should_refresh(domain):
            self._init_parser(domain)

        # クロール遅延を取得
        delay = None
        try:
            crawl_delay = self.parsers[domain].crawl_delay(self.user_agent)
            if crawl_delay is not None:
                # 文字列の場合はfloatに変換
                delay = float(crawl_delay)
                logger.debug("robots.txtで指定されたクロール遅延: %s秒", delay)
        except (OSError, ValueError, TypeError):
            logger.exception(
                "クロール遅延の取得中にエラーが発生しました: %s",
                url,
            )
        return delay

    def _init_parser(self, domain: str) -> None:
        """
        パーサーを初期化

        Args:
            domain: ドメイン

        """
        try:
            parser = urllib.robotparser.RobotFileParser()
            robots_url = f"{domain}/robots.txt"
            parser.set_url(robots_url)
            logger.info("robots.txtを取得しています: %s", robots_url)
            parser.read()
            self.parsers[domain] = parser
            self.last_checked[domain] = time.time()
            logger.debug("robots.txtを解析しました: %s", robots_url)
        except OSError:
            logger.exception("robots.txtの取得に失敗しました: %s", domain)
            # エラーの場合は空のパーサーを設定
            self.parsers[domain] = urllib.robotparser.RobotFileParser()
            self.last_checked[domain] = time.time()

    def _should_refresh(self, domain: str) -> bool:
        """
        パーサーを更新すべきかどうかを判断

        Args:
            domain: ドメイン

        Returns:
            bool: 更新すべき場合はTrue、そうでない場合はFalse

        """
        if domain not in self.last_checked:
            return True

        current_time = time.time()
        return (current_time - self.last_checked[domain]) > self.check_interval
