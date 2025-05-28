# example_usage.py
import urllib
from dbfileconverter import DbFileConverter

# 假設你有一個資料庫連線字串
# 這裡使用 SQLite 作為示範，實際上你可以使用任何 SQLAlchemy 支援的資料庫連線字串

# username = "manager"
# password = "iisi@641001"
# db_host = '34.134.75.49:1433'
# db_name = 'chatbot'
# encoded_password = urllib.parse.quote(password, safe="")
# engine_url = f"mssql+pyodbc://{username}:{encoded_password}@{db_host}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server"
# # 建立 DbFileConverter 實例
# converter = DbFileConverter(engine_url=engine_url)

# ---------------------------
# 範例 1：匯出資料表為 Excel 檔案
# ---------------------------
# export_success = converter.export_to_file(
#     table_name="USERS",          # 資料表名稱
#     file_path="users_data.xlsx", # 匯出檔案儲存路徑
#     file_type="excel",           # 匯出為 Excel 格式
#     columns=None,                # 若為 None 表示匯出所有欄位，也可指定部分欄位，例如 ["id", "name", "email"]
#     query_filter=None,           # 可傳入 SQL 條件字串作資料過濾，例如 "age > 30"
#     sheet_name="Users",          # Excel 工作表名稱
#     index=False                  # 是否包含 DataFrame 索引
# )
# print("Export success:", export_success)

# ---------------------------
# 範例 2：從 CSV 檔案匯入資料到資料表
# ---------------------------
# 假設你有一個 CSV 檔案 "import_users.csv"，檔案中欄位需與資料表 "users" 相符
# import_success = converter.import_from_file(
#     file_path="users_data.xlsx", # 檔案路徑
#     table_name="USERS",           # 目標資料表名稱
#     if_exists="append",           # 若資料表存在則追加資料；也可選 'fail' 或 'replace'
#     sheet_name=0,                 # CSV 檔案不適用工作表，這個參數可忽略
#     dtype=None,                   # 欄位資料型態映射 (可選)
#     converters=None,              # 欄位自定義轉換函數 (可選)
#     chunksize=500,                # 若資料量大，可分批次寫入，此例每次處理 500 筆
#     date_columns=None             # 需要轉換為日期的欄位 (可選)
# )
# print("Import success:", import_success)
