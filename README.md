# A2A Web Builder

A multi-agent collaborative web development platform powered by AI.

## Architecture

- **Frontend**: Next.js + Sandpack (CodeSandbox)
- **Backend**: Python FastAPI + WebSocket
- **Agents**:
  - **Analyst Agent** (LangGraph): Coordinates workflow and breaks down requirements
  - **Developer Agent** (LangChain): Generates and fixes code
  - **Tester Agent** (LangChain + Playwright): Tests and validates code

## Setup

### Frontend

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### Backend

```bash
cd backend

# Create virtual environment with uv
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Create .env file with your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run the server
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

Backend runs on `http://localhost:8000`

## Features

- **Real-time Chat**: Communicate with AI agents
- **Live Code Preview**: See code changes instantly with Sandpack
- **Multi-Agent Collaboration**: 
  - Analyst breaks down requirements
  - Developer generates code
  - Tester validates and reports bugs
  - Developer fixes bugs based on feedback
- **WebSocket Communication**: Real-time updates between frontend and backend

## Usage

1. Start both frontend and backend servers
2. Open `http://localhost:3000` in your browser
3. Type your request in the chat (e.g., "Build a todo app")
4. Watch the agents collaborate to build your application
5. See the live preview in the code panel

## Agent Workflow

```
User Request → Analyst (analyzes) → Developer (codes) → Tester (validates)
                                                              ↓
                                                         Bug Found?
                                                              ↓
                                              Developer (fixes) → Tester (re-validates)
```
