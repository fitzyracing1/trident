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

from trident import dependabot_cycle

def test_dependabot_lit_applies_dark_rolls_back():
    bot = Module("a", {"dependabot"}, 10)
    m = Module("m", set(), 10, manifest={"x": (1, 0), "y": (1, 0)})
    log = []
    dependabot_cycle(bot, [bot, m], log, registry={"x": (1, 1), "y": (2, 0)},
                     test=lambda mod, d, v: d == "x")
    assert m.manifest == {"x": (1, 1), "y": (1, 0)}
    assert any("lit -> applied m:x" in l for l in log)
    assert any("dark -> rolled back m:y" in l for l in log)

def test_dependabot_fails_over_then_hands_to_github():
    mods = [Module("a", {"dependabot"}, 5), Module("b", {"dependabot"}, 3)]
    log, asg, unc = run(mods, [{"a": 5}, {"b": 3}])
    assert any("HANDOFF dependabot: a -> b" in l for l in log)
    assert "dependabot" in unc
    assert any("GitHub Dependabot takes over" in l for l in log)
