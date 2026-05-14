from supabase import create_client
from faker import Faker
from dotenv import load_dotenv
import os
import random

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

fake = Faker()

models = [
    "DAIKIN-INV-1.5T-XP18",
    "LG-DUAL-INVERTER-1.5T",
    "VOLTAS-INV-183V",
    "SAMSUNG-WIND-FREE-1.5T",
    "BLUESTAR-INVERTER-IC318"
]

building_types = [
    "HOME",
    "OFFICE",
    "HOSPITAL",
    "SERVER_ROOM"
]

statuses = [
    "ACTIVE",
    "MAINTENANCE",
    "OFFLINE"
]

for _ in range(100):

    installation_date = fake.date_between(
        start_date='-3y',
        end_date='-1y'
    )

    last_service_date = fake.date_between(
        start_date='-6m',
        end_date='today'
    )

    data = {

        "model_number": random.choice(models),

        "tonnage": random.choice([
            1.0,
            1.5,
            2.0
        ]),

        "installation_date": str(
            installation_date
        ),

        "last_service_date": str(
            last_service_date
        ),

        "priority_level": random.choice([
            "LOW",
            "NORMAL",
            "HIGH",
            "CRITICAL"
        ]),

        "building_type": random.choice(
            building_types
        ),

        "current_status": random.choice(
            statuses
        )
    }

    supabase.table("devices").insert(
        data
    ).execute()

print("100 Inverter Split AC Devices Inserted")