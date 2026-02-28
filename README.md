# vllm-server

## run_vllm_server.py

`run_vllm_server.py` 用于一键启动 vLLM 的 OpenAI 兼容服务（等价于执行 `vllm serve ...`），并支持自动扫描本地模型目录，输出模型列表、按名称/序号选择模型启动，方便给 opencode 或其他 OpenAI SDK 客户端提供服务。

### 功能

- 启动 vLLM OpenAI 兼容接口（`/v1/chat/completions` 等）
- 扫描本地模型目录（默认 `/mnt/m/hf_models`）
  - 识别规则：目录下包含 `config.json` 的文件夹会被视为一个模型
  - 支持两层目录：`/mnt/m/hf_models/<name>/config.json` 与 `/mnt/m/hf_models/<org>/<name>/config.json`
- 输出模型列表（带序号/名称/路径）
- 按模型名称或序号选择模型并启动
- 支持常用 vLLM 参数透传：host/port/tp/max_model_len/tool calling 等
- 支持打印最终命令（不启动），用于确认参数拼装结果

### 快速开始

```bash
uv run /root/workspace/python_project/vllm_server/run_vllm_server.py \
  --model /mnt/m/hf_models/Qwen3-4B \
  --host 0.0.0.0 --port 58000
```

启动后，客户端（例如 opencode）一般这样连接：

```bash
export OPENAI_BASE_URL="http://127.0.0.1:58000/v1"
export OPENAI_API_KEY="EMPTY"
```

### 查看本地模型列表

```bash
uv run /root/workspace/python_project/vllm_server/run_vllm_server.py --list-models
```

输出格式：

```
<index>\t<name>\t<path>
```

### 按名称选择模型启动（推荐）

```bash
uv run /root/workspace/python_project/vllm_server/run_vllm_server.py \
  --model-name Qwen3-4B \
  --host 0.0.0.0 --port 58000
```

当使用 `--model-name` / `--model-index` 时，如果你没有显式传 `--served-model-name`，脚本会把它自动设置为所选模型名，便于客户端直接填写 `model=...`。

### 按序号选择模型启动

```bash
uv run /root/workspace/python_project/vllm_server/run_vllm_server.py \
  --model-index 2 \
  --host 0.0.0.0 --port 58000
```

### 自定义扫描目录

```bash
uv run /root/workspace/python_project/vllm_server/run_vllm_server.py \
  --models-dir /mnt/m/hf_models \
  --list-models
```

### 只打印命令（不启动）

```bash
uv run /root/workspace/python_project/vllm_server/run_vllm_server.py --model-name Qwen3-4B --print-cmd
```

### 常用参数

- `--host`：绑定地址（默认 `0.0.0.0`）
- `--port`：端口（默认 `58000`）
- `--tensor-parallel-size`：张量并行（默认 `1`）
- `--max-model-len`：覆盖最大上下文长度（默认 `0` 表示不覆盖）
- `--language-model-only`：跳过多模态组件（更省资源）
- `--enable-tool-calling`：启用工具调用相关参数（自动工具选择 + `qwen3_coder` 解析器）
- `--reasoning-parser`：设置 `--reasoning-parser`（例如 `qwen3`，按你模型/版本需要填写）

### 环境变量（可选）

所有参数均可用环境变量提供默认值：

- `VLLM_MODELS_DIR`：默认扫描目录（对应 `--models-dir`）
- `VLLM_MODEL`：默认模型（对应 `--model`）
- `VLLM_MODEL_NAME`：默认按名称选择（对应 `--model-name`）
- `VLLM_MODEL_INDEX`：默认按序号选择（对应 `--model-index`，1 开始；0 表示不使用）
- `VLLM_HOST` / `VLLM_PORT`：绑定 host/port
- `VLLM_SERVED_MODEL_NAME`：对外暴露模型名
- `VLLM_TP_SIZE`：张量并行大小
- `VLLM_MAX_MODEL_LEN`：最大上下文长度覆盖
- `VLLM_ENABLE_TOOL_CALLING`：启用工具调用（`1/true/yes`）
- `VLLM_REASONING_PARSER`：推理解析器
- `VLLM_LANGUAGE_MODEL_ONLY`：只启用语言模型（`1/true/yes`）

### 给 opencode 的建议配置

- `OPENAI_BASE_URL`：`http://<host>:<port>/v1`
- `OPENAI_API_KEY`：本地 vLLM 通常可填 `EMPTY`
- `model`：使用 `--served-model-name` 的值；如果你用 `--model-name` 启动且未显式指定，默认就是该模型名
