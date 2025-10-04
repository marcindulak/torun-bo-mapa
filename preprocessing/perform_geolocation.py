#!/usr/bin/env python3
"""Perform geolocation on budget entries with manually provided addresses."""

import json
import logging
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stderr)
logger = logging.getLogger(__name__)


def geocode_address(address: str) -> tuple[float, float] | None:
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


def geocode_entries(entries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int, int, int]:
    """
    Geocode entries that have manually provided addresses.

    Args:
        entries: List of budget entries

    Returns:
        Tuple of (entries, newly_geocoded, total_with_coords, total_entries, already_geocoded)
    """
    geocoded_count = 0
    already_geocoded_count = 0
    total_entries = len(entries)

    for entry in entries:
        address = entry.get("address", "")
        
        if "lat" in entry and "lon" in entry:
            already_geocoded_count += 1
            continue
            
        if address:
            coords = geocode_address(address)
            if coords:
                # Round to 5 decimal places (~1.1m precision)
                lat_rounded = round(coords[0], 5)
                lon_rounded = round(coords[1], 5)
                entry["lat"], entry["lon"] = lat_rounded, lon_rounded
                geocoded_count += 1
                logger.info(f"Geocoded: {address} -> ({lat_rounded}, {lon_rounded})")
            else:
                logger.warning(f"Failed to geocode: {address}")

    total_with_coords = geocoded_count + already_geocoded_count
    return entries, geocoded_count, total_with_coords, total_entries, already_geocoded_count


def main() -> None:
    if len(sys.argv) < 2:
        logger.error("Usage: perform_geolocation.py <json_file>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    
    if not json_path.exists():
        logger.error(f"File not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    entries, newly_geocoded, total_with_coords, total_entries, already_geocoded = geocode_entries(entries)

    if newly_geocoded > 0:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        logger.info(f"Successfully geocoded {total_with_coords} out of {total_entries} entries ({newly_geocoded} new, {already_geocoded} already geocoded) - updated {json_path}")
    else:
        logger.info(f"Successfully geocoded {total_with_coords} out of {total_entries} entries (all already geocoded) - no changes needed")


if __name__ == "__main__":
    main()
