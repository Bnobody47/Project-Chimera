---
description: Frontend UI specification: screens, components, data bindings, accessibility.
---

# Frontend Specification

## Overview

The Chimera frontend is a React-based dashboard for Network Operators and Human Reviewers, providing real-time visibility into agent fleet status, HITL queues, campaign management, and analytics.

## Screens & Wireframes

### 1. Agent Dashboard (Main Screen)

**Route**: `/dashboard`

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header: [Logo] [User Menu] [Notifications]            │
├─────────────────────────────────────────────────────────┤
│ Sidebar:                                                │
│  • Dashboard (active)                                   │
│  • Agents                                               │
│  • Campaigns                                            │
│  • HITL Queue                                           │
│  • Analytics                                            │
│  • Settings                                             │
├─────────────────────────────────────────────────────────┤
│ Main Content:                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Total Agents │  │ Active Tasks │  │ HITL Pending │ │
│  │     42       │  │     128      │  │      23      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  Agent Status Table:                                    │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Agent Name │ Status │ Balance │ Tasks │ Actions │ │
│  ├───────────────────────────────────────────────────┤ │
│  │ @fashion_ai │ Active │ $1.2k │ 5     │ [View]  │ │
│  │ @tech_guru │ Active │ $890  │ 12    │ [View]  │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Components**:
- `Header`: Logo, user menu dropdown, notification bell (shows HITL count)
- `Sidebar`: Navigation with active state highlighting
- `StatCard`: Displays metric (agents, tasks, HITL queue depth)
- `AgentTable`: Sortable table with pagination
  - Columns: Name, Status badge, Wallet balance, Active tasks count, Actions dropdown
  - Actions: View details, Pause/Resume, View campaigns

**Data Bindings**:
- `GET /api/v1/agents?status=active` → StatCard "Total Agents"
- `GET /api/v1/planner/tasks/pending?limit=1000` → StatCard "Active Tasks"
- `GET /api/v1/judge/hitl-queue?limit=1` → StatCard "HITL Pending" (total count)
- `GET /api/v1/agents` → AgentTable rows
- `POST /api/v1/agents/{id}/pause` → Pause action
- `POST /api/v1/agents/{id}/resume` → Resume action

**Accessibility**:
- ARIA labels on all interactive elements
- Keyboard navigation (Tab, Enter, Escape)
- Screen reader announcements for status changes
- Color contrast WCAG AA compliant

**Error States**:
- Loading skeleton while fetching
- Empty state: "No agents found. Create your first agent."
- Error banner: "Failed to load agents. Retry?"

### 2. HITL Queue Screen

**Route**: `/hitl-queue`

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header + Sidebar (same as Dashboard)                    │
├─────────────────────────────────────────────────────────┤
│ Filters: [Agent ▼] [Confidence ▼] [Status ▼] [Search] │
├─────────────────────────────────────────────────────────┤
│ Review Cards (scrollable):                              │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Agent: @fashion_ai │ Confidence: 0.75 │ High    │ │
│  │ Task: Generate Instagram post                     │ │
│  │ Content: [Image Preview]                         │ │
│  │ "Check out our new summer collection..."         │ │
│  │ [Approve] [Request Edit] [Reject] [Escalate]    │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Agent: @tech_guru │ Confidence: 0.68 │ Medium   │ │
│  │ Task: Reply to comment                            │ │
│  │ Content: "Thanks for the feedback!..."           │ │
│  │ [Approve] [Request Edit] [Reject] [Escalate]     │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Components**:
- `FilterBar`: Dropdowns for agent, confidence range, status; search input
- `ReviewCard`: Displays content preview, confidence badge (color-coded), agent info, action buttons
  - Red border if confidence < 0.70
  - Yellow border if 0.70 ≤ confidence < 0.90
  - Green border if confidence ≥ 0.90
- `BatchActions`: Select multiple cards, bulk approve/reject

**Data Bindings**:
- `GET /api/v1/judge/hitl-queue?agent_id={id}&status={status}&limit=50` → ReviewCard list
- `POST /api/v1/judge/hitl-decision` → Approve/Reject/Edit actions
- WebSocket `/ws/hitl-updates` → Real-time new items

**Accessibility**:
- Focus management: new items announced via aria-live region
- Keyboard shortcuts: `A` approve, `R` reject, `E` edit, `Esc` close modal
- High contrast mode support

**Error States**:
- Empty queue: "No items pending review. Great job!"
- Network error: Retry button + offline indicator

### 3. Campaign Composer

**Route**: `/campaigns/new`

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header + Sidebar                                        │
├─────────────────────────────────────────────────────────┤
│ Create Campaign:                                       │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Agent: [Select Agent ▼]                           │ │
│  │ Goal: [Textarea: "Promote summer fashion..."]     │ │
│  │ Constraints:                                       │ │
│  │   ☑ Avoid politics                                │ │
│  │   ☑ Use brand colors                              │ │
│  │   ☐ Include hashtags                              │ │
│  │ Budget: $[Input: 500] USDC                        │ │
│  │ [Cancel] [Create Campaign]                        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Components**:
- `AgentSelector`: Dropdown with search, shows agent name + status
- `GoalInput`: Textarea with character counter (max 1000 chars)
- `ConstraintCheckboxes`: Multi-select with custom options
- `BudgetInput`: Number input with currency selector

**Data Bindings**:
- `GET /api/v1/agents?status=active` → AgentSelector options
- `POST /api/v1/agents/{id}/campaigns` → Create campaign
- Response redirects to `/campaigns/{campaign_id}`

**Validation**:
- Agent required
- Goal 10-1000 characters
- Budget ≥ 0, ≤ agent's wallet_policy.max_daily_usdc

**Error States**:
- Validation errors inline below fields
- API error: Toast notification + form remains editable

### 4. Analytics Dashboard

**Route**: `/analytics`

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│ Header + Sidebar                                        │
├─────────────────────────────────────────────────────────┤
│ Date Range: [Last 7 days ▼] [Last 30 days] [Custom]    │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐           │
│  │ Engagement Rate  │  │ Content Volume   │           │
│  │    [Line Chart]  │  │   [Bar Chart]    │           │
│  └──────────────────┘  └──────────────────┘           │
│                                                         │
│  Top Performing Content:                                │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Post │ Agent │ Views │ Engagement │ Date         │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Components**:
- `DateRangePicker`: Preset or custom range
- `LineChart`: Engagement rate over time (Chart.js/Recharts)
- `BarChart`: Content volume by day
- `PerformanceTable`: Top posts with metrics

**Data Bindings**:
- `GET /api/v1/analytics/engagement?start={date}&end={date}` → LineChart
- `GET /api/v1/analytics/volume?start={date}&end={date}` → BarChart
- `GET /api/v1/analytics/top-content?limit=10` → PerformanceTable

**Accessibility**:
- Charts have text alternatives (data tables)
- Screen reader summaries: "Engagement rate increased 15% this week"

## Component Library

### Shared Components

**Button**: `variant` (primary, secondary, danger), `size` (sm, md, lg), `disabled`, `loading`
**Badge**: `variant` (success, warning, error, info), `size` (sm, md)
**Modal**: `isOpen`, `onClose`, `title`, `children`, `footer` (action buttons)
**Toast**: `type` (success, error, info), `message`, auto-dismiss after 5s
**Table**: `columns`, `data`, `sortable`, `pagination`, `onRowClick`
**Input**: `type`, `placeholder`, `error`, `helperText`, `required`

## Data Flow

1. **Initial Load**: App fetches user permissions + tenant_id from JWT
2. **Route Guards**: Check permissions before rendering screens
3. **API Calls**: All via `fetch()` wrapped in error handler + loading state
4. **Real-time Updates**: WebSocket connection for HITL queue, agent status
5. **State Management**: React Context for auth, Redux/Zustand for app state (optional)

## Responsive Design

- **Desktop**: Full sidebar + main content (≥1024px)
- **Tablet**: Collapsible sidebar, stacked cards (768-1023px)
- **Mobile**: Bottom navigation, single-column cards (<768px)

## Performance

- Code splitting: Route-based lazy loading
- Image optimization: Lazy load, WebP format
- API caching: React Query with 30s stale time
- Bundle size target: <200KB gzipped initial load
