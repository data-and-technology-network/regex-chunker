# regex-chunker

A lightweight tool for splitting PDFs into structured chunks using code headers (e.g. `QB0-9QGDTAC-OW`) as delimiters. The output is a parquet file with one row per chunk.

## How it works

1. All PDFs in the `pdfs/` folder are converted to plain text using [markitdown](https://github.com/microsoft/markitdown)
2. Codes that appear as section headers are identified using a regex pattern and a set of positional checks
3. The text is split into chunks at each header code
4. The chunks are saved to a parquet file in the `results/` folder

## Project structure

```
regex-chunker/
├── pdfs/                    # Place your PDFs here before running
├── results/                 # Output parquet file is saved here (auto-created)
├── src/
│   └── chunking.py          # Core chunking logic
├── chunk_pdfs.py            # Main script
└── pyproject.toml
```

## Installation

### Option 1: uv (recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. If you don't have it installed:

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then install and run the project:

```bash
# Clone or download the project, then navigate to the folder
cd regex-chunker

# Create a virtual environment and install dependencies
uv sync

# Run the script
uv run chunk_pdfs.py
```

### Option 2: pip

If you prefer to use pip, make sure you have Python 3.10 or higher installed. You can check with:

```bash
python --version
```

Then install and run the project:

```bash
# Clone or download the project, then navigate to the folder
cd regex-chunker

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# macOS / Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install markitdown[pdf] pandas fastparquet tqdm

# Install the local src package so imports work
pip install -e .

# Run the script
python chunk_pdfs.py
```

## Usage

1. Add your PDF files to the `pdfs/` folder
2. Run the script using either `uv run chunk_pdfs.py` or `python chunk_pdfs.py`
3. The output is saved to `results/chunked_text.parquet`

The parquet file contains three columns:

| column     | description                                      |
|------------|--------------------------------------------------|
| `code`     | The budget code that starts the chunk            |
| `chunk`    | The full text of the chunk                       |
| `filename` | The name of the PDF file the chunk came from     |

You can read the output in Python with:

```python
import pandas as pd

df = pd.read_parquet("results/chunked_text.parquet")
print(df.head())
```
