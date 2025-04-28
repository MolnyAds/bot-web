import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, conint

class UserOut(BaseModel):
    id: int
    balance: float
    class Config:
        orm_mode = True

class MyStatsOut(BaseModel):
    total_ads: int
    bought_ads: int
    active_orders: int
    cancelled_orders: int
    average_price: float
    ad_type_purchases: Dict[int, int]
    total_sales: int
    total_revenue: float
    sales_last_30_days: int
    revenue_last_30_days: float

class MyGroupsCountOut(BaseModel):
    count: int

class MyGroupOut(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str]
    subject_ids: List[int]
    sales_count: int

    class Config:
        orm_mode = True

class AdInfoIn(BaseModel):
    id: int
    price: float

class GroupEditIn(BaseModel):
    group_id: int
    subjects: List[int]
    country_id: Optional[int] = None
    language_id: Optional[int] = None
    ad_infos: List[AdInfoIn]
    schedule: Dict[conint(ge=1, le=7), List[conint(ge=0, le=23)]]

class CatalogGroupOut(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str]
    subject_ids: List[int]
    min_price: float
    subscribers: int

    class Config:
        orm_mode = True

class GroupIn(BaseModel):
    id: int
    owner_id: int
    username: str
    avg_views: int
    subscribers: int
    avatar_url: Optional[str]
    subjects: Optional[List[int]] = None

class GroupOut(BaseModel):
    id: int
    username: str
    avg_views: int
    subscribers: int
    in_catalog: bool
    owner_id: int
    avatar_url: Optional[str]
    subjects: Optional[List[int]] = None
    class Config:
        orm_mode = True

class AdvertisementTypeOut(BaseModel):
    id: int
    duration_in_hours: conint(ge=1)
    top_duration_in_hours: conint(ge=1)
    pinned: bool
    repost: bool

    class Config:
        orm_mode = True

class SubjectTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class AdvertisementOut(BaseModel):
    id: int
    group_id: int
    ad_type_id: int
    cost: float
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class PlacementOut(BaseModel):
    id: int
    ad_id: int
    buyer_id: int
    placement_date: datetime.datetime
    status_id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True