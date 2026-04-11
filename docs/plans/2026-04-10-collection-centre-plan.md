# Milk Collection Centre PWA — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a standalone Vite + MUI PWA for milk collection centre agents to record intake, enroll farmers, and view daily summaries.

**Architecture:** Separate `packages/collection/` Vite app using the same MUI theme and API backend. Auth reuses existing OTP flow with cookie-based JWT (role `milk_center` already in `STAFF_ROLES`). Six screens: Login, Intake, Receipt, Enroll, Dashboard, Settlements.

**Tech Stack:** Vite, React 18, TypeScript, MUI 5, React Router v6, Axios, vite-plugin-pwa

**Design doc:** `docs/plans/2026-04-10-collection-centre-ui-design.md`

---

## Task 1: Backend — Aadhaar fields on User model + migration

**Files:**
- Modify: `packages/api/app/models/user.py`
- Create: `packages/api/alembic/versions/xxxx_add_aadhaar_fields.py` (via alembic)

**Step 1: Add aadhaar fields to User model**

In `packages/api/app/models/user.py`, add after `village_code`:

```python
aadhaar_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
aadhaar_last4: Mapped[str | None] = mapped_column(String(4), nullable=True, index=True)
```

**Step 2: Generate and apply migration**

```bash
cd packages/api
alembic revision --autogenerate -m "add aadhaar fields to users"
alembic upgrade head
```

If alembic is not set up, manually add columns:

```sql
ALTER TABLE users ADD COLUMN aadhaar_hash VARCHAR(64);
ALTER TABLE users ADD COLUMN aadhaar_last4 VARCHAR(4);
CREATE INDEX ix_users_aadhaar_last4 ON users(aadhaar_last4);
```

**Step 3: Commit**

```bash
git add packages/api/app/models/user.py
git commit -m "feat: add aadhaar_hash and aadhaar_last4 fields to User model"
```

---

## Task 2: Backend — Farmer search endpoint

**Files:**
- Modify: `packages/api/app/routers/milk_center.py`

**Step 1: Add farmer search endpoint**

Add to `milk_center.py` after existing imports:

```python
from sqlalchemy import or_

@router.get("/farmers/search")
async def search_farmers(
    phone: str | None = Query(None, min_length=3, max_length=15),
    aadhaar_last4: str | None = Query(None, min_length=4, max_length=4),
    name: str | None = Query(None, min_length=2, max_length=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search farmers by phone, last 4 Aadhaar digits, or name."""
    if not any([phone, aadhaar_last4, name]):
        raise HTTPException(status_code=400, detail="At least one search parameter required")

    filters = []
    if phone:
        filters.append(User.phone.ilike(f"%{phone}%"))
    if aadhaar_last4:
        filters.append(User.aadhaar_last4 == aadhaar_last4)
    if name:
        filters.append(User.name.ilike(f"%{name}%"))

    result = await db.execute(
        select(User)
        .where(User.role == "farmer", or_(*filters))
        .limit(10)
    )
    farmers = result.scalars().all()

    return [
        {
            "id": str(f.id),
            "name": f.name,
            "phone": f.phone,
            "aadhaar_last4": f.aadhaar_last4,
            "village_code": f.village_code,
            "district": f.location_district,
        }
        for f in farmers
    ]
```

**Step 2: Verify endpoint works**

```bash
curl http://localhost:8000/v1/milk-center/farmers/search?phone=9876 -H "Cookie: token=<jwt>"
```

**Step 3: Commit**

```bash
git add packages/api/app/routers/milk_center.py
git commit -m "feat: add farmer search endpoint for collection centre"
```

---

## Task 3: Backend — Quick enroll endpoint

**Files:**
- Modify: `packages/api/app/routers/milk_center.py`

**Step 1: Add quick enroll endpoint**

```python
import hashlib

class QuickEnrollRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    aadhaar: str = Field(..., pattern=r"^\d{12}$")
    village_code: str | None = Field(None, max_length=20)

@router.post("/farmers/enroll", status_code=status.HTTP_201_CREATED)
async def quick_enroll_farmer(
    body: QuickEnrollRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Quick-enroll a new farmer at the collection centre."""
    # Check if phone already exists
    existing = await db.execute(select(User).where(User.phone == body.phone))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Phone number already registered")

    # Check Aadhaar dedup via hash
    aadhaar_hash = hashlib.sha256(body.aadhaar.encode()).hexdigest()
    dup_check = await db.execute(select(User).where(User.aadhaar_hash == aadhaar_hash))
    if dup_check.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Aadhaar already registered")

    farmer = User(
        name=body.name,
        phone=body.phone,
        role="farmer",
        aadhaar_hash=aadhaar_hash,
        aadhaar_last4=body.aadhaar[-4:],
        village_code=body.village_code,
        lang_pref="kn",
    )
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)

    return {
        "id": str(farmer.id),
        "name": farmer.name,
        "phone": farmer.phone,
        "aadhaar_last4": farmer.aadhaar_last4,
        "message": "Farmer enrolled successfully",
    }
```

**Step 2: Commit**

```bash
git add packages/api/app/routers/milk_center.py
git commit -m "feat: add quick farmer enroll endpoint with Aadhaar masking"
```

---

## Task 4: Frontend — Vite project scaffold

**Files:**
- Create: `packages/collection/package.json`
- Create: `packages/collection/vite.config.ts`
- Create: `packages/collection/tsconfig.json`
- Create: `packages/collection/index.html`
- Create: `packages/collection/src/main.tsx`
- Create: `packages/collection/src/App.tsx`
- Create: `packages/collection/src/theme.ts`
- Create: `packages/collection/public/manifest.json`

**Step 1: Create package.json**

```json
{
  "name": "@pashuraksha/collection",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --port 3001",
    "build": "tsc && vite build",
    "preview": "vite preview --port 3001"
  },
  "dependencies": {
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.16.0",
    "@mui/material": "^5.16.0",
    "axios": "^1.7.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.23.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.4.0",
    "vite": "^5.4.0",
    "vite-plugin-pwa": "^0.20.0"
  }
}
```

**Step 2: Create vite.config.ts**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: false, // use public/manifest.json
    }),
  ],
  server: {
    port: 3001,
    proxy: {
      "/v1": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
```

**Step 3: Create tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"]
}
```

**Step 4: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#0d6b58" />
    <link rel="manifest" href="/manifest.json" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <title>PashuRaksha - Collection Centre</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**Step 5: Create public/manifest.json**

```json
{
  "name": "PashuRaksha Collection Centre",
  "short_name": "PashuRaksha",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f0f4f3",
  "theme_color": "#0d6b58",
  "icons": []
}
```

**Step 6: Create src/main.tsx**

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider, CssBaseline } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { collectionTheme } from "./theme";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider theme={collectionTheme}>
      <CssBaseline />
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>
);
```

**Step 7: Create src/theme.ts**

Copy the admin theme but export as `collectionTheme`. Same palette, same fonts, same component overrides. This ensures visual consistency.

```typescript
import { createTheme } from "@mui/material/styles";

export const collectionTheme = createTheme({
  palette: {
    primary: { main: "#0d6b58", light: "#e8f5f1", dark: "#094d3f" },
    secondary: { main: "#1e3a5f", light: "#e8eef6" },
    error: { main: "#c0392b", light: "#fdeaea" },
    warning: { main: "#d97706", light: "#fef3c7" },
    success: { main: "#16a34a", light: "#dcfce7" },
    info: { main: "#0369a1", light: "#e0f2fe" },
    background: { default: "#f0f4f3", paper: "#ffffff" },
    text: { primary: "#1a2e2a", secondary: "#5f7a74" },
  },
  typography: {
    fontFamily: '"IBM Plex Sans", system-ui, -apple-system, sans-serif',
  },
  shape: { borderRadius: 10 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, textTransform: "none", fontWeight: 600 },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 14, boxShadow: "0 1px 3px rgba(0,0,0,0.06)" },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": { borderRadius: 8 },
        },
      },
    },
  },
});
```

**Step 8: Create src/App.tsx (shell with routes)**

```tsx
import { Routes, Route, Navigate } from "react-router-dom";

function Placeholder({ name }: { name: string }) {
  return <div style={{ padding: 32 }}>{name} — coming soon</div>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Placeholder name="Login" />} />
      <Route path="/intake" element={<Placeholder name="Intake" />} />
      <Route path="/intake/receipt/:id" element={<Placeholder name="Receipt" />} />
      <Route path="/enroll" element={<Placeholder name="Enroll" />} />
      <Route path="/dashboard" element={<Placeholder name="Dashboard" />} />
      <Route path="/settlements" element={<Placeholder name="Settlements" />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
```

**Step 9: Install dependencies and verify**

```bash
cd packages/collection
npm install
npm run dev
```

Visit `http://localhost:3001/login` — should show "Login — coming soon".

**Step 10: Commit**

```bash
git add packages/collection/
git commit -m "feat: scaffold collection centre Vite+MUI PWA project"
```

---

## Task 5: Frontend — API client + auth hooks

**Files:**
- Create: `packages/collection/src/api/client.ts`
- Create: `packages/collection/src/api/auth.ts`
- Create: `packages/collection/src/hooks/useAuth.tsx`
- Create: `packages/collection/src/components/AuthGuard.tsx`

**Step 1: Create API client (src/api/client.ts)**

```typescript
import axios from "axios";

const api = axios.create({
  baseURL: "/v1",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
```

**Step 2: Create auth API (src/api/auth.ts)**

```typescript
import api from "./client";

export async function requestOtp(phone: string) {
  return api.post("/auth/request-otp", { phone });
}

export async function verifyOtp(phone: string, otp: string, rememberMe: boolean) {
  return api.post("/auth/verify-otp", {
    phone,
    otp,
    remember_me: rememberMe,
    client_type: "web",
  });
}

export async function getMe() {
  return api.get<{ user_id: string; role: string; name: string }>("/auth/me");
}

export async function logout() {
  return api.post("/auth/logout");
}
```

**Step 3: Create auth hook (src/hooks/useAuth.tsx)**

```tsx
import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { getMe, logout as apiLogout } from "../api/auth";

interface AuthUser {
  userId: string;
  role: string;
  name: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  refresh: async () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const { data } = await getMe();
      setUser({ userId: data.user_id, role: data.role, name: data.name });
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleLogout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return (
    <AuthContext.Provider value={{ user, loading, refresh, logout: handleLogout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
```

**Step 4: Create AuthGuard (src/components/AuthGuard.tsx)**

```tsx
import { Navigate } from "react-router-dom";
import { CircularProgress, Box } from "@mui/material";
import { useAuth } from "../hooks/useAuth";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  return <>{children}</>;
}
```

**Step 5: Wire into App.tsx and main.tsx**

Update `main.tsx` to wrap with `AuthProvider`. Update `App.tsx` to wrap protected routes with `AuthGuard`.

**Step 6: Commit**

```bash
git add packages/collection/src/
git commit -m "feat: add API client, auth hooks, and route guard"
```

---

## Task 6: Frontend — Login page

**Files:**
- Create: `packages/collection/src/pages/Login.tsx`
- Modify: `packages/collection/src/App.tsx`

**Step 1: Create Login.tsx**

Mirror the admin login page pattern (from `packages/admin/src/app/login/page.tsx`) but:
- Header says "Collection Centre" instead of "Admin Portal"
- Same OTP flow: phone input → send OTP → 6-digit entry → verify
- On success: `navigate("/intake")` instead of `window.location.href = "/"`
- Uses `requestOtp` and `verifyOtp` from `src/api/auth.ts`
- Same phone validation: `PHONE_REGEX = /^[6-9]\d{9}$/`, prepend `+91`
- Same OTP paste handling, resend cooldown, remember me checkbox

Key differences from admin:
- No `"use client"` directive (not Next.js)
- Uses `useNavigate()` from react-router-dom
- Calls `auth.refresh()` after successful verify to update AuthContext

**Step 2: Commit**

```bash
git add packages/collection/src/pages/Login.tsx packages/collection/src/App.tsx
git commit -m "feat: add collection centre login page with OTP flow"
```

---

## Task 7: Frontend — Centre selection hook

**Files:**
- Create: `packages/collection/src/hooks/useCentre.tsx`
- Create: `packages/collection/src/api/milk.ts`

**Step 1: Create milk API (src/api/milk.ts)**

```typescript
import api from "./client";

export async function receiveMilk(data: {
  center_id: string;
  farmer_user_id: string;
  quantity_liters: number;
  fat_pct: number;
  snf_pct: number;
  shift: "morning" | "evening";
}) {
  return api.post("/milk-center/receive", data);
}

export async function getDailyReport(centerId: string) {
  return api.get(`/milk-center/${centerId}/daily-report`);
}

export async function getFarmerSettlements(centerId: string, days: number = 15) {
  return api.get(`/milk-center/${centerId}/farmer-settlements`, { params: { days } });
}

export async function searchFarmers(params: { phone?: string; aadhaar_last4?: string; name?: string }) {
  return api.get("/milk-center/farmers/search", { params });
}

export async function enrollFarmer(data: {
  name: string;
  phone: string;
  aadhaar: string;
  village_code?: string;
}) {
  return api.post("/milk-center/farmers/enroll", data);
}
```

**Step 2: Create centre hook (src/hooks/useCentre.tsx)**

For the sprint, hardcode a default centre or store selected centre ID in localStorage. The centre selection can be a simple dropdown on first use after login.

```tsx
import { createContext, useContext, useState, ReactNode } from "react";

interface CentreContextValue {
  centreId: string | null;
  centreName: string | null;
  setCentre: (id: string, name: string) => void;
}

const CentreContext = createContext<CentreContextValue>({
  centreId: null,
  centreName: null,
  setCentre: () => {},
});

export function CentreProvider({ children }: { children: ReactNode }) {
  const [centreId, setCentreId] = useState<string | null>(
    localStorage.getItem("collection_centre_id")
  );
  const [centreName, setCentreName] = useState<string | null>(
    localStorage.getItem("collection_centre_name")
  );

  const setCentre = (id: string, name: string) => {
    setCentreId(id);
    setCentreName(name);
    localStorage.setItem("collection_centre_id", id);
    localStorage.setItem("collection_centre_name", name);
  };

  return (
    <CentreContext.Provider value={{ centreId, centreName, setCentre }}>
      {children}
    </CentreContext.Provider>
  );
}

export function useCentre() {
  return useContext(CentreContext);
}
```

**Step 3: Commit**

```bash
git add packages/collection/src/api/milk.ts packages/collection/src/hooks/useCentre.tsx
git commit -m "feat: add milk API client and centre selection context"
```

---

## Task 8: Frontend — NavBar component

**Files:**
- Create: `packages/collection/src/components/NavBar.tsx`

**Step 1: Create NavBar**

Top app bar with:
- Left: PashuRaksha logo/text + centre name
- Center: navigation tabs — Intake | Dashboard | Settlements
- Right: agent name + logout button
- Active tab highlighted
- Uses `useAuth()` for name/logout and `useCentre()` for centre name
- MUI `AppBar` + `Tabs` component

**Step 2: Commit**

```bash
git add packages/collection/src/components/NavBar.tsx
git commit -m "feat: add collection centre navigation bar"
```

---

## Task 9: Frontend — Intake page + FarmerSearch + RatePreview

**Files:**
- Create: `packages/collection/src/pages/Intake.tsx`
- Create: `packages/collection/src/components/FarmerSearch.tsx`
- Create: `packages/collection/src/components/RatePreview.tsx`
- Create: `packages/collection/src/components/ShiftSelector.tsx`
- Create: `packages/collection/src/utils/pricing.ts`

**Step 1: Create pricing util (src/utils/pricing.ts)**

Port the Python `milk_pricing.py` to TypeScript — same slabs, same formula:

```typescript
const FAT_SLABS = [
  { min: 3.0, max: 3.5, rate: 7.50 },
  { min: 3.5, max: 4.0, rate: 8.00 },
  { min: 4.0, max: 4.5, rate: 8.50 },
  { min: 4.5, max: 5.0, rate: 9.00 },
  { min: 5.0, max: 5.5, rate: 9.50 },
  { min: 5.5, max: 6.0, rate: 10.00 },
  { min: 6.0, max: 7.0, rate: 10.50 },
  { min: 7.0, max: 10.0, rate: 11.00 },
];

const SNF_SLABS = [
  { min: 8.0, max: 8.3, rate: 5.00 },
  { min: 8.3, max: 8.5, rate: 5.50 },
  { min: 8.5, max: 8.8, rate: 6.00 },
  { min: 8.8, max: 9.0, rate: 6.50 },
  { min: 9.0, max: 10.0, rate: 7.00 },
];

function getSlabRate(value: number, slabs: { min: number; max: number; rate: number }[]): number {
  for (const slab of slabs) {
    if (value >= slab.min && value < slab.max) return slab.rate;
  }
  if (value >= slabs[slabs.length - 1].max) return slabs[slabs.length - 1].rate;
  return slabs[0].rate;
}

export function calculateRate(fatPct: number, snfPct: number): number {
  const fatRate = getSlabRate(fatPct, FAT_SLABS);
  const snfRate = getSlabRate(snfPct, SNF_SLABS);
  return Math.round(((fatPct * fatRate + snfPct * snfRate) / 2) * 100) / 100;
}
```

**Step 2: Create FarmerSearch component**

- Two tabs: "Phone" | "Aadhaar + Name"
- Phone tab: single text input with debounced search (300ms)
- Aadhaar tab: last-4 input + name input, search on button click
- Results shown as a small dropdown list below
- Selecting a farmer populates the intake form
- "New farmer?" link navigates to `/enroll?returnTo=/intake`
- Uses `searchFarmers()` from api/milk.ts

**Step 3: Create ShiftSelector component**

- Toggle button group: Morning | Evening
- Auto-selects based on current hour (before 12 = morning)
- Agent can override

**Step 4: Create RatePreview component**

- Takes `fatPct`, `snfPct`, `quantity` as props
- Displays: Rate/liter: ₹XX.XX | Total: ₹XXXX.XX
- Updates live using `calculateRate()` from utils/pricing.ts
- Shows "—" when fat/snf are empty

**Step 5: Create Intake page**

Full form layout (tablet-optimized, single column, large inputs):

```
┌─────────────────────────────────┐
│  🔍 Farmer Search               │
│  [FarmerSearch component]        │
├─────────────────────────────────┤
│  Selected: Ramesh Kumar (+91...) │
├─────────────────────────────────┤
│  Quantity (L)  [ ________ ]      │
│  Fat %         [ ________ ]      │
│  SNF %         [ ________ ]      │
├─────────────────────────────────┤
│  Shift: [Morning] [Evening]      │
├─────────────────────────────────┤
│  Rate: ₹32.50/L  Total: ₹325.00│
├─────────────────────────────────┤
│  [ Submit Milk Record ]          │
└─────────────────────────────────┘
```

- Submit calls `receiveMilk()` from api/milk.ts
- On success: navigate to `/intake/receipt/:id`
- Numeric inputs use `inputMode: "decimal"` for mobile keyboards

**Step 6: Commit**

```bash
git add packages/collection/src/
git commit -m "feat: add intake page with farmer search, rate preview, shift selector"
```

---

## Task 10: Frontend — Receipt page

**Files:**
- Create: `packages/collection/src/pages/Receipt.tsx`
- Create: `packages/collection/src/utils/print.css`

**Step 1: Create Receipt page**

- Reads receipt data from `location.state` (passed via navigate from Intake)
- Displays in a card format:
  - Centre name + code (from useCentre)
  - Date, time, shift
  - Farmer name + phone
  - Quantity, Fat%, SNF%
  - Rate per liter, Total amount (INR)
  - Receipt # (first 8 chars of UUID)
- Two buttons: "Print Receipt" + "Next Farmer"
- Print button: `window.print()`

**Step 2: Create print.css**

```css
@media print {
  body * { visibility: hidden; }
  #receipt-content, #receipt-content * { visibility: visible; }
  #receipt-content {
    position: absolute;
    left: 0;
    top: 0;
    width: 80mm;
    font-size: 12px;
    font-family: monospace;
  }
  button { display: none !important; }
}
```

Import in Receipt.tsx: `import "../utils/print.css";`

**Step 3: Commit**

```bash
git add packages/collection/src/pages/Receipt.tsx packages/collection/src/utils/print.css
git commit -m "feat: add printable receipt page for milk collection"
```

---

## Task 11: Frontend — Quick Enroll page

**Files:**
- Create: `packages/collection/src/pages/Enroll.tsx`

**Step 1: Create Enroll page**

Simple form with 4 fields:
- Full name (text)
- Phone (text with +91 prefix, same validation as login)
- Aadhaar (text, 12 digits, masked display as user types: XXXX-XXXX-1234)
- Village (optional text)

Submit calls `enrollFarmer()` from api/milk.ts.

On success:
- If `returnTo` query param exists (from Intake's "New farmer?" link), navigate back to intake with new farmer pre-selected via location state
- Otherwise, show success message + "Enroll Another" button

On duplicate phone/Aadhaar (409): show inline error.

**Step 2: Commit**

```bash
git add packages/collection/src/pages/Enroll.tsx
git commit -m "feat: add quick farmer enroll page with Aadhaar masking"
```

---

## Task 12: Frontend — Dashboard page

**Files:**
- Create: `packages/collection/src/pages/Dashboard.tsx`

**Step 1: Create Dashboard page**

Layout: 4 stat cards + morning/evening split.

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ 245.5 L  │ │ ₹8,240   │ │ 32       │ │ 4.2% Fat │
│ Today's   │ │ Today's   │ │ Farmers  │ │ 8.6% SNF │
│ Milk      │ │ Revenue   │ │ Count    │ │ Avg Qual │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

┌──────────────────────┬──────────────────────┐
│   Morning Shift      │   Evening Shift      │
│   152.3 L · 20       │   93.2 L · 18        │
│   farmers            │   farmers            │
└──────────────────────┴──────────────────────┘
```

- Uses `getDailyReport()` from api/milk.ts
- Auto-refreshes every 60 seconds (for live updates during collection)
- MUI `Card` components matching the admin theme
- Stat values use large typography (h4 weight 700)

**Step 2: Commit**

```bash
git add packages/collection/src/pages/Dashboard.tsx
git commit -m "feat: add daily collection dashboard with shift summary"
```

---

## Task 13: Frontend — Settlements page

**Files:**
- Create: `packages/collection/src/pages/Settlements.tsx`

**Step 1: Create Settlements page**

- Period selector: 3 buttons (15 days | 30 days | 45 days), default 15
- MUI `Table` with columns: Farmer Name, Deliveries, Total Liters, Avg Fat%, Avg SNF%, Total Payout (₹)
- Sorted by payout descending (comes pre-sorted from API)
- Footer row: total farmers + total payout
- Uses `getFarmerSettlements()` from api/milk.ts
- Note: API returns `farmer_user_id`, not name. For the sprint, display the ID. To show names, we'd need a join endpoint — defer to a follow-up task.

**Step 2: Commit**

```bash
git add packages/collection/src/pages/Settlements.tsx
git commit -m "feat: add farmer settlement summary page"
```

---

## Task 14: Integration — Wire all routes + docker-compose

**Files:**
- Modify: `packages/collection/src/App.tsx` (replace placeholders with real pages)
- Modify: `packages/collection/src/main.tsx` (add AuthProvider + CentreProvider)
- Modify: `docker-compose.yml` (add collection service, optional)

**Step 1: Update main.tsx**

Wrap with `AuthProvider` and `CentreProvider`.

**Step 2: Update App.tsx**

Replace all `Placeholder` components with actual page imports. Wrap protected routes with `AuthGuard`. Add `NavBar` to protected routes layout.

**Step 3: Add to docker-compose (optional)**

```yaml
collection:
  build: ./packages/collection
  ports:
    - "3001:3001"
  environment:
    VITE_API_URL: http://api:8000
```

**Step 4: Full smoke test**

```bash
cd packages/collection && npm run dev
# 1. Visit http://localhost:3001 → redirected to /login
# 2. Login with milk_center role user → lands on /intake
# 3. Search farmer → enter milk data → submit → receipt shows
# 4. Navigate to /dashboard → see today's stats
# 5. Navigate to /settlements → see farmer payouts
# 6. Navigate to /enroll → register new farmer → redirected back
```

**Step 5: Commit**

```bash
git add packages/collection/ docker-compose.yml
git commit -m "feat: wire all collection centre routes and complete integration"
```

---

## Task Summary

| # | Task | Type | ~Files |
|---|------|------|--------|
| 1 | Aadhaar fields on User model | Backend | 1 |
| 2 | Farmer search endpoint | Backend | 1 |
| 3 | Quick enroll endpoint | Backend | 1 |
| 4 | Vite project scaffold | Frontend | 8 |
| 5 | API client + auth hooks | Frontend | 4 |
| 6 | Login page | Frontend | 2 |
| 7 | Centre selection hook + milk API | Frontend | 2 |
| 8 | NavBar component | Frontend | 1 |
| 9 | Intake + FarmerSearch + RatePreview | Frontend | 5 |
| 10 | Receipt page | Frontend | 2 |
| 11 | Quick Enroll page | Frontend | 1 |
| 12 | Dashboard page | Frontend | 1 |
| 13 | Settlements page | Frontend | 1 |
| 14 | Wire routes + integration | Frontend | 3 |

**Total: ~33 files, 14 tasks**
