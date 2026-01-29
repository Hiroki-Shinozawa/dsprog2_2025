"""
仮説検証モジュール
統計的検定を使用して仮説を検証
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HypothesisResult:
    """仮説検証結果"""
    hypothesis_name: str
    test_name: str
    test_statistic: float
    p_value: float
    is_significant: bool
    conclusion: str
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """辞書形式に変換"""
        return {
            'hypothesis': self.hypothesis_name,
            'test': self.test_name,
            'statistic': self.test_statistic,
            'p_value': self.p_value,
            'significant': self.is_significant,
            'conclusion': self.conclusion,
            'timestamp': self.created_at
        }
    
    def __str__(self) -> str:
        """文字列表現"""
        sig_symbol = "✓" if self.is_significant else "✗"
        return f"""
{sig_symbol} {self.hypothesis_name}
  検定: {self.test_name}
  統計量: {self.test_statistic:.6f}
  p値: {self.p_value:.6f}
  結論: {self.conclusion}
"""


class HypothesisVerifier:
    """仮説検証クラス"""
    
    def __init__(self, alpha: float = 0.05):
        """
        初期化
        
        Args:
            alpha: 有意水準（デフォルト: 0.05）
        """
        self.alpha = alpha
        self.results: List[HypothesisResult] = []
    
    def verify_normality(self, data: np.ndarray, name: str = "データ") -> HypothesisResult:
        """
        正規性の検定（Shapiro-Wilk検定）
        
        Args:
            data: データ配列
            name: データ名
        
        Returns:
            HypothesisResult: 検定結果
        """
        # 外れ値を除去
        data_clean = data[~np.isnan(data)]
        
        if len(data_clean) < 3:
            return HypothesisResult(
                hypothesis_name=f"{name}は正規分布に従う",
                test_name="Shapiro-Wilk検定",
                test_statistic=np.nan,
                p_value=np.nan,
                is_significant=False,
                conclusion="サンプルサイズが不十分です"
            )
        
        if len(data_clean) > 5000:
            data_clean = np.random.choice(data_clean, 5000, replace=False)
        
        statistic, p_value = stats.shapiro(data_clean)
        is_significant = p_value < self.alpha
        
        conclusion = (
            f"p値 = {p_value:.6f} < {self.alpha}: 正規分布ではない"
            if is_significant
            else f"p値 = {p_value:.6f} >= {self.alpha}: 正規分布である可能性がある"
        )
        
        result = HypothesisResult(
            hypothesis_name=f"{name}は正規分布に従う",
            test_name="Shapiro-Wilk検定",
            test_statistic=statistic,
            p_value=p_value,
            is_significant=is_significant,
            conclusion=conclusion
        )
        
        self.results.append(result)
        return result
    
    def verify_correlation(self, x: np.ndarray, y: np.ndarray, 
                         name_x: str, name_y: str) -> HypothesisResult:
        """
        相関関係の検定
        
        Args:
            x: データ配列1
            y: データ配列2
            name_x: データ名1
            name_y: データ名2
        
        Returns:
            HypothesisResult: 検定結果
        """
        # 外れ値と欠損値を除去
        mask = ~(np.isnan(x) | np.isnan(y))
        x_clean = x[mask]
        y_clean = y[mask]
        
        if len(x_clean) < 3:
            return HypothesisResult(
                hypothesis_name=f"{name_x}と{name_y}に相関がある",
                test_name="Pearson相関検定",
                test_statistic=np.nan,
                p_value=np.nan,
                is_significant=False,
                conclusion="サンプルサイズが不十分です"
            )
        
        correlation, p_value = stats.pearsonr(x_clean, y_clean)
        is_significant = p_value < self.alpha
        
        conclusion = (
            f"相関係数 = {correlation:.4f}, p値 = {p_value:.6f}: "
            f"有意な相関がある" if is_significant
            else f"相関係数 = {correlation:.4f}, p値 = {p_value:.6f}: 有意な相関なし"
        )
        
        result = HypothesisResult(
            hypothesis_name=f"{name_x}と{name_y}に相関がある",
            test_name="Pearson相関検定",
            test_statistic=correlation,
            p_value=p_value,
            is_significant=is_significant,
            conclusion=conclusion
        )
        
        self.results.append(result)
        return result
    
    def verify_mean_difference(self, group1: np.ndarray, group2: np.ndarray,
                              name1: str, name2: str) -> HypothesisResult:
        """
        2グループの平均値の差検定（t検定）
        
        Args:
            group1: グループ1のデータ
            group2: グループ2のデータ
            name1: グループ1の名前
            name2: グループ2の名前
        
        Returns:
            HypothesisResult: 検定結果
        """
        # 外れ値と欠損値を除去
        g1 = group1[~np.isnan(group1)]
        g2 = group2[~np.isnan(group2)]
        
        if len(g1) < 2 or len(g2) < 2:
            return HypothesisResult(
                hypothesis_name=f"{name1}と{name2}の平均値が異なる",
                test_name="Welch's t検定",
                test_statistic=np.nan,
                p_value=np.nan,
                is_significant=False,
                conclusion="サンプルサイズが不十分です"
            )
        
        # Welch's t検定（等分散を仮定しない）
        t_statistic, p_value = stats.ttest_ind(g1, g2, equal_var=False)
        is_significant = p_value < self.alpha
        
        mean1, mean2 = np.mean(g1), np.mean(g2)
        conclusion = (
            f"t = {t_statistic:.4f}, p値 = {p_value:.6f}: "
            f"有意に異なる ({mean1:.4f} vs {mean2:.4f})"
            if is_significant
            else f"t = {t_statistic:.4f}, p値 = {p_value:.6f}: 有意な差なし"
        )
        
        result = HypothesisResult(
            hypothesis_name=f"{name1}と{name2}の平均値が異なる",
            test_name="Welch's t検定",
            test_statistic=t_statistic,
            p_value=p_value,
            is_significant=is_significant,
            conclusion=conclusion
        )
        
        self.results.append(result)
        return result
    
    def verify_variance_difference(self, group1: np.ndarray, group2: np.ndarray,
                                  name1: str, name2: str) -> HypothesisResult:
        """
        2グループの分散の差検定（Levene検定）
        
        Args:
            group1: グループ1のデータ
            group2: グループ2のデータ
            name1: グループ1の名前
            name2: グループ2の名前
        
        Returns:
            HypothesisResult: 検定結果
        """
        # 外れ値と欠損値を除去
        g1 = group1[~np.isnan(group1)]
        g2 = group2[~np.isnan(group2)]
        
        if len(g1) < 2 or len(g2) < 2:
            return HypothesisResult(
                hypothesis_name=f"{name1}と{name2}の分散が等しい",
                test_name="Levene検定",
                test_statistic=np.nan,
                p_value=np.nan,
                is_significant=False,
                conclusion="サンプルサイズが不十分です"
            )
        
        statistic, p_value = stats.levene(g1, g2)
        is_significant = p_value < self.alpha
        
        var1, var2 = np.var(g1, ddof=1), np.var(g2, ddof=1)
        conclusion = (
            f"F = {statistic:.4f}, p値 = {p_value:.6f}: "
            f"分散が異なる (var: {var1:.4f} vs {var2:.4f})"
            if is_significant
            else f"F = {statistic:.4f}, p値 = {p_value:.6f}: 分散に有意な差なし"
        )
        
        result = HypothesisResult(
            hypothesis_name=f"{name1}と{name2}の分散が等しい",
            test_name="Levene検定",
            test_statistic=statistic,
            p_value=p_value,
            is_significant=is_significant,
            conclusion=conclusion
        )
        
        self.results.append(result)
        return result
    
    def verify_anova(self, groups: List[np.ndarray], 
                    group_names: List[str]) -> HypothesisResult:
        """
        複数グループ間の平均値差検定（ANOVA）
        
        Args:
            groups: グループのデータリスト
            group_names: グループ名のリスト
        
        Returns:
            HypothesisResult: 検定結果
        """
        if len(groups) < 2:
            return HypothesisResult(
                hypothesis_name="複数グループ間の平均値が異なる",
                test_name="一元配置ANOVA",
                test_statistic=np.nan,
                p_value=np.nan,
                is_significant=False,
                conclusion="グループ数が不足しています"
            )
        
        # 外れ値と欠損値を除去
        clean_groups = [g[~np.isnan(g)] for g in groups]
        
        if any(len(g) < 2 for g in clean_groups):
            return HypothesisResult(
                hypothesis_name="複数グループ間の平均値が異なる",
                test_name="一元配置ANOVA",
                test_statistic=np.nan,
                p_value=np.nan,
                is_significant=False,
                conclusion="サンプルサイズが不十分です"
            )
        
        f_statistic, p_value = stats.f_oneway(*clean_groups)
        is_significant = p_value < self.alpha
        
        group_means = [np.mean(g) for g in clean_groups]
        conclusion = (
            f"F = {f_statistic:.4f}, p値 = {p_value:.6f}: "
            f"グループ間に有意な差がある"
            if is_significant
            else f"F = {f_statistic:.4f}, p値 = {p_value:.6f}: 有意な差なし"
        )
        
        result = HypothesisResult(
            hypothesis_name="複数グループ間の平均値が異なる",
            test_name="一元配置ANOVA",
            test_statistic=f_statistic,
            p_value=p_value,
            is_significant=is_significant,
            conclusion=conclusion
        )
        
        self.results.append(result)
        return result
    
    def get_results_dataframe(self) -> pd.DataFrame:
        """結果をDataFrameで取得"""
        if not self.results:
            return pd.DataFrame()
        
        data = [r.to_dict() for r in self.results]
        return pd.DataFrame(data)
    
    def print_summary(self):
        """結果サマリーを表示"""
        print("\n" + "="*60)
        print("【仮説検証結果サマリー】")
        print("="*60)
        
        for i, result in enumerate(self.results, 1):
            print(f"\n{i}. {result.hypothesis_name}")
            print(f"   検定: {result.test_name}")
            print(f"   統計量: {result.test_statistic:.6f}")
            print(f"   p値: {result.p_value:.6f}")
            sig = "有意" if result.is_significant else "非有意"
            print(f"   結果: {sig} (α={self.alpha})")
            print(f"   結論: {result.conclusion}")
        
        significant_count = sum(1 for r in self.results if r.is_significant)
        print(f"\n有意な結果: {significant_count}/{len(self.results)}")
        print("="*60 + "\n")


if __name__ == "__main__":
    # テスト実行
    verifier = HypothesisVerifier(alpha=0.05)
    
    # サンプルデータ生成
    np.random.seed(42)
    group1 = np.random.normal(100, 15, 100)
    group2 = np.random.normal(110, 15, 100)
    
    print("【仮説検証のテスト実行】\n")
    
    # 正規性検定
    print("1. 正規性の検定")
    verifier.verify_normality(group1, "グループ1")
    print(verifier.results[-1])
    
    # 平均値差検定
    print("2. 平均値差検定（t検定）")
    verifier.verify_mean_difference(group1, group2, "グループ1", "グループ2")
    print(verifier.results[-1])
    
    # 相関関係検定
    print("3. 相関関係検定")
    x = np.random.normal(50, 10, 50)
    y = x + np.random.normal(0, 5, 50)
    verifier.verify_correlation(x, y, "変数X", "変数Y")
    print(verifier.results[-1])
    
    # サマリー表示
    verifier.print_summary()
    
    # 結果をDataFrameで取得
    print("\n【結果テーブル】")
    print(verifier.get_results_dataframe().to_string(index=False))
