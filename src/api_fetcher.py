"""
e-Stat APIデータフェッチャーモジュール
賃金構造基本統計調査のデータをAPIから取得
"""

import requests
import json
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime
import time


class EStatAPIFetcher:
    """e-Stat APIからデータを取得するクラス"""
    
    BASE_URL = "http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    
    def __init__(self, app_id: str = ""):
        """
        初期化
        
        Args:
            app_id: e-Stat APIアプリケーションID
        """
        self.app_id = app_id
        self.last_response = None
        self.metadata = {}
    
    def set_app_id(self, app_id: str):
        """
        アプリケーションIDを設定
        
        Args:
            app_id: e-Stat APIアプリケーションID
        """
        self.app_id = app_id
        print(f"✓ アプリケーションIDを設定しました")
    
    def fetch_wage_statistics(self, 
                             stats_data_id: str = "0001867092",
                             params: Optional[Dict] = None,
                             request_delay: float = 1.0) -> Dict:
        """
        賃金構造基本統計調査データを取得
        
        Args:
            stats_data_id: 統計表ID（デフォルト: 賃金構造基本統計調査）
            params: 追加パラメータ
            request_delay: APIリクエスト間隔（秒）- サーバ負荷対応
        
        Returns:
            Dict: APIレスポンス
        """
        if not self.app_id:
            print("⚠️  警告: アプリケーションIDが設定されていません")
            print("   set_app_id()でIDを設定してください")
            return {}
        
        # デフォルトパラメータ
        request_params = {
            'appId': self.app_id,
            'lang': 'J',
            'statsDataId': stats_data_id,
            'metaGetFlg': 'Y',
            'cntGetFlg': 'N',
            'explanationGetFlg': 'Y',
            'annotationGetFlg': 'Y',
            'sectionHeaderFlg': '1',
            'replaceSpChars': '0'
        }
        
        # パラメータを更新
        if params:
            request_params.update(params)
        
        try:
            print(f"APIリクエストを送信中... (statsDataId: {stats_data_id})")
            print(f"  サーバ負荷対応: {request_delay}秒のディレイを使用")
            
            # サーバ負荷対応: リクエスト前にスリープ
            time.sleep(request_delay)
            
            response = requests.get(self.BASE_URL, params=request_params, timeout=30)
            response.raise_for_status()
            
            self.last_response = response.json()
            print("✓ APIレスポンスを受信しました")
            
            return self.last_response
        
        except requests.exceptions.RequestException as e:
            print(f"✗ APIリクエスト失敗: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"✗ JSONデコード失敗: {e}")
            return {}
    
    def parse_response(self, response: Dict) -> pd.DataFrame:
        """
        APIレスポンスをパースしてDataFrameに変換
        
        Args:
            response: APIレスポンス
        
        Returns:
            pd.DataFrame: パースされたデータフレーム
        """
        try:
            if not response or 'result' not in response:
                print("✗ レスポンスが空または不正な形式です")
                return pd.DataFrame()
            
            # メタデータの抽出
            if 'metadata' in response.get('result', {}).get('statDesc', {}):
                self.metadata = response['result']['statDesc']['metadata']
            
            # データの抽出
            if 'data' not in response.get('result', {}):
                print("✗ レスポンスにデータが含まれていません")
                return pd.DataFrame()
            
            data_list = response['result']['data']
            
            # リストをDataFrameに変換
            df = pd.DataFrame(data_list)
            print(f"✓ データをパースしました: {len(df)}行")
            
            return df
        
        except Exception as e:
            print(f"✗ パース処理エラー: {e}")
            return pd.DataFrame()
    
    def get_stats_info(self) -> Dict:
        """
        統計情報を取得
        
        Returns:
            Dict: 統計情報
        """
        if not self.metadata:
            return {}
        
        info = {
            '公開日': self.metadata.get('UPDATED_DATE', 'N/A'),
            '調査年月': self.metadata.get('SURVEY_MONTH', 'N/A'),
            '統計名': self.metadata.get('STAT_NAME', 'N/A'),
        }
        
        return info


class APIDataManager:
    """複数のAPIからデータを管理するクラス"""
    
    def __init__(self, app_id: str = ""):
        """
        初期化
        
        Args:
            app_id: e-Stat APIアプリケーションID
        """
        self.fetcher = EStatAPIFetcher(app_id)
        self.cached_data = {}
    
    def fetch_wage_data(self, stats_data_id: str = "0001867092") -> pd.DataFrame:
        """
        賃金統計データを取得
        
        Args:
            stats_data_id: 統計表ID
        
        Returns:
            pd.DataFrame: 賃金データ
        """
        response = self.fetcher.fetch_wage_statistics(stats_data_id)
        data = self.fetcher.parse_response(response)
        
        if not data.empty:
            self.cached_data['wage'] = data
        
        return data
    
    def get_cached_data(self, key: str) -> Optional[pd.DataFrame]:
        """
        キャッシュされたデータを取得
        
        Args:
            key: データキー
        
        Returns:
            pd.DataFrame: キャッシュデータ、またはNone
        """
        return self.cached_data.get(key)
    
    def print_stats_info(self):
        """統計情報を表示"""
        info = self.fetcher.get_stats_info()
        if info:
            print("\n統計情報:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print("統計情報が利用できません")


if __name__ == "__main__":
    # テスト実行
    manager = APIDataManager()
    
    print("e-Stat API フェッチャー")
    print("=" * 50)
    print("\nアプリケーションIDを設定してください:")
    print("  manager.fetcher.set_app_id('YOUR_APP_ID')")
    print("\n賃金データを取得:")
    print("  data = manager.fetch_wage_data()")
    print("\n統計情報を表示:")
    print("  manager.print_stats_info()")
