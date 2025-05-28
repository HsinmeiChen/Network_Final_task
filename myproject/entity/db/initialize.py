# create_tables.py
import glob
import importlib
import os
from db_connection import engine, Base
from tool.dbfileconverter import DbFileConverter
def initialize_database():
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")

def import_all_models():
    # 獲取 models 目錄下的所有 .py 文件
    models_dir = os.path.dirname(os.path.abspath(__file__)) + '/models'
    model_files = glob.glob(f"{models_dir}/[!_]*.py")
    
    for model_file in model_files:
        module_name = os.path.basename(model_file)[:-3]
        importlib.import_module(f'models.{module_name}')
    
    print(f"已導入的表格: {Base.metadata.tables.keys()}")


# if __name__ == "__main__":
#     import_all_models()
#     initialize_database()