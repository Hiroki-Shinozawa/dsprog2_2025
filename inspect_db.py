#!/usr/bin/env python3
"""
SQLiteデータベースの内容を確認するスクリプト
"""

import sqlite3
from pathlib import Path
import pandas as pd


def inspect_database():
    """データベースの内容を表示"""
    
    db_path = Path(__file__).parent / "data" / "analysis.db"
    
    print("\n" + "="*70)
    print(f"【SQLiteデータベース検査】")
    print(f"ファイル: {db_path.name}")
    print("="*70)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # ========================
        # テーブル一覧
        # ========================
        print("\n【1. テーブル一覧】")
        print("-"*70)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if tables:
            for table in tables:
                print(f"  - {table}")
        else:
            print("  (テーブルなし)")
        
        # ========================
        # 各テーブルの詳細
        # ========================
        for table in tables:
            print(f"\n【2. テーブル: {table}】")
            print("-"*70)
            
            # スキーマ情報
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            print(f"\n  スキーマ:")
            for col_id, name, type_, notnull, default_val, pk in columns:
                null_str = "NOT NULL" if notnull else "NULL"
                pk_str = " [PRIMARY KEY]" if pk else ""
                print(f"    {name:20s} {type_:15s} {null_str:10s}{pk_str}")
            
            # データ件数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            print(f"\n  データ件数: {row_count}")
            
            # 実際のデータを表示
            if row_count > 0:
                print(f"\n  データ内容:")
                df = pd.read_sql(f"SELECT * FROM {table}", conn)
                
                if row_count <= 10:
                    print(df.to_string(index=False))
                else:
                    print("\n  【最初の5行】")
                    print(df.head().to_string(index=False))
                    print("\n  【最後の5行】")
                    print(df.tail().to_string(index=False))
                    print(f"\n  ... 他 {row_count - 10} 行")
        
        # ========================
        # SQLクエリ実行例
        # ========================
        print("\n【3. サンプルクエリ実行例】")
        print("-"*70)
        
        if 'analysis_results' in tables:
            print("\n  SQL: SELECT * FROM analysis_results;")
            df = pd.read_sql("SELECT * FROM analysis_results", conn)
            if len(df) > 0:
                print(df.to_string(index=False))
            else:
                print("  (データなし)")
        
        if 'employment_data' in tables:
            print("\n  SQL: SELECT COUNT(*) as count FROM employment_data;")
            cursor.execute("SELECT COUNT(*) FROM employment_data")
            count = cursor.fetchone()[0]
            print(f"  結果: {count}")
        
        conn.close()
        print("\n" + "="*70 + "\n")
        
    except sqlite3.DatabaseError as e:
        print(f"\n✗ データベースエラー: {e}")
    except FileNotFoundError:
        print(f"\n✗ ファイルが見つかりません: {db_path}")
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    inspect_database()
