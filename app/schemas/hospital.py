from typing import Optional, List
from pydantic import BaseModel


class HospitalRowResult(BaseModel):
    row: int
    hospital_id: Optional[int] = None
    name: str
    status: str
    error: Optional[str] = None


class BulkCreateAcceptedResponse(BaseModel):
    batch_id: str
    status: str
    message: str
    status_url: str
    websocket_url: Optional[str] = None


class BulkProgressResponse(BaseModel):
    batch_id: str
    status: str
    total_hospitals: int
    processed_hospitals: int
    failed_hospitals: int
    batch_activated: bool
    hospitals: List[HospitalRowResult] = []
    errors: List[HospitalRowResult] = []
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None