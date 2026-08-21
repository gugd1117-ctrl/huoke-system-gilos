# GILOS · 全球智能获客操作系统

> **G**lobal **I**ntelligence **L**ead **O**cquisition **S**ystem
> Find Demand · Find Opportunity · Find Customers
> **找需求 → 找机会 → 找客户**

![version](https://img.shields.io/badge/version-v0.1.0--MVP-blue)
![status](https://img.shields.io/badge/status-已上线-34d399)
![stack](https://img.shields.io/badge/stack-FastAPI%20%2B%20Vue%203%20%2B%20SQLite-a855f7)

---

## 📌 产品定位

GILOS 是一款面向 B2B 销售 / 出海 / SaaS / 跨境电商团队的 **全球商业情报与智能获客操作系统**。

用户输入一个搜索主题（如「日本跨境电商卖家」「AI 客服 SaaS 客户」），系统会：

1. 🔑 **关键词智能扩展**（LLM + 规则双引擎，20~50 个相关词）
2. 🌐 **多平台并行爬取**（9 大 Tier 1 平台：Reddit / Google / YouTube / 抖音 / 小红书 / B站 / TikTok / Instagram / X）
3. 🧠 **AI 三级路由分析**（规则 → 轻量 LLM → 深度 LLM，成本最优化）
4. 🏷️ **7 类线索分类**（客户 / 企业 / 需求 / 痛点 / 机会 / 趋势 / 竞争）
5. 🔥 **高意向自动识别**（四维评分：意向 / 机会 / 紧急 / 综合）
6. 📄 **多格式报告导出**（Markdown / HTML / Excel）
7. 💰 **实时成本追踪**（按 Token / API 调用精确计费）

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────────────────────┐
│                     前端 UI (Vue 3 + Vite)                    │
│   HomeView(创建任务) · TaskDetailView(任务详情+线索池+导出)    │
└──────────────────────────────┬───────────────────────────────┘
                               │ Axios /api/v1
┌──────────────────────────────▼───────────────────────────────┐
│                   后端 API 层 (FastAPI)                       │
│  /tasks · /leads · /keywords · /meta · /report.* · /export   │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                  核心服务层 (Services)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌───────────────────┐       │
│  │ TaskEngine  │ │  LLMClient  │ │  KeywordExpander  │       │
│  └──────┬──────┘ └─────────────┘ └───────────────────┘       │
│  ┌──────▼──────┐ ┌─────────────┐ ┌───────────────────┐       │
│  │ LeadAnalyzer│ │ CostEngine  │ │  ReportGenerator  │       │
│  └─────────────┘ └─────────────┘ └───────────────────┘       │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              ContentCache (TTLCache · 7天)          │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│             平台适配层 (Platform Adapters · 9 个)              │
│  Reddit / GoogleSearch / YouTube                              │
│  抖音 / 小红书 / B站 / TikTok / Instagram / X                 │
│  → 统一输出 UnifiedContent schema                             │
└──────────────────────────────┬───────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────┐
│              数据层 (SQLAlchemy + SQLite)                     │
│  tasks / platform_results / leads / cost_logs                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 项目目录结构

```
获客系统/
├── backend/                          # 后端 FastAPI 服务
│   ├── app/
│   │   ├── main.py                   # FastAPI 入口 + 路由挂载
│   │   ├── config.py                 # 配置 (pydantic-settings + .env)
│   │   ├── database.py               # SQLAlchemy 引擎 + Session
│   │   ├── db_init.py                # 建表逻辑
│   │   ├── schemas.py                # Pydantic 请求/响应模型
│   │   ├── api/
│   │   │   └── routes.py             # 所有 REST API 路由定义
│   │   ├── models/
│   │   │   ├── task.py               # 任务模型 + 状态/搜索模式枚举
│   │   │   ├── lead.py               # 线索模型 + 7 类分类枚举
│   │   │   ├── platform_result.py    # 平台执行结果 + 错误码
│   │   │   └── cost_log.py           # 成本日志模型
│   │   ├── services/
│   │   │   ├── task_engine.py        # 任务引擎（核心调度）
│   │   │   ├── keyword_expander.py   # 关键词扩展（规则+LLM）
│   │   │   ├── llm_client.py         # LLM 客户端（Mock + 真实）
│   │   │   ├── lead_analyzer.py      # 线索分析（三级路由）
│   │   │   ├── cost_engine.py        # 成本计费 + 汇总
│   │   │   ├── content_cache.py      # 平台搜索结果缓存
│   │   │   └── report_generator.py   # 报告生成（MD/HTML/XLSX）
│   │   └── platforms/
│   │       ├── base.py               # 平台适配器抽象基类
│   │       ├── registry.py           # 平台注册中心（装饰器模式）
│   │       ├── unified_schema.py     # UnifiedContent 统一数据结构
│   │       ├── reddit_platform.py    # Reddit 适配器
│   │       ├── google_search.py      # Google Search 适配器
│   │       ├── youtube_platform.py   # YouTube 适配器
│   │       └── tier1_stubs.py        # 抖音/小红书/B站/TikTok/IG/X 适配器
│   ├── .env                          # 实际配置（不入库）
│   ├── .env.example                  # 配置模板
│   ├── requirements.txt              # Python 依赖
│   ├── test_api.py                   # API 集成测试脚本
│   └── data/gilos.db                 # SQLite 数据库（不入库）
│
├── frontend/                         # 前端 Vue 3 应用
│   ├── src/
│   │   ├── main.js                   # Vue 应用入口
│   │   ├── App.vue                   # 根组件（路由视图切换）
│   │   ├── api.js                    # Axios 封装 + 所有 API 方法
│   │   ├── styles.css                # 全局样式（暗色科技风）
│   │   └── views/
│   │       ├── HomeView.vue          # 首页：创建任务 + 任务列表
│   │       └── TaskDetailView.vue    # 详情页：统计/平台/线索池/导出
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js                # Vite + /api 代理配置
│   └── node_modules/                 # （不入库）
│
├── 白皮书.docx                        # 产品白皮书（产品战略/架构/路线图）
├── .gitignore                         # 忽略规则
├── README.md                          # 本文件
└── HANDOVER.md                        # 工作交接文档
```

---

## 🚀 快速启动

### 0. 环境要求

- Python **3.10+**
- Node.js **18+**

### 1. 启动后端服务

```bash
cd backend

# 1. 创建虚拟环境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（默认 MOCK 模式无需配置任何 Key）
cp .env.example .env
# 编辑 .env：如需真实 API，填入 OPENAI_API_KEY / REDDIT_* / GOOGLE_* / YOUTUBE_*

# 4. 启动服务
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

后端启动后访问：
- **API 文档 (Swagger)**: http://127.0.0.1:8000/docs
- **健康检查**: http://127.0.0.1:8000/health → `{"status":"ok"}`

### 2. 启动前端服务

```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 启动开发服务器（自带 /api 代理到 8000）
npm run dev
```

前端启动后访问：**http://127.0.0.1:5173/**

### 3. 一键测试（可选）

```bash
cd backend
.venv\Scripts\python test_api.py
```

该脚本会：
1. 创建「日本跨境电商卖家」全家桶任务
2. 轮询任务进度直到完成
3. 输出统计、高意向线索、成本汇总、扩展关键词

---

## ⚙️ 配置说明 (.env)

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | `sqlite:///./data/gilos.db` | 数据库地址（支持 SQLite / PostgreSQL / MySQL） |
| `ENABLE_MOCK_MODE` | `true` | **Mock 模式开关**：true 时无需任何 API Key，全部返回演示数据，可直接完整体验 |
| `LLM_MODEL` | `gpt-4o-mini` | LLM 模型名（仅 mock_mode=false 时生效） |
| `OPENAI_API_KEY` | `""` | OpenAI / 兼容 API 的 Key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API 基础地址（可换其他兼容接口） |
| `REDDIT_CLIENT_ID` / `SECRET` | `""` | Reddit API 凭证 |
| `GOOGLE_API_KEY` / `CSE_ID` | `""` | Google Custom Search 凭证 |
| `YOUTUBE_API_KEY` | `""` | YouTube Data API v3 Key |
| `CACHE_TTL_DAYS` | `7` | 平台搜索结果缓存 TTL（天） |

---

## 🔌 API 接口总览

所有接口前缀：`/api/v1`

| 方法 | 路径 | 说明 |
|------|------|------|
| **Meta** | | |
| GET | `/meta/search-modes` | 列出 7 种搜索模式 |
| GET | `/meta/platforms` | 列出所有接入平台 |
| GET | `/meta/lead-categories` | 列出 7 种线索分类 |
| **关键词** | | |
| POST | `/keywords/expand?query=...&search_mode=...` | 预览扩展关键词 |
| **任务** | | |
| POST | `/tasks` | 创建任务（后台异步执行） |
| GET | `/tasks?limit=50&offset=0` | 任务列表 |
| GET | `/tasks/{id}` | 任务详情（含平台执行、成本、扩展关键词） |
| POST | `/tasks/{id}/start` | 重新开始 / 重试失败任务 |
| **线索** | | |
| GET | `/tasks/{id}/leads` | 线索列表（支持 分类/高意向/最低分/平台/关键词 过滤） |
| **导出** | | |
| GET | `/tasks/{id}/report.md` | 下载 Markdown 报告 |
| GET | `/tasks/{id}/report.html` | 在线查看 HTML 报告 |
| GET | `/tasks/{id}/export.xlsx?high_intent_only=true` | 导出 Excel |

详见 Swagger 文档：http://127.0.0.1:8000/docs

---

## 🎯 核心业务逻辑说明

### 1. 任务执行流水线 (TaskEngine.run_task_async)

```
[10%]  关键词扩展（KeywordExpander）
[10%-80%] 逐平台执行：
  ├─ is_available() 检查
  ├─ 缓存命中 / adapter.search() 搜索
  ├─ 转换为 UnifiedContent 统一对象
  ├─ 逐内容 LeadAnalyzer.analyze_content()
  └─ 写入 leads 表
[80%-95%] 下一平台
[95%+] _refresh_stats() 汇总 8 项统计 → 100% 完成
```

### 2. LLM 三级路由策略 (LeadAnalyzer._route_model)

| 路由级别 | 触发条件 | LLM 调用 | 成本 |
|----------|----------|-----------|------|
| **rule** | 内容<300字且无需求/痛点关键词 | ❌ 纯规则关键词匹配 | $0 |
| **light** | 内容<800字 或 短内容含关键词 | ✅ 轻量 prompt | $0.15 / 1M tokens |
| **advanced** | 长文本 (>800字) | ✅ 完整分析 prompt | $2.50 / 1M tokens |

### 3. 高意向判定规则

在 `LeadAnalyzer.content_to_lead()` 中：
- `overall = intent * 0.45 + opportunity * 0.35 + urgency * 0.20`
- **高意向** = `intent >= 70` **或** `overall >= 65`

### 4. 线索分类（7 类）

| 值 | 中文名 | 含义 |
|----|--------|------|
| `customer` | 客户 | 存在明确购买意向的个人/企业 |
| `company` | 企业 | 招聘/扩张/可作为目标客户的公司 |
| `demand` | 需求 | 市场正在寻找的产品/服务/解决方案 |
| `pain_point` | 痛点 | 用户对现有方案的抱怨/吐槽 |
| `opportunity` | 机会 | 尚未被满足的蓝海/商业机会 |
| `trend` | 趋势 | 增长/热门/新兴方向 |
| `competition` | 竞争 | 竞品/竞争对手相关信号 |

---

## 📊 已验证运行指标

测试用例：`日本跨境电商卖家` + `family_bucket` 模式（Mock）

| 指标 | 数值 | 耗时 |
|------|------|------|
| 总内容发现 | **380 条** | |
| 🔥 高意向线索 | **347 条** (91.3%) | |
| 企业线索 | 225 条 | |
| 明确需求 | 347 条 | |
| 扩展关键词 | 31 个 | |
| 接入平台数 | 9 个 (all Tier 1) | |
| **端到端总耗时** | **~12 秒** | 2 次轮询完成 |
| **总成本** | **$0.20 / ¥1.44** | LLM $0.01 + API $0.19 |

---

## 🧪 测试

项目包含端到端测试脚本 `backend/test_api.py`，可直接运行验证全链路。

单元测试目录结构预留（可后续补充）：
```
backend/tests/
  test_keyword_expander.py
  test_lead_analyzer_rule.py
  test_task_engine_flow.py
```

---

## 🔜 后续迭代方向

见 [HANDOVER.md → 八、后续 TODO 与路线图](./HANDOVER.md#八后续-todo-与路线图)

---

## 📝 许可证 & 联系方式

内部项目，版权所有。
交接文档见：**[HANDOVER.md](./HANDOVER.md)**
