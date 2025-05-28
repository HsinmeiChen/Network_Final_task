#
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.exc import SQLAlchemyError
import os

class DbFileConverter:
    """
    資料庫與檔案轉換工具，支援將資料庫表格匯出為 Excel 或 CSV，
    以及將 Excel 或 CSV 檔案資料匯入指定的資料庫表格。
    """
    
    def __init__(self, db_session=None, engine_url=None):
        """
        初始化轉換工具
        
        Args:
            db_session: SQLAlchemy 的 Session 物件
            engine_url: 資料庫連線字串，如果未提供 db_session 則必須提供
        """
        if db_session:
            self.session = db_session
            self.engine = db_session.get_bind()
        elif engine_url:
            self.engine = create_engine(engine_url)
            # 這裡不創建 session，每個方法內會根據需要創建臨時 session
        else:
            raise ValueError("必須提供 db_session 或 engine_url 其中之一")
        
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
    
    def export_to_file(self, table_name, file_path, file_type='excel', columns=None, 
                       query_filter=None, sheet_name='Sheet1', index=False):
        """
        將指定資料表匯出為 Excel 或 CSV 檔案
        
        Args:
            table_name: 資料表名稱
            file_path: 檔案儲存路徑
            file_type: 檔案類型，'excel' 或 'csv'
            columns: 要匯出的欄位列表，None 表示全部欄位
            query_filter: SQLAlchemy 查詢條件，用於過濾資料
            sheet_name: Excel 工作表名稱 (僅用於 Excel 格式)
            index: 是否在輸出檔案中包含索引
            
        Returns:
            bool: 成功匯出則為 True，否則為 False
        """
        try:
            # 檢查資料表是否存在
            if table_name not in self.metadata.tables:
                print(f"錯誤：資料表 '{table_name}' 不存在")
                return False
            
            # 準備 SQL 查詢
            table = self.metadata.tables[table_name]
            query = f"SELECT "
            
            # 處理欄位
            if columns:
                # 檢查指定的欄位是否存在於資料表中
                table_columns = [c.name for c in table.columns]
                invalid_columns = [c for c in columns if c not in table_columns]
                if invalid_columns:
                    print(f"錯誤：以下欄位不存在於資料表 '{table_name}'：{', '.join(invalid_columns)}")
                    return False
                query += ", ".join(f'"{c}"' for c in columns)
            else:
                query += "*"
            
            query += f' FROM "{table_name}"'
            
            # 添加過濾條件
            if query_filter:
                query += f" WHERE {query_filter}"
            
            # 執行查詢並載入到 DataFrame
            df = pd.read_sql(query, self.engine)
            
            # 檢查是否有資料
            if df.empty:
                print(f"警告：查詢結果為空，將創建空檔案")
            
            # 根據檔案類型匯出
            if file_type.lower() == 'excel':
                # 檢查檔案副檔名
                if not file_path.endswith(('.xlsx', '.xls')):
                    file_path += '.xlsx'
                df.to_excel(file_path, sheet_name=sheet_name, index=index)
                print(f"成功：已將資料表 '{table_name}' 匯出為 Excel 檔案：{file_path}")
            elif file_type.lower() == 'csv':
                # 檢查檔案副檔名
                if not file_path.endswith('.csv'):
                    file_path += '.csv'
                df.to_csv(file_path, index=index, encoding='utf-8-sig')
                print(f"成功：已將資料表 '{table_name}' 匯出為 CSV 檔案：{file_path}")
            else:
                print(f"錯誤：不支援的檔案類型 '{file_type}'，支援的類型為 'excel' 或 'csv'")
                return False
            
            return True
        
        except Exception as e:
            print(f"匯出資料時發生錯誤：{str(e)}")
            return False
    
    def import_from_file(self, file_path, table_name, if_exists='append', 
                        sheet_name=0, dtype=None, converters=None, 
                        chunksize=None, date_columns=None):
        """
        從 Excel 或 CSV 檔案匯入資料到指定資料表
        
        Args:
            file_path: 檔案路徑
            table_name: 目標資料表名稱
            if_exists: 如果資料表已存在，執行的操作：'fail', 'replace' 或 'append'
            sheet_name: 工作表名稱或索引 (僅用於 Excel 格式)
            dtype: 欄位資料類型的字典映射
            converters: 欄位自定義轉換函數的字典映射
            chunksize: 處理大檔案時，每次讀取的行數
            date_columns: 需要轉換為日期時間格式的欄位列表
            
        Returns:
            bool: 成功匯入則為 True，否則為 False
        """
        try:
            # 檢查檔案是否存在
            if not os.path.exists(file_path):
                print(f"錯誤：檔案 '{file_path}' 不存在")
                return False
            
            # 檢查資料表是否存在
            table_exists = table_name in self.metadata.tables
            if not table_exists and if_exists != 'replace':
                print(f"錯誤：資料表 '{table_name}' 不存在，且 if_exists 不是 'replace'")
                return False
            
            # 根據檔案類型讀取資料
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # 讀取 Excel 檔案
                df = pd.read_excel(
                    file_path, 
                    sheet_name=sheet_name,
                    dtype=dtype,
                    converters=converters,
                    parse_dates=date_columns,
                    engine='openpyxl'
                )
            elif file_ext == '.csv':
                # 讀取 CSV 檔案
                df = pd.read_csv(
                    file_path,
                    dtype=dtype,
                    converters=converters,
                    parse_dates=date_columns,
                    encoding='utf-8-sig'
                )
            else:
                print(f"錯誤：不支援的檔案類型 '{file_ext}'，支援的類型為 .xlsx, .xls 或 .csv")
                return False
            
            # 檢查是否有資料
            if df.empty:
                print(f"警告：檔案 '{file_path}' 不包含資料")
                return False
            
            # 如果資料表已存在，檢查欄位是否匹配
            if table_exists and if_exists != 'replace':
                table = self.metadata.tables[table_name]
                table_columns = [c.name for c in table.columns]
                missing_columns = [c for c in df.columns if c not in table_columns]
                
                if missing_columns:
                    print(f"警告：檔案中的以下欄位在資料表 '{table_name}' 中不存在：{', '.join(missing_columns)}")
                    print("這些欄位將被忽略")
                    df = df[[c for c in df.columns if c in table_columns]]
            
            # 將資料寫入資料庫
            if chunksize:
                # 分批處理大資料集
                chunks = [df[i:i+chunksize] for i in range(0, len(df), chunksize)]
                for i, chunk in enumerate(chunks):
                    chunk.to_sql(
                        name=table_name,
                        con=self.engine,
                        if_exists='append' if i > 0 or if_exists == 'append' else if_exists,
                        index=False
                    )
                    print(f"進度：已處理 {min((i+1)*chunksize, len(df))}/{len(df)} 行")
            else:
                # 一次性處理
                df.to_sql(
                    name=table_name,
                    con=self.engine,
                    if_exists=if_exists,
                    index=False
                )
            
            print(f"成功：已從檔案 '{file_path}' 匯入 {len(df)} 行資料到資料表 '{table_name}'")
            
            # 重新讀取資料庫結構以反映可能的變更
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            
            return True
        
        except SQLAlchemyError as e:
            print(f"資料庫錯誤：{str(e)}")
            return False
        except Exception as e:
            print(f"匯入資料時發生錯誤：{str(e)}")
            return False