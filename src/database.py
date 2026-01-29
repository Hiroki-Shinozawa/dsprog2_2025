"""
データベース管理モジュール
分析データをSQLiteに保存・管理
"""

import sqlite3
from pathlib import Path
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime


class DatabaseManager:
    """SQLiteデータベースを管理するクラス"""
    
    def __init__(self, db_path: str = None):
        """
        初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        if db_path is None:
            current_dir = Path(__file__).parent.parent
            db_path = current_dir / "data" / "analysis.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
    
    def connect(self):
        """データベースに接続"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            print(f"✓ データベースに接続しました: {self.db_path.name}")
        except sqlite3.Error as e:
            print(f"✗ 接続エラー: {e}")
            raise
    
    def disconnect(self):
        """データベースを切断"""
        if self.conn:
            self.conn.close()
            print("✓ データベースを切断しました")
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        SQLを実行
        
        Args:
            sql: SQL文
            params: パラメータ
        
        Returns:
            sqlite3.Cursor: カーソルオブジェクト
        """
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor
    
    def commit(self):
        """変更をコミット"""
        if self.conn:
            self.conn.commit()
            print("✓ 変更をコミットしました")
    
    def create_table(self, table_name: str, columns: Dict[str, str]):
        """
        テーブルを作成
        
        Args:
            table_name: テーブル名
            columns: カラム定義 {カラム名: データ型}
        """
        col_defs = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({col_defs})"
        
        self.execute(sql)
        self.commit()
        print(f"✓ テーブルを作成しました: {table_name}")
    
    def save_dataframe(self, df: pd.DataFrame, table_name: str, 
                      if_exists: str = 'append'):
        """
        DataFrameをテーブルに保存
        
        Args:
            df: DataFrame
            table_name: テーブル名
            if_exists: 'fail', 'replace', 'append'
        """
        try:
            df.to_sql(table_name, self.conn, if_exists=if_exists, index=False)
            self.commit()
            print(f"✓ {len(df)}行をテーブル '{table_name}' に保存しました")
        except Exception as e:
            print(f"✗ 保存エラー: {e}")
            raise
    
    def read_dataframe(self, table_name: str, 
                      where: Optional[str] = None) -> pd.DataFrame:
        """
        テーブルからDataFrameを読み込む
        
        Args:
            table_name: テーブル名
            where: WHERE句（オプション）
        
        Returns:
            pd.DataFrame: 読み込んだデータ
        """
        sql = f"SELECT * FROM {table_name}"
        if where:
            sql += f" WHERE {where}"
        
        return pd.read_sql(sql, self.conn)
    
    def execute_query(self, sql: str) -> pd.DataFrame:
        """
        クエリを実行
        
        Args:
            sql: SQL文
        
        Returns:
            pd.DataFrame: クエリ結果
        """
        return pd.read_sql(sql, self.conn)
    
    def list_tables(self) -> List[str]:
        """
        テーブル一覧を取得
        
        Returns:
            List[str]: テーブル名のリスト
        """
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        cursor = self.execute(sql)
        tables = [row[0] for row in cursor.fetchall()]
        return tables
    
    def get_table_info(self, table_name: str) -> List[tuple]:
        """
        テーブル情報を取得
        
        Args:
            table_name: テーブル名
        
        Returns:
            List[tuple]: カラム情報のリスト
        """
        sql = f"PRAGMA table_info({table_name})"
        cursor = self.execute(sql)
        return cursor.fetchall()
    
    def delete_table(self, table_name: str):
        """
        テーブルを削除
        
        Args:
            table_name: テーブル名
        """
        sql = f"DROP TABLE IF EXISTS {table_name}"
        self.execute(sql)
        self.commit()
        print(f"✓ テーブル '{table_name}' を削除しました")


class AnalysisDatabase(DatabaseManager):
    """分析用データベースクラス"""
    
    def __init__(self, db_path: str = None):
        """初期化"""
        super().__init__(db_path)
        self.connect()
    
    def initialize_schema(self):
        """データベーススキーマを初期化"""
        
        # 職業紹介データテーブル
        self.create_table('employment_data', {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'date': 'TEXT NOT NULL',
            'occupation': 'TEXT',
            'job_offers': 'INTEGER',
            'job_placements': 'INTEGER',
            'applicants': 'INTEGER',
            'ratio': 'REAL',
            'created_at': 'TEXT'
        })
        
        # 賃金データテーブル
        self.create_table('wage_data', {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'year': 'INTEGER',
            'industry': 'TEXT',
            'average_wage': 'REAL',
            'median_wage': 'REAL',
            'std_wage': 'REAL',
            'created_at': 'TEXT'
        })
        
        # 分析結果テーブル
        self.create_table('analysis_results', {
            'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
            'analysis_type': 'TEXT',
            'result_summary': 'TEXT',
            'metric_value': 'REAL',
            'created_at': 'TEXT'
        })
    
    def save_employment_data(self, df: pd.DataFrame):
        """職業紹介データを保存"""
        df['created_at'] = datetime.now().isoformat()
        self.save_dataframe(df, 'employment_data', if_exists='append')
    
    def save_wage_data(self, df: pd.DataFrame):
        """賃金データを保存"""
        df['created_at'] = datetime.now().isoformat()
        self.save_dataframe(df, 'wage_data', if_exists='append')
    
    def get_employment_stats(self) -> pd.DataFrame:
        """職業紹介データの統計を取得"""
        sql = """
        SELECT 
            occupation,
            COUNT(*) as count,
            AVG(job_offers) as avg_offers,
            AVG(ratio) as avg_ratio
        FROM employment_data
        GROUP BY occupation
        ORDER BY avg_ratio DESC
        """
        return self.execute_query(sql)
    
    def save_analysis_results(self, analysis_type: str, 
                             result_summary: str, metric_value: float):
        """分析結果を保存"""
        sql = """
        INSERT INTO analysis_results (analysis_type, result_summary, metric_value, created_at)
        VALUES (?, ?, ?, ?)
        """
        self.execute(sql, (analysis_type, result_summary, metric_value, 
                          datetime.now().isoformat()))
        self.commit()
        print(f"✓ 分析結果を保存しました: {analysis_type}")
    
    def get_analysis_report(self) -> str:
        """分析レポートを生成"""
        report = "\n【分析レポート】\n" + "="*60 + "\n"
        
        # 職業紹介データの統計
        emp_stats = self.get_employment_stats()
        if not emp_stats.empty:
            report += "\n【職業別マッチング比率（平均）】\n"
            report += emp_stats.to_string(index=False) + "\n"
        
        # 保存されている分析結果
        try:
            results = self.execute_query("SELECT * FROM analysis_results ORDER BY created_at DESC LIMIT 5")
            if not results.empty:
                report += "\n【最近の分析結果】\n"
                for _, row in results.iterrows():
                    report += f"\n{row['analysis_type']}:\n"
                    report += f"  結果: {row['result_summary']}\n"
                    report += f"  値: {row['metric_value']:.4f}\n"
        except Exception as e:
            report += f"\n⚠️  分析結果の取得に失敗: {e}\n"
        
        report += "\n" + "="*60 + "\n"
        return report


if __name__ == "__main__":
    # テスト実行
    try:
        db = AnalysisDatabase()
        db.initialize_schema()
        
        print("\nテーブル一覧:")
        tables = db.list_tables()
        for table in tables:
            print(f"  - {table}")
        
        db.disconnect()
        print("\n✓ データベースの初期化が完了しました")
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        print("\nデータベースが初期化できない場合:")
        print("  - /data/analysis.db ファイルの権限を確認してください")
        print("  - /data/ ディレクトリが存在することを確認してください")
