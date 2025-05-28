# conversation/db_connection.py
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import urllib

#----------DB1 設定-----------

username = "manager"
password = "iisi@641001"
encoded_password = urllib.parse.quote(password, safe="")
DATABASE_URL = f"mssql+pyodbc://{username}:{encoded_password}@34.134.75.49:1433/chatbot?driver=ODBC+Driver+17+for+SQL+Server"
Base = declarative_base()
# 建立 SQLAlchemy 引擎，設定連線池參數 (pool_size 與 max_overflow 可依需求調整)
engine = create_engine(DATABASE_URL,pool_size=10, max_overflow=30)
session = scoped_session(sessionmaker(bind=engine))
#----------DB2 設定-----------
#...


@contextmanager
def session_scope():
    try:
        yield session
        session.commit()  # 根據需要，可以在成功時 commit
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.remove()




