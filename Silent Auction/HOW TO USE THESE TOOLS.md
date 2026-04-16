# Silent Auction Tools — Quick Guide

Two tools are in this folder. Here's everything you need to know.

---

## Tool 1: Auction Catalog Website
**File:** `auction-catalog.html`

This is a beautiful webpage your church members and guests can open on their phones or any browser to browse all the donated items before and during the auction.

### Before the Event (IT person edits the list)

Open `auction-catalog.html` in any text editor (Notepad, TextEdit, VS Code, etc.) and find the section that says **`const ITEMS = [`** — that's your item list. Each item looks like this:

```
{
  id: 1,
  title: "Weekend Getaway — Napa Valley B&B",
  category: "Travel & Experience",
  desc: "Two nights for two at a charming Napa...",
  donor: "The Johnson Family",
  startBid: 150,
  value: 400,
  table: "Table A · #1",
  photo: "",         ← put a photo filename here, e.g. "photos/item1.jpg"
  icon: "🏡"         ← emoji shown if no photo
},
```

To add a new item, copy one block, paste it after the previous one (separated by a comma), and fill in the details.

### Adding Photos

1. Create a folder called `photos` next to `auction-catalog.html`
2. Put your item photos in there (any name, e.g. `quilt.jpg`)
3. In the item entry, set `photo: "photos/quilt.jpg"`

### Sharing With Guests

- **Simplest:** Connect a laptop to a TV/projector in the dining room — guests can walk up and browse
- **Best:** Ask your IT friend to put the file on a simple free host like Netlify Drop (drag and drop the whole folder at [drop.netlify.com](https://drop.netlify.com)) — then guests can open the URL on their phones
- **Also fine:** Email the HTML file to guests ahead of time so they can open it on their devices

---

## Tool 2: Bid Sheet Scanner
**File:** `scan_bid_sheets.py`

This script reads photos of your handwritten bid sheets using AI and produces a clean list of winners. Your IT friend will set this up.

### One-Time Setup (IT person does this)

1. Install Python if not already installed: [python.org/downloads](https://www.python.org/downloads)
2. Open Terminal (Mac) or Command Prompt (Windows)
3. Run: `pip install anthropic`
4. Get a free API key at [console.anthropic.com](https://console.anthropic.com) → Create account → API Keys
5. Set the key (do this once per session):
   - **Mac:** `export ANTHROPIC_API_KEY="sk-ant-your-key-here"`
   - **Windows:** `set ANTHROPIC_API_KEY=sk-ant-your-key-here`

> **Cost note:** Each photo scan costs roughly $0.02–0.05. Scanning 60 bid sheets will cost about $1–3 total.

### On Auction Night

**Step 1 — Collect photos**
- As bid sheets come in, photograph each one with a phone
- Tips for good photos: flat surface, good light, no shadows, capture the whole sheet

**Step 2 — Get photos to the laptop**
- AirDrop (iPhone → Mac): easiest
- Google Photos / iCloud: sync automatically
- USB cable or email to yourself

**Step 3 — Put photos in a folder**
- Create a folder called `bid_photos` next to the script
- Move all bid sheet photos into it

**Step 4 — Run the scanner**
- Open Terminal / Command Prompt
- Navigate to this folder: `cd "path/to/Silent Auction"`
- Run: `python scan_bid_sheets.py bid_photos`

**Step 5 — Read the results**
- The terminal shows a formatted winner table immediately
- A `winners_[timestamp].csv` file is also saved (open in Excel)

### Sample Output

```
======================================================================
             🏆  SILENT AUCTION WINNERS
          Generated: August 15, 2026  08:42 PM
======================================================================

  ITEM                              WINNER                   AMOUNT
  --------------------------------  ----------------------  --------
  Weekend Getaway — Napa Valley     Patricia Williams        $275.00
  Handmade Quilt - Garden Blooms    Robert & Mary Chen       $210.00
  Professional Portrait Session     James Thompson           $150.00
  ...

  ⚠️ Items marked ⚠️ had low confidence — double-check manually
======================================================================
```

### What the confidence levels mean

- **High** — handwriting was clear, amounts were obvious
- **Medium** — some words were hard to read, result is likely correct
- **Low** — very messy or hard to read, verify manually before announcing

---

## Questions?

Reach out to your IT volunteer or bring this guide to the event. Good luck and God bless the auction! 🙏
