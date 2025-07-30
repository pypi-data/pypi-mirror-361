# 🧠🌸🔮 Test suite for agentic_entry_orchestrator and modular agents
import os
import sys
import json
import tempfile
import shutil
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from jgtagentic.entry_script_gen import EntryScriptGen
from jgtagentic.fdbscan_agent import FDBScanAgent
from jgtagentic.campaign_env import CampaignEnv
from jgtagentic.agentic_decider import AgenticDecider

# --- Fixtures ---
@pytest.fixture
def sample_signal():
    return {
        'instrument': 'GBP/USD',
        'timeframe': 'm5',
        'tlid_id': '250519140525',
        'entry_script_path': None,
        'entry_script': '# test script',
    }

@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

# --- Tests ---
def test_entry_script_gen_bash(sample_signal):
    gen = EntryScriptGen()
    script = gen.generate_bash_entry(sample_signal)
    assert '#!/bin/bash' in script
    assert 'GBP/USD' in script

def test_campaign_env_prepare(sample_signal):
    env = CampaignEnv()
    result = env.prepare_env(sample_signal)
    assert 'Prepared environment' in result

def test_fdbscan_agent_scan_timeframe(capsys):
    agent = FDBScanAgent()
    agent.scan_timeframe('m5')
    out = capsys.readouterr().out
    assert 'Would scan: m5' in out

def test_fdbscan_agent_real_flag_without_scanner(monkeypatch, capsys):
    monkeypatch.setattr('jgtagentic.fdbscan_agent._FDBSCAN_AVAILABLE', False)
    agent = FDBScanAgent(real=True)
    agent.scan_timeframe('m5')
    out = capsys.readouterr().out
    assert 'Real mode requested' in out
    assert 'Would scan: m5' in out

def test_fdbscan_agent_real_flag_with_scanner(monkeypatch, capsys):
    calls = []

    def dummy_main():
        print('real scan executed')
        calls.append(True)

    monkeypatch.setattr('jgtagentic.fdbscan_agent._FDBSCAN_AVAILABLE', True)
    monkeypatch.setattr('jgtagentic.fdbscan_agent.fdb_scanner_2408', type('D', (), {'main': staticmethod(dummy_main)}))
    agent = FDBScanAgent(real=True)
    agent.scan_timeframe('m5', 'EUR/USD')
    out = capsys.readouterr().out
    assert 'real scan executed' in out
    assert calls

def test_agentic_decider_decide(sample_signal):
    decider = AgenticDecider()
    result = decider.decide(sample_signal)
    assert 'Decision for' in result

# --- Integration: Orchestrator spiral ---
def test_orchestrator_spiral(tmp_path, sample_signal):
    # Simulate the spiral: env, script, scan, decide
    gen = EntryScriptGen()
    env = CampaignEnv()
    agent = FDBScanAgent()
    decider = AgenticDecider()
    # 1. Prepare env
    env_result = env.prepare_env(sample_signal)
    # 2. Generate script
    script = gen.generate_bash_entry(sample_signal)
    script_path = tmp_path / 'entry.sh'
    with open(script_path, 'w') as f:
        f.write(script)
    # 3. Scan
    agent.scan_timeframe(sample_signal['timeframe'])
    # 4. Decide
    decision = decider.decide(sample_signal)
    assert os.path.exists(script_path)
    assert 'Prepared environment' in env_result
    assert 'Decision for' in decision
