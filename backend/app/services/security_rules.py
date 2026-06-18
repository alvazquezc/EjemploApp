from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from app.schemas import SecurityRule


BACKEND_RULES_PATH = Path(__file__).resolve().parents[2] / "security_rules.yaml"
CONFIG_RULES_PATH = Path(__file__).resolve().parents[3] / "config" / "security_rules.yaml"


def _clean_yaml_value(value: str) -> str:
    cleaned = value.strip()
    if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
        return cleaned[1:-1]
    return cleaned


def _parse_rule_pair(target: dict[str, str], content: str) -> None:
    if ":" not in content:
        return
    key, value = content.split(":", 1)
    target[key.strip()] = _clean_yaml_value(value)


def _parse_rules_yaml(raw_yaml: str) -> list[dict[str, str]]:
    rules: list[dict[str, str]] = []
    current: Optional[dict[str, str]] = None
    in_rules = False

    for raw_line in raw_yaml.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "rules:":
            in_rules = True
            continue
        if not in_rules:
            continue
        if stripped.startswith("- "):
            if current:
                rules.append(current)
            current = {}
            _parse_rule_pair(current, stripped[2:])
            continue
        if current is not None:
            _parse_rule_pair(current, stripped)

    if current:
        rules.append(current)

    return rules


@lru_cache(maxsize=None)
def load_security_rules() -> list[SecurityRule]:
    rules_path = CONFIG_RULES_PATH if CONFIG_RULES_PATH.exists() else BACKEND_RULES_PATH
    with rules_path.open("r", encoding="utf-8") as rules_file:
        raw_rules = _parse_rules_yaml(rules_file.read())

    return [SecurityRule(**rule) for rule in raw_rules]
