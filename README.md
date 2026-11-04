# Trident

Trident is an idea for one satellite that does many jobs at once: comms relay, navigation/timing, earth observation, power, and compute. Instead of many separate satellites, one object with several modules.

This repo is a **small Python simulation only**. It is not flight software, not a design, and not tested against any real hardware. No weapons.

## How it works
- Each module has a name, the roles it can do, and a capacity `N`.
- `gate(n)` returns True when `n <= 0`: the module is out.
- When a module goes out, each role it was doing moves to the healthiest working module that can do that role. Every move is logged.
- If no module can take a role, it is reported as uncovered.

## Run
    python trident.py
    pip install pytest && pytest

The original idea is kept in `docs/original-idea.md`.

No license has been chosen yet, so default copyright applies.
