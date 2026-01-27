"""
分析・可視化用のユーティリティモジュール
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict, Optional


class DataAnalyzer:
    """データ分析用クラス"""
    
    @staticmethod
    def calculate_correlation(df: pd.DataFrame, 
                            x_col: str = "job_opening_rate",
                            y_col: str = "average_wage") -> Tuple[float, float]:
        """
        2つの変数の相関係数とp値を計算
        
        Args:
            df: データフレーム
            x_col: 説明変数の列名
            y_col: 被説明変数の列名
            
        Returns:
            (相関係数, p値)
        """
        # NaN値を除去
        valid_data = df[[x_col, y_col]].dropna()
        
        if len(valid_data) < 2:
            return np.nan, np.nan
        
        correlation, p_value = stats.pearsonr(valid_data[x_col], valid_data[y_col])
        return correlation, p_value
    
    @staticmethod
    def linear_regression(df: pd.DataFrame,
                         x_col: str = "job_opening_rate",
                         y_col: str = "average_wage") -> Dict[str, float]:
        """
        線形回帰分析を実施
        
        Args:
            df: データフレーム
            x_col: 説明変数の列名
            y_col: 被説明変数の列名
            
        Returns:
            回帰パラメータの辞書 {slope, intercept, r_squared, p_value}
        """
        # NaN値を除去
        valid_data = df[[x_col, y_col]].dropna()
        
        if len(valid_data) < 2:
            return {}
        
        x = valid_data[x_col].values
        y = valid_data[y_col].values
        
        # 線形回帰
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'std_err': std_err
        }
    
    @staticmethod
    def rank_prefectures(df: pd.DataFrame, 
                        sort_by: str = "job_opening_rate",
                        ascending: bool = False) -> pd.DataFrame:
        """
        都道府県をランキング
        
        Args:
            df: データフレーム
            sort_by: ソート対象列
            ascending: 昇順フラグ
            
        Returns:
            ランク付きデータフレーム
        """
        ranked_df = df.sort_values(sort_by, ascending=ascending).reset_index(drop=True)
        ranked_df['rank'] = range(1, len(ranked_df) + 1)
        return ranked_df[['rank', 'prefecture', sort_by]]
    
    @staticmethod
    def get_high_low_pairs(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        有効求人倍率が高い地域と低い地域を抽出
        
        Args:
            df: データフレーム
            
        Returns:
            (高い地域DF, 低い地域DF)
        """
        threshold = df['job_opening_rate'].median()
        
        high = df[df['job_opening_rate'] >= threshold].copy()
        low = df[df['job_opening_rate'] < threshold].copy()
        
        return high, low
    
    @staticmethod
    def compare_groups(high: pd.DataFrame, low: pd.DataFrame) -> Dict[str, float]:
        """
        高求人倍率地域と低求人倍率地域の賃金を比較
        
        Args:
            high: 高求人倍率地域のDF
            low: 低求人倍率地域のDF
            
        Returns:
            比較統計情報の辞書
        """
        high_wage = high['average_wage'].dropna()
        low_wage = low['average_wage'].dropna()
        
        # t検定
        if len(high_wage) > 0 and len(low_wage) > 0:
            t_stat, p_value = stats.ttest_ind(high_wage, low_wage)
        else:
            t_stat, p_value = np.nan, np.nan
        
        return {
            'high_wage_mean': high_wage.mean(),
            'low_wage_mean': low_wage.mean(),
            'high_wage_std': high_wage.std(),
            'low_wage_std': low_wage.std(),
            'wage_difference': high_wage.mean() - low_wage.mean(),
            't_statistic': t_stat,
            'p_value': p_value,
            'high_count': len(high),
            'low_count': len(low)
        }


class VisualizationHelper:
    """可視化用ヘルパークラス"""
    
    @staticmethod
    def prepare_scatter_data(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, list]:
        """
        散布図用データを準備
        
        Args:
            df: データフレーム
            
        Returns:
            (X値, Y値, ラベル)
        """
        valid_df = df.dropna(subset=['job_opening_rate', 'average_wage'])
        
        x = valid_df['job_opening_rate'].values
        y = valid_df['average_wage'].values
        labels = valid_df['prefecture'].values
        
        return x, y, labels
    
    @staticmethod
    def prepare_bar_data(df: pd.DataFrame, top_n: int = 10) -> Tuple[list, list]:
        """
        棒グラフ用データを準備
        
        Args:
            df: データフレーム
            top_n: 表示上位数
            
        Returns:
            (都道府県名リスト, 値リスト)
        """
        top_df = df.nlargest(top_n, 'average_wage')
        return top_df['prefecture'].tolist(), top_df['average_wage'].tolist()


if __name__ == "__main__":
    # テスト実行
    sample_data = pd.DataFrame({
        'prefecture': ['東京', '大阪', '愛知', '福岡', '京都'],
        'job_opening_rate': [1.2, 1.0, 1.1, 0.9, 0.8],
        'average_wage': [4100, 3800, 3900, 3600, 3700]
    })
    
    # 相関係数
    corr, p_val = DataAnalyzer.calculate_correlation(sample_data)
    print(f"Correlation: {corr:.3f}, p-value: {p_val:.3f}")
    
    # 線形回帰
    reg_result = DataAnalyzer.linear_regression(sample_data)
    print(f"Regression results: {reg_result}")
    
    # ランキング
    ranked = DataAnalyzer.rank_prefectures(sample_data)
    print(f"\nRanked data:\n{ranked}")
