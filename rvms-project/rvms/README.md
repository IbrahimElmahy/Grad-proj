# RVMS — Runway Vision Monitoring System

A production-grade **React 18 + Tailwind CSS** SaaS dashboard for airport runway FOD (Foreign Object Debris) detection and safety monitoring.

---

## Tech Stack

| Layer       | Technology                    |
|-------------|-------------------------------|
| UI          | React 18 + Vite               |
| Styling     | Tailwind CSS v3               |
| Routing     | React Router DOM v6           |
| State       | Zustand v4                    |
| Animation   | Framer Motion v10             |
| Charts      | Recharts v2                   |
| HTTP        | Axios v1 (mock interceptors)  |
| Fonts       | DM Sans + Space Mono          |

---

## Project Structure

```
rvms/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── package.json
└── src/
    ├── main.jsx              # Entry point
    ├── App.jsx               # Root router
    ├── index.css             # Tailwind + global styles
    │
    ├── components/
    │   ├── ui/
    │   │   ├── Badge.jsx       # Severity/status badge
    │   │   ├── Button.jsx      # Animated button
    │   │   ├── Card.jsx        # Card + CardHeader
    │   │   ├── Table.jsx       # Generic data table
    │   │   ├── Toggle.jsx      # Toggle switch
    │   │   ├── StatCard.jsx    # KPI metric card
    │   │   └── SearchModal.jsx # ⌘K search overlay
    │   └── layout/
    │       ├── Sidebar.jsx     # Dark nav sidebar
    │       └── Navbar.jsx      # Top bar w/ clock
    │
    ├── layouts/
    │   └── DashLayout.jsx      # Sidebar + Navbar shell
    │
    ├── pages/
    │   ├── LoginPage.jsx       # Split login with runway visual
    │   ├── DashboardPage.jsx   # Main control center
    │   ├── AlertsPage.jsx      # Filterable alert table
    │   ├── HistoryPage.jsx     # Paginated scan history
    │   └── SettingsPage.jsx    # Profile + system config
    │
    ├── store/
    │   ├── authStore.js        # Zustand auth (persisted)
    │   ├── appStore.js         # Dark mode, scan state, search
    │   └── alertsStore.js      # Alerts filter + resolve
    │
    ├── data/
    │   └── mockData.js         # All mock datasets + chart data
    │
    ├── services/
    │   └── api.js              # Axios mock API service
    │
    └── hooks/
        ├── useScans.js         # Fetch recent scans
        ├── useClock.js         # Live clock hook
        └── usePagination.js    # Generic pagination hook
```

---

## Getting Started

### 1. Install dependencies

```bash
cd rvms
npm install
```

### 2. Start development server

```bash
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173)

### 3. Build for production

```bash
npm run build
npm run preview
```

---

## Login

The login accepts **any email + password** (mock auth).

> Try: `admin@rvms.aero` / `password`

After login you are redirected to the **Dashboard**.

---

## Pages

### 🛫 Login
- Split layout: animated runway SVG on the left, form on the right
- Show/hide password toggle
- Loading spinner on submit
- Persisted login state via Zustand + localStorage

### 📊 Dashboard
- Three stat cards: Runway Status, Last Inspection, System Health
- Manual scan hero card with animated progress bar and real-time result
- Activity feed table (Scan ID, Timestamp, Status, FOD)
- Right sidebar: Alerts today, Resolved alerts, Last scan result, 24h trend chart

### 🚨 Alerts
- Filter tabs: All / Critical / Warning / Safe — with live counts
- Animated table rows (Framer Motion layout animations)
- Resolve alert by clicking "View Details"
- Bottom row: System status, live camera SVG feed, trend area chart

### 📋 History
- Date range + status filters
- Paginated scan table (7 per page)
- Monthly bar chart (total scans vs FOD flags)
- Export CSV button (UI only)

### ⚙️ Settings
- User profile section with avatar
- Dark mode toggle (applies class to `<html>`)
- Notification, email digest, sound toggles
- Scan interval selector + confidence threshold range slider
- Sensor grid (cameras, LIDAR, thermal, radar)
- Save confirmation with animated feedback
- Danger zone buttons

---

## Key Design Decisions

- **No real backend** — all data comes from `src/data/mockData.js` via mock Axios interceptors in `src/services/api.js`
- **Zustand persist** — auth state survives page refresh
- **Framer Motion** — page transitions, row animations, scan progress
- **Recharts** — AreaChart (dashboard + alerts), BarChart (history)
- **Path aliases** — `@/` maps to `src/` via `vite.config.js`
- **Tailwind custom theme** — `brand` color palette + DM Sans / Space Mono fonts

---

## Customisation

| What              | Where                              |
|-------------------|------------------------------------|
| Mock scan data    | `src/data/mockData.js`             |
| Alert rules       | `src/store/alertsStore.js`         |
| Sidebar nav items | `src/components/layout/Sidebar.jsx`|
| Color palette     | `tailwind.config.js` → `brand`     |
| API endpoints     | `src/services/api.js`              |
| Scan logic        | `src/store/appStore.js`            |
