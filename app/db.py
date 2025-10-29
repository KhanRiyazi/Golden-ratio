import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Text,
    DateTime, func, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from contextlib import contextmanager

# =========================================================
# 1️⃣ Database Path Configuration
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Ensure single shared /data directory (one DB file for all runs)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "affiliate.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# =========================================================
# 2️⃣ SQLAlchemy Engine + Session Setup
# =========================================================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite thread safety
    pool_pre_ping=True,
    echo=False  # Set to True for SQL query debugging
)

# Thread-safe session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()

# =========================================================
# 3️⃣ ORM Models
# =========================================================
class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    url = Column(Text, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship: One link → Many clicks
    clicks = relationship("Click", back_populates="link", cascade="all, delete-orphan")


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id", ondelete="CASCADE"))
    ip = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship: Many clicks → One link
    link = relationship("Link", back_populates="clicks")

# =========================================================
# 4️⃣ Database Initialization and Session Handling
# =========================================================
def init_db():
    """
    Initialize the database — create tables if missing,
    without deleting existing data.
    """
    db_created = not os.path.exists(DB_PATH)
    Base.metadata.create_all(bind=engine)

    if db_created:
        print(f"🆕 New database created at: {DB_PATH}")
    else:
        print(f"✅ Using existing database at: {DB_PATH}")


def get_db():
    """Dependency for FastAPI routes — provides a session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================================================
# 5️⃣ Context Manager (for scripts / testing)
# =========================================================
@contextmanager
def db_session():
    """Manual session context for CLI or background tasks."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        print("❌ Database Error:", e)
        raise
    finally:
        db.close()
