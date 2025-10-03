#!/usr/bin/env python3
"""Find entries that fail geocoding and output them for manual address assignment."""

import json
import sys

json_path = "budzet_obywatelski.json"

with open(json_path, "r", encoding="utf-8") as f:
    entries = json.load(f)

failed = []
succeeded = []

for entry in entries:
    if "lat" not in entry or "lon" not in entry:
        failed.append({
            "name": entry["name"],
            "location": entry["location"],
            "address": entry["address"],
            "address_manual": entry["address_manual"]
        })
    else:
        succeeded.append({
            "name": entry["name"],
            "location": entry["location"],
            "lat": entry["lat"],
            "lon": entry["lon"]
        })

print(f"Total entries: {len(entries)}", file=sys.stderr)
print(f"Succeeded geocoding: {len(succeeded)}", file=sys.stderr)
print(f"Failed geocoding: {len(failed)}", file=sys.stderr)
print(file=sys.stderr)
print("FAILED ENTRIES (add these to get_manual_address):", file=sys.stderr)
print(file=sys.stderr)

for entry in failed:
    key = f'        ("{entry["name"]}", "{entry["location"]}"): "Reja 1",'
    print(key)

print(file=sys.stderr)
print(file=sys.stderr)
print("SUCCEEDED ENTRIES (add these to test_known_good_locations):", file=sys.stderr)
print(file=sys.stderr)

for entry in succeeded:
    key = f'        ("{entry["name"]}", "{entry["location"]}"): ({entry["lat"]}, {entry["lon"]}),'
    print(key)
