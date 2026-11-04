# Trident

Trident is an idea for one satellite that does many jobs at once: comms relay, navigation/timing, earth observation, power, and compute. Instead of many separate satellites, one object with several modules.

This repo is a **small Python simulation only**. It is not flight software, not a design, and not tested against any real hardware. No weapons.

## How it works
- Each module has a name, the roles it can do, and a capacity `N`.
- `gate(n)` returns True when `n <= 0`: the module is out.
- When a module goes out, each role it was doing moves to the healthiest working module that can do that role. Every move is logged.
- If no module can take a role, it is reported as uncovered.

## Two dependabots (v0.2.0)
- **Onboard dependabot** is one of Trident's roles. It looks at each module's (made-up) software list, compares versions with a (made-up) "latest" list, and proposes updates. It runs a pretend test: if the test is **lit** (passes) the update stays; if it is **dark** (fails) the update is rolled back. Everything is logged. Because it's a role, if its module goes out (N <= 0) another capable module takes it over.
- **GitHub Dependabot** is the real one, set up in `.github/dependabot.yml` (pip and GitHub Actions, weekly). If no module can run the onboard dependabot, the log says GitHub Dependabot takes over repo-level updates. The two don't actually talk to each other; this handoff is just a log line.
- **CI** (`.github/workflows/ci.yml`) runs the tests on every push. Green check = lit, red X = dark.

## Run
    python trident.py
    pip install -r requirements.txt && pytest

The original idea is kept in `docs/original-idea.md`.

No license has been chosen yet, so default copyright applies.
