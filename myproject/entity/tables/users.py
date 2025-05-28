# main.py (或放置於你專案中的某個模組中)
from .db_connection import engine
from datetime import datetime
import hashlib
import os
#import pandas as pd  # 匯入 pandas 用來寫入 Excel
import string
import random

# 取得原生 DBAPI 連線 (注意：取得的是 engine.raw_connection())
def get_db_connection():
    return engine.raw_connection()

# --------------------------
# 密碼處理
# --------------------------
def generate_salt():
    """生成隨機 salt"""
    return os.urandom(16).hex()

def hash_password(password, salt):
    """使用 salt 進行密碼雜湊"""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_random_password(length=10):
    """
    生成由大小寫字母與數字組成的亂數密碼
    例如： 'aB3dE5fG7H'
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))
# --------------------------
# 使用者管理功能
# --------------------------

def create_users_table():
    """
    建立大寫欄位及表名的 USERS 資料表
    資料表結構：
      - USERID: 使用者 ID，主鍵，VARCHAR(50)
      - USERNAME: 使用者名稱，NVARCHAR(100)
      - EMAIL: 電子郵件，NVARCHAR(255)
      - PASSWORD_HASH: 密碼雜湊，NVARCHAR(64)
      - SALT: 密碼雜湊所用的 salt，VARCHAR(32)
      - ROLE: 使用者角色，VARCHAR(20)
      - IS_ACTIVE: 帳號是否啟用 (BIT)，預設為 1 (啟用)
      - FAILED_ATTEMPTS: 登入失敗次數 (INT)，預設為 0
      - LAST_LOGIN: 最後登入時間 (DATETIME)，允許 NULL
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 利用 SQL Server 的 OBJECT_ID 判斷 dbo.USERS 是否存在，若不存在則建立
        create_table_sql = """
        IF OBJECT_ID('dbo.USERS', 'U') IS NULL
        BEGIN
            CREATE TABLE dbo.USERS (
                USERID VARCHAR(50) PRIMARY KEY,
                USERNAME NVARCHAR(100) NOT NULL,
                EMAIL NVARCHAR(255) NOT NULL,
                PASSWORD_HASH NVARCHAR(64) NOT NULL,
                SALT VARCHAR(32) NOT NULL,
                ROLE VARCHAR(20) NOT NULL,
                IS_ACTIVE BIT DEFAULT 1,
                FAILED_ATTEMPTS INT DEFAULT 0,
                LAST_LOGIN DATETIME NULL
            )
        END
        """
        cursor.execute(create_table_sql)
        conn.commit()
        print("USERS table created successfully (or already exists).")
    except Exception as err:
        if conn:
            conn.rollback()
        print(f"Error creating USERS table: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def add_user(userid, username, email, password, role='user'):
    """
    新增使用者至 USERS 資料表
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        
        sql = """
            INSERT INTO USERS (USERID, USERNAME, EMAIL, PASSWORD_HASH, SALT, ROLE)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(sql, (userid, username, email, password_hash, salt, role))
        conn.commit()
        print(f"User {username} added successfully.")
    except Exception as err:
        if conn:
            conn.rollback()
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def delete_user(userid):
    """
    刪除指定 USERID 的使用者
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM USERS WHERE USERID = ?"
        cursor.execute(sql, (userid,))
        conn.commit()
        print(f"User with ID {userid} deleted successfully.")
    except Exception as err:
        if conn:
            conn.rollback()
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_user(userid, username=None, email=None, password=None, role=None):
    """
    更新指定使用者的資料
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        
        if username:
            fields.append("USERNAME = ?")
            values.append(username)
        if email:
            fields.append("EMAIL = ?")
            values.append(email)
        if password:
            salt = generate_salt()
            password_hash = hash_password(password, salt)
            fields.append("PASSWORD_HASH = ?")
            fields.append("SALT = ?")
            values.append(password_hash)
            values.append(salt)
        if role:
            fields.append("ROLE = ?")
            values.append(role)
        
        if not fields:
            print("No fields to update.")
            return
        
        values.append(userid)
        sql = f"UPDATE USERS SET {', '.join(fields)} WHERE USERID = ?"
        cursor.execute(sql, values)
        conn.commit()
        print(f"User with ID {userid} updated successfully.")
    except Exception as err:
        if conn:
            conn.rollback()
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def verify_login(userid, password):
    """
    驗證使用者登入，回傳 (True, user) 表示驗證成功，
    回傳 (False, user) 或 (False, None) 表示失敗。
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM USERS WHERE USERID = ?"
        cursor.execute(sql, (userid,))
        row = cursor.fetchone()
        if row:
            # 將 row 轉換為 dictionary (欄位名稱皆為大寫)
            columns = [col[0] for col in cursor.description]
            user = dict(zip(columns, row))
        else:
            user = None

        if not user:
            return False, None
        elif not user.get('IS_ACTIVE', True):
            return False, user
        elif user.get('FAILED_ATTEMPTS', 0) >= 5:
            return False, user
        else:
            input_password_hash = hash_password(password, user['SALT'])
            if user['PASSWORD_HASH'] == input_password_hash:
                # 成功登入，重設 FAILED_ATTEMPTS 並更新 LAST_LOGIN
                sql_update = "UPDATE USERS SET FAILED_ATTEMPTS = 0, LAST_LOGIN = ? WHERE USERID = ?"
                cursor.execute(sql_update, (datetime.now(), userid))
                conn.commit()
                return True, user
            else:
                # 密碼錯誤，更新 FAILED_ATTEMPTS
                sql_update = "UPDATE USERS SET FAILED_ATTEMPTS = FAILED_ATTEMPTS + 1 WHERE USERID = ?"
                cursor.execute(sql_update, (userid,))
                conn.commit()
                return False, user
    except Exception as err:
        if conn:
            conn.rollback()
        print(f"Error during login verification: {err}")
        return False, None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def deactivate_user(userid):
    """
    停用指定使用者 (將 IS_ACTIVE 設為 0)
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE USERS SET IS_ACTIVE = 0 WHERE USERID = ?"
        cursor.execute(sql, (userid,))
        conn.commit()
        print(f"User with ID {userid} has been deactivated.")
    except Exception as err:
        if conn:
            conn.rollback()
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --------------------------
# 測試程式 (可根據需要測試各功能)
# --------------------------
# if __name__ == "__main__":
#     # 建立 USERS 資料表 (若不存在)
#     create_users_table()
    
#     # 新增使用者
#     add_user('u001', '王小明', 'xiaoming@example.com', 'password123')
    
#     # 更新使用者資料
#     update_user('u001', username='王小明更新', email='xiaoming_updated@example.com', password='newpassword123')
    
#     # 驗證登入 (正確與錯誤兩種情況)
#     verify_login('u001', 'newpassword123')
#     verify_login('u001', 'wrong_password')
    
#     # 停用使用者
#     deactivate_user('u001')
    
#     # 刪除使用者
#     delete_user('u001')

# if __name__ == "__main__":
#     # 建立 USERS 資料表 (若不存在)
#     create_users_table()
    
#     # 用來儲存新增使用者的帳密資訊，方便後續輸出到 Excel
#     user_records = []
    
#     # 建立 40 個使用者，每個使用者的密碼為亂數 10 個字元
#     for i in range(1, 41):
#         userid = f"u{i:03d}"               # 例如：u001, u002, ..., u040
#         username = f"使用者{i:03d}"          # 例如：使用者001, 使用者002, ..., 使用者040
#         email = f"user{i:03d}@example.com"   # 例如：user001@example.com, ...
#         password = generate_random_password(10)  # 亂數生成 10 個字元的密碼
        
#         # 新增使用者至資料庫
#         add_user(userid, username, email, password)
        
#         # 記錄帳號資訊 (注意：這裡記錄的是明文密碼，僅供測試使用，
#         #          實際上請勿以明文方式儲存密碼)
#         user_records.append({
#             "USERID": userid,
#             "USERNAME": username,
#             "EMAIL": email,
#             "PASSWORD": password
#         })
    
#     # 利用 pandas 將使用者帳密資訊寫入 Excel 檔案
#     df = pd.DataFrame(user_records)
#     output_file = "user_accounts.xlsx"
#     df.to_excel(output_file, index=False)
#     print(f"User account information has been written to '{output_file}'.")
