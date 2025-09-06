# SQLAlchemy setup for Azure SQL Database
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Replace with your Azure SQL connection string
#DATABASE_URL = os.getenv("AZURE_SQL_CONNECTION_STRING", "mssql+pyodbc://username:password@server:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server")
DATABASE_URL = os.getenv("SQLITE_DB_URL", "sqlite:///./test.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class StockSignal(Base):
    __tablename__ = "stock_signals"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    buy_signal = Column(Integer)
    sell_signal = Column(Integer)
    hold_signal = Column(Integer)  # 1 if hold, 0 otherwise
    confidence = Column(Float)
    timestamp = Column(DateTime)
    current_price = Column(Float)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)

# To create tables: Base.metadata.create_all(bind=engine)
