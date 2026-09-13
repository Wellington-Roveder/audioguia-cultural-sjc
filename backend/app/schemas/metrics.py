from uuid import UUID

from pydantic import BaseModel


class WorkMetricsRead(BaseModel):
    work_id: UUID
    access_count: int


class ExhibitionMetricsRead(BaseModel):
    exhibition_id: UUID
    access_count: int
