import tomllib
from typing import List
from appdirs import user_config_dir
from pathlib import Path
import yaml
from dataclasses import dataclass


@dataclass
class Models:
    model_name: str
    max_tokens: int


GROQ_MODELS: List[Models] = [
    Models(
        model_name="llama-3.3-70b-versatile",
        max_tokens=8000
    )
    # Models(
    #     model_name="llama-3.1-8b-instruct",
    #     max_tokens=8000
    # )
]


HUGGING_FACE_MODELS: List[Models] = [
    Models(
        model_name="Qwen/Qwen3-32B",
        max_tokens=32760
    ),
    # Models(
    #     model_name="Qwen/QwQ-32B-Preview",
    #     max_tokens=16000
    # ),
    # Models(
    #     model_name="llama-3.1-8b-instruct",
    #     max_tokens=8000
    # )
]

OLLAMA_MODELS: List[Models] = [
    Models(
        model_name="deepseek-r1:1.5b",
        max_tokens=8000
    ),
    Models(
        model_name="deepseek-r1:7b",
        max_tokens=8000
    ),
    Models(
        model_name="deepseek-r1:8b",
        max_tokens=8000
    ),
    Models(
        model_name="deepseek-r1:14b",
        max_tokens=8000
    ),
    Models(
        model_name="phi4",
        max_tokens=8000
    ),
]

GEMINI_MODELS: List[Models] = [
    Models(
        model_name="gemini-2.0-flash",
        max_tokens=8000
    )
]


DEFAULT_CONFIG = {
    'interface': 'huggingface',
    # 'max_tokens': 32760,
    'temperature': 1,
    'target_branch': 'master',
    'assignee_id': 10437754,
    # 'model': HUGGING_FACE_MODELS[0].model_name,
}


class ConfigManager:
    def __init__(
        self,
        app_name: str,
        app_author: str = None,
        config_filename: str = "config.yaml"
    ):

        # Local config path
        self.local_config_path = Path.cwd() / ".gai.yaml"

        # Global config path
        self.config_dir = Path(user_config_dir(app_name, app_author))
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # eg: /home/username/.config/gai/config.yaml
        self.config_path = self.config_dir / config_filename
        self.config = self.load_config()

    def load_config(self):
        # Try to load local config first
        if self.local_config_path.exists():
            with self.local_config_path.open('r') as f:
                local_config = yaml.safe_load(f)
                if local_config is not None:
                    return local_config

        # Fall back to global config
        if not self.config_path.exists():
            self.create_default_config()

        with self.config_path.open('r') as f:
            return yaml.safe_load(f)

    def create_default_config(self):
        default_config = DEFAULT_CONFIG.copy()

        with self.config_path.open('w') as f:
            yaml.dump(default_config, f)
        print(f"Created default config at {self.config_path}")

    def save_config(self):
        config_path = self.local_config_path if self.local_config_path.exists() else self.config_path
        with config_path.open('w') as f:
            yaml.dump(self.config, f)
        print(f"Saved config to {config_path}")

    def update_config(self, key, value):
        self.config[key] = value
        self.save_config()

    def get_config(self, key, default=None):
        return self.config.get(key, default)

    def init_local_config(self):
        """Initialize a local configuration file in the current directory."""
        if self.local_config_path.exists():
            print(f"Local config already exists at {self.local_config_path}")
            return False

        # Create local config with current settings
        with self.local_config_path.open('w') as f:
            yaml.dump(self.config, f)
        print(f"Created local config at {self.local_config_path}")
        return True


def get_app_name():
    try:
        with open('pyproject.toml', 'rb') as f:
            pyproject = tomllib.load(f)
        return pyproject['project']['name']
    except (FileNotFoundError, KeyError):
        return "gai-tool"


if __name__ == "__main__":
    config_manager = ConfigManager(get_app_name())
    target_branch = config_manager.get_config('target_branch')
    print(f"Target branch: {target_branch}")
