import json
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker with a fallback locale
fake = Faker('en_IN')

# Setup seed for reproducibility
random.seed(42)
Faker.seed(42)

# Bounding boxes for Karnataka districts (Lat, Lng)
DISTRICT_BOUNDS = {
    "Bengaluru Urban": {"lat": (12.85, 13.10), "lng": (77.45, 77.75)},
    "Bengaluru Rural": {"lat": (13.15, 13.40), "lng": (77.30, 77.60)},
    "Mysuru": {"lat": (12.25, 12.35), "lng": (76.58, 76.72)},
    "Mangaluru": {"lat": (12.82, 12.95), "lng": (74.80, 74.95)},
    "Hubballi-Dharwad": {"lat": (15.35, 15.48), "lng": (75.05, 75.20)},
    "Belagavi": {"lat": (15.82, 15.92), "lng": (74.48, 74.60)},
    "Kalaburagi": {"lat": (17.28, 17.38), "lng": (76.78, 76.90)},
    "Shivamogga": {"lat": (13.88, 14.00), "lng": (75.52, 75.68)},
}

# Police Stations mapped to districts
POLICE_STATIONS_CONFIG = {
    "Bengaluru Urban": ["Whitefield PS", "Indiranagar PS", "Koramangala PS", "Jayanagar PS", "Ulsoor PS", "Electronic City PS", "HSR Layout PS"],
    "Bengaluru Rural": ["Davanagere PS", "Devenahalli PS", "Nelamangala PS", "Hosakote PS"],
    "Mysuru": ["Lashkar PS", "Devaraja PS", "K.R. Puram PS", "Vidyaranyapuram PS"],
    "Mangaluru": ["Mangaluru Town PS", "Kadri PS", "Urwa PS", "Ullal PS"],
    "Hubballi-Dharwad": ["Hubballi Town PS", "Suburban PS", "Dharwad Town PS", "Vidyagiri PS"],
    "Belagavi": ["Belagavi Town PS", "Khade Bazar PS", "Udyambag PS"],
    "Kalaburagi": ["Kalaburagi Town PS", "Station Bazar PS", "Chowk PS"],
    "Shivamogga": ["Shivamogga Town PS", "Kote PS", "Tunga Nagar PS"],
}

CRIME_TYPES = [
    "vehicle_theft", "burglary", "assault", "drug_trafficking", 
    "fraud", "robbery", "kidnapping", "cybercrime", 
    "domestic_violence", "murder"
]

MODUS_OPERANDI = {
    "vehicle_theft": [
        "steals unlocked motorcycle using a master key",
        "uses signal jammer to disable GPS, hotwires ignition",
        "breaks window of parked car, steals and transports to scrap yard",
        "carjacks vehicle at gunpoint in low-lit highway stretches",
        "rents vehicle under fake identity documents and sells it off"
    ],
    "burglary": [
        "enters via balcony/terrace doors during midnight hours",
        "breaks padlock of commercial shops using iron rod",
        "masquerades as delivery executive, surveys house, strikes later",
        "drills locks of residential apartments when owners are on vacation",
        "enters through bathroom window ventilation shaft"
    ],
    "assault": [
        "verbal altercation escalates to physical violence using blunt objects",
        "pre-planned attack by rival gang members using sharp weapons",
        "road rage incident leading to physical assault of other driver",
        "drunken brawl at local establishment escalating to street fight",
        "land dispute settlement turning violent with physical harm"
    ],
    "drug_trafficking": [
        "peddles small bags of synthetic drugs in student neighborhoods",
        "transports bulk marijuana concealed in vegetable delivery trucks",
        "coordinates drug sales via encrypted messaging apps, drop-offs in parks",
        "smuggles contraband via inter-state luxury passenger buses",
        "operates clandestine drug manufacturing setup in rented warehouse"
    ],
    "fraud": [
        "identity theft to obtain personal credit cards and run up bills",
        "ponzi scheme promising high returns on agricultural land investments",
        "phishing email campaign targeting senior citizens for banking credentials",
        "forgery of property deed documents to sell land owned by NRIs",
        "fake job consultancy charging fees for non-existent overseas positions"
    ],
    "robbery": [
        "snatches gold chains from women pedestrians using speeding motorcycle",
        "robs convenience store cashier at knifepoint during late-night shift",
        "intercepts commuters on highway bypass roads, robs cash and phones",
        "breaks into house, binds occupants, steals jewelry and cash under threat",
        "picks pockets in crowded local markets and bus stations using razor blade"
    ],
    "kidnapping": [
        "abducts child of businessman from school gate for ransom",
        "holds victim hostage over unpaid financial business debt",
        "honeytraps victim, abducts and demands ransom from family",
        "kidnaps rival gang member for retaliation and intimidation",
        "abducts minor girl under false pretext of marriage"
    ],
    "cybercrime": [
        "unauthorized access to corporate database, demanding ransom in Bitcoin",
        "financial fraud using cloned SIM cards to bypass OTP verification",
        "creates fake social media profiles of prominent officials to extort money",
        "phishing portal mimicking government tax website to steal credentials",
        "deploys malware to steal credential logs from internet cafe terminals"
    ],
    "domestic_violence": [
        "physical and verbal harassment by husband and in-laws over dowry demands",
        "habitual physical assault under influence of alcohol in family residence",
        "emotional abuse and confinement of spouse within household limits",
        "assault of family members during domestic property division dispute",
        "systematic harassment and denial of basic medical care to elderly parents"
    ],
    "murder": [
        "homicidal attack due to long-standing family property dispute",
        "retaliatory gang murder using sharp weapons in public area",
        "murder for financial gain during a home break-in",
        "crime of passion following a heated domestic dispute",
        "contract killing ordered by business rival, executed by local gang"
    ]
}

VEHICLE_TYPES = ["Motorcycle", "Scooter", "Auto-rickshaw", "Sedan", "SUV", "Hatchback", "Truck"]
BANK_NAMES = ["State Bank of India", "Canara Bank", "HDFC Bank", "ICICI Bank", "Karnataka Bank", "Bank of Baroda"]
LOCATION_TYPES = ["metro_station", "market", "residential_area", "commercial_hub", "highway", "slum_pocket", "industrial_estate"]

def get_random_coords(district):
    bounds = DISTRICT_BOUNDS.get(district, DISTRICT_BOUNDS["Bengaluru Urban"])
    lat = random.uniform(bounds["lat"][0], bounds["lat"][1])
    lng = random.uniform(bounds["lng"][0], bounds["lng"][1])
    return round(lat, 5), round(lng, 5)

def generate_aadhaar():
    return f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"

def generate_phone():
    return f"+91-{random.randint(6, 9)}{random.randint(100000000, 999999999)}"

def generate_vehicle_reg():
    dist_code = random.choice(["01", "02", "03", "04", "05", "51", "53"])
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=2))
    digits = f"{random.randint(1000, 9999)}"
    return f"KA-{dist_code}-{letters}-{digits}"

def generate_crime_description(crime_type, offender_name, victim_name, location_name, date_str, mo):
    descriptions = {
        "vehicle_theft": [
            f"On {date_str}, complainant reported that their vehicle was stolen from {location_name}. The offender {mo}. Suspect identified as {offender_name}.",
            f"Vehicle theft report registered. Complainant parked their two-wheeler near {location_name} and returned to find it missing. CCTV footage shows suspect matching {offender_name}'s description who {mo}."
        ],
        "burglary": [
            f"A house break-in was reported at a residential property in {location_name} during the night. Gold ornaments and cash worth lakhs stolen. The perpetrator {mo}. Evidence points to local gang associate {offender_name}.",
            f"Complainant reported that a locked shop in {location_name} was burgled. The locks were broken, and electronic items were missing. Investigation suggests the burglar {mo}. Informant network suspects {offender_name}."
        ],
        "assault": [
            f"A physical altercation broke out near {location_name} between the victim {victim_name} and the accused {offender_name}. The dispute arose over parking issues, leading the accused to commit assault. {offender_name} {mo}.",
            f"Accused {offender_name} assaulted victim {victim_name} in broad daylight at {location_name}. The altercation escalated from a verbal dispute regarding business transactions. Accused {mo}."
        ],
        "drug_trafficking": [
            f"Based on credible information, a raid was conducted near {location_name}. Accused {offender_name} was found in possession of commercial quantities of banned drugs. The suspect {mo}.",
            f"During routine patrol near {location_name}, officers intercepted {offender_name} acting suspiciously. Search revealed hidden pockets containing synthetic narcotics. The suspect {mo}."
        ],
        "fraud": [
            f"Complainant {victim_name} was cheated of their savings by the accused {offender_name} who ran a fake investment scheme. The fraudster {mo}.",
            f"A cyber fraud complaint filed by {victim_name} details unauthorized transfers from their bank account. The fraudster {mo}. Investigation linked the OTP logs to {offender_name}."
        ],
        "robbery": [
            f"The victim {victim_name} was walking near {location_name} when the accused {offender_name} intercepted them. Under threat, the accused robbed the victim of jewelry. The robber {mo}.",
            f"A robbery incident was reported on the bypass road near {location_name}. Complainant was stopped while driving by {offender_name} who {mo} and took their mobile and cash."
        ],
        "kidnapping": [
            f"Complainant reported that their relative was missing and they subsequently received a ransom call demanding money. The kidnappers {mo}. Accused {offender_name} is suspected to be involved.",
            f"An abduction case was filed. Victim {victim_name} was forcibly taken in a vehicle near {location_name}. The abductor {mo}. Leads suggest gang led by {offender_name} is responsible."
        ],
        "cybercrime": [
            f"Company portal reported a ransomware attack where the system database was locked. The perpetrator {mo}. Digital footprint traced to server logs associated with {offender_name}.",
            f"A massive phishing scam reported by bank customers. The cybercriminal {mo}. Account trails trace back to beneficiary accounts registered under dummy names managed by {offender_name}."
        ],
        "domestic_violence": [
            f"Victim {victim_name} filed a complaint against husband {offender_name} detailing persistent physical abuse and harassment. The accused {mo}.",
            f"Domestic harassment case registered at the local station. Complainant details how the accused {offender_name} {mo} over family disputes and locked them out of the house."
        ],
        "murder": [
            f"A body was found near {location_name} with multiple injuries. Investigating officers identified the victim as {victim_name}. The murderer {mo}. Suspect {offender_name} arrested after attempt to flee.",
            f"Homicide case registered. Rivalry between gang elements erupted in violent clash near {location_name} resulting in the death of {victim_name}. The assailant {offender_name} {mo}."
        ]
    }
    
    return random.choice(descriptions.get(crime_type, ["Crime details registered for investigation."]))

def calculate_risk_score(prior_cases, has_gang, reoffend_gap, crime_types_count, escalation):
    score = 0
    score += min(prior_cases * 10, 40)
    score += 20 if has_gang else 0
    score += 15 if reoffend_gap < 90 else 0
    score += 10 if crime_types_count > 2 else 0
    score += 15 if escalation else 0
    return min(score, 100)

def main():
    print("Generating synthetic dataset...")
    os.makedirs("data", exist_ok=True)
    
    # 1. Generate Socio-Economic Zones
    districts = list(DISTRICT_BOUNDS.keys())
    se_zones = []
    for idx, dist in enumerate(districts):
        se_zones.append({
            "zone_id": f"SEZ_{idx+1:03d}",
            "district": dist,
            "literacy_rate": round(random.uniform(65.0, 88.0), 2),
            "unemployment_rate": round(random.uniform(3.0, 15.0), 2),
            "migration_index": round(random.uniform(0.1, 0.9), 2),
            "urbanization_score": round(random.uniform(10, 95), 1),
            "median_income_bracket": random.choice(["Low", "Medium-Low", "Medium", "Medium-High", "High"])
        })
    
    # 2. Generate Police Stations
    stations = []
    station_id_map = {}
    st_counter = 1
    for dist, names in POLICE_STATIONS_CONFIG.items():
        for name in names:
            st_id = f"PS_{st_counter:03d}"
            lat, lng = get_random_coords(dist)
            stations.append({
                "station_id": st_id,
                "name": name,
                "district": dist,
                "latitude": lat,
                "longitude": lng,
                "officer_in_charge": f"Inspector {fake.name()}"
            })
            station_id_map[name] = st_id
            st_counter += 1
            
    # 3. Generate Recurring Crime Locations
    locations = []
    loc_counter = 1
    for dist in districts:
        # Generate 10 key locations per district
        for i in range(10):
            loc_id = f"LOC_{loc_counter:03d}"
            lat, lng = get_random_coords(dist)
            locations.append({
                "location_id": loc_id,
                "name": f"{fake.city()} {random.choice(LOCATION_TYPES).replace('_', ' ').title()}",
                "latitude": lat,
                "longitude": lng,
                "district": dist,
                "type": random.choice(LOCATION_TYPES)
            })
            loc_counter += 1
            
    # 4. Generate Accused (Suspects)
    accused_list = []
    accused_phones = []
    accused_accounts = []
    accused_vehicles = []
    
    # We will generate 300 suspects.
    # Out of these, let's create 5 gang clusters (about 10 members each) to make the graph network awesome.
    gangs = []
    for g_idx in range(5):
        gang_members = []
        gang_name = f"Gang_{g_idx+1}"
        gangs.append((gang_name, gang_members))
        
    for a_idx in range(300):
        a_id = f"ACC_{a_idx+1:03d}"
        gender = random.choice(["Male", "Male", "Male", "Female"]) # Male skewed in crime data
        name = fake.name_male() if gender == "Male" else fake.name_female()
        
        # Decide if this person is in a gang (first 50 suspects)
        gang_name = None
        if a_idx < 50:
            gang_idx = a_idx // 10
            gang_name, gang_members = gangs[gang_idx]
            gang_members.append(a_id)
            
        accused_list.append({
            "accused_id": a_id,
            "name": name,
            "age": random.randint(18, 65),
            "gender": gender,
            "address": fake.address().replace("\n", ", "),
            "phone_number": generate_phone(),
            "aadhaar_hash": generate_aadhaar(),
            "crime_history_count": 0, # Will update based on FIR assignment
            "risk_score": 0,          # Will compute later
            "photo_url": f"https://api.dicebear.com/7.x/avataaars/svg?seed={name.replace(' ', '')}",
            "gang_name": gang_name
        })
        
        # Phones linked to accused
        p_id = f"PH_{a_idx+1:03d}"
        accused_phones.append({
            "phone_id": p_id,
            "number": accused_list[-1]["phone_number"],
            "accused_id": a_id
        })
        
        # Bank Accounts linked to accused
        accused_accounts.append({
            "account_id": f"AC_{a_idx+1:03d}",
            "account_number_hash": f"{random.randint(100000000000, 999999999999)}",
            "bank_name": random.choice(BANK_NAMES),
            "accused_id": a_id
        })
        
    # 5. Generate FIRs & Victims
    firs = []
    victims = []
    relationships = []
    
    # Track case counts per accused to calculate history and risk scores
    accused_history = {a["accused_id"]: [] for a in accused_list}
    
    start_date = datetime(2023, 1, 1)
    
    # 500 FIRs
    for f_idx in range(500):
        fir_id = f"FIR_{f_idx+1:03d}"
        
        # Select station and location
        station = random.choice(stations)
        dist = station["district"]
        dist_locations = [l for l in locations if l["district"] == dist]
        location = random.choice(dist_locations)
        
        crime_type = random.choice(CRIME_TYPES)
        mo_list = MODUS_OPERANDI[crime_type]
        mo = random.choice(mo_list)
        
        # Generate occurrence date with festival spikes (Dasara/Diwali in Oct/Nov)
        days_offset = random.randint(0, 1200) # ~3 years
        occ_date = start_date + timedelta(days=days_offset)
        
        # Festival boost
        if occ_date.month in [10, 11] and crime_type in ["vehicle_theft", "robbery", "burglary"]:
            # Increased chance of robbery/theft in holiday seasons
            if random.random() < 0.3:
                # Add another case
                pass
                
        date_filed = occ_date + timedelta(hours=random.randint(1, 48))
        time_occ = f"{random.randint(0,23):02d}:{random.randint(0,59):02d}:00"
        
        # Assign Accused to this FIR
        # To make things realistic, some cases have multiple accused, some have none (unsolved), and some are repeat offenders.
        assigned_accused = []
        
        # 10% chance of unsolved (no accused)
        if random.random() > 0.10:
            # Decide if gang crime (if it's a major crime in Bengaluru and we choose from first 50 suspects)
            if random.random() < 0.15 and dist in ["Bengaluru Urban", "Bengaluru Rural"]:
                # Select a gang
                gang_name, gang_members = random.choice(gangs)
                # Assign 2-3 members of this gang
                num_members = min(len(gang_members), random.randint(2, 3))
                assigned_accused = random.sample(gang_members, num_members)
            else:
                # Standard crime: 1-2 random accused
                num_accused = random.choices([1, 2], weights=[0.85, 0.15])[0]
                assigned_accused = random.sample([a["accused_id"] for a in accused_list], num_accused)
                
        # Select one primary accused's name for description
        primary_offender_name = "Unknown Suspect"
        if assigned_accused:
            primary_acc = [a for a in accused_list if a["accused_id"] == assigned_accused[0]][0]
            primary_offender_name = primary_acc["name"]
            
        # Create victim
        v_gender = random.choice(["Male", "Female"])
        v_name = fake.name_male() if v_gender == "Male" else fake.name_female()
        v_id = f"VIC_{f_idx+1:03d}"
        victims.append({
            "victim_id": v_id,
            "name": v_name,
            "age": random.randint(5, 75),
            "gender": v_gender,
            "address": fake.address().replace("\n", ", "),
            "fir_id": fir_id
        })
        
        case_desc = generate_crime_description(
            crime_type, primary_offender_name, v_name, location["name"], 
            occ_date.strftime("%Y-%m-%d"), mo
        )
        
        # Create FIR entry
        fir_num_dist_code = dist[:3].upper()
        fir_number = f"KSP/{occ_date.year}/{fir_num_dist_code}/{f_idx+1:05d}"
        
        status = random.choices(
            ["open", "closed", "chargesheeted", "acquitted", "convicted"],
            weights=[0.15, 0.10, 0.40, 0.10, 0.25]
        )[0]
        
        firs.append({
            "fir_id": fir_id,
            "fir_number": fir_number,
            "police_station_id": station["station_id"],
            "district": dist,
            "crime_type": crime_type,
            "date_filed": date_filed.strftime("%Y-%m-%d"),
            "date_of_occurrence": occ_date.strftime("%Y-%m-%d"),
            "time_of_occurrence": time_occ,
            "location_description": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "status": status,
            "modus_operandi": mo,
            "case_description": case_desc
        })
        
        # Map Graph Relationships
        relationships.append({
            "type": "FILED_AT",
            "source": fir_id,
            "target": station["station_id"]
        })
        relationships.append({
            "type": "OCCURRED_AT",
            "source": fir_id,
            "target": location["location_id"]
        })
        relationships.append({
            "type": "VICTIM_IN",
            "source": v_id,
            "target": fir_id
        })
        
        for idx, a_id in enumerate(assigned_accused):
            role = "primary" if idx == 0 else "secondary"
            relationships.append({
                "type": "INVOLVED_IN",
                "source": a_id,
                "target": fir_id,
                "role": role
            })
            
            # Save historical case date to calculate offender risk profile
            accused_history[a_id].append({
                "date": occ_date,
                "crime_type": crime_type,
                "status": status
            })
            
            # Vehicles used by accused in the crime (sometimes)
            if crime_type in ["vehicle_theft", "robbery", "burglary"] and random.random() < 0.4:
                reg_num = generate_vehicle_reg()
                veh_id = f"VEH_{len(accused_vehicles)+1:03d}"
                accused_vehicles.append({
                    "vehicle_id": veh_id,
                    "registration_number": reg_num,
                    "type": random.choice(VEHICLE_TYPES),
                    "fir_id": fir_id,
                    "accused_id": a_id
                })
                relationships.append({
                    "type": "USES_VEHICLE",
                    "source": a_id,
                    "target": veh_id
                })
                relationships.append({
                    "type": "VEHICLE_LINKED_TO_FIR",
                    "source": veh_id,
                    "target": fir_id
                })
                
            # Accused frequents this location
            relationships.append({
                "type": "FREQUENTS",
                "source": a_id,
                "target": location["location_id"]
            })

    # Update Accused History Counts & Compute Risk Scores
    for a in accused_list:
        a_id = a["accused_id"]
        history = accused_history[a_id]
        prior_cases = len(history)
        a["crime_history_count"] = prior_cases
        
        # Calculate attributes for risk profiling
        has_gang = a["gang_name"] is not None
        
        # Calculate re-offending gap
        reoffend_gap = 9999
        if prior_cases >= 2:
            sorted_dates = sorted([h["date"] for h in history])
            gaps = [(sorted_dates[i+1] - sorted_dates[i]).days for i in range(len(sorted_dates)-1)]
            reoffend_gap = min(gaps) if gaps else 9999
            
        crime_types = set([h["crime_type"] for h in history])
        crime_types_count = len(crime_types)
        
        # Check for crime escalation (e.g. moving from theft/burglary to assault/murder)
        escalation = False
        if prior_cases >= 2:
            sorted_history = sorted(history, key=lambda x: x["date"])
            first_type = sorted_history[0]["crime_type"]
            last_type = sorted_history[-1]["crime_type"]
            violent_crimes = ["assault", "robbery", "kidnapping", "murder"]
            non_violent_crimes = ["vehicle_theft", "burglary", "fraud", "cybercrime"]
            if first_type in non_violent_crimes and last_type in violent_crimes:
                escalation = True
                
        a["risk_score"] = calculate_risk_score(prior_cases, has_gang, reoffend_gap, crime_types_count, escalation)
        
        # Write generic graph relationships
        # USES_PHONE
        p_id = f"PH_{a['accused_id'].split('_')[1]}"
        relationships.append({
            "type": "USES_PHONE",
            "source": a_id,
            "target": p_id
        })
        # OWNS_ACCOUNT
        ac_id = f"AC_{a['accused_id'].split('_')[1]}"
        relationships.append({
            "type": "OWNS_ACCOUNT",
            "source": a_id,
            "target": ac_id
        })

    # 6. Generate Gang Networks (KNOWS relationship in graph)
    # If two accused are in the same gang, they know each other.
    for gang_name, gang_members in gangs:
        for i in range(len(gang_members)):
            for j in range(i + 1, len(gang_members)):
                relationships.append({
                    "type": "KNOWS",
                    "source": gang_members[i],
                    "target": gang_members[j],
                    "relationship_type": "gang_member"
                })
                
    # 7. Generate Phone Contact Detail Records (CONTACTED relations)
    # Simulate contact records between gang members (highly contacted) and random suspects
    phone_relations = []
    # Gang members contacted each other
    for gang_name, gang_members in gangs:
        for i in range(len(gang_members)):
            for j in range(i + 1, len(gang_members)):
                p1_id = f"PH_{gang_members[i].split('_')[1]}"
                p2_id = f"PH_{gang_members[j].split('_')[1]}"
                
                # Retrieve phone numbers
                p1 = [p for p in accused_phones if p["phone_id"] == p1_id][0]["number"]
                p2 = [p for p in accused_phones if p["phone_id"] == p2_id][0]["number"]
                
                # Generate 2-5 calls between them
                for _ in range(random.randint(2, 5)):
                    phone_relations.append({
                        "type": "CONTACTED",
                        "source": p1,
                        "target": p2,
                        "duration_sec": random.randint(10, 1800),
                        "timestamp": (start_date + timedelta(days=random.randint(0, 1200), hours=random.randint(0,23))).strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
    relationships.extend(phone_relations)

    # 8. Save everything to JSON files
    with open("data/socio_economic_zones.json", "w") as f:
        json.dump(se_zones, f, indent=2)
    with open("data/stations.json", "w") as f:
        json.dump(stations, f, indent=2)
    with open("data/locations.json", "w") as f:
        json.dump(locations, f, indent=2)
    with open("data/accused.json", "w") as f:
        json.dump(accused_list, f, indent=2)
    with open("data/phones.json", "w") as f:
        json.dump(accused_phones, f, indent=2)
    with open("data/bank_accounts.json", "w") as f:
        json.dump(accused_accounts, f, indent=2)
    with open("data/vehicles.json", "w") as f:
        json.dump(accused_vehicles, f, indent=2)
    with open("data/firs.json", "w") as f:
        json.dump(firs, f, indent=2)
    with open("data/victims.json", "w") as f:
        json.dump(victims, f, indent=2)
    with open("data/relationships.json", "w") as f:
        json.dump(relationships, f, indent=2)

    print("Synthetic dataset successfully generated:")
    print(f"- {len(se_zones)} Socio-Economic Zones")
    print(f"- {len(stations)} Police Stations")
    print(f"- {len(locations)} Key Crime Locations")
    print(f"- {len(accused_list)} Accused individuals")
    print(f"- {len(accused_phones)} Phone numbers linked to accused")
    print(f"- {len(accused_accounts)} Bank accounts linked to accused")
    print(f"- {len(accused_vehicles)} Vehicles linked to crimes/accused")
    print(f"- {len(firs)} FIRs")
    print(f"- {len(victims)} Victims")
    print(f"- {len(relationships)} Graph Relationships (edges)")

if __name__ == "__main__":
    main()
