#!/usr/bin/env python3
"""Print the JSON list of published paths to pass as `paths` when reading the live canvas during Sync."""
import json
import pathlib

P = pathlib.Path(__file__).resolve().parent.parent / "workspace" / "project"
names = sorted(p.name for p in P.iterdir() if p.suffix in (".html", ".css", ".json"))
print(json.dumps(["project/" + n for n in names]))
