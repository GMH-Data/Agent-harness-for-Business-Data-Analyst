# React Glassmorphism Dashboard - Master Implementation Spec
## Project: AI RISSER Enterprise System
## Version: 3.0 (Detailed Menu Architecture)

You are an elite React Architect and UI/UX Engineer. Your objective is to build a massive, highly sophisticated, and visually stunning Dashboard for the **AI RISSER Data & Agentic System**. This is a **Glassmorphism-first** design. The entire application acts as a frosted glass pane floating over an ambient, blurred, and animated mesh gradient.

This document serves as the absolute source of truth. You must follow every single directive, layout rule, state management strategy, and aesthetic guideline described below.

---

## PART 1: CORE AESTHETICS & GLOBAL FOUNDATION

### 1.1 The Mesh Gradient Background
The application does not use solid backgrounds. The `<body>` must feature an animated, warm, and sophisticated mesh gradient.
- **Base Color:** `#eaddd7` (Soft warm grey/beige).
- **Gradients:** Combine multiple radial gradients that blend seamlessly.
  - Top Left: `radial-gradient(circle at 0% 0%, hsla(28, 65%, 85%, 1) 0%, transparent 50%)` (Peach).
  - Bottom Right: `radial-gradient(circle at 100% 100%, hsla(23, 45%, 80%, 1) 0%, transparent 50%)` (Warm Sand).
  - Bottom Left: `radial-gradient(circle at 0% 100%, hsla(43, 70%, 90%, 1) 0%, transparent 50%)` (Light Beige).
- **Animation:** The background should subtly pulse or shift over a 20-second CSS keyframe cycle to feel "alive".

### 1.2 Glassmorphism Variables
Define these exact custom utilities in your Tailwind configuration or use arbitrary values:
- `bg-glass`: `rgba(255, 255, 255, 0.55)` (Main container background).
- `bg-glass-card`: `rgba(255, 255, 255, 0.75)` (Child cards background).
- `bg-glass-dark`: `rgba(28, 28, 30, 0.85)` (High-contrast dark cards).
- `border-glass`: `rgba(255, 255, 255, 0.8)` (1px solid).
- `shadow-glass`: `0 12px 40px 0 rgba(31, 38, 135, 0.07)` (Deep soft shadow).
- `blur-glass`: `backdrop-filter: blur(24px)`.

### 1.3 Typography & Icons
- **Font:** `Plus Jakarta Sans` (Google Fonts). Include weights 400, 500, 600, 700, 800.
- **Text Colors:**
  - `text-main`: `#1f2937` (Dark Slate for primary text/headers).
  - `text-muted`: `#8b8e99` (Soft Grey for secondary text).
- **Icons:** Phosphor Icons (`@phosphor-icons/react`). Use `weight="fill"` for active states and `weight="regular"` for inactive.

---

## PART 2: APPLICATION SHELL & LAYOUT

### 2.1 The Container
- Center the app in the viewport: `min-h-screen flex items-center justify-center p-10`.
- The main wrapper `<AppContainer>`: 
  - Width: `w-full max-w-[1600px]`.
  - Height: `h-[90vh]`.
  - Styling: `bg-glass backdrop-blur-3xl border border-glass rounded-[40px] shadow-glass overflow-hidden`.
  - Layout: CSS Grid `grid-cols-[280px_1fr]`.

### 2.2 The Sidebar (`<Sidebar />`)
The left column (280px).
- **Logo Section (h-24):** Flex container, centered. Icon (Hexagon, text-orange-500) + Text "AI RISSER" (font-bold text-xl tracking-tight).
- **Menu Section:** A vertical list of 5 main tabs. Manage this via React State (`const [activeTab, setActiveTab] = useState('dashboard')`).
- **Tab Styling (Inactive):** `flex items-center gap-4 px-6 py-4 text-gray-500 hover:text-gray-900 transition-all cursor-pointer font-medium`.
- **Tab Styling (Active):** `bg-white rounded-2xl text-gray-900 shadow-sm font-semibold transform scale-[1.02] transition-all`. Add a subtle orange left-border indicator.

### 2.3 The Header (`<Header />`)
The top bar of the main content area (height ~ 96px).
- Flexbox `justify-between items-center px-10 py-8 border-b border-white/40`.
- **Left:** Dynamic Title based on `activeTab` (e.g., "System Dashboard", "Audit Logs", "Agent Workspace"). `text-3xl font-bold text-gray-800`.
- **Right (User Profile):** A pill button. `bg-white/80 backdrop-blur-md rounded-full px-5 py-2 flex items-center gap-3 border border-white/50 shadow-sm`. Inside: Avatar (`w-8 h-8 rounded-full`), Name ("Admin"), and a CaretDown icon.

---

## PART 3: DETAILED MENU SPECIFICATIONS

Below is the exhaustive specification for each of the 5 tabs. When a user clicks a tab in the Sidebar, the Main Content area smoothly fades into the respective component.

---

### 3.1 MENU 1: DASHBOARD (`<DashboardView />`)
**Purpose:** The central nervous system. Provides an eagle-eye view of BigQuery data health, Agent executions, and system resources.

**Layout Grid:**
Uses a complex, responsive grid.
- **Row 1:** Top Stats (3 columns).
- **Row 2:** Middle Section (Grid 8 / 4).
- **Row 3:** Bottom Section (Grid 8 / 4).

#### 3.1.1 Top Stats (`<TopStatsRow />`)
- **Card 1 (BigQuery Health):** 
  - Icon: `Database` in an orange circle.
  - Label: "Total Rows Processed". Value: "14.2M". Sub-label: "+12% vs last week" (green).
- **Card 2 (Agent Core):**
  - Icon: `Robot` in a blue circle.
  - Label: "Agent Invocations". Value: "1,248". Sub-label: "99.8% Success Rate".
- **Card 3 (System Latency):**
  - Icon: `Activity` in a purple circle.
  - Label: "Avg RAG Latency". Value: "420ms". Sub-label: "Optimal".

#### 3.1.2 Data Ingestion Trend (`<IngestionChart />`) - Col-span-8
- **Style:** Standard Glass Card (`bg-glass-card rounded-3xl p-8 border-glass`).
- **Header:** "Data Ingestion Trend" (Left) | Dropdown "Past 7 days" (Right).
- **Chart:** Pure CSS Bar Chart.
  - X-Axis: Days (Mon, Tue, Wed...).
  - Y-Axis: GB (0, 0.5, 1.0, 1.5, 2.0).
  - Bars: Array of 7 divs. Container is `h-48 flex items-end gap-4`. Track `bg-white/50 rounded-t-xl`. Fill `bg-gradient-to-t from-orange-400 to-peach-300 w-12 rounded-t-xl hover:opacity-80 cursor-pointer transition-all`.

#### 3.1.3 Live System Alerts (`<LiveAlertsCard />`) - Col-span-4
- **Crucial Aesthetic:** The Dark Glass Card. Contrasts the entire UI.
- **Style:** `bg-[rgba(28,28,30,0.85)] text-white rounded-3xl p-8 border border-white/10 shadow-2xl relative overflow-hidden`.
- **Glow Effect:** `<div className="absolute -top-20 -right-20 w-64 h-64 bg-orange-500 rounded-full blur-[100px] opacity-20 pointer-events-none" />`.
- **Content:** A vertical timeline of alerts.
  - Item 1: 🔴 "High Bounce Rate detected in fct_user_event_tracking" (08:12 AM).
  - Item 2: 🔵 "Agent Dashboard Architect spawned successfully" (07:45 AM).
  - Item 3: 🟢 "dbt Silver transform completed" (Yesterday 23:00).
- Timeline dots must pulse softly using CSS `@keyframes`.

#### 3.1.4 Recent Agent Tasks (`<TasksTable />`) - Col-span-8
- **Style:** `bg-glass-card rounded-3xl p-8 border-glass`.
- **Table:** Clean, borderless table. Headers: `text-xs uppercase text-gray-500 font-bold`.
- **Data Rows:**
  - TSK-092 | Dashboard Architect | Status: [Progress Bar 100% Green] | 2.4s
  - TSK-093 | SQL Analyst | Status: [Progress Bar 45% Orange Gradient, animated width] | Running
  - TSK-094 | QA Agent | Status: [Progress Bar 0% Grey] | Pending

#### 3.1.5 Resource Allocation (`<ResourceWidgets />`) - Col-span-4
- 3 stacked widgets displaying % usage.
- BigQuery: `bg-orange-50 rounded-2xl p-5 flex justify-between`. Text: "BigQuery Compute". Value: "45%".
- Cloud Run: `bg-white/60 rounded-2xl p-5`. Value: "32%".
- Qdrant Vector DB: `bg-white/60 rounded-2xl p-5`. Value: "23%".

---

### 3.2 MENU 2: LOG (`<LogView />`)
**Purpose:** A dedicated, full-screen console interface for reading system traces, errors, and warnings across all microservices (Airflow, Agent Core, Superset).

**Layout:**
- **Toolbar:** `flex gap-4 mb-6`.
  - Search Input: `<input type="text" placeholder="Search logs..." className="bg-white/50 border border-white/60 rounded-xl px-4 py-2 w-96 backdrop-blur-md focus:outline-none focus:ring-2 focus:ring-orange-300" />`
  - Filter Badges: 4 clickable pills (`ALL`, `INFO`, `WARN`, `ERROR`). ERROR is red-tinted, WARN is yellow, INFO is blue.
- **Log Console:** 
  - A massive dark-mode window taking up remaining height.
  - `bg-[rgba(20,20,22,0.9)] rounded-3xl border border-white/10 shadow-inner p-6 overflow-y-auto font-mono text-sm`.
  - **Log Entry Structure:** `[TIMESTAMP] [SERVICE_NAME] [LEVEL] MESSAGE`.
  - Color coding inside the console:
    - Timestamp: `text-gray-500`.
    - Service (e.g., `[AGENT_CORE]`): `text-purple-400`.
    - Level `[ERROR]`: `text-red-400 font-bold`.
    - Message: `text-gray-300`.
  - **Auto-scroll:** Implement a fake auto-scroll behavior or a "Tail -f" toggle button floating at the bottom right of the console.

---

### 3.3 MENU 3: AGENT (`<AgentWorkspace />`)
**Purpose:** The interactive chat interface for human-in-the-loop (HITL) communication with the Tri-Collection Agent Workflow (`POST /run`).

**Layout:**
Split into two panels: A History Sidebar (Left, 300px) and the Chat Area (Right, 1fr).

#### 3.3.1 Agent History Sidebar
- Inside the Main Content area, dock a glass pane to the left.
- **Header:** "Conversations" + "New Chat" button.
- **List:** Displays previous Thread IDs or Session titles (e.g., "Generate Marketing KPI Dashboard", "Debug dbt pipeline").
- Active session is highlighted in white.

#### 3.3.2 Chat Interface
- **Message List (`flex-col gap-6 p-8 overflow-y-auto h-[calc(100%-100px)]`)**:
  - **User Message:** Aligned right. Bubble style: `bg-gradient-to-br from-orange-400 to-peach-400 text-white rounded-2xl rounded-tr-sm px-6 py-4 shadow-md max-w-[70%]`.
  - **Agent Message:** Aligned left. Bubble style: `bg-white/80 backdrop-blur-md text-gray-800 rounded-2xl rounded-tl-sm px-6 py-4 shadow-sm border border-white/50 max-w-[80%]`.
  - **Rich Text:** The Agent message must support rendering Markdown (conceptually), so it should look clean, with proper spacing for bullet points and bold text.
  - **Thinking Indicator:** A sub-component showing a pulsing 3-dot animation when waiting for the `POST /run` API.

#### 3.3.3 Input Area
- Docked at the bottom of the chat.
- **Container:** `bg-white/60 backdrop-blur-xl border border-white p-2 rounded-3xl flex items-center gap-4 shadow-lg`.
- **Textarea:** `w-full bg-transparent border-none outline-none px-4 py-2 text-gray-700 resize-none` (Auto-expanding up to 4 lines).
- **Send Button:** A circular button `bg-orange-500 text-white p-3 rounded-full hover:bg-orange-600 transition-all cursor-pointer shadow-[0_0_15px_rgba(249,115,22,0.4)]`.

---

### 3.4 MENU 4: AIRFLOW (`<AirflowView />`)
**Purpose:** To manage Data Engineering DAGs (Bronze -> Silver -> Gold).

**Implementation Directives:**
- Since Airflow is an external cloud service, this view will primarily serve as a stylized wrapper.
- **Hero Section:** "Pipeline Orchestrator".
- **Status Cards:** Show mock sync status.
  - "ClickHouse to Bronze" -> Status: Success (2 mins ago).
  - "dbt Silver Transform" -> Status: Running.
- **Iframe Container:**
  - `<div className="w-full h-full bg-white/50 rounded-3xl border border-white overflow-hidden p-2">`
  - `<iframe src="YOUR_AIRFLOW_URL" className="w-full h-full rounded-2xl" />`
  - *Note: Add a placeholder overlay saying "Connect Airflow API / Iframe" if URL is empty.*

---

### 3.5 MENU 5: SUPERSET (`<SupersetView />`)
**Purpose:** To display Business Intelligence Dashboards directly within the AI RISSER portal.

**Implementation Directives:**
- **Toolbar:** Dropdown to select different Dashboards (e.g., "Marketing Star Schema", "Hardware OBT").
- **Iframe Container:** 
  - Massive glass wrapper. `bg-white/40 backdrop-blur-3xl rounded-[32px] border border-white/60 shadow-glass w-full h-[calc(100%-80px)] p-3 relative`.
  - `<iframe src="https://airisser-superset-598635008208.asia-southeast1.run.app" className="w-full h-full rounded-[24px] border-0" />`.
- **Floating Controls:** Add small floating action buttons inside the glass wrapper (top right, absolutely positioned) to "Refresh Data", "Expand Fullscreen", and "Share".

---

## PART 4: REACT STATE & COMPONENT ARCHITECTURE

### 4.1 Required State Variables (App.tsx)
You must define these states at the top level to pass down as props:
```javascript
const [activeTab, setActiveTab] = useState('DASHBOARD');
const [isAgentTyping, setIsAgentTyping] = useState(false);
const [chatMessages, setChatMessages] = useState([
  { role: 'agent', content: 'Hello! I am the AI RISSER Agent Core. How can I assist you with your BigQuery data today?' }
]);
```

### 4.2 Data Mocking
Do not use `<!-- Insert Data Here -->`. You MUST define Javascript arrays holding the mock data for all tables, charts, and logs.
Example for Logs:
```javascript
const mockLogs = [
  { id: 1, time: '10:42:01', service: 'AGENT_CORE', level: 'INFO', message: 'Received user prompt: Create marketing dashboard' },
  { id: 2, time: '10:42:03', service: 'LANGGRAPH', level: 'WARN', message: 'Semantic Cache miss. Routing to SQL Generator.' },
  { id: 3, time: '10:42:10', service: 'BIGQUERY', level: 'ERROR', message: 'Partition limit exceeded on fct_user_event_tracking' }
];
```

### 4.3 Animation & Polish
- Use Tailwind's `transition-all duration-300 ease-in-out` on all interactive elements (buttons, hover states).
- Use `group` and `group-hover` for revealing actions (like the 3-dots in tables).
- The transition between Menu Tabs must not be jarring. If possible, wrap the rendering logic in a fade-in container:
  ```jsx
  <div className="animate-fade-in duration-500">
    {activeTab === 'DASHBOARD' && <DashboardView />}
    {/* ... */}
  </div>
  ```

---

## PART 5: FINAL DIRECTIVE

**Rule 1:** Produce the FULL, EXHAUSTIVE React code. No shortcuts. No "leave as exercise". 
**Rule 2:** The final output must literally copy-paste into `App.tsx` and run flawlessly using standard Tailwind utility classes.
**Rule 3:** The Glassmorphism aesthetic is non-negotiable. Maintain the strict rgba background colors, blur values, and the mesh gradient body background.

Begin writing the application.
