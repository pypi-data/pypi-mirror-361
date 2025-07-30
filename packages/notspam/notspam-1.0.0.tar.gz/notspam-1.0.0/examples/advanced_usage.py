"""
notspam 高度な使用例
"""

import notspam
import time
import threading
import logging

def advanced_example():
    print("=== notspam 高度な使用例 ===\n")
    
    # 1. 複数のロガーを使用
    print("1. 複数のロガーを使用")
    api_logger = notspam.create_logger(suppress_seconds=30, name="api")
    db_logger = notspam.create_logger(suppress_seconds=60, name="database")
    
    api_logger.info("API request received")
    db_logger.error("Database connection failed")
    
    # 2. ログレベルの動的変更
    print("\n2. ログレベルの動的変更")
    debug_logger = notspam.create_logger(suppress_seconds=10, name="debug_test")
    debug_logger.set_level(logging.DEBUG)
    
    debug_logger.debug("This debug message will be shown")
    debug_logger.set_level(logging.INFO)
    debug_logger.debug("This debug message will be hidden")
    
    # 3. スレッドセーフティのテスト
    print("\n3. スレッドセーフティのテスト")
    thread_logger = notspam.create_logger(suppress_seconds=5, name="thread_test")
    
    def worker(worker_id):
        for i in range(3):
            thread_logger.info(f"Worker {worker_id} message {i}")
            time.sleep(0.1)
    
    # 複数のスレッドを開始
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 全スレッドの完了を待つ
    for thread in threads:
        thread.join()
    
    # 4. パフォーマンステスト
    print("\n4. パフォーマンステスト")
    perf_logger = notspam.create_logger(suppress_seconds=60, name="performance")
    
    start_time = time.time()
    for i in range(1000):
        perf_logger.info("Performance test message")
    end_time = time.time()
    
    print(f"1000回の重複ログ処理時間: {end_time - start_time:.4f}秒")
    
    # 5. メモリ使用量の確認
    print("\n5. メモリ使用量の確認")
    memory_logger = notspam.create_logger(suppress_seconds=60, name="memory_test")
    
    # 大量の異なるメッセージを送信
    for i in range(100):
        memory_logger.info(f"Unique message {i}")
    
    print(f"100個のユニークメッセージ後の履歴数: {memory_logger.get_suppressed_count()}")
    
    # 履歴をクリア
    memory_logger.clear_history()
    print(f"履歴クリア後: {memory_logger.get_suppressed_count()}")
    
    # 6. フォーマット済みメッセージのテスト
    print("\n6. フォーマット済みメッセージのテスト")
    format_logger = notspam.create_logger(suppress_seconds=10, name="format_test")
    
    # 同じフォーマット結果は抑制される
    format_logger.info("User %s logged in", "alice")
    format_logger.info("User %s logged in", "alice")  # 抑制される
    format_logger.info("User %s logged in", "bob")    # 異なるユーザーなので出力される
    
    print("\n=== 高度な使用例完了 ===")

if __name__ == "__main__":
    advanced_example()