#!/usr/bin/env python3
"""Extract budget data from PDF and convert to JSON format."""

import json
from typing import Any

from tools import extract_budget_data, extract_cost_from_string, extract_first_sentence, is_project_accepted


def process_row_2025(row_dict: dict[str, Any]) -> dict[str, Any] | None:
    """
    Process a single row from 2025 PDF table.

    Args:
        row_dict: Dictionary mapping column headers to row values

    Returns:
        Entry dictionary or None if row should be skipped
    """
    nazwa_col = row_dict.get("Tytuł / lokalizacja / zakres")
    if not nazwa_col:
        return None

    koszt_col = row_dict.get("Koszt projektu")
    cost = extract_cost_from_string(koszt_col)
    if cost is None:
        return None

    accepted_col = row_dict.get("Czy projekt został wybrany?")
    accepted = is_project_accepted(accepted_col)

    description = str(nazwa_col)

    if "\nZakres:" in description:
        before_zakres, _ = description.split("\nZakres:", 1)
    else:
        before_zakres = description

    name = extract_first_sentence(before_zakres)

    return {
        "name": name,
        "address": "",
        "category": "",
        "cost": cost,
        "description": description,
        "accepted": accepted
    }


def main() -> None:
    pdf_path = "data/2025/bo_2025_wyniki_glosowania_komplet_16-10-2024.pdf"

    entries = extract_budget_data(pdf_path, process_row_2025)

    output = json.dumps(entries, ensure_ascii=False, indent=2)
    print(output)


if __name__ == "__main__":
    main()
