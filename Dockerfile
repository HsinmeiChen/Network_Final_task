# 使用 Python 基礎映像
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製專案檔案
COPY . /app

# 更新套件清單並安裝必要的套件
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        apt-transport-https \
        gnupg2 \
        unixodbc-dev

# 新增 Microsoft 的 GPG 金鑰並加入 Microsoft 軟體來源
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list \
      > /etc/apt/sources.list.d/mssql-release.list

# 再次更新套件清單並安裝 ODBC Driver 17（安裝過程會需要接受 EULA）
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# 安裝依賴項
RUN pip install --no-cache-dir -r requirements.txt

# 設定環境變數
ENV PORT 8080
#ENV DJANGO_SETTINGS_MODULE myproject.settings.production  # 替換成實際的 settings 模組

# 收集靜態檔案
#RUN python manage.py collectstatic --noinput

# 啟動指令
CMD exec gunicorn myproject.wsgi:application --bind :$PORT --workers 3