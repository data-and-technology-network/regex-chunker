import re
import pandas as pd


def find_header_positions(text: str, pattern: str) -> list[tuple[str, int]]:
    """Finds positions of budget code headers in text.

    A budget code is considered a header when it:
        - Appears at the start of a line with no preceding text
        - Is followed by a dash or em-dash and descriptive text
        - Is not followed by punctuation (which would indicate inline usage)

    Args:
        text: The full text content to be searched.
        pattern: A regex pattern to identify budget codes.

    Returns:
        A list of tuples of (code, line_start) for each header code found.
    """
    header_positions = []
    for match in re.finditer(pattern, text):
        start, end = match.span()
        code = match.group()

        is_start_of_line = start == 0 or text[start - 1] == "\n"
        line_start = text.rfind("\n", 0, start) + 1
        has_no_text_before = text[line_start:start].strip() == ""
        remaining_text = text[end:]
        has_separator_after = bool(
            re.match(r"\s{0,4}[-\u2013\u2014]\s+\w", remaining_text)
        )
        not_followed_by_punctuation = not bool(re.match(r"\s*[.,;:]", remaining_text))

        if (
            is_start_of_line
            and has_no_text_before
            and has_separator_after
            and not_followed_by_punctuation
        ):
            header_positions.append((code, line_start))

    return header_positions


def chunk_text_by_header_codes(text: str, pattern: str, filename: str) -> pd.DataFrame:
    """Splits text into chunks using budget code headers as delimiters.

    Args:
        text: The full text content to be chunked.
        pattern: A regex pattern to identify budget codes.
        filename: The name of the source PDF file, added as a column.

    Returns:
        A DataFrame with columns:
            - code:     The budget code that starts each chunk.
            - chunk:    The full text of the chunk, from the code header up
                        to the start of the next code header.
            - filename: The name of the source PDF file.
    """
    header_positions = find_header_positions(text, pattern)
    result = {"code": [], "chunk": []}
    for i, (code, pos) in enumerate(header_positions):
        chunk_end = (
            header_positions[i + 1][1] if i + 1 < len(header_positions) else len(text)
        )
        result["code"].append(code)
        result["chunk"].append(text[pos:chunk_end].strip())

    return pd.DataFrame(result).assign(filename=filename)
