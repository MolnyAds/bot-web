import datetime
import os
from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from telegram_webapp_auth.auth import WebAppUser

from sqlalchemy import asc, create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Table, desc, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session

from auth import get_current_user, verify_bot_token
from database import Base, SessionLocal, engine
from models import Advertisement, AdvertisementType, Country, Group, Language, Placement, Schedule, Status, Subject, User, ads_schedule, groups_subjects
from schemas import AdvertisementOut, AdvertisementTypeOut, CatalogGroupOut, GroupEditIn, GroupIn, GroupOut, MyGroupsCountOut, MyGroupOut, PlacementOut, MyStatsOut, SubjectTypeOut, UserOut

from config.env import TOKEN

import uvicorn


import logging
logger = logging.getLogger("fastapi_logger")
logger.setLevel(logging.INFO)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        initial_data = [
            Status(id='0', name='pending'),
            Status(id='1', name='active'),
            Status(id='2', name='completed'),
            Status(id='3', name='canceled'),
            Language(id='0', name='Russian'),
            Language(id='1', name='English'),
            Country(id='0', name='Russia'),
            Subject(id='0', name='CS 2'),
            Subject(id='1', name='CS GO')
        ]
        for item in initial_data:
            db.merge(item)
        db.commit()

app = FastAPI()

origins = [
    "https://molnyads.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://molnyads.github.io"],  # список разрешённых доменов
    allow_credentials=True,
    allow_methods=["*"],     # разрешённые методы: GET, POST и т.д.
    allow_headers=["*"],     # разрешённые заголовки
)

@app.get("/api/user", dependencies=[Depends(get_current_user)], response_model=UserOut)
def get_user(user: WebAppUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        # Для теста возвращаем фейковый баланс
        db_user = User(id=user.id, balance=1000.0)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    else:
        db_user.balance = 1000.0  # Фейк-баланс всегда 1000
    return db_user

@app.get("/api/my/stats", dependencies=[Depends(get_current_user)], response_model=MyStatsOut)
def get_my_stats(
    db: Session = Depends(get_db),
    current_user: WebAppUser = Depends(get_current_user)
):
    now = datetime.datetime.utcnow()
    thirty_days_ago = now - datetime.timedelta(days=30)

    # 1) Все группы пользователя
    user_group_ids = db.query(Group.id).filter(Group.owner_id == current_user.id).subquery()

    # 2) Все объявления пользователя
    user_ads = db.query(Advertisement).filter(Advertisement.group_id.in_(user_group_ids)).subquery()

    # 3) Все размещения на объявления пользователя
    user_placements = db.query(Placement).join(user_ads, Placement.ad_id == user_ads.c.id)

    # 1) Кол-во размещенных реклам
    total_ads = db.query(func.count()).select_from(user_ads).scalar()

    # 2) Кол-во купленных реклам (завершённые размещения)
    bought_ads = user_placements.filter(Placement.status.has(name="completed")).count()

    # 3) Кол-во активных заказов
    active_orders = user_placements.filter(Placement.status.has(name="active")).count()

    # 4) Кол-во отменённых заказов
    cancelled_orders = user_placements.filter(Placement.status.has(name="cancelled")).count()

    # 5) Средняя цена размещения
    avg_price = db.query(func.avg(Advertisement.cost)).filter(Advertisement.group_id.in_(user_group_ids)).scalar() or 0

    # 6) Кол-во покупок по типам
    type_counts = {}
    types = db.query(AdvertisementType).all()
    for ad_type in types:
        count = user_placements.join(Advertisement).filter(
            Advertisement.ad_type_id == ad_type.id,
            Placement.status.has(name="completed")
        ).count()
        type_counts[ad_type] = count

    # 7) Общая статистика
    total_sales = bought_ads
    total_revenue = db.query(func.sum(Advertisement.cost)).filter(
        Advertisement.group_id.in_(user_group_ids),
        Advertisement.id.in_(user_placements.with_entities(Placement.ad_id).filter(Placement.status.has(name="completed")))
    ).scalar() or 0

    # 8) За последние 30 дней
    recent_sales = user_placements.filter(
        Placement.status.has(name="completed"),
        Placement.created_at >= thirty_days_ago
    ).count()

    recent_revenue = db.query(func.sum(Advertisement.cost)).filter(
        Advertisement.group_id.in_(user_group_ids),
        Advertisement.id.in_(
            user_placements.with_entities(Placement.ad_id).filter(
                Placement.status.has(name="completed"),
                Placement.created_at >= thirty_days_ago
            )
        )
    ).scalar() or 0

    # return MyStatsOut(
    #     total_ads=total_ads,
    #     bought_ads=bought_ads,
    #     active_orders=active_orders,
    #     cancelled_orders=cancelled_orders,
    #     average_price=round(avg_price, 2),
    #     ad_type_purchases=type_counts,
    #     total_sales=total_sales,
    #     total_revenue=round(total_revenue, 2),
    #     sales_last_30_days=recent_sales,
    #     revenue_last_30_days=round(recent_revenue, 2)
    # )
    return MyStatsOut(
        total_ads=1000,
        bought_ads=1,
        active_orders=5,
        cancelled_orders=3,
        average_price=1736.3,
        ad_type_purchases={0: 1, 1: 999},
        total_sales=999,
        total_revenue=513513.3,
        sales_last_30_days=30,
        revenue_last_30_days=13
    )

@app.get("/api/my/groups/count", dependencies=[Depends(get_current_user)], response_model=MyGroupsCountOut)
def get_my_groups_count(
    search: str = Query("", alias="search"),
    subject_ids: List[int] = Query([]),
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    query = db.query(Group).filter(Group.owner_id == user.id)

    if search:
        query = query.filter(Group.username.ilike(f"%{search}%"))

    if subject_ids:
        query = query.join(Group.subjects).filter(Subject.id.in_(subject_ids)).distinct()
    
    response = MyGroupsCountOut(count=query.count())
    return response

@app.get("/api/my/groups", dependencies=[Depends(get_current_user)], response_model=List[MyGroupOut])
def get_my_groups(user: WebAppUser = Depends(get_current_user),
                  db: Session = Depends(get_db),
                  page: int = Query(1, ge=1),
                  limit: int = Query(10, ge=1),
                  search: str = Query("", alias="search"),
                  subject_ids: List[int] = Query(None),
                  sort_by_sales: str = Query("desc", regex="^(asc|desc)$")):
    offset = (page - 1) * limit

    query = db.query(Group).filter(Group.owner_id == user.id)

    if search:
        query = query.filter(Group.username.ilike(f"%{search}%"))

    if subject_ids:
        query = query.join(Group.subjects).filter(Subject.id.in_(subject_ids)).distinct()

    sales_subquery = (
        db.query(
            Advertisement.group_id.label("group_id"),
            func.count(Placement.id).label("sales_count")
        )
        .join(Placement, Placement.ad_id == Advertisement.id)
        .filter(Placement.status.has(name="completed"))
        .group_by(Advertisement.group_id)
        .subquery()
    )

    query = query.outerjoin(sales_subquery, Group.id == sales_subquery.c.group_id)

    sales_column = func.coalesce(sales_subquery.c.sales_count, 0)

    if sort_by_sales == "desc":
        query = query.order_by(sales_column.desc())
    else:
        query = query.order_by(sales_column.asc())

    groups = query.offset(offset).limit(limit).all()

    result = []
    for group in groups:
        subject_ids = [subj.id for subj in group.subjects]
        sales_count = getattr(group, "sales_count", 0) or 0
        result.append(MyGroupOut(
            id=group.id,
            username=group.username,
            avatar_url=group.avatar_url,
            subject_ids=subject_ids,
            sales_count=sales_count
        ))

    return result

@app.post("/my/group/edit", dependencies=[Depends(get_current_user)])
def edit_group(
    data: GroupEditIn,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    # Проверка прав
    group = db.query(Group).filter(Group.id == data.group_id, Group.owner_id == user.id).first()
    if not group:
        raise HTTPException(status_code=403, detail="Group wasn't found or doesn't belong to user.")

    # Обновление тематики
    group.subjects.clear()
    if data.subjects:
        subjects = db.query(Subject).filter(Subject.id.in_(data.subjects)).all()
        group.subjects.extend(subjects)

    # Обновление страны и языка
    group.country_id = data.country_id
    group.language_id = data.language_id

    db.commit()

    # Удаляем старые объявления и связи
    old_ads = db.query(Advertisement).filter(Advertisement.group_id == group.id).all()
    for ad in old_ads:
        db.query(ads_schedule).filter(ads_schedule.c.ad_id == ad.id).delete()
        db.delete(ad)
    db.commit()

    # Проверка расписания
    schedule_cache = {
        (s.day_of_week, s.hour): s.id for s in db.query(Schedule).all()
    }

    for day, hours in data.schedule.items():
        for hour in hours:
            key = (day, hour)
            if key not in schedule_cache:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid (day, hour): {key}"
                )

    # Добавляем объявления и связи
    for ad_info in data.ad_infos:
        if not db.query(AdvertisementType).filter(AdvertisementType.id == ad_info.id).first():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid ad type: {ad_info}"
            )

        ad = Advertisement(
            group_id=group.id,
            ad_type_id=ad_info,
            cost=ad_info.price
        )
        db.add(ad)
        db.flush()

        for day, hours in data.schedule.items():
            for hour in hours:
                schedule_id = schedule_cache[(day, hour)]
                db.execute(ads_schedule.insert().values(ad_id=ad.id, schedule_id=schedule_id))

    db.commit()
    return True


@app.get("/api/catalog", dependencies=[Depends(verify_bot_token)], response_model=List[CatalogGroupOut])
def get_catalog(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = Query(""),
    subject_ids: List[int] = Query(None),
    sort_by: str = Query("price_asc", regex="^(price_asc|price_desc|subs_asc|subs_desc)$"),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    # Базовый запрос: только группы, у которых есть объявления (т.е. что-то продают)
    query = db.query(Group).filter(Group.in_catalog == True)

    if search:
        query = query.filter(Group.username.ilike(f"%{search}%"))

    if subject_ids:
        query = query.join(Group.subjects).filter(Subject.id.in_(subject_ids)).distinct()

    # Подзапрос: минимальная цена объявления в каждой группе
    min_price_subquery = (
        db.query(
            Advertisement.group_id.label("group_id"),
            func.min(Advertisement.cost).label("min_price")
        )
        .group_by(Advertisement.group_id)
        .subquery()
    )

    query = query.join(min_price_subquery, Group.id == min_price_subquery.c.group_id)

    # Сортировка
    if sort_by == "price_asc":
        query = query.order_by(min_price_subquery.c.min_price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(min_price_subquery.c.min_price.desc())
    elif sort_by == "subs_asc":
        query = query.order_by(Group.subscribers.asc())
    elif sort_by == "subs_desc":
        query = query.order_by(Group.subscribers.desc())

    # Пагинация
    query = query.offset(offset).limit(limit)

    groups = query.all()

    result = []
    for group in groups:
        subject_ids = [subj.id for subj in group.subjects]
        min_price = db.query(func.min(Advertisement.cost)).filter(Advertisement.group_id == group.id).scalar() or 0.0

        result.append(CatalogGroupOut(
            id=group.id,
            username=group.username,
            avatar_url=group.avatar_url,
            subject_ids=subject_ids,
            min_price=round(min_price, 2),
            subscribers=group.subscribers
        ))

    return result

@app.post("/api/catalog/add", dependencies=[Depends(verify_bot_token)], response_model=GroupOut)
async def add_group(group: GroupIn, user: WebAppUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group.id).first()
    if db_group:
        db_group.owner_id = group.owner_id
        db_group.username = group.username
        db_group.avg_views = group.avg_views
        db_group.subscribers = group.subscribers
        db_group.avatar_url = group.avatar_url
    else:
        db_group = Group(
            id=group.id,
            owner_id=group.owner_id,
            username=group.username,
            avg_views=group.avg_views,
            subscribers=group.subscribers,
            in_catalog=False,
            avatar_url=group.avatar_url
        )
        db.add(db_group)
        if group.subjects:
            for subject_id in group.subjects:
                subj = db.query(Subject).get(subject_id)
                if subj:
                    db_group.subjects.append(subj)
    db.commit()
    db.refresh(db_group)
    return db_group


@app.delete("/api/groups/{group_id}", dependencies=[Depends(get_current_user)])
def delete_group(group_id: int, user: WebAppUser = Depends(get_current_user), db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id, Group.owner_id == user.id).first()
    if not group:
        raise HTTPException(404, "Канал не найден")
    db.delete(group)
    db.commit()
    return {"ok": True}

@app.post("/api/ads", dependencies=[Depends(get_current_user)], response_model=AdvertisementOut)
def create_ad(group_id: int, ad_type_id: int, cost: float, db: Session = Depends(get_db), user: WebAppUser = Depends(get_current_user)):
    group = db.query(Group).filter(Group.id == group_id, Group.owner_id == user.id).first()
    if not group:
        raise HTTPException(404, "Группа не найдена или не принадлежит вам")
    ad = Advertisement(
        group_id=group_id,
        ad_type_id=ad_type_id,
        cost=cost
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

@app.get("/api/ads",dependencies=[Depends(get_current_user)],  response_model=List[AdvertisementOut])
def list_ads(db: Session = Depends(get_db)):
    return db.query(Advertisement).all()

@app.get("/api/ads/{ad_id}", dependencies=[Depends(get_current_user)], response_model=AdvertisementOut)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(Advertisement).filter(Advertisement.id == ad_id).first()
    if not ad:
        raise HTTPException(404, "Объявление не найдено")
    return ad

@app.delete("/api/ads/{ad_id}", dependencies=[Depends(get_current_user)])
def delete_ad(ad_id: int, user: WebAppUser = Depends(get_current_user), db: Session = Depends(get_db)):
    ad = db.query(Advertisement).join(Group).filter(Advertisement.id == ad_id, Group.owner_id == user.id).first()
    if not ad:
        raise HTTPException(404, "Объявление не найдено или не принадлежит вам")
    db.delete(ad)
    db.commit()
    return {"ok": True}

@app.post("/api/placements", dependencies=[Depends(get_current_user)], response_model=PlacementOut)
def create_placement(ad_id: int, placement_date: datetime.datetime, db: Session = Depends(get_db), user: WebAppUser = Depends(get_current_user)):
    status = db.query(Status).filter(Status.name == "pending").first()
    placement = Placement(
        ad_id=ad_id,
        buyer_id=user.id,
        placement_date=placement_date,
        status_id=status.id
    )
    db.add(placement)
    db.commit()
    db.refresh(placement)
    return placement

@app.get("/api/placements/my", dependencies=[Depends(get_current_user)], response_model=List[PlacementOut])
def my_placements(user: WebAppUser = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Placement).filter(Placement.buyer_id == user.id).all()

@app.delete("/api/placements/{placement_id}", dependencies=[Depends(get_current_user)])
def delete_placement(placement_id: int, user: WebAppUser = Depends(get_current_user), db: Session = Depends(get_db)):
    placement = db.query(Placement).filter(Placement.id == placement_id, Placement.buyer_id == user.id).first()
    if not placement:
        raise HTTPException(404, "Покупка не найдена или не принадлежит вам")
    db.delete(placement)
    db.commit()
    return {"ok": True}

# --- СПРАВОЧНИКИ ---
@app.get("/catalog/count")
def get_catalog_groups_count(
    search: str = Query(""),
    subject_ids: List[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Group).filter(Group.in_catalog == True)

    if search:
        query = query.filter(Group.username.ilike(f"%{search}%"))

    if subject_ids:
        query = query.join(Group.subjects).filter(Subject.id.in_(subject_ids)).distinct()

    # Только группы, у которых есть хотя бы одно объявление
    groups_with_ads = db.query(Advertisement.group_id).distinct().subquery()
    query = query.filter(Group.id.in_(groups_with_ads))

    return {"count": query.count()}

@app.get("/api/tables/ad_types", response_model=List[AdvertisementTypeOut])
def get_ad_types(db: Session = Depends(get_db)):
    return db.query(AdvertisementType).all()

@app.get("/api/tables/languages")
def get_languages(db: Session = Depends(get_db)):
    return db.query(Language).all()

@app.get("/api/tables/countries")
def get_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()

@app.get("/api/tables/subjects", response_model=List[SubjectTypeOut])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()

@app.get("/api/tables/statuses")
def get_statuses(db: Session = Depends(get_db)):
    return db.query(Status).all()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.on_event("startup")
def on_startup():
    init_database()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

