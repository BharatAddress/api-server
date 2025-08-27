#!/usr/bin/env python3
import json
from pathlib import Path
from main import app


def main():
    out = Path("openapi.json")
    out.write_text(json.dumps(app.openapi(), indent=2))
    print(f"Wrote {out.resolve()}")


if __name__ == "__main__":
    main()

