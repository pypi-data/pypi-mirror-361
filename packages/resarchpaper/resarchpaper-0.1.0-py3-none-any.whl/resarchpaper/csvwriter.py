import csv
from typing import List, Dict, Optional

def write_csv(rows: List[Dict[str, str]], filename: Optional[str] = None) -> None:
    if not rows:
        print("No data to write")
        return

    headers = rows[0].keys()
    if filename:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved {len(rows)} records to '{filename}'")
    else:
        for row in rows:
            print(', '.join(f"{k}: {v}" for k, v in row.items()))
