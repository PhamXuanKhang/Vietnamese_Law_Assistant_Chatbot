from .models import Base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import inspect
from dotenv import load_dotenv
import os

load_dotenv(".env")
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

# Tạo connection string để kết nối với MySQL
connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8mb4"
engine = create_engine(connection_string, echo=False)

SessionLocal = sessionmaker(bind=engine)

# Hàm tạo kết nối với database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hàm tạo các bảng nếu chưa tồn tại
def create_tables(engine):
    inspector = inspect(engine)

    existing_tables = inspector.get_table_names()
    all_tables = Base.metadata.tables.keys()
    missing_tables = [table for table in all_tables if table not in existing_tables]

    if missing_tables:
        print(f"Tạo các bảng chưa tồn tại: {missing_tables}")
        Base.metadata.create_all(engine)
    else:
        print("Tất cả các bảng đã tồn tại.")