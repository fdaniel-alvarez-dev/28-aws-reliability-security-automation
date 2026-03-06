#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    severity: str  # ERROR | WARN | INFO
    rule_id: str
    message: str
    path: str | None = None


def repo_read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def add(findings: list[Finding], severity: str, rule_id: str, message: str, path: Path | None = None) -> None:
    findings.append(
        Finding(
            severity=severity,
            rule_id=rule_id,
            message=message,
            path=str(path.relative_to(REPO_ROOT)) if path else None,
        )
    )


def summarize(findings: list[Finding]) -> dict:
    return {
        "errors": sum(1 for f in findings if f.severity == "ERROR"),
        "warnings": sum(1 for f in findings if f.severity == "WARN"),
        "info": sum(1 for f in findings if f.severity == "INFO"),
    }


def check_script_safety(findings: list[Finding]) -> None:
    scripts_dir = REPO_ROOT / "scripts"
    if not scripts_dir.exists():
        add(findings, "ERROR", "scripts.missing", "scripts/ directory is missing.", scripts_dir)
        return

    scripts = sorted(scripts_dir.glob("*.sh"))
    if not scripts:
        add(findings, "ERROR", "scripts.empty", "No scripts found under scripts/.", scripts_dir)
        return

    for s in scripts:
        text = repo_read(s)
        if "set -euo pipefail" not in text:
            add(findings, "WARN", "bash.strict_mode", "Script should use `set -euo pipefail`.", s)
        if "docker compose ps -q" in text and "exit 2" not in text:
            add(findings, "WARN", "docker.preflight", "Script should fail clearly when containers are missing.", s)

    restore = scripts_dir / "restore.sh"
    if restore.exists():
        text = repo_read(restore)
        if "drop schema public cascade" in text:
            add(
                findings,
                "ERROR",
                "restore.destructive",
                "Restore should not drop the primary schema. Restore into an isolated verification database instead.",
                restore,
            )
        if "appdb_verify" not in text:
            add(findings, "WARN", "restore.verify_db", "Restore should use an isolated verification database (e.g., appdb_verify).", restore)


def check_runbooks(findings: list[Finding]) -> None:
    rb = REPO_ROOT / "docs" / "runbooks" / "backup-and-restore.md"
    if not rb.exists():
        add(findings, "WARN", "runbooks.missing", "Missing backup/restore runbook.", rb)
        return
    text = repo_read(rb)
    if "Safety" not in text and "Verification" not in text:
        add(findings, "WARN", "runbooks.verification", "Runbook should include explicit verification and safety notes.", rb)


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline automation guardrails for this repo.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--out", default="", help="Write output to a file (optional).")
    args = parser.parse_args()

    findings: list[Finding] = []
    check_script_safety(findings)
    check_runbooks(findings)

    report = {"summary": summarize(findings), "findings": [asdict(f) for f in findings]}

    if args.format == "json":
        output = json.dumps(report, indent=2, sort_keys=True)
    else:
        lines = []
        for f in findings:
            where = f" ({f.path})" if f.path else ""
            lines.append(f"{f.severity} {f.rule_id}{where}: {f.message}")
        lines.append("")
        lines.append(f"Summary: {report['summary']}")
        output = "\n".join(lines)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

