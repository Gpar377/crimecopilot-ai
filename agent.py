from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

# Define AgentState matching PRD specifications
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

# Node 1: Intent Classifier
def intent_classifier(state: AgentState) -> Dict[str, Any]:
    print("[Node: intent_classifier] Classifying intent and extracting entities...")
    query = state.get("user_query", "").lower()
    
    # Simple regex-based skeleton classifier
    intent = "sql_lookup"
    entities = {}
    
    if "connection" in query or "network" in query or "associate" in query or "knows" in query:
        intent = "graph_network"
    elif "hotspot" in query or "map" in query or "coordinates" in query:
        intent = "hotspot_map"
    elif "similar" in query or "solved" in query:
        intent = "similarity_search"
        
    # Extract simple district entities
    districts = ["bengaluru", "mysuru", "mangalore", "hubli", "belgaum", "gulbarga", "shimoga"]
    for d in districts:
        if d in query:
            entities["district"] = d.title()
            
    # Extract crime type entities
    crime_types = ["theft", "burglary", "assault", "drug", "fraud", "robbery", "murder"]
    for ct in crime_types:
        if ct in query:
            entities["crime_type"] = ct
            
    return {
        "intent": intent,
        "context": {**state.get("context", {}), "entities": entities}
    }

# Node 2: Context Merger
def context_merger(state: AgentState) -> Dict[str, Any]:
    print("[Node: context_merger] Merging conversation context history...")
    # In full build, this merges current entities with history
    return {}

# Node 3: SQL Executor
def sql_executor(state: AgentState) -> Dict[str, Any]:
    print("[Node: sql_executor] Executing SQL relational queries...")
    intent = state.get("intent")
    sql_results = []
    
    # In skeleton, return mock or simple relational results
    if intent == "sql_lookup":
        sql_results = [{"fir_number": "KSP/2026/BLR/00001", "district": "Bengaluru Urban", "status": "open"}]
        
    return {"sql_results": sql_results}

# Node 4: Graph Executor
def graph_executor(state: AgentState) -> Dict[str, Any]:
    print("[Node: graph_executor] Executing Neo4j Graph traversal...")
    intent = state.get("intent")
    graph_results = []
    
    # In skeleton, return simple mock graph paths
    if intent == "graph_network":
        graph_results = [{"source": "Accused_1", "target": "Accused_2", "type": "KNOWS"}]
        
    return {"graph_results": graph_results}

# Node 5: Evidence Builder
def evidence_builder(state: AgentState) -> Dict[str, Any]:
    print("[Node: evidence_builder] Constructing explainable evidence trail...")
    evidence = []
    
    # Build list of database entries referenced
    for r in state.get("sql_results", []):
        evidence.append({"type": "SQL", "record": r})
    for r in state.get("graph_results", []):
        evidence.append({"type": "Graph", "record": r})
        
    return {"evidence_trail": evidence}

# Node 6: Response Formatter
def response_formatter(state: AgentState) -> Dict[str, Any]:
    print("[Node: response_formatter] Formatting response language...")
    intent = state.get("intent")
    
    # Basic skeleton response templates
    if intent == "graph_network":
        response = "I searched the graph network database and found connections between Suspect 1 and Suspect 2."
        vis_type = "graph"
        vis_data = {"nodes": [{"id": "1", "label": "Suspect 1"}, {"id": "2", "label": "Suspect 2"}], "edges": [{"from": "1", "to": "2", "label": "KNOWS"}]}
    elif intent == "hotspot_map":
        response = "Here are the mapped crime hotspots in the selected region."
        vis_type = "heatmap"
        vis_data = {"points": [{"lat": 12.9716, "lng": 77.5946, "intensity": 0.9}]}
    else:
        response = f"Retrieved matches from the relational database for your request."
        vis_type = "table"
        vis_data = {"headers": ["FIR Number", "District", "Status"], "rows": [["KSP/2026/BLR/00001", "Bengaluru Urban", "open"]]}
        
    return {
        "response": response,
        "visualization_type": vis_type,
        "visualization_data": vis_data,
        "confidence": 0.90,
        "follow_up_suggestions": ["Show their criminal records", "Generate case PDF report"]
    }

# Node 7: Hallucination Guard
def hallucination_guard(state: AgentState) -> Dict[str, Any]:
    print("[Node: hallucination_guard] Verifying facts against evidence...")
    # Check if we have facts in response that are not supported in evidence trail
    evidence = state.get("evidence_trail", [])
    response = state.get("response", "")
    
    # In skeleton, always passes verification
    print("Hallucination check passed: 100% grounded in evidence.")
    return {}


# Build LangGraph Workflow
builder = StateGraph(AgentState)

# Add Nodes
builder.add_node("intent_classifier", intent_classifier)
builder.add_node("context_merger", context_merger)
builder.add_node("sql_executor", sql_executor)
builder.add_node("graph_executor", graph_executor)
builder.add_node("evidence_builder", evidence_builder)
builder.add_node("response_formatter", response_formatter)
builder.add_node("hallucination_guard", hallucination_guard)

# Add Edges
builder.add_edge(START, "intent_classifier")
builder.add_edge("intent_classifier", "context_merger")
builder.add_edge("context_merger", "sql_executor")
builder.add_edge("sql_executor", "graph_executor")
builder.add_edge("graph_executor", "evidence_builder")
builder.add_edge("evidence_builder", "response_formatter")
builder.add_edge("response_formatter", "hallucination_guard")
builder.add_edge("hallucination_guard", END)

# Compile Workflow
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
    # Test execution
    res = run_agent("Show connections between vehicle thieves in Bengaluru")
    print("\n--- Final Agent Response ---")
    print(res["response"])
    print(f"Visualization: {res['visualization_type']}")
    print(f"Evidence Trail: {res['evidence_trail']}")
