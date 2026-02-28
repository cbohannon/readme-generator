"""
analyzer.py - Score and rank files by how useful they are for README generation.

Higher score = more likely to reveal what the project is and how it works.
"""

from pathlib import Path

# Base scores by file name (case-insensitive exact match)
NAME_SCORES = {
    "main.py": 100, "app.py": 95, "run.py": 90, "server.py": 90,
    "main.cpp": 100, "main.c": 100, "main.cs": 100, "main.go": 100,
    "main.rs": 100, "main.java": 100, "main.rb": 100,
    "index.js": 95, "index.ts": 95,
    "package.json": 85, "cargo.toml": 85, "pyproject.toml": 85,
    "setup.py": 80, "setup.cfg": 75,
    "cmakelists.txt": 80, "makefile": 75,
    "readme.md": 70, "readme.rst": 70, "readme.txt": 70,
    "requirements.txt": 60, "pipfile": 60,
    "dockerfile": 55, "docker-compose.yml": 55,
    ".github": 40,
}

# Bonus scores by file extension
EXT_SCORES = {
    ".vcxproj": 70, ".csproj": 70, ".sln": 65,
    ".cpp": 50, ".c": 50, ".h": 45, ".hpp": 45,
    ".py": 40, ".go": 40, ".rs": 40, ".java": 40, ".cs": 40,
    ".js": 35, ".ts": 35,
    ".json": 20, ".toml": 20, ".yaml": 15, ".yml": 15,
    ".md": 15, ".txt": 10,
}

# Penalty for files buried deeply in the tree
DEPTH_PENALTY_PER_LEVEL = 5

# Hard cap on total characters we'll send for source context
MAX_CONTEXT_CHARS = 80_000


def score_file(rel_path: str) -> int:
    p = Path(rel_path)
    name_score = NAME_SCORES.get(p.name.lower(), 0)
    ext_score = EXT_SCORES.get(p.suffix.lower(), 0)
    depth = len(p.parts) - 1
    penalty = depth * DEPTH_PENALTY_PER_LEVEL
    return name_score + ext_score - penalty


def select_files(files: dict, max_chars: int = MAX_CONTEXT_CHARS) -> list[tuple[str, str]]:
    """
    Return an ordered list of (rel_path, content) tuples, highest-scored first,
    trimmed so the total character count stays under `max_chars`.
    """
    scored = sorted(files.items(), key=lambda kv: score_file(kv[0]), reverse=True)

    selected = []
    chars_used = 0
    for rel_path, content in scored:
        if chars_used >= max_chars:
            break
        # Truncate very long individual files so one file can't crowd everything out
        if len(content) > 8_000:
            content = content[:8_000] + "\n... [truncated]"
        selected.append((rel_path, content))
        chars_used += len(content)

    return selected
