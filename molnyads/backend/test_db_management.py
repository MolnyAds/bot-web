import datetime
from sqlalchemy import create_engine
from database import Base
from models import Advertisement, AdvertisementType, Country, Group, Language, Placement, Schedule, Status, Subject, Transaction, User, ads_schedule
from config.env import DATABASE_URL
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        # Статусы
        statuses = [
            Status(id=0, name="pending"),
            Status(id=1, name="active"),
            Status(id=2, name="completed"),
            Status(id=3, name="canceled"),
        ]

        # Языки и страны
        languages = [Language(id=0, name="Russian"), Language(id=1, name="English")]
        countries = [Country(id=0, name="Russia")]

        # Тематики
        subjects = [Subject(id=0, name="CS 2"), Subject(id=1, name="CS GO")]

        db.add_all(statuses + languages + countries + subjects)

        # Пользователи
        user1 = User(id=1, balance=1000)
        user2 = User(id=2, balance=500)
        db.add_all([user1, user2])

        # Группа
        group1 = Group(
            id=1,
            owner_id=1,
            username="test_channel",
            avg_views=5000,
            subscribers=15000,
            country_id=0,
            language_id=1,
            in_catalog=True,
            subjects=subjects
        )
        group2 = Group(
            id=2,
            owner_id=1271744188,
            username="канаальчик lokerp",
            avg_views=5000,
            subscribers=1000,
            country_id=0,
            language_id=1,
            in_catalog=True,
            subjects=subjects
        )
        group3 = Group(
            id=3,
            owner_id=470208396,
            username="канаальчик snorovkaaa",
            avg_views=1000,
            subscribers=1066600,
            country_id=0,
            language_id=1,
            in_catalog=True,
            subjects=subjects
        )

        db.add_all([group1, group2, group3])

        # Типы рекламы
        type1 = AdvertisementType(id=1, duration_in_hours=24, top_duration_in_hours=1, pinned=False, repost=False)
        type2 = AdvertisementType(id=2, duration_in_hours=48, top_duration_in_hours=3, pinned=True, repost=False)
        db.add_all([type1, type2])

        # Объявления
        ad1 = Advertisement(id=1001, group_id=1, ad_type=type1, cost=10.0)
        ad2 = Advertisement(id=1002, group_id=1, ad_type=type2, cost=2050.0)
        ad3 = Advertisement(id=1003, group_id=2, ad_type=type1, cost=12120.0)
        ad4 = Advertisement(id=1004, group_id=3, ad_type=type2, cost=70520.0)
        db.add_all([ad1, ad2, ad3, ad4])

        # Расписание
        schedules = [
            Schedule(day_of_week=day, hour=hour)
            for day in range(1, 8)  # 1 to 7
            for hour in range(0, 24)  # 0 to 23
        ]
        db.add_all(schedules)

        # Привязка объявлений к слотам
        db.execute(ads_schedule.insert().values([
            {"ad_id": ad1.id, "schedule_id": 5},
            {"ad_id": ad1.id, "schedule_id": 6},
            {"ad_id": ad2.id, "schedule_id": 7}
        ]))

        # Размещение (реклама куплена)
        placement1 = Placement(
            ad_id=ad1.id,
            buyer_id=1271744188,
            message_id=111111,
            placement_date=datetime.datetime.utcnow(),
            status_id=2  # completed
        )
        placement2 = Placement(
            ad_id=ad1.id,
            buyer_id=470208396,
            message_id=222222,
            placement_date=datetime.datetime.utcnow(),
            status_id=2  # completed
        )
        db.add_all([placement1, placement2])

        # Транзакция
        tx = Transaction(user_id=1, amount=300, created_at=datetime.datetime.utcnow())
        db.add(tx)

        db.commit()

if __name__ == "__main__":
    reset_database()