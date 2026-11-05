"""Fail-closed registration, credential and public text gates."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

SECRET = re.compile(
    r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|"
    r"(?:postgres(?:ql)?://)[^/\s]+:[^@\s]+@)"
)
BANNED = ("delve", "game-changing", "revolutionary", "seamlessly")


def scan_text(text: str, prose: bool = False) -> list[str]:
    errors = []
    if chr(0x2014) in text:
        errors.append("em_dash")
    if SECRET.search(text):
        errors.append("credential")
    if prose:
        for word in BANNED:
            if re.search(r"\b" + re.escape(word) + r"\b", text, re.I):
                errors.append("vocabulary:" + word)
    return errors


def run(root: Path) -> list[str]:
    paths = [
        p
        for p in root.rglob("*")
        if p.is_file()
        and not any(
            x
            in {".git", ".venv", "node_modules", "private", "__pycache__", ".pytest_cache", "build"}
            for x in p.parts
        )
        and p.suffix in {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".tsx", ".ts"}
    ]
    if not paths:
        raise ValueError("no_files_to_scan")
    errors = []
    for p in paths:
        relative = p.relative_to(root).as_posix()
        if relative == "docs/SPEC.md":
            continue  # Source contract preserves vocabulary examples.
        for error in scan_text(p.read_text(encoding="utf-8"), p.suffix == ".md"):
            errors.append(relative + ":" + error)
    return errors


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    subprocess.run(["python", "scripts/register.py", "--check"], cwd=root, check=True)
    failures = run(root)
    if failures:
        raise SystemExit("\n".join(failures))
    print("source gates passed")
