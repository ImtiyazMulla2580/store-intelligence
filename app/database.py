from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./store_intelligence.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EventDB(Base):
    __tablename__ = "events"

    event_id     = Column(String, primary_key=True)
    store_id     = Column(String, index=True)
    camera_id    = Column(String)
    visitor_id   = Column(String, index=True)
    event_type   = Column(String, index=True)
    timestamp    = Column(DateTime, index=True)
    zone_id      = Column(String, nullable=True)
    dwell_ms     = Column(Integer, default=0)
    is_staff     = Column(Boolean, default=False)
    confidence   = Column(Float, default=1.0)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()