"""
generator.py - Build the prompt and call the Claude API to generate a README.
"""

import anthropic

MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """\
You are an expert technical writer. Given information about a software project, \
you write clear, accurate, and well-structured README.md files in GitHub-flavored Markdown.

Guidelines:
- Be concise but thorough.
- Use only information present in the provided files — do not invent features or dependencies.
- If the language, framework, or build system is apparent from the files, mention it.
- Format code blocks with the appropriate language tag.
- Output ONLY the raw Markdown for the README. Do not wrap it in triple backticks or add any preamble.
"""

README_SECTIONS = """\
The README must include at minimum:
1. Project name and one-sentence description
2. Features / what it does (brief bullets)
3. Requirements / prerequisites
4. Installation / build instructions
5. Usage (with a short example)
6. (Optional) Notes or known limitations if obvious from the code
"""


def build_user_prompt(tree: list[str], selected_files: list[tuple[str, str]]) -> str:
    tree_str = "\n".join(tree) if tree else "(empty)"

    file_blocks = []
    for rel_path, content in selected_files:
        file_blocks.append(f"### {rel_path}\n```\n{content}\n```")
    files_str = "\n\n".join(file_blocks) if file_blocks else "(no readable source files found)"

    return f"""\
Please generate a README.md for the project described below.

{README_SECTIONS}

---

## Repository file tree

```
{tree_str}
```

---

## Source file contents (most relevant files)

{files_str}
"""


def generate_readme(tree: list[str], selected_files: list[tuple[str, str]]) -> str:
    """
    Call the Claude API and return the generated README as a string.
    Reads ANTHROPIC_API_KEY from the environment (loaded by the caller).
    """
    client = anthropic.Anthropic()  # picks up ANTHROPIC_API_KEY automatically

    user_prompt = build_user_prompt(tree, selected_files)

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text
