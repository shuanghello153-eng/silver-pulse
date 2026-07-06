#!/usr/bin/env python3
"""
fix_funding_format.py — Batch fix funding display formats.

Rules:
- If amount is a pure number (e.g. "100000000"), format as "$1.0亿" or "$5000万"
- If amount is already Chinese text (e.g. "上亿融资"), keep as-is
- display format: "{round} {formatted_amount} ({date})" or "{round} {formatted_amount}"
- For funding_total: "累计 {formatted_amount}"
"""
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FILE_PATH = os.path.join(DATA_DIR, "enterprise/all_enterprises.json")


def format_amount(amount_str):
    """Format a numeric amount string to Chinese readable format."""
    if not amount_str:
        return ""

    # Try to parse as number
    try:
        # Remove any non-numeric chars except dots
        cleaned = re.sub(r"[^\d.]", "", str(amount_str))
        if not cleaned or cleaned == ".":
            return str(amount_str)  # Not a number, return as-is

        num = float(cleaned)

        # Already Chinese text like "亿元级", "数千万", "上亿融资" etc.
        if not str(amount_str).replace(".", "").isdigit():
            return str(amount_str)

        # Format based on magnitude
        if num >= 1_0000_0000:  # >= 1亿
            yi = num / 1_0000_0000
            if yi == int(yi):
                return f"${int(yi)}亿"
            return f"${yi:.1f}亿"
        elif num >= 1_0000:  # >= 1万
            wan = num / 1_0000
            if wan == int(wan):
                return f"${int(wan)}万"
            return f"${wan:.1f}万"
        else:
            return f"${num:.0f}"
    except (ValueError, TypeError):
        return str(amount_str)


def fix_funding_display(fund_obj, is_total=False):
    """Fix display field of a funding dict."""
    if not fund_obj or not isinstance(fund_obj, dict):
        return fund_obj

    amount = fund_obj.get("amount", "")
    round_name = fund_obj.get("round", "")
    date = fund_obj.get("date", "")

    # Skip if no display or already good
    if not amount:
        return fund_obj

    # Check if amount is a pure number
    is_numeric = False
    try:
        cleaned = re.sub(r"[^\d.]", "", str(amount))
        if cleaned and cleaned != "." and float(cleaned) > 0:
            is_numeric = str(amount).replace(".", "").isdigit()
    except (ValueError, TypeError):
        pass

    if is_numeric:
        formatted = format_amount(amount)
    else:
        # Already text, keep as-is
        formatted = str(amount)

    # Build display
    if is_total:
        # funding_total: "累计 {formatted}"
        display = f"累计{formatted}"
    else:
        # funding_latest: "{round} {formatted} ({date})"
        parts = []
        if round_name:
            parts.append(str(round_name))
        parts.append(formatted)
        if date:
            parts.append(f"({date})")
        display = " ".join(parts)

    fund_obj["display"] = display
    return fund_obj


def main():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    fixed_count = 0
    for e in data:
        changed = False

        # Fix funding_latest
        fl = e.get("funding_latest")
        if fl and isinstance(fl, dict):
            old_display = fl.get("display", "")
            new_fl = fix_funding_display(fl, is_total=False)
            if new_fl and new_fl.get("display", "") != old_display:
                changed = True

        # Fix funding_total
        ft = e.get("funding_total")
        if ft and isinstance(ft, dict):
            old_display = ft.get("display", "")
            new_ft = fix_funding_display(ft, is_total=True)
            if new_ft and new_ft.get("display", "") != old_display:
                changed = True

        if changed:
            fixed_count += 1

    # Save
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Fixed {fixed_count}/{len(data)} enterprises' funding display")

    # Show samples of fixed entries
    print("\n=== After fix: funding_latest samples ===")
    count = 0
    for e in data:
        fl = e.get("funding_latest")
        if fl and isinstance(fl, dict) and fl.get("display"):
            print(f"  {e['name']}: {fl['display']}")
            count += 1
            if count >= 15:
                break

    print("\n=== After fix: funding_total samples ===")
    count = 0
    for e in data:
        ft = e.get("funding_total")
        if ft and isinstance(ft, dict) and ft.get("display") and ft["display"] != "累计未披露":
            print(f"  {e['name']}: {ft['display']}")
            count += 1
            if count >= 10:
                break


if __name__ == "__main__":
    main()
