import json
import os
import sys
from db import (
    SessionLocal, init_db, SocioEconomicZone, PoliceStation, Location, 
    Accused, FIR, FIRAccused, Victim, Vehicle, Phone, BankAccount
)

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        sys.exit(1)
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    print("Initializing local database schema...")
    init_db()
    
    db = SessionLocal()
    try:
        print("Loading JSON datasets...")
        se_zones_data = load_json("data/socio_economic_zones.json")
        stations_data = load_json("data/stations.json")
        locations_data = load_json("data/locations.json")
        accused_data = load_json("data/accused.json")
        phones_data = load_json("data/phones.json")
        accounts_data = load_json("data/bank_accounts.json")
        vehicles_data = load_json("data/vehicles.json")
        firs_data = load_json("data/firs.json")
        victims_data = load_json("data/victims.json")
        relationships_data = load_json("data/relationships.json")

        # Clear existing data to ensure idempotent seed runs
        print("Clearing existing records...")
        db.query(FIRAccused).delete()
        db.query(Vehicle).delete()
        db.query(Victim).delete()
        db.query(FIR).delete()
        db.query(Phone).delete()
        db.query(BankAccount).delete()
        db.query(Accused).delete()
        db.query(Location).delete()
        db.query(PoliceStation).delete()
        db.query(SocioEconomicZone).delete()
        db.commit()

        print("Seeding Socio-Economic Zones...")
        for z in se_zones_data:
            db.add(SocioEconomicZone(
                zone_id=z["zone_id"],
                district=z["district"],
                literacy_rate=z["literacy_rate"],
                unemployment_rate=z["unemployment_rate"],
                migration_index=z["migration_index"],
                urbanization_score=z["urbanization_score"],
                median_income_bracket=z["median_income_bracket"]
            ))

        print("Seeding Police Stations...")
        for s in stations_data:
            db.add(PoliceStation(
                station_id=s["station_id"],
                name=s["name"],
                district=s["district"],
                latitude=s["latitude"],
                longitude=s["longitude"],
                officer_in_charge=s["officer_in_charge"]
            ))

        print("Seeding Locations...")
        for l in locations_data:
            db.add(Location(
                location_id=l["location_id"],
                name=l["name"],
                latitude=l["latitude"],
                longitude=l["longitude"],
                district=l["district"],
                type=l["type"]
            ))

        print("Seeding Accused Profiles...")
        for a in accused_data:
            db.add(Accused(
                accused_id=a["accused_id"],
                name=a["name"],
                age=a["age"],
                gender=a["gender"],
                address=a["address"],
                phone_number=a["phone_number"],
                aadhaar_hash=a["aadhaar_hash"],
                crime_history_count=a["crime_history_count"],
                risk_score=a["risk_score"],
                photo_url=a["photo_url"],
                gang_name=a["gang_name"]
            ))

        print("Seeding Phones...")
        for p in phones_data:
            db.add(Phone(
                phone_id=p["phone_id"],
                number=p["number"],
                accused_id=p["accused_id"]
            ))

        print("Seeding Bank Accounts...")
        for b in accounts_data:
            db.add(BankAccount(
                account_id=b["account_id"],
                account_number_hash=b["account_number_hash"],
                bank_name=b["bank_name"],
                accused_id=b["accused_id"]
            ))

        print("Seeding FIRs...")
        for f in firs_data:
            db.add(FIR(
                fir_id=f["fir_id"],
                fir_number=f["fir_number"],
                police_station_id=f["police_station_id"],
                district=f["district"],
                crime_type=f["crime_type"],
                date_filed=f["date_filed"],
                date_of_occurrence=f["date_of_occurrence"],
                time_of_occurrence=f["time_of_occurrence"],
                location_description=f["location_description"],
                latitude=f["latitude"],
                longitude=f["longitude"],
                status=f["status"],
                modus_operandi=f["modus_operandi"],
                case_description=f["case_description"]
            ))

        print("Seeding Victims...")
        for v in victims_data:
            db.add(Victim(
                victim_id=v["victim_id"],
                name=v["name"],
                age=v["age"],
                gender=v["gender"],
                address=v["address"],
                fir_id=v["fir_id"]
            ))

        print("Seeding Vehicles...")
        for v in vehicles_data:
            db.add(Vehicle(
                vehicle_id=v["vehicle_id"],
                registration_number=v["registration_number"],
                type=v["type"],
                fir_id=v["fir_id"],
                accused_id=v["accused_id"]
            ))

        db.commit()

        print("Seeding Junction Table (FIR Accused Associations)...")
        # Extract INVOLVED_IN relations
        for r in relationships_data:
            if r.get("type") == "INVOLVED_IN":
                db.add(FIRAccused(
                    fir_id=r["target"],
                    accused_id=r["source"],
                    role=r.get("role", "suspect")
                ))
        db.commit()
        print("Data loaded to SQL successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error loading SQL data: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
