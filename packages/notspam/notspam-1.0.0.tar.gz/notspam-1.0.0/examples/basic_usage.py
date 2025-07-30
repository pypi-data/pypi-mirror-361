"""
notspam 基本的な使用例
"""

import notspam
import time

def main():
    print("=== notspam 基本的な使用例 ===\n")
    
    # デフォルト設定（60秒間抑制）でロガーを作成
    logger = notspam.get_logger()
    
    print("1. 最初のログメッセージ（出力される）")
    logger.info("This is a test message")
    
    print("\n2. 同じメッセージを即座に送信（抑制される）")
    logger.info("This is a test message")
    
    print("\n3. 異なるメッセージ（出力される）")
    logger.info("This is a different message")
    
    print("\n4. 複数のログレベルをテスト")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    print("\n5. 同じエラーメッセージを連続送信（抑制される）")
    logger.error("Database connection failed")
    logger.error("Database connection failed")
    logger.error("Database connection failed")
    
    print("\n6. 現在抑制中のメッセージ数:", logger.get_suppressed_count())
    
    print("\n=== カスタム設定の例 ===\n")
    
    # 5秒間抑制の短いテスト
    short_logger = notspam.create_logger(suppress_seconds=5, name="short_test")
    
    print("7. 短い抑制時間のテスト（5秒）")
    short_logger.info("Short suppression test")
    short_logger.info("Short suppression test")  # 抑制される
    
    print("\n8. 5秒待機後...")
    time.sleep(5)
    short_logger.info("Short suppression test")  # 5秒後なので出力される
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    main()