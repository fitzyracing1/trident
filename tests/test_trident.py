import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from trident import gate, Module, run

def test_gate():
    assert gate(-1) is True
    assert gate(0) is True
    assert gate(0.0001) is False

def test_reassign_to_healthiest():
    mods = [Module("a", {"comms"}, 10), Module("b", {"comms"}, 5), Module("c", {"comms"}, 8)]
    log, asg, _ = run(mods, [{"a": 10}])
    assert asg["comms"].name == "c"
    assert any("HANDOFF comms: a -> c" in l for l in log)

def test_uncovered_reported():
    mods = [Module("a", {"comms"}, 1)]
    log, asg, unc = run(mods, [{"a": 1}])
    assert "comms" in unc
    assert any(l.startswith("UNCOVERED comms") for l in log)
