# 一般職業紹介状況の分析

## 📋 プロジェクト概要

本プロジェクトは、日本の**一般職業紹介状況**に関する統計データを分析するものです。労働市場の動向、職業別の求人状況、地域別の特徴などを包括的に分析します。

### データソース
- **第２０表**: 一般職業紹介状況（職業安定業務統計）
  - 調査年月: 2024年3月
  - 公開日: 2024-04-30
  - データ形式: XLSX

### 追加データソース
- **e-Stat API**: 賃金構造基本統計調査
  - API URL: http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?appId=&lang=J&statsDataId=0001867092&metaGetFlg=Y&cntGetFlg=N&explanationGetFlg=Y&annotationGetFlg=Y&sectionHeaderFlg=1&replaceSpChars=0
  - 公開日: 2024-11-27

## 🏗️ プロジェクト構成

```
最終課題/
├── src/
│   ├── __init__.py              # パッケージ初期化
│   ├── data_loader.py           # Excelデータ読み込み
│   ├── api_fetcher.py           # e-Stat APIからのデータ取得
│   ├── database.py              # SQLiteデータベース管理
│   └── analyzer.py              # データ分析・可視化
├── notebooks/
│   └── analysis.ipynb           # 分析・可視化ノートブック
├── data/
│   └── 第20表.xlsx              # 一般職業紹介状況データ
├── tests/
│   ├── test_data_loader.py      # データ読み込みテスト
│   └── test_api_fetcher.py      # API取得テスト
├── requirements.txt             # 依存パッケージリスト
└── README.md                    # このファイル
```

## 📊 分析内容

1. **基本統計量の計算** - 平均、標準偏差、中央値など
2. **時系列分析** - 求人数、就職者数の推移
3. **職業別・地域別分析** - 異なる職業や地域間の比較
4. **可視化** - グラフやチャートによる結果表示

## 🚀 セットアップと実行

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. データの確認

データは `data/第20表.xlsx` に配置されています。

### 3. 分析ノートブックの実行

```bash
jupyter notebook notebooks/analysis.ipynb
```

## 📝 ファイル説明

- **data_loader.py**: Excelファイルから職業紹介状況データを読み込み
- **api_fetcher.py**: e-Stat APIから賃金統計データを取得
- **database.py**: データベースへのデータ保存・クエリ
- **analyzer.py**: 統計分析と可視化処理

## 🔧 技術スタック

- Python 3.10+
- pandas: データ操作
- openpyxl: Excel読み込み
- requests: API通信
- sqlite3: データベース
- matplotlib/seaborn: 可視化
- numpy/scipy: 統計計算
- jupyter: ノートブック環境

## 📞 注記

APIを使用する場合、appIdの設定が必要です。
