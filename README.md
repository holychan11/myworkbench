# MyWorkbench · 个人 AI 工作台

一个以**微信为遥控器、Web 为控制台、电脑为执行终端、多 LLM 为大脑**的个人 AI 工作台。

- ✅ 微信遥控电脑（命令沙箱 + 危险操作二次确认）
- ✅ A股盘前智能分析（每交易日 08:30 自动选股并推送）
- ✅ 多用户登录，每人绑定自己的微信、配置自己的 LLM（填 API Key 即用）
- ✅ 可插拔策略与网关，方便扩展

---

## 一、快速开始

### 1. 安装依赖（首次运行一次）

```powershell
cd C:\Users\86189\Desktop\myworkbench
powershell -ExecutionPolicy Bypass -File install.ps1
```

> 后端会安装 `akshare`（A股数据源，体积较大，请耐心等待）。

### 2. 启动

```powershell
powershell -ExecutionPolicy Bypass -File start.ps1
```

启动后：

| 入口 | 地址 |
|---|---|
| Web 控制台 | http://127.0.0.1:5173 |
| API 文档 | http://127.0.0.1:8000/docs |
| 默认管理员 | `admin` / `admin123456` |

### 3. 首次使用四步走

1. **登录/注册**：打开 Web 控制台，用默认管理员登录，或注册一个新账号。
2. **添加模型**：进入「模型管理」→「添加模型」，选择厂商、填 `API Key` 与模型名，点「测试」验证连通。
3. **绑定微信**：进入「微信绑定」→「生成绑定码」，在「模拟微信」面板把绑定码发给机器人（真实环境用手机微信发）。
4. **订阅盘前报告**：进入「A股分析」→ 打开订阅开关、选风险偏好 → 保存。

---

## 二、微信指令

| 指令 | 说明 |
|---|---|
| `/help` | 查看帮助 |
| `/status` | 查看本机状态 |
| `/report` | 立即生成一次盘前选股报告 |
| `/run <命令>` | 执行电脑命令（危险操作需二次确认） |
| 直接发文字 | 由你配置的 LLM 回答 |

危险操作（如 `del`、`rm -rf`、`format`、`shutdown` 等）会先弹「二次确认」，回复 `确认` 执行、`取消` 终止（120 秒内有效）。

---

## 三、微信通道说明（默认本地测试，无需真实微信）

系统采用**可插拔网关**，业务代码零改动即可切换通道：

| 通道 | 配置 | 说明 |
|---|---|---|
| `console`（默认） | `GATEWAY_TYPE=console` | 本地模拟收发，用于开发/体验，Web「微信绑定」页即基于此 |
| `wecom` | `GATEWAY_TYPE=wecom` | 企业微信应用官方 API，合规生产首选（填 WECOM_*） |
| `wcf` | `GATEWAY_TYPE=wcf` | WeChatFerry，Windows 个人号 Hook（需 `pip install wcferry`） |
| `onebot` | `GATEWAY_TYPE=onebot` | QQ（OneBot 11 协议），配合 NapCat/LLOneBot 使用 |

## QQ 通道（OneBot）快速接入

1. 准备一个 QQ 小号，用 **NapCat**（推荐）或 **LLOneBot** 登录。
2. 在 NapCat 配置里：
   - **HTTP 上报** 地址设为 `http://127.0.0.1:8000/onebot/event`
   - 记下它的 **HTTP API 地址**（默认 `http://127.0.0.1:3000`）
3. 复制 `.env.example` 为 `.env`，设置 `GATEWAY_TYPE=onebot`、`ONE_BOT_HTTP_URL=http://127.0.0.1:3000`。
4. 重启 MyWorkbench，在 Web 端「微信绑定」生成绑定码，用手机 QQ 把码私聊发给机器人 QQ 号即完成绑定。

修改 `.env`（复制 `.env.example`）后重启即可。

---

## 四、目录结构

```
myworkbench/
├── backend/            # FastAPI 后端
│   ├── app/
│   │   ├── main.py     # 入口（装配网关/调度器/路由）
│   │   ├── config.py   # 配置（密钥自动生成）
│   │   ├── core/       # 分发器、绑定、审计
│   │   ├── gateway/    # 微信网关（console/wecom/wcf）
│   │   ├── llm/        # 模型管理器 + Key 加密
│   │   ├── executor/   # 命令沙箱 + 二次确认
│   │   ├── stock/      # 可插拔策略 + 8:30 调度
│   │   └── router/     # REST 路由
│   └── requirements.txt
├── frontend/           # React + Vite + Ant Design
├── data/               # SQLite 数据库 + 自动生成的密钥（勿外泄）
├── workspace/          # 命令沙箱工作目录
├── install.ps1         # 一键安装依赖
├── start.ps1           # 一键启动
└── .env.example        # 环境变量模板
```

---

## 五、安全说明

- **API Key 加密存储**：Fernet 对称加密后入库，主密钥保存在 `data/master.key`（请妥善备份，丢失将无法解密已存 Key）。
- **命令沙箱**：白名单放行 + 危险模式二次确认 + 默认拒绝 + 全量审计。
- **多租户隔离**：所有数据按 `user_id` 分区，每个用户独立的模型/会话/报告/日志。
- **防提示词注入**：结构化命令（`/` 开头）不经过 LLM；LLM 仅做兜底问答，不拥有命令执行权限。

> ⚠️ 首次登录后请修改默认管理员密码；对外部署请启用 HTTPS 并改用 `wecom` 官方通道。

---

## 六、选型参考（高 star 开源组件）

| 组件 | 用途 | star |
|---|---|---|
| FastAPI | 后端框架 | 10.2万 |
| Ant Design / Vite | 前端 | 9.9万 / 8.3万 |
| SQLite (SQLAlchemy) | 存储（单机零依赖） | — |
| APScheduler | 8:30 定时调度 | 0.8万 |
| AKShare | A股数据源 | 2.2万 |
| cryptography (Fernet) | API Key 加密 | 0.8万 |
| OpenAI SDK | 多模型统一调用（OpenAI 兼容） | 3.1万 |

可选底座：chatgpt-on-wechat（4.7万★）、LiteLLM（5.7万★）、OpenClaw（38.8万★）。
