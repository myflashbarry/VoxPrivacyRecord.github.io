"""Database models and operations."""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

# SQLite database URL
DATABASE_URL = f"sqlite:///{settings.db_path}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    """User table to track participants."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to recordings
    recordings = relationship("Recording", back_populates="user")


class Recording(Base):
    """Recording table to track all audio submissions."""
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), nullable=False, index=True)
    language = Column(String, nullable=False)  # "zh" or "en"
    task_type = Column(String, nullable=False)  # "pair" or "extra_question"
    role = Column(String, nullable=False)  # "secret" or "question"
    item_id = Column(String, nullable=False, index=True)  # ID from JSONL
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="recordings")


def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_progress(db, username: str) -> dict:
    """Calculate user's progress from recordings."""
    recordings = db.query(Recording).filter(Recording.username == username).all()
    
    # Track pairs (need both secret and question for same item)
    zh_pairs = {}
    en_pairs = {}
    zh_extra = set()
    en_extra = set()
    
    for rec in recordings:
        if rec.task_type == "pair":
            if rec.language == "zh":
                if rec.item_id not in zh_pairs:
                    zh_pairs[rec.item_id] = {"secret": False, "question": False}
                zh_pairs[rec.item_id][rec.role] = True
            elif rec.language == "en":
                if rec.item_id not in en_pairs:
                    en_pairs[rec.item_id] = {"secret": False, "question": False}
                en_pairs[rec.item_id][rec.role] = True
        elif rec.task_type == "extra_question":
            if rec.language == "zh":
                zh_extra.add(rec.item_id)
            elif rec.language == "en":
                en_extra.add(rec.item_id)
    
    # Count completed pairs (both secret and question done)
    zh_pairs_done = sum(1 for p in zh_pairs.values() if p["secret"] and p["question"])
    en_pairs_done = sum(1 for p in en_pairs.values() if p["secret"] and p["question"])
    
    return {
        "zh_pairs_done": zh_pairs_done,
        "en_pairs_done": en_pairs_done,
        "zh_extra_questions_done": len(zh_extra),
        "en_extra_questions_done": len(en_extra),
        # Also return incomplete pairs info for task manager
        "_zh_pairs_dict": zh_pairs,
        "_en_pairs_dict": en_pairs,
        "_zh_extra_items": zh_extra,
        "_en_extra_items": en_extra
    }


def get_user_recorded_items(db, username: str, language: str, task_type: str) -> set:
    """Get set of item IDs already recorded by user for given language/task_type."""
    recordings = db.query(Recording).filter(
        Recording.username == username,
        Recording.language == language,
        Recording.task_type == task_type
    ).all()
    return {rec.item_id for rec in recordings}

