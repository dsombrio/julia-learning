# CRM Database Schema

## Overview
- SQLite for mobile (offline-first)
- PostgreSQL for web backend
- Sync between local SQLite and cloud PostgreSQL

---

## Tables

### 1. companies
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | TEXT | Company name |
| type | TEXT | Company type (builder, contractor, distributor, etc.) |
| address | TEXT | Full address |
| city | TEXT | City |
| state | TEXT | State |
| zip | TEXT | ZIP code |
| metro_area | TEXT | Derived from address (Austin, Houston, etc.) |
| metro_radius | INTEGER | 50-mile radius from metro center (optional) |
| latitude | DECIMAL | GPS latitude (for radius calc) |
| longitude | DECIMAL | GPS longitude (for radius calc) |
| phone | TEXT | Company phone |
| website | TEXT | Company website |
| notes | TEXT | General company notes |
| created_at | DATETIME | When added |
| updated_at | DATETIME | Last update |
| last_visited | DATETIME | Last visit/contact |
| user_id | UUID | Owner (for multi-user) |

### 2. contacts
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key → companies |
| first_name | TEXT | Contact first name |
| last_name | TEXT | Contact last name |
| position | TEXT | Job title |
| cell_phone | TEXT | Mobile number |
| email | TEXT | Email address |
| is_primary | BOOLEAN | Primary contact for company |
| created_at | DATETIME | When added |
| updated_at | DATETIME | Last update |

### 3. products
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | TEXT | Product name |
| category | TEXT | Category (windows, doors, hardware, etc.) |
| is_active | BOOLEAN | Available for new deals |
| is_other | BOOLEAN | Is "other" custom entry |
| created_at | DATETIME | When added |

**Default Products (Checkbox List):**
- Single-Family Windows
- Multi-Family Windows
- Luxury Windows
- Door Parts
- Doors
- Door Hardware
- Closets/Shelving
- Residential Doors
- Commercial Doors
- Other (free text)

### 4. deals
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key → companies |
| name | TEXT | Deal/project name |
| value | DECIMAL | Deal value in $ |
| stage | TEXT | Stage (prospect, proposal, negotiation, won, lost) |
| status | TEXT | Active, closed_won, closed_lost |
| probability | INTEGER | 0-100% |
| expected_close | DATE | Expected close date |
| notes | TEXT | Deal notes |
| created_at | DATETIME | When created |
| updated_at | DATETIME | Last update |
| closed_at | DATETIME | When closed |

### 5. deal_products
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| deal_id | UUID | Foreign key → deals |
| product_id | UUID | Foreign key → products |
| product_other_text | TEXT | If "other" product selected, enter custom text |
| quantity | INTEGER | Quantity |
| unit_price | DECIMAL | Price per unit |
| total_price | DECIMAL | Total |

### 6. interactions
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key → companies |
| contact_id | UUID | Foreign key → contacts (optional) |
| type | TEXT | type (call, email, meeting, site_visit, note) |
| subject | TEXT | Brief subject |
| notes | TEXT | Detailed notes (supports voice-to-text) |
| follow_up_required | BOOLEAN | Needs follow-up |
| follow_up_date | DATE | When to follow up |
| created_at | DATETIME | When logged |
| user_id | UUID | Who logged it |

### 7. tasks
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key → companies |
| contact_id | UUID | Foreign key → contacts (optional) |
| deal_id | UUID | Foreign key → deals (optional) |
| title | TEXT | Task title |
| description | TEXT | Task details |
| due_date | DATETIME | When due |
| completed | BOOLEAN | Is done |
| completed_at | DATETIME | When completed |
| created_at | DATETIME | When created |
| user_id | UUID | Owner |

### 8. business_cards
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| company_id | UUID | Foreign key → companies (created from scan) |
| contact_id | UUID | Foreign key → contacts (created from scan) |
| image_url | TEXT | Path to scanned image |
| raw_text | TEXT | OCR raw text |
| scanned_at | DATETIME | When scanned |
| user_id | UUID | Who scanned it |

### 9. users
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | TEXT | Login email |
| name | TEXT | Display name |
| role | TEXT | admin, user |
| created_at | DATETIME | When added |

### 10. sync_queue
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| table_name | TEXT | Table that changed |
| record_id | UUID | Record that changed |
| action | TEXT | insert, update, delete |
| data | JSON | Changed data |
| created_at | DATETIME | When queued |
| synced_at | DATETIME | When synced (null if not yet) |

---

## Lead Status (derived from deal stage)
| Status | Definition |
|--------|------------|
| Prospect | First contact, no deal yet |
| Unqualified Lead | Contacted but not interested |
| Qualified Lead | Interested, deal in progress |
| Customer | Won deal |
| Former Customer | Past customer (lost deal or inactive) |

---

## Metro Areas (auto-detected from address, 50-mile radius)
- Austin (50 mi)
- Houston (50 mi)
- Dallas-Fort Worth (50 mi)
- San Antonio (50 mi)
- College Station (50 mi)
- Waco (50 mi)
- Killeen-Temple (50 mi)
- Other (manual entry)

**How it works:**
1. User enters company address
2. System geocodes address (Google Maps API) → lat/lng
3. System calculates 50-mile radius from metro center
4. Companies within radius are tagged with that metro area
5. Users can filter by metro area for geographic routing

---

## Indexes (for performance)
- companies: name, metro_area, user_id
- contacts: company_id, email
- deals: company_id, stage, status
- interactions: company_id, created_at
- tasks: user_id, due_date, completed

---

## API Endpoints (REST)
```
POST   /api/companies          Create company
GET    /api/companies          List companies (with filters)
GET    /api/companies/:id      Get company details
PUT    /api/companies/:id      Update company
DELETE /api/companies/:id     Delete company

POST   /api/contacts          Create contact
GET    /api/contacts          List contacts
PUT    /api/contacts/:id      Update contact

POST   /api/deals             Create deal
GET    /api/deals             List deals (with filters)
PUT    /api/deals/:id         Update deal

POST   /api/interactions      Log interaction
GET    /api/interactions      List interactions

POST   /api/tasks             Create task
GET    /api/tasks             List tasks (user's todo list)
PUT    /api/tasks/:id         Complete task

POST   /api/business-cards/scan   Scan business card

GET    /api/search            Search companies, contacts, deals
```

---

*Last updated: March 10, 2026*
