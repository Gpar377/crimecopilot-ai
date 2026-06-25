import json
import os
import sys

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        sys.exit(1)
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    print("Validating generated synthetic dataset...")
    
    # Load all files
    se_zones = load_json("data/socio_economic_zones.json")
    stations = load_json("data/stations.json")
    locations = load_json("data/locations.json")
    accused = load_json("data/accused.json")
    phones = load_json("data/phones.json")
    bank_accounts = load_json("data/bank_accounts.json")
    vehicles = load_json("data/vehicles.json")
    firs = load_json("data/firs.json")
    victims = load_json("data/victims.json")
    relationships = load_json("data/relationships.json")
    
    # Store IDs for quick lookup
    zone_ids = {z["zone_id"] for z in se_zones}
    station_ids = {s["station_id"] for s in stations}
    location_ids = {l["location_id"] for l in locations}
    accused_ids = {a["accused_id"] for a in accused}
    phone_ids = {p["phone_id"] for p in phones}
    phone_numbers = {p["number"] for p in phones}
    account_ids = {b["account_id"] for b in bank_accounts}
    vehicle_ids = {v["vehicle_id"] for v in vehicles}
    fir_ids = {f["fir_id"] for f in firs}
    victim_ids = {v["victim_id"] for v in victims}
    
    errors = []
    
    # 1. Validate SE Zones
    print("Checking Socio-Economic Zones...")
    for idx, z in enumerate(se_zones):
        if not z.get("zone_id") or not z.get("district"):
            errors.append(f"SE Zone at index {idx} is missing zone_id or district.")
            
    # 2. Validate Stations
    print("Checking Police Stations...")
    for idx, s in enumerate(stations):
        if not s.get("station_id") or not s.get("name") or not s.get("district"):
            errors.append(f"Police Station at index {idx} is missing required fields.")
        if s.get("latitude") is None or s.get("longitude") is None:
            errors.append(f"Police Station {s.get('station_id')} is missing coordinates.")
            
    # 3. Validate Locations
    print("Checking Locations...")
    for idx, l in enumerate(locations):
        if not l.get("location_id") or not l.get("name") or not l.get("district"):
            errors.append(f"Location at index {idx} is missing required fields.")
            
    # 4. Validate Accused
    print("Checking Accused Profiles...")
    for idx, a in enumerate(accused):
        a_id = a.get("accused_id")
        if not a_id or not a.get("name") or a.get("risk_score") is None:
            errors.append(f"Accused at index {idx} is missing required fields.")
        if a.get("risk_score") < 0 or a.get("risk_score") > 100:
            errors.append(f"Accused {a_id} has invalid risk score: {a.get('risk_score')}")
            
    # 5. Validate Phones, Accounts, Vehicles
    print("Checking Accused Attachments (Phones, Bank Accounts, Vehicles)...")
    for p in phones:
        if p.get("accused_id") not in accused_ids:
            errors.append(f"Phone {p.get('phone_id')} links to non-existent accused: {p.get('accused_id')}")
            
    for b in bank_accounts:
        if b.get("accused_id") not in accused_ids:
            errors.append(f"Bank Account {b.get('account_id')} links to non-existent accused: {b.get('accused_id')}")
            
    for v in vehicles:
        if v.get("accused_id") not in accused_ids:
            errors.append(f"Vehicle {v.get('vehicle_id')} links to non-existent accused: {v.get('accused_id')}")
        if v.get("fir_id") not in fir_ids:
            errors.append(f"Vehicle {v.get('vehicle_id')} links to non-existent FIR: {v.get('fir_id')}")
            
    # 6. Validate FIRs
    print("Checking FIRs...")
    for f in firs:
        f_id = f.get("fir_id")
        if not f_id or not f.get("fir_number") or not f.get("police_station_id"):
            errors.append(f"FIR at index {idx} is missing required fields.")
        if f.get("police_station_id") not in station_ids:
            errors.append(f"FIR {f_id} links to non-existent police station: {f.get('police_station_id')}")
            
    # 7. Validate Victims
    print("Checking Victims...")
    for v in victims:
        v_id = v.get("victim_id")
        if not v_id or not v.get("fir_id"):
            errors.append(f"Victim at index {idx} is missing required fields.")
        if v.get("fir_id") not in fir_ids:
            errors.append(f"Victim {v_id} links to non-existent FIR: {v.get('fir_id')}")
            
    # 8. Validate Relationships
    print("Checking Graph Relationships...")
    for idx, r in enumerate(relationships):
        r_type = r.get("type")
        source = r.get("source")
        target = r.get("target")
        
        if not r_type or not source or not target:
            errors.append(f"Relationship at index {idx} is missing type, source, or target.")
            continue
            
        # Referential integrity checks per relationship type
        if r_type == "FILED_AT":
            if source not in fir_ids:
                errors.append(f"FILED_AT source {source} does not exist in FIRs.")
            if target not in station_ids:
                errors.append(f"FILED_AT target {target} does not exist in Stations.")
        elif r_type == "OCCURRED_AT":
            if source not in fir_ids:
                errors.append(f"OCCURRED_AT source {source} does not exist in FIRs.")
            if target not in location_ids:
                errors.append(f"OCCURRED_AT target {target} does not exist in Locations.")
        elif r_type == "VICTIM_IN":
            if source not in victim_ids:
                errors.append(f"VICTIM_IN source {source} does not exist in Victims.")
            if target not in fir_ids:
                errors.append(f"VICTIM_IN target {target} does not exist in FIRs.")
        elif r_type == "INVOLVED_IN":
            if source not in accused_ids:
                errors.append(f"INVOLVED_IN source {source} does not exist in Accused.")
            if target not in fir_ids:
                errors.append(f"INVOLVED_IN target {target} does not exist in FIRs.")
        elif r_type == "USES_VEHICLE":
            if source not in accused_ids:
                errors.append(f"USES_VEHICLE source {source} does not exist in Accused.")
            if target not in vehicle_ids:
                errors.append(f"USES_VEHICLE target {target} does not exist in Vehicles.")
        elif r_type == "VEHICLE_LINKED_TO_FIR":
            if source not in vehicle_ids:
                errors.append(f"VEHICLE_LINKED_TO_FIR source {source} does not exist in Vehicles.")
            if target not in fir_ids:
                errors.append(f"VEHICLE_LINKED_TO_FIR target {target} does not exist in FIRs.")
        elif r_type == "FREQUENTS":
            if source not in accused_ids:
                errors.append(f"FREQUENTS source {source} does not exist in Accused.")
            if target not in location_ids:
                errors.append(f"FREQUENTS target {target} does not exist in Locations.")
        elif r_type == "USES_PHONE":
            if source not in accused_ids:
                errors.append(f"USES_PHONE source {source} does not exist in Accused.")
            if target not in phone_ids:
                errors.append(f"USES_PHONE target {target} does not exist in Phones.")
        elif r_type == "OWNS_ACCOUNT":
            if source not in accused_ids:
                errors.append(f"OWNS_ACCOUNT source {source} does not exist in Accused.")
            if target not in account_ids:
                errors.append(f"OWNS_ACCOUNT target {target} does not exist in Bank Accounts.")
        elif r_type == "KNOWS":
            if source not in accused_ids:
                errors.append(f"KNOWS source {source} does not exist in Accused.")
            if target not in accused_ids:
                errors.append(f"KNOWS target {target} does not exist in Accused.")
        elif r_type == "CONTACTED":
            if source not in phone_numbers:
                errors.append(f"CONTACTED source phone {source} is not registered to any accused.")
            if target not in phone_numbers:
                errors.append(f"CONTACTED target phone {target} is not registered to any accused.")
        else:
            errors.append(f"Unknown relationship type found: {r_type}")

    # Output Validation Report
    print("---------------------------------------")
    if not errors:
        print("Success: Dataset validation passed with 0 errors!")
        sys.exit(0)
    else:
        print(f"Failed: Dataset validation failed with {len(errors)} errors:")
        for err in errors[:20]:
            print(f"- {err}")
        if len(errors) > 20:
            print(f"... and {len(errors) - 20} more errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
