# conversation/schema.py
from sqlalchemy import text
from .db_connection import engine
from datetime import datetime
from .thread_executor import executor

def create_conversation_table():
    """
    檢查並建立 CONVERSATION 資料表 (適用於 SQL Server)
    更新：
      - 將原本的 USER_NAME 欄位改為 USER_ID VARCHAR(20)
      - 新增 FAIL_COUNT, GPT_ANSWER_FEEDBACK, GPT_FEEDBACK 三個欄位
    """
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CONVERSATION')
    BEGIN
        CREATE TABLE CONVERSATION (
            CURRENT_STEP SMALLINT,
            CURRENT_GUIDE NVARCHAR(10),
            USER_ID VARCHAR(20),
            USER_MESSAGE NVARCHAR(MAX),
            TIMESTAMP DATETIME,
            GPT_ANSWER_VALIDATOR_REPLY BIT NULL,
            FAIL_COUNT SMALLINT,
            GPT_ANSWER_FEEDBACK NVARCHAR(255),
            GPT_FEEDBACK NVARCHAR(255)
        )
    END
    """
    with engine.begin() as conn:
        conn.execute(text(create_table_sql))


def sql_insert_conversation(current_step, current_guide, user_id, user_message,
                            timestamp=None, gpt_answer_validator_reply=None,
                            fail_count=None, gpt_answer_feedback=None, gpt_feedback=None):
    """
    將一筆對話資料寫入 CONVERSATION 資料表

    參數:
        current_step: 小整數 (CURRENT_STEP)
        current_guide: 長度固定 10 的字串 (CURRENT_GUIDE)
        user_id: 長度固定 20 的字串 (USER_ID)
        user_message: 文字訊息 (USER_MESSAGE)
        timestamp: 日期時間，若未提供則使用目前時間 (TIMESTAMP)
        gpt_answer_validator_reply: 布林值，表示 GPT 答案驗證結果 (GPT_ANSWER_VALIDATOR_REPLY)
        fail_count: 小整數 (FAIL_COUNT)
        gpt_answer_feedback: 文字訊息，最大 255 字元 (GPT_ANSWER_FEEDBACK)
        gpt_feedback: 文字訊息，最大 255 字元 (GPT_FEEDBACK)
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(timestamp, datetime):
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    insert_sql = text("""
    INSERT INTO CONVERSATION (
        CURRENT_STEP, 
        CURRENT_GUIDE, 
        USER_ID, 
        USER_MESSAGE, 
        TIMESTAMP, 
        GPT_ANSWER_VALIDATOR_REPLY,
        FAIL_COUNT,
        GPT_ANSWER_FEEDBACK,
        GPT_FEEDBACK
    )
    VALUES (
        :current_step, 
        :current_guide, 
        :user_id, 
        :user_message, 
        :timestamp, 
        :gpt_answer_validator_reply,
        :fail_count,
        :gpt_answer_feedback,
        :gpt_feedback
    )
    """)
    
    with engine.begin() as conn:
        conn.execute(insert_sql, {
            'current_step': current_step,
            'current_guide': current_guide,
            'user_id': user_id,
            'user_message': user_message,
            'timestamp': timestamp,
            'gpt_answer_validator_reply': gpt_answer_validator_reply,
            'fail_count': fail_count,
            'gpt_answer_feedback': gpt_answer_feedback,
            'gpt_feedback': gpt_feedback
        })


def async_sql_insert_conversation(current_step, current_guide, user_id, user_message,
                                  timestamp=None, gpt_answer_validator_reply=None,
                                  fail_count=None, gpt_answer_feedback=None, gpt_feedback=None):
    """
    非同步將一筆對話資料寫入資料庫，利用 ThreadPoolExecutor 提交任務執行。

    參數:
        current_step: 小整數 (CURRENT_STEP)
        current_guide: 長度固定 10 的字串 (CURRENT_GUIDE)
        user_id: 長度固定 20 的字串 (USER_ID)
        user_message: 文字訊息 (USER_MESSAGE)
        timestamp: 日期時間，若未提供則使用目前時間 (TIMESTAMP)
        gpt_answer_validator_reply: 布林值，表示 GPT 答案驗證結果 (GPT_ANSWER_VALIDATOR_REPLY)
        fail_count: 小整數 (FAIL_COUNT)
        gpt_answer_feedback: 文字訊息，最大 255 字元 (GPT_ANSWER_FEEDBACK)
        gpt_feedback: 文字訊息，最大 255 字元 (GPT_FEEDBACK)
    """
    future = executor.submit(
        sql_insert_conversation,
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

# 測試用：
# create_conversation_table()
# sql_insert_conversation(1, "Guide1", "testUser01", "TestContent", gpt_answer_validator_reply=True,
#                         fail_count=0, gpt_answer_feedback="Feedback", gpt_feedback="Feedback")
# async_sql_insert_conversation(1, "Guide1", "testUser01", "TestContent", gpt_answer_validator_reply=True,
#                               fail_count=0, gpt_answer_feedback="Feedback", gpt_feedback="Feedback")
