"""Extract and chunk text from PDF files using budget code headers as delimiters.

This script scans all PDF files in the `pdfs/` folder, converts them to plain
text, and splits the text into chunks using budget codes (e.g. QB0-9QGDTAC-OW)
as delimiters. The resulting chunks are saved to a parquet file in the `results/`
folder.

Expected folder structure:
    pdfs/          - Place your PDF files here before running the script
    markdown/      - Intermediate markdown files are saved here (auto-created)
    results/       - Output parquet file is saved here (auto-created)

Output:
    results/chunked_text.parquet - A parquet file with columns:
        - code:     The budget code that starts each chunk
        - chunk:    The full text of the chunk
        - filename: The name of the PDF file the chunk came from
"""

from pathlib import Path

import pandas as pd
from markitdown import MarkItDown
from tqdm import tqdm

from src.chunking import chunk_text_by_header_codes

# Budget code pattern, matches codes like QB0-9QGDTAC-OW:
#   - 3 alphanumeric characters
#   - a hyphen
#   - 7 alphanumeric characters
#   - a hyphen
#   - 2 alphanumeric characters
PATTERN = r"\b[A-Za-z0-9]{3}-[A-Za-z0-9]{7}-[A-Za-z0-9]{2}\b"

OUTPUT_PATH = "results"
DF_FILENAME = "chunked_text.parquet"
PDF_FOLDER_PATH = Path("")

# Prepare output and intermediate folders
output_filepath = Path(OUTPUT_PATH)
output_filepath.mkdir(exist_ok=True)

script_path = Path(__file__)
pdf_folder_path = script_path.parent / "pdfs"

# Check if pdf folder exists, if not create it, then exit.
if not pdf_folder_path.exists():
    pdf_folder_path.mkdir(exist_ok=True)
    print(f"Please add PDFs to the {pdf_folder_path} folder and run again.")
    raise SystemExit  # Exit the script if no PDFs are found, no need to raise an error, just exit with

# Collect all PDF files from the pdfs/ folder
pdfs = [file for file in pdf_folder_path.glob("*.pdf") if file.is_file()]

if not pdfs:
    print(
        f"No PDFs found in {pdf_folder_path}. Please add PDFs to the folder and run again."
    )
    raise SystemExit  # Exit the script if no PDFs are found, no need to raise an error, just exit with

# Convert each PDF to plain text using markitdown
# Plugins are disabled to keep the output as clean plain text with line breaks
md_converter = MarkItDown(enable_plugins=False)
results = [
    md_converter.convert(file).text_content
    for file in tqdm(pdfs, desc="Converting PDFs to text")
]


# Process each PDF and combine into a single DataFrame
# zip() ties each converted text back to its source PDF filename
df = pd.concat(
    [
        chunk_text_by_header_codes(text, PATTERN, file.name)
        for text, file in zip(tqdm(results, desc="Chunking text"), pdfs)
    ]
)

# Write to disc
df.to_parquet(output_filepath / DF_FILENAME, index=False)
