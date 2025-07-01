# 🧼 图标背景去除器

一个基于 [Gradio](https://gradio.app/) + [rembg](https://github.com/danielgatis/rembg) 的图标去背景工具，支持批量处理、尺寸统一、背景替换、ZIP 打包下载，并支持移动端自适应布局。

> 🚀 已打包为 Docker 镜像，支持局域网访问、离线模型挂载、代理加速等高级特性。

---

## ✨ 功能特色

- ✅ 自动去除图标背景（rembg）
- ✅ 中文背景色选择（透明、白、黑、浅灰、金色）
- ✅ 图标尺寸统一（64~512px）
- ✅ 实时处理日志输出
- ✅ 单个图标下载 + ZIP 打包下载
- ✅ 自适应移动端布局
- ✅ 支持代理访问 GitHub
- ✅ 支持模型离线挂载，避免重复下载

---

## 🚀 快速启动（推荐 Docker Compose）

### 1. 克隆项目

```bash
git clone https://github.com/zeyu8023/icon-remove-docker.git
cd icon-remove-docker
```

### 2. 准备模型（推荐）

自持部署时自动下载模型，你也可以选择手动下载模型文件：

- [u2net.onnx](https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx)

放入项目目录下的 `rembg/` 文件夹：

```
icon-remove-docker/
├── rembg/
│   └── u2net.onnx
```

---

### 3. 启动服务

```bash
docker compose up -d
```

---

### 4. 浏览器访问

```
http://localhost:7860
或
http://<你的局域网IP>:7860
```

---

## 🐳 Docker Compose 配置

```yaml
version: "3.8"

services:
  icon-remove:
    image: zeyu8023/icon-remove:latest
    container_name: icon-remove
    network_mode: host  # ✅ 使用宿主机网络（Linux 推荐）
    environment:
      - HTTP_PROXY=http://127.0.0.1:7890
      - HTTPS_PROXY=http://127.0.0.1:7890
      - NO_PROXY=localhost,127.0.0.1,::1
    volumes:
      - ./logs:/app/logs
      - ./rembg:/root/.u2net
    restart: unless-stopped
```

> ✅ 如果你不使用代理，可移除 `HTTP_PROXY` 和 `HTTPS_PROXY`  （代理用来首次运行时下载模型）
> ✅ 如果你不是 Linux 用户，请改为使用 `ports: - "7860:7860"` 而不是 `network_mode: host`

---

## 📦 镜像说明

你也可以直接拉取镜像运行：

```bash
docker pull zeyu8023/icon-remove:latest
```

---

## 📁 项目结构

```
icon-remove-docker/
├── app.py                 # 主程序
├── Dockerfile             # 构建镜像
├── docker-compose.yml     # 一键部署
├── requirements.txt       # Python 依赖
├── rembg/                 # 模型缓存目录（挂载）
├── logs/                  # 日志输出目录（挂载）
└── .github/workflows/     # 自动构建配置（可选）
```

---

## 📜 License

MIT License © zeyu8023
