from pathlib import Path
from registry.parser.yaml_parser import load_rules_from_yaml

def test_load_rules_from_yaml():
    rules = load_rules_from_yaml(Path('aws/ec2.yml'))
    assert any(r.rule_id == 'aws.ec2.rightsize' for r in rules)
