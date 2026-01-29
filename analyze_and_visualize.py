"""
データ前処理と可視化スクリプト
職業紹介状況データを整形して分析・可視化
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent))
from src.database import AnalysisDatabase

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Hiragino Sans W3', 'Hiragino Sans W6']
plt.rcParams['axes.unicode_minus'] = False


def extract_numeric_data(file_path: str, sheet_name: int = 0) -> pd.DataFrame:
    """
    Excelファイルから数値データを抽出
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # 最初の4行はメタデータ
    # 行4（index=4）がデータの開始
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    # 列の変換
    data_rows = []
    
    for idx, row in df.iterrows():
        try:
            # 最初の列がラベル
            label = str(row.iloc[0]) if pd.notna(row.iloc[0]) else f"Data_{idx}"
            
            # 数値を抽出
            values = []
            for i in range(1, len(row)):
                val = row.iloc[i]
                try:
                    if pd.notna(val):
                        numeric_val = float(str(val).replace(',', ''))
                        values.append(numeric_val)
                except:
                    values.append(np.nan)
            
            if values and len([v for v in values if not pd.isna(v)]) > 0:
                data_rows.append({
                    'label': label,
                    'count': len([v for v in values if not pd.isna(v)]),
                    'values': values
                })
        except:
            pass
    
    return data_rows


def create_analysis_dataframe(data_rows: list) -> pd.DataFrame:
    """
    抽出したデータをDataFrameに整形
    """
    analysis_data = []
    
    for row_info in data_rows:
        label = row_info['label']
        values = row_info['values']
        
        # 年別データを集計
        numeric_values = [v for v in values if not pd.isna(v)]
        
        if numeric_values:
            analysis_data.append({
                'カテゴリ': label,
                '平均': np.mean(numeric_values),
                '最大': np.max(numeric_values),
                '最小': np.min(numeric_values),
                '合計': np.sum(numeric_values),
                'データ数': len(numeric_values)
            })
    
    return pd.DataFrame(analysis_data)


def main():
    """メイン処理"""
    print("=" * 70)
    print("職業紹介状況データ可視化分析")
    print("=" * 70)
    print()
    
    # 1. データを抽出
    print("[1/5] データを抽出中...")
    print("-" * 70)
    try:
        excel_path = Path(__file__).parent / "data" / "第20表.xlsx"
        data_rows = extract_numeric_data(str(excel_path), sheet_name=0)
        print(f"✓ {len(data_rows)}行のデータを抽出しました")
        print()
    except Exception as e:
        print(f"✗ エラー: {e}")
        return
    
    # 2. DataFrameを作成
    print("[2/5] DataFrameを作成中...")
    print("-" * 70)
    df_analysis = create_analysis_dataframe(data_rows)
    print(f"✓ 分析用データフレーム作成: {len(df_analysis)}行")
    print(f"  カラム: {list(df_analysis.columns)}")
    print()
    
    # 3. データをソート・表示
    print("[3/5] トップデータを表示...")
    print("-" * 70)
    df_top = df_analysis.nlargest(10, '合計')[['カテゴリ', '平均', '最大', '最小', '合計']]
    print(df_top.to_string())
    print()
    
    # 4. グラフを生成
    print("[4/5] グラフを生成中...")
    print("-" * 70)
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    graphs_generated = 0
    
    try:
        # グラフ1: 合計値のトップ10
        print("✓ グラフ1: 合計値ランキング（トップ10）")
        fig, ax = plt.subplots(figsize=(12, 6))
        df_plot = df_analysis.nlargest(10, '合計')
        ax.barh(range(len(df_plot)), df_plot['合計'].values, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_yticks(range(len(df_plot)))
        ax.set_yticklabels(df_plot['カテゴリ'].values)
        ax.set_xlabel('合計値')
        ax.set_title('職業紹介状況 - 合計値ランキング（トップ10）')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, v in enumerate(df_plot['合計'].values):
            ax.text(v, i, f" {int(v):,}", va='center')
        
        plt.tight_layout()
        fig.savefig(output_dir / "01_ranking_top10.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        graphs_generated += 1
    except Exception as e:
        print(f"  ⚠️  グラフ1生成に失敗: {e}")
    
    try:
        # グラフ2: 基本統計量の比較
        print("✓ グラフ2: 統計量の分布")
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        axes[0, 0].hist(df_analysis['平均'], bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('平均値の分布')
        axes[0, 0].set_xlabel('平均値')
        axes[0, 0].grid(True, alpha=0.3)
        
        axes[0, 1].hist(df_analysis['最大'], bins=20, color='lightcoral', edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('最大値の分布')
        axes[0, 1].set_xlabel('最大値')
        axes[0, 1].grid(True, alpha=0.3)
        
        axes[1, 0].hist(df_analysis['最小'], bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
        axes[1, 0].set_title('最小値の分布')
        axes[1, 0].set_xlabel('最小値')
        axes[1, 0].grid(True, alpha=0.3)
        
        axes[1, 1].boxplot([df_analysis['平均'], df_analysis['最大'], df_analysis['最小']], 
                          labels=['平均', '最大', '最小'])
        axes[1, 1].set_title('統計量の箱ひげ図')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        fig.savefig(output_dir / "02_statistics_distribution.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        graphs_generated += 1
    except Exception as e:
        print(f"  ⚠️  グラフ2生成に失敗: {e}")
    
    try:
        # グラフ3: 散布図（平均 vs 最大）
        print("✓ グラフ3: 平均値と最大値の関係")
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.scatter(df_analysis['平均'], df_analysis['最大'], s=100, alpha=0.6, edgecolor='black')
        ax.set_xlabel('平均値')
        ax.set_ylabel('最大値')
        ax.set_title('平均値と最大値の関係')
        ax.grid(True, alpha=0.3)
        
        # 相関係数を表示
        corr = df_analysis['平均'].corr(df_analysis['最大'])
        ax.text(0.05, 0.95, f'相関係数: {corr:.3f}', transform=ax.transAxes,
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        fig.savefig(output_dir / "03_scatter_mean_vs_max.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        graphs_generated += 1
    except Exception as e:
        print(f"  ⚠️  グラフ3生成に失敗: {e}")
    
    try:
        # グラフ4: 基本統計量
        print("✓ グラフ4: 基本統計量サマリー")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        stats_data = {
            '平均': [df_analysis['平均'].mean(), df_analysis['平均'].std()],
            '最大': [df_analysis['最大'].mean(), df_analysis['最大'].std()],
            '最小': [df_analysis['最小'].mean(), df_analysis['最小'].std()],
            '合計': [df_analysis['合計'].mean(), df_analysis['合計'].std()]
        }
        
        x = np.arange(len(stats_data))
        width = 0.35
        
        means = [stats_data[k][0] for k in stats_data]
        stds = [stats_data[k][1] for k in stats_data]
        
        ax.bar(x, means, width, label='平均', alpha=0.7, color='steelblue', edgecolor='black')
        ax.errorbar(x, means, stds, fmt='none', color='red', capsize=5, label='標準偏差')
        
        ax.set_xlabel('統計量')
        ax.set_ylabel('値')
        ax.set_title('各統計量の平均値と標準偏差')
        ax.set_xticks(x)
        ax.set_xticklabels(stats_data.keys())
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        fig.savefig(output_dir / "04_statistics_summary.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        graphs_generated += 1
    except Exception as e:
        print(f"  ⚠️  グラフ4生成に失敗: {e}")
    
    print()
    
    # 5. 結果をまとめる
    print("[5/5] 結果をまとめ中...")
    print("-" * 70)
    
    # 基本統計量
    print("\n【分析データの基本統計量】")
    print(f"  データ件数: {len(df_analysis)}")
    print(f"  平均値の平均: {df_analysis['平均'].mean():.2f}")
    print(f"  平均値の標準偏差: {df_analysis['平均'].std():.2f}")
    print(f"  最大値の平均: {df_analysis['最大'].mean():.2f}")
    print(f"  最小値の平均: {df_analysis['最小'].mean():.2f}")
    print(f"  合計値の平均: {df_analysis['合計'].mean():.2f}")
    
    # 相関分析
    print(f"\n【相関分析】")
    corr_mean_max = df_analysis['平均'].corr(df_analysis['最大'])
    corr_mean_min = df_analysis['平均'].corr(df_analysis['最小'])
    corr_max_min = df_analysis['最大'].corr(df_analysis['最小'])
    
    print(f"  平均 ↔ 最大: {corr_mean_max:.3f}")
    print(f"  平均 ↔ 最小: {corr_mean_min:.3f}")
    print(f"  最大 ↔ 最小: {corr_max_min:.3f}")
    
    print()
    print("=" * 70)
    print(f"✓ 可視化が完了しました ({graphs_generated}個のグラフを生成)")
    print("=" * 70)
    print(f"\n保存先: {output_dir}")
    print("\n生成されたファイル:")
    for file in sorted(output_dir.glob("*.png")):
        file_size = file.stat().st_size / 1024
        print(f"  - {file.name} ({file_size:.1f} KB)")


if __name__ == "__main__":
    main()
