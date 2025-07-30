"""
notspam テストスイート
"""

import unittest
import time
import logging
from io import StringIO
import sys

# テスト対象のモジュールをインポート
sys.path.insert(0, '/app/notspam-library')
from notspam import get_logger, create_logger, NotSpamLogger


class TestNotSpamLogger(unittest.TestCase):
    """NotSpamLoggerのテストクラス"""
    
    def setUp(self):
        """テストの前処理"""
        # テスト用のStringIOハンドラーを作成
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)
        
    def tearDown(self):
        """テストの後処理"""
        self.log_stream.close()
        
    def test_basic_suppression(self):
        """基本的な抑制機能のテスト"""
        logger = create_logger(suppress_seconds=1, name="test_basic")
        
        # 同じロガーのハンドラーを全て削除
        logger._logger.handlers.clear()
        logger._logger.addHandler(self.handler)
        
        # 最初のログは出力される
        logger.info("test message")
        self.assertIn("test message", self.log_stream.getvalue())
        
        # ログストリームをクリア
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        # 同じメッセージは抑制される
        logger.info("test message")
        self.assertEqual("", self.log_stream.getvalue())
        
    def test_different_messages(self):
        """異なるメッセージは抑制されないテスト"""
        logger = create_logger(suppress_seconds=60, name="test_different")
        logger._logger.handlers.clear()
        logger._logger.addHandler(self.handler)
        
        # 異なるメッセージは両方出力される
        logger.info("message 1")
        logger.info("message 2")
        
        log_output = self.log_stream.getvalue()
        self.assertIn("message 1", log_output)
        self.assertIn("message 2", log_output)
        
    def test_time_window_expiry(self):
        """時間窓の期限切れテスト"""
        logger = create_logger(suppress_seconds=1, name="test_expiry")
        logger._logger.handlers.clear()
        logger._logger.addHandler(self.handler)
        
        # 最初のログ
        logger.info("expiry test")
        self.assertIn("expiry test", self.log_stream.getvalue())
        
        # 1秒待機
        time.sleep(1.1)
        
        # ログストリームをクリア
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        # 時間が経過したので再度出力される
        logger.info("expiry test")
        self.assertIn("expiry test", self.log_stream.getvalue())
        
    def test_all_log_levels(self):
        """全ログレベルのテスト"""
        logger = create_logger(suppress_seconds=60, name="test_levels", level=logging.DEBUG)
        logger._logger.handlers.clear()
        logger._logger.addHandler(self.handler)
        
        # 全てのログレベルをテスト
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")
        
        log_output = self.log_stream.getvalue()
        self.assertIn("debug message", log_output)
        self.assertIn("info message", log_output)
        self.assertIn("warning message", log_output)
        self.assertIn("error message", log_output)
        self.assertIn("critical message", log_output)
        
    def test_suppressed_count(self):
        """抑制中のメッセージ数のテスト"""
        logger = create_logger(suppress_seconds=60, name="test_count")
        
        # 初期状態
        self.assertEqual(logger.get_suppressed_count(), 0)
        
        # メッセージを追加
        logger.info("message 1")
        self.assertEqual(logger.get_suppressed_count(), 1)
        
        logger.info("message 2")
        self.assertEqual(logger.get_suppressed_count(), 2)
        
        # 履歴をクリア
        logger.clear_history()
        self.assertEqual(logger.get_suppressed_count(), 0)
        
    def test_get_logger_singleton(self):
        """get_logger()のシングルトン動作テスト"""
        logger1 = get_logger()
        logger2 = get_logger()
        
        # 同じインスタンスが返される
        self.assertIs(logger1, logger2)
        
    def test_create_logger_different_instances(self):
        """create_logger()の異なるインスタンス生成テスト"""
        logger1 = create_logger(name="test1")
        logger2 = create_logger(name="test2")
        
        # 異なるインスタンスが返される
        self.assertIsNot(logger1, logger2)
        
    def test_message_formatting(self):
        """メッセージフォーマットのテスト"""
        logger = create_logger(suppress_seconds=60, name="test_format")
        logger._logger.handlers.clear()
        logger._logger.addHandler(self.handler)
        
        # % フォーマットのテスト
        logger.info("Hello %s", "world")
        self.assertIn("Hello world", self.log_stream.getvalue())
        
        # ログストリームをクリア
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        
        # 同じフォーマット済みメッセージは抑制される
        logger.info("Hello %s", "world")
        self.assertEqual("", self.log_stream.getvalue())


if __name__ == '__main__':
    unittest.main()