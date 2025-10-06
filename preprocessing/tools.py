"""Common utility functions for budget data extraction."""

import logging
import re
import sys
from collections.abc import Callable
from typing import Any

import pdfplumber

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)


def extract_cost_from_string(cost_str: str | None) -> int | None:
    """
    Extract numeric cost from string by removing non-digit characters.
    Handles decimal separators (comma or period) by ignoring decimal part.

    Args:
        cost_str: String containing cost (e.g., "100 000 zł" or "10 000,00 zł")

    Returns:
        Integer cost value, or None if no digits found
    """
    if not cost_str:
        return None

    # Split on decimal separator (comma or period) and take integer part
    cost_str_clean = str(cost_str).split(',')[0].split('.')[0]
    
    cost_digits = re.sub(r"[^\d]", "", cost_str_clean)
    if not cost_digits:
        return None

    return int(cost_digits)


def is_project_accepted(value: str | None) -> bool:
    """
    Check if project was accepted based on column value.

    Args:
        value: Value from "Czy projekt został wybrany?" column

    Returns:
        True if value is "TAK", False otherwise
    """
    if not value:
        return False

    return str(value).strip() == "TAK"


def extract_first_sentence(text: str) -> str:
    """
    Extract first sentence from text.

    Args:
        text: Input text

    Returns:
        First sentence (first line ending with punctuation)
    """
    lines = text.split('\n')
    if not lines:
        return ""

    first_line = lines[0].strip()
    if first_line.endswith(('.', '!', '?')):
        return first_line

    return first_line


def extract_budget_data(pdf_path: str, process_row: Callable[[dict[str, Any]], dict[str, Any] | None]) -> list[dict[str, Any]]:
    """
    Extract budget data from PDF table using year-specific row processing function.

    Args:
        pdf_path: Path to the PDF file
        process_row: Function that processes a row dictionary and returns entry dict or None

    Returns:
        List of budget entries extracted from PDF
    """
    entries = []

    with pdfplumber.open(pdf_path) as pdf:
        logger.info(f"Processing {len(pdf.pages)} pages")

        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            if not tables:
                logger.info(f"Page {page_num}: no tables found")
                continue

            logger.info(f"Page {page_num}: {len(tables)} table(s) found")

            for table in tables:
                if not table:
                    continue

                headers = table[0]
                logger.info(f"  Headers: {headers}")

                for row in table[1:]:
                    if not row or len(row) < 2:
                        continue

                    row_dict = {k: v for k, v in zip(headers, row) if k is not None}
                    entry = process_row(row_dict)
                    
                    if entry:
                        entries.append(entry)
                        logger.info(f"  Extracted: {entry['name'][:50]}...")

    logger.info(f"Total entries extracted: {len(entries)}")
    return entries
