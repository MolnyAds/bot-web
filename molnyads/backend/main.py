import datetime
import os
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from telegram_webapp_auth.auth import WebAppUser

from sqlalchemy import asc, create_engine, Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Table, desc, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session

from auth import get_current_user, verify_bot_token
from database import Base, SessionLocal, engine
from models import Advertisement, AdvertisementType, Country, Group, Language, Placement, Schedule, Status, Subject, Transaction, User, ads_schedule, groups_subjects, groups_schedule
from schemas import AdvertisementTypeOut, BalanceOut, BotAdTaskOut, BotGroupUpdateIn, CountryTypeOut, DepositIn, EditGroupRequest, LanguagesTypeOut, MyGroupInfo, MyGroupsCountOut, MyPurchaseOut, MyPurchasesCountOut, OtherGroupInfo, MyStatsOut, SchedulesTypeOut, SetInCatalogRequest, StatusesTypeOut, SubjectTypeOut, TransactionOut, UpdateScheduleRequest

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

app = FastAPI()

origins = [
    "https://molnyads.github.io",
    "https://molnyads.tech"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ОСНОВНЫЕ ЭНДПОИНТЫ ---

@app.get("/api/user", dependencies=[Depends(get_current_user)])
def init_user(db: Session = Depends(get_db),
              user: WebAppUser = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        db_user = User(id=user.id, balance=1)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return True

@app.get("/api/my/balance", dependencies=[Depends(get_current_user)], response_model=BalanceOut)
def get_my_balance(
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return BalanceOut(balance=db_user.balance)

@app.post("/api/my/balance/deposit", dependencies=[Depends(get_current_user)])
def deposit_balance(
    data: DepositIn,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    db_user = db.query(User).filter(User.id == user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Пополняем баланс
    db_user.balance += data.amount

    # Добавляем транзакцию
    new_transaction = Transaction(
        user_id=user.id,
        amount=data.amount
    )
    db.add(new_transaction)
    db.commit()

    return BalanceOut(balance=db_user.balance)

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
        type_counts[ad_type.id] = count

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

    return MyStatsOut(
        total_ads=total_ads,
        bought_ads=bought_ads,
        active_orders=active_orders,
        cancelled_orders=cancelled_orders,
        average_price=round(avg_price, 2),
        ad_type_purchases=type_counts,
        total_sales=total_sales,
        total_revenue=round(total_revenue, 2),
        sales_last_30_days=recent_sales,
        revenue_last_30_days=round(recent_revenue, 2)
    )

@app.get("/api/my/purchases/count", response_model=MyPurchasesCountOut)
def get_my_purchases_count(
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user),
    status: Optional[List[str]] = Query(None)
):
    query = (
        db.query(func.count(Placement.id))
        .join(Placement.status)
        .filter(Placement.buyer_id == user.id)
    )

    if status:
        query = query.filter(Status.name.in_(status))

    return MyPurchasesCountOut(count=query.scalar())

@app.get("/api/my/purchases", response_model=List[MyPurchaseOut])
def get_my_purchases(
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort_by: str = Query("time_desc", regex="^(time_asc|time_desc)$"),
    status: Optional[List[str]] = Query(None)
):
    offset = (page - 1) * limit

    query = (
        db.query(Placement)
        .join(Placement.status)
        .join(Placement.ad)
        .join(Advertisement.group)
        .filter(Placement.buyer_id == user.id)
    )

    if status:
        query = query.filter(Status.name.in_(status))

    if sort_by == "time_asc":
        query = query.order_by(Placement.created_at.asc())
    else:
        query = query.order_by(Placement.created_at.desc())

    placements = query.offset(offset).limit(limit).all()

    # Получаем слоты из ads_schedule
    result = []
    for placement in placements:
        ad = placement.ad
        group = ad.group
        row = db.query(ads_schedule.c.schedule_id).filter(
            ads_schedule.c.ad_id == ad.id
        ).first()
        schedule_id = row[0] if row else None

        result.append(MyPurchaseOut(
            id=placement.id,
            group_id=group.id,
            group_username=group.username,
            ad_type_id=ad.ad_type_id,
            ad_cost=ad.cost,
            placement_date=placement.placement_date,
            status=placement.status.name,
            schedule=schedule_id
        ))

    return result

@app.get("/api/my/purchases/{placement_id}", response_model=MyPurchaseOut)
def get_my_purchase_detail(
    placement_id: int,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    placement = (
        db.query(Placement)
        .join(Placement.ad)
        .join(Advertisement.group)
        .join(Placement.status)
        .filter(Placement.id == placement_id, Placement.buyer_id == user.id)
        .first()
    )

    if not placement:
        raise HTTPException(status_code=404, detail="Покупка не найдена или не принадлежит пользователю")

    ad = placement.ad
    group = ad.group

    # Получаем один слот (если он есть)
    schedule = (
        db.query(Schedule)
        .join(ads_schedule, ads_schedule.c.schedule_id == Schedule.id)
        .filter(ads_schedule.c.ad_id == ad.id)
        .first()
    )

    return MyPurchaseOut(
        id=placement.id,
        group_id=group.id,
        group_username=group.username,
        ad_type_id=ad.ad_type_id,
        ad_cost=ad.cost,
        placement_date=placement.placement_date,
        status=placement.status.name,
        schedule=schedule.id
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

@app.get("/api/my/groups", dependencies=[Depends(get_current_user)], response_model=List[MyGroupInfo])
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
        result.append(MyGroupInfo(
            id=group.id,
            username=group.username,
            avatar_url=group.avatar_url,
            subject_ids=subject_ids,
            subscribers=group.subscribers,
            avg_views=group.avg_views,
            country_id=group.country_id,
            language_id=group.language_id,
            sales_count=sales_count,
            in_catalog=group.in_catalog
        ))

    return result

@app.get("/api/my/group/{group_id}", response_model=MyGroupInfo)
def get_my_group_info(
    group_id: int,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    group = db.query(Group).filter(Group.id == group_id, Group.owner_id == user.id).first()
    if not group:
        raise HTTPException(403, "Группа не найдена или не принадлежит вам")

    ads = db.query(Advertisement).filter(Advertisement.group_id == group.id).all()

    ad_ids = [ad.id for ad in ads]

    schedule_ids = db.query(ads_schedule.c.schedule_id).filter(ads_schedule.c.ad_id.in_(ad_ids)).distinct()
    busy_schedule_ids = (
        db.query(ads_schedule.c.schedule_id)
        .join(Placement, Placement.ad_id == ads_schedule.c.ad_id)
        .filter(
            ads_schedule.c.ad_id.in_(ad_ids),
            Placement.status.has(name="completed")
        )
        .distinct()
        .all()
    )
    subject_ids = [s.id for s in group.subjects]
    ad_prices = {ad.id: ad.cost for ad in ads}

    sales_count = (
        db.query(func.count(Placement.id))
        .join(Advertisement, Advertisement.id == Placement.ad_id)
        .join(Status, Status.id == Placement.status_id)
        .filter(Advertisement.group_id == group_id)
        .filter(Status.name == "completed")
        .scalar()
    )

    return MyGroupInfo(
        id=group.id,
        username=group.username,
        avatar_url=group.avatar_url,
        subject_ids=subject_ids,
        subscribers=group.subscribers,
        avg_views=group.avg_views,
        country_id=group.country_id,
        language_id=group.language_id,
        ad_prices=ad_prices,
        all_slots_ids=schedule_ids,
        busy_slots_ids=busy_schedule_ids,
        sales_count=sales_count,
        in_catalog=group.in_catalog
    )

@app.get("/api/group/{group_id}", dependencies=[Depends(get_current_user)], response_model=OtherGroupInfo)
def get_group_info(
    group_id: int,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(404, "Канал не найден")

    if group.owner_id == user.id:
        return RedirectResponse(url=f"/api/my/group/{group_id}", status_code=307)

    subject_ids = [s.id for s in group.subjects]

    # Рекламные объявления и типы
    ads = db.query(Advertisement).filter(Advertisement.group_id == group.id).all()
    ad_prices = {ad.id: ad.cost for ad in ads}

    # Все расписания, привязанные к объявлениям (ads_schedule)
    ad_ids = [ad.id for ad in ads]
    schedule_ids = [
        row[0] for row in db.query(ads_schedule.c.schedule_id)
        .filter(ads_schedule.c.ad_id.in_(ad_ids))
        .distinct()
        .all()
    ]

    busy_schedule_ids = [
        row[0] for row in db.query(ads_schedule.c.schedule_id)
        .join(Placement, Placement.ad_id == ads_schedule.c.ad_id)
        .filter(
            ads_schedule.c.ad_id.in_(ad_ids),
            Placement.status.has(name="completed")
        )
        .distinct()
        .all()
    ]
    return OtherGroupInfo(
        id=group.id,
        username=group.username,
        subject_ids=subject_ids,
        subscribers=group.subscribers,
        avg_views=group.avg_views,
        country_id=group.country_id,
        language_id=group.language_id,
        ad_prices=ad_prices,
        all_slots_ids=schedule_ids,
        busy_slots_ids=busy_schedule_ids
    )

@app.post("/group/{group_id}/edit", dependencies=[Depends(get_current_user)])
def edit_group(
    group_id: int,
    data: EditGroupRequest,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    group = db.query(Group).filter(Group.id == group_id, Group.owner_id == user.id).first()
    if not group:
        raise HTTPException(403, "Группа не найдена или не принадлежит пользователю")

    # Тематики
    group.subjects.clear()
    if data.subject_ids:
        subjects = db.query(Subject).filter(Subject.id.in_(data.subject_ids)).all()
        group.subjects.extend(subjects)

    # Страна и язык
    group.country_id = data.country_id
    group.language_id = data.language_id

    # Обновление цен на объявления
    for ad_id, price in data.ad_prices.items():
        ad = db.query(Advertisement).filter(
            Advertisement.ad_type_id == ad_id,
            Advertisement.group_id == group.id
        ).first()
        if ad:
            ad.cost = price

    db.commit()
    return True

@app.post("/api/my/group/{group_id}/schedule", dependencies=[Depends(get_current_user)])
def update_group_schedule(
    group_id: int,
    data: UpdateScheduleRequest,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    # Проверка владельца
    group = db.query(Group).filter(Group.id == group_id, Group.owner_id == user.id).first()
    if not group:
        raise HTTPException(403, "Группа не найдена или не принадлежит пользователю")

    # Получаем объявления группы
    ads = db.query(Advertisement).filter(Advertisement.group_id == group.id).all()
    ad_ids = [ad.id for ad in ads]
    if not ad_ids:
        raise HTTPException(400, "У группы нет объявлений")

    # Проверяем, что все schedule_id существуют
    existing_ids = set(r[0] for r in db.query(Schedule.id).filter(Schedule.id.in_(data.schedule_ids)).all())
    missing_ids = set(data.schedule_ids) - existing_ids
    if missing_ids:
        raise HTTPException(400, f"Неверные ID расписаний: {list(missing_ids)}")

    # Удаляем старые слоты
    db.query(ads_schedule).filter(ads_schedule.c.ad_id.in_(ad_ids)).delete(synchronize_session=False)

    # Добавляем новые слоты
    values = []
    for ad_id in ad_ids:
        for schedule_id in data.schedule_ids:
            values.append({"ad_id": ad_id, "schedule_id": schedule_id})

    if values:
        db.execute(ads_schedule.insert().values(values))

    db.commit()
    return True

@app.post("/api/my/group/{group_id}/set_in_catalog", dependencies=[Depends(get_current_user)])
def set_group_in_catalog(
    group_id: int,
    data: SetInCatalogRequest,
    db: Session = Depends(get_db),
    user: WebAppUser = Depends(get_current_user)
):
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.owner_id == user.id
    ).first()

    if not group:
        raise HTTPException(status_code=403, detail="Группа не найдена или не принадлежит пользователю")

    group.in_catalog = data.in_catalog
    db.commit()
    return True

@app.get(
    "/api/my/transactions",
    dependencies=[Depends(get_current_user)],
    response_model=List[TransactionOut]
)
def get_my_transactions(
    limit: int = Query(30, ge=1),
    current_user: WebAppUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Transaction)
            .filter(Transaction.user_id == current_user.id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
    )

@app.get("/api/catalog/count")
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

@app.get("/api/catalog", dependencies=[Depends(get_current_user)], response_model=List[OtherGroupInfo])
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

        result.append(OtherGroupInfo(
            id=group.id,
            username=group.username,
            avatar_url=group.avatar_url,
            subject_ids=subject_ids,
            subscribers=group.subscribers,
            avg_views=group.avg_views,
            min_price=round(min_price, 2)
        ))

    return result

# --- БОТ ---
@app.post("/api/bot/group_update", dependencies=[Depends(verify_bot_token)])
def bot_group_update(
    data: BotGroupUpdateIn,
    db: Session = Depends(get_db),
):
    group = db.query(Group).filter(Group.id == data.id).first()
    if data.event == "added" and not group:
        group = Group(id=data.id,
                        owner_id=data.owner_id,
                        username=data.username,
                        avg_views=data.avg_views,
                        subscribers=data.subscribers,
                        in_catalog=False)
        db.add(group)
    elif data.event == "updated" and group:
        group.id = data.id
        group.owner_id = data.owner_id
        group.username = data.username
        group.avg_views = data.avg_views
        group.subscribers = data.subscribers
    elif data.event == "removed":
        if group:
            db.delete(group)
    db.commit()
    return True

@app.get("/api/bot/ad_tasks", dependencies=[Depends(verify_bot_token)])
def get_ad_tasks(
    db: Session = Depends(get_db)
):
    now = datetime.datetime.utcnow()
    placements = db.query(Placement).join(Advertisement).filter(
        Placement.status.has(name="pending"),
        Placement.placement_date <= now
    ).all()
    result = []
    for placement in placements:
        ad = placement.ad
        result.append(BotAdTaskOut(
            group_id=ad.group_id,
            message_id=placement.message_id
        ))
    return result

# --- СПРАВОЧНИКИ ---
@app.get("/api/tables/ad_types", response_model=List[AdvertisementTypeOut])
def get_ad_types(db: Session = Depends(get_db)):
    return db.query(AdvertisementType).all()

@app.get("/api/tables/languages", response_model=List[LanguagesTypeOut])
def get_languages(db: Session = Depends(get_db)):
    return db.query(Language).all()

@app.get("/api/tables/countries", response_model=List[CountryTypeOut])
def get_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()

@app.get("/api/tables/subjects", response_model=List[SubjectTypeOut])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()

@app.get("/api/tables/statuses", response_model=List[StatusesTypeOut])
def get_statuses(db: Session = Depends(get_db)):
    return db.query(Status).all()

@app.get("/api/tables/schedules", response_model=List[SchedulesTypeOut])
def get_schedules(db: Session = Depends(get_db)):
    return db.query(Schedule).all()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

