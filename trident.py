"""Trident: a toy simulation of a multi-role satellite with module failover.

Simulation only. Not flight software.
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

    @property
    def out(self) -> bool:
        return gate(self.capacity)


ROLES = ["comms", "navigation", "observation", "power", "compute"]


def default_modules():
    return [
        Module("alpha", {"comms", "navigation", "compute"}, 100.0),
        Module("bravo", {"observation", "compute", "comms"}, 80.0),
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


# step -> {module: capacity drop}
DEFAULT_TIMELINE = [
    {"alpha": 30},
    {"alpha": 80, "delta": 20},
    {"bravo": 85},
    {"charlie": 95},
]


def run(modules=None, timeline=None):
    modules = modules or default_modules()
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
