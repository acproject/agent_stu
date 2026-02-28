import argparse
import os
import shlex
import subprocess
from pathlib import Path


def discover_local_models(models_dir: str) -> list[tuple[str, str]]:
    base = Path(models_dir)
    if not base.exists() or not base.is_dir():
        return []

    results: dict[str, str] = {}

    for p in base.iterdir():
        if not p.is_dir():
            continue
        config_path = p / "config.json"
        if config_path.is_file():
            results[p.name] = str(p)

    for config_path in base.glob("*/*/config.json"):
        model_dir = config_path.parent
        name = model_dir.relative_to(base).as_posix()
        results.setdefault(name, str(model_dir))

    return sorted(results.items(), key=lambda x: x[0].lower())


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run vLLM OpenAI-compatible server (vllm serve) for local models.",
    )
    parser.add_argument(
        "--models-dir",
        default=os.getenv("VLLM_MODELS_DIR", "/mnt/m/hf_models"),
        help="Directory to scan for local models. Env: VLLM_MODELS_DIR",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List detected local models and exit.",
    )
    parser.add_argument(
        "--model-name",
        default=os.getenv("VLLM_MODEL_NAME", ""),
        help="Select a detected model by name from --models-dir. Env: VLLM_MODEL_NAME",
    )
    parser.add_argument(
        "--model-index",
        type=int,
        default=int(os.getenv("VLLM_MODEL_INDEX", "0")),
        help="Select a detected model by 1-based index from --models-dir. Env: VLLM_MODEL_INDEX",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("VLLM_MODEL", "/mnt/m/hf_models/Qwen3-4B"),
        help="HF model name or local model directory. Env: VLLM_MODEL",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("VLLM_HOST", "0.0.0.0"),
        help="Bind host. Env: VLLM_HOST",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("VLLM_PORT", "58000")),
        help="Bind port. Env: VLLM_PORT",
    )
    parser.add_argument(
        "--served-model-name",
        default=os.getenv("VLLM_SERVED_MODEL_NAME", ""),
        help="Expose this model name to clients. Env: VLLM_SERVED_MODEL_NAME",
    )
    parser.add_argument(
        "--max-model-len",
        type=int,
        default=int(os.getenv("VLLM_MAX_MODEL_LEN", "0")),
        help="Override max context length. Env: VLLM_MAX_MODEL_LEN (0 disables)",
    )
    parser.add_argument(
        "--tensor-parallel-size",
        type=int,
        default=int(os.getenv("VLLM_TP_SIZE", "1")),
        help="Tensor parallel size. Env: VLLM_TP_SIZE",
    )
    parser.add_argument(
        "--enable-tool-calling",
        action="store_true",
        default=os.getenv("VLLM_ENABLE_TOOL_CALLING", "").lower() in {"1", "true", "yes"},
        help="Enable auto tool choice & tool call parser (qwen3_coder). Env: VLLM_ENABLE_TOOL_CALLING",
    )
    parser.add_argument(
        "--reasoning-parser",
        default=os.getenv("VLLM_REASONING_PARSER", ""),
        help="Set --reasoning-parser (e.g. qwen3). Env: VLLM_REASONING_PARSER",
    )
    parser.add_argument(
        "--language-model-only",
        action="store_true",
        default=os.getenv("VLLM_LANGUAGE_MODEL_ONLY", "").lower() in {"1", "true", "yes"},
        help="Skip multimodal profiling and vision components. Env: VLLM_LANGUAGE_MODEL_ONLY",
    )
    parser.add_argument(
        "--print-cmd",
        action="store_true",
        help="Print the resolved command and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = build_args()
    detected_models = discover_local_models(args.models_dir)

    if args.list_models:
        for i, (name, path) in enumerate(detected_models, start=1):
            print(f"{i}\t{name}\t{path}")
        return 0

    if args.model_name:
        mapping = {name: path for name, path in detected_models}
        if args.model_name not in mapping:
            available = ", ".join(name for name, _ in detected_models)
            raise SystemExit(
                f"Model not found in {args.models_dir}: {args.model_name}\n"
                f"Available: {available}"
            )
        args.model = mapping[args.model_name]
        if not args.served_model_name:
            args.served_model_name = args.model_name

    if args.model_index:
        if args.model_index < 1 or args.model_index > len(detected_models):
            raise SystemExit(
                f"Invalid --model-index {args.model_index}; "
                f"expected 1..{len(detected_models)}"
            )
        args.model = detected_models[args.model_index - 1][1]
        if not args.served_model_name:
            args.served_model_name = detected_models[args.model_index - 1][0]

    cmd: list[str] = [
        "vllm",
        "serve",
        args.model,
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--tensor-parallel-size",
        str(args.tensor_parallel_size),
    ]

    if args.served_model_name:
        cmd += ["--served-model-name", args.served_model_name]

    if args.max_model_len and args.max_model_len > 0:
        cmd += ["--max-model-len", str(args.max_model_len)]

    if args.reasoning_parser:
        cmd += ["--reasoning-parser", args.reasoning_parser]

    if args.language_model_only:
        cmd += ["--language-model-only"]

    if args.enable_tool_calling:
        cmd += ["--enable-auto-tool-choice", "--tool-call-parser", "qwen3_coder"]

    if args.print_cmd:
        print(shlex.join(cmd))
        return 0

    env = os.environ.copy()
    env.setdefault("OPENAI_API_KEY", "EMPTY")
    return subprocess.call(cmd, env=env)


if __name__ == "__main__":
    raise SystemExit(main())
