# CRM System Specification

## Overview
A clean, card-based CRM for sales reps to track contacts, deals, tasks, and notes.
- Backend: Node.js + SQLite (local storage)
- Frontend: Single-page app, strike.me inspired
- Auto-backup: Nightly to tradbot@traditionsales.com OneDrive via Graph API

---

## Tech Stack

### Backend
- **Runtime**: Node.js (local Mac Mini)
- **Database**: SQLite (better-sqlite3)
- **API**: Express.js REST API
- **Auth**: JWT tokens
- **File Storage**: SQLite DB at ~/Library/Application Support/TradBot/crm.db
- **Backup**: Graph API → OneDrive (nightly cron)

### Frontend
- **Framework**: Vanilla JS (no framework, fast and simple)
- **Styling**: CSS with CSS variables for theming
- **Icons**: Lucide icons (via CDN)
- **Font**: Inter or system font stack

---

## Data Model

### Users
```
id, email, password_hash, name, created_at
```

### Contacts
```
id, user_id, first_name, last_name, email, phone, company, type (customer/vendor/prospect), metro (austin/dallas/houston/san antonio), notes, created_at, updated_at
```

### Deals
```
id, user_id, contact_id, title, value, stage (lead/prospect/proposal/negotiation/won/lost), notes, created_at, updated_at
```

### Tasks
```
id, user_id, contact_id, deal_id, title, description, due_date, timeframe_minutes, source (manual/plaud), status (pending/completed), created_at, completed_at
```

### Notes
```
id, user_id, contact_id, deal_id, content, created_at
```

---

## UI Design

### Theme
- Clean, minimal strike.me inspired
- Card-based layout
- Subtle shadows, rounded corners (8px)
- Dark mode default (sales reps often in dim offices)
- Accent color: Blue (#3B82F6)

### Pages

#### 1. Dashboard
- Today's tasks (with elapsed time indicators)
- Active deals count + total value
- Recent notes
- Quick add buttons

#### 2. Contacts
- Search bar
- Filter chips (All, Customers, Vendors, Prospects)
- Card grid layout
- Each card: Name, company, email, phone, type badge
- Click to expand/edit

#### 3. Deals
- List view (not Kanban - simpler)
- Stage badge
- Value displayed
- Contact name linked
- Sort by: Date, Value, Stage

#### 4. Tasks (To-Do)
- **Time elapsed display**: Shows "2h ago", "1d 4h ago", etc.
- **Visual urgency**:
  - Normal: Default text color
  - >1 day old: Red text
  - >timeframe: Flashing red background (gentle pulse)
- Add task: Title, description, timeframe (optional), link to contact/deal
- Filter: All, Pending, Completed, Overdue
- Swipe/click to complete

#### 5. Notes
- Simple list
- Per contact or deal
- Timestamp

### Interactions
- Quick-add forms slide in from right
- Confirmation on delete
- Inline editing
- Toast notifications for actions

---

## API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### Contacts
- GET /api/contacts (with search, filter)
- GET /api/contacts/:id
- POST /api/contacts
- PUT /api/contacts/:id
- DELETE /api/contacts/:id

### Deals
- GET /api/deals
- GET /api/deals/:id
- POST /api/deals
- PUT /api/deals/:id
- DELETE /api/deals/:id

### Tasks
- GET /api/tasks
- POST /api/tasks
- PUT /api/tasks/:id
- PATCH /api/tasks/:id/complete
- DELETE /api/tasks/:id

### Notes
- GET /api/notes
- POST /api/notes
- PUT /api/notes/:id
- DELETE /api/notes/:id

### Dashboard
- GET /api/dashboard (today's tasks, active deals, recent notes)

---

## Backup Strategy

- SQLite database stored at: ~/Library/Application Support/TradBot/crm.db
- Nightly cron (2am) exports to OneDrive: /TradBot/backups/crm-YYYY-MM-DD.db
- Uses Graph API with existing Azure AD auth (same as email)

---

## Future Enhancements
- Business card OCR (Google Cloud Vision - commented out for now)
- Email integration
- Calendar sync
- Mobile app
