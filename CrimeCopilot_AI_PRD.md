# CrimeCopilot AI — Product Requirements Document
### Datathon 2026 | Karnataka State Police | Challenge 1 (+ Challenge 2 embedded)
**Solo Developer:** Parthiv Gopa  
**Version:** 1.0 — Living Document  
**Last Updated:** June 2026  
**Status:** Pre-Build

---

## 0. HOW TO USE THIS DOCUMENT

This PRD is designed to be **never rewritten, only annotated**. Every section contains:
- What to build
- What can go wrong (pitfalls)
- What the fallback is if it breaks
- What the upgrade path is if you have extra time

If a decision changes mid-build, add a dated note at the end of the relevant section. Do NOT rewrite the original — that creates confusion about what was decided and when.

---

## 1. PRODUCT VISION

### 1.1 One-Line Description
An AI-powered Crime Intelligence & Investigation Copilot that enables Karnataka State Police investigators, analysts, and policymakers to query, analyze, and act on crime data through natural language — surfacing hidden relationships, crime patterns, and predictive insights as part of a single conversational interface.

### 1.2 What This Is NOT
- Not a chatbot that wraps an SQL query
- Not a dashboard with charts that also has a search box
- Not a hallucination machine that makes up FIR numbers
- Not a 12-module monolith that half-works

### 1.3 The Strategic Frame
Challenge 1 is the primary submission. Challenge 2 features (heatmaps, network graphs, trend analysis, forecasting) are embedded as **intelligence tools invoked through the conversational interface** — not as a separate product.

Judges see one coherent system. Not scope creep.

### 1.4 Demo Story (The North Star)
Every build decision must serve this story:

> A senior investigator types: *"Show vehicle theft cases in Bengaluru East over the last 6 months."*  
> CrimeCopilot retrieves cases, displays a trend chart.  
> Investigator: *"Are there repeat offenders?"*  
> AI identifies suspects with risk scores.  
> Investigator: *"Show connections between them."*  
> Network graph appears.  
> Investigator: *"Why is Whitefield flagged?"*  
> Evidence trail appears with FIR references, no hallucinations.  
> Investigator: *"Any similar solved cases?"*  
> 5 similar cases with outcomes appear.

At that point, judges are not watching a demo. They are watching an AI crime analyst.

---

## 2. PLATFORM ARCHITECTURE

### 2.1 Platform Layers

```
┌─────────────────────────────────────────┐
│           FRONTEND (Next.js)            │
│    React + TypeScript + Tailwind        │
│    Deployed on: Catalyst Slate          │
└────────────────┬────────────────────────┘
                 │ HTTPS
┌────────────────▼────────────────────────┐
│        CATALYST API GATEWAY             │
│  Auth → Role Check → Route to Function  │
└────────┬──────────────────┬────────────┘
         │                  │
┌────────▼────────┐  ┌──────▼──────────┐
│ Catalyst        │  │ Catalyst        │
│ Functions       │  │ AppSail         │
│ (Node.js/Python)│  │ (FastAPI Python) │
│ - Auth handlers │  │ - AI Engine     │
│ - Data Store    │  │ - LangGraph     │
│   CRUD          │  │ - Neo4j Client  │
│ - File Storage  │  │ - Analytics     │
└────────┬────────┘  └──────┬──────────┘
         │                  │
┌────────▼────────┐  ┌──────▼──────────┐
│ Catalyst        │  │ Neo4j AuraDB    │
│ Data Store      │  │ (External)      │
│ (PostgreSQL-    │  │ Free Tier       │
│  compatible)    │  │ Graph DB        │
└─────────────────┘  └─────────────────┘
```

### 2.2 Why This Architecture

**Catalyst handles:**
- Authentication & session management (built-in)
- Role-based access control (built-in)
- Relational data storage for FIRs, cases, users
- File storage for PDF exports
- Frontend hosting (Slate for Next.js)
- API gateway routing

**AppSail handles:**
- Long-running FastAPI server (avoids Function timeout issues)
- LangGraph agent execution
- Neo4j connection management
- Analytics computation
- Streaming SSE responses

**This split is critical.** Catalyst Functions have a 15-minute timeout (sometimes 5 minutes in practice per community reports). LangGraph multi-hop agents can take 20-60 seconds per response. Running them in AppSail avoids timeout failures entirely.

### 2.3 Platform Constraint Log

| Constraint | Reality | Our Mitigation |
|---|---|---|
| Catalyst Functions timeout | 15 min documented, 5 min reported in practice | All AI/agent work runs in AppSail, not Functions |
| Catalyst Functions memory | 128-512 MB configurable | Light functions only in FaaS layer |
| Neo4j AuraDB Free | 200k nodes / 400k relationships (verify in console — docs inconsistent) | Synthetic dataset designed to fit within 50k nodes to be safe |
| Catalyst Data Store | MySQL-compatible relational DB | Use for structured FIR/case data, not graph |
| AppSail | Full PaaS, no Catalyst-specific restrictions | Deploy FastAPI here, full control |

---

## 3. MODULE SPECIFICATIONS

### MODULE 0: Synthetic Dataset (Build First)

**Why this is Module 0:** Everything depends on it. The AI is only as impressive as the data underneath it. This must be built before any other module.

**Schema:**

```
FIR
├── fir_id (PK)
├── fir_number (human-readable: KSP/2024/BLR/00123)
├── police_station_id (FK)
├── district
├── crime_type (vehicle_theft, burglary, assault, fraud, drug, etc.)
├── date_filed
├── date_of_occurrence
├── time_of_occurrence
├── location_description
├── latitude
├── longitude
├── status (open, closed, chargesheeted, acquitted, convicted)
├── modus_operandi
└── case_description

Accused
├── accused_id (PK)
├── name
├── age
├── gender
├── address
├── phone_number
├── aadhaar_hash (fake)
├── crime_history_count
├── risk_score (computed)
└── photo_url (placeholder)

FIR_Accused (junction)
├── fir_id
├── accused_id
└── role (primary, secondary, suspect)

Victim
├── victim_id (PK)
├── name
├── age
├── gender
├── address
└── fir_id (FK)

PoliceStation
├── station_id (PK)
├── name
├── district
├── latitude
├── longitude
└── officer_in_charge

Vehicle
├── vehicle_id
├── registration_number
├── type
├── fir_id (FK)
└── accused_id (FK, nullable)

PhoneNumber
├── phone_id
├── number
└── accused_id (FK)

BankAccount
├── account_id
├── account_number_hash (fake)
├── bank_name
└── accused_id (FK)

Location (recurring crime locations)
├── location_id
├── name
├── latitude
├── longitude
├── district
└── type (metro_station, market, residential, highway, etc.)

SocioEconomicZone
├── zone_id
├── district
├── literacy_rate
├── unemployment_rate
├── migration_index
├── urbanization_score
└── median_income_bracket
```

**Graph Schema (Neo4j):**
```
Nodes: Accused, FIR, Victim, Location, Vehicle, Phone, BankAccount, PoliceStation
Edges:
(Accused)-[:INVOLVED_IN]->(FIR)
(Accused)-[:KNOWS]->(Accused)
(Accused)-[:USES]->(Vehicle)
(Accused)-[:USES]->(Phone)
(Accused)-[:OWNS]->(BankAccount)
(Accused)-[:FREQUENTS]->(Location)
(Victim)-[:VICTIM_IN]->(FIR)
(FIR)-[:FILED_AT]->(PoliceStation)
(FIR)-[:OCCURRED_AT]->(Location)
(Phone)-[:CONTACTED]->(Phone)
```

**Volume targets:**
- 500 FIRs across 8 Karnataka districts
- 300 accused (some with multiple FIRs)
- 50 deliberately connected in organized crime clusters
- 400 victims
- 30 police stations
- All generated with Python Faker + custom Karnataka locale

**Pitfall:** Generic faker data looks obviously fake. Mitigation: Use real Karnataka district names, police station names (BBMP jurisdiction names are public), real crime type distributions from public NCRB data.

**Fallback:** If synthetic data is too thin, the demo breaks. Generate data FIRST, load it into both Catalyst Data Store and Neo4j, verify queries work before building any UI.

---

### MODULE 1: Conversational Crime Intelligence (CORE — MUST SHIP)

**What it is:** The primary interface. Natural language in, structured intelligence out.

**Architecture:**
```
User Query
    │
    ▼
Intent Classifier (LangGraph Node 1)
    │
    ├── FIR_LOOKUP → SQL Agent
    ├── PERSON_LOOKUP → SQL + Graph Agent  
    ├── NETWORK_ANALYSIS → Graph Agent
    ├── PATTERN_ANALYSIS → Analytics Agent
    ├── HOTSPOT → Map Agent
    ├── SIMILAR_CASES → Embedding Agent
    └── FORECAST → ML Agent
    │
    ▼
Query Executor (parallel where possible)
    │
    ▼
Response Formatter (Evidence Builder)
    │
    ▼
Streaming SSE → Frontend
```

**LangGraph Graph Design:**
```python
# State definition
class AgentState(TypedDict):
    user_query: str
    session_id: str
    user_role: str
    intent: str
    context: dict           # entities from conversation history
    sql_results: list
    graph_results: list
    analytics_results: dict
    evidence_trail: list    # sources used — never empty
    response: str
    visualization_type: str # "table" | "graph" | "heatmap" | "chart" | "none"
    visualization_data: dict
    confidence: float
    follow_up_suggestions: list
```

**Nodes:**
1. `intent_classifier` — classifies query, extracts entities (district, crime type, date range, person name)
2. `context_merger` — merges current query with conversation history (enables follow-up without re-typing context)
3. `query_router` — routes to appropriate tool(s), can call multiple in parallel
4. `sql_executor` — queries Catalyst Data Store
5. `graph_executor` — queries Neo4j via bolt connection
6. `analytics_executor` — runs pandas/numpy analytics on retrieved data
7. `evidence_builder` — constructs evidence trail (FIR IDs, case IDs, sources)
8. `response_formatter` — generates human language response + structured visualization data
9. `hallucination_guard` — checks response against evidence trail, blocks any claim without source

**Hallucination Prevention (Critical):**

This is the #1 risk for Challenge 1 submissions. Every other team's chatbot will make up FIR numbers. Ours won't.

Rules enforced by `hallucination_guard` node:
- Response MUST contain only claims supported by `evidence_trail`
- FIR numbers, names, dates must be pulled from actual query results, never generated by LLM
- If query returns 0 results, the system says "No matching records found" — never invents data
- LLM is used ONLY for language generation around pre-verified facts
- System prompt explicitly instructs: "You are a formatter. Here are the verified facts. Write a response using ONLY these facts. Do not add any information not present in the facts."

**Context Management (Follow-up Queries):**

Stored in Catalyst Data Store per session:
```json
{
  "session_id": "abc123",
  "user_id": "investigator_001",
  "turn_history": [
    {
      "turn": 1,
      "query": "Show vehicle theft cases in Bengaluru East",
      "entities": {
        "crime_type": "vehicle_theft",
        "district": "Bengaluru East",
        "date_range": "last_6_months"
      },
      "result_summary": "47 cases found"
    }
  ]
}
```

Follow-up like "Are there repeat offenders?" automatically inherits `crime_type` and `district` from previous turn.

**Streaming:**
- FastAPI + SSE (Server-Sent Events)
- Frontend receives token stream as agent thinks
- Shows intermediate steps: "Searching records... Found 47 cases... Analyzing patterns..."
- Uses `astream_events` from LangGraph v2

**Pitfalls:**
- Cold start on AppSail: first request may take 10-15 seconds. Mitigation: keep-alive ping from frontend every 4 minutes.
- LLM API rate limits during demo: Mitigation: implement response caching for identical queries, use Gemini Flash (cheaper, faster) with Gemini Pro as fallback.
- Long queries timeout: Mitigation: 30-second client timeout with graceful "still computing..." message.

**Fallback if LangGraph breaks:** Simple FastAPI endpoint that does direct SQL query + template-based response formatting. No LLM. Looks less impressive but never crashes.

**Upgrade if time permits:** Add Kannada translation layer (Module 7).

---

### MODULE 2: Criminal Network Graph (HIGH PRIORITY — TARGET TO SHIP)

**What it is:** The jaw-drop feature. Interactive graph showing connections between accused, victims, locations, vehicles, phones, bank accounts.

**Backend (Neo4j Cypher queries):**

```cypher
// Find all connections for a person
MATCH (a:Accused {name: $name})-[r]-(connected)
RETURN a, r, connected

// Find organized crime clusters (accused sharing locations)
MATCH (a1:Accused)-[:FREQUENTS]->(l:Location)<-[:FREQUENTS]-(a2:Accused)
WHERE a1 <> a2
RETURN a1, l, a2

// Find suspects sharing phone contact
MATCH (a1:Accused)-[:USES]->(p1:Phone)-[:CONTACTED]->(p2:Phone)<-[:USES]-(a2:Accused)
RETURN a1, p1, p2, a2

// Community detection (use APOC or GDS if available, else manual)
MATCH (a:Accused)-[:INVOLVED_IN]->(f:FIR)<-[:INVOLVED_IN]-(b:Accused)
WHERE a <> b
RETURN a.name, b.name, count(f) as shared_cases
ORDER BY shared_cases DESC
```

**Frontend Visualization:**
- Library: **Cytoscape.js** (handles large graphs, interactive, proven)
- Fallback: **D3.js force layout** (more control, more code)
- Node colors: Accused=red, Victim=blue, Location=green, Vehicle=yellow, Phone=gray
- Click on node: shows profile panel
- Click on edge: shows relationship type + evidence

**Pitfall:** Neo4j AuraDB Free may not have Graph Data Science (GDS) plugin. Mitigation: implement community detection manually using connected components algorithm in Python on the query results, don't depend on GDS.

**Pitfall:** Rendering 500+ nodes in browser freezes it. Mitigation: always limit initial render to 2-hop neighborhood around queried entity. "Expand" button to load more.

**Fallback if Neo4j is unavailable:** Pre-compute graph structure and store as JSON in Catalyst Data Store. Render from static JSON. Loses real-time traversal but demo still looks correct.

---

### MODULE 3: Crime Hotspot Heatmap (HIGH PRIORITY — TARGET TO SHIP)

**What it is:** Interactive Karnataka map with crime density visualization, filterable by crime type, date range, district.

**Tech:**
- **Leaflet.js** for map
- **Leaflet.heat** plugin for heatmap layer
- **OpenStreetMap** tiles (free, no API key)
- Data: latitude/longitude from FIR records

**Features:**
- Filter by crime type
- Filter by date range
- Filter by district (zoom to district)
- Toggle between heatmap and cluster markers
- Click marker: shows FIR summary

**Data pipeline:**
```python
# Analytics endpoint
GET /api/hotspots?crime_type=vehicle_theft&district=Bengaluru East&from=2024-01-01

# Returns
{
  "points": [
    {"lat": 12.9716, "lng": 77.5946, "intensity": 0.8, "fir_count": 12},
    ...
  ],
  "hotspot_zones": [...],
  "trend": "increasing"  // vs historical average
}
```

**Pitfall:** Real Karnataka coordinates required. Synthetic data must use real lat/lng ranges for Karnataka districts. Pre-defined bounding boxes per district stored in config.

**Fallback:** Static pre-rendered PNG heatmap if Leaflet breaks. Embarrassing but passable.

---

### MODULE 4: Similar Case Retrieval (HIGH PRIORITY — TARGET TO SHIP)

**What it is:** Given a current FIR description, find the 5 most similar solved cases with outcomes.

**How it works:**
1. Generate embeddings for all FIR case descriptions at data load time
2. Store embeddings (use simple numpy array + cosine similarity, or pgvector if Catalyst Data Store supports it — verify)
3. On query: embed the input → cosine similarity search → return top 5

**Embedding model:** `text-embedding-3-small` (OpenAI) or `models/text-embedding-004` (Gemini) — both cheap, fast.

**Output per similar case:**
```json
{
  "fir_number": "KSP/2023/MYS/00456",
  "crime_type": "vehicle_theft",
  "district": "Mysuru",
  "similarity_score": 0.87,
  "outcome": "convicted",
  "conviction_duration_days": 180,
  "key_evidence": "CCTV footage, witness testimony",
  "investigating_officer": "SI Ramesh Kumar"
}
```

**Pitfall:** pgvector may not be available in Catalyst Data Store (MySQL-compatible). Mitigation: store embeddings as JSON blobs, load into numpy on query, compute cosine similarity in Python. Slow for 500 cases? No. 500 × 1536 dimensions fits in memory easily.

**Fallback:** If embeddings API is down during demo, fall back to TF-IDF similarity computed on crime_type + modus_operandi keywords. Less semantic, still functional.

---

### MODULE 5: Offender Risk Profiling (MEDIUM PRIORITY)

**What it is:** Per-accused risk score and behavioral profile.

**Risk score formula:**
```python
def compute_risk_score(accused):
    score = 0
    score += min(accused.prior_cases * 10, 40)          # up to 40pts for history
    score += 20 if accused.has_organized_crime_links else 0  # network centrality
    score += 15 if accused.recidivism_gap_days < 90 else 0   # quick re-offend
    score += 10 if accused.crime_types_count > 2 else 0       # diverse crime types
    score += 15 if accused.escalation_detected else 0         # escalating severity
    return min(score, 100)
```

**Profile page shows:**
- Risk score (0-100) with color coding
- Crime history timeline
- MO summary
- Known associates (links to network graph)
- Geographic range (map of incident locations)
- Similar convicted offenders

**Pitfall:** Don't present risk scores as "AI predictions" to judges without explaining the formula. Judges from law enforcement will ask how it's computed. Always show the formula. This satisfies the Explainable AI requirement.

---

### MODULE 6: Investigator Decision Support (MEDIUM PRIORITY)

**What it is:** Auto-generated case summary + timeline + recommended leads.

**Input:** FIR ID  
**Output:**
```
Case Summary: Vehicle theft of KA-01-MX-4521 reported at Whitefield PS on 14 April 2026.
Primary suspect: Raju (3 prior vehicle theft cases, Bengaluru East).

Timeline:
- 02:14 AM: Vehicle last seen at Trinity Metro Station (CCTV)
- 02:47 AM: FIR registered
- 03:10 AM: Suspect identified via prior MO match

Similar Solved Cases: 3 cases with identical MO, all resolved via CCTV + informant network.

Recommended Leads:
1. Check CCTV at Trinity Metro Station, Gate 2
2. Cross-reference with accused Raju's known associates (see network graph)
3. Contact informant network active in Whitefield area
```

**How it's generated:** LLM with strict grounding in FIR data + similar cases + graph neighbors. No hallucination permitted — same hallucination_guard applies.

---

### MODULE 7: Voice + Kannada (LOW-MEDIUM PRIORITY — ship if time allows)

**What it is:** Speech-to-text input in English and Kannada, text-to-speech response.

**Stack:**
- Speech to Text: **OpenAI Whisper** (supports Kannada reasonably well) via API
- Kannada translation: **Google Cloud Translation API** or **IndicTrans2** (open source)
- Text to Speech: **Google Cloud TTS** with `kn-IN` voice or **Bhashini API** (Indian govt NLP platform, free for Indian devs)

**Bhashini API note:** This is a Government of India initiative for Indian language NLP. Using it in a KSP hackathon submission is a strong narrative move. Register at bhashini.gov.in.

**Flow:**
```
User speaks (Kannada/English)
    → Whisper transcribes
    → If Kannada: translate to English
    → English query → LangGraph pipeline
    → Response in English
    → If original was Kannada: translate response back
    → TTS speaks response in Kannada
```

**Pitfall:** Kannada ASR accuracy is ~70-80% with Whisper. Wrong transcription → wrong query. Mitigation: always show transcription text so user can correct before submitting.

**Fallback:** If voice breaks during demo, text input works identically. Don't demo voice unless you've tested it 20 times successfully.

---

### MODULE 8: Crime Forecasting (LOW PRIORITY — ship if time allows)

**What it is:** Predict likely crime hotspots for next 30 days.

**Model:**
- Input features: district, crime_type, month, season, day_of_week, festival_flag, historical_count_same_period
- Model: XGBoost classifier (risk: low/medium/high) + Prophet for time series trend
- Training data: synthetic historical data (generate 3 years of data, train on 2.5, test on 0.5)

**Output:**
```
Forecast: Bengaluru East, Vehicle Theft
Risk Level: HIGH (74% confidence)
Based on: 31% increase in last 2 weeks, Dasara festival period historically +40% theft
```

**Pitfall:** Don't claim "98% accuracy." Judges will ask for validation. Always show confidence intervals and state this is probabilistic guidance, not a guarantee.

**Fallback:** If model isn't ready, show trend-based alerts only: "This area has shown 27% increase vs same period last year" — no ML model needed, just arithmetic.

---

### MODULE 9: Sociological Crime Insights (LOW PRIORITY — ship if time allows)

**What it is:** Correlation of crime patterns with socio-economic indicators.

**Data:** SocioEconomicZone table (pre-populated with synthetic but realistic Karnataka district data)

**Insights generated:**
- Scatter plot: literacy_rate vs crime_rate per district
- Heatmap overlay: urbanization_score + vehicle theft density
- Time series: unemployment_index vs property crime trend

**Pitfall:** Correlation ≠ causation. Any insight shown must include this caveat. Judges from law enforcement or policy background may question causal claims. Frame as "correlation analysis" not "this causes crime."

---

### MODULE 10: PDF Export (LOW PRIORITY — required by statement, quick to implement)

**What it is:** Export conversation + findings to PDF.

**Implementation:** `jsPDF` or `html2pdf.js` on frontend. Captures current conversation, any charts/graphs visible, evidence trail. Saves locally.

**Pitfall:** Graph visualizations (Cytoscape.js canvas) may not export cleanly to PDF. Mitigation: convert canvas to image (toDataURL) before PDF generation.

---

## 4. ROLE-BASED ACCESS CONTROL

Implemented via Catalyst Authentication (built-in).

| Role | Access |
|---|---|
| Investigator | Query own assigned cases + all FIR search |
| Analyst | All FIR data + analytics + network graph |
| Supervisor | All investigator + analyst + approve reports |
| Admin | Full system access + user management |
| Demo User | Full read access (for hackathon demo) |

**Implementation:** Catalyst user roles → JWT claims → FastAPI middleware checks role before executing queries.

---

## 5. EXPLAINABLE AI LAYER

Every single AI response must include:

```json
{
  "response": "47 vehicle theft cases found in Bengaluru East...",
  "evidence_trail": [
    {"type": "fir", "id": "KSP/2024/BLR/00123", "relevance": "primary match"},
    {"type": "fir", "id": "KSP/2024/BLR/00124", "relevance": "same modus operandi"},
    {"type": "graph_query", "cypher": "MATCH (a:Accused)...", "result_count": 12}
  ],
  "data_sources": ["Catalyst Data Store", "Neo4j Graph"],
  "query_executed": "SELECT * FROM FIR WHERE district='Bengaluru East'...",
  "confidence": 0.95,
  "model_used": "gemini-1.5-flash",
  "timestamp": "2026-06-17T10:32:00Z"
}
```

Frontend shows this in a collapsible "Evidence Trail" panel below every response. Clicking an FIR ID opens the full FIR record.

This is the Explainable AI requirement satisfied.

---

## 6. TECH STACK (FINAL)

| Layer | Technology | Reason | Fallback |
|---|---|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind | Familiar, fast, SSE support | React plain |
| Frontend hosting | Catalyst Slate | Required (Catalyst) | Vercel |
| API Gateway | Catalyst API Gateway | Required (Catalyst) | — |
| Auth | Catalyst Authentication | Required (Catalyst) | — |
| Relational DB | Catalyst Data Store | Required (Catalyst) | — |
| File Storage | Catalyst File Store | Required (Catalyst) | — |
| Backend (AI) | FastAPI on Catalyst AppSail | Avoids Function timeout | Flask |
| AI Orchestration | LangGraph | State machine agent | Direct API calls |
| LLM | Gemini 1.5 Flash (primary) | Fast, cheap | GPT-4o-mini |
| Embeddings | Gemini text-embedding-004 | Free tier generous | OpenAI ada-002 |
| Graph DB | Neo4j AuraDB Free | Graph traversal | JSON adjacency list |
| Map | Leaflet.js + OpenStreetMap | Free, no API key | Static image |
| Network Graph | Cytoscape.js | Interactive, handles large graphs | D3.js |
| Charts | Recharts | React-native, easy | Chart.js |
| Data generation | Python Faker + custom | — | Manual CSV |
| Voice STT | OpenAI Whisper API | Kannada support | Browser SpeechRecognition |
| Voice TTS | Bhashini API / Google TTS | Kannada voice | Browser SpeechSynthesis |
| PDF Export | html2pdf.js | Client-side, no server needed | jsPDF |
| Forecasting | XGBoost + Prophet | Proven, interpretable | Arithmetic trend |
| Similarity Search | numpy cosine similarity | No infra needed | TF-IDF |

---

## 7. BUILD TIMELINE (40 Days, Solo)

### Guiding Principle
**Ship a working core before adding features.** A fully working Module 1 + Module 2 is worth more than 8 half-working modules.

### Week 1 (Days 1-7): Foundation
- [ ] Day 1: Set up Catalyst project, AppSail, Data Store, Slate. Confirm all connections work.
- [ ] Day 2-3: Design and generate synthetic dataset (Python script). Load into Catalyst Data Store.
- [ ] Day 4: Set up Neo4j AuraDB. Load graph data. Test basic Cypher queries.
- [ ] Day 5: Build FastAPI on AppSail. Confirm it can query both Catalyst Data Store and Neo4j.
- [ ] Day 6-7: Build LangGraph skeleton (intent classifier + query router + hallucination guard). No frontend yet — test via curl/Postman.

**Week 1 Exit Criteria:** Query "Show theft cases in Mysuru" via API → returns real data from DB → evidence trail included. Nothing else matters yet.

### Week 2 (Days 8-14): Core AI + Basic Frontend
- [ ] Day 8-9: Build SQL agent + graph agent nodes in LangGraph.
- [ ] Day 10: Build context manager (follow-up query support).
- [ ] Day 11-12: Build Next.js frontend chat interface. Connect to AppSail SSE stream.
- [ ] Day 13-14: Integrate Catalyst Auth. Role-based demo users working.

**Week 2 Exit Criteria:** Full chat conversation in browser. Follow-up queries work. Evidence trail shown. No hallucinations.

### Week 3 (Days 15-21): Network Graph + Heatmap
- [ ] Day 15-16: Build Neo4j relationship queries. Build Cytoscape.js graph component.
- [ ] Day 17: Wire graph to conversational trigger ("Show connections between suspects").
- [ ] Day 18-19: Build Leaflet heatmap component. Wire to hotspot analytics endpoint.
- [ ] Day 20-21: Polish chat + graph + map. Fix layout. Make it look like a product.

**Week 3 Exit Criteria:** Network graph renders from chat command. Heatmap shows Karnataka crime density.

### Week 4 (Days 22-28): Similar Cases + Risk Profiles + Polish
- [ ] Day 22-23: Generate embeddings for all FIRs. Build similarity search endpoint.
- [ ] Day 24: Build offender risk profile page.
- [ ] Day 25-26: Build PDF export. Test conversation export.
- [ ] Day 27-28: End-to-end demo flow testing. Fix everything that breaks.

**Week 4 Exit Criteria:** Full demo story from Section 1.4 works without errors.

### Week 5 (Days 29-35): Enhancement Week (ship these if core is stable)
- [ ] Voice + Kannada (if Bhashini API works)
- [ ] Crime forecasting (XGBoost model)
- [ ] Sociological insights dashboard
- [ ] Investigator decision support auto-summary

### Week 6 (Days 36-40): Demo Prep ONLY
- [ ] NO NEW FEATURES. Zero.
- [ ] Rehearse demo story 20 times.
- [ ] Prepare 3 backup scenarios if primary demo fails.
- [ ] Stress test with 50 queries. Fix any crashes.
- [ ] Record demo video as backup if internet fails at venue.
- [ ] Prepare 2-minute pitch + 8-minute demo breakdown.

---

## 8. RISK REGISTER

| Risk | Probability | Impact | Mitigation | Status |
|---|---|---|---|---|
| LangGraph agent hallucinates FIR numbers | HIGH | Critical | hallucination_guard node, LLM only formats verified facts | Designed |
| Catalyst Function timeout during AI query | HIGH | High | All AI work in AppSail, not Functions | Designed |
| Neo4j AuraDB free tier insufficient | MEDIUM | Medium | Design dataset within 50k nodes | Designed |
| Neo4j GDS plugin unavailable | HIGH | Low | Manual community detection in Python | Designed |
| Gemini API rate limit during demo | MEDIUM | High | Response caching + Gemini Flash (faster quota) | Planned |
| Voice/Kannada STT errors | HIGH | Low | Show transcription text, allow correction | Designed |
| Cytoscape.js performance with large graph | MEDIUM | Medium | Limit initial render to 2-hop neighborhood | Designed |
| PDF export breaks graph canvas | MEDIUM | Low | canvas.toDataURL() before PDF generation | Planned |
| Synthetic data looks fake | MEDIUM | High | Use real Karnataka geography, real crime distributions | Designed |
| AppSail cold start delays demo | MEDIUM | Medium | Frontend keep-alive ping | Planned |
| Catalyst Slate/Next.js deployment issues | LOW | High | Test deployment Week 1 Day 1, not Week 5 | Planned |
| Internet failure at demo venue | LOW | Critical | Local backup demo on laptop, pre-recorded video | Planned |

---

## 9. WHAT A "VERSION 2.0" LOOKS LIKE (Upgrade Paths)

These are NOT in scope for Datathon but are documented so if a judge asks "can this scale?", you have answers.

- **Real KSP data integration:** Replace synthetic data with actual FIR API feed
- **Real-time FIR ingestion:** Kafka stream → Neo4j + Data Store
- **GIS integration:** Survey of India map tiles, sub-ward level analysis
- **CCTV integration:** Frame analysis for suspect identification
- **Biometric matching:** Aadhaar-verified accused records
- **Court case tracking:** Link FIRs to court proceedings via e-Courts API
- **Multi-language expansion:** Tamil, Telugu, Hindi via IndicTrans2
- **Mobile app:** React Native version for field investigators

---

## 10. DEMO PREPARATION

### Primary Demo Flow (10 minutes)
```
00:00 - 01:00  Problem statement in 60 seconds
               "Police today use Excel. We built an AI crime analyst."

01:00 - 03:00  Live query 1: "Show vehicle theft cases in Bengaluru East"
               → Results + trend chart

03:00 - 05:00  Live query 2: "Are there repeat offenders?"
               → Accused list with risk scores

05:00 - 07:00  Live query 3: "Show connections between them"
               → Network graph renders

07:00 - 08:30  Live query 4: "Any similar solved cases?"
               → 5 similar cases with outcomes

08:30 - 09:30  Evidence trail demonstration
               "Every claim is sourced. No hallucinations."

09:30 - 10:00  "This is what KSP investigators would actually use."
```

### Backup Demo Flow (if internet down)
Pre-load all query responses in static JSON. Frontend reads from local mock. Looks identical.

### Things That Will Impress Judges More Than Features
1. Zero hallucinations (FIR numbers are always real)
2. Evidence trail visible for every response
3. Follow-up queries work without re-typing context
4. The network graph renders smoothly
5. Kannada voice input (if it works reliably)

### Things That Will Hurt More Than Help
1. Demoing half-built features that crash
2. Claiming "98% prediction accuracy"
3. Slow responses with no streaming indicator
4. FIR numbers that don't match any database record

---

## 11. REVISION LOG

*Use this section to track any mid-build decisions. Append, never delete.*

| Date | Change | Reason |
|---|---|---|
| Jun 2026 | Initial PRD created | — |

---

## 12. APPENDIX: QUICK REFERENCE

### Catalyst CLI Commands
```bash
catalyst init
catalyst serve          # local dev
catalyst deploy         # production deploy
catalyst functions:deploy
catalyst appsail:deploy
```

### Key Environment Variables
```
GEMINI_API_KEY=
NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=
CATALYST_PROJECT_ID=
BHASHINI_API_KEY=        # if voice implemented
OPENAI_API_KEY=          # backup LLM
```

### Karnataka Districts to Cover
Bengaluru Urban, Bengaluru Rural, Mysuru, Mangaluru, Hubballi-Dharwad, Belagavi, Kalaburagi, Shivamogga

### Crime Types in Dataset
vehicle_theft, burglary, assault, drug_trafficking, fraud, robbery, kidnapping, cybercrime, domestic_violence, murder

---
*End of PRD v1.0*
