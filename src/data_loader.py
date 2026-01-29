"""
Excelデータローダーモジュール
一般職業紹介状況データを読み込む機能を提供
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple


class DataLoader:
    """一般職業紹介状況のExcelデータを読み込むクラス"""
    
    def __init__(self, excel_path: str = None):
        """
        初期化
        
        Args:
            excel_path: Excelファイルのパス
        """
        if excel_path is None:
            # デフォルトのパスを設定
            current_dir = Path(__file__).parent.parent
            excel_path = current_dir / "data" / "第20表.xlsx"
        
        self.excel_path = Path(excel_path)
        self.data = None
        self.metadata = {}
    
    def load_data(self, sheet_name=0) -> pd.DataFrame:
        """
        Excelファイルからデータを読み込む
        
        Args:
            sheet_name: シート名またはシートのインデックス
        
        Returns:
            pd.DataFrame: 読み込んだデータフレーム
        """
        if not self.excel_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.excel_path}")
        
        try:
            self.data = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            print(f"✓ データを読み込みました: {self.excel_path.name}")
            print(f"  行数: {len(self.data)}, 列数: {len(self.data.columns)}")
            return self.data
        except Exception as e:
            raise ValueError(f"データ読み込みエラー: {e}")
    
    def get_sheet_names(self) -> List[str]:
        """
        Excelファイルのシート名一覧を取得
        
        Returns:
            List[str]: シート名のリスト
        """
        xls = pd.ExcelFile(self.excel_path)
        return xls.sheet_names
    
    def get_column_info(self) -> Dict:
        """
        カラム情報を取得
        
        Returns:
            Dict: カラム情報
        """
        if self.data is None:
            raise ValueError("データが読み込まれていません")
        
        info = {
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'shape': self.data.shape
        }
        return info
    
    def get_basic_stats(self) -> pd.DataFrame:
        """
        基本統計量を計算
        
        Returns:
            pd.DataFrame: 基本統計量
        """
        if self.data is None:
            raise ValueError("データが読み込まれていません")
        
        return self.data.describe()
    
    def clean_data(self) -> pd.DataFrame:
        """
        データをクリーニング
        - 欠損値の処理
        - データ型の修正
        
        Returns:
            pd.DataFrame: クリーニング済みデータ
        """
        if self.data is None:
            raise ValueError("データが読み込まれていません")
        
        # 欠損値の確認
        print("欠損値の確認:")
        print(self.data.isnull().sum())
        
        # 欠損値の処理（数値列は0で埋める、その他は削除）
        numeric_cols = self.data.select_dtypes(include=['number']).columns
        self.data[numeric_cols] = self.data[numeric_cols].fillna(0)
        self.data = self.data.dropna()
        
        return self.data


def load_employment_data(excel_path: str = None) -> pd.DataFrame:
    """
    一般職業紹介状況データを読み込む関数
    
    Args:
        excel_path: Excelファイルのパス
    
    Returns:
        pd.DataFrame: 読み込んだデータ
    """
    loader = DataLoader(excel_path)
    return loader.load_data()


if __name__ == "__main__":
    # テスト実行
    try:
        loader = DataLoader()
        
        print("シート一覧:")
        sheets = loader.get_sheet_names()
        for sheet in sheets:
            print(f"  - {sheet}")
        
        print("\nデータ読み込み...")
        data = loader.load_data()
        
        print("\nカラム情報:")
        info = loader.get_column_info()
        for col in info['columns'][:10]:  # 最初の10列のみ表示
            print(f"  - {col}")
        
        print("\n基本統計量:")
        print(loader.get_basic_stats())
    
    except FileNotFoundError as e:
        print(f"✗ エラー: ファイルが見つかりません")
        print(f"  詳細: {e}")
        print(f"\n確認事項:")
        print(f"  - data/第20表.xlsx が存在しますか?")
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        print(f"\nデータが正しく読み込めない場合は以下をご確認ください:")
        print(f"  - Excelファイルが /最終課題/data/第20表.xlsx に存在すること")
        print(f"  - ファイルが破損していないこと")
