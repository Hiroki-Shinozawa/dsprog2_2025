#!/usr/bin/env python3
"""
データベースから高度なクエリを実行するスクリプト
"""

import sys
from pathlib import Path
import pandas as pd

# モジュールパス設定
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database import AnalysisDatabase


def execute_advanced_queries():
    """高度なSQLクエリを実行して分析結果を表示"""
    
    print("\n" + "="*70)
    print("【データベースからの高度なクエリ実行】")
    print("="*70)
    
    try:
        db = AnalysisDatabase()
        
        # ========================
        # クエリ1: 職業別の求人統計
        # ========================
        print("\n【クエリ1】職業別の求人統計")
        print("-"*70)
        
        query1 = """
        SELECT 
            occupation as '職業',
            COUNT(*) as '件数',
            ROUND(AVG(job_offers), 0) as '平均求人数',
            ROUND(MAX(job_offers), 0) as '最大求人数',
            ROUND(MIN(job_offers), 0) as '最小求人数',
            ROUND(MAX(job_offers) - MIN(job_offers), 0) as '範囲'
        FROM employment_data
        GROUP BY occupation
        ORDER BY AVG(job_offers) DESC
        """
        
        result1 = db.execute_query(query1)
        print(result1.to_string(index=False))
        
        # ========================
        # クエリ2: マッチング比率の分析
        # ========================
        print("\n【クエリ2】マッチング比率（求人/応募）の分析")
        print("-"*70)
        
        query2 = """
        SELECT 
            occupation as '職業',
            ROUND(AVG(ratio), 4) as '平均比率',
            ROUND(AVG(job_placements / CASE WHEN applicants = 0 THEN 1 ELSE applicants END), 4) as '成功率',
            COUNT(CASE WHEN ratio > 0.8 THEN 1 END) as '高比率件数',
            COUNT(CASE WHEN ratio <= 0.8 THEN 1 END) as '低比率件数'
        FROM employment_data
        GROUP BY occupation
        ORDER BY AVG(ratio) DESC
        """
        
        result2 = db.execute_query(query2)
        print(result2.to_string(index=False))
        
        # ========================
        # クエリ3: 産業別賃金比較
        # ========================
        print("\n【クエリ3】産業別賃金比較（2023年）")
        print("-"*70)
        
        query3 = """
        SELECT 
            industry as '産業',
            ROUND(average_wage, 0) as '平均賃金',
            ROUND(median_wage, 0) as '中央値',
            ROUND(std_wage, 0) as '標準偏差',
            ROUND((average_wage - median_wage) / CASE WHEN median_wage = 0 THEN 1 ELSE median_wage END * 100, 2) as '歪度(%)'
        FROM wage_data
        ORDER BY average_wage DESC
        """
        
        result3 = db.execute_query(query3)
        print(result3.to_string(index=False))
        
        # ========================
        # クエリ4: 求人・採用統計
        # ========================
        print("\n【クエリ4】全体求人・採用統計")
        print("-"*70)
        
        query4 = """
        SELECT 
            '総求人数' as '統計項目',
            CAST(SUM(job_offers) AS INTEGER) as '数値',
            '' as '補足'
        FROM employment_data
        
        UNION ALL
        
        SELECT 
            '総採用数' as '統計項目',
            CAST(SUM(job_placements) AS INTEGER) as '数値',
            '' as '補足'
        FROM employment_data
        
        UNION ALL
        
        SELECT 
            '総応募者数' as '統計項目',
            CAST(SUM(applicants) AS INTEGER) as '数値',
            '' as '補足'
        FROM employment_data
        
        UNION ALL
        
        SELECT 
            '求人平均値' as '統計項目',
            CAST(AVG(job_offers) AS INTEGER) as '数値',
            CAST(COUNT(*) AS TEXT) || '職業' as '補足'
        FROM employment_data
        
        UNION ALL
        
        SELECT 
            '採用平均値' as '統計項目',
            CAST(AVG(job_placements) AS INTEGER) as '数値',
            CAST(COUNT(*) AS TEXT) || '職業' as '補足'
        FROM employment_data
        
        UNION ALL
        
        SELECT 
            '全体マッチング比率' as '統計項目',
            CAST(ROUND(SUM(job_offers) / SUM(applicants) * 100, 2) AS TEXT) as '数値',
            '%' as '補足'
        FROM employment_data
        """
        
        result4 = db.execute_query(query4)
        print(result4.to_string(index=False))
        
        # ========================
        # クエリ5: 分析結果履歴
        # ========================
        print("\n【クエリ5】実行済みの分析結果")
        print("-"*70)
        
        query5 = """
        SELECT 
            id as 'ID',
            analysis_type as '分析タイプ',
            result_summary as '結果概要',
            ROUND(metric_value, 6) as 'メトリクス値',
            created_at as '実行日時'
        FROM analysis_results
        ORDER BY created_at DESC
        """
        
        result5 = db.execute_query(query5)
        print(result5.to_string(index=False))
        
        # ========================
        # クエリ6: 職業別の求人効率分析
        # ========================
        print("\n【クエリ6】職業別の求人効率分析（求人数vs採用数）")
        print("-"*70)
        
        query6 = """
        SELECT 
            occupation as '職業',
            ROUND(SUM(job_offers), 0) as '総求人数',
            ROUND(SUM(job_placements), 0) as '総採用数',
            ROUND(SUM(job_placements) / SUM(job_offers) * 100, 2) as '採用率(%)',
            CASE 
                WHEN SUM(job_placements) / SUM(job_offers) >= 0.9 THEN '優秀'
                WHEN SUM(job_placements) / SUM(job_offers) >= 0.7 THEN '良好'
                ELSE '改善必要'
            END as '評価'
        FROM employment_data
        GROUP BY occupation
        ORDER BY SUM(job_offers) DESC
        """
        
        result6 = db.execute_query(query6)
        print(result6.to_string(index=False))
        
        # ========================
        # 最終サマリー
        # ========================
        print("\n【最終サマリー】")
        print("-"*70)
        
        total_employment = db.execute_query("SELECT COUNT(*) as count FROM employment_data")
        total_wage = db.execute_query("SELECT COUNT(*) as count FROM wage_data")
        total_results = db.execute_query("SELECT COUNT(*) as count FROM analysis_results")
        
        print(f"""
✓ データベース統計
  - employment_dataレコード: {total_employment.iloc[0, 0]}件
  - wage_dataレコード: {total_wage.iloc[0, 0]}件
  - analysis_resultsレコード: {total_results.iloc[0, 0]}件
  - 総データ件数: {total_employment.iloc[0, 0] + total_wage.iloc[0, 0] + total_results.iloc[0, 0]}件

✓ 実行可能なクエリ:
  1. 職業別の求人統計
  2. マッチング比率の分析
  3. 産業別賃金比較
  4. 求人・採用統計
  5. 分析結果履歴
  6. 職業別の求人効率分析
""")
        
        db.disconnect()
        print("\n" + "="*70 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = execute_advanced_queries()
    sys.exit(0 if success else 1)
