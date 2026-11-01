from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

Base = declarative_base()

# Primary Engine (Read/Write for Backend Services and ETL)
engine = create_engine(
    settings.get_database_url(),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Read-Only Engine (Strict SELECT-only for GenAI AI Assistant)
readonly_engine = create_engine(
    settings.get_readonly_database_url(),
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    execution_options={"isolation_level": "AUTOCOMMIT"}
)

ReadonlySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=readonly_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_readonly_db():
    db = ReadonlySessionLocal()
    try:
        yield db
    finally:
        db.close()
