#!/usr/bin/env python3
"""
Beach Safety Lookup CLI
Quick beach conditions from the command line.

Usage:
    python3 beach_lookup.py "Miami Beach"
    python3 beach_lookup.py "Waikiki Beach, Oahu"
    python3 beach_lookup.py "Bondi Beach, Sydney"
    python3 beach_lookup.py --list    # list known Florida beaches
"""

import json
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from server import get_comprehensive_report, format_report_text, geocode_beach

BEACHES_FILE = Path(__file__).parent / "beaches.json"

def load_beaches():
    if BEACHES_FILE.exists():
        with open(BEACHES_FILE) as f:
            return {b["name"].lower(): b for b in json.load(f)}
    return {}

def find_beach(name: str, beaches: dict):
    name_lower = name.lower()
    if name_lower in beaches:
        return beaches[name_lower]
    for beach_name, data in beaches.items():
        if name_lower in beach_name or beach_name in name_lower:
            return data
    return None

async def main():
    beaches = load_beaches()

    if len(sys.argv) < 2 or sys.argv[1] == "--list":
        print(f"Florida Beaches ({len(beaches)} total):")
        for name in sorted(beaches.keys()):
            print(f"  {name}")
        print("\n(Any beach worldwide can be looked up by name — try 'Waikiki' or 'Bondi Beach'!)")
        return

    beach_name = " ".join(sys.argv[1:])

    # 1. Try static Florida list first (fast, no external call)
    beach = find_beach(beach_name, beaches)
    if beach:
        lat, lon = beach["lat"], beach["lon"]
        display_name = beach["name"]
        print(f"Checking {display_name} (from local database)...")
    else:
        # 2. Geocode via OpenStreetMap — works for any beach worldwide
        print(f"Looking up {beach_name}...")
        display_name, lat, lon = await geocode_beach(beach_name)
        if lat == 0.0 and lon == 0.0:
            print(f"Beach not found: {beach_name}")
            print("Try adding a state/country, e.g., 'Venice Beach, CA' or 'Bondi Beach, Sydney'")
            return
        beach_name = display_name
        print(f"Found: {display_name}")

    report = await get_comprehensive_report(beach_name, lat, lon, "")
    print(format_report_text(report))

if __name__ == "__main__":
    asyncio.run(main())
