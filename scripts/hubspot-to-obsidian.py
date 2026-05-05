#!/usr/bin/env python3
"""
hubspot-to-obsidian.py
Pulls all HubSpot contacts + deals and generates Obsidian note files.
Run: python3 hubspot-to-obsidian.py [vault_path]
"""

import sys, os, json, urllib.request, time, pathlib
from datetime import datetime

# ── CONFIG ──────────────────────────────────────────────────────────────────
HUBSPOT_KEY = 'pat-na1-a59cdfa5-fa0f-4b5e-b738-feb6665d32fd'
HEADERS = {'Authorization': f'Bearer {HUBSPOT_KEY}', 'Content-Type': 'application/json'}

VAULT_PATH = sys.argv[1] if len(sys.argv) > 1 else '/Users/tradbot/Library/Mobile Documents/com~apple~CloudDocs/Obsidian Vault'
# ^ update this to your actual vault path

# ── HELPERS ───────────────────────────────────────────────────────────────
def hubspot_search(endpoint, body, limit=100):
    url = f'https://api.hubapi.com{endpoint}'
    payload = json.dumps(body).encode()
    req = urllib.request.Request(url, data=payload, headers=HEADERS)
    resp = json.loads(urllib.request.urlopen(req).read())
    return resp.get('results', []), resp.get('paging', {}).get('next', {}).get('after')

def get_all(endpoint, body, limit=100):
    results, after = hubspot_search(endpoint, body)
    while after:
        more, after = hubspot_search(endpoint, {**body, 'after': after})
        results.extend(more)
        time.sleep(0.3)
    return results

def slug(name):
    """Safe filename from any string"""
    return ''.join(c if c.isalnum() or c in ' -_' else '' for c in name).strip()[:60]

def frontmatter_key(k): return k.lower().replace(' ', '_')

# ── TEMPLATES ──────────────────────────────────────────────────────────────

CONTACT_TEMPLATE = """---
type: contact
id: {id}
created: {created}
tags:
  - CRM
  - contact
  - territory/{territory}
  - product/{product}
links:
  - [[companies/{company_slug}]]

# Contact Information
First Name:: {first_name}
Last Name:: {last_name}
Full Name:: {full_name}
Company:: [[companies/{company_slug}|{company}]]
Job Title:: {job_title}
Email:: mailto:{email}
Phone:: tel:{phone}
Mobile:: tel:{mobile}

# Location
City:: {city}
State:: {state}

# Pipeline
Stage:: {stage}
Lead Source:: {lead_source}
Last Contact:: {last_contact}
Next Step:: {next_step}
Follow-up Date:: {followup_date}

# Notes
# Background::
# Decision Maker::
# Budget::
# Timeline::
---

## History

| Date | Type | Summary | Outcome |
|------|------|---------|---------|
| {last_contact} | initial | Imported from HubSpot | — |

## Related Deals

```dataview
TABLE deal-name AS "Deal", amount AS "Value", stage AS "Stage"
FROM "CRM/Deals"
WHERE contains(contact-name, "{full_name}")
SORT close-date ASC
```
"""

COMPANY_TEMPLATE = """---
type: company
id: {id}
created: {created}
tags:
  - CRM
  - company
  - territory/{territory}
  - product/{product}
links:
  - [[contacts/{contact_slug}]]

# Company Information
Company Name:: {company}
Industry:: {industry}
Website:: {website}
Address:: {address}
City:: {city}
State:: {state}

# Pipeline
Stage:: {stage}
Lead Source:: {lead_source}
Last Contact:: {last_contact}

# Notes
# About::
# Key Products Carried::
# Current Suppliers::
# Decision Maker::
---

## Active Deals

```dataview
TABLE deal-name AS "Deal", amount AS "Value", stage AS "Stage"
FROM "CRM/Deals"
WHERE company = "{company}"
SORT close-date ASC
```

## Contacts

```dataview
TABLE job-title AS "Title", phone AS "Phone", email AS "Email"
FROM "CRM/Contacts"
WHERE company = "{company}"
```

## Notes

> {notes}
"""

# ── MAIN ─────────────────────────────────────────────────────────────────
def main():
    vault = pathlib.Path(VAULT_PATH)
    contacts_dir = vault / 'CRM' / 'Contacts'
    companies_dir = vault / 'CRM' / 'Companies'
    deals_dir = vault / 'CRM' / 'Deals'

    for d in [contacts_dir, companies_dir, deals_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Pull contacts from HubSpot
    print("Fetching HubSpot contacts...")
    contacts = get_all('/crm/v3/objects/contacts/search', {
        'limit': 100,
        'properties': ['firstname','lastname','email','phone','company',
                       'jobtitle','city','state','hs_lead_status','notes_last_updated']
    })
    print(f"  → {len(contacts)} contacts")

    companies = {}  # name → slug
    created = 0

    for c in contacts:
        p = c.get('properties', {})
        fn = (p.get('firstname') or '').strip()
        ln = (p.get('lastname') or '').strip()
        company = (p.get('company') or '').strip()
        full = f"{fn} {ln}".strip()
        if not full: full = company or 'Unknown'
        if not fn and not ln: fn = full

        cs = slug(company) if company else 'unknown-company'
        companies.setdefault(company, cs)

        stage = p.get('hs_lead_status') or 'imported'
        last = p.get('notes_last_updated') or ''
        if last: last = last[:10]

        note = CONTACT_TEMPLATE.format(
            id=c.get('id',''),
            created=c.get('createdAt','')[:10],
            first_name=fn,
            last_name=ln,
            full_name=full,
            company_slug=cs,
            company=company,
            job_title=p.get('jobtitle') or '—',
            email=p.get('email') or '—',
            phone=p.get('phone') or '—',
            mobile='—',
            city=p.get('city') or '—',
            state=p.get('state') or '—',
            territory='texas-oklahoma',  # default; can refine per contact
            product='building-materials',
            stage=stage.replace('_',' ').title(),
            lead_source='HubSpot Import',
            last_contact=last,
            next_step='—',
            followup_date='—'
        )

        fname = contacts_dir / f"{slug(full)}.md"
        # Don't overwrite if exists (preserve edits)
        if not fname.exists():
            fname.write_text(note)
            created += 1
        else:
            print(f"  SKIP (exists): {full}")

    # Pull deals from HubSpot
    print("Fetching HubSpot deals...")
    deals = get_all('/crm/v3/objects/deals/search', {
        'limit': 100,
        'properties': ['dealname','amount','dealstage','closedate','hubspot_owner_id',
                        'notes_last_updated','associatedCompanyId']
    })
    print(f"  → {len(deals)} deals")

    for d in deals:
        p = d.get('properties', {})
        deal_name = (p.get('dealname') or '').strip()
        if not deal_name: continue

        stage = p.get('dealstage') or 'imported'
        amount = p.get('amount') or '0'
        close = p.get('closedate') or ''
        if close: close = close[:10]

        note = f"""---
type: deal
id: {d.get('id','')}
created: {d.get('createdAt','')[:10]}
tags:
  - CRM
  - deal
  - product/building-materials
  - territory/texas-oklahoma
  - stage/{stage}

# Deal Overview
Deal Name:: {deal_name}
Company:: [[companies/{slug(deal_name)}|{deal_name}]]
Stage:: {stage.replace('_',' ').title()}
Estimated Value:: ${float(amount or 0):,.0f}
Close Date:: {close}

# Notes
# Why We Won/Lost::
# Special Terms::
---

## Stage History

| Date | Stage | Notes | Owner |
|------|-------|-------|-------|
| {d.get('createdAt','')[:10]} | {stage.replace('_',' ').title()} | Imported from HubSpot | — |

## Tasks

- [ ] Follow up on {deal_name}
"""

        dname = deals_dir / f"{slug(deal_name)}.md"
        if not dname.exists():
            dname.write_text(note)
        else:
            print(f"  SKIP (exists): {deal_name}")

    print(f"\nDone — {created} contact notes created")
    print(f"Vault: {VAULT_PATH}")
    print(f"Contacts: {contacts_dir}")
    print(f"Deals: {deals_dir}")

if __name__ == '__main__':
    main()
