# CrimeCopilot AI - Decentered Intelligence Dashboard for Karnataka State Police

CrimeCopilot AI is a premium, high-performance, AI-driven crime analysis console built for the Karnataka State Police (KSP) Datathon 2026. It integrates relational database filters (SQLite), graph network traversals (Neo4j), TF-IDF semantic case matching, offender risk timelines, and bilingual voice recognition (English/Kannada) into a unified "Stadium Noir" command dashboard.

---

## 1. Prototype Brief (Project Overview)

### A. Problem Statement Addressed
Modern police intelligence relies on fragmented silos (Excel, PDF files, isolated databases). When investigating crime syndicates, officers face:
1. **Hidden Connections:** Difficulty identifying links between suspects, shared vehicles, and bank accounts.
2. **Information Overload:** Scanning thousands of written FIR descriptions to find patterns (modus operandi).
3. **Language Barriers:** Inability to easily query or record voice notes in native languages like Kannada.
4. **Explainability Deficit:** Black-box AI systems that make claims without verifiable sources.

### B. Key Features & Functionality
* **Conversational AI Console (SSE Streaming):** Natural language routing with real-time progress logs.
* **Interactive Cytoscape.js Network Graph:** Visualizes 2-hop criminal syndicates, communications, and financial channels.
* **Geospatial Hotspot Leaflet Map:** Renders regional crime hotspots on custom dark-theme GIS tiles.
* **TF-IDF Semantic Similar Case Search:** Matches crime descriptions using local Cosine Similarity vectors.
* **Offender Risk Profiling:** Renders suspect cards with gang banners, timelines, and SVG risk gauges.
* **Bilingual Voice Input (Speech-to-Text):** Browser SpeechRecognition supporting Kannada and English transcription and automated query translation.
* **Official PDF Report Export:** Custom `@media print` rules styling printable case sheets with 1 click.
* **Grounded Explainability (Hallucination Guard):** Verifies all AI response tokens against evidence trails.

### C. Technology Stack
* **Frontend:** Next.js 16 (App Router + TS), Tailwind CSS (Stadium Noir Theme), Cytoscape.js, React-Leaflet.
* **Backend:** FastAPI (Python 3.13), LangGraph (Agent State Orchestration), SQLAlchemy ORM.
* **Database:** SQLite (Relational), Neo4j AuraDB (Graph database + Cypher engine).
* **LLM Engine:** Gemini 1.5 Flash (via `google-generativeai`).

### D. Proposed Impact
Reduces time-to-insight for field investigators from hours to seconds. Promotes native language usage in administrative interfaces, and ensures 100% auditability through verifiable evidence trails.

---

## 2. Setup & Local Execution

### A. Backend Setup
1. Navigate to the project root:
   ```bash
   cd crimecopilot-ai
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment template and add your API Keys:
   ```bash
   copy .env.example .env
   ```
   Edit `.env` to supply:
   * `GEMINI_API_KEY` (Get from Google AI Studio)
   * `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` (Optional: Neo4j Aura DB credentials)

5. Seed the relational and graph databases:
   ```bash
   python generate_data.py
   python validate_data.py
   python load_sql.py
   # Optional Neo4j graph seed:
   python load_neo4j.py
   ```

6. Start the FastAPI development server:
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

### B. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server with Turbopack:
   ```bash
   npm run dev
   ```
4. Access the command console at: `http://localhost:3000`

---

## 3. Zoho Catalyst Deployment Guide

To deploy the solution to the **Zoho Catalyst** platform, follow these steps:

### A. Deploy Backend on AppSail
Catalyst AppSail hosts full-stack python apps.
1. Install Catalyst CLI globally:
   ```bash
   npm install -g zcatalyst-cli
   ```
2. Login to your Zoho account:
   ```bash
   catalyst login
   ```
3. Initialize the AppSail service in the root directory:
   ```bash
   catalyst init
   # Select 'AppSail' and associate it with your Catalyst project.
   ```
4. Configure `app-config.json` inside the root folder to point to `main:app` using uvicorn:
   ```json
   {
     "build": {
       "command": "pip install -r requirements.txt"
     },
     "run": {
       "command": "uvicorn main:app --host 0.0.0.0 --port $PORT"
     }
   }
   ```
5. Deploy to Catalyst AppSail:
   ```bash
   catalyst deploy
   ```

### B. Deploy Frontend on Catalyst Slate
1. Navigate to `frontend/` and configure Next.js for static export by editing `next.config.ts`:
   ```typescript
   const nextConfig = {
     output: 'export'
   };
   export default nextConfig;
   ```
2. Build the static distribution:
   ```bash
   npm run build
   # This generates an 'out/' directory.
   ```
3. Initialize Catalyst Slate hosting inside the `frontend/` folder:
   ```bash
   catalyst init
   # Select 'Hosting' or 'Slate', point the public source directory to 'out'.
   ```
4. Deploy the frontend:
   ```bash
   catalyst deploy --only hosting
   ```
