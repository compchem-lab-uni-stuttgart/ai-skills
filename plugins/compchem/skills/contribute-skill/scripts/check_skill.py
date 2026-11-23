#!/usr/bin/env python3
"""Pre-commit check for a skill or subagent going into the public ai-skills repo.

Usage:
    python3 check_skill.py <path> [<path> ...]

<path> can be a skill folder (contains SKILL.md), a folder of skill folders
(e.g. plugins/compchem/skills), or a subagent file (agents/<name>.md).

Checks what `claude plugin validate` does not:
  - frontmatter: name present, lowercase-hyphen, <= 64 chars, matches the
    folder/file name; description present and <= 1024 chars
  - privacy: personal home paths, email addresses, API keys / tokens /
    private keys, research data files, oversized files, editor/OS junk
  - README: the skill or agent is listed in the repo README

Exit code 1 if any ERROR was found, else 0. WARN lines need a human decision.
Standard library only.
"""
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

PATH_PATTERNS = [
    (re.compile(r"/Users/(?![<${])[A-Za-z0-9._-]+"), "personal macOS home path"),
    (re.compile(r"/home/(?![<${])[A-Za-z0-9._-]+"), "personal Linux home path"),
    (re.compile(r"[A-Za-z]:\\\\?Users\\\\?(?![<${])[A-Za-z0-9._-]+"), "personal Windows home path"),
]
SOFT_PATH_PATTERNS = [
    (re.compile(r"~/(Desktop|Documents|Downloads)/\S+"), "path into someone's Desktop/Documents/Downloads"),
]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
EMAIL_ALLOW = ("example.com", "example.org", "example.net", "users.noreply.github.com", "anthropic.com")
SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "Anthropic API key"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "API key (sk-...)"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), "GitHub token"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHub token"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
]
SOFT_SECRET_RE = re.compile(
    r"(?i)\b(password|passwd|api[_-]?key|secret|token)\b\s*[:=]\s*[\"']?(?![<${])[^\s\"'<>{}()]{8,}"
)
DATA_EXT = {
    ".h5", ".hdf5", ".npy", ".npz", ".pkl", ".pickle", ".pt", ".pth", ".ckpt",
    ".xyz", ".extxyz", ".traj", ".dcd", ".xtc", ".trr", ".lammpstrj", ".cube",
    ".chk", ".fchk", ".db", ".sqlite", ".mat", ".nc",
}
JUNK = {"__pycache__", ".DS_Store", ".ipynb_checkpoints"}
WARN_BYTES = 1_000_000
ERROR_BYTES = 5_000_000


class Report:
    def __init__(self):
        self.errors = 0
        self.warnings = 0

    def error(self, where, msg):
        self.errors += 1
        print(f"ERROR {where}: {msg}")

    def warn(self, where, msg):
        self.warnings += 1
        print(f"WARN  {where}: {msg}")


def parse_frontmatter(text):
    """Return (dict, ok). Handles key: value, quoted values and >/| blocks."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, False
    data, key = {}, None
    for line in lines[1:end]:
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if value in (">", "|", ">-", "|-"):
                value = ""
            data[key] = value
        elif key and line.startswith((" ", "\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
    for k, v in data.items():
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            data[k] = v[1:-1]
    return data, True


def check_frontmatter(path, expected_name, rep):
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, ok = parse_frontmatter(text)
    if not ok:
        rep.error(path, "no YAML frontmatter (file must start with --- ... ---)")
        return None
    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        rep.error(path, "frontmatter has no 'name'")
    else:
        if not NAME_RE.match(name) or len(name) > 64:
            rep.error(path, f"name '{name}' must be lowercase letters, digits and hyphens, max 64 chars")
        if name != expected_name:
            rep.error(path, f"name '{name}' does not match '{expected_name}' (folder or file name)")
    if not desc:
        rep.error(path, "frontmatter has no 'description' (Claude uses it to decide when to load the skill)")
    else:
        if len(desc) > 1024:
            rep.error(path, f"description is {len(desc)} chars, max 1024")
        if len(desc) < 80:
            rep.warn(path, "description is very short; say what it does AND when to use it, or it will rarely trigger")
        if "<" in desc or ">" in desc:
            rep.warn(path, "description contains < or >; some upload paths (claude.ai) reject angle brackets")
    body_lines = len(text.splitlines())
    if body_lines > 500:
        rep.warn(path, f"{body_lines} lines; consider moving reference material into separate files")
    return name or expected_name


def is_binary(path):
    try:
        with open(path, "rb") as fh:
            return b"\0" in fh.read(8192)
    except OSError:
        return True


def scan_files(root, rep):
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*"))
    for p in files:
        if any(part in JUNK for part in p.parts):
            if p.name in JUNK:
                rep.warn(p, "OS/editor junk; delete it (it is git-ignored, but keep the folder clean)")
            continue
        if not p.is_file():
            continue
        size = p.stat().st_size
        if size > ERROR_BYTES:
            rep.error(p, f"{size / 1e6:.1f} MB; too large for this repo")
        elif size > WARN_BYTES:
            rep.warn(p, f"{size / 1e6:.1f} MB; is this file really needed?")
        if p.suffix.lower() in DATA_EXT:
            rep.warn(p, "research data file; only commit published, non-confidential, small example data")
        if is_binary(p):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            where = f"{p}:{lineno}"
            for rx, what in PATH_PATTERNS:
                for m in rx.finditer(line):
                    rep.error(where, f"{what} '{m.group(0)}'; use a placeholder like <project_dir> or a path relative to the skill")
            for rx, what in SOFT_PATH_PATTERNS:
                for m in rx.finditer(line):
                    rep.warn(where, f"{what} '{m.group(0)}'; fine only if it is a generic example")
            for m in EMAIL_RE.finditer(line):
                domain = m.group(0).split("@", 1)[1].lower()
                if not any(domain == d or domain.endswith("." + d) for d in EMAIL_ALLOW):
                    rep.error(where, f"email address '{m.group(0)}'; remove it or use name@example.com")
            hit = next((what for rx, what in SECRET_PATTERNS if rx.search(line)), None)
            if hit:
                rep.error(where, f"possible secret ({hit}); remove it and revoke the key")
            elif SOFT_SECRET_RE.search(line):
                rep.warn(where, "looks like a hard-coded password/key/token; check it is a placeholder")


def find_repo_readme(start):
    for d in [start, *start.parents]:
        if (d / ".claude-plugin" / "marketplace.json").is_file():
            readme = d / "README.md"
            return readme if readme.is_file() else None
    return None


def check_readme(target, needle, rep):
    readme = find_repo_readme(target.resolve())
    if readme and needle not in readme.read_text(encoding="utf-8", errors="replace"):
        rep.warn(readme, f"no link to '{needle}'; add a row for it to the table")


def check_skill_dir(d, rep):
    skill_md = d / "SKILL.md"
    if not skill_md.is_file():
        rep.error(d, "no SKILL.md in this folder")
        return
    check_frontmatter(skill_md, d.name, rep)
    scan_files(d, rep)
    check_readme(d, f"skills/{d.name}/", rep)


def check_agent_file(f, rep):
    check_frontmatter(f, f.stem, rep)
    scan_files(f, rep)
    check_readme(f, f"agents/{f.name}", rep)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    rep = Report()
    for arg in argv:
        p = Path(arg).expanduser()
        if p.is_file() and p.suffix == ".md":
            if p.name == "SKILL.md":
                check_skill_dir(p.parent, rep)
            else:
                check_agent_file(p, rep)
        elif p.is_dir() and (p / "SKILL.md").is_file():
            check_skill_dir(p, rep)
        elif p.is_dir():
            subs = [s for s in sorted(p.iterdir()) if s.is_dir() and (s / "SKILL.md").is_file()]
            agents = [a for a in sorted(p.glob("*.md"))]
            if not subs and not agents:
                print(f"NOTE  {p}: no skills or agents inside, nothing to check")
            for s in subs:
                check_skill_dir(s, rep)
            for a in agents:
                check_agent_file(a, rep)
        else:
            rep.error(p, "not found")
    status = "FAILED" if rep.errors else "OK"
    print(f"\n{status}: {rep.errors} error(s), {rep.warnings} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
