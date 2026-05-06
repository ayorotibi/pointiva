from pydantic import BaseModel
from typing import List
from typing import Optional

class UploadCreateResponse(BaseModel):
    id: int
    status: str
    filename: str

class UploadStatusResponse(BaseModel):
    id: int
    status: str
    submitted: str
    message: Optional[str] = None


class Wallet(BaseModel):
    available_points: int
    pending_points: int
    lifetime_earnings: int

class Upload(BaseModel):
    id: int
    status: str
    submitted: str
    filename: str
    metadata: dict = {}   # default value


class FeaturedMoment(BaseModel):
    id: int
    title: str
    creator: str
    location: str

class DashboardResponse(BaseModel):
    user: dict
    wallet: Wallet
    uploads: List[Upload]
    featured: List[FeaturedMoment]


