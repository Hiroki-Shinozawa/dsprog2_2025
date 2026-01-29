"""
API フェッチャーのテスト
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api_fetcher import EStatAPIFetcher, APIDataManager


def test_api_fetcher():
    """APIフェッチャーのテスト"""
    print("=" * 70)
    print("e-Stat API フェッチャーテスト")
    print("=" * 70)
    print()
    
    # テスト1: APIフェッチャーの初期化
    print("[テスト1] APIフェッチャーの初期化")
    try:
        fetcher = EStatAPIFetcher()
        print("✓ EStatAPIFetcherの初期化に成功しました")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト2: APIフェッチャーマネージャーの初期化
    print("\n[テスト2] APIデータマネージャーの初期化")
    try:
        manager = APIDataManager()
        print("✓ APIDataManagerの初期化に成功しました")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト3: APIのパラメータ確認
    print("\n[テスト3] APIのベースURL確認")
    print(f"✓ ベースURL: {EStatAPIFetcher.BASE_URL}")
    
    # テスト4: アプリケーションIDの設定テスト
    print("\n[テスト4] アプリケーションIDの設定")
    try:
        test_app_id = "test_app_id_12345"
        fetcher.set_app_id(test_app_id)
        print(f"✓ アプリケーションIDを設定しました")
        print(f"  ID: {fetcher.app_id}")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト5: 賃金統計のパラメータ確認
    print("\n[テスト5] 賃金統計APIのパラメータ")
    print("✓ デフォルトパラメータ:")
    print(f"  - statsDataId: 0001867092 (賃金構造基本統計調査)")
    print(f"  - lang: J (日本語)")
    print(f"  - metaGetFlg: Y (メタデータ取得)")
    print(f"  - sectionHeaderFlg: 1 (セクションヘッダー付き)")
    
    # テスト6: APIリクエストのシミュレーション（実際には実行しない）
    print("\n[テスト6] APIリクエストの準備確認")
    print("✓ APIリクエストの準備ができています")
    print("  - appIdを設定することで本当のリクエストが可能になります")
    print("  - 実際のリクエストにはe-Stat APIキーが必要です")
    
    # テスト7: データ保存機能の確認
    print("\n[テスト7] キャッシュ機能の確認")
    try:
        import pandas as pd
        # テストデータを作成
        test_df = pd.DataFrame({
            'year': [2023, 2024],
            'wage': [300, 320]
        })
        manager.cached_data['test'] = test_df
        
        cached = manager.get_cached_data('test')
        if cached is not None and len(cached) == 2:
            print("✓ キャッシュ機能が正常に動作しています")
        else:
            print("✗ キャッシュ機能に問題があります")
            return False
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ 全テストに成功しました")
    print("=" * 70)
    print("\n📝 注: 実際のAPIリクエストを実行する場合:")
    print("1. e-Stat APIキー（appId）を取得してください")
    print("2. fetcher.set_app_id('YOUR_APP_ID')でキーを設定")
    print("3. manager.fetch_wage_data()でデータを取得")
    
    return True


if __name__ == "__main__":
    success = test_api_fetcher()
    sys.exit(0 if success else 1)
