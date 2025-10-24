#!/usr/bin/env python3
"""Extract budget data from 2026 PDF and convert to JSON format."""

import json
from typing import Any

from tools import extract_budget_data, extract_cost_from_string, is_project_accepted


def process_row_2026(row_dict: dict[str, Any]) -> dict[str, Any] | None:
    """
    Process a single row from 2026 PDF table.

    Args:
        row_dict: Dictionary mapping column headers to row values

    Returns:
        Entry dictionary or None if row should be skipped
    """
    # Skip district headers and incomplete rows
    typ_col = row_dict.get("Tytuł")
    if not typ_col:
        return None

    koszt_col = row_dict.get("Koszt projektu")
    cost = extract_cost_from_string(koszt_col)
    if cost is None:
        return None

    accepted_col = row_dict.get("Czy projekt został\nwybrany?")
    accepted = is_project_accepted(accepted_col)

    name = str(typ_col).strip().replace('\n', ' ')

    lokalizacja_col = row_dict.get("Lokalizacja", "")

    description_parts = [name]
    if lokalizacja_col:
        description_parts.append(f"Lokalizacja: {lokalizacja_col}")
    description = "\n".join(description_parts)

    return {
        "name": name,
        "address": "",
        "category": "",
        "cost": cost,
        "description": description,
        "accepted": accepted
    }


def main() -> None:
    pdf_path = "data/2026/bo_2026_wyniki_zestawienie_20-10-2025_podpis.pdf"

    # Predefined headers for 2026 PDF (pdfplumber treats each table's first row as headers)
    headers = [
        "Lp.",
        "Nr projektu",
        "Tytuł",
        "Lokalizacja",
        "Liczba\ngłosów",
        "Czy projekt został\nwybrany?",
        "Koszt projektu",
        "Pula/dostępne srodki"
    ]

    entries = extract_budget_data(pdf_path, process_row_2026, headers=headers)

    output = json.dumps(entries, ensure_ascii=False, indent=2)
    print(output)


if __name__ == "__main__":
    main()
