# Task: Mission Control — Agent Organization Dashboard

**Assigned:** 2026-03-23  
**Priority:** P0 (URGENT — Infrastructure)  
**Estimated Hours:** 4-6  
**Due:** Morning report expected by 7 AM (alongside or before Emojournal)

---

## Overview

Build "Mission Control" — a centralized dashboard web app to view, manage, and control the entire agent organization (Night Owl, R&D Department, future agents).

**Core Principle:** Single pane of glass for all agent operations.

---

## Architecture (Extensible)

**Stack:**
- React + Vite (consistent with Emojournal)
- Tailwind CSS (dark theme — command center aesthetic)
- LocalStorage/IndexedDB (client-side state, no backend needed)
- Optional: WebSocket or polling for "live" updates

**Extensibility Design:**
- Plugin-based agent cards (easy to add new agent types)
- Task queue system (generic, not hardcoded)
- Status API interface (agents can report in via simple JSON)

---

## Core Features

### 1. Agent Overview Panel
**Display all active agents:**
- **Night Owl** — Coding agent
  - Current task
  - Status: Idle / Working / Completed / Error
  - Progress bar (% complete)
  - Last commit / output
  - Schedule: Next run time
  
- **R&D Scout** — Content monitor
  - Last check timestamp
  - Sources monitored (RSS, YouTube)
  - New items found
  - Status: Watching / Extracting / Idle
  
- **R&D Analyst** — Opportunity processor
  - Queue length (items waiting analysis)
  - Current analysis
  - Status: Idle / Analyzing / Reporting

- **Future agents** (placeholder slots)
  - Sales Agent
  - Marketing Agent
  - Research Agent
  - etc.

### 2. Task Queue View
**Universal task management:**
- All pending tasks across all agents
- Task metadata: Title, assigned agent, priority, created time, ETA
- Status: Queued / Active / Completed / Blocked
- Filter by: Agent, priority, status, date range
- Sort by: Priority, date, agent

**Task detail view:**
- Full task description
- Progress updates (timestamped logs)
- Output/artifacts produced
- Link to deliverables (files, reports)

### 3. Activity Feed
**Real-time (or near-real-time) log:**
- Timestamped events
- Agent actions: "Night Owl started Emojournal MVP"
- Completion events: "R&D Analyst generated Opportunity Card #284"
- Error alerts: "Scout failed to reach RSS feed"
- System events: "Night Owl auto-activated at 2:00 AM"

### 4. Quick Actions
**Manual triggers:**
- "Wake Night Owl" (start now, skip schedule)
- "Run R&D Scout" (manual poll)
- "Pause/Resume Agent"
- "Priority Boost Task" (move to front of queue)
- "View Latest Output" (quick access to deliverables)

### 5. Deliverables Browser
**Access all outputs:**
- Code projects (links to folders)
- Analysis reports (markdown viewer)
- Opportunity Cards (filtered view)
- Log files (text viewer)
- Download/export options

### 6. Configuration Panel
**Manage agents:**
- Toggle agents on/off
- Edit schedules (cron expressions)
- Update agent parameters (model, cost limits)
- Notification preferences

---

## Data Model (Extensible)

```typescript
// Agent definition
interface Agent {
  id: string;
  name: string;
  type: 'coder' | 'analyst' | 'scout' | 'custom';
  status: 'idle' | 'working' | 'completed' | 'error' | 'paused';
  currentTask?: Task;
  schedule?: string; // cron expression
  lastRun?: Date;
  nextRun?: Date;
  config: AgentConfig;
}

// Task definition
interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string; // agent ID
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  status: 'queued' | 'active' | 'completed' | 'blocked';
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  progress: number; // 0-100
  deliverables?: string[];
  logs: LogEntry[];
}

// Activity log
interface LogEntry {
  timestamp: Date;
  agent: string;
  event: string;
  type: 'info' | 'success' | 'warning' | 'error';
  metadata?: any;
}
```

---

## File Structure

```
mission-control/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── components/
│   │   ├── AgentCard.jsx          # Individual agent display
│   │   ├── AgentGrid.jsx          # All agents overview
│   │   ├── TaskQueue.jsx          # Task list with filters
│   │   ├── TaskDetail.jsx         # Single task view
│   │   ├── ActivityFeed.jsx       # Real-time log
│   │   ├── QuickActions.jsx       # Manual controls
│   │   ├── DeliverablesBrowser.jsx
│   │   ├── ConfigPanel.jsx
│   │   └── Layout/
│   │       ├── Sidebar.jsx
│   │       ├── Header.jsx
│   │       └── Dashboard.jsx
│   ├── hooks/
│   │   ├── useAgents.js           # Agent state management
│   │   ├── useTasks.js            # Task queue management
│   │   ├── useActivity.js         # Activity feed
│   │   └── useStorage.js          # IndexedDB wrapper
│   ├── store/
│   │   ├── agentStore.js          # Agent configuration
│   │   ├── taskStore.js           # Task queue
│   │   └── activityStore.js       # Event log
│   ├── utils/
│   │   ├── agentAdapter.js        # Interface for different agent types
│   │   ├── taskScheduler.js       // Cron parsing, next-run calculation
│   │   └── statusReporter.js      // Agent status reporting
│   └── styles/
│       └── main.css
```

---

## UI Design (Command Center Aesthetic)

**Theme:** Dark, futuristic, NASA mission control meets modern dashboard

**Colors:**
- Background: #0a0a0f (deep space black)
- Cards: #14141a (panel gray)
- Accent: #00d4ff (cyan) or #ff6b35 (amber alert)
- Success: #00c853
- Warning: #ffc107
- Error: #ff3d00

**Layout:**
- Left sidebar: Agent list, quick navigation
- Center: Main dashboard (agent grid or task queue)
- Right panel: Activity feed (live scrolling)
- Top bar: Status summary, manual controls, settings

**Visual elements:**
- Glowing status indicators (idle = dim, working = pulse, error = flash)
- Progress bars with gradient fills
- Timestamp badges
- Agent avatars/icons

---

## Integration Points

**How agents report in:**

Agents write status to a simple JSON file:
```json
// .mission-control/status/night-owl.json
{
  "agentId": "night-owl",
  "status": "working",
  "currentTask": "emojournal-mvp",
  "progress": 65,
  "lastUpdate": "2026-03-24T05:30:00Z",
  "message": "Building React components"
}
```

Mission Control polls these files (or uses file watchers) to update UI.

**How tasks are created:**
- Manual: User clicks "New Task" in UI
- Automatic: Scout finds content → creates analysis task
- API: External trigger writes to `.mission-control/tasks/pending/`

---

## Phase 1 MVP (This Build)

**Core (must have):**
- [ ] Agent overview panel (Night Owl, R&D Scout, R&D Analyst)
- [ ] Task queue view (read from `.nightowl/tasks/` and `.rnd/tasks/`)
- [ ] Activity feed (manual entries for now)
- [ ] Basic status display (idle/working/completed)
- [ ] Dark command center UI

**Stretch (if time):**
- [ ] Quick action buttons (wake agents, run now)
- [ ] Live progress updates
- [ ] Deliverables browser

---

## Future Extensions (Post-MVP)

**Phase 2:**
- Real-time WebSocket updates (agents push status)
- Mobile-responsive layout
- Authentication (if multi-user)
- Agent performance metrics (tokens used, cost per task)
- Task templates (quick-create common tasks)

**Phase 3:**
- Agent-to-agent communication (Scout alerts Analyst automatically)
- Automated task assignment (AI decides which agent handles what)
- Integration with external tools (GitHub, Discord, Telegram)
- Voice commands ("Hey Mission Control, wake Night Owl")

---

## Acceptance Criteria

- [ ] Dashboard displays all 3 current agents (Night Owl, R&D Scout, R&D Analyst)
- [ ] Shows real task data from `.nightowl/tasks/` and `.rnd/`
- [ ] Activity feed shows events (can be manually populated for MVP)
- [ ] Dark, polished UI that feels like a command center
- [ ] Responsive layout (works on desktop, usable on tablet)
- [ ] Code is modular/extensible (easy to add new agents)

---

## Relationship to Emojournal

**Build order:**
1. Mission Control (infrastructure first — you need this to manage everything)
2. Emojournal (product build)

**Or parallel:**
- If Night Owl has time: Both in one night
- If not: Mission Control is P0 (you need it to see Emojournal progress anyway)

**Integration:**
- Emojournal build progress visible in Mission Control
- Night Owl status updates show Emojournal task completion

---

## Success Metric

Okeito opens Mission Control and can see:
- Night Owl's current progress on Emojournal
- R&D Scout's last check for TKO content
- R&D Analyst's Opportunity Card queue
- All tasks and their status in one view

**"I know exactly what my agents are doing without asking."**
