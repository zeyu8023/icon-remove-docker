# 使用官方 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 拷贝项目文件
COPY requirements.txt .
COPY app.py .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 启动 Gradio 服务（监听所有 IP）
CMD ["python", "app.py"]