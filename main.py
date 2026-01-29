"""
メイン分析スクリプト
一般職業紹介状況データを読み込んで分析
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# srcモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import DataLoader
from src.analyzer import DataAnalyzer
from src.database import AnalysisDatabase


def main():
    """メイン処理"""
    print("=" * 70)
    print("一般職業紹介状況データ分析プログラム")
    print("=" * 70)
    print()
    
    # 1. データを読み込む
    print("[1/5] データを読み込み中...")
    print("-" * 70)
    try:
        loader = DataLoader()
        df = loader.load_data()
        print()
    except FileNotFoundError as e:
        print(f"✗ ファイルが見つかりません")
        print(f"  {e}")
        print(f"\n✓ 確認事項:")
        print(f"  - data/第20表.xlsx が存在しますか?")
        print(f"  - ファイルパス: {Path(__file__).parent}/data/第20表.xlsx")
        return
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        print(f"\n✓ 対処方法:")
        print(f"  1. Excelファイルが破損していないか確認してください")
        print(f"  2. ファイルが /最終課題/data/第20表.xlsx に存在することを確認してください")
        return
    
    # 2. データの確認
    print("[2/5] データの確認...")
    print("-" * 70)
    info = loader.get_column_info()
    print(f"データサイズ: {info['shape']}")
    print(f"カラム数: {len(info['columns'])}")
    print("\nカラム名:")
    for i, col in enumerate(info['columns'][:15], 1):
        print(f"  {i:2d}. {col}")
    if len(info['columns']) > 15:
        print(f"  ... 他{len(info['columns']) - 15}個")
    print()
    
    # 3. データをクリーニング
    print("[3/5] データをクリーニング中...")
    print("-" * 70)
    df_clean = loader.clean_data()
    print(f"クリーニング後のサイズ: {len(df_clean)}")
    print()
    
    # 4. 分析を実行
    print("[4/5] 分析を実行中...")
    print("-" * 70)
    try:
        analyzer = DataAnalyzer(df_clean)
        
        # 基本統計量
        print("基本統計量を計算...")
        basic_stats = analyzer.get_basic_statistics()
        
        # 相関分析
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            print("相関分析を実行...")
            corr = analyzer.correlation_analysis(numeric_cols[:5])  # 最初の5列のみ
        
        # レポート出力
        print("\n" + analyzer.get_summary_report())
        
    except Exception as e:
        print(f"✗ 分析エラー: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. データベースに保存
    print("[5/5] データベースに保存中...")
    print("-" * 70)
    try:
        db = AnalysisDatabase()
        
        # スキーマを初期化
        db.initialize_schema()
        
        print("✓ 分析完了")
        db.disconnect()
    except Exception as e:
        print(f"✗ データベース保存エラー: {e}")
    
    print()
    print("=" * 70)
    print("分析が完了しました")
    print("=" * 70)


if __name__ == "__main__":
    main()
