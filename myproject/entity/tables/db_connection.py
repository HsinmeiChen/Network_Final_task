# conversation/db_connection.py
from sqlalchemy import create_engine
import pyodbc
# 請根據 GCP Cloud SQL SQL Server 的連線字串進行設定
DATABASE_URL = "mssql+pyodbc://student:IMstudent123@34.55.151.218:1433/chatbot?driver=ODBC+Driver+17+for+SQL+Server"

# 建立 SQLAlchemy 引擎，設定連線池參數 (pool_size 與 max_overflow 可依需求調整)
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=30)
