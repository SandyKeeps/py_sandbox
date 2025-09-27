import yaml
from pathlib import Path
from typing import Optional, List, Any, Dict


class AnalyzerConfig:

    # Baseline defaults live in ONE place to avoid divergence.
    _DEFAULTS = {
        "allowed_imports": [],
        "blacklist_imports": ["os", "sys", "socket"],
        "allowed_functions": [],
        "blacklisted_functions": ["open"],
        "allowed_statements": [],
        "blacklist_statements": [],
        "allowed_complexity": 4,
        "no_exec": False,
    }

    def __init__(
        self,
        config_path: Optional[str] = None,
        *,
        allowed_imports: Optional[List[str]] = None,
        blacklist_imports: Optional[List[str]] = None,
        allowed_functions: Optional[List[str]] = None,
        blacklisted_functions: Optional[List[str]] = None,
        allowed_statements: Optional[List[str]] = None,
        blacklist_statements: Optional[List[str]] = None,
        allowed_complexity: Optional[int] = None,
        no_exec: Optional[bool] = None,
    ):
        self.config_path = config_path

        # Start from fresh copies of defaults
        self._assign_defaults()

        # Apply constructor-level overrides (if provided)
        if allowed_imports is not None:
            self.allowed_imports = list(allowed_imports)
        if blacklist_imports is not None:
            self.blacklist_imports = list(blacklist_imports)
        if allowed_functions is not None:
            self.allowed_functions = list(allowed_functions)
        if blacklisted_functions is not None:
            self.blacklisted_functions = list(blacklisted_functions)
        if allowed_statements is not None:
            self.allowed_statements = list(allowed_statements)
        if blacklist_statements is not None:
            self.blacklist_statements = list(blacklist_statements)
        if allowed_complexity is not None:
            self.allowed_complexity = int(allowed_complexity)
        if no_exec is not None:
            self.no_exec = bool(no_exec)

        # Apply YAML overrides last (highest precedence if provided)
        if self.config_path:
            self._load_from_yaml(self.config_path)

        # Final derived field
        self.blacklist = (
            list(self.blacklist_imports)
            + list(self.blacklist_statements)
            + list(self.blacklisted_functions)
        )

    # ----------------------- internals -----------------------

    def _assign_defaults(self) -> None:
        """Assign fresh copies of the baseline defaults."""
        self.allowed_imports = list(self._DEFAULTS["allowed_imports"])
        self.blacklist_imports = list(self._DEFAULTS["blacklist_imports"])
        self.allowed_functions = list(self._DEFAULTS["allowed_functions"])
        self.blacklisted_functions = list(self._DEFAULTS["blacklisted_functions"])
        self.allowed_statements = list(self._DEFAULTS["allowed_statements"])
        self.blacklist_statements = list(self._DEFAULTS["blacklist_statements"])
        self.allowed_complexity = int(self._DEFAULTS["allowed_complexity"])
        self.no_exec = bool(self._DEFAULTS["no_exec"])

    def _load_from_yaml(self, config_file_path: str) -> None:
        path = Path(config_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        if path.suffix.lower() not in {".yaml", ".yml"}:
            raise ValueError(f"Config must be YAML (.yaml/.yml), got: {path.suffix}")

        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}

        if not isinstance(data, dict):
            raise ValueError("Top-level YAML must be a mapping/object")

        self._assign_attributes(data)

    def _assign_attributes(self, config_data: Dict[str, Any]) -> None:
        """
        Shallow-assign known keys from YAML into the instance.
        Unknown keys are ignored (safer for forward-compat).
        """
        # Only allow known keys
        known_keys = {
            "allowed_imports",
            "blacklist_imports",
            "allowed_functions",
            "blacklisted_functions",
            "allowed_statements",
            "blacklist_statements",
            "allowed_complexity",
            "no_exec",
        }

        for key, value in config_data.items():
            if key not in known_keys:
                # ignore unknown keys silently; or log if you prefer
                continue

            # Normalize/validate types lightly
            if key in {
                "allowed_imports",
                "blacklist_imports",
                "allowed_functions",
                "blacklisted_functions",
                "allowed_statements",
                "blacklist_statements",
            }:
                if value is None:
                    value = []
                elif not isinstance(value, list):
                    raise ValueError(f"YAML: '{key}' must be a list")
                setattr(self, key, list(value))

            elif key == "allowed_complexity":
                if value is None:
                    continue
                if not isinstance(value, int):
                    raise ValueError("YAML: 'allowed_complexity' must be an int")
                self.allowed_complexity = int(value)

            elif key == "no_exec":
                if value is None:
                    continue
                if not isinstance(value, bool):
                    raise ValueError("YAML: 'no_exec' must be a bool")
                self.no_exec = bool(value)
