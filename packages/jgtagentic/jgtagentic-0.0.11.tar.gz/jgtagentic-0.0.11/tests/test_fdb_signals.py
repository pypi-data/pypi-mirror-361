# Test data for agentic orchestrator — signals from fdbscan
import json
import pytest

@pytest.fixture
def fdb_signals():
    # Minimal valid signals, as would be parsed from fdb_signals_out__250519.json
    return {
        "GBP/USD_m5_250519140525": {
            "sh": "# test shell script",
            "entry": 1.3351,
            "stop": 1.3346,
            "bs": "B",
            "lots": 1,
            "tlid_id": "250519140525",
            "i": "GBP/USD",
            "t": "m5",
            "pips_risk": 5.4,
        },
        "AUD/USD_m5_250519140533": {
            "sh": "# test shell script",
            "entry": 0.64512,
            "stop": 0.64492,
            "bs": "B",
            "lots": 1,
            "tlid_id": "250519140533",
            "i": "AUD/USD",
            "t": "m5",
            "pips_risk": 2.4,
        },
    }

def test_fdb_signals_structure(fdb_signals):
    assert "GBP/USD_m5_250519140525" in fdb_signals
    sig = fdb_signals["GBP/USD_m5_250519140525"]
    assert sig["i"] == "GBP/USD"
    assert sig["t"] == "m5"
    assert isinstance(sig["entry"], float)
    assert isinstance(sig["stop"], float)
    assert isinstance(sig["pips_risk"], float)
