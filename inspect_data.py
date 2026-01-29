"""
データ構造確認スクリプト
Excelファイルの構造を詳細に分析
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from src.data_loader import DataLoader


def main():
    """メイン処理"""
    print("=" * 70)
    print("データ構造詳細分析")
    print("=" * 70)
    print()
    
    loader = DataLoader()
    
    # シート一覧
    sheets = loader.get_sheet_names()
    print(f"[1] Excelシート一覧: {len(sheets)}個")
    for i, sheet in enumerate(sheets, 1):
        print(f"    {i}. {sheet}")
    print()
    
    # 各シートのサイズを確認
    print("[2] 各シートのサイズ:")
    for sheet in sheets:
        df = pd.read_excel(loader.excel_path, sheet_name=sheet)
        print(f"    {sheet}: {df.shape}")
    print()
    
    # 最初のシートを詳細分析
    print("[3] 最初のシート（第１表）の詳細分析:")
    df = loader.load_data(sheet_name=0)
    print(f"    形状: {df.shape}")
    print(f"    行数: {len(df)}")
    print(f"    列数: {len(df.columns)}")
    print()
    
    # データ型の分布
    print("[4] データ型の分布:")
    dtype_dist = df.dtypes.value_counts()
    for dtype, count in dtype_dist.items():
        print(f"    {dtype}: {count}個")
    print()
    
    # 最初の数行を表示
    print("[5] データの最初の5行:")
    print(df.head())
    print()
    
    # 列の詳細情報
    print("[6] 列情報（最初の10列）:")
    for i, col in enumerate(df.columns[:10], 1):
        print(f"    {i:2d}. {col}")
        print(f"        データ型: {df[col].dtype}")
        print(f"        非null数: {df[col].count()}/{len(df)}")
        print(f"        サンプル値: {df[col].iloc[0]}")
    print()
    
    # 数値データの抽出を試みる
    print("[7] 数値データの検出:")
    numeric_cols = []
    for col in df.columns:
        try:
            pd.to_numeric(df[col], errors='coerce')
            non_null = df[col].notna().sum()
            if non_null > 0:
                numeric_cols.append((col, non_null))
        except:
            pass
    
    if numeric_cols:
        print(f"    検出された数値列: {len(numeric_cols)}個")
        for col, count in numeric_cols[:5]:
            print(f"    - {col}: {count}行のデータ")
    else:
        print(f"    ✗ 数値列が見つかりません")
    print()
    
    # データの可視化に適したシートを探す
    print("[8] 最適なシートの検索:")
    best_sheet = None
    best_numeric_count = 0
    
    for sheet in sheets:
        df_sheet = pd.read_excel(loader.excel_path, sheet_name=sheet)
        numeric_count = len(df_sheet.select_dtypes(include=[np.number]).columns)
        print(f"    {sheet}: 数値列 {numeric_count}個")
        
        if numeric_count > best_numeric_count:
            best_numeric_count = numeric_count
            best_sheet = sheet
    
    if best_sheet:
        print(f"\n    ✓ 推奨シート: {best_sheet} ({best_numeric_count}列)")
    print()
    
    # 推奨シートのデータを表示
    if best_sheet:
        print(f"[9] 推奨シート({best_sheet})の分析:")
        df_best = pd.read_excel(loader.excel_path, sheet_name=best_sheet)
        print(f"    形状: {df_best.shape}")
        print(f"    数値列: {len(df_best.select_dtypes(include=[np.number]).columns)}")
        print()
        print("    最初の5行:")
        print(df_best.head())


if __name__ == "__main__":
    main()
