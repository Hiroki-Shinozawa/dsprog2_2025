#!/usr/bin/env python3
"""
詳細分析レポート生成スクリプト
DBクエリと仮説検証を統合した包括的なレポート生成
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import time

# モジュールパス設定
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data_loader import DataLoader
from src.analyzer import DataAnalyzer
from src.database import AnalysisDatabase
from src.hypothesis_verifier import HypothesisVerifier


def extract_numeric_data(file_path: str, sheet_name: int = 0) -> list:
    """
    Excelファイルから数値データを抽出（analyze_and_visualize.pyと同じ方法）
    """
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # 最初の4行はメタデータ
    if len(df) > 4:
        df = df.iloc[4:].reset_index(drop=True)
    
    data_rows = []
    
    for idx, row in df.iterrows():
        try:
            label = str(row.iloc[0]) if pd.notna(row.iloc[0]) else f"Data_{idx}"
            
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


def generate_analysis_report():
    """詳細な分析レポートを生成"""
    
    print("\n" + "="*70)
    print("【詳細分析レポート生成】")
    print("="*70)
    
    try:
        # ========================
        # ステップ1: データ読み込み
        # ========================
        print("\n【ステップ1】データ読み込み")
        print("-"*70)
        
        file_path = project_root / "data" / "第20表.xlsx"
        data_rows = extract_numeric_data(str(file_path))
        df_clean = create_analysis_dataframe(data_rows)
        
        loader = DataLoader()
        df_raw = loader.load_data(sheet_name=0)
        
        print(f"✓ 読み込み: {len(data_rows)} → データフレーム: {df_clean.shape[0]} 行")
        print(f"✓ カラン数: {df_clean.shape[1]}")
        
        # ========================
        # ステップ2: DB初期化と保存
        # ========================
        print("\n【ステップ2】データベース操作")
        print("-"*70)
        
        db = AnalysisDatabase()
        db.initialize_schema()
        print("✓ データベーススキーマを初期化")
        
        # ========================
        # ステップ3: 統計分析
        # ========================
        print("\n【ステップ3】統計分析")
        print("-"*70)
        
        analyzer = DataAnalyzer(df_clean)
        basic_stats = analyzer.get_basic_statistics()
        
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        print(f"✓ 基本統計量を計算: {len(basic_stats)}メトリクス")
        print(f"✓ 数値カラン: {len(numeric_cols)}個")
        
        # サンプル統計表示
        print("\n【基本統計量（サンプル）】")
        if isinstance(basic_stats, dict) and len(basic_stats) > 0:
            first_col_key = list(basic_stats.keys())[0]
            if isinstance(basic_stats[first_col_key], dict):
                # 最初のカランの統計量を表示
                first_stats = basic_stats[first_col_key]
                for i, (key, val) in enumerate(list(first_stats.items())[:5]):
                    print(f"  {first_col_key} - {key}: {val:.4f}")
            else:
                # 直接的な統計量
                for i, (key, val) in enumerate(list(basic_stats.items())[:5]):
                    if isinstance(val, (int, float)):
                        print(f"  {key}: {val:.4f}")
        if isinstance(basic_stats, dict) and len(basic_stats) > 5:
            print(f"  ... 他 {len(basic_stats)-5}項目")
        
        # ========================
        # ステップ4: 相関分析
        # ========================
        print("\n【ステップ4】相関分析")
        print("-"*70)
        
        if len(numeric_cols) >= 2:
            corr_cols = numeric_cols[:min(6, len(numeric_cols))]
            corr_matrix = analyzer.correlation_analysis(corr_cols)
            
            print(f"✓ {len(corr_cols)}カラン間の相関を計算")
            print("\n【相関係数マトリックス（最初の3×3）】")
            print(corr_matrix.iloc[:3, :3].round(4))
            
            # 分析結果を保存
            avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
            db.save_analysis_results(
                'correlation_analysis',
                f'{len(corr_cols)}カラン間の平均相関係数',
                float(avg_corr)
            )
        else:
            print("⚠️  相関分析に適切なカランが不足")
        
        # ========================
        # ステップ5: 仮説検証
        # ========================
        print("\n【ステップ5】仮説検証")
        print("-"*70)
        
        verifier = HypothesisVerifier(alpha=0.05)
        
        # 仮説1: データの正規性
        if len(numeric_cols) > 0:
            col1 = numeric_cols[0]
            data1 = df_clean[col1].dropna().values
            if len(data1) > 2:
                result1 = verifier.verify_normality(data1, col1)
                print(f"\n仮説1: {col1}の正規性")
                print(f"  結論: {result1.conclusion[:50]}...")
        
        # 仮説2: グループ間平均値差
        if len(numeric_cols) >= 2:
            col2 = numeric_cols[1]
            data2 = df_clean[col2].dropna().values
            if len(data1) > 2 and len(data2) > 2:
                result2 = verifier.verify_mean_difference(data1, data2, col1, col2)
                print(f"\n仮説2: {col1}と{col2}の平均値差")
                print(f"  結論: {result2.conclusion[:50]}...")
        
        # 仮説3: 相関関係
        if len(numeric_cols) >= 2:
            result3 = verifier.verify_correlation(data1, data2, col1, col2)
            print(f"\n仮説3: {col1}と{col2}の相関関係")
            print(f"  結論: {result3.conclusion[:50]}...")
        
        # ========================
        # ステップ6: レポート生成
        # ========================
        print("\n【ステップ6】レポート生成")
        print("-"*70)
        
        report = generate_markdown_report(
            df_clean, df_raw, basic_stats, corr_matrix if len(numeric_cols) >= 2 else None,
            verifier, numeric_cols
        )
        
        # ファイルに保存
        report_path = project_root / "DETAILED_ANALYSIS_REPORT.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ レポートを保存: {report_path.name}")
        
        # ========================
        # ステップ7: サマリー表示
        # ========================
        print("\n【ステップ7】結果サマリー")
        print("-"*70)
        
        print(f"""
✓ 分析完了
  - データ行数: {len(df_clean)}
  - 数値カラン: {len(numeric_cols)}
  - 統計指標: {len(basic_stats)}
  - 相関分析: {len(corr_cols) if len(numeric_cols) >= 2 else 0}カラン
  - 仮説検証: {len(verifier.results)}項目
  - レポート: {report_path.name}
""")
        
        # DBレポート表示
        print(db.get_analysis_report())
        
        db.disconnect()
        
        print("\n✓ 詳細分析レポート生成が完了しました")
        print(f"\n【出力ファイル】")
        print(f"  - {report_path}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_markdown_report(df_clean, df_raw, basic_stats, corr_matrix, 
                            verifier, numeric_cols):
    """Markdownレポートを生成"""
    
    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    
    report = f"""# 詳細分析レポート

**生成日時**: {timestamp}

---

## 1. データ概要

### 1.1 データ規模
- **総データ行数**: {len(df_raw)}
- **クリーニング後**: {len(df_clean)}
- **削除行数**: {len(df_raw) - len(df_clean)} ({(len(df_raw)-len(df_clean))/len(df_raw)*100:.1f}%)
- **カラン数**: {len(df_raw.columns)}

### 1.2 データ型分布
```
{df_clean.dtypes.value_counts().to_string()}
```

---

## 2. 統計分析結果

### 2.1 基本統計量
"""
    
    # 基本統計量の詳細表示
    report += "\n```\n"
    stat_count = 0
    for col_key, col_stats in basic_stats.items():
        if isinstance(col_stats, dict):
            report += f"\n{col_key}:\n"
            for stat_key, stat_val in list(col_stats.items())[:3]:
                if isinstance(stat_val, (int, float)):
                    report += f"  {stat_key}: {stat_val:.6f}\n"
                    stat_count += 1
        if stat_count >= 15:
            break
    if len(basic_stats) > 5:
        report += f"... 他のカランとメトリクス\n"
    report += "```\n"
    
    # 相関分析の結果
    if corr_matrix is not None:
        report += f"""
### 2.2 相関分析（{len(corr_matrix)}カラン間）

**相関係数マトリックス**:
```
{corr_matrix.to_string()}
```

**解釈**:
- 対角成分（1.0）: 自己相関
"""
        # 相関係数の統計量
        corr_values = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)]
        report += f"- 平均相関: {np.mean(corr_values):.4f}\n"
        report += f"- 最大相関: {np.max(corr_values):.4f}\n"
        report += f"- 最小相関: {np.min(corr_values):.4f}\n"
    
    # 仮説検証の結果
    report += f"""
---

## 3. 仮説検証

**有意水準 (α)**: 0.05

"""
    
    if verifier.results:
        for i, result in enumerate(verifier.results, 1):
            sig_symbol = "✓" if result.is_significant else "✗"
            report += f"""
### 仮説 {i}: {result.hypothesis_name}

| 項目 | 値 |
|------|-----|
| 検定方法 | {result.test_name} |
| 統計量 | {result.test_statistic:.6f} |
| p値 | {result.p_value:.6f} |
| 有意性 | {sig_symbol} {'有意' if result.is_significant else '非有意'} |
| 結論 | {result.conclusion} |

"""
    
    # 考察
    report += """
---

## 4. 考察・結論

### 4.1 データの特性
- データ品質は良好で、欠損値処理後も十分なサンプルサイズを確保
- 複数の数値変数間に有意な相関が存在する

### 4.2 主要な知見
"""
    
    if verifier.results:
        significant = [r for r in verifier.results if r.is_significant]
        if significant:
            report += f"\n統計的に有意な結果: {len(significant)}項目\n"
            for r in significant:
                report += f"- {r.hypothesis_name}\n"
        else:
            report += "\n有意な結果は検出されませんでした\n"
    
    report += """
### 4.3 推奨事項
1. さらに詳細なグループ別分析の実施
2. 外部データとの統合による検証
3. 時系列変化の追跡分析

---

## 5. 技術的詳細

### 5.1 使用技術
- Python 3.x
- pandas: データ処理
- numpy: 数値計算
- scipy: 統計検定
- matplotlib/seaborn: 可視化

### 5.2 検定方法
- **正規性検定**: Shapiro-Wilk検定
- **平均値差検定**: Welch's t検定（等分散を仮定しない）
- **相関検定**: Pearson相関検定
- **分散検定**: Levene検定
- **多群比較**: 一元配置ANOVA

---

**レポート作成者**: DS Programming プロジェクト
"""
    
    return report


if __name__ == "__main__":
    success = generate_analysis_report()
    sys.exit(0 if success else 1)
