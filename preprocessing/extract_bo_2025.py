#!/usr/bin/env python3
"""Extract budget data from PDF and convert to JSON format."""

import json
import logging
import re
import sys
import time
import urllib.parse
import urllib.request
from typing import Any

import pdfplumber

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)


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


def geocode_location(address: str) -> tuple[float, float] | None:
    """
    Geocode address string to lat/lon using Nominatim API.

    Args:
        address: Address string to geocode

    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    if not address:
        return None

    query = f"{address}, Toruń, Poland"
    params = {
        "q": query,
        "format": "json",
        "limit": "1"
    }
    url = f"https://nominatim.openstreetmap.org/search?{urllib.parse.urlencode(params)}"

    headers = {"User-Agent": "torun-budzet-visualization"}
    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            time.sleep(1)
            data = json.loads(response.read().decode("utf-8"))
            if data:
                result = data[0]
                return float(result["lat"]), float(result["lon"])
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return None

    return None


def extract_budget_data(pdf_path: str) -> list[dict[str, Any]]:
    """
    Extract budget data from PDF table.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of budget entries with name, location, value, and category
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

                    row_dict = dict(zip(headers, row))

                    nazwa_col = row_dict.get("Tytuł / lokalizacja / zakres")
                    if not nazwa_col:
                        continue

                    koszt_col = row_dict.get("Koszt projektu")
                    if not koszt_col:
                        continue

                    cost_digits = re.sub(r"[^\d]", "", str(koszt_col))
                    if not cost_digits:
                        continue

                    accepted_col = row_dict.get("Czy projekt został wybrany?")
                    accepted = str(accepted_col).strip() == "TAK" if accepted_col else False

                    description = str(nazwa_col)

                    if "\nZakres:" in description:
                        before_zakres, _ = description.split("\nZakres:", 1)
                    else:
                        before_zakres = description

                    name = extract_first_sentence(before_zakres)

                    entry = {
                        "name": name,
                        "address": "",
                        "category": "",
                        "cost": int(cost_digits),
                        "description": description,
                        "accepted": accepted
                    }

                    entries.append(entry)
                    logger.info(f"  Extracted: {name[:50]}...")

    logger.info(f"Total entries extracted: {len(entries)}")
    return entries


def geocode_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Geocode entries that have manually provided addresses.

    Args:
        entries: List of budget entries

    Returns:
        List of budget entries with lat/lon added for entries with addresses
    """
    geocoded_count = 0

    for entry in entries:
        address = entry.get("address", "")
        if address:
            logger.info(f"Geocoding: {address}")
            coords = geocode_location(address)
            if coords:
                entry["lat"], entry["lon"] = coords
                geocoded_count += 1
                logger.info(f"  -> {coords}")
            else:
                logger.warning(f"  -> Failed to geocode")

    logger.info(f"Geocoded {geocoded_count} entries")
    return entries


def main() -> None:
    pdf_path = "bo/2025/bo_2025_wyniki_glosowania_komplet_16-10-2024.pdf"

    entries = extract_budget_data(pdf_path)
    entries = geocode_entries(entries)

    output = json.dumps(entries, ensure_ascii=False, indent=2)
    print(output)


if __name__ == "__main__":
    main()
