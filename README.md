# offline-ai-lite · 离线 AI 聊天（轻量版）

本地离线大语言模型聊天客户端 + 中文语音朗读。单文件 exe，连接本机已安装的 Ollama，**无需联网即可使用**。

本项目是 [`offline-ai`](https://github.com/Make-coder-567/offline-ai) 的**轻量发行变体**：去掉了约 17GB 的模型权重与便携 Ollama，体积降到约 470MB（仅含运行时 + 语音/TTS 模型），更适合直接分发与下载。

## 功能特性

- **桌面聊天 UI**（PySide6）：多模型切换、多轮对话、Markdown 渲染、会话持久化、停止生成、参数面板。
- **离线语音**：AI 回答可用 **piper 中文 TTS** 朗读（模型随 exe 内置，无网可用）；麦克风输入用 **faster-whisper** 本地转写。
- **文档理解（RAG）**：拖入 PDF / Word / Excel / PPT / ePub / 图片即可问答；扫描件与图片走本地 OCR；长文档自动入库检索并带 `[1][2]` 引用。
- **深度思考**：草稿 → 自检 → 定稿（三轮本地推理，质量换时间）。
- **多会话 / 长期记忆 / 定时任务**。
- **MCP 桥接**：把本地模型能力接入 WorkBuddy 等外部智能体（22 个工具）。
- **OpenAI 兼容网关**：任意 OpenAI 客户端把 `base_url` 指向本机即可直连。
- **多模态**：拖拽 / Ctrl+V 粘贴图片，配合视觉模型理解图像。

> 语音朗读已在源码中修复为「后台线程合成 + 播放」，不再卡死界面；espeak 音素数据已随包打包，确保冻结态真正出声。

## 快速开始（使用预编译 exe）

1. 本机安装并启动 [Ollama](https://ollama.com)（桌面版会自动常驻，或 `ollama serve`），并拉取一个模型：
   ```bash
   ollama pull gemma3:4b
   ```
2. 到本仓库 **Releases** 下载 `offline_chat_lite.exe`，双击运行。
3. 首次使用会自动 `ollama pull` 默认模型（需联网一次）；之后完全离线。

> 轻量版不含 `model_assets/`，文档向量检索与语音按钮在缺失对应模型时会自动降级 / 隐藏。

## 从源码运行

需要 Python 3.10+（仅开发态）。

```bash
git clone https://github.com/Make-coder-567/offline-ai-lite.git
cd offline-ai-lite
pip install -r requirements.txt
python chatui/chat_app.py          # 需本机 Ollama 在跑
```

## 构建轻量 exe

```bash
cd chatui
set OFFLINE_LITE=1                 # 轻量版开关（不含模型与便携 Ollama）
set OFFLINE_KEEP_ASSETS=1          # 保留语音 / RAG 向量模型，使朗读与 OCR 可用
python -m PyInstaller --noconfirm --clean offline_chat.spec
```

产物为单文件 `dist/offline_chat_lite.exe`。若去掉 `OFFLINE_KEEP_ASSETS=1`，体积更小，但语音朗读与文档向量检索将不可用（按钮自动隐藏）。

> 构建需要较大内存与临时空间；若旧包正在运行会占住目录导致失败，先关闭程序。

## 目录结构

| 路径 | 说明 |
|------|------|
| `chatui/` | 离线聊天 UI（`chat_app.py`）、多会话（`sessions.py`）、语音（`voice.py`）、打包配置与运维工具 |
| `server/` | MCP server 与能力模块：`docparse` / `rag` / `embed` / `audit` / `tools` / `agent` / `memory` / `scheduler` / `gateway` / `paths` |
| `bridge/` | 文件桥接协议（agent 任务 JSON） |
| `config.yaml` | 运行时配置（模型、路由等） |
| `tests/` | 回归冒烟测试（无需 Ollama 即可跑 UI 部分） |

## 回归测试

```bash
python tests/smoke_test.py          # 全部（UI 部分使用 offscreen，无需 Ollama）
python tests/smoke_test.py --no-ui  # 只跑后端
```

## 许可证

本项目以 **MIT** 许可证开源（详见 `LICENSE`）。

模型权重（Qwen / Gemma / Llama / DeepSeek 等）遵循各自上游许可证，本仓库不重新分发任何权重文件（`chatui/gguf_models`、`model_assets` 均已加入 `.gitignore`）。MIT 仅覆盖本仓库代码，打包进安装包的模型仍有各自的商用条款。
