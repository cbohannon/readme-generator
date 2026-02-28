# README Generator

A CLI tool that crawls a local code repository and generates a `README.md` using the Claude API.

## Project Structure

- `main.py` — CLI entry point (argparse, orchestrates the pipeline)
- `readme_gen/crawler.py` — Walks the repo, collects file paths and text contents
- `readme_gen/analyzer.py` — Scores and ranks files by relevance, trims to context budget
- `readme_gen/generator.py` — Builds the prompt and calls the Claude API

## Setup

```bash
pip install -r requirements.txt
copy .env.example .env   # then add your ANTHROPIC_API_KEY
```

## Usage

```bash
# Write README.md to the target repo
python main.py C:\path\to\repo

# Print to stdout instead
python main.py C:\path\to\repo --print-only

# Custom output path
python main.py C:\path\to\repo --output C:\path\to\output.md
```

## Key Details

- Model: `claude-opus-4-6`
- Context budget: 80,000 characters across selected files (8,000 char cap per file)
- Files are scored by name, extension, and depth; highest-scored files are sent first
- `.env` is gitignored — never commit it
