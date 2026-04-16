#!/usr/bin/env python3
"""
=============================================================
  SILENT AUCTION — BID SHEET SCANNER
  Church Auction Night Tool
=============================================================
  WHAT THIS DOES
  --------------
  1. You drop photos of bid sheets into a folder
  2. Run this script
  3. It reads each photo using AI (Claude vision)
  4. It finds the highest bidder on each sheet
  5. It prints a clean winner list AND saves it to winners.csv

  SETUP (one-time, ask your IT friend)
  -----
  pip install anthropic --break-system-packages

  Then set your API key:
    Mac/Linux: export ANTHROPIC_API_KEY="sk-ant-..."
    Windows:   set ANTHROPIC_API_KEY=sk-ant-...

  Get a free API key at: https://console.anthropic.com

  HOW TO USE ON AUCTION NIGHT
  ---------------------------
  1. As sheets come in, take phone photos of each one
  2. AirDrop / email / USB the photos to the laptop
  3. Put all photos in a folder (e.g., "bid_photos")
  4. Run:  python scan_bid_sheets.py bid_photos
  5. See the winner list on screen, and in winners.csv

  TIPS FOR GOOD PHOTOS
  --------------------
  - Lay the sheet flat on a table
  - Good lighting (no shadows across the writing)
  - Hold phone steady, capture the whole sheet
  - Landscape orientation works well for wide sheets

=============================================================
"""

import anthropic
import base64
import csv
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ── Configuration ────────────────────────────────────────────
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

PROMPT = """
You are helping at a church silent auction. I am showing you a photo of a
HANDWRITTEN BID SHEET taken during the auction dinner.

Please carefully read ALL the handwriting on this sheet — it may be cursive,
printed, or messy. Then extract the following information:

1. ITEM NAME or NUMBER at the top of the sheet (if visible)
2. ALL bids listed — each bid typically shows: bidder name, phone/contact (optional), and bid amount
3. The HIGHEST bid amount and the name of that bidder (the WINNER)

Return your answer as a JSON object with this exact structure:
{
  "item_name": "...",
  "item_number": "...",
  "all_bids": [
    {"name": "...", "contact": "...", "amount": 0},
    ...
  ],
  "winner_name": "...",
  "winner_amount": 0,
  "confidence": "high/medium/low",
  "notes": "any hard to read parts or uncertainties"
}

If you cannot read something clearly, make your best guess and note it in
'notes'. For winner_amount, return just the number (e.g., 75 not "$75").
If no bids were placed, set winner_name to "No bids" and winner_amount to 0.
"""

def encode_image(path: Path) -> tuple[str, str]:
    """Read and base64-encode an image. Returns (b64_data, media_type)."""
    ext = path.suffix.lower()
    media_map = {
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
    }
    media_type = media_map.get(ext, 'image/jpeg')
    with open(path, 'rb') as f:
        return base64.standard_b64encode(f.read()).decode('utf-8'), media_type


def scan_sheet(client: anthropic.Anthropic, image_path: Path) -> dict:
    """Send one image to Claude and parse the result."""
    print(f"  📷 Scanning: {image_path.name} ...", end=' ', flush=True)
    try:
        b64, media_type = encode_image(image_path)
        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64
                        }
                    },
                    {
                        "type": "text",
                        "text": PROMPT
                    }
                ]
            }]
        )
        raw = message.content[0].text.strip()

        # Extract JSON from the response (it might be wrapped in markdown code fences)
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)
        result['file'] = image_path.name
        result['error'] = None
        print(f"✅  Winner: {result.get('winner_name', '?')} (${result.get('winner_amount', '?')})")
        return result

    except json.JSONDecodeError as e:
        print(f"⚠️  Could not parse AI response: {e}")
        return {
            'file': image_path.name,
            'item_name': 'PARSE ERROR',
            'item_number': '',
            'all_bids': [],
            'winner_name': 'ERROR — see notes',
            'winner_amount': 0,
            'confidence': 'low',
            'notes': f'JSON parse error: {e}. Raw response saved.',
            'error': str(e)
        }
    except Exception as e:
        print(f"❌  Error: {e}")
        return {
            'file': image_path.name,
            'item_name': 'ERROR',
            'item_number': '',
            'all_bids': [],
            'winner_name': 'ERROR',
            'winner_amount': 0,
            'confidence': 'low',
            'notes': str(e),
            'error': str(e)
        }


def print_summary(results: list[dict]):
    """Print a formatted winner summary to the terminal."""
    width = 70
    print()
    print("=" * width)
    print("  🏆  SILENT AUCTION WINNERS".center(width))
    print(f"  Generated: {datetime.now().strftime('%B %d, %Y  %I:%M %p')}".center(width))
    print("=" * width)

    winners = [r for r in results if r.get('winner_amount', 0) > 0]
    no_bids = [r for r in results if r.get('winner_amount', 0) == 0 and not r.get('error')]
    errors  = [r for r in results if r.get('error')]

    if winners:
        print()
        print(f"  {'ITEM':<32}  {'WINNER':<22}  {'AMOUNT':>8}")
        print(f"  {'-'*32}  {'-'*22}  {'-'*8}")
        for r in sorted(winners, key=lambda x: x.get('winner_amount', 0), reverse=True):
            item  = (r.get('item_name') or r.get('item_number') or r['file'])[:32]
            name  = r.get('winner_name', '')[:22]
            amt   = f"${r.get('winner_amount', 0):,.2f}"
            conf  = ' ⚠️' if r.get('confidence') in ('low', 'medium') else ''
            print(f"  {item:<32}  {name:<22}  {amt:>8}{conf}")
        print()

    if no_bids:
        print(f"  No bids placed on {len(no_bids)} item(s):")
        for r in no_bids:
            print(f"    • {r.get('item_name') or r['file']}")
        print()

    if errors:
        print(f"  ⚠️  Could not read {len(errors)} sheet(s) — check manually:")
        for r in errors:
            print(f"    • {r['file']}: {r['notes']}")
        print()

    print("=" * width)
    print(f"  Total items scanned: {len(results)}")
    print(f"  Items with winners:  {len(winners)}")
    if no_bids:
        print(f"  Items with no bids:  {len(no_bids)}")
    if errors:
        print(f"  Scan errors:         {len(errors)}")
    print("=" * width)
    print()
    print("  ⚠️  Items marked with ⚠️ had low or medium confidence.")
    print("     Please double-check those winner names manually.")
    print()


def save_csv(results: list[dict], output_path: Path):
    """Save results to a CSV file."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'File', 'Item #', 'Item Name', 'Winner Name',
            'Winning Bid', 'Confidence', 'Notes',
            'All Bids (JSON)'
        ])
        for r in results:
            writer.writerow([
                r.get('file', ''),
                r.get('item_number', ''),
                r.get('item_name', ''),
                r.get('winner_name', ''),
                r.get('winner_amount', ''),
                r.get('confidence', ''),
                r.get('notes', ''),
                json.dumps(r.get('all_bids', []))
            ])
    print(f"  💾 Results saved to: {output_path}")


def main():
    # ── Parse arguments ──────────────────────────────────────
    if len(sys.argv) < 2:
        folder = Path('bid_photos')
        print(f"No folder specified. Looking for photos in: ./{folder}/")
    else:
        folder = Path(sys.argv[1])

    if not folder.exists():
        print(f"\n❌  Folder not found: {folder}")
        print(f"\n  Create the folder and put your bid sheet photos in it:")
        print(f"    mkdir {folder}")
        sys.exit(1)

    # ── Find images ──────────────────────────────────────────
    images = sorted([
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ])

    if not images:
        print(f"\n❌  No image files found in: {folder}")
        print(f"  Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(1)

    print(f"\n  Found {len(images)} image(s) in '{folder}/'")
    print(f"  Starting scan with AI vision...\n")

    # ── Check API key ─────────────────────────────────────────
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌  ANTHROPIC_API_KEY not set.")
        print("\n  Get your key at: https://console.anthropic.com")
        print("  Then run:")
        print("    Mac/Linux: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("    Windows:   set ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # ── Scan each image ───────────────────────────────────────
    results = []
    for img in images:
        result = scan_sheet(client, img)
        results.append(result)

    # ── Output ─────────────────────────────────────────────────
    print_summary(results)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = folder.parent / f"winners_{timestamp}.csv"
    save_csv(results, csv_path)


if __name__ == '__main__':
    main()
