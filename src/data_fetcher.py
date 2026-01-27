"""
e-stat APIからデータを取得するモジュール
有効求人倍率と平均賃金データを取得
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional
import pandas as pd

# e-stat APIの設定
ESTAT_BASE_URL = "https://www.e-stat.go.jp/api/1.0"
ESTAT_API_KEY = os.getenv("ESTAT_API_KEY", "YOUR_API_KEY_HERE")

# 統計表ID（e-statの統計表ID）
# 一般職業紹介状況（有効求人倍率）: 00200563
# 賃金構造基本統計調査（平均賃金）: 00330001


class EstatDataFetcher:
    """e-stat APIからデータを取得するクラス"""
    
    def __init__(self, api_key: str):
        """
        初期化
        
        Args:
            api_key: e-stat APIキー
        """
        self.api_key = api_key
        self.base_url = ESTAT_BASE_URL
        
    def fetch_job_opening_rate(self, year: int = 2023) -> Optional[pd.DataFrame]:
        """
        有効求人倍率データを取得
        
        Args:
            year: 取得対象年
            
        Returns:
            データフレーム（都道府県、有効求人倍率）
        """
        try:
            # 統計表ID: 00200563 - 一般職業紹介状況
            table_id = "00200563"
            
            params = {
                "apikey": self.api_key,
                "statsDataId": table_id,
                "limit": 100000,
                "cdTime": year
            }
            
            response = requests.get(
                f"{self.base_url}/json/get_data",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                return None
                
            data = response.json()
            
            if "result" not in data or data["result"]["error_msg"]:
                print(f"API Error: {data.get('result', {}).get('error_msg', 'Unknown error')}")
                return None
            
            # データの処理
            df = self._process_estat_data(data)
            time.sleep(1)  # サーバー負荷対策
            
            return df
            
        except Exception as e:
            print(f"Error fetching job opening rate: {e}")
            return None
    
    def fetch_wage_data(self, year: int = 2023) -> Optional[pd.DataFrame]:
        """
        平均賃金データを取得
        
        Args:
            year: 取得対象年
            
        Returns:
            データフレーム（都道府県、平均賃金）
        """
        try:
            # 統計表ID: 00330001 - 賃金構造基本統計調査
            table_id = "00330001"
            
            params = {
                "apikey": self.api_key,
                "statsDataId": table_id,
                "limit": 100000,
                "cdTime": year
            }
            
            response = requests.get(
                f"{self.base_url}/json/get_data",
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                return None
                
            data = response.json()
            
            if "result" not in data or data["result"]["error_msg"]:
                print(f"API Error: {data.get('result', {}).get('error_msg', 'Unknown error')}")
                return None
            
            # データの処理
            df = self._process_estat_data(data)
            time.sleep(1)  # サーバー負荷対策
            
            return df
            
        except Exception as e:
            print(f"Error fetching wage data: {e}")
            return None
    
    def _process_estat_data(self, data: Dict) -> pd.DataFrame:
        """
        e-stat APIからのレスポンスを処理してDataFrameに変換
        
        Args:
            data: APIレスポンスのJSON
            
        Returns:
            処理済みのDataFrame
        """
        records = []
        
        # e-statのレスポンス形式に応じて処理
        if "result" in data and "data" in data["result"]:
            for item in data["result"]["data"]:
                # 必要なフィールドを抽出
                record = {
                    "prefecture": item.get("全国", ""),
                    "value": item.get("value", 0),
                    "time": item.get("時間軸", "")
                }
                records.append(record)
        
        return pd.DataFrame(records)


def fetch_all_data(api_key: str, year: int = 2023) -> tuple:
    """
    有効求人倍率と平均賃金データを取得
    
    Args:
        api_key: e-stat APIキー
        year: 取得対象年
        
    Returns:
        (有効求人倍率DF, 平均賃金DF)のタプル
    """
    fetcher = EstatDataFetcher(api_key)
    
    print(f"Fetching job opening rate data for {year}...")
    job_opening_df = fetcher.fetch_job_opening_rate(year)
    
    print(f"Fetching wage data for {year}...")
    wage_df = fetcher.fetch_wage_data(year)
    
    return job_opening_df, wage_df


if __name__ == "__main__":
    # テスト実行
    api_key = os.getenv("ESTAT_API_KEY", "")
    
    if not api_key:
        print("Warning: ESTAT_API_KEY environment variable not set")
        print("Please set your e-stat API key before running this script")
    else:
        job_df, wage_df = fetch_all_data(api_key)
        
        if job_df is not None:
            print("\n=== Job Opening Rate Data ===")
            print(job_df.head())
            
        if wage_df is not None:
            print("\n=== Wage Data ===")
            print(wage_df.head())
