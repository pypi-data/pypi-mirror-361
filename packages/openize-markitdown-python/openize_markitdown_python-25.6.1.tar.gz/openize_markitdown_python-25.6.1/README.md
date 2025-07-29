# Openize.MarkItDown for Python

![Python Version](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-alpha-orange)

Openize.MarkItDown for Python converts documents into Markdown format. It supports multiple file formats, provides flexible output handling, and integrates with popular LLMs for post-processing, including OpenAI, Claude, Gemini, and Mistral.

## Features

- Convert `.docx`, `.pdf`, `.xlsx`, and `.pptx` to Markdown.
- Save Markdown files locally or send them to an LLM (OpenAI, Claude, Gemini, Mistral).
- Structured with the **Factory & Strategy Pattern** for scalability.
- Works with Windows and Linux-compatible paths.
- Command-line interface for easy use.

## Requirements

This package depends on the Aspose libraries, which are commercial products:

- [Aspose.Words](https://purchase.aspose.com/buy/words/python)
- [Aspose.Cells](https://purchase.aspose.com/buy/cells/python)
- [Aspose.Slides](https://purchase.aspose.com/buy/slides/python)

You'll need to obtain valid licenses for these libraries separately. The package will install these dependencies, but you're responsible for complying with Aspose's licensing terms.

LLM integration may require the following additional packages or valid API credentials:

- `openai` (for OpenAI)
- `anthropic` (for Claude)
- `requests` (used for Gemini and Mistral REST APIs)

## Installation

```bash
pip install openize-markitdown-python
```

## Usage

### Command Line Interface

```bash
# Convert a file and save locally
markitdown document.docx -o output_folder

# Process with an LLM (requires appropriate API key)
markitdown document.docx -o output_folder --llm openai
markitdown document.docx -o output_folder --llm claude
markitdown document.docx -o output_folder --llm gemini
markitdown document.docx -o output_folder --llm mistral
```

### Python API

```python
from openize.markitdown.core import MarkItDown

input_file = "report.pdf"
output_dir = "output_markdown"

converter = MarkItDown(output_dir, llm_client_name="gemini")
converter.convert_document(input_file)

print("Conversion completed and data sent to Gemini.")
```

## Environment Variables

The following environment variables are used to control license and LLM access:

| Variable            | Description                                                |
|---------------------|------------------------------------------------------------|
| `ASPOSE_LICENSE_PATH` | Required to activate Aspose license (if using paid APIs)  |
| `OPENAI_API_KEY`     | Required for OpenAI integration                            |
| `OPENAI_MODEL`       | (Optional) OpenAI model name (default: `gpt-4`)            |
| `CLAUDE_API_KEY`     | Required for Claude integration                            |
| `CLAUDE_MODEL`       | (Optional) Claude model name (default: `claude-v1`)        |
| `GEMINI_API_KEY`     | Required for Gemini integration                            |
| `GEMINI_MODEL`       | (Optional) Gemini model name (default: `gemini-pro`)       |
| `MISTRAL_API_KEY`    | Required for Mistral integration                           |
| `MISTRAL_MODEL`      | (Optional) Mistral model name (default: `mistral-medium`)  |

### Setting Environment Variables

**Unix-based (Linux/macOS):**
```bash
export ASPOSE_LICENSE_PATH="/path/to/license"
export OPENAI_API_KEY="your-openai-key"
export CLAUDE_API_KEY="your-claude-key"
export GEMINI_API_KEY="your-gemini-key"
export MISTRAL_API_KEY="your-mistral-key"
```

**Windows PowerShell:**
```powershell
$env:ASPOSE_LICENSE_PATH = "C:\path\to\license"
$env:OPENAI_API_KEY = "your-openai-key"
$env:CLAUDE_API_KEY = "your-claude-key"
$env:GEMINI_API_KEY = "your-gemini-key"
$env:MISTRAL_API_KEY = "your-mistral-key"
```
## Running Tests

To run unit tests for **Openize.MarkItDown**, follow these steps:

### 1. Navigate to the package directory

From the root of the repository, change into the package directory:

```bash
cd openize-markitdown/packages/markitdown
```

### 2. Install test dependencies

Make sure `pytest` and `pytest-mock` are installed:

```bash
pip install pytest pytest-mock
```

### 3. Run tests using `pytest`

To run all tests:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test.py
```

### Tip

Use `-v` for more detailed test output:

```bash
pytest -v
```

## License

This package is licensed under the MIT License. However, it depends on Aspose libraries, which are proprietary, closed-source libraries.

⚠️ You must obtain valid licenses for Aspose libraries separately. This repository does not include or distribute any proprietary components.
