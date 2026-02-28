"""
crawler.py - Walk a repository directory and collect file paths + contents.
"""

import os
from pathlib import Path

# Directories that are almost never useful for README generation
IGNORE_DIRS = {
    ".git", ".svn", ".hg",
    "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", "out", "bin", "obj",
    ".vs", ".idea", ".vscode",
    "packages", ".nuget",
}

# Extensions we are willing to read as text
TEXT_EXTENSIONS = {
    # Source
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".kt", ".cs", ".cpp", ".cc",
    ".cxx", ".c", ".h", ".hpp", ".hxx", ".go", ".rs", ".rb", ".php", ".swift",
    ".m", ".scala", ".r", ".lua", ".dart", ".ex", ".exs", ".erl", ".hs",
    # Config / project files
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf",
    ".xml", ".vcxproj", ".csproj", ".sln", ".props",
    # Docs / markup
    ".md", ".rst", ".txt",
    # Shell
    ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd",
    # Web
    ".html", ".htm", ".css",
    # Build
    "makefile", "dockerfile", ".cmake",
}

MAX_FILE_BYTES = 64 * 1024  # 64 KB hard cap per file


def should_ignore_dir(name: str) -> bool:
    return name.lower() in IGNORE_DIRS or name.startswith(".")


def is_readable(path: Path) -> bool:
    suffix = path.suffix.lower()
    name = path.name.lower()
    return suffix in TEXT_EXTENSIONS or name in TEXT_EXTENSIONS


def crawl(repo_path: str) -> dict:
    """
    Walk `repo_path` and return a dict:
        {
            "tree": [str, ...],          # relative paths of every non-ignored file
            "files": {rel_path: content} # text content of readable files
        }
    Files larger than MAX_FILE_BYTES are noted in `tree` but skipped in `files`.
    """
    root = Path(repo_path).resolve()
    if not root.is_dir():
        raise ValueError(f"Not a directory: {repo_path}")

    tree = []
    files = {}

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored dirs in-place so os.walk won't descend into them
        dirnames[:] = [d for d in sorted(dirnames) if not should_ignore_dir(d)]

        rel_dir = Path(dirpath).relative_to(root)

        for fname in sorted(filenames):
            fpath = Path(dirpath) / fname
            rel = str(rel_dir / fname).replace("\\", "/")
            tree.append(rel)

            if not is_readable(fpath):
                continue
            if fpath.stat().st_size > MAX_FILE_BYTES:
                files[rel] = f"[File too large to include — {fpath.stat().st_size} bytes]"
                continue

            try:
                files[rel] = fpath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass  # skip unreadable files silently

    return {"tree": tree, "files": files}
