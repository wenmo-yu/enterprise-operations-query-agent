# 企业经营智能问数 Agent

面向企业经营分析的语义数据 Agent。它将自然语言问题转为受控的只读 SQL，并通过短期记忆维护指标、时间、分析维度和筛选条件，支持连续追问。

![企业经营智能问数 Agent 控制台预览](docs/images/insight-query-console.png)

## 核心能力

- **连续上下文问数**：`StructuredQueryState` 显式保存指标、时间、维度、筛选、排序与 Top-N；后续追问先补全完整分析意图，再进入检索链路。
- **Dense Retrieval + Reranker**：Qdrant 负责语义候选召回，Cross-Encoder Reranker 负责精排，动态 Top-K 控制上下文规模。
- **Elasticsearch Value Retrieval**：检索真实字段值，辅助解析区域、客户类型、渠道等筛选条件。
- **Schema Dependency Expansion**：自动补齐指标依赖字段、时间字段和 Join Key。
- **受限 SQL 闭环**：仅允许单条 `SELECT`/`WITH` 查询；生成后预检查，最多一次修正后再次检查；执行层有超时和 1000 行上限。
- **可观察执行**：SSE 推送检索、生成、校验、修正与执行状态。

## 系统架构

```text
React Console ── session_id ──> FastAPI / SSE
                                  │
                    Memory + StructuredQueryState
                                  │
Query expansion ─> Qdrant Dense ─> Cross-Encoder Reranker ─┐
ES value retrieval ─────────────────────────────────────────┼─> Schema expansion ─> Safe SQL loop
                                                             ┘
```

## Evaluation

评测设置与可复现口径见 [docs/evaluation.md](docs/evaluation.md)。在 BIRD Mini-Dev 的 500 条样本上，执行准确率从 Raw Schema baseline 的 **57.4%** 提升至 Schema RAG 的 **74.2%**，加入一次受限 Self-Correction 后为 **77.0%**；Schema Recall@5 为 **93.6%**。

## Demo

- 统计本月各区域收入与客户数，并按收入从高到低排序。
- 为什么某区域业务量增长，但利润率下降？
- 分析本月客户流失率明显上升的可能原因，并列出待验证指标。

示例元数据使用零售样例数仓，目的是便于本地启动；核心检索、状态管理和 SQL 安全链路不依赖特定行业。

## Quick Start

需要 Python 3.14+、[uv](https://docs.astral.sh/uv/)、Node 22+、pnpm 10+ 和 Docker。

```bash
copy .env.example .env
docker compose -f docker/docker-compose.yaml up -d
uv sync
uv run python app/scripts/build_meta_knowledge.py
uv run fastapi dev main.py
```

另开一个终端启动前端：

```bash
pnpm --dir frontend install
pnpm --dir frontend dev
```

在 `.env` 配置 `LLM_API_KEY` 后访问 `http://localhost:5173`。首次启动还需准备 `BAAI/bge-reranker-v2-m3` 模型文件，Reranker 服务默认运行在 `http://localhost:8082/rerank`。

## Safety

- Docker 示例数仓账户仅被授予 `SELECT`；已有数据卷需要管理员撤销旧写权限后重新授权。
- SQL 解析器拒绝多语句、DML/DDL 和文件读写表达式。
- 查询有执行超时和返回行数限制；生产环境仍应使用独立的最小权限只读账户。

## Project Structure

```text
app/agent/          # LangGraph 工作流与节点
app/services/       # 会话状态与查询编排
app/repositories/   # MySQL、Qdrant、Elasticsearch 数据访问
conf/               # 应用配置与示例元数据
frontend/           # React SSE 问数界面
docs/               # 架构预览与评测说明
```

## 开发检查

```bash
uv run ruff check .
python -m unittest discover -s tests -v
pnpm --dir frontend build
```

## Acknowledgements

本项目的早期智能问数工程原型参考了 [AI Agents From Zero](https://didilili.github.io/ai-agents-from-zero)。本项目已围绕企业经营分析场景，独立重构了产品定位、会话状态管理、检索精排、Schema 依赖扩展、SQL 安全闭环与交互文案。

## License

MIT，详见 [LICENSE](LICENSE)。
