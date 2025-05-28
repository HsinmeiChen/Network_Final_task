# models/conversation.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, SmallInteger, Unicode
from ..db_connection import Base, session_scope
from datetime import datetime
from ..thread_executor import executor

class Conversation(Base):
    __tablename__ = 'CONVERSATION'
    
    # 加入一個 ID 欄位作為主鍵
    ID = Column(Integer, primary_key=True, autoincrement=True)
    CURRENT_STEP = Column(SmallInteger, nullable=False)
    CURRENT_GUIDE = Column(String(10), nullable=False)
    USER_ID = Column(String(20), nullable=False)
    USER_MESSAGE = Column(Unicode(200), nullable=False)
    TIMESTAMP = Column(DateTime, nullable=False)
    GPT_ANSWER_VALIDATOR_REPLY = Column(Boolean, nullable=True)
    FAIL_COUNT = Column(SmallInteger, nullable=True)
    GPT_ANSWER_FEEDBACK = Column(Unicode(255), nullable=True)
    GPT_FEEDBACK = Column(Unicode(255), nullable=True)
    
    def __repr__(self):
        return f"<Conversation(ID={self.ID}, USER_ID={self.USER_ID}, TIMESTAMP={self.TIMESTAMP})>"
    
    @classmethod
    def insert_conversation(cls, current_step, current_guide, user_id, user_message,
                            timestamp=None, gpt_answer_validator_reply=None,
                            fail_count=None, gpt_answer_feedback=None, gpt_feedback=None):
        """
        將一筆對話資料寫入 CONVERSATION 資料表。
        """
        try:
            if timestamp is None:
                timestamp = datetime.now()
            
            conversation = cls(
                CURRENT_STEP=current_step,
                CURRENT_GUIDE=current_guide,
                USER_ID=user_id,
                USER_MESSAGE=user_message,
                TIMESTAMP=timestamp,
                GPT_ANSWER_VALIDATOR_REPLY=gpt_answer_validator_reply,
                FAIL_COUNT=fail_count,
                GPT_ANSWER_FEEDBACK=gpt_answer_feedback,
                GPT_FEEDBACK=gpt_feedback
            )
            
            with session_scope() as session:
                session.add(conversation)
            
            print(f"Conversation for user {user_id} added successfully.")
            return conversation
        except Exception as err:
            print(f"Error inserting conversation: {err}")
            raise
    
    @classmethod
    def async_insert_conversation(cls, current_step, current_guide, user_id, user_message,
                                  timestamp=None, gpt_answer_validator_reply=None,
                                  fail_count=None, gpt_answer_feedback=None, gpt_feedback=None):
        """
        非同步將一筆對話資料寫入資料庫，利用 ThreadPoolExecutor 提交任務執行。
        參數與 insert_conversation 相同。
        """
        future = executor.submit(
            cls.insert_conversation,
            current_step,
            current_guide,
            user_id,
            user_message,
            timestamp,
            gpt_answer_validator_reply,
            fail_count,
            gpt_answer_feedback,
            gpt_feedback
        )
        return future
    
    @classmethod
    def get_conversations_by_user_id(cls, user_id):
        """
        根據用戶ID獲取所有對話記錄。
        """
        try:
            with session_scope() as session:
                conversations = session.query(cls).filter_by(USER_ID=user_id).all()
            return conversations
        except Exception as err:
            print(f"Error retrieving conversations: {err}")
            return []
    
    @classmethod
    def get_latest_conversation(cls, user_id):
        """
        獲取用戶最新的一筆對話記錄。
        """
        try:
            with session_scope() as session:
                conversation = session.query(cls).filter_by(USER_ID=user_id).order_by(cls.TIMESTAMP.desc()).first()
            return conversation
        except Exception as err:
            print(f"Error retrieving latest conversation: {err}")
            return None
