# src/looplm/chat/prompts.py

import json
from pathlib import Path
from typing import Dict

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant"""


class PromptsManager:
    """Manages system prompts configuration"""

    def __init__(self):
        """Initialize prompts manager"""
        self.config_dir = Path.home() / ".looplm" / "prompts"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_file = self.config_dir / "prompts.json"

        # Shipped prompts directory
        self.shipped_prompts_dir = Path(__file__).parent.parent / "prompts"

        # Create default prompts if file doesn't exist
        if not self.prompts_file.exists():
            self.save_prompts(
                {
                    "default": DEFAULT_SYSTEM_PROMPT,
                }
            )

    def load_prompts(self) -> Dict[str, str]:
        """Load saved prompts"""
        try:
            if self.prompts_file.exists():
                return json.loads(self.prompts_file.read_text())
            return {"default": DEFAULT_SYSTEM_PROMPT}
        except Exception:
            return {"default": DEFAULT_SYSTEM_PROMPT}

    def save_prompts(self, prompts: Dict[str, str]):
        """Save prompts to file"""
        self.prompts_file.write_text(json.dumps(prompts, indent=2))

    def get_prompt(self, name: str = "default") -> str:
        """Get a specific prompt"""
        # First check if it's a special shipped prompt
        if name == "compact":
            return self.get_compact_prompt()

        prompts = self.load_prompts()
        return prompts.get(name, DEFAULT_SYSTEM_PROMPT)

    def get_compact_prompt(self) -> str:
        """Get the compact prompt from shipped prompts"""
        compact_file = self.shipped_prompts_dir / "compact.txt"
        if compact_file.exists():
            try:
                return compact_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass

        # Fallback if file doesn't exist or can't be read
        return "Please provide a comprehensive summary of this conversation."

    def save_prompt(self, name: str, prompt: str):
        """Save a new prompt"""
        prompts = self.load_prompts()
        prompts[name] = prompt
        self.save_prompts(prompts)

    def delete_prompt(self, name: str) -> bool:
        """Delete a saved prompt"""
        if name == "default":
            return False

        prompts = self.load_prompts()
        if name in prompts:
            del prompts[name]
            self.save_prompts(prompts)
            return True
        return False

    def list_prompts(self) -> Dict[str, str]:
        """Get all saved prompts"""
        return self.load_prompts()

    @staticmethod
    def resolve_system_prompt(
        system_prompt: str, system_prompt_file: str = None
    ) -> str:
        """Resolve system prompt from either text or file

        Args:
            system_prompt: Direct system prompt text
            system_prompt_file: Path to file containing system prompt

        Returns:
            System prompt text

        Raises:
            ValueError: If both or neither arguments are provided
            FileNotFoundError: If system_prompt_file doesn't exist
            IOError: If system_prompt_file cannot be read
        """
        if system_prompt and system_prompt_file:
            raise ValueError(
                "Cannot specify both --system-prompt and --system-prompt-file"
            )

        if not system_prompt and not system_prompt_file:
            raise ValueError(
                "Must specify either --system-prompt or --system-prompt-file"
            )

        if system_prompt_file:
            try:
                file_path = Path(system_prompt_file)
                if not file_path.exists():
                    raise FileNotFoundError(
                        f"System prompt file not found: {system_prompt_file}"
                    )

                content = file_path.read_text(encoding="utf-8").strip()
                if not content:
                    raise ValueError(
                        f"System prompt file is empty: {system_prompt_file}"
                    )

                return content
            except Exception as e:
                if isinstance(e, (FileNotFoundError, ValueError)):
                    raise
                raise IOError(
                    f"Failed to read system prompt file: {system_prompt_file}"
                ) from e

        return system_prompt.strip()
