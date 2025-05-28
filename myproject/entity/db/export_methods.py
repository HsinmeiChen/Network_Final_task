import pandas as pd

def export_model_to_file(session, model, filename, columns=None):
    """
    將指定 SQLAlchemy model 的資料輸出成 CSV 或 Excel 檔案

    :param session: SQLAlchemy 的 session 物件
    :param model: 要輸出的 SQLAlchemy model class
    :param filename: 輸出檔案名稱，必須以 .csv 或 .xlsx/.xls 結尾
    :param columns: 要輸出的欄位列表，預設為 model 中所有欄位
    """
    # 如果未指定欄位，則使用 model 中所有欄位
    if columns is None:
        columns = [c.name for c in model.__table__.columns]

    # 查詢所有資料
    instances = session.query(model).all()

    # 將資料轉換成 list of dicts
    data = []
    for instance in instances:
        row = {col: getattr(instance, col) for col in columns}
        data.append(row)

    # 建立 DataFrame
    df = pd.DataFrame(data)

    # 根據檔案副檔名輸出成 CSV 或 Excel
    if filename.lower().endswith('.csv'):
        df.to_csv(filename, index=False, encoding='utf-8')
    elif filename.lower().endswith(('.xlsx', '.xls')):
        df.to_excel(filename, index=False)
    else:
        raise ValueError("檔案名稱必須以 .csv 或 .xlsx/.xls 結尾")
