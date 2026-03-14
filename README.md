# AI Navigation

一个前后端分离的 AI 导航站项目。

前端提供导航站首页、内容详情、投稿、友链、后台管理页面；后端提供公开接口、后台接口、登录鉴权和 SQLite 数据存储。

## 项目结构

```text
.
├─ web/                  Vue 3 前端
├─ pybackground/         FastAPI 后端
├─ deploy/               线上发布脚本
├─ docker-compose.yml    本地 Docker 启动
└─ release/              本地打包后的发布产物
```

## 技术栈

前端：

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Axios
- Tailwind CSS

后端：

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- PyJWT
- SQLite

部署相关：

- Docker
- Docker Compose
- Nginx

## 功能概览

- 导航站首页与分类展示
- 内容详情页
- 网站投稿
- 友情链接申请
- 管理员登录
- 后台内容管理
- 后台分类管理
- 后台友链审核
- SQLite 持久化存储

## 默认端口

本地开发：

- 前端 Vite: `5173`
- 后端 FastAPI: `8000`

本地 Docker：

- 前端: `80`
- 后端直连: `18000`

线上发布：

- 前端统一入口: `18080`
- 后端通过前端容器反代，不单独暴露

## 环境要求

非 Docker 方式：

- Node.js 20+
- npm 10+
- Python 3.11+

Docker 方式：

- Docker
- Docker Compose 插件

## 从 0 开始本地运行

### 1. 启动后端

进入后端目录并安装依赖：

```powershell
cd .\pybackground
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

启动后端：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

健康检查：

```text
http://127.0.0.1:8000/api/v1/health
```

### 2. 启动前端

打开新终端，进入前端目录：

```powershell
cd .\web
npm install
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

说明：

- 前端开发环境已通过 Vite 代理 `/api` 到 `http://127.0.0.1:8000`
- 默认管理员账号：`admin`
- 默认管理员密码：`admin123`

## 数据库说明

本地开发默认使用：

`pybackground/data/navigation.db`

后端启动时会自动初始化表结构，并在数据库为空时写入默认管理员和种子数据。

可通过环境变量覆盖管理员信息和 JWT 密钥：

- `NAV_ADMIN_USERNAME`
- `NAV_ADMIN_PASSWORD`
- `NAV_SECRET_KEY`

## 数据导入

项目提供了导入脚本，可将 JSON 数据导入 SQLite：

```powershell
cd .\pybackground
python .\import_sites.py --source ..\数据爬取\pybackground_sites.json
```

可选参数：

- `--level1`
- `--status`
- `--allow-duplicates`

## 非 Docker 生产运行

适合你自己管理宿主机进程或由宿主机 Nginx 反代。

### 后端

```bash
cd /path/to/pybackground
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 前端

```bash
cd /path/to/web
npm install
npm run build
```

构建产物在：

`web/dist`

然后用 Nginx 托管 `dist`，并把 `/api/` 反代到：

`http://127.0.0.1:8000`

## Docker 本地运行

根目录执行：

```powershell
docker compose up --build -d
```

访问：

- 前端：`http://localhost`
- 后端直连：`http://localhost:18000/api/v1/health`

停止：

```powershell
docker compose down
```

说明：

- 本地 Docker 数据目录映射到 `pybackground/data`
- 本地 `8000` 宿主机端口可能已被占用，所以后端映射为 `18000`

## Docker 线上部署

项目已经提供了离线发布方案。

本地打包：

```powershell
.\deploy\package-release.ps1
```

打包后会生成：

`release/nav-stack-release.zip`

上传到服务器 `/home/daohang` 后，一键执行：

```bash
cd /home/daohang && unzip -o nav-stack-release.zip && cd nav-stack-release && chmod +x install.sh && ./install.sh
```

线上默认访问端口：

`18080`

线上数据库固定使用：

`/home/daohang/data/navigation.db`

说明：

- 发布包不会覆盖线上数据库
- 线上镜像名固定为 `nav-backend:release` 和 `nav-frontend:release`
- 宿主机 Nginx 可直接反代到 `127.0.0.1:18080`

## 常用命令

前端构建：

```powershell
cd .\web
npm run build
```

本地重新打包发布：

```powershell
.\deploy\package-release.ps1
```

查看 Docker 服务状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f
```

## 相关文件

- `deploy/package-release.ps1`：本地打包发布包
- `deploy/install.sh`：线上一键安装入口
- `deploy/server-deploy.sh`：线上镜像加载和容器启动
- `deploy/compose.prod.yml`：线上 Compose 配置
- `docker-compose.yml`：本地 Docker 配置

## 后续建议

- 生产环境修改 `NAV_ADMIN_PASSWORD`
- 生产环境修改 `NAV_SECRET_KEY`
- 宿主机 Nginx 接入域名和 HTTPS
- 定期备份 `/home/daohang/data/navigation.db`
