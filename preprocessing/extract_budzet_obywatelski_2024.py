#!/usr/bin/env python3
"""Extract budget data from PDF and convert to JSON format."""

import json
import re
import sys
import time
from typing import Any
from urllib.parse import urlencode

import pdfplumber
import spacy
import urllib3


def get_manual_address(name: str, location: str) -> str:
    """
    Get manual address override for specific entries.

    Args:
        name: Project name
        location: Location string

    Returns:
        Manual address or empty string
    """
    manual_addresses: dict[tuple[str, str], str] = {
    }
    
    key = (name, location)
    return manual_addresses.get(key, "")


def extract_address_from_location(location: str, nlp: Any) -> str:
    """
    Extract address from location field using spaCy tokenization.

    Args:
        location: Raw location string
        nlp: spaCy language model

    Returns:
        Extracted address or empty string
    """
    if not location:
        return ""
    
    doc = nlp(location)
    tokens = [token.text for token in doc]
    
    for i, token in enumerate(tokens):
        if token.lower() in ["u", "zbieg", "zbiegu"]:
            j = i + 1
            if j < len(tokens) and tokens[j].lower() in ["zbiegu", "zbieg"]:
                j += 1
            if j < len(tokens) and tokens[j].lower() in ["ul", "ulica"]:
                j += 1
            if j < len(tokens) and tokens[j] == ".":
                j += 1
            
            street_parts = []
            while j < len(tokens):
                t = tokens[j]
                if t in ["/", "i"]:
                    street_parts.append(t)
                    j += 1
                    if j < len(tokens) and tokens[j].lower() in ["ul", "ulica"]:
                        j += 1
                    if j < len(tokens) and tokens[j] == ".":
                        j += 1
                    continue
                if t in ["w", ",", "."]:
                    break
                if len(t) > 0 and t[0].isupper():
                    street_parts.append(t)
                    j += 1
                else:
                    break
            
            if street_parts:
                return " ".join(street_parts)
    
    for i, token in enumerate(tokens):
        if token.lower() in ["ul", "ulica", "ulicy", "ulice", "przy"]:
            start_idx = i + 1
            if token.lower() == "przy" and start_idx < len(tokens) and tokens[start_idx].lower() in ["ul", "ulica"]:
                start_idx = i + 2
            
            if start_idx >= len(tokens):
                continue
            
            if start_idx < len(tokens) and tokens[start_idx] == ".":
                start_idx += 1
            
            if start_idx >= len(tokens):
                continue
            
            next_token = tokens[start_idx]
            if next_token and len(next_token) > 0 and next_token[0].isupper():
                address_parts = []
                j = start_idx
                while j < len(tokens):
                    t = tokens[j]
                    if t in ["na", "przy", "w"] and j > start_idx:
                        if t == "w" and j + 1 < len(tokens) and tokens[j + 1].lower().startswith("torun"):
                            break
                        if t in ["na", "przy"]:
                            break
                    if t in [",", "."]:
                        break
                    if len(t) > 0 and (t[0].isupper() or t.isdigit() or t in ["-", "/", "i"] or (t[0].isdigit() and any(c.isalpha() for c in t))):
                        address_parts.append(t)
                        j += 1
                        if j < len(tokens) and tokens[j] == "/" and j + 1 < len(tokens) and tokens[j + 1].isdigit():
                            address_parts.append(tokens[j])
                            j += 1
                            address_parts.append(tokens[j])
                            j += 1
                    else:
                        break
                
                if address_parts:
                    return " ".join(address_parts)
    
    for i, token in enumerate(tokens):
        if token.lower() in ["rynek", "rynku"]:
            j = i
            rynek_parts = []
            while j < len(tokens):
                t = tokens[j]
                if t in [",", "."]:
                    break
                if len(t) > 0 and t[0].isupper():
                    rynek_parts.append(t)
                    j += 1
                else:
                    break
            
            if len(rynek_parts) >= 2:
                return " ".join(rynek_parts)
    
    for i, token in enumerate(tokens):
        if len(token) > 0 and token[0].isupper() and i + 1 < len(tokens) and tokens[i + 1].isdigit():
            address_parts = [token, tokens[i + 1]]
            j = i + 2
            if j < len(tokens) and tokens[j] == "/" and j + 1 < len(tokens) and tokens[j + 1].isdigit():
                address_parts.extend([tokens[j], tokens[j + 1]])
                j += 2
            while j < len(tokens) and (tokens[j] in ["-"] or (len(tokens[j]) > 0 and tokens[j][0].isdigit() and any(c.isalpha() for c in tokens[j]))):
                address_parts.append(tokens[j])
                j += 1
            return " ".join(address_parts)
    
    district_keywords = [
        "Bydgoskie Przedmieście", "Chełmińskie Przedmieście", "Czerniewice",
        "Kaszczorek", "Rudak", "Rubinkowo", "Skarpa", "Podgórz", "Glinki"
    ]
    for district in district_keywords:
        if district.lower() in location.lower():
            return district
    
    if "toruń" in location.lower() and len(location.split()) <= 3:
        return "Toruń"
    
    return ""


def clean_address_for_geocoding(address: str) -> str:
    """
    Clean address string for better geocoding results.

    Args:
        address: Extracted address string

    Returns:
        Cleaned address string
    """
    if not address:
        return ""
    
    cleaned = address
    
    cleaned = re.sub(r"^(?:[Uu]l\.|[Uu]lica|[Uu]licy)\s*", "", cleaned)
    
    cleaned = re.sub(r",?\s*\d{2}-\d{3}\s+Toruń.*", "", cleaned)
    cleaned = re.sub(r",?\s*Toruń.*", "", cleaned)
    
    cleaned = re.sub(r"\.$", "", cleaned)
    
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    return cleaned


def geocode_location(address: str, http: urllib3.PoolManager) -> tuple[float, float] | None:
    """
    Geocode address string to lat/lon using Nominatim API.

    Args:
        address: Address string to geocode
        http: urllib3 PoolManager instance

    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    if not address:
        return None
    
    cleaned = clean_address_for_geocoding(address)
    if not cleaned:
        return None
    
    query = f"{cleaned}, Toruń, Poland"
    params = {
        "q": query,
        "format": "json",
        "limit": "1"
    }
    url = f"https://nominatim.openstreetmap.org/search?{urlencode(params)}"
    
    headers = {"User-Agent": "torun-budzet-visualization"}
    
    response = http.request("GET", url, headers=headers)
    time.sleep(1)
    
    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        if data:
            result = data[0]
            return float(result["lat"]), float(result["lon"])
    
    return None


def test_known_good_locations(entries: list[dict[str, Any]]) -> None:
    """
    Test that known good locations still parse correctly.

    Args:
        entries: List of extracted budget entries
    """
    known_good: dict[tuple[str, str], tuple[float, float]] = {
    }
    
    if not known_good:
        return
    
    failures = []
    
    for entry in entries:
        key = (entry["name"], entry["location"])
        if key in known_good:
            expected_lat, expected_lon = known_good[key]
            actual_lat = entry.get("lat")
            actual_lon = entry.get("lon")
            
            if actual_lat is None or actual_lon is None:
                failures.append(f"Missing coordinates for: {entry['name']}")
            elif abs(actual_lat - expected_lat) > 0.001 or abs(actual_lon - expected_lon) > 0.001:
                failures.append(f"Coordinates changed for: {entry['name']}\n  Expected: ({expected_lat}, {expected_lon})\n  Got: ({actual_lat}, {actual_lon})")
    
    if failures:
        print("LOCATION PARSING TEST FAILURES:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        sys.exit(1)


def extract_budget_data(pdf_path: str) -> list[dict[str, Any]]:
    """
    Extract budget data from PDF table.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of budget entries with name, location, value, and category
    """
    nlp = spacy.load("pl_core_news_sm")
    http = urllib3.PoolManager()
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
                    
                    address = extract_address_from_location(location, nlp)
                    address_manual = get_manual_address(name, location)
                    
                    entry = {
                        "name": name,
                        "location": location,
                        "address": address,
                        "address_manual": address_manual,
                        "value": int(value_digits),
                        "category": category_digits,
                        "description": description
                    }
                    
                    geocode_address = address_manual if address_manual else address
                    coords = geocode_location(geocode_address, http)
                    if coords:
                        entry["lat"], entry["lon"] = coords
                    
                    entries.append(entry)

    return entries


def main() -> None:
    pdf_path = "noupload/2024/Projekty wybrane przez mieszkancow w procedurze budzetu obywatelskiego.pdf"

    entries = extract_budget_data(pdf_path)
    
    test_known_good_locations(entries)

    output = json.dumps(entries, ensure_ascii=False, indent=2)
    print(output)


if __name__ == "__main__":
    main()
