# 🚀 PyCodeReview AI: Intelligent Multi-Language Code Reviewer & Sandbox

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev)
[![Tree-Sitter](https://img.shields.io/badge/AST-Tree--Sitter-brightgreen.svg)](https://tree-sitter.github.io)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Monaco Editor](https://img.shields.io/badge/Editor-Monaco%20Editor-blue.svg)](https://microsoft.github.io/monaco-editor/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%20%2B%20Beanie-47A248.svg?logo=mongodb&logoColor=white)](https://beanie-odm.dev)

An enterprise-grade, asynchronous AI-driven code analysis, static linting, and automated test-execution platform. Built with a high-performance **Python 3.11+ / FastAPI** engine, **Google Gemini 2.5 Flash** structured outputs, **Tree-Sitter** multi-language AST parser, a secure **sandboxed runner**, and a modern **React + Monaco Editor** client.

---

## 📑 Table of Contents
1. [System Architecture](#-system-architecture)
2. [Monorepo Directory Layout](#-monorepo-directory-layout)
3. [Backend Specification (`/backend`)](#-backend-specification-backend)
   - [Tech Stack & Dependencies](#backend-tech-stack--dependencies)
   - [Pydantic Schemas & Data Contracts](#pydantic-schemas--data-contracts)
   - [Google Gemini 2.5 Flash Engine](#google-gemini-25-flash-engine)
   - [Tree-Sitter AST & Static Analysis](#tree-sitter-ast--static-analysis)
   - [Sandboxed Test Runner](#sandboxed-test-runner)
   - [WebSocket Live Analysis](#websocket-live-analysis)
   - [Database Persistence (Beanie ODM)](#database-persistence-beanie-odm)
4. [Frontend Specification (`/frontend`)](#-frontend-specification-frontend)
   - [Tech Stack & Libraries](#frontend-tech-stack--libraries)
   - [Architecture & State Flow](#frontend-architecture--state-flow)
   - [Core UI Components](#core-ui-components)
5. [End-to-End API Contracts](#-end-to-end-api-contracts)
6. [Step-by-Step Implementation Roadmap](#-step-by-step-implementation-roadmap)
7. [Environment Setup & Quickstart](#-environment-setup--quickstart)
8. [Docker Compose & Deployment](#-docker-compose--deployment)

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client ["Client Layer (React + Monaco)"]
        UI[User / React Frontend]
        Editor[Monaco Code Editor]
        TestCaseUI[Test Case Runner UI]
        VerdictUI[Verdict & Review Dashboard]
    end

    subgraph Gateway ["API Gateway (FastAPI)"]
        Router[FastAPI Router /api/v1]
        WS[WebSocket Manager /ws]
        CORS[CORS & Security Middleware]
    end

    subgraph Engine ["Python AI & Analysis Engine"]
        AST[Tree-Sitter AST Parser<br/>(C, C++, Java, Py, JS)]
        Static[Static Analyzer<br/>(Radon Complexity & Ruff)]
        Runner[Isolated Sandboxed Runner<br/>(Subprocess / TLE / Memory limits)]
        Gemini[Google Gemini 2.5 Flash<br/>(Structured Pydantic Schema)]
        Aggregator[Verdict & Metrics Aggregator]
    end

    subgraph Storage ["Persistence Layer"]
        DB[(MongoDB via Beanie ODM)]
    end

    UI -->|Code Edit (Debounced 500ms)| WS
    WS -->|Live Syntax & AST Warnings| Editor
    
    UI -->|POST /api/v1/run-tests| Router
    Router --> Runner
    Runner -->|Stdout, Stderr, TLE Verdict| TestCaseUI

    UI -->|POST /api/v1/reviews| Router
    Router --> AST
    Router --> Static
    Router --> Runner
    AST --> Aggregator
    Static --> Aggregator
    Runner --> Aggregator
    Aggregator --> Gemini
    Gemini -->|Strict JSON| Aggregator
    Aggregator --> DB
    Aggregator -->|Verdict JSON| VerdictUI
```

---

## 📁 Monorepo Directory Layout

```text
Major_1_2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app factory, middleware & lifespan
│   │   ├── config.py                   # Pydantic BaseSettings & env configs
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                 # Dependency injection (Auth, DB session)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── router.py           # V1 API aggregator
│   │   │       ├── reviews.py          # POST /reviews, GET /reviews/{id}
│   │   │       ├── runner.py           # POST /run-tests
│   │   │       └── websocket.py        # WS /ws/realtime-analysis
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── gemini.py               # Google GenAI 2.5 client & structured prompt
│   │   │   ├── ast_parser.py           # Tree-sitter multi-language parser
│   │   │   ├── static_analyzer.py      # Radon cyclomatic complexity & linter
│   │   │   └── test_runner.py          # Subprocess sandboxed execution engine
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                 # Beanie user document
│   │   │   └── review.py               # Beanie review document (history & stats)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── review.py               # Pydantic request & structured response
│   │   │   └── test_case.py            # Test execution schemas
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── normalizer.py           # String output normalization & diff engine
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_ast.py
│   │   ├── test_runner.py
│   │   └── test_gemini.py
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── Navbar.jsx              # App header with language selector & theme toggle
│   │   │   ├── CodeEditor.jsx          # Monaco Editor wrapper with WebSocket diagnostics
│   │   │   ├── TestCaseRunner.jsx      # Test runner panel with custom input & results
│   │   │   ├── VerdictView.jsx         # Review score, Big-O comparison & recommendations
│   │   │   ├── ComplexityCard.jsx      # Visual Time/Space complexity badge comparison
│   │   │   └── IssueList.jsx           # Line-by-line syntax & performance warnings
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js         # Reconnecting WebSocket client for live linting
│   │   │   └── useDebounce.js          # Input debouncing hook
│   │   ├── services/
│   │   │   └── api.js                  # Axios client configured with base URL
│   │   ├── App.jsx                     # Root application layout
│   │   ├── main.jsx                    # React entrypoint
│   │   └── index.css                   # Global design tokens and styling
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
│
├── docker-compose.yml                  # Full stack local orchestration
└── README.md                           # Master Project Blueprint
```

---

## ⚙️ Backend Specification (`/backend`)

### Backend Tech Stack & Dependencies

```ini
# Core Framework & Settings
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
pydantic-settings>=2.2.0

# AI & LLM Engine
google-genai>=2.17.1

# AST & Static Code Parsing
tree-sitter>=0.22.0
tree-sitter-languages>=1.10.2

# Code Metrics & Quality
radon>=6.0.1
ruff>=0.3.0
bandit>=1.7.8

# Database (Async MongoDB)
motor>=3.3.2
beanie>=1.25.0

# Async System & Utilities
aiofiles>=23.2.1
python-dotenv>=1.0.1
pytest>=8.0.0
pytest-asyncio>=0.23.5
httpx>=0.27.0
```

---



## 🎨 Frontend Specification (`/frontend`)

### Frontend Tech Stack & Libraries

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@monaco-editor/react": "^4.6.0",
    "lucide-react": "^0.359.0",
    "axios": "^1.6.8",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.2.0"
  }
}
```

---

### Frontend Architecture & State Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Editor as Monaco Editor
    participant WS as WebSocket Hook
    participant API as Axios Service
    participant Dashboard as Verdict & Test View

    User->>Editor: Type Code (e.g. Two Sum in Python)
    Editor->>WS: Emit Code via WebSocket (Debounced 400ms)
    WS-->>Editor: Inline Syntax Diagnostics & Error Markers

    User->>Dashboard: Click "Run Tests"
    Dashboard->>API: POST /api/v1/runner/run-tests
    API-->>Dashboard: Test Case Verdicts (Passed / Failed / Actual Output)

    User->>Dashboard: Click "Get AI Code Review"
    Dashboard->>API: POST /api/v1/reviews
    API-->>Dashboard: Complete CodeReviewResponse (Rating, Big-O, Canonical Code)
    Dashboard-->>User: Render Interactive Visual Score & Issues
```

---

### Core UI Components

1. **`Navbar.jsx`**:
   - Language selector dropdown (`Python`, `JavaScript`, `Java`, `C++`, `C`).
   - Action buttons: `Run Tests` (Green play button), `AI Review` (Purple sparkle button with loading state).
   - Theme toggle (Dark / Light).

2. **`CodeEditor.jsx`**:
   - Embedded `@monaco-editor/react`.
   - Real-time syntax decorations and error squiggles powered by the WebSocket AST endpoint.
   - Configurable font size, mini-map, and automatic layout resizing.

3. **`TestCaseRunner.jsx`**:
   - Tabbed interface: Sample Test Cases & Custom Test Case input.
   - Status chips: `PASSED` (green), `FAILED` (red), `TIME LIMIT EXCEEDED` (amber).
   - Diff view between `expectedOutput` and `actualOutput`.

4. **`VerdictView.jsx`**:
   - Radial / circular score badge (0 to 100).
   - `ComplexityCard.jsx`: Comparative Time & Space Complexity pills:
     - User Complexity: `O(N^2)` Time | `O(1)` Space
     - Optimal Target: `O(N)` Time | `O(N)` Space
   - Algorithmic Approach identification chip (e.g. `Hash Map Lookup`).
   - Expandable Optimal Solution code block with one-click copy.
   - `IssueList.jsx`: Categorized warnings and security notes with suggested fixes.

---

## 📡 End-to-End API Contracts

### 1. `POST /api/v1/reviews`
Analyzes code submission, runs static analysis + AST pre-checks, executes tests, and prompts Gemini 2.5 Flash.

**Request Payload:**
```json
{
  "code": "def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
  "language": "python",
  "problemTitle": "Two Sum",
  "problemDescription": "Find indices of two numbers such that they add up to target.",
  "testCases": [
    {
      "input": "[2,7,11,15]\n9",
      "expectedOutput": "[0, 1]"
    }
  ]
}
```

**Response Payload (`200 OK`):**
```json
{
  "summary": "Brute-force nested loop solution successfully finding the target pair, but suffers from quadratic time complexity.",
  "rating": 68,
  "verdict": "Needs Improvement",
  "algorithmicApproach": "Brute Force Iteration",
  "complexityComparison": {
    "userTime": "O(N^2)",
    "optimalTime": "O(N)",
    "userSpace": "O(1)",
    "optimalSpace": "O(N)"
  },
  "testCaseResults": [
    {
      "input": "[2,7,11,15]\n9",
      "expectedOutput": "[0, 1]",
      "actualOutput": "[0, 1]",
      "passed": true,
      "explanation": "Matches expected indices."
    }
  ],
  "issues": [
    {
      "line": 2,
      "severity": "Warning",
      "message": "Nested loop causes O(N^2) time complexity. Will hit TLE on large arrays (N > 10^4).",
      "suggestedFix": "Use a hash map to look up the complement in O(1) average time."
    }
  ],
  "correctCode": "def twoSum(nums, target):\n    lookup = {}\n    for i, num in enumerate(nums):\n        diff = target - num\n        if diff in lookup:\n            return [lookup[diff], i]\n        lookup[num] = i\n    return []",
  "optimalExplanation": "By storing previously visited elements and their indices in a hash map, we achieve linear O(N) runtime."
}
```

---

### 2. `POST /api/v1/runner/run-tests`
Fast path execution without triggering the full AI review.

**Request Payload:**
```json
{
  "code": "print('Hello World')",
  "language": "python",
  "input": ""
}
```

**Response Payload (`200 OK`):**
```json
{
  "stdout": "Hello World",
  "stderr": "",
  "exitCode": 0,
  "status": "COMPLETED",
  "executionTimeMs": 18.4
}
```

---

### 3. `WS /ws/realtime-analysis`
Two-way WebSocket connection for interactive editor linting.

**Client to Server:**
```json
{
  "code": "def foo():\n    pass",
  "language": "python"
}
```

**Server to Client:**
```json
{
  "type": "AST_DIAGNOSTICS",
  "metrics": {
    "has_syntax_error": false,
    "function_count": 1,
    "loop_count": 0,
    "error_count": 0
  }
}
```

---

## 🚦 Step-by-Step Implementation Roadmap

| Phase | Milestone | Core Deliverables |
| :--- | :--- | :--- |
| **Phase 1** | **Backend Foundations** | • Initialize virtual environment (`python3 -m venv .venv`)<br>• Install dependencies (`fastapi`, `uvicorn`, `google-genai`, `tree-sitter`)<br>• Configure `config.py` with `Pydantic-Settings` & `.env` validation<br>• Create FastAPI entrypoint in `app/main.py` with CORS |
| **Phase 2** | **AI Engine & Schemas** | • Define `app/schemas/review.py` matching camelCase frontend keys<br>• Implement `app/core/gemini.py` using Gemini 2.5 Flash structured output<br>• Write unit test verifying structured schema generation |
| **Phase 3** | **AST & Code Diagnostics** | • Implement `app/core/ast_parser.py` using `tree-sitter-languages`<br>• Extract syntax errors, functions, and loop counts<br>• Expose WebSocket endpoint at `app/api/v1/websocket.py` |
| **Phase 4** | **Sandboxed Test Runner** | • Implement `app/core/test_runner.py` with `asyncio.create_subprocess_exec`<br>• Set execution timeouts and process kill on TLE<br>• Build output normalizer to compare actual vs. expected test results |
| **Phase 5** | **Database & API Routes** | • Initialize Beanie ODM with MongoDB connection in FastAPI lifespan<br>• Implement `POST /api/v1/reviews` and `POST /api/v1/runner/run-tests`<br>• Store review history and metrics in `ReviewDocument` |
| **Phase 6** | **Frontend Integration** | • Initialize Vite React app in `frontend/`<br>• Install `@monaco-editor/react`, `lucide-react`, `axios`<br>• Build `CodeEditor.jsx`, `TestCaseRunner.jsx`, `VerdictView.jsx`<br>• Connect live WebSocket diagnostics to Monaco markers |
| **Phase 7** | **End-to-End Verification** | • Run end-to-end review flows for Python, JS, and C++<br>• Test edge-case inputs (infinite loops, syntax errors, large outputs)<br>• Containerize full stack with `docker-compose.yml` |

---

## 💻 Environment Setup & Quickstart

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+** & npm
- **MongoDB** (running locally on port `27017` or via Docker / Atlas)
- **Google Gemini API Key** ([Get key here](https://aistudio.google.com/app/apikey))

---

### 2. Backend Setup
```bash
# Navigate to backend directory
cd /Users/surajkumar/Developer/MAIN_PROJECT/Major_1_2/backend

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat <<EOF > .env
GEMINI_API_KEY=your_actual_gemini_api_key
PORT=8000
MONGODB_URL=mongodb://localhost:27017/codereview
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
EOF

# Start development server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: **`http://localhost:8000/docs`**

---

### 3. Frontend Setup
```bash
# Navigate to frontend directory in another terminal
cd /Users/surajkumar/Developer/MAIN_PROJECT/Major_1_2/frontend

# Install dependencies
npm install

# Create .env file
cat <<EOF > .env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws/realtime-analysis
EOF

# Start Vite React dev server
npm run dev
```
Client UI will be accessible at: **`http://localhost:5173`**

---

## 🐳 Docker Compose & Deployment

Run the entire platform (Backend + Frontend + MongoDB) with a single command:

```yaml
# docker-compose.yml
version: "3.8"

services:
  mongodb:
    image: mongo:6.0
    container_name: codereview_mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  backend:
    build: ./backend
    container_name: codereview_backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - MONGODB_URL=mongodb://mongodb:27017/codereview
      - CORS_ORIGINS=http://localhost:5173
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    container_name: codereview_frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000/api/v1
      - VITE_WS_URL=ws://localhost:8000/ws/realtime-analysis
    depends_on:
      - backend

volumes:
  mongo_data:
```

To build and run:
```bash
docker-compose up --build
```
