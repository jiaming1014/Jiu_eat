"""資料庫連線設定"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 從環境變數讀取資料庫連線字串，預設為 MSSQL（Windows 整合驗證）
DATABASE_URL = os.getenv("DATABASE_URL", "mssql+pyodbc://@localhost:1433/jiu_eat_1.2?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes")

# SQLite 需要 check_same_thread=False，其他資料庫不需要
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# 建立資料庫引擎
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# 建立 Session 工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 模型的基礎類別
Base = declarative_base()


def get_db():
    """FastAPI 依賴注入用：提供資料庫 Session，請求結束後自動關閉"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
