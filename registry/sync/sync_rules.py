from pathlib import Path
from typing import List
from registry.parser.yaml_parser import load_rules_from_yaml
from registry.sync.db import upsert_rules

RULE_DIRS: List[Path] = [Path('aws'), Path('ncp')]


def discover_yaml_files() -> List[Path]:
    files: List[Path] = []
    for base in RULE_DIRS:
        if base.exists():
            files.extend(sorted(base.glob('*.yml')))
            files.extend(sorted(base.glob('*.yaml')))
    return files


def main() -> None:
    files = discover_yaml_files()
    all_rules = []
    for p in files:
        rules = load_rules_from_yaml(p)
        all_rules.extend(rules)
    upsert_rules(all_rules)
    print(f"Synced {len(all_rules)} rules from {len(files)} files.")


if __name__ == '__main__':
    main()
