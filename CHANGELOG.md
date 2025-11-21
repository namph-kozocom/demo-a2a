# Changelog

## 2025-11-21 - Major Refactoring

### Backend Changes

#### 1. Removed A2A Naming Convention
- **Deleted old files:**
  - `backend/main.py` (old version)
  - `backend/agents/analyst.py` (old version)
  - `backend/agents/developer.py` (old version)
  - `backend/agents/tester.py` (old version)
  - `backend/a2a/` (entire directory)

- **Renamed files (removed `_a2a` suffix):**
  - `main_a2a.py` → `main.py`
  - `agents/analyst_a2a.py` → `agents/analyst.py`
  - `agents/developer_a2a.py` → `agents/developer.py`
  - `agents/tester_a2a.py` → `agents/tester.py`

#### 2. Renamed Classes
- `AnalystAgentA2A` → `AnalystAgent`
- `DeveloperAgentA2A` → `DeveloperAgent`
- `TesterAgentA2A` → `TesterAgent`

#### 3. Protocol Module Restructuring
- **Created new `protocol/` directory** (replaced `a2a/`)
- **Renamed protocol classes:**
  - `A2AMessage` → `Message`
  - `A2ARequest` → `Request`
  - `A2AResponse` → `Response`
  - `A2ANotification` → `Notification`
  - `A2AMessageBus` → `MessageBus`

- **Updated all imports:**
  - `from a2a import ...` → `from protocol import ...`

#### 4. Updated Documentation
- Changed all docstrings from "A2A protocol support" to "protocol support"
- Updated API title from "A2A Web Builder API" to "Web Builder API"
- Removed all A2A references in comments and messages

### Frontend Changes

#### 1. Added VSCode-like File Explorer
- **New Features:**
  - File tree view with folder/file icons
  - Expandable/collapsible folders
  - Click to switch between files
  - Active file highlighting
  - Hover effects on tree items

- **UI Components:**
  - Left sidebar file explorer (250px width)
  - Folder icons (purple color)
  - File icons (gray color)
  - Chevron icons for expand/collapse
  - "FILES" header in explorer

- **Styling:**
  - VSCode-inspired dark theme
  - Smooth transitions and hover effects
  - Active file highlighted with accent color
  - Proper indentation for nested items

### File Structure After Changes

```
backend/
├── protocol/              # NEW: Renamed from a2a/
│   ├── __init__.py       # Updated exports
│   └── protocol.py       # Renamed classes
├── agents/
│   ├── __init__.py
│   ├── base_agent.py     # Updated imports
│   ├── analyst.py        # Renamed from analyst_a2a.py
│   ├── developer.py      # Renamed from developer_a2a.py
│   └── tester.py         # Renamed from tester_a2a.py
├── main.py               # Renamed from main_a2a.py
├── requirements.txt
└── .env

src/
├── components/
│   ├── CodePanel.tsx     # Added file explorer
│   ├── CodePanel.module.css  # Added explorer styles
│   ├── ChatPanel.tsx
│   └── Header.tsx
└── app/
    ├── layout.tsx
    └── page.tsx
```

### Breaking Changes
- All imports from `a2a` module must be changed to `protocol`
- Class names no longer have `A2A` prefix
- File names no longer have `_a2a` suffix

### Migration Guide
If you have any custom code that imports from the old structure:

**Before:**
```python
from a2a import A2ARequest, A2AResponse, message_bus
from agents.analyst_a2a import AnalystAgentA2A
```

**After:**
```python
from protocol import Request, Response, message_bus
from agents.analyst import AnalystAgent
```

### Testing
- ✅ Backend server starts successfully on port 8000
- ✅ All agents properly initialized
- ✅ Protocol communication working
- ✅ Frontend file explorer displays correctly
- ✅ File switching works in code panel

### Next Steps
- Test full workflow with frontend
- Verify WebSocket communication
- Test code generation and modification
- Ensure all agent interactions work correctly
