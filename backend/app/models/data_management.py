from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum
import json

Base = declarative_base()

class DataSourceStatus(str, enum.Enum):
    """データソースステータス"""
    ACTIVE = "active"           # アクティブ
    INACTIVE = "inactive"       # 非アクティブ  
    MAINTENANCE = "maintenance" # メンテナンス中
    ERROR = "error"            # エラー状態

class UpdateFrequency(str, enum.Enum):
    """更新頻度"""
    REAL_TIME = "real_time"    # リアルタイム
    HOURLY = "hourly"          # 1時間毎
    DAILY = "daily"            # 日次
    WEEKLY = "weekly"          # 週次
    MONTHLY = "monthly"        # 月次
    QUARTERLY = "quarterly"    # 四半期毎
    YEARLY = "yearly"          # 年次
    MANUAL = "manual"          # 手動

class DataQualityLevel(str, enum.Enum):
    """データ品質レベル"""
    EXCELLENT = "excellent"    # 優秀 (95-100%)
    GOOD = "good"             # 良好 (80-94%)
    FAIR = "fair"             # 普通 (60-79%)
    POOR = "poor"             # 不良 (40-59%)
    CRITICAL = "critical"     # 危険 (0-39%)

class TaskStatus(str, enum.Enum):
    """タスクステータス"""
    PENDING = "pending"        # 待機中
    RUNNING = "running"        # 実行中
    SUCCESS = "success"        # 成功
    FAILED = "failed"         # 失敗
    CANCELLED = "cancelled"    # キャンセル

class DataSource(Base):
    """データソース管理モデル"""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False)  # api, csv, excel, database等
    
    # 接続情報
    endpoint_url = Column(String(500), nullable=True)
    api_key = Column(String(255), nullable=True)
    authentication_method = Column(String(50), nullable=True)
    connection_params = Column(JSON, nullable=True)  # その他の接続パラメータ
    
    # データ情報
    data_format = Column(String(50), nullable=True)  # json, csv, xml等
    encoding = Column(String(20), default="utf-8", nullable=False)
    table_name = Column(String(100), nullable=True)  # 保存先テーブル名
    
    # 更新設定
    update_frequency = Column(Enum(UpdateFrequency), default=UpdateFrequency.DAILY, nullable=False)
    update_schedule = Column(String(100), nullable=True)  # cron形式のスケジュール
    last_updated = Column(DateTime, nullable=True)
    next_update = Column(DateTime, nullable=True)
    
    # ステータス・品質
    status = Column(Enum(DataSourceStatus), default=DataSourceStatus.ACTIVE, nullable=False)
    quality_level = Column(Enum(DataQualityLevel), default=DataQualityLevel.GOOD, nullable=False)
    quality_score = Column(Float, default=0.0, nullable=False)
    
    # メタデータ
    data_owner = Column(String(100), nullable=True)
    license_info = Column(Text, nullable=True)
    usage_restrictions = Column(Text, nullable=True)
    
    # システム情報
    created_by = Column(Integer, nullable=True)  # ユーザーID
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class DataUpdateTask(Base):
    """データ更新タスクモデル"""
    __tablename__ = "data_update_tasks"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, nullable=False, index=True)
    task_name = Column(String(200), nullable=False)
    task_type = Column(String(50), nullable=False)  # extract, transform, load, validate
    
    # タスク設定
    parameters = Column(JSON, nullable=True)
    schedule = Column(String(100), nullable=True)  # cron形式
    priority = Column(Integer, default=5, nullable=False)  # 1-10 (高-低)
    timeout_seconds = Column(Integer, default=3600, nullable=False)
    
    # 実行情報
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # 結果情報
    records_processed = Column(Integer, default=0, nullable=False)
    records_success = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_log = Column(Text, nullable=True)
    
    # システム情報
    created_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class DataQualityCheck(Base):
    """データ品質チェックモデル"""
    __tablename__ = "data_quality_checks"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, nullable=False, index=True)
    check_name = Column(String(200), nullable=False)
    check_type = Column(String(50), nullable=False)  # completeness, accuracy, consistency, validity
    
    # チェック設定
    check_rule = Column(Text, nullable=False)  # JSON形式のルール定義
    severity_level = Column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    threshold_value = Column(Float, nullable=True)
    
    # 実行結果
    last_check_at = Column(DateTime, nullable=True)
    last_result = Column(Boolean, nullable=True)
    last_score = Column(Float, nullable=True)
    last_message = Column(Text, nullable=True)
    
    # 統計情報
    total_checks = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failure_count = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    
    # システム情報
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class DataQualityMetric(Base):
    """データ品質メトリクスモデル"""
    __tablename__ = "data_quality_metrics"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, nullable=False, index=True)
    metric_date = Column(DateTime, nullable=False, index=True)
    
    # 品質メトリクス
    completeness_score = Column(Float, default=0.0, nullable=False)      # 完全性
    accuracy_score = Column(Float, default=0.0, nullable=False)          # 正確性
    consistency_score = Column(Float, default=0.0, nullable=False)       # 一貫性
    validity_score = Column(Float, default=0.0, nullable=False)          # 妥当性
    timeliness_score = Column(Float, default=0.0, nullable=False)        # 適時性
    uniqueness_score = Column(Float, default=0.0, nullable=False)        # 一意性
    
    # 総合スコア
    overall_score = Column(Float, default=0.0, nullable=False)
    quality_level = Column(Enum(DataQualityLevel), default=DataQualityLevel.GOOD, nullable=False)
    
    # 詳細情報
    total_records = Column(Integer, default=0, nullable=False)
    null_records = Column(Integer, default=0, nullable=False)
    duplicate_records = Column(Integer, default=0, nullable=False)
    invalid_records = Column(Integer, default=0, nullable=False)
    
    # メタデータ
    check_duration_ms = Column(Integer, nullable=True)
    issues_detected = Column(JSON, nullable=True)  # 検出された問題のリスト
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class DataAlert(Base):
    """データアラートモデル"""
    __tablename__ = "data_alerts"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # quality, update, system
    severity = Column(String(20), nullable=False)    # low, medium, high, critical
    
    # アラート内容
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    # ステータス
    is_resolved = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(Integer, nullable=True)  # ユーザーID
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # 通知設定
    notification_sent = Column(Boolean, default=False, nullable=False)
    notification_channels = Column(JSON, nullable=True)  # email, slack等
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class DataUpdateLog(Base):
    """データ更新ログモデル"""
    __tablename__ = "data_update_logs"

    id = Column(Integer, primary_key=True, index=True)
    data_source_id = Column(Integer, nullable=False, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    
    # ログ情報
    log_level = Column(String(20), nullable=False)    # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_message = Column(Text, nullable=False)
    log_context = Column(JSON, nullable=True)         # 追加コンテキスト情報
    
    # 実行情報
    execution_step = Column(String(50), nullable=True) # extract, transform, load, validate
    records_affected = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # エラー情報
    error_code = Column(String(50), nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class DataLineage(Base):
    """データ系譜モデル"""
    __tablename__ = "data_lineage"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False, index=True)     # 元データソース
    target_id = Column(Integer, nullable=False, index=True)     # 変換後データソース
    transformation_type = Column(String(50), nullable=False)    # join, aggregate, filter等
    
    # 変換情報
    transformation_rule = Column(JSON, nullable=False)
    transformation_logic = Column(Text, nullable=True)
    dependency_level = Column(Integer, default=1, nullable=False)
    
    # メタデータ
    created_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> dict:
        """データ系譜情報を辞書形式で返す"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "transformation_type": self.transformation_type,
            "transformation_rule": json.loads(self.transformation_rule) if self.transformation_rule else None,
            "transformation_logic": self.transformation_logic,
            "dependency_level": self.dependency_level,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }