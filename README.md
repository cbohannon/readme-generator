# README Generator

A CLI tool that crawls a local code repository and generates a high-quality `README.md` using the Anthropic Claude API.

## Features

- **Repository crawling** — Recursively walks a local codebase, collecting file paths and text contents while skipping common non-essential directories (`.git`, `node_modules`, `__pycache__`, etc.)
- **Intelligent file selection** — Scores and ranks files by name, extension, and directory depth to prioritize the most informative files (e.g., `main.py`, `package.json`, `Cargo.toml`)
- **Context-aware trimming** — Stays within an 80,000-character context budget, with an 8,000-character cap per individual file, so the API prompt remains focused
- **Claude-powered generation** — Sends the curated project context to Claude (`claude-opus-4-6`) and returns a well-structured, GitHub-flavored Markdown README
- **Flexible output** — Write directly to the repo, specify a custom output path, or print to stdout

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/)

### Python Dependencies

- `anthropic >= 0.40.0`
- `python-dotenv >= 1.0.0`

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/readme-generator.git
   cd readme-generator
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API key:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your Anthropic API key:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

## Usage

### Generate a README and write it to the target repository

```bash
python main.py /path/to/repo
```

This creates (or overwrites) `README.md` inside `/path/to/repo`.

### Print the generated README to stdout

```bash
python main.py /path/to/repo --print-only
```

### Specify a custom output path

```bash
python main.py /path/to/repo --output /somewhere/else/README.md
```

### Full CLI reference

```
usage: main.py [-h] [--output OUTPUT] [--print-only] repo_path

Generate a README.md for a local code repository using Claude.

positional arguments:
  repo_path             Path to the local repository

options:
  -h, --help            show this help message and exit
  --output, -o OUTPUT   Output file path (default: <repo_path>/README.md)
  --print-only, -p      Print the generated README to stdout instead of writing a file
```

## How It Works

1. **Crawl** — `readme_gen/crawler.py` walks the repository tree, ignoring common non-essential directories and binary files. Text files up to 64 KB are read and collected.
2. **Analyze** — `readme_gen/analyzer.py` assigns a relevance score to each file based on its name (e.g., `main.py` → 100), extension (e.g., `.py` → 40), and depth in the directory tree (penalty of 5 per level). Files are sorted by score and selected until the context budget is filled.
3. **Generate** — `readme_gen/generator.py` constructs a structured prompt containing the file tree and selected file contents, then sends it to the Claude API.
4. **Output** — The generated Markdown is written to a file or printed to stdout.

## Notes & Limitations

- **API key required** — The tool will exit with an error if `ANTHROPIC_API_KEY` is not set in the environment or `.env` file.
- **Context limits** — Very large repositories will have many files truncated or excluded; the tool prioritizes the most informative files but may miss relevant ones buried deep in the tree.
- **Text files only** — Binary files (images, compiled artifacts, etc.) are listed in the file tree but their contents are not read or sent to the API.
- **Single-file cap** — Individual files are truncated at 8,000 characters to prevent any single file from dominating the context window.
- **Model** — Currently hardcoded to use `claude-opus-4-6`. To change the model, edit the `MODEL` constant in `readme_gen/generator.py`.
- **Never commit `.env`** — The `.env` file containing your API key is gitignored by default.