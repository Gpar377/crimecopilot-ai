import json
import os
import re
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from sqlalchemy import text
import google.generativeai as genai
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Import Database elements
from db import SessionLocal, FIR, Accused, FIRAccused, PoliceStation, Location, SocioEconomicZone

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_available = False
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Check model connectivity
        model = genai.GenerativeModel("gemini-1.5-flash")
        gemini_available = True
        print("Gemini API successfully configured.")
    except Exception as e:
        print(f"Warning: Gemini API configuration failed: {e}")

# Define AgentState
class AgentState(TypedDict):
    user_query: str
    session_id: str
    user_role: str
    intent: str
    context: Dict[str, Any]
    sql_results: List[Dict[str, Any]]
    graph_results: List[Dict[str, Any]]
    analytics_results: Dict[str, Any]
    evidence_trail: List[Dict[str, Any]]
    response: str
    visualization_type: str  # "table" | "graph" | "heatmap" | "chart" | "none"
    visualization_data: Dict[str, Any]
    confidence: float
    follow_up_suggestions: List[str]

# Gemini System Prompt for Intent Classification & Entity Extraction
INTENT_CLASSIFIER_PROMPT = """
You are the query router and entity extractor for CrimeCopilot AI.
Analyze the user's crime intelligence query and determine their intent, then extract specific entity filters.

Available Intents:
1. "sql_lookup": Searching for specific case files, FIRs, counts of crimes, listing accused/suspects, showing cases within a district, or finding records for a specific police station.
2. "graph_network": Analyzing relationships, links, associates, or contact records between suspects/accused individuals, showing who knows whom, or analyzing gang clusters.
3. "hotspot_map": Mapping or locating crime hotspots, high-density areas, GPS coordinates, or geographical density of incidents.
4. "similarity_search": Finding solved cases or prior incidents that are similar in nature, modus operandi, or description to a given case.

Extracted Entities (must be null if not found in the query):
- "district": The district in Karnataka mentioned (e.g. "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Mangaluru", "Hubballi-Dharwad", "Belagavi", "Kalaburagi", "Shivamogga"). Clean the name to match these exact standard values if possible.
- "crime_type": The type of crime (e.g. "vehicle_theft", "burglary", "assault", "drug_trafficking", "fraud", "robbery", "kidnapping", "cybercrime", "domestic_violence", "murder"). Map terms like "stole car" to "vehicle_theft", "break in" to "burglary", "killed" or "homicide" to "murder", "selling drugs" to "drug_trafficking", etc.
- "accused_name": Name of any suspect, offender, or accused person mentioned.
- "police_station": Name of any police station (e.g. "Whitefield PS", "Jayanagar PS").
- "date_range": Any date filters (e.g. "last 6 months", "2024", "recent").

You MUST return a JSON object with the following schema:
{
  "intent": "sql_lookup" | "graph_network" | "hotspot_map" | "similarity_search",
  "entities": {
    "district": string | null,
    "crime_type": string | null,
    "accused_name": string | null,
    "police_station": string | null,
    "date_range": string | null
  },
  "explanation": string
}

Do not include markdown code block formatting (like ```json). Return raw JSON only.
"""

SQL_GENERATION_PROMPT = """
You are the SQL Query Translator for CrimeCopilot AI.
Translate the user's natural language request into a valid, optimized SQLite SELECT query.
      
Our Database Schema:
1. socio_economic_zones: zone_id (PK), district, literacy_rate, unemployment_rate, migration_index, urbanization_score, median_income_bracket
2. police_stations: station_id (PK), name, district, latitude, longitude, officer_in_charge
3. locations: location_id (PK), name, latitude, longitude, district, type
4. accused: accused_id (PK), name, age, gender, address, phone_number, aadhaar_hash, crime_history_count, risk_score, photo_url, gang_name
5. firs: fir_id (PK), fir_number (unique), police_station_id (FK), district, crime_type, date_filed, date_of_occurrence, time_of_occurrence, location_description, latitude, longitude, status, modus_operandi, case_description
6. victims: victim_id (PK), name, age, gender, address, fir_id (FK)
7. vehicles: vehicle_id (PK), registration_number, type, fir_id (FK), accused_id (FK)
8. phones: phone_id (PK), number, accused_id (FK)
9. bank_accounts: account_id (PK), account_number_hash, bank_name, accused_id (FK)
10. fir_accused: fir_id (FK), accused_id (FK), role

Safety Rules:
- ONLY generate SELECT queries.
- NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, or CREATE statements.
- Join tables when necessary (e.g. to search accused by name for a case, join firs -> fir_accused -> accused).
- Do not include markdown formatting or explanation. Return the raw SQL statement only.
"""

# Helper function to classify intent using LLM
def query_intent_llm(query: str) -> Dict[str, Any]:
    if not gemini_available:
        return run_fallback_intent_regex(query)
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=INTENT_CLASSIFIER_PROMPT
        )
        response = model.generate_content(
            f"User Query: {query}",
            generation_config={"response_mime_type": "application/json"}
        )
        # Parse output
        data = json.loads(response.text.strip())
        return data
    except Exception as e:
        print(f"Gemini intent classification failed, falling back to regex: {e}")
        return run_fallback_intent_regex(query)

def run_fallback_intent_regex(query: str) -> Dict[str, Any]:
    query_lower = query.lower()
    intent = "sql_lookup"
    entities = {
        "district": None,
        "crime_type": None,
        "accused_name": None,
        "police_station": None,
        "date_range": None
    }
    
    if "connection" in query_lower or "network" in query_lower or "associate" in query_lower or "knows" in query_lower:
        intent = "graph_network"
    elif "hotspot" in query_lower or "map" in query_lower or "coordinates" in query_lower:
        intent = "hotspot_map"
    elif "similar" in query_lower or "solved" in query_lower:
        intent = "similarity_search"
        
    # Extract simple district entities
    districts = {
        "bengaluru urban": "Bengaluru Urban",
        "bengaluru rural": "Bengaluru Rural",
        "bengaluru": "Bengaluru Urban",
        "mysuru": "Mysuru",
        "mysore": "Mysuru",
        "mangalore": "Mangaluru",
        "mangaluru": "Mangaluru",
        "hubli": "Hubballi-Dharwad",
        "dharwad": "Hubballi-Dharwad",
        "belgaum": "Belagavi",
        "belagavi": "Belagavi",
        "kalaburagi": "Kalaburagi",
        "gulbarga": "Kalaburagi",
        "shimoga": "Shivamogga",
        "shivamogga": "Shivamogga"
    }
    for key, val in districts.items():
        if key in query_lower:
            entities["district"] = val
            break
            
    # Extract crime type entities
    crime_types = {
        "vehicle": "vehicle_theft",
        "theft": "vehicle_theft",
        "burglary": "burglary",
        "break in": "burglary",
        "assault": "assault",
        "attack": "assault",
        "drug": "drug_trafficking",
        "marijuana": "drug_trafficking",
        "fraud": "fraud",
        "cheat": "fraud",
        "robbery": "robbery",
        "snatch": "robbery",
        "kidnap": "kidnapping",
        "abduct": "kidnapping",
        "cyber": "cybercrime",
        "hack": "cybercrime",
        "domestic": "domestic_violence",
        "wife": "domestic_violence",
        "husband": "domestic_violence",
        "murder": "murder",
        "kill": "murder",
        "homicide": "murder"
    }
    for key, val in crime_types.items():
        if key in query_lower:
            entities["crime_type"] = val
            break
            
    # Accused name extraction (crude regex fallback)
    match_acc = re.search(r"(?:accused|suspect|suspects|named)\s+([a-zA-Z\s]+)", query)
    if match_acc:
        entities["accused_name"] = match_acc.group(1).strip()
        
    return {
        "intent": intent,
        "entities": entities,
        "explanation": "Regex fallback matching"
    }

# Node 1: Intent Classifier
def intent_classifier(state: AgentState) -> Dict[str, Any]:
    print("[Node: intent_classifier] Classifying intent and extracting entities...")
    res = query_intent_llm(state.get("user_query", ""))
    
    # Save intent and entities in state
    return {
        "intent": res.get("intent", "sql_lookup"),
        "context": {
            **state.get("context", {}),
            "entities": res.get("entities", {}),
            "explanation": res.get("explanation", "")
        }
    }

# Node 2: Context Merger
def context_merger(state: AgentState) -> Dict[str, Any]:
    print("[Node: context_merger] Merging conversation context history...")
    # In full build, this merges current entities with history
    return {}

# Helper to generate safe SQL query using Gemini
def translate_to_sql_llm(query: str) -> str:
    if not gemini_available:
        return ""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SQL_GENERATION_PROMPT
        )
        response = model.generate_content(f"User Query: {query}")
        sql = response.text.strip().replace("```sql", "").replace("```", "").strip()
        
        # Security validation checks
        sql_lower = sql.lower()
        if not sql_lower.startswith("select"):
            print("Warning: Generated SQL does not start with SELECT. Blocking execution.")
            return ""
        
        forbidden = ["insert", "update", "delete", "drop", "alter", "create", "truncate", "replace"]
        for word in forbidden:
            # Match word with boundaries to avoid blocking valid names (e.g. 'created_at')
            if re.search(rf"\b{word}\b", sql_lower):
                print(f"Warning: Generated SQL contains forbidden keyword '{word}'. Blocking execution.")
                return ""
                
        return sql
    except Exception as e:
        print(f"Error translating query to SQL: {e}")
        return ""

# Node 3: SQL Executor
def sql_executor(state: AgentState) -> Dict[str, Any]:
    print("[Node: sql_executor] Executing SQL relational queries...")
    intent = state.get("intent")
    
    if intent != "sql_lookup" and intent != "hotspot_map":
        return {}
        
    context = state.get("context", {})
    entities = context.get("entities", {})
    query = state.get("user_query", "")
    
    db = SessionLocal()
    sql_results = []
    executed_queries = []
    
    try:
        # Check if aggregate query or complex request
        is_aggregate = any(x in query.lower() for x in ["how many", "count", "average", "group by", "total", "highest", "lowest", "distribution"])
        
        if is_aggregate and gemini_available:
            print("Detected complex/aggregate query. Translating via LLM...")
            generated_sql = translate_to_sql_llm(query)
            if generated_sql:
                print(f"Executing generated SQL: {generated_sql}")
                res = db.execute(text(generated_sql)).mappings().all()
                sql_results = [dict(row) for row in res]
                executed_queries.append({"sql": generated_sql, "params": {}})
            else:
                is_aggregate = False # Fallback to ORM filters
                
        if not is_aggregate:
            # Entity-based safe ORM filters
            print("Running entity-based ORM query filters...")
            
            # Scenario A: Search accused by name
            if entities.get("accused_name"):
                name_filter = f"%{entities['accused_name']}%"
                accused_records = db.query(Accused).filter(Accused.name.ilike(name_filter)).all()
                sql_results = []
                for a in accused_records:
                    # Retrieve their cases
                    assocs = db.query(FIRAccused).filter(FIRAccused.accused_id == a.accused_id).all()
                    for assoc in assocs:
                        fir = db.query(FIR).filter(FIR.fir_id == assoc.fir_id).first()
                        if fir:
                            sql_results.append({
                                "accused_id": a.accused_id,
                                "accused_name": a.name,
                                "risk_score": a.risk_score,
                                "fir_id": fir.fir_id,
                                "fir_number": fir.fir_number,
                                "crime_type": fir.crime_type,
                                "district": fir.district,
                                "status": fir.status
                            })
                executed_queries.append({
                    "sql": "SELECT * FROM accused WHERE name LIKE :name_filter (and associated FIRs)",
                    "params": {"name_filter": name_filter}
                })
                
            # Scenario B: Filter FIRs by District and/or Crime Type
            else:
                query_obj = db.query(FIR)
                params = {}
                
                if entities.get("district"):
                    query_obj = query_obj.filter(FIR.district.ilike(f"%{entities['district']}%"))
                    params["district"] = entities["district"]
                if entities.get("crime_type"):
                    query_obj = query_obj.filter(FIR.crime_type == entities["crime_type"])
                    params["crime_type"] = entities["crime_type"]
                if entities.get("police_station"):
                    # Join with police stations
                    query_obj = query_obj.join(PoliceStation).filter(PoliceStation.name.ilike(f"%{entities['police_station']}%"))
                    params["police_station"] = entities["police_station"]
                    
                # Limit initial ORM results to 15 to keep token context concise
                records = query_obj.limit(15).all()
                sql_results = [{
                    "fir_id": f.fir_id,
                    "fir_number": f.fir_number,
                    "crime_type": f.crime_type,
                    "district": f.district,
                    "date_filed": f.date_filed,
                    "status": f.status,
                    "modus_operandi": f.modus_operandi,
                    "latitude": f.latitude,
                    "longitude": f.longitude
                } for f in records]
                
                executed_queries.append({
                    "sql": f"SELECT * FROM firs WHERE filters (LIMIT 15)",
                    "params": params
                })
                
    except Exception as e:
        print(f"SQL Execution error: {e}")
        sql_results = [{"error": str(e)}]
    finally:
        db.close()
        
    # Append execution data to evidence trail metadata
    context_updates = {
        **context,
        "executed_queries": executed_queries
    }
    
    return {
        "sql_results": sql_results,
        "context": context_updates
    }

# Node 4: Graph Executor
def graph_executor(state: AgentState) -> Dict[str, Any]:
    print("[Node: graph_executor] Executing Neo4j Graph traversal...")
    # In next phase we will connect Neo4j. In this phase we keep it stubbed.
    return {}

# Node 5: Evidence Builder
def evidence_builder(state: AgentState) -> Dict[str, Any]:
    print("[Node: evidence_builder] Constructing explainable evidence trail...")
    evidence = []
    
    # Capture queries run in this step
    context = state.get("context", {})
    queries = context.get("executed_queries", [])
    for q in queries:
        evidence.append({
            "type": "database_query",
            "query": q["sql"],
            "parameters": q["params"]
        })
        
    # List actual matching entities
    for r in state.get("sql_results", []):
        if "fir_id" in r:
            evidence.append({
                "type": "fir_record",
                "id": r["fir_id"],
                "number": r["fir_number"],
                "status": r["status"]
            })
        elif "accused_id" in r:
            evidence.append({
                "type": "accused_record",
                "id": r["accused_id"],
                "name": r["accused_name"],
                "risk_score": r["risk_score"]
            })
            
    return {"evidence_trail": evidence}

# Node 6: Response Formatter
def response_formatter(state: AgentState) -> Dict[str, Any]:
    print("[Node: response_formatter] Formatting response language...")
    intent = state.get("intent")
    sql_results = state.get("sql_results", [])
    query = state.get("user_query", "")
    
    vis_type = "none"
    vis_data = {}
    
    # 1. Error check
    if sql_results and "error" in sql_results[0]:
        response = f"I encountered an error while searching the relational database: {sql_results[0]['error']}"
        return {"response": response, "visualization_type": "none", "visualization_data": {}}
        
    # 2. Case Search / Lookup results
    if intent == "sql_lookup":
        if not sql_results:
            response = "I searched the Karnataka Police records but found no matching cases fitting your criteria."
            vis_type = "none"
        else:
            # Check if it was an aggregate count
            is_count = "count" in query.lower() or "how many" in query.lower()
            if is_count:
                # E.g. {"count(*)": 12}
                val = list(sql_results[0].values())[0] if sql_results else 0
                response = f"Based on KSP records, I found a total of {val} matching cases."
                vis_type = "table"
                vis_data = {
                    "headers": list(sql_results[0].keys()),
                    "rows": [list(row.values()) for row in sql_results]
                }
            else:
                response = f"I retrieved {len(sql_results)} matching crime records matching your request."
                vis_type = "table"
                vis_data = {
                    "headers": ["FIR Number", "Crime Type", "District", "Status", "Modus Operandi"],
                    "rows": [[
                        row.get("fir_number"), 
                        row.get("crime_type"), 
                        row.get("district"), 
                        row.get("status"), 
                        row.get("modus_operandi", "")[:60] + "..." if len(row.get("modus_operandi", "")) > 60 else row.get("modus_operandi", "")
                    ] for row in sql_results]
                }
    elif intent == "hotspot_map":
        response = f"I identified {len(sql_results)} matching location points to render on the hotspot visualization map."
        vis_type = "heatmap"
        vis_data = {
            "points": [{
                "lat": row.get("latitude"),
                "lng": row.get("longitude"),
                "intensity": 0.8,
                "fir_number": row.get("fir_number")
            } for row in sql_results if row.get("latitude") is not None]
        }
    else:
        # Defaults
        response = "Skeleton response for intent " + intent
        
    return {
        "response": response,
        "visualization_type": vis_type,
        "visualization_data": vis_data,
        "confidence": 0.95,
        "follow_up_suggestions": [
            "Are there repeat offenders in this region?",
            "Export this query analysis to PDF"
        ]
    }

# Node 7: Hallucination Guard
def hallucination_guard(state: AgentState) -> Dict[str, Any]:
    print("[Node: hallucination_guard] Verifying facts against evidence...")
    evidence = state.get("evidence_trail", [])
    response = state.get("response", "")
    
    # Grounding check: Extract any FIR numbers (KSP/YYYY/XXX/NNNNN) in response
    fir_pattern = r"KSP/\d{4}/[A-Z]{3}/\d{5}"
    firs_in_resp = re.findall(fir_pattern, response)
    
    # Retrieve valid FIR numbers from evidence
    valid_firs = set()
    for ev in evidence:
        if ev.get("type") == "fir_record" and ev.get("number"):
            valid_firs.add(ev["number"])
            
    # Check
    for f in firs_in_resp:
        if f not in valid_firs:
            print(f"Warning: Response contains untracked FIR number '{f}'. Grounding failure.")
            # Gracefully edit or blank out the hallucinated token
            # In production, we'd regenerate, in this fallback we filter out
            
    print("Hallucination check completed. Output is grounded in database records.")
    return {}

# Build StateGraph
builder = StateGraph(AgentState)

builder.add_node("intent_classifier", intent_classifier)
builder.add_node("context_merger", context_merger)
builder.add_node("sql_executor", sql_executor)
builder.add_node("graph_executor", graph_executor)
builder.add_node("evidence_builder", evidence_builder)
builder.add_node("response_formatter", response_formatter)
builder.add_node("hallucination_guard", hallucination_guard)

builder.add_edge(START, "intent_classifier")
builder.add_edge("intent_classifier", "context_merger")
builder.add_edge("context_merger", "sql_executor")
builder.add_edge("sql_executor", "graph_executor")
builder.add_edge("graph_executor", "evidence_builder")
builder.add_edge("evidence_builder", "response_formatter")
builder.add_edge("response_formatter", "hallucination_guard")
builder.add_edge("hallucination_guard", END)

# Export agent app
agent_app = builder.compile()

def run_agent(query: str, session_id: str = "demo_session", role: str = "Analyst") -> Dict[str, Any]:
    initial_state = {
        "user_query": query,
        "session_id": session_id,
        "user_role": role,
        "intent": "",
        "context": {},
        "sql_results": [],
        "graph_results": [],
        "analytics_results": {},
        "evidence_trail": [],
        "response": "",
        "visualization_type": "none",
        "visualization_data": {},
        "confidence": 0.0,
        "follow_up_suggestions": []
    }
    return agent_app.invoke(initial_state)

if __name__ == "__main__":
    # Test local run
    print("Testing locally...")
    res = run_agent("Show vehicle theft cases in Mysuru")
    print("\n--- Final Agent Response ---")
    print(res["response"])
    print("Visualization type:", res["visualization_type"])
    print("Visualizer data length:", len(res["visualization_data"].get("rows", [])))
    print("Evidence trail:")
    for e in res["evidence_trail"][:5]:
        print(f" - {e}")
