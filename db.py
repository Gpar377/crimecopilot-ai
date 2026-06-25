import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///crimecopilot.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Junction table for FIR-Accused relationship (Many-to-Many with association details)
class FIRAccused(Base):
    __tablename__ = "fir_accused"
    
    fir_id = Column(String(50), ForeignKey("firs.fir_id"), primary_key=True)
    accused_id = Column(String(50), ForeignKey("accused.accused_id"), primary_key=True)
    role = Column(String(50), nullable=False) # e.g. "primary", "secondary", "suspect"

    # Relationships
    fir = relationship("FIR", back_populates="accused_associations")
    accused = relationship("Accused", back_populates="fir_associations")


class SocioEconomicZone(Base):
    __tablename__ = "socio_economic_zones"
    
    zone_id = Column(String(50), primary_key=True)
    district = Column(String(100), nullable=False)
    literacy_rate = Column(Float, nullable=False)
    unemployment_rate = Column(Float, nullable=False)
    migration_index = Column(Float, nullable=False)
    urbanization_score = Column(Float, nullable=False)
    median_income_bracket = Column(String(50), nullable=False)


class PoliceStation(Base):
    __tablename__ = "police_stations"
    
    station_id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    district = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    officer_in_charge = Column(String(150), nullable=False)

    firs = relationship("FIR", back_populates="police_station")


class Location(Base):
    __tablename__ = "locations"
    
    location_id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    district = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)


class Accused(Base):
    __tablename__ = "accused"
    
    accused_id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    address = Column(String(500), nullable=False)
    phone_number = Column(String(50), nullable=False)
    aadhaar_hash = Column(String(100), nullable=False)
    crime_history_count = Column(Integer, default=0)
    risk_score = Column(Integer, default=0)
    photo_url = Column(String(500), nullable=True)
    gang_name = Column(String(100), nullable=True)

    # Relationships
    fir_associations = relationship("FIRAccused", back_populates="accused", cascade="all, delete-orphan")
    phones = relationship("Phone", back_populates="accused", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="accused", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="accused")


class FIR(Base):
    __tablename__ = "firs"
    
    fir_id = Column(String(50), primary_key=True)
    fir_number = Column(String(100), unique=True, nullable=False)
    police_station_id = Column(String(50), ForeignKey("police_stations.station_id"), nullable=False)
    district = Column(String(100), nullable=False)
    crime_type = Column(String(100), nullable=False)
    date_filed = Column(String(50), nullable=False)
    date_of_occurrence = Column(String(50), nullable=False)
    time_of_occurrence = Column(String(50), nullable=False)
    location_description = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(50), nullable=False) # e.g. "open", "closed", "chargesheeted"
    modus_operandi = Column(String(500), nullable=False)
    case_description = Column(String(2000), nullable=False)

    # Relationships
    police_station = relationship("PoliceStation", back_populates="firs")
    accused_associations = relationship("FIRAccused", back_populates="fir", cascade="all, delete-orphan")
    victims = relationship("Victim", back_populates="fir", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="fir")


class Victim(Base):
    __tablename__ = "victims"
    
    victim_id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(50), nullable=False)
    address = Column(String(500), nullable=False)
    fir_id = Column(String(50), ForeignKey("firs.fir_id"), nullable=False)

    # Relationships
    fir = relationship("FIR", back_populates="victims")


class Vehicle(Base):
    __tablename__ = "vehicles"
    
    vehicle_id = Column(String(50), primary_key=True)
    registration_number = Column(String(50), nullable=False)
    type = Column(String(100), nullable=False)
    fir_id = Column(String(50), ForeignKey("firs.fir_id"), nullable=False)
    accused_id = Column(String(50), ForeignKey("accused.accused_id"), nullable=True)

    # Relationships
    fir = relationship("FIR", back_populates="vehicles")
    accused = relationship("Accused", back_populates="vehicles")


class Phone(Base):
    __tablename__ = "phones"
    
    phone_id = Column(String(50), primary_key=True)
    number = Column(String(50), nullable=False)
    accused_id = Column(String(50), ForeignKey("accused.accused_id"), nullable=False)

    # Relationships
    accused = relationship("Accused", back_populates="phones")


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    account_id = Column(String(50), primary_key=True)
    account_number_hash = Column(String(100), nullable=False)
    bank_name = Column(String(150), nullable=False)
    accused_id = Column(String(50), ForeignKey("accused.accused_id"), nullable=False)

    # Relationships
    accused = relationship("Accused", back_populates="bank_accounts")


def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
