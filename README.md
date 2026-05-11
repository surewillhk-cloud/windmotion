# 风动 Wind Motion

> AI 驱动的链上交易推演引擎 —— 看见每一步决策背后的逻辑

## 系统概述

风动是一个基于多 Agent 协作和解耦 Skill 架构的链上交易分析与推演系统。它接收鲸鱼地址和链上交易数据，通过筛选、逆向分析、因果建模、事件注入、概率定价、深度审议六个核心能力，输出结构化的策略分析报告和推演回放。

## 核心特性

- **14 个 AI Agent** — 裁判、导演、链上分析师、Token 分析师、宏观分析师、审查×3、散户×3、社交媒体×2、机构投资者
- **12 个 Skill** — 因果图谱构建、事件分析、概率定价、审议、报告生成、鲸鱼筛选、因子反推、图谱同步、上下文管理、模型路由、数据采集、价格预言机
- **反向推演** — 从已知结果反推决策过程和因子分析
- **正向推演** — 实时因果推演，10分钟内输出概率判断
- **深空科幻 UI** — 深色背景 + 发光元素 + 扫描线效果
- **7 种语言** — 简中/繁中/英文/泰语/韩语/日语/越南语
- **嵌入式推演展示** — iframe 嵌入，自定义标题，展示真实推演过程

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + D3.js + ECharts + Pinia + vue-i18n |
| 后端 API | Python FastAPI |
| 推演引擎 | Python (Orchestrator + Skill 执行) |
| 图谱存储 | Neo4j |
| 结构化数据 | PostgreSQL |
| 缓存/队列 | Redis |
| 大模型 | DeepSeek-R1 / DeepSeek-V3 / Qwen-Turbo |

## 快速开始

### 前置条件

- Docker & Docker Compose
- Node.js 20+
- Python 3.11+

### 使用 Docker

```bash
# 启动所有服务
make docker-up

# 或手动
docker compose up -d
```

### 本地开发

```bash
# 安装依赖
make install

# 启动数据库服务
docker compose up -d postgres neo4j redis

# 启动后端
make dev-backend

# 启动前端（新终端）
make dev-frontend
```

### 访问

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## 项目结构

```
windmotion/
├── backend/                 # Python 后端
│   ├── orchestrator/        # 编排器（正向/反向推演流程）
│   ├── agents/              # 14 个 Agent 实现
│   ├── skills/              # 12 个 Skill 实现
│   ├── config/              # JSON 配置文件
│   ├── api/                 # REST API + WebSocket
│   ├── models/              # 数据模型
│   ├── services/            # 业务服务
│   ├── db/                  # 数据库连接
│   └── tests/               # 测试
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── pages/           # 11 个页面
│       ├── components/      # 组件库
│       ├── i18n/            # 国际化（7种语言）
│       ├── stores/          # Pinia 状态管理
│       ├── services/        # API 客户端
│       ├── styles/          # 深空科幻主题
│       └── router/          # 路由
├── docker-compose.yml
├── Makefile
└── README.md
```

## 产品演进路线

### 阶段一（当前）：反推分析系统
- 输入：鲸鱼地址 + 链上交易数据
- 输出：策略报告 + 决策时间线 + 因子评分矩阵 + 策略模式标签

### 阶段二（中期）：正向推演引擎
- 输入：实时链上数据 + 因果图谱模板
- 输出：实时推演报告 + 概率判断 + 因果图谱

### 阶段三（最终）：EA 自动交易系统
- 输入：推演引擎输出的交易信号
- 输出：自动化交易执行

## API 文档

启动后端后访问 http://localhost:8000/docs 查看完整 API 文档。

### 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/whales/feed | 实时鲸鱼交易 Feed |
| POST | /api/whales/{address}/analyze | 启动反向分析 |
| POST | /api/whales/{address}/infer | 启动正向推演 |
| GET/POST | /api/filters | 筛选方案管理 |
| GET | /api/analysis/{id}/progress | 分析进度 |
| GET | /api/analysis/{id}/report | 分析报告 |
| GET | /api/embed/cases | 嵌入案例列表 |

### WebSocket 通道

| 通道 | 说明 |
|------|------|
| ws://host/ws/feed | 实时交易推送 |
| ws://host/ws/analysis/{id}/progress | 推演进度 |
| ws://host/ws/analysis/{id}/graph | 图谱更新 |
| ws://host/ws/analysis/{id}/probability | 概率更新 |

## 成本估算

| 场景 | 预估成本 |
|------|----------|
| 单次正向推演 | ~¥3-4 |
| 单次反向推演（深度） | ~¥0.02 |
| 每月运营（10正向+50反向/天） | ~¥900-1200 |

## License

Private - All rights reserved
