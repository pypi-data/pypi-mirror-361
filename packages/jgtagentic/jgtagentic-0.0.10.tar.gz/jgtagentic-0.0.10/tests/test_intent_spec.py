from jgtagentic.intent_spec import IntentSpecParser
import json
import tempfile
import os
import yaml


def test_intent_spec_parser_load():
    spec_data = {
        "strategy_intent": "Demo",
        "signals": [{"name": "dragon_breakout"}]
    }
    with tempfile.NamedTemporaryFile('w+', delete=False) as f:
        yaml.dump(spec_data, f)
        path = f.name
    parser = IntentSpecParser()
    loaded = parser.load(path)
    os.unlink(path)
    assert loaded["strategy_intent"] == "Demo"
    assert loaded["signals"][0]["name"] == "dragon_breakout"
    assert parser.signals(loaded)[0]["name"] == "dragon_breakout"

