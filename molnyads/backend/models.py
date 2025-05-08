import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base, engine

groups_subjects = Table(
    "groups_subjects", Base.metadata,
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id"), primary_key=True)
)
ads_schedule = Table(
    "advertisements_schedule", Base.metadata,
    Column("ad_id", Integer, ForeignKey("advertisements.id"), primary_key=True),
    Column("schedule_id", Integer, ForeignKey("schedule.id"), primary_key=True)
)

groups_schedule = Table(
    "groups_schedule", Base.metadata,
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True),
    Column("schedule_id", Integer, ForeignKey("schedule.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    balance = Column(Float, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    username = Column(String, nullable=False)
    avg_views = Column(Integer, nullable=False)
    subscribers = Column(Integer, nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"))
    language_id = Column(Integer, ForeignKey("languages.id"))
    in_catalog = Column(Boolean, default=True, nullable=False)
    avatar_url = Column(String, nullable=True)

    owner = relationship("User")
    subjects = relationship("Subject", secondary=groups_subjects, back_populates="groups")
    schedules = relationship("Schedule", secondary=groups_schedule, backref="groups")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    groups = relationship("Group", secondary=groups_subjects, back_populates="subjects")

class AdvertisementType(Base):
    __tablename__ = "advertisement_types"
    id = Column(Integer, primary_key=True)
    duration_in_hours = Column(Integer, nullable=False)
    top_duration_in_hours = Column(Integer)
    pinned = Column(Boolean, nullable=False)
    repost = Column(Boolean, nullable=False)

class Advertisement(Base):
    __tablename__ = "advertisements"
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    ad_type_id = Column(Integer, ForeignKey("advertisement_types.id"), nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    group = relationship("Group")
    ad_type = relationship("AdvertisementType")

class Country(Base):
    __tablename__ = "countries"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship("User")

class Status(Base):
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Placement(Base):
    __tablename__ = "placements"
    id = Column(Integer, primary_key=True)
    ad_id = Column(Integer, ForeignKey("advertisements.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    placement_date = Column(DateTime, nullable=False)
    message_id = Column(Integer, nullable=False)
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ad = relationship("Advertisement")
    buyer = relationship("User")
    status = relationship("Status")

class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True)
    day_of_week = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
