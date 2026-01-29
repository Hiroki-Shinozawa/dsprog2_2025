"""
データ分析・可視化モジュール
統計分析とグラフ作成機能を提供
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['Hiragino Sans W3', 'Hiragino Sans W6']
plt.rcParams['axes.unicode_minus'] = False


class DataAnalyzer:
    """データ分析と可視化を行うクラス"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初期化
        
        Args:
            df: 分析対象のDataFrame
        """
        self.df = df.copy()
        self.analysis_results = {}
        self.figures = []
    
    def get_basic_statistics(self) -> Dict:
        """
        基本統計量を計算
        
        Returns:
            Dict: 基本統計量
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        stats_dict = {}
        for col in numeric_cols:
            stats_dict[col] = {
                '平均': self.df[col].mean(),
                '中央値': self.df[col].median(),
                '標準偏差': self.df[col].std(),
                '最小値': self.df[col].min(),
                '最大値': self.df[col].max(),
                'Q1': self.df[col].quantile(0.25),
                'Q3': self.df[col].quantile(0.75)
            }
        
        self.analysis_results['basic_stats'] = stats_dict
        return stats_dict
    
    def correlation_analysis(self, columns: List[str]) -> pd.DataFrame:
        """
        相関分析を実行
        
        Args:
            columns: 分析対象の列
        
        Returns:
            pd.DataFrame: 相関行列
        """
        corr_matrix = self.df[columns].corr()
        self.analysis_results['correlation'] = corr_matrix
        return corr_matrix
    
    def linear_regression(self, x_col: str, y_col: str) -> Dict:
        """
        線形回帰分析を実行
        
        Args:
            x_col: 説明変数
            y_col: 目的変数
        
        Returns:
            Dict: 回帰分析結果
        """
        # 欠損値を削除
        data = self.df[[x_col, y_col]].dropna()
        
        x = data[x_col].values
        y = data[y_col].values
        
        # 線形回帰
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        result = {
            '傾き': slope,
            '切片': intercept,
            '相関係数': r_value,
            'R²': r_value ** 2,
            'p値': p_value,
            '標準誤差': std_err
        }
        
        self.analysis_results['regression'] = result
        return result
    
    def group_comparison(self, group_col: str, value_col: str) -> Dict:
        """
        グループ別の比較分析
        
        Args:
            group_col: グループ分け用の列
            value_col: 比較対象の値列
        
        Returns:
            Dict: グループ別統計
        """
        groups = self.df.groupby(group_col)[value_col].agg([
            'count', 'mean', 'std', 'min', 'max'
        ])
        
        self.analysis_results['group_comparison'] = groups
        return groups
    
    def plot_distribution(self, column: str, bins: int = 30) -> plt.Figure:
        """
        分布をプロット
        
        Args:
            column: 列名
            bins: ヒストグラムのビン数
        
        Returns:
            plt.Figure: 図オブジェクト
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        
        # ヒストグラム
        axes[0].hist(self.df[column].dropna(), bins=bins, edgecolor='black', alpha=0.7)
        axes[0].set_xlabel(column)
        axes[0].set_ylabel('度数')
        axes[0].set_title(f'{column}の分布')
        axes[0].grid(True, alpha=0.3)
        
        # 箱ひげ図
        axes[1].boxplot(self.df[column].dropna())
        axes[1].set_ylabel(column)
        axes[1].set_title(f'{column}の箱ひげ図')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_scatter(self, x_col: str, y_col: str, 
                    hue_col: Optional[str] = None) -> plt.Figure:
        """
        散布図をプロット
        
        Args:
            x_col: X軸の列
            y_col: Y軸の列
            hue_col: 色分け用の列（オプション）
        
        Returns:
            plt.Figure: 図オブジェクト
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if hue_col:
            for group in self.df[hue_col].unique():
                mask = self.df[hue_col] == group
                ax.scatter(self.df[mask][x_col], self.df[mask][y_col], 
                          label=str(group), alpha=0.6)
            ax.legend()
        else:
            ax.scatter(self.df[x_col], self.df[y_col], alpha=0.6)
        
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'{x_col}と{y_col}の関係')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_correlation_heatmap(self, columns: Optional[List[str]] = None) -> plt.Figure:
        """
        相関係数のヒートマップをプロット
        
        Args:
            columns: 対象列（Noneの場合は数値列全て）
        
        Returns:
            plt.Figure: 図オブジェクト
        """
        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        corr = self.df[columns].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, ax=ax, cbar_kws={'label': '相関係数'})
        ax.set_title('相関係数マトリックス')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def plot_bar_chart(self, x_col: str, y_col: str, 
                      title: Optional[str] = None) -> plt.Figure:
        """
        棒グラフをプロット
        
        Args:
            x_col: X軸の列
            y_col: Y軸の列
            title: タイトル
        
        Returns:
            plt.Figure: 図オブジェクト
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        data = self.df.groupby(x_col)[y_col].sum().sort_values(ascending=False)
        ax.bar(range(len(data)), data.values, color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data.index, rotation=45, ha='right')
        ax.set_ylabel(y_col)
        ax.set_title(title or f'{x_col}別{y_col}')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        self.figures.append(fig)
        return fig
    
    def get_summary_report(self) -> str:
        """
        分析結果サマリーレポートを取得
        
        Returns:
            str: レポートテキスト
        """
        report = "=" * 60 + "\n"
        report += "データ分析レポート\n"
        report += "=" * 60 + "\n\n"
        
        report += f"データ形状: {self.df.shape[0]}行 × {self.df.shape[1]}列\n\n"
        
        if 'basic_stats' in self.analysis_results:
            report += "基本統計量:\n"
            for col, stats_dict in self.analysis_results['basic_stats'].items():
                report += f"\n{col}:\n"
                for stat_name, value in stats_dict.items():
                    report += f"  {stat_name}: {value:.4f}\n"
        
        if 'correlation' in self.analysis_results:
            report += "\n相関行列:\n"
            report += str(self.analysis_results['correlation']) + "\n"
        
        if 'regression' in self.analysis_results:
            report += "\n線形回帰結果:\n"
            for key, value in self.analysis_results['regression'].items():
                report += f"  {key}: {value:.6f}\n"
        
        report += "\n" + "=" * 60 + "\n"
        return report
    
    def save_figures(self, output_dir: str = "output"):
        """
        図を保存
        
        Args:
            output_dir: 出力ディレクトリ
        """
        from pathlib import Path
        Path(output_dir).mkdir(exist_ok=True)
        
        for i, fig in enumerate(self.figures):
            fig.savefig(f"{output_dir}/figure_{i+1}.png", dpi=300, bbox_inches='tight')
            print(f"✓ 図を保存しました: {output_dir}/figure_{i+1}.png")


if __name__ == "__main__":
    print("⚠️  このモジュールは実データが必要です")
    print("使用方法:")
    print("  1. data_loader.pyでデータを読み込んでください")
    print("  2. 読み込んだDataFrameをDataAnalyzerに渡してください")
    print("\n例:")
    print("  from src.data_loader import DataLoader")
    print("  from src.analyzer import DataAnalyzer")
    print("  loader = DataLoader()")
    print("  df = loader.load_data()")
    print("  analyzer = DataAnalyzer(df)")
    print("  analyzer.get_basic_statistics()")
