# CRM Mobile App Architecture

## Tech Stack
- **Framework:** React Native (iOS + Android from one codebase)
- **Language:** TypeScript
- **State:** React Context + SQLite (offline-first)
- **OCR:** Google ML Kit (on-device) or Google Cloud Vision API
- **Maps:** Google Maps SDK
- **Voice-to-text:** React Native Voice or native speech recognition
- **Sync:** Background sync with PostgreSQL backend

---

## App Screens

### 1. Dashboard (Home)
- Today's tasks
- Recent interactions
- Quick actions: Scan Card, Add Contact, Add Deal
- Sync status indicator

### 2. Business Card Scan
- Camera viewfinder
- Capture button
- OCR processing indicator
- Results screen with editable fields:
  - Company name, address, phone, website
  - Contact name, position, cell, email
  - Date auto-populated
  - Product checkboxes
  - Notes (voice-to-text enabled)
  - Follow-up update field
- Save → Creates company + contact + interaction

### 3. Contacts List
- Search bar
- Filters: metro, lead status, last visited
- List view with company name, contact name, status
- Pull-to-refresh

### 4. Contact Detail
- Company info (editable)
- Contact info (editable)
- Deal history
- Interaction history
- Associated tasks
- Add interaction button

### 5. Deals List
- Search by deal name
- Filters: stage, status, value range, products
- Kanban or list view toggle
- Total pipeline value shown

### 6. Deal Detail
- Deal info (name, value, stage)
- Company/contact link
- Products (checkbox list with quantities/pricing)
- Notes
- Associated interactions

### 7. Add/Edit Forms
- Company form
- Contact form
- Deal form
- Product picker (checkbox list)
- Task form

### 8. Task List
- Today's tasks view
- All tasks view
- Filter: completed, due today, overdue
- Swipe to complete
- Tap to view details

### 9. Settings
- User profile
- Sync status
- Offline data management
- Logout

---

## Offline-First Architecture

### Local Storage (SQLite)
```
┌─────────────────────────────────────┐
│           SQLite Database            │
├─────────────────────────────────────┤
│ companies                           │
│ contacts                            │
│ deals                               │
│ deal_products                      │
│ interactions                        │
│ tasks                              │
│ business_cards                     │
│ sync_queue                         │
└─────────────────────────────────────┘
```

### Sync Flow
```
1. User makes change (add contact)
2. Save to SQLite
3. Add to sync_queue
4. Background sync tries to push to server
5. If online: push → mark synced
6. If offline: queue stays → sync later
7. Server changes pull down on sync
8. Conflict resolution: last-write-wins
```

### Sync Status Indicators
- ✓ Synced (green)
- ⏳ Syncing (blue)
- ⚠️ Offline (yellow)
- ✗ Sync failed (red)

---

## API Integration

### Backend (REST API)
```
Base URL: https://api.yourcrm.com

Authentication: JWT tokens
- Login: POST /api/auth/login
- Refresh: POST /api/auth/refresh
- Logout: POST /api/auth/logout

Companies: /api/companies
Contacts: /api/contacts
Deals: /api/deals
Interactions: /api/interactions
Tasks: /api/tasks
Search: /api/search?q=...
```

### Business Card OCR

**Option A: On-device (ML Kit)**
- Free, fast, works offline
- Less accurate for complex cards

**Option B: Google Cloud Vision API**
- More accurate
- Costs ~$1.50/1000 scans
- Requires internet

**Recommendation:** Start with Cloud Vision for accuracy, add ML Kit as fallback

---

## Voice-to-Text

Using native speech recognition:
- iOS: Native Speech framework
- Android: SpeechRecognizer API

Flow:
1. User taps microphone
2. Recording starts
3. User taps stop
4. Speech → text
5. Text inserted into notes field
6. User can edit

---

## Maps Integration

- Google Maps SDK for location
- Geocoding: address → lat/lng
- 50-mile radius filter from metro centers
- Map view of accounts by metro

---

## Security

- JWT authentication
- Tokens stored in secure storage
- SQLite encrypted on device
- HTTPS only
- Optional biometric login

---

## Deployment

### Mobile App
- **iOS:** TestFlight (beta) → App Store
- **Android:** Google Play Console (beta) → Play Store
- Or: Enterprise/Sideload (private distribution)

### Backend
- **VPS:** DigitalOcean, Linode, or similar ($20-50/mo)
- **Docker:** Containerized API + PostgreSQL
- **Domain:** yourcrm.com

---

## Estimated Build Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Schema + Backend | 1 week | Medium |
| Mobile Core (CRUD) | 2 weeks | High |
| Business Card Scan | 1 week | Medium |
| Offline Sync | 1 week | High |
| Voice-to-Text | 3 days | Low |
| Testing | 1 week | Medium |
| **Total** | **~7-8 weeks** | |

---

## Cost Estimate (Tokens for AI Build)

| Phase | Tokens |
|-------|--------|
| Backend API | 100K |
| Mobile CRUD screens | 150K |
| Business card OCR | 50K |
| Offline sync logic | 75K |
| Voice integration | 25K |
| **Total** | **~400K** |

~$80-160 in MiniMax API costs

---

*Last updated: March 10, 2026*
