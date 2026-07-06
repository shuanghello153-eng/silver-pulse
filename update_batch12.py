"""
Batch 12: Update enterprises with known founding years and website URLs.
"""
import json
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "enterprise", "all_enterprises.json")

KNOWN = {}
