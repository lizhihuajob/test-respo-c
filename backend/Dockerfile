FROM python:3.12-alpine

WORKDIR /app

# 创建数据目录
RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 设置环境变量，用于在Docker中指定数据库路径
ENV DATABASE_PATH=/app/data/kanban.db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]