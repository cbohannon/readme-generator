"""
main.py - CLI entry point for the README generator.

Usage:
    python main.py <repo_path> [--output <file>] [--print-only] [--model <model>]

Options:
    repo_path           Path to the local repository to analyze.
    --output, -o        Where to write the README (default: <repo_path>/README.md).
    --print-only, -p    Print the README to stdout instead of writing a file.
    --model, -m         Claude model to use (default: claude-opus-4-6).
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from readme_gen.crawler import crawl
from readme_gen.analyzer import select_files
from readme_gen.generator import generate_readme


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a README.md for a local code repository using Claude."
    )
    parser.add_argument("repo_path", help="Path to the local repository")
    parser.add_argument("--output", "-o", default=None, help="Output file path (default: <repo_path>/README.md)", )
    parser.add_argument("--print-only", "-p", action="store_true", help="Print the generated README to stdout instead of writing a file", )
    parser.add_argument(
        "--model", "-m",
        default="claude-opus-4-6",
        choices=["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
        help="Claude model to use (default: claude-opus-4-6)",
    )
    return parser.parse_args()


def main():
    load_dotenv()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        print("Copy .env.example to .env and add your key, or export the variable.", file=sys.stderr)
        sys.exit(1)

    args = parse_args()
    repo_path = Path(args.repo_path).resolve()

    if not repo_path.is_dir():
        print(f"Error: '{repo_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    # --- Step 1: Crawl ---
    print(f"Crawling repository: {repo_path}", file=sys.stderr)
    result = crawl(str(repo_path))
    tree = result["tree"]
    files = result["files"]
    print(f"  Found {len(tree)} files, {len(files)} readable.", file=sys.stderr)

    # --- Step 2: Prioritize ---
    selected = select_files(files)
    print(f"  Selected {len(selected)} files for context.", file=sys.stderr)

    # --- Step 3: Generate ---
    print(f"Generating README via Claude API ({args.model})...", file=sys.stderr)
    readme = generate_readme(tree, selected, model=args.model)

    # --- Step 4: Output ---
    if args.print_only:
        print(readme)
    else:
        out_path = Path(args.output) if args.output else repo_path / "README.md"
        out_path.write_text(readme, encoding="utf-8")
        print(f"README written to: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
