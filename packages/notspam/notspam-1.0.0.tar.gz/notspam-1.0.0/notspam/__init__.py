"""
notspam - 一定時間内に同一ログを出さない超軽量ログラッパー

Usage:
    import notspam
    
    # デフォルト設定（60秒間）
    logger = notspam.get_logger()
    logger.info("This message will be suppressed if repeated within 60 seconds")
    
    # カスタム設定
    logger = notspam.get_logger(suppress_seconds=30, name="my_logger")
    logger.warning("Custom suppression time")
"""

from .core import NotSpamLogger, get_logger, create_logger

__version__ = "1.0.0"
__all__ = ["NotSpamLogger", "get_logger", "create_logger"]