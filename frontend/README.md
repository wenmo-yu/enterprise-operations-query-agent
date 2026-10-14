<!--
  前端项目说明文档
  记录启动方式、代理配置和部署时的环境变量
-->

# Enterprise Operations Analytics Console

React + Vite + Tailwind CSS 的企业经营分析界面。它保存浏览器会话 ID，并将后端返回的指标、时间、维度和筛选状态可视化，支持连续追问。

## 启动

```bash
cd frontend
pnpm install
pnpm dev
```

默认开发代理会把 `/api` 转发到 `http://127.0.0.1:8000`，对应后端的 `POST /api/query` SSE 接口。

如需修改后端地址：

```bash
cp .env.example .env
```

然后调整：

```bash
VITE_DEV_PROXY_TARGET=http://127.0.0.1:8000
```

如果前端与后端不在同一域部署，可设置：

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```
