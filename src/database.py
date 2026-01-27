"""
SQLiteデータベース管理モジュール
有効求人倍率と平均賃金データを管理
"""

import sqlite3
import pandas as pd
from typing import Optional, List, Tuple
from pathlib import Path


class DatabaseManager:
    """SQLiteデータベースを管理するクラス"""
    
    def __init__(self, db_path: str = "data/analysis.db"):
        """
        初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.connect()
    
    def connect(self) -> None:
        """データベースに接続"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
    
    def close(self) -> None:
        """データベース接続を閉じる"""
        if self.connection:
            self.connection.close()
    
    def create_tables(self) -> None:
        """テーブルを作成"""
        cursor = self.connection.cursor()
        
        # 都道府県マスターテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prefectures (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                region TEXT
            )
        """)
        
        # 有効求人倍率テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_opening_rate (
                id INTEGER PRIMARY KEY,
                prefecture_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER,
                rate REAL,
                FOREIGN KEY (prefecture_id) REFERENCES prefectures(id),
                UNIQUE(prefecture_id, year, month)
            )
        """)
        
        # 平均賃金テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS average_wage (
                id INTEGER PRIMARY KEY,
                prefecture_id INTEGER NOT NULL,
                year INTEGER NOT NULL,
                wage REAL,
                FOREIGN KEY (prefecture_id) REFERENCES prefectures(id),
                UNIQUE(prefecture_id, year)
            )
        """)
        
        self.connection.commit()
    
    def insert_prefectures(self, prefectures: List[Tuple[str, str]]) -> None:
        """
        都道府県データを挿入
        
        Args:
            prefectures: (都道府県名, 地域) のリスト
        """
        cursor = self.connection.cursor()
        cursor.executemany(
            "INSERT OR IGNORE INTO prefectures (name, region) VALUES (?, ?)",
            prefectures
        )
        self.connection.commit()
    
    def insert_job_opening_rates(self, data: pd.DataFrame) -> None:
        """
        有効求人倍率データを挿入
        
        Args:
            data: (prefecture_name, year, month, rate) の列を持つDataFrame
        """
        cursor = self.connection.cursor()
        
        for _, row in data.iterrows():
            # 都道府県IDを取得
            cursor.execute(
                "SELECT id FROM prefectures WHERE name = ?",
                (row['prefecture'],)
            )
            result = cursor.fetchone()
            
            if result:
                prefecture_id = result[0]
                cursor.execute("""
                    INSERT OR REPLACE INTO job_opening_rate 
                    (prefecture_id, year, month, rate)
                    VALUES (?, ?, ?, ?)
                """, (prefecture_id, row['year'], row.get('month'), row['rate']))
        
        self.connection.commit()
    
    def insert_wage_data(self, data: pd.DataFrame) -> None:
        """
        平均賃金データを挿入
        
        Args:
            data: (prefecture_name, year, wage) の列を持つDataFrame
        """
        cursor = self.connection.cursor()
        
        for _, row in data.iterrows():
            # 都道府県IDを取得
            cursor.execute(
                "SELECT id FROM prefectures WHERE name = ?",
                (row['prefecture'],)
            )
            result = cursor.fetchone()
            
            if result:
                prefecture_id = result[0]
                cursor.execute("""
                    INSERT OR REPLACE INTO average_wage
                    (prefecture_id, year, wage)
                    VALUES (?, ?, ?)
                """, (prefecture_id, row['year'], row['wage']))
        
        self.connection.commit()
    
    def get_analysis_data(self, year: int) -> pd.DataFrame:
        """
        分析用データを取得（有効求人倍率と平均賃金を結合）
        
        Args:
            year: 対象年
            
        Returns:
            結合されたデータフレーム
        """
        query = """
            SELECT 
                p.name as prefecture,
                j.rate as job_opening_rate,
                w.wage as average_wage
            FROM prefectures p
            LEFT JOIN job_opening_rate j ON p.id = j.prefecture_id AND j.year = ?
            LEFT JOIN average_wage w ON p.id = w.prefecture_id AND w.year = ?
            WHERE j.rate IS NOT NULL AND w.wage IS NOT NULL
            ORDER BY p.name
        """
        
        df = pd.read_sql_query(query, self.connection, params=(year, year))
        return df
    
    def get_prefectures(self) -> List[str]:
        """すべての都道府県名を取得"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM prefectures ORDER BY name")
        return [row[0] for row in cursor.fetchall()]
    
    def get_yearly_trend(self, prefecture: str) -> pd.DataFrame:
        """
        特定の都道府県の年別トレンドデータを取得
        
        Args:
            prefecture: 都道府県名
            
        Returns:
            トレンドデータフレーム
        """
        query = """
            SELECT 
                j.year,
                j.rate as job_opening_rate,
                w.wage as average_wage
            FROM job_opening_rate j
            LEFT JOIN average_wage w ON j.prefecture_id = w.prefecture_id 
                                    AND j.year = w.year
            WHERE j.prefecture_id = (
                SELECT id FROM prefectures WHERE name = ?
            )
            ORDER BY j.year
        """
        
        df = pd.read_sql_query(query, self.connection, params=(prefecture,))
        return df
    
    def get_statistics(self, year: int) -> dict:
        """
        指定年の統計情報を取得
        
        Args:
            year: 対象年
            
        Returns:
            統計情報の辞書
        """
        query = """
            SELECT 
                COUNT(*) as count,
                AVG(job_opening_rate) as avg_job_rate,
                MIN(job_opening_rate) as min_job_rate,
                MAX(job_opening_rate) as max_job_rate,
                AVG(average_wage) as avg_wage,
                MIN(average_wage) as min_wage,
                MAX(average_wage) as max_wage
            FROM (
                SELECT 
                    j.rate as job_opening_rate,
                    w.wage as average_wage
                FROM prefectures p
                LEFT JOIN job_opening_rate j ON p.id = j.prefecture_id AND j.year = ?
                LEFT JOIN average_wage w ON p.id = w.prefecture_id AND w.year = ?
                WHERE j.rate IS NOT NULL AND w.wage IS NOT NULL
            )
        """
        
        cursor = self.connection.cursor()
        cursor.execute(query, (year, year))
        row = cursor.fetchone()
        
        if row:
            return {
                'count': row[0],
                'avg_job_rate': row[1],
                'min_job_rate': row[2],
                'max_job_rate': row[3],
                'avg_wage': row[4],
                'min_wage': row[5],
                'max_wage': row[6]
            }
        
        return {}


if __name__ == "__main__":
    # テスト実行
    db = DatabaseManager()
    
    # テーブル作成
    db.create_tables()
    print("Database tables created successfully")
    
    # サンプルデータ挿入
    prefectures = [
        ("東京都", "関東"),
        ("大阪府", "関西"),
        ("愛知県", "中部"),
        ("福岡県", "九州"),
    ]
    db.insert_prefectures(prefectures)
    print("Sample prefectures inserted")
    
    db.close()
