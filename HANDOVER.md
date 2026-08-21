# 工作交接文档 · GILOS 全球智能获客 OS

> **文档版本**: v1.0  
> **交接日期**: 2026-08-21  
> **当前状态**: ✅ v0.1 MVP 已完成，后端 + 前端 + Mock 模式全链路可运行

---

## 一、项目背景与产品战略

### 1.1 项目定位
GILOS（**G**lobal **I**ntelligence **L**ead **O**cquisition **S**ystem）是从「抖音获客工具」演进而来的**全球商业情报与智能获客操作系统**。

核心 Slogan：**Find Demand · Find Opportunity · Find Customers → 找需求 → 找机会 → 找客户**

### 1.2 白皮书核心战略（已提取自 白皮书.docx）

| 维度 | 核心要点 |
|------|----------|
| **产品定位** | 从单一抖音获客工具 → 全球商业情报 + 智能获客操作系统 |
| **技术架构** | 平台分层设计（Base/Tier1/Tier2/Tier3），AI 成本优化（三级路由），可靠性优先 |
| **业务逻辑** | 结果分层处理：线索/企业/需求/痛点/机会/趋势/竞争 七维 |
| **发展路线图** | 四阶段：① MVP 演示版 → ② 真实 API 接入 → ③ 平台化/多租户 → ④ 操作系统级 |
| **商业模式** | 任务计费 / Token 成本透明 / 企业订阅 |

### 1.3 全家桶搜索模式 (family_bucket)
系统核心搜索模式——**同时搜索所有七个维度**（客户/企业/需求/供应商/合作/机会 + 全家桶），返回最全面的获客情报。这是 MVP 阶段默认推荐模式。

---

## 二、已完成功能清单（v0.1 MVP）

### ✅ 后端 (FastAPI)

| 模块 | 文件 | 完成度 | 说明 |
|------|------|--------|------|
| **API 层** | [routes.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/api/routes.py) | 100% | 7 类 Meta / Keywords / Tasks / Leads / Export 共 13+ 接口 |
| **任务引擎** | [task_engine.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/services/task_engine.py) | 100% | 异步线程执行、进度实时更新、8 项统计自动汇总 |
| **平台注册中心** | [registry.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/platforms/registry.py) | 100% | 装饰器模式注册，按 Tier 分层查询 |
| **平台适配器 (×9)** | tier1_stubs / reddit / google / youtube | 100% | 9 个 Tier 1 平台，**均已实现 Mock 模式**，可完整演示 |
| **关键词扩展** | [keyword_expander.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/services/keyword_expander.py) | 100% | 规则扩展 + LLM 扩展，双层合并去重 |
| **LLM 客户端** | [llm_client.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/services/llm_client.py) | 100% | Mock 模式 + 真实 OpenAI 兼容 API，失败自动降级 Mock |
| **线索分析器** | [lead_analyzer.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/services/lead_analyzer.py) | 100% | **三级路由**（rule/light/advanced），成本最优 |
| **成本引擎** | [cost_engine.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/services/cost_engine.py) | 100% | LLM Token + Platform API 双维度计费，分类汇总 |
| **缓存服务** | [content_cache.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/services/content_cache.py) | 100% | TTLCache，SHA256 key，7 天 TTL |
| **报告生成器** | [report_generator.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/services/report_generator.py) | 100% | Markdown / HTML / Excel 三格式导出 |
| **数据模型 (×4)** | task / lead / platform_result / cost_log | 100% | SQLAlchemy ORM，关系 + 索引完整 |
| **配置/数据库** | config.py / database.py / db_init.py | 100% | pydantic-settings，启动时自动建表 |

### ✅ 前端 (Vue 3 + Vite)

| 模块 | 文件 | 完成度 | 说明 |
|------|------|--------|------|
| **首页 HomeView** | [HomeView.vue](file:///c:/Users/mfk88/Desktop/获客系统/frontend/src/views/HomeView.vue) | 100% | 搜索框 + 示例 chip + 7 种模式 + 9 平台多选 + 扩展关键词预览 + 最近任务表 |
| **详情页 TaskDetailView** | [TaskDetailView.vue](file:///c:/Users/mfk88/Desktop/获客系统/frontend/src/views/TaskDetailView.vue) | 100% | 8 项统计卡片 + 9 平台执行状态卡片 + 扩展关键词 + 线索池表格（多维筛选） |
| **API 封装** | [api.js](file:///c:/Users/mfk88/Desktop/获客系统/frontend/src/api.js) | 100% | Axios 实例 + 所有后端接口方法封装 |
| **全局样式** | [styles.css](file:///c:/Users/mfk88/Desktop/获客系统/frontend/src/styles.css) | 100% | 暗色科技风，响应式 Grid，进度条、tag、chip、table、btn 组件类 |

### ✅ 全链路验证
- 端到端测试脚本 [test_api.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/test_api.py) **运行通过**（exit code 0）
- 测试结果：`日本跨境电商卖家` 任务 → **12 秒完成，380 条内容，347 条高意向，347 条需求，成本 $0.20**
- 浏览器页面加载验证：首页、详情页快照完整，API 请求（search-modes / platforms / tasks）全部 200

---

## 三、启动步骤（给接手人）

### 3.0 前置依赖
```
Python 3.10+      ← 后端运行时
Node.js 18+       ← 前端运行时
（可选）Git       ← 版本控制 & 推送代码
```

### 3.1 后端启动
```bash
cd backend

# Windows PowerShell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 配置（默认 MOCK 模式，无需改任何东西）
copy .env.example .env

# 启动
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
→ 验证：浏览器打开 http://127.0.0.1:8000/health 应该返回 `{"status":"ok","service":"gilos-backend"}`

### 3.2 前端启动
```bash
cd frontend

npm install
npm run dev
```
→ 验证：浏览器打开 http://127.0.0.1:5173/ 出现「全球智能获客 OS」首页

### 3.3 一键跑通测试（可选）
```bash
cd backend
.venv\Scripts\python test_api.py
```
观察输出是否有 `=== FINAL STATS ===` 且各指标数字正常。

---

## 四、配置说明（重要）

### 4.1 两种运行模式

| 模式 | ENABLE_MOCK_MODE | 需要 API Key? | 用途 |
|------|-------------------|----------------|------|
| **Mock 模式 (默认)** | `true` | ❌ 不需要 | 产品演示 / UI 开发 / 后端联调 |
| **真实 API 模式** | `false` | ✅ 需要（OpenAI + 各平台） | 上线 / 真实业务场景 |

### 4.2 切换到真实模式需要填的 Key

编辑 `backend/.env`:

| 变量 | 用途 | 从哪里获取 |
|------|------|-----------|
| `OPENAI_API_KEY` | LLM 调用（关键词扩展 + 内容分析 + 报告） | platform.openai.com 或其他兼容接口 |
| `OPENAI_BASE_URL` | 兼容其他 API 中转 | 默认官方，可换兼容地址 |
| `REDDIT_CLIENT_ID` / `SECRET` | Reddit 搜索 | old.reddit.com/prefs/apps |
| `GOOGLE_API_KEY` + `CSE_ID` | Google Custom Search | console.cloud.google.com + cse.google.com |
| `YOUTUBE_API_KEY` | YouTube Data API v3 | console.cloud.google.com |

**其他平台**（抖音 / 小红书 / B站 / TikTok / Instagram / X）：在各 `*_stubs.py` 中 `is_available()` 目前返回 NOT_SUPPORTED / AUTH_ERROR，因这些平台多为企业级 API 或非公开，需后续逐一申请接入权限后在对应适配器中实现。

---

## 五、代码设计与关键约定

### 5.1 后端分层约定

```
请求
  ↓
routes.py (API 层：参数校验、调用服务、返回 schemas)
  ↓
services/*.py (业务层：无 HTTP，纯逻辑、可测试)
  ↓
platforms/*.py (平台层：统一 adapter 接口，注册到 Registry)
  ↓
models/*.py + database.py (持久化层：SQLAlchemy ORM)
```

**新增平台的标准步骤**：
1. 复制 `reddit_platform.py` 为新文件 `xxx_platform.py`
2. 类继承 `PlatformAdapter`，用 `@PlatformRegistry.register` 装饰
3. 实现 `name / display_name / tier / enabled` 类属性
4. 实现 `is_available()` → 返回可用性三元组
5. 实现 `search(keywords, checkpoint, max_items)` → 返回 `List[UnifiedContent]`
6. 在 `routes.py` 顶部 `import app.platforms.xxx_platform`（触发注册）

### 5.2 关键数据结构

#### UnifiedContent — 统一内容结构
所有平台搜索结果必须转换为 [unified_schema.py](file:///c:/Users/mfk88/Desktop/获客系统/backend/app/platforms/unified_schema.py#L20-L60) 的 `UnifiedContent` dataclass，再传入 LeadAnalyzer。字段说明：

- `platform` / `content_type` / `raw_id` 为必填三元组（platform + raw_id 唯一）
- `title` / `content` 为 AI 分析的核心文本
- `author_company` / `author_location` 直接影响企业线索识别
- `engagement` dict 会被规则分析用到（总量 >1000/10000 加分）

#### Lead 四维评分
在 `lead_analyzer.py:content_to_lead()`:
```python
overall = intent * 0.45 + opportunity * 0.35 + urgency * 0.20
高意向  =  intent >= 70   OR   overall >= 65
```
> 如需调整权重/阈值，改这两行即可。

### 5.3 装饰器模式的平台注册
每个平台适配器类上添加 `@PlatformRegistry.register`，即可自动注册。然后在 `routes.py` 顶部显式 `import` 对应模块（触发装饰器执行）。

### 5.4 任务引擎：threading + asyncio.run
`TaskEngine.start_task()` 创建 daemon 线程，线程内部 `asyncio.run(self.run_task_async(task_id))`，因此服务层全部 async 编写，但 FastAPI 路由层同步调用即可，不会阻塞主线程。

---

## 六、已知问题 & 常见 FAQ

### Q1: 为什么打开前端是空白 / 加载不出来？
**可能原因**：
- 后端没启动（Vite 代理 /api → localhost:8000 超时）
- 使用了 `localhost` 而不是 `127.0.0.1`（部分 Windows DNS 问题）

**解决**：
1. 确认后端在 8000 端口运行（访问 http://127.0.0.1:8000/health）
2. 确认前端用 http://127.0.0.1:5173/ 打开
3. 打开浏览器开发者工具（F12）→ Network 面板，看 `/api/v1/*` 请求的状态码

### Q2: 任务一直 pending / running 不更新？
- 检查后端终端是否有异常 traceback
- 访问 `GET /tasks/{id}` 看 `error_message` 字段
- 可在前端详情页点击「▶ 重新执行」按钮（调 `POST /tasks/{id}/start`）

### Q3: 想换数据库（PostgreSQL / MySQL）？
改 `backend/.env` 的 `DATABASE_URL`：
- PostgreSQL: `postgresql://user:pw@localhost:5432/gilos` （需 `pip install psycopg2-binary`）
- MySQL: `mysql+pymysql://user:pw@localhost:3306/gilos` （需 `pip install pymysql`）

SQLAlchemy 支持无缝切换，业务代码无需修改。

### Q4: 高意向线索太多/太少，怎么调？
改 `lead_analyzer.py` 中：
1. **`_route_model()`** — 控制什么内容走 LLM / 规则
2. **`_rule_based_analyze()`** — 规则关键词、加分权重
3. **`content_to_lead()` 最后** — 高意向阈值 (`intent>=70 OR overall>=65`)
4. 或前端 `filter.high_only` 过滤展示

### Q5: 成本看起来虚高（Mock 模式下）？
Mock 下 `LLMClient.mock_mode` 仍会估算 tokens 并计入 CostLog，这是为了在演示时也能展示成本面板。真实模式下按实际 API usage 返回。

### Q6: 前端导出的 Excel 打不开？
确保后端 `requirements.txt` 中 `openpyxl` 已安装。导出接口是 `StreamingResponse`，Content-Type 正确。

---

## 七、部署指南（生产环境）

### 方案 A：同机部署（简易）

```bash
# 1. 后端：用 gunicorn + uvicorn worker
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000

# 2. 前端：构建静态文件
cd frontend && npm run build
# 将 dist/ 放到 Nginx 根目录
```

**Nginx 配置模板**（反向代理 + 静态文件）：
```nginx
server {
  listen 80;
  server_name your-domain.com;

  # 前端静态
  location / {
    root /var/www/gilos/frontend/dist;
    try_files $uri $uri/ /index.html;
  }

  # 后端 API 代理
  location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 300s;  # 任务可能执行较长
  }

  location /health {
    proxy_pass http://127.0.0.1:8000;
  }
}
```

### 方案 B：Docker 部署（后续可加）
建议补充 `backend/Dockerfile` + `frontend/Dockerfile` + `docker-compose.yml`，使用多阶段构建。MVP 阶段暂未提供。

---

## 八、后续 TODO 与路线图

### 🔴 P0 · 真实数据接入（下一步必做）
1. **接入真实 Reddit API**：在 `reddit_platform.py` 中实现 praw / 直接 HTTP 调用（已有 `is_available` 判断，补全 `search` 即可）
2. **接入真实 Google Custom Search JSON API**：`google_search.py` 补全，每日 100 次免费查询
3. **接入 YouTube Data API v3**：`youtube_platform.py` 已有 Key 变量，补全 search.list
4. **为各 Adapter 加上请求速率限制 + 重试（tenacity）**：`tenacity==9.0.0` 已在 requirements 中，直接用 `@retry` 装饰 search

### 🟠 P1 · 平台扩展（Tier 2）
白皮书规划的第二梯队平台，建议按优先级逐个实现：
- **LinkedIn**（招聘/企业/B2B 关键信号源）
- **Crunchbase**（融资/公司信息）
- **AngelList / Product Hunt**（创业/新品机会）
- **Glassdoor / Indeed**（招聘/人才需求）
- **Amazon / Shopify App Store**（电商卖家信号）

每个都按 Adapter 标准模板开发即可，不用改核心。

### 🟡 P2 · 功能增强
1. **线索去重与合并**：当前跨平台同一条内容（转载）会重复入库。可基于 title 哈希 + content simhash 做去重合并
2. **企业/联系人实体抽取**：从 Lead 内容中抽取公司名、人名、邮箱、电话（可用 LLM function call 或正则）
3. **CRM 导出**：新增 `/tasks/{id}/export.csv` 或对接 Salesforce / HubSpot / 飞书多维表格 API
4. **通知回调**：任务完成时 Webhook 通知 / 邮件 / 企业微信机器人
5. **任务调度**：定时重复任务（比如每周跑一次某个搜索主题，对比增量线索）
6. **数据可视化**：前端已装 `echarts` + `vue-echarts`，可在 TaskDetailView 加入饼图（平台分布/类别分布）+ 趋势折线

### 🟢 P3 · 平台化演进（白皮书路线图 Phase 3）
1. **多租户 / 用户系统**：加 User 模型，FastAPI Users 或 Auth0
2. **团队工作区**：Task/Lead 加 workspace_id 外键
3. **权限与角色**：Admin / Member / Viewer
4. **额度 / 计费系统**：CostEngine 已覆盖基础，在此之上加余额/套餐扣减
5. **自定义 Adapter 插件市场**：Registry 动态加载第三方适配器

### 🔵 P4 · 操作系统级（白皮书 Phase 4，远期）
1. **开放 API + API Key 管理**：让外部系统调用 GILOS 创建任务 / 拉取线索
2. **Webhook 事件流**：lead_created / task_completed 等事件向外推送
3. **自动化工作流引擎**：if 某 lead 高意向 → then 自动发邮件 + 推送 CRM
4. **AI Agent 自主跟进**：基于 Lead 推荐行动，由 Agent 实际执行外呼/邮件

---

## 九、文件索引（关键文件速查）

| 想修改的内容 | 对应文件 |
|-------------|----------|
| 新增 API 接口 | `backend/app/api/routes.py` |
| 新增请求/响应字段 | `backend/app/schemas.py` + 对应 model |
| 加数据库字段 / 新表 | `backend/app/models/*.py` 改完删 data/gilos.db 重启即重建 |
| 调任务执行流程 | `backend/app/services/task_engine.py` |
| 调高意向阈值 / 评分权重 | `backend/app/services/lead_analyzer.py: content_to_lead()` |
| 扩展关键词数量与质量 | `backend/app/services/keyword_expander.py` + LLM system prompt |
| 改成本计算规则 | `backend/app/services/cost_engine.py` (log_llm 里 price_per_m dict) |
| 改报告内容 / 章节顺序 | `backend/app/services/report_generator.py` |
| 接入新平台 | 新建 `backend/app/platforms/xxx_platform.py` → 参照 reddit |
| 改前端首页 UI | `frontend/src/views/HomeView.vue` |
| 改前端详情页 UI | `frontend/src/views/TaskDetailView.vue` |
| 加前端 API 方法 | `frontend/src/api.js` |
| 改全局颜色/组件样式 | `frontend/src/styles.css` |
| 改代理端口（前后端本地联调） | `frontend/vite.config.js` |
| 改环境变量 | `backend/.env` + 变量定义在 `backend/app/config.py` |

---

## 十、联系方式与维护记录

| 日期 | 版本 | 变更内容 | 负责人 |
|------|------|----------|--------|
| 2026-08-21 | v0.1 MVP | 后端 9 平台 + 前端 2 视图 + Mock 全链路跑通 | 初版交接 |
| (待补充) | | | |

> **接手人 checklist**：
> - [ ] 按「三、启动步骤」在本机跑通前后端
> - [ ] 运行 test_api.py 观察输出
> - [ ] 在前端手动创建一个新任务，等待 10~20 秒轮询完成
> - [ ] 打开任务详情 → 导出 Excel，验证下载文件能打开
> - [ ] 阅读本文件「八、后续 TODO」，确定下一步迭代方向

---

**文档结束 · 祝使用顺利！** 🚀
