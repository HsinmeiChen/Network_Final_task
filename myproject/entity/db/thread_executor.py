# executor.py
from concurrent.futures import ThreadPoolExecutor

# 建立全域的 ThreadPoolExecutor 實例
# 可根據需求調整 max_workers 的數量
executor = ThreadPoolExecutor(max_workers=40)
