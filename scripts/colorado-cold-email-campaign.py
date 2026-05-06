#!/usr/bin/env python3
"""
Colorado Cold Email Campaign Generator
American Flashings — Building Materials Sales Agency
Generates personalized cold emails for Colorado roofing/lumber prospects.
"""

import csv
import re
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Tuple, Tuple

# ── Config ────────────────────────────────────────────────────────────────────
HUBSPOT_API_KEY = "pat-na1-a59cdfa5-fa0f-4b5e-b738-feb6665d32fd"
HUBSPOT_SEARCH_URL = "https://api.hubapi.com/crm/v3/objects/contacts/search"
HUBSPOT_HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json",
}

PROSPECTS_FILE = "/Users/tradbot/.openclaw/workspace/prospecting/colorado-roofing-lumber-prospects.md"
OUTPUT_CSV = "/Users/tradbot/.openclaw/workspace/colorado-cold-email-campaign.csv"
SCRIPT_PATH = "/Users/tradbot/.openclaw/workspace/scripts/colorado-cold-email-campaign.py"

# ── HubSpot helpers ────────────────────────────────────────────────────────────

def hubspot_search_contact(first_name: str, last_name: str, company: str) -> Optional[dict]:
    """Search HubSpot for a contact by name and company. Returns contact dict or None."""
    payload = {
        "query": f"{first_name} {last_name}",
        "limit": 5,
        "properties": ["firstname", "lastname", "email", "company", "phone", "city", "state"],
    }
    req = urllib.request.Request(
        HUBSPOT_SEARCH_URL,
        data=json.dumps(payload).encode(),
        headers=HUBSPOT_HEADERS,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            results = data.get("results", [])
            for contact in results:
                props = contact.get("properties", {})
                co = props.get("company", "").lower()
                if company.lower() in co or co in company.lower():
                    return props
            # Fallback: return first result if any
            if results:
                return results[0].get("properties", {})
    except Exception as e:
        print(f"    [HubSpot error] {e}")
    return None


def hubspot_search_by_company(company: str) -> Optional[dict]:
    """Search HubSpot for any contact at a given company."""
    payload = {
        "query": company,
        "limit": 5,
        "properties": ["firstname", "lastname", "email", "company", "phone", "city", "state"],
    }
    req = urllib.request.Request(
        HUBSPOT_SEARCH_URL,
        data=json.dumps(payload).encode(),
        headers=HUBSPOT_HEADERS,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            results = data.get("results", [])
            if results:
                return results[0].get("properties", {})
    except Exception as e:
        print(f"    [HubSpot error] {e}")
    return None


# ── Email / name parsing ───────────────────────────────────────────────────────

def make_email_pattern(company_name: str, first: str, last: str) -> str:
    """Build first.last@company.com from company name."""
    domain = company_name.lower()
    domain = re.sub(r"[^a-z0-9\s]", "", domain)
    domain = re.sub(r"\s+", "", domain)
    domain = domain.replace(" ", "") + ".com"
    return f"{first.lower()}.{last.lower()}@{domain}"


def make_info_email(company_name: str) -> str:
    """Build info@company.com from company name."""
    domain = re.sub(r"[^a-z0-9\s]", "", company_name.lower())
    domain = re.sub(r"\s+", "", domain) + ".com"
    return f"info@{domain}"


# ── Company classification ─────────────────────────────────────────────────────

LUMBER_KEYWORDS = ["lumber", "plywood", "millwork", "hardwood", "timber", "building supply"]
ROOFING_KEYWORDS = ["roofing", "roof", "metal roof", "standing seam"]
CHAIN_KEYWORDS = ["qxo", "builders firstsource", "srs distribution", "abc supply", "sutherlands"]

METAL_HOOKS = [
    "Colorado's mild summer dry-spell is ideal for metal roofing installations — no weather delays, clean cuts.",
    "With Denver's hailstorms and freeze-thaw cycles, your customers need a roofing solution that outlasts asphalt.",
    "Colorado's mountain communities are driving demand for standing seam — does your supply chain keep up?",
    "With wildfire season reshaping western roofing priorities, metal is becoming the default for more builders.",
]

STOCK_HOOKS = [
    "We're stocked on the hardware your crews need right now — no special orders, no delays.",
    "When a GC calls Friday afternoon needing hardware, can you deliver from stock? We can.",
    "Custom door hardware that ships same day from our warehouse means your lead times stay short.",
    "We carry full inventory on the products Colorado contractors spec most — so you don't have to wait.",
]

VALID_CITIES = {
    "fort collins", "greeley", "evans", "loveland",
    "denver", "arvada", "wheat ridge",
    "boulder", "la fayette", "longmont",
    "colorado springs", "pueblo",
    "ft. collins",
}

# Things that identify a header/note/table-row as NOT a real company
NON_COMPANY_PATTERNS = [
    re.compile(r"present in market", re.I),
    re.compile(r"^key observations", re.I),
    re.compile(r"^major national", re.I),
    re.compile(r"^ownership changes", re.I),
    re.compile(r"^family-owned gems", re.I),
    re.compile(r"^metal roofing opportunity", re.I),
    re.compile(r"^discount liquidation", re.I),
    re.compile(r"^decking focus", re.I),
]


def is_real_company(company: dict) -> bool:
    """Return False for section headers, notes sections, or non-company entries."""
    name = company.get("name", "")
    # Names ending in colon are section headers
    if name.strip().endswith(":"):
        return False
    # Names with no spaces (single-word section titles)
    if " " not in name.strip() and len(name.strip()) < 6:
        return False
    # Match against known non-company patterns
    for pat in NON_COMPANY_PATTERNS:
        if pat.search(name):
            return False
    # A real company should have at least one of: confirmed email, GM/Owner, phone
    has_owner = bool(company.get("contact_name") or company.get("contact_first"))
    has_phone = bool(company.get("phone") and company["phone"] not in ("Not confirmed", ""))
    has_email = bool(company.get("email_confirmed") and "@" in company["email_confirmed"])
    has_website = bool(company.get("website") and company["website"] not in ("Not confirmed", ""))
    # If it reads like a section header (all caps, long, no owner/phone/email), skip it
    if name.isupper() and not has_owner and not has_phone and not has_email:
        return False
    return True


def classify_company(name: str, products: str) -> Tuple[str, str, str]:
    """
    Classify company type and return (company_type, specific_need, personalized_hook).
    """
    name_lower = name.lower()
    products_lower = products.lower()

    is_lumber = any(k in name_lower or k in products_lower for k in LUMBER_KEYWORDS)
    is_roofing = any(k in name_lower or k in products_lower for k in ROOFING_KEYWORDS)
    is_metal = any(k in products_lower for k in ["metal roofing", "standing seam", "copper", "steel roofing"])
    is_chain = any(k in name_lower for k in CHAIN_KEYWORDS)

    # Metal roofing specialists
    if is_metal:
        hook_idx = hash(name) % len(METAL_HOOKS)
        return ("metal roofing supplier", "standing seam and metal roofing hardware", METAL_HOOKS[hook_idx])

    # Metal-focused by name
    if "metal" in name_lower and is_lumber:
        hook_idx = hash(name) % len(METAL_HOOKS)
        return ("metal building materials supplier", "metal roofing hardware and flashing", METAL_HOOKS[hook_idx])

    # Roofing supply
    if is_roofing or "roof" in name_lower:
        hook = "Colorado's roofing season is short — having a supplier with full stock on shingles, underlayment, and flashing means you're never caught waiting on a reorder."
        return ("roofing materials supplier", "roofing hardware and flashing", hook)

    # Decking/fencing focus
    if "deck" in name_lower or "fence" in name_lower or "pergola" in name_lower:
        hook = "Colorado builders are increasingly spec'ing composite and cedar decking — make sure your yard is stocked when the orders come in."
        return ("decking/fencing supplier", "decking materials and hardware", hook)

    # Lumber/general building supply
    if is_lumber:
        if is_chain:
            hook = "As a larger operation you know the challenge: keeping specialty hardware in stock without carrying excess inventory. We can help fill that gap."
            return ("lumber/building supply (chain)", "specialty hardware and flashing", hook)
        hook_idx = hash(name) % len(STOCK_HOOKS)
        return ("lumber/building supply", "door hardware and specialty flashing", STOCK_HOOKS[hook_idx])

    # Generic fallback
    hook = "Colorado's construction market is active year-round — having a reliable, stocked supplier for door hardware and flashing makes every job easier."
    return ("building materials supplier", "door hardware and flashing", hook)


# ── Markdown parser ────────────────────────────────────────────────────────────

def parse_prospects(path: str) -> list[dict]:
    """Parse the markdown file into a list of company dicts."""
    with open(path) as f:
        content = f.read()

    companies = []
    current_section = ""

    # Split on ## headers (city sections)
    sections = re.split(r"\n##\s+", content)
    # First chunk before any ## is the intro; skip it
    for chunk in sections[1:]:
        lines = chunk.split("\n")
        current_section = lines[0].strip()  # e.g. "FORT COLLINS"
        in_company = False
        company = {}

        for i, line in enumerate(lines[1:], 1):
            # New company starts with ###
            if line.startswith("### "):
                if company and company.get("name"):
                    companies.append(company)
                name = line[4:].strip()
                company = {
                    "name": name,
                    "city": current_section.replace("GREELEY", "Greeley").replace("DENVER / FRONT RANGE", "Denver"),
                    "section": current_section,
                    "website": "",
                    "phone": "",
                    "email_confirmed": "",
                    "email_guessed": "",
                    "contact_name": "",
                    "contact_first": "",
                    "contact_last": "",
                    "products": "",
                    "notes": "",
                    "needs_verification": False,
                }
                in_company = True
                continue

            if not in_company:
                continue

            # Field extraction
            if line.startswith("**City:**"):
                company["city"] = re.search(r"\*\*(City|Location):\*\* (.+)", line).group(2).strip() if re.search(r"\*\*(City|Location):\*\* (.+)", line) else company.get("city", "")
            elif line.startswith("**Website:**"):
                m = re.search(r"\*\*(?:Website|URL):\*\* (.+)", line)
                if m:
                    company["website"] = m.group(1).strip()
            elif line.startswith("**Phone:**"):
                m = re.search(r"\*\*(?:Phone|Tel):\*\* (.+)", line)
                if m:
                    company["phone"] = m.group(1).strip()
            elif line.startswith("**GM/Owner:**"):
                m = re.search(r"\*\*GM/Owner:\*\* (.+)", line)
                if m:
                    raw = m.group(1).strip()
                    parts = raw.split()
                    if len(parts) >= 2:
                        company["contact_name"] = raw
                        company["contact_first"] = parts[0]
                        company["contact_last"] = parts[-1]
                    elif len(parts) == 1:
                        company["contact_name"] = raw
                        company["contact_first"] = parts[0]
            elif line.startswith("**GM/Manager:**"):
                m = re.search(r"\*\*GM/Manager:\*\* (.+)", line)
                if m:
                    raw = m.group(1).strip()
                    parts = raw.split()
                    if len(parts) >= 2:
                        company["contact_name"] = raw
                        company["contact_first"] = parts[0]
                        company["contact_last"] = parts[-1]
            elif line.startswith("**Purchasing:**"):
                m = re.search(r"\*\*Purchasing:\*\* (.+)", line)
                if m and not company.get("contact_name"):
                    raw = m.group(1).strip()
                    parts = raw.split()
                    if len(parts) >= 2:
                        company["contact_name"] = raw
                        company["contact_first"] = parts[0]
                        company["contact_last"] = parts[-1]
            elif line.startswith("**Sales Contacts:**"):
                m = re.search(r"\*\*Sales Contacts:\*\* (.+)", line)
                if m and not company.get("contact_name"):
                    raw = m.group(1).strip()
                    parts = raw.split("(")[0].strip().split()
                    if len(parts) >= 2:
                        company["contact_name"] = raw
                        company["contact_first"] = parts[0]
                        company["contact_last"] = parts[-1]
            elif line.startswith("**Email:**"):
                m = re.search(r"\*\*Email:\*\* (.+)", line)
                if m:
                    email = m.group(1).strip()
                    if email and email != "Not confirmed":
                        company["email_confirmed"] = email
                        if "@" in email:
                            parts = email.split("@")[0].split(".")
                            if len(parts) >= 2:
                                company["contact_first"] = parts[0].capitalize()
                                company["contact_last"] = parts[-1].strip()
            elif line.startswith("**Products/Services:**"):
                company["products"] = line.split(":**", 1)[1].strip()
            elif line.startswith("**Notes:**"):
                company["notes"] = line.split(":**", 1)[1].strip()

        if company and company.get("name"):
            companies.append(company)

    return companies


# ── Email generator ────────────────────────────────────────────────────────────

def generate_email(company: dict, contact_first: str, email_addr: str, email_status: str) -> Tuple[str, str, str, str]:
    """
    Generate personalized email subject and body.
    Returns (subject, body, personalization_notes, needs_verification).
    """
    name = company["name"]
    city = company["city"]
    products = company.get("products", "")
    section = company.get("section", "")

    # City-specific regional reference
    if city.lower() in ["denver", "arvada", "wheat ridge"]:
        region_ref = "Denver metro"
    elif city.lower() in ["fort collins", "greeley", "evans", "loveland"]:
        region_ref = "Northern Colorado"
    elif city.lower() in ["boulder", "la fayette", "longmont"]:
        region_ref = "Boulder County"
    elif city.lower() == "colorado springs":
        region_ref = "Colorado Springs"
    elif city.lower() == "pueblo":
        region_ref = "Pueblo"
    else:
        region_ref = city

    company_type, specific_need, hook = classify_company(name, products)

    first_display = contact_first if contact_first else "there"

    # Subject line
    subject = f"{first_display}, can I help {name} with {specific_need}?"

    # Body
    body = (
        f"Hi {first_display},\n\n"
        f"{hook}\n\n"
        f"I'm with American Flashings — we carry full stock on door hardware, flashing, column wraps, and related building materials. "
        f"Same-day will-call, no special orders needed.\n\n"
        f"For a {region_ref} {company_type}, having a supplier who can turn around custom hardware fast means fewer delays on the job site. "
        f"We work with lumberyards and roofing supply companies throughout Colorado.\n\n"
        f"Open to a 15-minute call this week to see if we're a fit? Happy to stop by if that's easier.\n\n"
        f"— David Sombrio, Tradition Sales"
    )

    notes = (
        f"Company type: {company_type} | "
        f"City: {city} | "
        f"Hook: {hook[:60]}... | "
        f"Email status: {email_status}"
    )

    return subject, body, notes, email_status == "needs_verification"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=== Colorado Cold Email Campaign Generator ===")
    print(f"Parsing prospects from: {PROSPECTS_FILE}")

    companies = parse_prospects(PROSPECTS_FILE)
    print(f"Parsed {len(companies)} raw entries")

    # Filter out non-company entries (section headers, notes rows, etc.)
    companies = [c for c in companies if is_real_company(c)]
    print(f"Filtered to {len(companies)} real companies")

    rows = []

    for i, company in enumerate(companies, 1):
        name = company["name"]
        city = company["city"]
        print(f"\n[{i}/{len(companies)}] {name} ({city})")

        contact_first = company.get("contact_first", "")
        contact_last = company.get("contact_last", "")
        contact_name = company.get("contact_name", "")
        confirmed_email = company.get("email_confirmed", "")
        website = company.get("website", "")

        email_addr = ""
        email_status = ""

        # 1. Use confirmed email from prospects file
        if confirmed_email and "@" in confirmed_email:
            email_addr = confirmed_email
            email_status = "confirmed_from_prospect_file"
            print(f"  Using confirmed email: {email_addr}")
        else:
            # 2. Build guessed email from known contact name + website domain
            if contact_first and contact_last:
                if website and website not in ("Not confirmed", ""):
                    # Derive domain from website: strip protocol, take hostname
                    domain = website.lower()
                    domain = re.sub(r"^https?://(www\.)?", "", domain)
                    domain = re.sub(r"/.*", "", domain)  # remove path
                    domain = domain + ".com" if not domain.endswith(".com") else domain
                    email_addr = f"{contact_first.lower()}.{contact_last.lower()}@{domain}"
                    email_status = "guessed_pattern_from_website"
                    print(f"  Guessed email (from website domain): {email_addr}")
                else:
                    email_addr = make_email_pattern(name, contact_first, contact_last)
                    email_status = "guessed_pattern_from_company_name"
                    print(f"  Guessed email (from company name): {email_addr}")
            elif contact_first and not contact_last:
                email_addr = make_info_email(name)
                email_status = "info@fallback_no_last_name"
                print(f"  No last name known, using info@: {email_addr}")
            else:
                email_addr = make_info_email(name)
                email_status = "info@fallback"
                print(f"  No contact known, using info@: {email_addr}")

        # 3. Enrich with HubSpot (only if no confirmed email)
        hubspot_contact = None
        if not confirmed_email or "@" not in str(confirmed_email):
            print(f"  Searching HubSpot for contact at {name}...")
            time.sleep(1.1)  # Rate limit

            if contact_first and contact_last:
                hubspot_contact = hubspot_search_contact(contact_first, contact_last, name)
            if not hubspot_contact:
                hubspot_contact = hubspot_search_by_company(name)

            if hubspot_contact:
                hs_email = hubspot_contact.get("email", "")
                hs_first = hubspot_contact.get("firstname", "")
                hs_last = hubspot_contact.get("lastname", "")
                if hs_email and "@" in hs_email:
                    email_addr = hs_email
                    contact_first = hs_first or contact_first
                    contact_last = hs_last or contact_last
                    email_status = "hubspot_confirmed"
                    print(f"  HubSpot hit: {hs_email}")
                elif hs_first or hs_last:
                    # Use HubSpot name even if no email
                    contact_first = hs_first or contact_first
                    contact_last = hs_last or contact_last
                    contact_name = f"{contact_first} {contact_last}".strip()
                    email_status = "hubspot_name_only"
                    print(f"  HubSpot found name: {contact_name}, no email")

        # Determine if we need verification
        needs_verification = (
            email_status in ("guessed_pattern_from_website", "guessed_pattern_from_company_name", "info@fallback")
            or not contact_first
            or not contact_last
        )
        if needs_verification and email_status != "hubspot_confirmed":
            email_status = "needs_verification"

        # Generate email
        subject, body, notes, nv_flag = generate_email(company, contact_first, email_addr, email_status)
        needs_verification = needs_verification or nv_flag

        rows.append({
            "Company": name,
            "City": city,
            "Contact Name": contact_name or f"{contact_first} {contact_last}".strip(),
            "Email": email_addr,
            "Subject": subject,
            "Body": body,
            "Personalization Notes": notes,
            "Needs Verification": "YES" if needs_verification else "no",
        })

    # Write CSV
    fieldnames = ["Company", "City", "Contact Name", "Email", "Subject", "Body", "Personalization Notes", "Needs Verification"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n=== DONE ===")
    print(f"Wrote {len(rows)} rows to: {OUTPUT_CSV}")
    verified = sum(1 for r in rows if r["Needs Verification"] == "YES")
    confirmed = sum(1 for r in rows if r["Needs Verification"] == "no")
    print(f"  Confirmed emails: {confirmed}")
    print(f"  Needs verification: {verified}")


if __name__ == "__main__":
    main()