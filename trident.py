"""Trident: a toy simulation of a multi-role satellite with module failover.

Simulation only. Not flight software.
v0.2.0 adds an onboard dependabot role that can hand off to GitHub Dependabot.
"""
import math
from dataclasses import dataclass, field


def gate(n) -> bool:
    """Logic gate: True means the module is OUT (capacity N <= 0)."""
    return n <= 0


@dataclass
class Module:
    name: str
    roles: set
    capacity: float
    serving: set = field(default_factory=set)
    manifest: dict = field(default_factory=dict)  # simulated deps: name -> version tuple

    @property
    def out(self) -> bool:
        return gate(self.capacity)


ROLES = ["comms", "navigation", "observation", "power", "compute", "dependabot"]


def default_modules():
    return [
        Module("alpha", {"comms", "navigation", "compute", "dependabot"}, 100.0),
        Module("bravo", {"observation", "compute", "comms", "dependabot"}, 80.0),
        Module("charlie", {"power", "navigation"}, 90.0),
        Module("delta", {"power", "observation"}, 60.0),
    ]


def pick(role, modules):
    """Healthiest live module that can serve the role, or None."""
    live = [m for m in modules if role in m.roles and not m.out]
    return max(live, key=lambda m: m.capacity, default=None)


def assign(modules, assignment, log):
    """(Re)assign roles whose owner is out or missing. Returns uncovered roles."""
    uncovered = []
    for role in ROLES:
        cur = assignment.get(role)
        if cur is not None and not cur.out:
            continue
        new = pick(role, modules)
        if cur is not None:
            cur.serving.discard(role)
        if new is None:
            assignment[role] = None
            uncovered.append(role)
            if cur is not None:
                log.append(f"UNCOVERED {role}: {cur.name} out, no capable module left")
            continue
        new.serving.add(role)
        assignment[role] = new
        log.append(f"HANDOFF {role}: {cur.name if cur else '-'} -> {new.name}")
    return uncovered


# ---- onboard dependabot (simulated) ----
REGISTRY = {"radio-stack": (2, 1), "nav-core": (1, 4), "imager": (3, 0), "pwr-ctl": (1, 2)}
BROKEN = {("imager", (3, 0))}  # simulated: this update turns the test dark


def default_manifests():
    return {"alpha": {"radio-stack": (2, 0), "nav-core": (1, 4)},
            "bravo": {"imager": (2, 9), "radio-stack": (2, 1)},
            "charlie": {"pwr-ctl": (1, 0), "nav-core": (1, 3)},
            "delta": {"pwr-ctl": (1, 2), "imager": (2, 9)}}


def fmt(v):
    return ".".join(map(str, v))


def simulated_test(module, dep, version) -> bool:
    """Lit (True) unless this dep/version is in BROKEN."""
    return (dep, version) not in BROKEN


def dependabot_cycle(bot, modules, log, t=0, registry=REGISTRY, test=simulated_test):
    """Check every live module's manifest vs registry; apply if lit, roll back if dark."""
    if bot is None:
        log.append(f"t={t} DEPENDABOT onboard role uncovered -> GitHub Dependabot "
                   "takes over repo-level updates (.github/dependabot.yml)")
        return
    for m in modules:
        if m.out:
            continue
        for dep, have in sorted(m.manifest.items()):
            want = registry.get(dep)
            if want is None or want <= have:
                continue
            log.append(f"t={t} DEPENDABOT[{bot.name}] propose {m.name}:{dep} {fmt(have)} -> {fmt(want)}")
            m.manifest[dep] = want
            if test(m, dep, want):
                log.append(f"t={t} DEPENDABOT[{bot.name}] lit -> applied {m.name}:{dep} {fmt(want)}")
            else:
                m.manifest[dep] = have
                log.append(f"t={t} DEPENDABOT[{bot.name}] dark -> rolled back {m.name}:{dep} {fmt(have)}")


# step -> {module: capacity drop}
DEFAULT_TIMELINE = [
    {"alpha": 30},
    {"alpha": 80, "delta": 20},
    {"bravo": 85},
    {"charlie": 95},
]


def run(modules=None, timeline=None):
    if modules is None:
        modules = default_modules()
        for m in modules:
            m.manifest = default_manifests().get(m.name, {})
    timeline = DEFAULT_TIMELINE if timeline is None else timeline
    by_name = {m.name: m for m in modules}
    log, assignment = [], {}
    uncovered = assign(modules, assignment, log)
    for t, drops in enumerate(timeline, 1):
        for name, d in drops.items():
            m = by_name[name]
            m.capacity -= d
            if m.out:
                log.append(f"t={t} GATE {name} N={m.capacity:g} <= 0 -> out")
        uncovered = assign(modules, assignment, log)
        dependabot_cycle(assignment.get("dependabot"), modules, log, t)
    return log, assignment, uncovered


def main():
    log, assignment, uncovered = run()
    for line in log:
        print(line)
    live = sum(1 for r in ROLES if assignment.get(r))
    print(f"coverage {live}/{len(ROLES)} ({math.floor(100 * live / len(ROLES))}%)")
    print("uncovered:", ", ".join(uncovered) if uncovered else "none")
    return uncovered


if __name__ == "__main__":
    main()
