# 鳥取県住みやすさ創出プロジェクト - バックエンドAPI

## 概要
統計データ分析・可視化・政策支援のためのFastAPI基盤。

## 技術スタック
- **Python**: 3.11+
- **FastAPI**: RESTful API フレームワーク
- **PostgreSQL**: メインデータベース
- **Redis**: キャッシュ・セッション管理
- **SQLAlchemy**: ORM
- **Alembic**: データベースマイグレーション
- **Docker**: コンテナ化

## セットアップ

### 前提条件
- Docker & Docker Compose
- Python 3.11+ (ローカル開発の場合)

### 1. リポジトリクローン
```bash
git clone <repository-url>
cd stat-tottori/backend
```

### 2. 環境変数設定
```bash
cp .env.example .env
# .envファイルを編集して適切な値を設定
```

### 3. Docker Composeでサービス起動
```bash
docker-compose up -d
```

### 4. データベースマイグレーション
```bash
# コンテナ内でマイグレーション実行
docker-compose exec api alembic upgrade head
```

## API エンドポイント

### ヘルスチェック
- `GET /` - API基本情報
- `GET /health` - ヘルスチェック

### 人口データ (`/api/v1/population/`)
- `GET /` - 人口データ一覧
- `GET /summary` - 人口サマリー
- `GET /trend` - 人口推移（Chart.js用）
- `GET /forecast` - 人口予測

### 住みやすさ (`/api/v1/livability/`)
- `GET /scores` - 住みやすさスコア
- `GET /comparison` - 地域比較
- `GET /radar-chart` - レーダーチャート用データ
- `GET /indicators` - 指標マスターデータ
- `POST /calculate-score` - カスタムスコア計算

### 統計分析 (`/api/v1/statistics/`)
- `GET /kpi-dashboard` - KPIダッシュボード用データ
- `GET /correlation-matrix` - 相関関係マトリクス
- `GET /time-series-analysis` - 時系列分析
- `GET /comparative-analysis` - 地域間比較分析
- `GET /geographic-data` - 地図表示用データ

## 開発

### ローカル開発環境
```bash
# 依存パッケージインストール
pip install -r requirements.txt

# 開発サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API ドキュメント
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### データベース管理
- pgAdmin: http://localhost:5050
  - Email: admin@stat-tottori.local
  - Password: admin

## データベース構造

### 主要テーブル
- `population_data` - 人口データ
- `population_forecasts` - 人口予測データ
- `livability_scores` - 住みやすさスコア
- `livability_indicators` - 住みやすさ指標マスター
- `user_livability_weights` - ユーザー重み設定

### マイグレーション
```bash
# 新しいマイグレーション作成
docker-compose exec api alembic revision --autogenerate -m "description"

# マイグレーション適用
docker-compose exec api alembic upgrade head

# マイグレーション履歴確認
docker-compose exec api alembic history
```

## テスト
```bash
# テスト実行
docker-compose exec api pytest

# カバレッジ付きテスト
docker-compose exec api pytest --cov=app
```

## デプロイ

### 本番環境
1. 環境変数を本番用に設定
2. `DEBUG=False` に設定
3. セキュリティキーを適切に設定
4. HTTPS対応の実施

### 監視・ログ
- アプリケーションログ: `/var/log/app.log`
- PostgreSQLログ: Docker Composeログ
- Redis ログ: Docker Composeログ

## トラブルシューティング

### よくある問題
1. **データベース接続エラー**
   - PostgreSQLコンテナが起動しているか確認
   - DATABASE_URL設定を確認

2. **Redisキャッシュエラー**
   - Redisコンテナが起動しているか確認
   - REDIS_URL設定を確認

3. **マイグレーションエラー**
   - データベースが初期化されているか確認
   - テーブル構造の競合がないか確認