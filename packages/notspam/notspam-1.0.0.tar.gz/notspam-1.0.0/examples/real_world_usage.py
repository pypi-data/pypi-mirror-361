"""
実際のWebアプリケーションでの使用例
"""

import notspam
import time
import random

def simulate_web_app():
    """Webアプリケーションのログ使用例をシミュレート"""
    print("=== Webアプリケーションでの使用例 ===\n")
    
    # 各種ログ設定
    api_logger = notspam.create_logger(suppress_seconds=60, name="api")
    db_logger = notspam.create_logger(suppress_seconds=30, name="database")
    auth_logger = notspam.create_logger(suppress_seconds=120, name="auth")
    
    # 1. API リクエストログ
    print("1. API リクエストログのシミュレーション")
    for i in range(5):
        api_logger.info("GET /api/users request received")
        time.sleep(0.1)
    
    print("   ^ 最初のログのみ出力され、残りは抑制されます\n")
    
    # 2. データベース接続エラー
    print("2. データベース接続エラーのシミュレーション")
    for i in range(3):
        db_logger.error("Database connection failed: Connection timeout")
        time.sleep(0.1)
    
    print("   ^ 同じエラーが連続して発生しても、最初のログのみ出力されます\n")
    
    # 3. 認証ログ
    print("3. 認証ログのシミュレーション")
    users = ["alice", "bob", "charlie"]
    for user in users:
        auth_logger.info(f"User {user} logged in successfully")
        # 同じユーザーの重複ログイン（通常は抑制されるべき）
        auth_logger.info(f"User {user} logged in successfully")
    
    print("   ^ 各ユーザーの最初のログインのみ記録されます\n")
    
    # 4. 動的なエラーメッセージ
    print("4. 動的なエラーメッセージのテスト")
    error_logger = notspam.create_logger(suppress_seconds=30, name="error")
    
    # 異なるエラーコードは別々に記録される
    error_codes = [404, 500, 404, 500, 404]
    for code in error_codes:
        error_logger.error(f"HTTP Error {code}: Request failed")
        time.sleep(0.1)
    
    print("   ^ 異なるエラーコードは別々に記録されます\n")
    
    # 5. メモリ使用量の監視
    print("5. メモリ使用量の監視")
    memory_logger = notspam.create_logger(suppress_seconds=60, name="memory")
    
    # 大量のリクエストをシミュレート
    for i in range(50):
        if i % 10 == 0:
            memory_logger.info(f"Memory usage: {70 + random.randint(0, 20)}%")
        else:
            memory_logger.info("Memory usage: 75%")  # 同じメッセージが多数
    
    print(f"   メモリロガーの現在の履歴数: {memory_logger.get_suppressed_count()}")
    print("   ^ 繰り返しメッセージが抑制され、メモリ効率が保たれます\n")
    
    print("=== Webアプリケーション例完了 ===")

def simulate_monitoring_system():
    """モニタリングシステムの使用例"""
    print("\n=== モニタリングシステムでの使用例 ===\n")
    
    # システム監視用のロガー
    system_logger = notspam.create_logger(suppress_seconds=300, name="system_monitor")
    
    # 1. CPU使用率アラート
    print("1. CPU使用率アラートのシミュレーション")
    for i in range(10):
        if random.random() < 0.3:  # 30%の確率で高CPU使用率
            system_logger.warning("CPU usage exceeded 90%")
        time.sleep(0.1)
    
    print("   ^ 高CPU使用率のアラートが重複して送信されることを防ぎます\n")
    
    # 2. ディスク容量監視
    print("2. ディスク容量監視のシミュレーション")
    for i in range(5):
        system_logger.critical("Disk space critically low: 95% used")
        time.sleep(0.1)
    
    print("   ^ 同じクリティカルアラートの重複送信を防ぎます\n")
    
    # 3. サービス監視
    print("3. サービス監視のシミュレーション")
    services = ["web", "database", "cache", "worker"]
    for service in services:
        system_logger.error(f"Service {service} is not responding")
        # 同じサービスの重複エラー
        system_logger.error(f"Service {service} is not responding")
    
    print("   ^ 各サービスの最初のエラーのみ記録されます\n")
    
    print("=== モニタリングシステム例完了 ===")

if __name__ == "__main__":
    simulate_web_app()
    simulate_monitoring_system()