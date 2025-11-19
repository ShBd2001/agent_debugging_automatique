# config.py
import json
from pathlib import Path
from typing import Optional, Dict, Any

CONFIG_FILE = Path("config.json")


def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {
            "python_path": "venv\\Scripts\\python.exe",
            "last_script": ""
        }
    with CONFIG_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: Dict[str, Any]) -> None:
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
