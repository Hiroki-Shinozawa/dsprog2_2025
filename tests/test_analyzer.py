"""
ユニットテストモジュール
"""

import unittest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# src モジュールをインポート可能にする
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzer import DataAnalyzer, VisualizationHelper


class TestDataAnalyzer(unittest.TestCase):
    """DataAnalyzerのテストクラス"""
    
    def setUp(self):
        """テスト前処理"""
        self.test_df = pd.DataFrame({
            'prefecture': ['東京', '大阪', '愛知', '福岡', '京都'],
            'job_opening_rate': [1.2, 1.0, 1.1, 0.9, 0.8],
            'average_wage': [4100, 3800, 3900, 3600, 3700]
        })
    
    def test_correlation_calculation(self):
        """相関係数計算のテスト"""
        corr, p_val = DataAnalyzer.calculate_correlation(self.test_df)
        
        # 相関係数は -1 から 1 の範囲
        self.assertGreaterEqual(corr, -1)
        self.assertLessEqual(corr, 1)
        
        # p値は 0 から 1 の範囲
        self.assertGreaterEqual(p_val, 0)
        self.assertLessEqual(p_val, 1)
    
    def test_correlation_with_empty_data(self):
        """空データでの相関係数計算テスト"""
        empty_df = pd.DataFrame({
            'job_opening_rate': [],
            'average_wage': []
        })
        
        corr, p_val = DataAnalyzer.calculate_correlation(empty_df)
        self.assertTrue(np.isnan(corr))
        self.assertTrue(np.isnan(p_val))
    
    def test_linear_regression(self):
        """線形回帰分析のテスト"""
        result = DataAnalyzer.linear_regression(self.test_df)
        
        # 必要なキーが存在
        self.assertIn('slope', result)
        self.assertIn('intercept', result)
        self.assertIn('r_squared', result)
        self.assertIn('p_value', result)
        
        # R²は 0 から 1 の範囲（調整済みでない限り）
        self.assertGreaterEqual(result['r_squared'], 0)
        self.assertLessEqual(result['r_squared'], 1)
    
    def test_rank_prefectures(self):
        """都道府県ランキングのテスト"""
        ranked = DataAnalyzer.rank_prefectures(self.test_df, sort_by='average_wage')
        
        # ランク数が等しい
        self.assertEqual(len(ranked), len(self.test_df))
        
        # ランクが1から始まる
        self.assertEqual(ranked['rank'].iloc[0], 1)
        
        # ランクが昇順（最初のNaN値を除外）
        self.assertTrue((ranked['rank'].diff().dropna() > 0).all())
    
    def test_rank_prefectures_descending(self):
        """都道府県ランキング（降順）のテスト"""
        ranked = DataAnalyzer.rank_prefectures(
            self.test_df, 
            sort_by='average_wage', 
            ascending=True
        )
        
        # 最初の行が最小値
        self.assertEqual(
            ranked['average_wage'].iloc[0],
            self.test_df['average_wage'].min()
        )
    
    def test_get_high_low_pairs(self):
        """高低グループ分けのテスト"""
        high, low = DataAnalyzer.get_high_low_pairs(self.test_df)
        
        # 高グループと低グループの合計元データと等しい
        total = len(high) + len(low)
        self.assertEqual(total, len(self.test_df))
        
        # 高グループのすべてが低グループより大きい（中央値以上）
        if len(high) > 0 and len(low) > 0:
            self.assertGreaterEqual(
                high['job_opening_rate'].min(),
                low['job_opening_rate'].max()
            )
    
    def test_compare_groups(self):
        """グループ比較のテスト"""
        high, low = DataAnalyzer.get_high_low_pairs(self.test_df)
        result = DataAnalyzer.compare_groups(high, low)
        
        # 必要なキーが存在
        self.assertIn('high_wage_mean', result)
        self.assertIn('low_wage_mean', result)
        self.assertIn('wage_difference', result)
        self.assertIn('p_value', result)
        
        # 差が計算されている
        self.assertIsNotNone(result['wage_difference'])


class TestVisualizationHelper(unittest.TestCase):
    """VisualizationHelperのテストクラス"""
    
    def setUp(self):
        """テスト前処理"""
        self.test_df = pd.DataFrame({
            'prefecture': ['東京', '大阪', '愛知', '福岡', '京都'],
            'job_opening_rate': [1.2, 1.0, 1.1, 0.9, 0.8],
            'average_wage': [4100, 3800, 3900, 3600, 3700]
        })
    
    def test_prepare_scatter_data(self):
        """散布図用データ準備のテスト"""
        x, y, labels = VisualizationHelper.prepare_scatter_data(self.test_df)
        
        # 配列の長さが等しい
        self.assertEqual(len(x), len(y))
        self.assertEqual(len(x), len(labels))
        
        # NaN値がない
        self.assertFalse(np.isnan(x).any())
        self.assertFalse(np.isnan(y).any())
    
    def test_prepare_scatter_data_with_nan(self):
        """NaN値を含むデータでの散布図用データ準備テスト"""
        df_with_nan = self.test_df.copy()
        df_with_nan.loc[0, 'average_wage'] = np.nan
        
        x, y, labels = VisualizationHelper.prepare_scatter_data(df_with_nan)
        
        # NaN行が除外されている
        self.assertEqual(len(x), len(self.test_df) - 1)
        self.assertFalse(np.isnan(x).any())
        self.assertFalse(np.isnan(y).any())
    
    def test_prepare_bar_data(self):
        """棒グラフ用データ準備のテスト"""
        prefectures, values = VisualizationHelper.prepare_bar_data(self.test_df, top_n=3)
        
        # 指定数以下のデータ
        self.assertLessEqual(len(prefectures), 3)
        self.assertEqual(len(prefectures), len(values))
        
        # 値が降順
        for i in range(len(values) - 1):
            self.assertGreaterEqual(values[i], values[i + 1])
    
    def test_prepare_bar_data_top_n_larger_than_data(self):
        """データ数より大きなtop_nでのテスト"""
        prefectures, values = VisualizationHelper.prepare_bar_data(self.test_df, top_n=100)
        
        # すべてのデータが返される
        self.assertEqual(len(prefectures), len(self.test_df))


class TestDataIntegration(unittest.TestCase):
    """統合テストクラス"""
    
    def setUp(self):
        """テスト前処理"""
        self.test_df = pd.DataFrame({
            'prefecture': ['東京', '大阪', '愛知', '福岡', '京都', '埼玉', '千葉'],
            'job_opening_rate': [1.2, 1.0, 1.1, 0.9, 0.8, 1.05, 1.15],
            'average_wage': [4100, 3800, 3900, 3600, 3700, 3750, 4050]
        })
    
    def test_workflow(self):
        """全体的なワークフロー"""
        # 1. 相関係数を計算
        corr, p_val = DataAnalyzer.calculate_correlation(self.test_df)
        self.assertIsNotNone(corr)
        
        # 2. 線形回帰を実施
        reg = DataAnalyzer.linear_regression(self.test_df)
        self.assertGreater(len(reg), 0)
        
        # 3. ランキング
        ranked = DataAnalyzer.rank_prefectures(self.test_df)
        self.assertEqual(len(ranked), len(self.test_df))
        
        # 4. グループ比較
        high, low = DataAnalyzer.get_high_low_pairs(self.test_df)
        comparison = DataAnalyzer.compare_groups(high, low)
        self.assertIsNotNone(comparison['wage_difference'])


if __name__ == '__main__':
    unittest.main()
