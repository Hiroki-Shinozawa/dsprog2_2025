"""
データローダーのユニットテスト
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import DataLoader


def test_data_loader():
    """データローダーのテスト"""
    print("=" * 70)
    print("データローダーテスト")
    print("=" * 70)
    print()
    
    # テスト1: DataLoaderの初期化
    print("[テスト1] DataLoaderの初期化")
    try:
        loader = DataLoader()
        print("✓ DataLoaderの初期化に成功しました")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト2: ファイルの存在確認
    print("\n[テスト2] ファイルの存在確認")
    if loader.excel_path.exists():
        print(f"✓ ファイルが存在します: {loader.excel_path}")
    else:
        print(f"✗ ファイルが見つかりません: {loader.excel_path}")
        return False
    
    # テスト3: シート名の取得
    print("\n[テスト3] シート名の取得")
    try:
        sheets = loader.get_sheet_names()
        print(f"✓ シート数: {len(sheets)}")
        for sheet in sheets[:5]:
            print(f"  - {sheet}")
        if len(sheets) > 5:
            print(f"  ... 他{len(sheets) - 5}個")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト4: データの読み込み
    print("\n[テスト4] データの読み込み")
    try:
        df = loader.load_data()
        print(f"✓ データを読み込みました")
        print(f"  形状: {df.shape}")
        print(f"  メモリ使用量: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト5: カラム情報の取得
    print("\n[テスト5] カラム情報の取得")
    try:
        info = loader.get_column_info()
        print(f"✓ カラム情報を取得しました")
        print(f"  カラム数: {len(info['columns'])}")
        print(f"  最初の5カラム: {info['columns'][:5]}")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト6: 欠損値の確認
    print("\n[テスト6] 欠損値の確認")
    try:
        null_counts = df.isnull().sum()
        null_pct = (null_counts / len(df) * 100).round(2)
        
        cols_with_nulls = null_counts[null_counts > 0]
        if len(cols_with_nulls) > 0:
            print(f"✓ 欠損値を検出しました:")
            for col in cols_with_nulls.head(5).index:
                print(f"  - {col}: {null_counts[col]}行 ({null_pct[col]}%)")
            if len(cols_with_nulls) > 5:
                print(f"  ... 他{len(cols_with_nulls) - 5}個")
        else:
            print("✓ 欠損値はありません")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    # テスト7: データ型の確認
    print("\n[テスト7] データ型の確認")
    try:
        print("✓ データ型:")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            print(f"  - {dtype}: {count}個")
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ 全テストに成功しました")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_data_loader()
    sys.exit(0 if success else 1)
