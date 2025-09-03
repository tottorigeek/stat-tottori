import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import pandas as pd
import json
import traceback
from concurrent.futures import ThreadPoolExecutor
import schedule
import time

from app.models.data_management import (
    DataSource, DataUpdateTask, DataQualityCheck, DataQualityMetric, 
    DataAlert, DataUpdateLog, TaskStatus, DataQualityLevel, DataSourceStatus
)
from app.db.database import get_db
from app.services.data_collectors import DataCollectorFactory
from app.services.data_quality_service import DataQualityService
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class DataPipeline:
    """データパイプライン管理クラス"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.quality_service = DataQualityService()
        self.notification_service = NotificationService()
        self.collector_factory = DataCollectorFactory()
        self.running_tasks = {}  # 実行中タスクの管理
        
    async def execute_data_update_task(
        self, 
        task_id: int, 
        db: Session,
        force_run: bool = False
    ) -> bool:
        """データ更新タスクの実行"""
        
        task = db.query(DataUpdateTask).filter(DataUpdateTask.id == task_id).first()
        if not task:
            logger.error(f"タスクが見つかりません: {task_id}")
            return False
        
        data_source = db.query(DataSource).filter(DataSource.id == task.data_source_id).first()
        if not data_source:
            logger.error(f"データソースが見つかりません: {task.data_source_id}")
            return False
        
        # タスクが既に実行中の場合はスキップ
        if task.status == TaskStatus.RUNNING and not force_run:
            logger.warning(f"タスクは既に実行中です: {task_id}")
            return False
        
        start_time = datetime.utcnow()
        
        try:
            # タスクステータスを実行中に更新
            task.status = TaskStatus.RUNNING
            task.started_at = start_time
            task.error_message = None
            db.commit()
            
            self.running_tasks[task_id] = {
                'task': task,
                'data_source': data_source,
                'start_time': start_time
            }
            
            # ログ記録
            self._log_message(
                db, data_source.id, task_id, "INFO", 
                f"タスク開始: {task.task_name}", {"task_type": task.task_type}
            )
            
            # タスクタイプに応じた処理実行
            success = await self._execute_task_by_type(task, data_source, db)
            
            # 実行時間計算
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # タスクステータス更新
            task.status = TaskStatus.SUCCESS if success else TaskStatus.FAILED
            task.completed_at = end_time
            task.execution_time_ms = execution_time_ms
            
            if success:
                # データソースの最終更新時刻を更新
                data_source.last_updated = end_time
                data_source.next_update = self._calculate_next_update(data_source)
                
                # 品質チェック実行
                await self._run_quality_checks(data_source, db)
                
                self._log_message(
                    db, data_source.id, task_id, "INFO", 
                    f"タスク完了: {task.task_name}", 
                    {
                        "execution_time_ms": execution_time_ms,
                        "records_processed": task.records_processed
                    }
                )
            
            db.commit()
            
            return success
            
        except Exception as e:
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            # エラー処理
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error_message = error_message
            task.execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # データソースステータス更新
            data_source.status = DataSourceStatus.ERROR
            
            # エラーログ記録
            self._log_message(
                db, data_source.id, task_id, "ERROR", 
                f"タスク失敗: {error_message}",
                {"stack_trace": stack_trace}
            )
            
            # アラート生成
            await self._create_alert(
                db, data_source.id, "update", "high",
                f"データ更新失敗: {data_source.name}",
                f"タスク「{task.task_name}」でエラーが発生しました: {error_message}"
            )
            
            db.commit()
            logger.error(f"タスク実行エラー ({task_id}): {error_message}")
            
            return False
            
        finally:
            # 実行中タスクから削除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def _execute_task_by_type(
        self, 
        task: DataUpdateTask, 
        data_source: DataSource, 
        db: Session
    ) -> bool:
        """タスクタイプ別の処理実行"""
        
        try:
            if task.task_type == "extract":
                return await self._execute_extract_task(task, data_source, db)
            elif task.task_type == "transform":
                return await self._execute_transform_task(task, data_source, db)
            elif task.task_type == "load":
                return await self._execute_load_task(task, data_source, db)
            elif task.task_type == "validate":
                return await self._execute_validate_task(task, data_source, db)
            else:
                logger.error(f"未対応のタスクタイプ: {task.task_type}")
                return False
                
        except Exception as e:
            logger.error(f"タスク実行エラー ({task.task_type}): {e}")
            raise
    
    async def _execute_extract_task(
        self, 
        task: DataUpdateTask, 
        data_source: DataSource, 
        db: Session
    ) -> bool:
        """データ抽出タスクの実行"""
        
        try:
            # データコレクター取得
            collector = self.collector_factory.get_collector(data_source.source_type)
            if not collector:
                raise ValueError(f"未対応のデータソースタイプ: {data_source.source_type}")
            
            # データ抽出実行
            extracted_data = await collector.extract_data(data_source)
            
            if extracted_data is not None and len(extracted_data) > 0:
                # 一時的にデータを保存（実際の実装では適切なストレージに）
                task.records_processed = len(extracted_data)
                task.records_success = len(extracted_data)
                
                # 抽出データのメタ情報を保存
                self._save_extraction_metadata(db, data_source.id, extracted_data)
                
                return True
            else:
                task.error_message = "データの抽出に失敗しました"
                return False
                
        except Exception as e:
            task.error_message = f"抽出処理エラー: {str(e)}"
            raise
    
    async def _execute_transform_task(
        self, 
        task: DataUpdateTask, 
        data_source: DataSource, 
        db: Session
    ) -> bool:
        """データ変換タスクの実行"""
        
        try:
            # 変換パラメータ取得
            transform_params = task.parameters or {}
            
            # データ変換ロジック実行
            # 実際の実装では、変換ルールに基づいてデータを変換
            
            task.records_processed = transform_params.get('estimated_records', 0)
            task.records_success = task.records_processed
            
            self._log_message(
                db, data_source.id, task.id, "INFO",
                "データ変換完了",
                {"transform_type": transform_params.get('type', 'unknown')}
            )
            
            return True
            
        except Exception as e:
            task.error_message = f"変換処理エラー: {str(e)}"
            raise
    
    async def _execute_load_task(
        self, 
        task: DataUpdateTask, 
        data_source: DataSource, 
        db: Session
    ) -> bool:
        """データロードタスクの実行"""
        
        try:
            # ロードパラメータ取得
            load_params = task.parameters or {}
            target_table = load_params.get('target_table', data_source.table_name)
            
            if not target_table:
                raise ValueError("ロード先テーブルが指定されていません")
            
            # データロード実行
            # 実際の実装では、変換済みデータをターゲットテーブルにロード
            
            task.records_processed = load_params.get('estimated_records', 0)
            task.records_success = task.records_processed
            
            self._log_message(
                db, data_source.id, task.id, "INFO",
                f"データロード完了: {target_table}",
                {"target_table": target_table}
            )
            
            return True
            
        except Exception as e:
            task.error_message = f"ロード処理エラー: {str(e)}"
            raise
    
    async def _execute_validate_task(
        self, 
        task: DataUpdateTask, 
        data_source: DataSource, 
        db: Session
    ) -> bool:
        """データ検証タスクの実行"""
        
        try:
            # 検証パラメータ取得
            validate_params = task.parameters or {}
            
            # データ品質チェック実行
            quality_result = await self.quality_service.run_comprehensive_quality_check(
                data_source.id, db
            )
            
            task.records_processed = quality_result.get('total_records', 0)
            task.records_success = quality_result.get('valid_records', 0)
            task.records_failed = quality_result.get('invalid_records', 0)
            
            # 品質スコア更新
            quality_score = quality_result.get('overall_score', 0.0)
            data_source.quality_score = quality_score
            data_source.quality_level = self._determine_quality_level(quality_score)
            
            self._log_message(
                db, data_source.id, task.id, "INFO",
                f"データ検証完了: 品質スコア {quality_score:.2f}",
                quality_result
            )
            
            return True
            
        except Exception as e:
            task.error_message = f"検証処理エラー: {str(e)}"
            raise
    
    async def _run_quality_checks(self, data_source: DataSource, db: Session):
        """データ品質チェック実行"""
        
        try:
            # アクティブな品質チェック取得
            quality_checks = db.query(DataQualityCheck).filter(
                and_(
                    DataQualityCheck.data_source_id == data_source.id,
                    DataQualityCheck.is_active == True
                )
            ).all()
            
            for check in quality_checks:
                result = await self.quality_service.execute_quality_check(check, db)
                
                if not result['success']:
                    # 品質チェック失敗時のアラート
                    await self._create_alert(
                        db, data_source.id, "quality", check.severity_level,
                        f"品質チェック失敗: {check.check_name}",
                        result.get('error_message', '品質チェックに失敗しました')
                    )
            
        except Exception as e:
            logger.error(f"品質チェック実行エラー: {e}")
    
    def _save_extraction_metadata(self, db: Session, data_source_id: int, data: Any):
        """抽出データのメタデータ保存"""
        
        try:
            metadata = {
                "extraction_time": datetime.utcnow().isoformat(),
                "record_count": len(data) if hasattr(data, '__len__') else None,
                "data_type": type(data).__name__
            }
            
            if isinstance(data, pd.DataFrame):
                metadata.update({
                    "columns": list(data.columns),
                    "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
                    "null_counts": data.isnull().sum().to_dict()
                })
            
            self._log_message(
                db, data_source_id, None, "INFO",
                "抽出メタデータ保存",
                metadata
            )
            
        except Exception as e:
            logger.warning(f"メタデータ保存エラー: {e}")
    
    def _calculate_next_update(self, data_source: DataSource) -> Optional[datetime]:
        """次回更新時刻の計算"""
        
        if not data_source.update_frequency or data_source.update_frequency.value == "manual":
            return None
        
        now = datetime.utcnow()
        
        frequency_map = {
            "hourly": timedelta(hours=1),
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30),  # 概算
            "quarterly": timedelta(days=90),  # 概算
            "yearly": timedelta(days=365)  # 概算
        }
        
        delta = frequency_map.get(data_source.update_frequency.value)
        if delta:
            return now + delta
        
        return None
    
    def _determine_quality_level(self, score: float) -> DataQualityLevel:
        """品質スコアから品質レベルを決定"""
        
        if score >= 95:
            return DataQualityLevel.EXCELLENT
        elif score >= 80:
            return DataQualityLevel.GOOD
        elif score >= 60:
            return DataQualityLevel.FAIR
        elif score >= 40:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.CRITICAL
    
    async def _create_alert(
        self, 
        db: Session, 
        data_source_id: int,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        details: Optional[Dict] = None
    ):
        """アラート作成"""
        
        try:
            alert = DataAlert(
                data_source_id=data_source_id,
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                details=details
            )
            
            db.add(alert)
            db.commit()
            
            # 通知送信
            await self.notification_service.send_alert_notification(alert)
            
        except Exception as e:
            logger.error(f"アラート作成エラー: {e}")
    
    def _log_message(
        self, 
        db: Session,
        data_source_id: int,
        task_id: Optional[int],
        level: str,
        message: str,
        context: Optional[Dict] = None
    ):
        """ログメッセージ記録"""
        
        try:
            log_entry = DataUpdateLog(
                data_source_id=data_source_id,
                task_id=task_id,
                log_level=level,
                log_message=message,
                log_context=context
            )
            
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            logger.warning(f"ログ記録エラー: {e}")
    
    async def run_scheduled_tasks(self, db: Session) -> Dict[str, Any]:
        """スケジュールされたタスクの実行"""
        
        try:
            now = datetime.utcnow()
            
            # 実行対象のタスク検索
            pending_tasks = db.query(DataUpdateTask).filter(
                and_(
                    DataUpdateTask.is_active == True,
                    DataUpdateTask.status.in_([TaskStatus.PENDING]),
                    or_(
                        DataUpdateTask.next_scheduled_run <= now,
                        DataUpdateTask.next_scheduled_run.is_(None)
                    )
                )
            ).limit(50).all()  # 一度に実行するタスク数を制限
            
            results = {
                'total_tasks': len(pending_tasks),
                'success_count': 0,
                'failure_count': 0,
                'executed_tasks': []
            }
            
            # 並行実行
            tasks = []
            for task in pending_tasks:
                task_coroutine = self.execute_data_update_task(task.id, db)
                tasks.append(task_coroutine)
            
            if tasks:
                task_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(task_results):
                    task = pending_tasks[i]
                    
                    if isinstance(result, Exception):
                        results['failure_count'] += 1
                        logger.error(f"タスク実行エラー ({task.id}): {result}")
                    elif result:
                        results['success_count'] += 1
                    else:
                        results['failure_count'] += 1
                    
                    results['executed_tasks'].append({
                        'task_id': task.id,
                        'task_name': task.task_name,
                        'success': isinstance(result, bool) and result
                    })
            
            logger.info(f"スケジュールタスク実行完了: 成功={results['success_count']}, 失敗={results['failure_count']}")
            return results
            
        except Exception as e:
            logger.error(f"スケジュールタスク実行エラー: {e}")
            raise
    
    async def get_pipeline_status(self, db: Session) -> Dict[str, Any]:
        """パイプライン状態取得"""
        
        try:
            # アクティブなデータソース数
            active_sources = db.query(DataSource).filter(
                DataSource.status == DataSourceStatus.ACTIVE
            ).count()
            
            # 実行中タスク数
            running_tasks = db.query(DataUpdateTask).filter(
                DataUpdateTask.status == TaskStatus.RUNNING
            ).count()
            
            # 最近のタスク実行状況
            recent_tasks = db.query(DataUpdateTask).filter(
                DataUpdateTask.completed_at >= datetime.utcnow() - timedelta(hours=24)
            ).all()
            
            success_count = sum(1 for task in recent_tasks if task.status == TaskStatus.SUCCESS)
            failure_count = sum(1 for task in recent_tasks if task.status == TaskStatus.FAILED)
            
            # 未解決アラート数
            unresolved_alerts = db.query(DataAlert).filter(
                DataAlert.is_resolved == False
            ).count()
            
            return {
                'active_data_sources': active_sources,
                'running_tasks': running_tasks,
                'recent_task_stats': {
                    'total': len(recent_tasks),
                    'success': success_count,
                    'failure': failure_count,
                    'success_rate': (success_count / len(recent_tasks) * 100) if recent_tasks else 0
                },
                'unresolved_alerts': unresolved_alerts,
                'system_status': 'healthy' if failure_count < success_count else 'degraded'
            }
            
        except Exception as e:
            logger.error(f"パイプライン状態取得エラー: {e}")
            return {
                'system_status': 'error',
                'error': str(e)
            }