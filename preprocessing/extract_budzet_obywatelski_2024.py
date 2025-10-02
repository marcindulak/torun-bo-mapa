#!/usr/bin/env python3
"""Extract budget data from PDF and convert to JSON format."""

import json
import re
from typing import Any

import pdfplumber
import spacy


def extract_budget_data(pdf_path: str) -> list[dict[str, Any]]:
    """
    Extract budget data from PDF table.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of budget entries with name, location, value, and category
    """
    nlp = spacy.load("pl_core_news_sm")
    entries = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                
                headers = table[0]
                
                for row in table[1:]:
                    if not row or len(row) < 2:
                        continue
                    
                    row_dict = dict(zip(headers, row))
                    
                    nazwa_col = row_dict.get("Nazwa zadania/ lokalizacja/zakres")
                    if not nazwa_col:
                        continue
                    
                    koszt_col = row_dict.get("Koszty po\nweryfikacji (zł)")
                    if not koszt_col:
                        continue
                    
                    value_digits = re.sub(r"[^\d]", "", str(koszt_col))
                    if not value_digits:
                        continue
                    
                    dzial_col = row_dict.get("Dział")
                    if not dzial_col:
                        continue
                    
                    category_digits = re.sub(r"[^\d]", "", str(dzial_col))
                    if not category_digits:
                        continue
                    
                    description = str(nazwa_col)
                    
                    if "\nZakres:" in description:
                        before_zakres, _ = description.split("\nZakres:", 1)
                    else:
                        before_zakres = description
                    
                    doc = nlp(before_zakres.replace("\n", " "))
                    sentences = list(doc.sents)
                    
                    name = sentences[0].text.strip() if len(sentences) > 0 else ""
                    location = sentences[1].text.strip() if len(sentences) > 1 else ""
                    
                    entry = {
                        "name": name,
                        "location": location,
                        "value": int(value_digits),
                        "category": category_digits,
                        "description": description
                    }
                    
                    entries.append(entry)

    return entries


def main() -> None:
    pdf_path = "noupload/2024/Projekty wybrane przez mieszkancow w procedurze budzetu obywatelskiego.pdf"

    entries = extract_budget_data(pdf_path)

    output = json.dumps(entries, ensure_ascii=False, indent=2)
    print(output)


if __name__ == "__main__":
    main()
