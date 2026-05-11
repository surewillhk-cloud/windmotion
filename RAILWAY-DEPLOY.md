# Railway 部署配置指南

> 6 个服务：PostgreSQL · Neo4j · Redis · Backend · Worker · Frontend
> 所有内部通信使用 Railway Private Network（`*.railway.internal`）

---

## 一、服务清单与 Watch Paths

| # | 服务名 | 类型 | Root Directory | Watch Paths | Dockerfile |
|---|--------|------|---------------|-------------|------------|
| 1 | Postgres | Database | `/` | — | — |
| 2 | Neo4j | Database | `/` | — | — |
| 3 | Redis | Database | `/` | — | — |
| 4 | Backend | Service | `/` | `backend/`, `requirements.txt` | `backend/Dockerfile` |
| 5 | Worker | Service | `/` | `worker/`, `backend/`, `requirements.txt` | `worker/Dockerfile` |
| 6 | Frontend | Service | `/frontend` | `src/`, `public/`, `package.json`, `vite.config.ts` | `Dockerfile` |

---

## 二、各服务环境变量

### 1. Postgres（数据库插件）

Railway Postgres 插件自动提供以下变量，**无需手动设置**：

```
DATABASE_URL          ← 自动生成，格式: postgresql://user:pass@host:port/db
PGHOST / PGPORT / PGUSER / PGPASSWORD / PGDATABASE
```

**需要手动添加：**

| 变量 | 值 | 说明 |
|------|-----|------|
| `POSTGRES_DB` | `windmotion` | 数据库名 |
| `POSTGRES_USER` | `windmotion` | 用户名 |

---

### 2. Neo4j（Docker 镜像服务）

> Railway 没有 Neo4j 插件，需用 Docker 镜像 `neo4j:5-community`

**环境变量：**

| 变量 | 值 | 说明 |
|------|-----|------|
| `NEO4J_AUTH` | `neo4j/自定义强密码` | 认证（格式: user/password） |
| `NEO4J_PLUGINS` | `["apoc"]` | 安装 APOC 插件 |

**生成后记下内部域名，格式：** `neo4j.railway.internal:7687`

---

### 3. Redis（数据库插件）

Railway Redis 插件自动提供：

```
REDIS_URL             ← 自动生成，格式: redis://default:pass@host:port
REDISHOST / REDISPORT / REDISPASSWORD
```

**无需手动设置。**

---

### 4. Backend（FastAPI 服务）

**Source Directory:** `/`（monorepo 根目录）
**Watch Paths:** `backend/`, `requirements.txt`

| 变量 | 值 | 来源 |
|------|-----|------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Railway 变量引用 ⭐ |
| `NEO4J_URI` | `bolt://neo4j.railway.internal:7687` | 手动填写 |
| `NEO4J_USER` | `neo4j` | 手动填写 |
| `NEO4J_PASSWORD` | `${{Neo4j.NEO4J_AUTH}}` 中的密码部分 | 见下方说明 |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Railway 变量引用 ⭐ |
| `DEEPSEEK_API_KEY` | `sk-xxx` | 手动填写 |
| `QWEN_API_KEY` | `sk-xxx` | 手动填写 |
| `BSCSCAN_API_KEY` | `xxx` | 手动填写 |
| `CORS_ORIGINS` | `https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}` | Railway 变量引用 |
| `FRONTEND_URL` | `https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}` | Railway 变量引用 |
| `PORT | `8080`` | Railway 自动提供，Dockerfile 中使用 `$PORT` |

> ⚠️ **NEO4J_PASSWORD 说明：** Railway 无法直接拆分 `NEO4J_AUTH` 的密码部分。
> 建议在 Neo4j 服务中额外添加一个自定义变量 `NEO4J_PASSWORD`（值与 `NEO4J_AUTH` 中的密码一致），
> 然后 Backend 中引用 `${{Neo4j.NEO4J_PASSWORD}}`。

**Dockerfile 路径：** `backend/Dockerfile`
**Start Command：**
```bash
python -m backend.db.migrations.run_migrations && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

---

### 5. Worker（Python Worker 服务）

**Source Directory:** `/`（monorepo 根目录）
**Watch Paths:** `worker/`, `backend/`

| 变量 | 值 | 来源 |
|------|-----|------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Railway 变量引用 |
| `NEO4J_URI` | `bolt://neo4j.railway.internal:7687` | 手动填写 |
| `NEO4J_USER` | `neo4j` | 手动填写 |
| `NEO4J_PASSWORD` | `${{Neo4j.NEO4J_PASSWORD}}` | 与 Backend 一致 |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Railway 变量引用 |
| `DEEPSEEK_API_KEY` | `sk-xxx` | 手动填写 |
| `QWEN_API_KEY` | `sk-xxx` | 手动填写 |
| `BSCSCAN_API_KEY` | `xxx` | 手动填写 |
| `WORKER_CONCURRENCY` | `3` | 手动填写（默认 3） |
| `TASK_TIMEOUT` | `600` | 手动填写（默认 600s） |

**Dockerfile 路径：** `worker/Dockerfile`
**Start Command：** `python -m worker.main`

---

### 6. Frontend（Nginx + Vue 3 SPA）

**Source Directory:** `/frontend`
**Watch Paths:** `src/`, `public/`, `package.json`, `vite.config.ts`

| 变量 | 值 | 来源 |
|------|-----|------|
| `BACKEND_URL` | `http://backend.railway.internal:8080` | 内部通信 |
| `VITE_API_BASE` | `https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}` | 构建时注入（可选） |

**Dockerfile 路径：** `frontend/Dockerfile`
**Start Command：** 默认（nginx）

---

## 三、Railway 变量引用语法

Railway 支持跨服务变量引用，格式为：

```
${{ServiceName.VARIABLE_NAME}}
```

**本项目需要的引用关系：**

```
Backend  → Postgres:  ${{Postgres.DATABASE_URL}}
Backend  → Redis:     ${{Redis.REDIS_URL}}
Backend  → Neo4j:     手动填写内部域名
Backend  → Frontend:  ${{Frontend.RAILWAY_PUBLIC_DOMAIN}}

Worker   → Postgres:  ${{Postgres.DATABASE_URL}}
Worker   → Redis:     ${{Redis.REDIS_URL}}
Worker   → Neo4j:     手动填写内部域名

Frontend → Backend:   内部域名（不经过公网）
```

---

## 四、操作步骤（按顺序）

### Step 1: 配置数据库服务

**Postgres 插件：**
- 添加变量 `POSTGRES_DB=windmotion`，`POSTGRES_USER=windmotion`

**Neo4j Docker 服务：**
- Image: `neo4j:5-community`
- 添加变量：
  - `NEO4J_AUTH=neo4j/你的强密码`
  - `NEO4J_PASSWORD=你的强密码`（冗余一份，方便引用）
  - `NEO4J_PLUGINS=["apoc"]`
- 端口：7687（Bolt）、7474（HTTP，可选）

**Redis 插件：**
- 无需额外配置

### Step 2: 配置 Backend

- Root Directory: `/`
- Watch Paths: `backend/**`, `requirements.txt`
- Dockerfile Path: `backend/Dockerfile`
- 按上表填写所有环境变量
- 设置 Health Check Path: `/health`

### Step 3: 配置 Worker

- Root Directory: `/`
- Watch Paths: `worker/**`, `backend/**`
- Dockerfile Path: `worker/Dockerfile`
- 按上表填写所有环境变量
- **不需要** Health Check（Worker 无 HTTP 端口）

### Step 4: 配置 Frontend

- Root Directory: `/frontend`
- Watch Paths: `src/**`, `public/**`, `package.json`, `vite.config.ts`
- Dockerfile Path: `Dockerfile`
- 设置 `BACKEND_URL=http://backend.railway.internal:8080`
- 设置 Health Check Path: `/health`（nginx 已配置返回 200）

### Step5: 验证连通性

部署完成后，检查：
1. Backend 日志：`Wind Motion started successfully` + 三个数据库连接成功
2. Worker 日志：`Redis connected` / `PostgreSQL connected` / `Neo4j connected`
3. Frontend 访问：`https://xxx.up.railway.app` 能加载页面
4. API 代理：`https://xxx.up.railway.app/api/health` 返回 200

---

## 五、Railway.json 配置（可选覆盖）

当前 `railway.json` 只针对 Backend。如需为每个服务单独配置，可创建多个配置文件或通过 Railway Dashboard 设置。

**Backend 的 railway.json（已有）：**
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "backend/Dockerfile"
  },
  "deploy": {
    "startCommand": "python -m backend.db.migrations.run_migrations && uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 30,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**Worker 建议配置（通过 Dashboard 设置）：**
```
Start Command: python -m worker.main
Restart Policy: ON_FAILURE
Max Retries: 3
Health Check: 无（Worker 无 HTTP）
```

---

## 六、常见问题

### Q: NEO4J_PASSWORD 怎么引用？
A: 在 Neo4j 服务中额外添加一个变量 `NEO4J_PASSWORD=你的密码`，然后其他服务引用 `${{Neo4j.NEO4J_PASSWORD}}`。

### Q: Backend 和 Worker 的 Root Directory 设成什么？
A: 设为 `/`（monorepo 根目录），因为 Dockerfile 中 `COPY` 的路径是相对于 build context 的。

### Q: Watch Paths 支持 glob 吗？
A: 支持。用 `backend/**` 匹配 backend 目录下所有文件变更。

### Q: 前端构建时怎么注入 API 地址？
A: Nginx 模板中使用 `${BACKEND_URL}` 环境变量做反向代理，前端 JS 中如果需要直接调 API，可以在构建时用 `VITE_API_BASE` 注入。但推荐统一通过 nginx 代理 `/api/` 路径。

### Q: Worker 需要公网访问吗？
A: 不需要。Worker 只通过 Redis 队列与 Backend 通信，保持内部网络即可。
