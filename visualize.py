"""
可視化スクリプト
データを読み込んで、グラフやチャートを生成
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# srcモジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loader import DataLoader
from src.analyzer import DataAnalyzer
from src.database import AnalysisDatabase

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Hiragino Sans W3', 'Hiragino Sans W6']
plt.rcParams['axes.unicode_minus'] = False


def main():
    """メイン処理"""
    print("=" * 70)
    print("一般職業紹介状況データ可視化プログラム")
    print("=" * 70)
    print()
    
    # 1. データを読み込む
    print("[1/4] データを読み込み中...")
    print("-" * 70)
    try:
        loader = DataLoader()
        df = loader.load_data()
        print(f"✓ データを読み込みました: {df.shape}")
        print()
    except FileNotFoundError as e:
        print(f"✗ ファイルが見つかりません: {e}")
        return
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        return
    
    # 2. データをクリーニング
    print("[2/4] データをクリーニング中...")
    print("-" * 70)
    df_clean = loader.clean_data()
    print(f"✓ クリーニング完了: {len(df_clean)}行 × {len(df_clean.columns)}列")
    print()
    
    # 3. 分析を実行
    print("[3/4] 分析を実行中...")
    print("-" * 70)
    analyzer = DataAnalyzer(df_clean)
    
    # 基本統計量
    print("✓ 基本統計量を計算...")
    basic_stats = analyzer.get_basic_statistics()
    
    # 数値カランを取得
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    print(f"✓ 数値カラン数: {len(numeric_cols)}")
    
    # 相関分析
    if len(numeric_cols) >= 2:
        print("✓ 相関分析を実行...")
        corr_cols = numeric_cols[:min(8, len(numeric_cols))]
        corr = analyzer.correlation_analysis(corr_cols)
    
    print()
    
    # 4. グラフを生成
    print("[4/4] グラフを生成中...")
    print("-" * 70)
    
    # 出力ディレクトリを作成
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # グラフの生成
    graphs_generated = 0
    
    # 1. 分布グラフ
    if len(numeric_cols) > 0:
        try:
            col = numeric_cols[0]
            print(f"✓ 分布グラフを生成: {col}")
            fig = analyzer.plot_distribution(col, bins=30)
            fig.savefig(output_dir / "01_distribution.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            graphs_generated += 1
        except Exception as e:
            print(f"  ⚠️  分布グラフの生成に失敗: {e}")
    
    # 2. 相関係数ヒートマップ
    if len(numeric_cols) >= 2:
        try:
            print(f"✓ 相関係数ヒートマップを生成")
            fig = analyzer.plot_correlation_heatmap(corr_cols)
            fig.savefig(output_dir / "02_correlation_heatmap.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            graphs_generated += 1
        except Exception as e:
            print(f"  ⚠️  ヒートマップの生成に失敗: {e}")
    
    # 3. 散布図
    if len(numeric_cols) >= 2:
        try:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            print(f"✓ 散布図を生成: {x_col} vs {y_col}")
            fig = analyzer.plot_scatter(x_col, y_col)
            fig.savefig(output_dir / "03_scatter_plot.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
            graphs_generated += 1
        except Exception as e:
            print(f"  ⚠️  散布図の生成に失敗: {e}")
    
    # 4. 棒グラフ
    if len(numeric_cols) > 0:
        categorical_cols = df_clean.select_dtypes(include=['object']).columns.tolist()
        if len(categorical_cols) > 0:
            try:
                cat_col = categorical_cols[0]
                num_col = numeric_cols[0]
                print(f"✓ 棒グラフを生成: {cat_col}別{num_col}")
                fig = analyzer.plot_bar_chart(cat_col, num_col)
                fig.savefig(output_dir / "04_bar_chart.png", dpi=300, bbox_inches='tight')
                plt.close(fig)
                graphs_generated += 1
            except Exception as e:
                print(f"  ⚠️  棒グラフの生成に失敗: {e}")
    
    print()
    print(f"✓ {graphs_generated}個のグラフを生成しました")
    print(f"  保存先: {output_dir}")
    print()
    
    # 5. サマリーレポート
    print("=" * 70)
    print("分析サマリー")
    print("=" * 70)
    print(analyzer.get_summary_report())
    
    print()
    print("=" * 70)
    print("✓ 可視化が完了しました")
    print("=" * 70)
    print(f"\n生成されたファイル:")
    for file in sorted(output_dir.glob("*.png")):
        print(f"  - {file.name}")


if __name__ == "__main__":
    main()
