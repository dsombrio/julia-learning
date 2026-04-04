# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics.

## What Goes Here

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

### HubSpot

- **Token:** pat-na1-a59cdfa5-fa0f-4b5e-b738-feb6665d32fd
- **Scopes:** crm.objects.contacts.read, crm.objects.companies.read, crm.objects.deals.read

#### Available Commands:
- `hubspot contacts` - List contacts
- `hubspot deals` - List open deals
- `hubspot companies` - List companies

### Outlook Calendar

- **Client ID:** af03f985-1424-465a-bdbf-0cee6b59743b
- **Tenant ID:** 3ac44adf-88d3-4ffe-aa18-d7ac71dc866f
- **Client Secret:** yx58Q~ztCwAayJ3XO5650qc9N1cNcXmLbSAfTbRl
- **User:** tradbot@traditionsales.com
- **Password:** C(643400569213os
- **Scopes:** Calendars.Read, Calendars.ReadWrite

---

### Finnhub (Stocks)

- **API Key:** d6f31jhr01qvn4o1lap0d6f31jhr01qvn4o1lapg
- **Stocks Tracked:** CIFR, XXI, BRR, MSTR, SCHD, JEPI, QQQH, DLR, EMXC, STXE, NVDA, TSLA, AAPL, MSFT, GOOGL, AMZN, META
- **Threshold:** Only report moves > 1.5%

### Instagram (@tradition_sales)

- **Username:** tradition_sales
- **Password:** funwid-fatmyx-moMre1
- Used to access Instagram reels for content reference and site builds

---

### CoinGecko (Crypto)

- **Crypto Tracked:** BTC, ZEC, XMR, XAUT (tether-gold)
- **Threshold:** Only report moves > 1.5%

### Daily Brief Config

- **Weather:** Open-Meteo (feels-like temps)
- **Crypto:** CoinGecko
- **Stocks:** Finnhub (only >1.5%)
- **HubSpot:** Filter out closed-won deals
- **Calendar:** Outlook (needs re-auth)
- **Sports:** Texas A&M Football/Baseball, Dallas Stars, NY Mets# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
