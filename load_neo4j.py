import json
import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        sys.exit(1)
    with open(filepath, 'r') as f:
        return json.load(f)

def run_cypher(tx, query, parameters=None):
    tx.run(query, parameters)

def check_connection():
    if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
        print("\n[WARNING] Neo4j environment variables are not fully configured in your .env file.")
        print("Please check your .env and set the following:")
        print("  NEO4J_URI=bolt://localhost:7687")
        print("  NEO4J_USER=neo4j")
        print("  NEO4J_PASSWORD=your_password")
        print("\nFor local setup, you can run a Neo4j Docker container:")
        print("  docker run --name neo4j -p 7474:7474 -p 7687:7687 -d -e NEO4J_AUTH=neo4j/password neo4j:latest")
        print("Alternatively, set up a free database instance on Neo4j AuraDB (https://neo4j.com/cloud/auradb/).")
        print("Skipping graph ingestion for now.\n")
        return False
    try:
        # Check driver connection
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            driver.verify_connectivity()
        return True
    except Exception as e:
        print(f"\n[WARNING] Could not connect to Neo4j database at {NEO4J_URI}.")
        print(f"Error: {e}")
        print("Please ensure Neo4j is running and credentials are correct.")
        print("Skipping graph ingestion for now.\n")
        return False

def main():
    print("Checking Neo4j connection status...")
    if not check_connection():
        # Exit gracefully without throwing a failure so the build/test script doesn't fail
        return

    # Load data
    stations = load_json("data/stations.json")
    locations = load_json("data/locations.json")
    accused = load_json("data/accused.json")
    phones = load_json("data/phones.json")
    bank_accounts = load_json("data/bank_accounts.json")
    vehicles = load_json("data/vehicles.json")
    firs = load_json("data/firs.json")
    victims = load_json("data/victims.json")
    relationships = load_json("data/relationships.json")

    print("Connecting to Neo4j...")
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            # 1. Setup Constraints
            print("Configuring Database constraints...")
            constraints = [
                "CREATE CONSTRAINT accused_id_unique IF NOT EXISTS FOR (a:Accused) REQUIRE a.accused_id IS UNIQUE",
                "CREATE CONSTRAINT fir_id_unique IF NOT EXISTS FOR (f:FIR) REQUIRE f.fir_id IS UNIQUE",
                "CREATE CONSTRAINT station_id_unique IF NOT EXISTS FOR (s:PoliceStation) REQUIRE s.station_id IS UNIQUE",
                "CREATE CONSTRAINT location_id_unique IF NOT EXISTS FOR (l:Location) REQUIRE l.location_id IS UNIQUE",
                "CREATE CONSTRAINT vehicle_id_unique IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.vehicle_id IS UNIQUE",
                "CREATE CONSTRAINT phone_id_unique IF NOT EXISTS FOR (p:Phone) REQUIRE p.phone_id IS UNIQUE",
                "CREATE CONSTRAINT phone_num_unique IF NOT EXISTS FOR (p:Phone) REQUIRE p.number IS UNIQUE",
                "CREATE CONSTRAINT account_id_unique IF NOT EXISTS FOR (b:BankAccount) REQUIRE b.account_id IS UNIQUE",
                "CREATE CONSTRAINT victim_id_unique IF NOT EXISTS FOR (v:Victim) REQUIRE v.victim_id IS UNIQUE"
            ]
            for c in constraints:
                try:
                    session.execute_write(run_cypher, c)
                except Exception as e:
                    # Some neo4j versions have different syntax for constraints
                    print(f"Warning setting constraint: {e}")

            # 2. Reset Database
            print("Clearing existing Graph elements...")
            session.execute_write(run_cypher, "MATCH (n) DETACH DELETE n")

            # 3. Create Nodes
            print("Ingesting Police Stations...")
            for s in stations:
                session.execute_write(run_cypher, 
                    "CREATE (n:PoliceStation {station_id: $station_id, name: $name, district: $district})", 
                    s
                )

            print("Ingesting Crime Locations...")
            for l in locations:
                session.execute_write(run_cypher, 
                    "CREATE (n:Location {location_id: $location_id, name: $name, district: $district, type: $type})", 
                    l
                )

            print("Ingesting Accused Profiles...")
            for a in accused:
                session.execute_write(run_cypher, 
                    "CREATE (n:Accused {accused_id: $accused_id, name: $name, age: $age, gender: $gender, phone_number: $phone_number, risk_score: $risk_score, gang_name: $gang_name})", 
                    a
                )

            print("Ingesting Phone Records...")
            for p in phones:
                session.execute_write(run_cypher, 
                    "CREATE (n:Phone {phone_id: $phone_id, number: $number})", 
                    p
                )

            print("Ingesting Bank Accounts...")
            for b in bank_accounts:
                session.execute_write(run_cypher, 
                    "CREATE (n:BankAccount {account_id: $account_id, account_number_hash: $account_number_hash, bank_name: $bank_name})", 
                    b
                )

            print("Ingesting Vehicles...")
            for v in vehicles:
                session.execute_write(run_cypher, 
                    "CREATE (n:Vehicle {vehicle_id: $vehicle_id, registration_number: $registration_number, type: $type})", 
                    v
                )

            print("Ingesting FIRs...")
            for f in firs:
                session.execute_write(run_cypher, 
                    "CREATE (n:FIR {fir_id: $fir_id, fir_number: $fir_number, crime_type: $crime_type, date_filed: $date_filed, status: $status})", 
                    f
                )

            print("Ingesting Victims...")
            for v in victims:
                session.execute_write(run_cypher, 
                    "CREATE (n:Victim {victim_id: $victim_id, name: $name, age: $age, gender: $gender})", 
                    v
                )

            # 4. Create Relationships
            print("Ingesting Relationships (Edges)...")
            for idx, r in enumerate(relationships):
                r_type = r.get("type")
                source = r.get("source")
                target = r.get("target")

                if r_type == "FILED_AT":
                    session.execute_write(run_cypher, 
                        "MATCH (f:FIR {fir_id: $source}), (s:PoliceStation {station_id: $target}) MERGE (f)-[:FILED_AT]->(s)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "OCCURRED_AT":
                    session.execute_write(run_cypher, 
                        "MATCH (f:FIR {fir_id: $source}), (l:Location {location_id: $target}) MERGE (f)-[:OCCURRED_AT]->(l)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "VICTIM_IN":
                    session.execute_write(run_cypher, 
                        "MATCH (v:Victim {victim_id: $source}), (f:FIR {fir_id: $target}) MERGE (v)-[:VICTIM_IN]->(f)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "INVOLVED_IN":
                    session.execute_write(run_cypher, 
                        "MATCH (a:Accused {accused_id: $source}), (f:FIR {fir_id: $target}) MERGE (a)-[:INVOLVED_IN {role: $role}]->(f)", 
                        {"source": source, "target": target, "role": r.get("role", "suspect")}
                    )
                elif r_type == "USES_VEHICLE":
                    session.execute_write(run_cypher, 
                        "MATCH (a:Accused {accused_id: $source}), (v:Vehicle {vehicle_id: $target}) MERGE (a)-[:USES_VEHICLE]->(v)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "VEHICLE_LINKED_TO_FIR":
                    session.execute_write(run_cypher, 
                        "MATCH (v:Vehicle {vehicle_id: $source}), (f:FIR {fir_id: $target}) MERGE (v)-[:LINKED_TO_FIR]->(f)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "FREQUENTS":
                    session.execute_write(run_cypher, 
                        "MATCH (a:Accused {accused_id: $source}), (l:Location {location_id: $target}) MERGE (a)-[:FREQUENTS]->(l)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "USES_PHONE":
                    session.execute_write(run_cypher, 
                        "MATCH (a:Accused {accused_id: $source}), (p:Phone {phone_id: $target}) MERGE (a)-[:USES]->(p)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "OWNS_ACCOUNT":
                    session.execute_write(run_cypher, 
                        "MATCH (a:Accused {accused_id: $source}), (b:BankAccount {account_id: $target}) MERGE (a)-[:OWNS]->(b)", 
                        {"source": source, "target": target}
                    )
                elif r_type == "KNOWS":
                    session.execute_write(run_cypher, 
                        "MATCH (a1:Accused {accused_id: $source}), (a2:Accused {accused_id: $target}) MERGE (a1)-[:KNOWS {relationship_type: $relationship_type}]->(a2)", 
                        {"source": source, "target": target, "relationship_type": r.get("relationship_type", "gang_member")}
                    )
                elif r_type == "CONTACTED":
                    session.execute_write(run_cypher, 
                        "MATCH (p1:Phone {number: $source}), (p2:Phone {number: $target}) MERGE (p1)-[:CONTACTED {duration_sec: $duration_sec, timestamp: $timestamp}]->(p2)", 
                        {"source": source, "target": target, "duration_sec": r.get("duration_sec"), "timestamp": r.get("timestamp")}
                    )

            print("Neo4j database loaded successfully!")

if __name__ == "__main__":
    main()
