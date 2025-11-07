import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from flask_login import current_user
from sqlalchemy import desc, func

from app.modules.dataset.models import Author, DataSet, DOIMapping, DSDownloadRecord, DSMetaData, DSViewRecord
from core.repositories.BaseRepository import BaseRepository

logger = logging.getLogger(__name__)


class AuthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)


class DSDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSDownloadRecord)

    def total_dataset_downloads(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0


class DSMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSMetaData)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.model.query.filter_by(dataset_doi=doi).first()


class DSViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSViewRecord)

    def total_dataset_views(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.model.query.filter_by(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_cookie=user_cookie,
        ).first()

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_date=datetime.now(timezone.utc),
            view_cookie=user_cookie,
        )


class DataSetRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.isnot(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DataSet.id == dataset_id, DSMetaData.dataset_doi.is_(None))
            .first()
        )

    def count_synchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.isnot(None)).count()

    def count_unsynchronized_datasets(self):
        return self.model.query.join(DSMetaData).filter(DSMetaData.dataset_doi.is_(None)).count()

    def latest_synchronized(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .order_by(desc(self.model.id))
            .limit(5)
            .all()
        )

    def get_trending_datasets_by_downloads(self, days: int = 7, limit: int = 10):
        # Devuelve los datasets más descargados en los últimos `days` días (por defecto 7).
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            self.model.query
            .join(DSDownloadRecord, DSDownloadRecord.dataset_id == self.model.id)
            .filter(DSDownloadRecord.download_date >= cutoff)
            .group_by(self.model.id)
            .order_by(desc(func.count(DSDownloadRecord.id)))
            .limit(limit)
            .all()
        )
    
    def get_number_of_downloads(self, dataset_id: int, days: int = 7) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            DSDownloadRecord.query
            .filter(
                DSDownloadRecord.dataset_id == dataset_id,
                DSDownloadRecord.download_date >= cutoff
            )
            .count()
        )

    def get_trending_datasets_by_views(self, days: int = 7, limit: int = 10):
        # Devuelve los datasets más vistos en los últimos `days` días (por defecto 7)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            self.model.query
            .join(DSViewRecord, DSViewRecord.dataset_id == self.model.id)
            .filter(DSViewRecord.view_date >= cutoff)
            .group_by(self.model.id)
            .order_by(desc(func.count(DSViewRecord.id)))
            .limit(limit)
            .all()
        )
    
    def get_number_of_views(self, dataset_id: int, days: int = 7) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            DSViewRecord.query
            .filter(
                DSViewRecord.dataset_id == dataset_id,
                DSViewRecord.view_date >= cutoff
            )
            .count()
        )

class DOIMappingRepository(BaseRepository):
    def __init__(self):
        super().__init__(DOIMapping)

    def get_new_doi(self, old_doi: str) -> str:
        return self.model.query.filter_by(dataset_doi_old=old_doi).first()
