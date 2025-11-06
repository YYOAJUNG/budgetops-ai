import yaml
from pathlib import Path
from typing import List
from registry.models.rule import RuleMetadata

def load_rules_from_yaml(path: Path) -> List[RuleMetadata]:
    with path.open('r', encoding='utf-8') as f:
        raw = yaml.safe_load(f) or {}
    rules = []
    items = raw.get('rules', []) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise ValueError(f"Invalid YAML format in {path}: 'rules' should be a list")
    for item in items:
        rules.append(RuleMetadata(**item))
    return rules
