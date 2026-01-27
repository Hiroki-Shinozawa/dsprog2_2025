# 都道府県別有効求人倍率と平均賃金の関係分析

## 📋 プロジェクト概要

本プロジェクトは、日本の都道府県における**有効求人倍率**と**平均賃金**の関係を統計的に分析するものです。

### 仮説
> **「有効求人倍率が高い地域ほど賃金も高い」**

労働需要が高い地域では、労働供給を確保するため企業が賃金を引き上げる傾向があるという経済学的仮説を検証します。

### データ取得元
- [e-stat.go.jp](https://www.e-stat.go.jp/) - 政府統計オンラインデータベース
  - 一般職業紹介状況（職業安定業務統計）
  - 賃金構造基本統計調査

## 🏗️ プロジェクト構成

```
最終課題/
├── src/
│   ├── __init__.py           # パッケージ初期化
│   ├── data_fetcher.py       # e-Stat APIからのデータ取得
│   ├── database.py           # SQLiteデータベース管理
│   └── analyzer.py           # 分析・可視化ユーティリティ
├── notebooks/
│   └── analysis.ipynb        # 分析・可視化ノートブック
├── tests/
│   └── test_analyzer.py      # ユニットテスト
├── data/
│   └── analysis.db           # SQLiteデータベース（自動生成）
├── requirements.txt          # 依存パッケージリスト
├── .gitignore                # Git除外ファイル
└── README.md                 # このファイル
```

## 📊 分析方法

1. **相関分析** - ピアソンの相関係数を用いた関係性の評価
2. **線形回帰分析** - 有効求人倍率から平均賃金を予測
3. **グループ比較** - 高求人倍率地域と低求人倍率地域の賃金比較（t検定）
4. **可視化** - 散布図、ランキングチャート等による視覚化

## 🚀 セットアップと実行

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. e-Stat APIキーの設定

```bash
export ESTAT_API_KEY="your_api_key_here"
```

### 3. 分析ノートブックの実行

```bash
jupyter notebook notebooks/analysis.ipynb
```

### 4. テストの実行

```bash
python -m unittest tests.test_analyzer -v
```

## 📈 主な機能

### `data_fetcher.py` - データ取得
- **EstatDataFetcher クラス**
  - `fetch_job_opening_rate()` - 有効求人倍率データ取得
  - `fetch_wage_data()` - 平均賃金データ取得
  - サーバー負荷対策として `time.sleep()` を実装

### `database.py` - データベース管理
- **DatabaseManager クラス**
  - `create_tables()` - テーブル作成
  - `insert_prefectures()` - 都道府県マスターデータ挿入
  - `insert_job_opening_rates()` - 求人倍率データ挿入
  - `insert_wage_data()` - 賃金データ挿入
  - `get_analysis_data()` - 分析用データ取得（結合済み）
  - `get_yearly_trend()` - 年別トレンドデータ取得
  - `get_statistics()` - 統計情報取得

### `analyzer.py` - 分析・可視化
- **DataAnalyzer クラス**
  - `calculate_correlation()` - 相関係数とp値計算
  - `linear_regression()` - 線形回帰分析
  - `rank_prefectures()` - 都道府県ランキング作成
  - `get_high_low_pairs()` - グループ分割
  - `compare_groups()` - グループ比較統計

- **VisualizationHelper クラス**
  - `prepare_scatter_data()` - 散布図用データ準備
  - `prepare_bar_data()` - 棒グラフ用データ準備

## 🧪 テストカバレッジ

合計12個のユニットテストを実装：
- ✓ 相関係数計算（空データ含む）
- ✓ 線形回帰分析
- ✓ ランキング作成
- ✓ グループ比較
- ✓ 散布図・棒グラフ用データ準備
- ✓ 統合ワークフロー

すべてのテストが **PASS** しています。

```bash
Ran 12 tests in 0.017s
OK
```

## 🔍 使用した統計手法

1. **ピアソンの相関係数**
   - 2つの連続変数間の線形関係を測定
   - -1 から 1 の範囲（1に近いほど強い正の相関）

2. **線形回帰分析**
   ```
   wage = slope × job_opening_rate + intercept
   ```
   - 求人倍率から賃金を予測
   - R²値でモデルの適合度を評価

3. **独立標本t検定**
   - 2グループ間の平均値の有意差を検証
   - 帰無仮説：2グループの平均値に差がない

## ⚠️ 制限事項と今後の課題

1. **相関と因果の混同を避ける**
   - 相関があっても因果関係を示さない
   - 第三変数の存在を考慮する必要あり

2. **考慮すべき要因**
   - 業種構成による影響
   - 生活コスト地域差
   - 産業用途の地域差

3. **今後の拡張**
   - 時系列分析（複数年度の比較）
   - 産業別分析
   - 地域クラスタリング分析

## 🛠️ 開発に使用した技術

- **Python 3.12**
- **pandas** - データ操作・分析
- **numpy** - 数値計算
- **scipy** - 統計分析
- **matplotlib, seaborn** - データ可視化
- **SQLite** - データベース
- **Jupyter Notebook** - インタラクティブ分析環境
- **unittest** - テスティングフレームワーク

## 📝 ノートブックの構成

`notebooks/analysis.ipynb` は以下のセクションで構成されています：

1. ライブラリのインポート
2. サンプルデータの作成
3. 相関分析
4. 線形回帰分析
5. グループ比較分析
6. 散布図による可視化
7. ランキングチャートの作成
8. 結論と解釈

---

**最後の更新**: 2026年1月27日
- [ ] 機械学習による予測モデル構築
- [ ] インタラクティブなダッシュボード化
- [ ] より詳細なメタデータの取得と処理

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 参考リンク

- [e-Stat（政府統計オンラインデータベース）](https://www.e-stat.go.jp/)
- [一般職業紹介状況](https://www.e-stat.go.jp/dbview?sid=0002035010)
- [賃金構造基本統計調査](https://www.e-stat.go.jp/dbview?sid=0003320010)

## 作成者

データサイエンス・プログラミング講座 最終課題
