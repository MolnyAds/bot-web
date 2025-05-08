import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, confloat, conint

class BalanceOut(BaseModel):
    balance: float

class DepositIn(BaseModel):
    amount: confloat(gt=0)

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

class MyPurchasesCountOut(BaseModel):
    count: int

class MyPurchaseOut(BaseModel):
    id: int
    group_id: int
    group_username: str
    ad_type_id: int
    ad_cost: float
    placement_date: datetime.datetime
    status: str
    schedule: int

class MyGroupsCountOut(BaseModel):
    count: int

class OtherGroupInfo(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    subject_ids: List[int]
    subscribers: int
    avg_views: int
    country_id: Optional[int] = None
    language_id: Optional[int] = None
    ad_prices: Optional[Dict[int, float]] = None
    all_slots_ids: Optional[List[int]] = None
    busy_slots_ids: Optional[List[int]] = None

class MyGroupInfo(OtherGroupInfo):
    sales_count: int
    in_catalog: int

class EditGroupRequest(BaseModel):
    subject_ids: List[int]
    country_id: Optional[int]
    language_id: Optional[int]
    ad_prices: Dict[int, float]

class UpdateScheduleRequest(BaseModel):
    schedule_ids: List[int]

class SetInCatalogRequest(BaseModel):
    in_catalog: bool

class TransactionOut(BaseModel):
    id: int
    amount: float
    created_at: datetime.datetime

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

class CountryTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class SubjectTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class StatusesTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class LanguagesTypeOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class SchedulesTypeOut(BaseModel):
    id: int
    day_of_week: conint(ge=1, le=7)
    hour: conint(ge=0, le=23)

    class Config:
        orm_mode = True

class BotGroupUpdateIn(BaseModel):
    id: int
    owner_id: int
    username: str
    avg_views: int
    subscribers: int
    avatar_url: str

    event: str  # 'added', 'removed', 'updated'

class BotAdTaskOut(BaseModel):
    group_id: int
    message_id: int