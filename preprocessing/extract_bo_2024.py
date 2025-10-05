#!/usr/bin/env python3
"""Extract budget data from PDF and convert to JSON format."""

import json
from typing import Any

from tools import extract_budget_data, extract_cost_from_string, is_project_accepted


def process_row_2024(row_dict: dict[str, Any]) -> dict[str, Any] | None:
    """
    Process a single row from 2024 PDF table.

    Args:
        row_dict: Dictionary mapping column headers to row values

    Returns:
        Entry dictionary or None if row should be skipped
    """
    nazwa_col = row_dict.get("Tytuł projektu")
    if not nazwa_col:
        return None

    koszt_col = row_dict.get("Szacowany\nkoszt realizacji")
    cost = extract_cost_from_string(koszt_col)
    if cost is None:
        return None

    accepted_col = row_dict.get("Czy projekt\nzostał wybrany?")
    accepted = is_project_accepted(accepted_col)

    name = str(nazwa_col).strip().replace('\n', ' ')
    
    lokalizacja_col = row_dict.get("Lokalizacja", "")
    zakres_col = row_dict.get("Zakres", "")
    
    description_parts = [name]
    if lokalizacja_col:
        description_parts.append(f"Lokalizacja: {lokalizacja_col}")
    if zakres_col:
        description_parts.append(f"Zakres: {zakres_col}")
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
    pdf_path = "bo/2024/bo_2024_wyniki_komplet_13-10-2023_int_ok.pdf"

    entries = extract_budget_data(pdf_path, process_row_2024)

    output = json.dumps(entries, ensure_ascii=False, indent=2)
    print(output)


if __name__ == "__main__":
    main()
