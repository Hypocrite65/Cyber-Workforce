FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 【优化】禁用 Python 输出缓冲，实现日志实时打印
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 升级 PIP
RUN pip install --no-cache-dir --upgrade pip

# 安装依赖 - 显式版本
RUN pip install --no-cache-dir pyautogen==0.2.28 numpy pandas colorama duckduckgo-search

# 验证 Import
RUN python -c "import autogen; print('✅ Verified AutoGen:', autogen.__version__)"

# 复制源码
COPY ai_core/ ./ai_core/
COPY secrets/ ./secrets/
COPY main.py .

CMD ["python", "-u", "main.py"]
