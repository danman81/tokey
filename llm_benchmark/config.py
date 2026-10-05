"""Tokey configuration and the small built-in model catalog."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib


@dataclass(frozen=True)
class Model:
    id: str
    name: str
    size: str
    filename: str
    repository: str
    revision: str
    sha256: str
    bytes: int

    @property
    def url(self) -> str:
        return f"https://huggingface.co/{self.repository}/resolve/{self.revision}/{self.filename}"


CATALOG = {
    model.id: model for model in (
        Model("minicpm5-2b", "MiniCPM5", "2B", "MiniCPM5-2B-Q4_K_M.gguf", "openbmb/MiniCPM5-2B-GGUF", "2079a22f3beaa4e306449978533478fe0522f4b3", "ec2d5801640099e97d8d7e8003ad4d81f336e757811f03a26173dddf386602fd", 1561318368),
        Model("spark-x2.5-4b", "Spark X2.5", "4B", "Spark-X2.5-4B-Q4_K_M.gguf", "XHToken/Spark-X2.5-4B-GGUF", "9826e0be84e6e6e8b9668abc91421109a1df1e2d", "adfcfa19a4ed6a5985da8bf565fe15f8e1a7e131d79bae2d19d48d1c40109428", 2600224352),
        Model("qwen3.8-4b", "Qwen3.8", "4B", "Qwen3.8-4B-Q4_K_M.gguf", "empero-ai/Qwen3.8-4B-Distill-GGUF", "391fc7d103e3942a408def3e4f51c2f85d464417", "dec96e8cf2e11b613bb46513dec485377f9ca5a351e71712ee0e244f287c6790", 2783446304),
        Model("ornith-1.5-9b", "Ornith 1.5", "9B", "Ornith-1.5-9B-Q4_K_M.gguf", "ornith-ai/Ornith-1.5-9B-GGUF", "abdd624b12ebf020b767fff532ff44fe552b28c3", "70c112196e0b7023803c9762752e46d29e612a92c83f995bc3ba1ceb07e8fab6", 5780090816),
        Model("qwen3.5-9b", "Qwen3.5", "9B", "Qwen3.5-9B-Q4_K_M.gguf", "unsloth/Qwen3.5-9B-GGUF", "3885219b6810b007914f3a7950a8d1b469d598a5", "03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8", 5680522464),
        Model("lfm2.5-2.6b", "LFM2.5", "2.6B", "LFM2.5-2.6B-Q4_K_M.gguf", "LiquidAI/LFM2.5-2.6B-GGUF", "e7caca5d835a3901a8e0d63e94009429bafafdfc", "02a8b7e17487d326e46d68ce0ba24211e1b80a14c4cd0597fa73c1cd697f52ed", 1674455040),
        Model("jan-v3.5-4b", "Jan v3.5", "4B", "Jan-v3.5-4B-Q4_K_M.gguf", "janhq/Jan-v3.5-4B-gguf", "2b0fcab0066198e78f7c004a0815179fbce13985", "2f5305d93100ad9105eeb47c45ef1af99ba6d568c734fc267b0628b3be41c07a", 2716066656),
        Model("llama-3.2-3b", "Llama 3.2", "3B", "Llama-3.2-3B-Instruct-Q4_K_M.gguf", "bartowski/Llama-3.2-3B-Instruct-GGUF", "5ab33fa94d1d04e903623ae72c95d1696f09f9e8", "6c1a2b41161032677be168d354123594c0e6e67d2b9227c84f296ad037c728ff", 2019377696),
        Model("phi-4-mini", "Phi-4 mini", "3.8B", "microsoft_Phi-4-mini-instruct-Q4_K_M.gguf", "bartowski/microsoft_Phi-4-mini-instruct-GGUF", "7ff82c2aaa4dde30121698a973765f39be5288c0", "01999f17c39cc3074afae5e9c539bc82d45f2dd7faa3917c66cbef76fce8c0c2", 2491874688),
        Model("deepseek-r1-7b", "DeepSeek R1", "7B", "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf", "unsloth/DeepSeek-R1-Distill-Qwen-7B-GGUF", "097680e4eed7a83b3df6b0bb5e5134099cadf1b0", "78272d8d32084548bd450394a560eb2d70de8232ab96a725769b1f9171235c1c", 4683073248),
    )
}


@dataclass(frozen=True)
class Config:
    system_name: str
    runners: tuple[Model, ...]


def config_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "tokey" / "config.toml"


def default_config_path() -> Path:
    return Path(__file__).with_name("default-config.toml")


def load_config(path: Path | None = None) -> Config:
    source = path or config_path()
    if not source.exists():
        source = default_config_path()
    data = tomllib.loads(source.read_text(encoding="utf-8"))
    system_name = data.get("system_name", "")
    runner_ids = data.get("runners", [])
    if not isinstance(system_name, str):
        raise ValueError("system_name must be text")
    if not isinstance(runner_ids, list) or not all(isinstance(item, str) for item in runner_ids):
        raise ValueError("runners must be a list of model IDs")
    unknown = [item for item in runner_ids if item not in CATALOG]
    if unknown:
        raise ValueError("Unknown runner: " + ", ".join(unknown))
    return Config(system_name, tuple(CATALOG[item] for item in runner_ids))
