"""
notspam コアライブラリ

一定時間内に同じログメッセージを抑制する軽量ログラッパー
"""

import logging
import time
import threading
from typing import Dict, Optional, Any


class NotSpamLogger:
    """
    一定時間内に同じログを出力しないログラッパー
    """
    
    def __init__(self, suppress_seconds: int = 60, name: Optional[str] = None, 
                 level: int = logging.INFO):
        """
        Args:
            suppress_seconds: 同じログを抑制する秒数（デフォルト：60秒）
            name: ロガー名（デフォルト：notspam）
            level: ログレベル（デフォルト：INFO）
        """
        self.suppress_seconds = suppress_seconds
        self.name = name or "notspam"
        
        # 内部用のPythonロガー
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(level)
        
        # ハンドラーが設定されていない場合はコンソールハンドラーを追加
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
        
        # ログの履歴を保存（メッセージ -> 最後のログ時刻）
        self._log_history: Dict[str, float] = {}
        
        # スレッドセーフティのためのロック
        self._lock = threading.Lock()
    
    def _should_suppress(self, message: str) -> bool:
        """
        メッセージを抑制すべきかチェック
        
        Args:
            message: ログメッセージ
            
        Returns:
            True if suppressed, False otherwise
        """
        current_time = time.time()
        
        with self._lock:
            # 過去のログ履歴をクリーンアップ（メモリ効率化）
            cutoff_time = current_time - self.suppress_seconds
            messages_to_remove = [
                msg for msg, timestamp in self._log_history.items()
                if timestamp < cutoff_time
            ]
            for msg in messages_to_remove:
                del self._log_history[msg]
            
            # 同じメッセージが最近ログされているかチェック
            if message in self._log_history:
                last_time = self._log_history[message]
                if current_time - last_time < self.suppress_seconds:
                    return True
            
            # 新しいログを記録
            self._log_history[message] = current_time
            return False
    
    def _log(self, level: int, message: str, *args, **kwargs):
        """
        内部ログメソッド
        
        Args:
            level: ログレベル
            message: ログメッセージ
            *args: 追加の引数
            **kwargs: 追加のキーワード引数
        """
        # メッセージを文字列に変換
        if args:
            try:
                formatted_message = message % args
            except (TypeError, ValueError):
                formatted_message = f"{message} {' '.join(str(arg) for arg in args)}"
        else:
            formatted_message = str(message)
        
        # 抑制チェック
        if not self._should_suppress(formatted_message):
            self._logger.log(level, formatted_message, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """DEBUGレベルのログ"""
        self._log(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """INFOレベルのログ"""
        self._log(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """WARNINGレベルのログ"""
        self._log(logging.WARNING, message, *args, **kwargs)
    
    def warn(self, message: str, *args, **kwargs):
        """WARNINGレベルのログ（エイリアス）"""
        self.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """ERRORレベルのログ"""
        self._log(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """CRITICALレベルのログ"""
        self._log(logging.CRITICAL, message, *args, **kwargs)
    
    def fatal(self, message: str, *args, **kwargs):
        """CRITICALレベルのログ（エイリアス）"""
        self.critical(message, *args, **kwargs)
    
    def set_level(self, level: int):
        """ログレベルを設定"""
        self._logger.setLevel(level)
    
    def get_suppressed_count(self) -> int:
        """現在抑制中のメッセージ数を取得"""
        with self._lock:
            return len(self._log_history)
    
    def clear_history(self):
        """ログ履歴をクリア"""
        with self._lock:
            self._log_history.clear()


# グローバルロガーインスタンス
_global_logger: Optional[NotSpamLogger] = None


def get_logger(suppress_seconds: int = 60, name: Optional[str] = None, 
               level: int = logging.INFO) -> NotSpamLogger:
    """
    NotSpamLoggerのインスタンスを取得
    
    Args:
        suppress_seconds: 同じログを抑制する秒数（デフォルト：60秒）
        name: ロガー名（デフォルト：notspam）
        level: ログレベル（デフォルト：INFO）
        
    Returns:
        NotSpamLogger インスタンス
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = NotSpamLogger(suppress_seconds, name, level)
    
    return _global_logger


def create_logger(suppress_seconds: int = 60, name: Optional[str] = None, 
                 level: int = logging.INFO) -> NotSpamLogger:
    """
    新しいNotSpamLoggerインスタンスを作成
    
    Args:
        suppress_seconds: 同じログを抑制する秒数（デフォルト：60秒）
        name: ロガー名（デフォルト：notspam）
        level: ログレベル（デフォルト：INFO）
        
    Returns:
        NotSpamLogger インスタンス
    """
    return NotSpamLogger(suppress_seconds, name, level)