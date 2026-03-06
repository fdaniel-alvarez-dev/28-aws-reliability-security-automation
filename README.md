# 28-aws-reliability-security-automation

A portfolio-grade repository focused on **automation for database reliability**: small scripts and drills that turn fragile operational work into repeatable, reviewable, and testable workflows.

This repository is intentionally generic (no employer branding). It demonstrates operational automation that you can validate locally and in CI.

## The 3 core problems this repo solves
1) **Repeatable operations:** backup/restore and replica checks you can run without tribal knowledge.
2) **Safer automation:** scripts that fail clearly, avoid destructive defaults, and produce verifiable outcomes.
3) **Production-safe validation:** explicit test modes separating offline checks from real integrations.

## Quickstart (local lab)
Prereqs: Docker + Docker Compose.

```bash
make demo
```

## Tests (two explicit modes)

This repo supports exactly two test modes via `TEST_MODE`:

- `TEST_MODE=demo` (default): offline-only (runs automation guardrails and repo policy checks)
- `TEST_MODE=production`: real integrations when configured (guarded by explicit opt-in)

Run demo mode:

```bash
make test-demo
```

Run production mode:

```bash
make test-production
```

Production integration options:
- Make Docker usable to run the local lab drills
- Or set `PG_TEST_DSN` to run a real `psql` connectivity query

## Automation guardrails

The file `tools/automation_guardrails.py` runs offline checks that enforce automation hygiene:
- strict bash mode expectations
- safer restore behavior (non-destructive by default)
- presence of verification/safety notes in critical runbooks

Generate an evidence artifact:

```bash
python3 tools/automation_guardrails.py --format json --out artifacts/automation_guardrails.json
```

## Sponsorship and contact

Sponsored by:
CloudForgeLabs  
https://cloudforgelabs.ainextstudios.com/  
support@ainextstudios.com

Built by:
Freddy D. Alvarez  
https://www.linkedin.com/in/freddy-daniel-alvarez/

For job opportunities, contact:
it.freddy.alvarez@gmail.com

## License

Personal, educational, and non-commercial use is free. Commercial use requires paid permission.
See `LICENSE` and `COMMERCIAL_LICENSE.md`.
