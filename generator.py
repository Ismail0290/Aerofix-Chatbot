from supabase import create_client
from dotenv import load_dotenv
import os
import random
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def generate_log(device, scenario="healthy"):

    building_type = device["building_type"]

    # Base inverter AC behavior
    data = {
        "device_id": device["id"],

        "compressor_frequency": random.randint(30, 60),

        "power_consumption": round(
            random.uniform(1100, 1600), 2
        ),

        "ambient_temp": round(
            random.uniform(32, 40), 2
        ),

        "evaporator_temp": round(
            random.uniform(8, 14), 2
        ),

        "error_code": "NONE",

        "refrigerant_pressure": round(
            random.uniform(110, 130), 2
        )
    }

    # -----------------------------
    # GAS LEAK
    # -----------------------------
    if scenario == "gas_leak":

        data["refrigerant_pressure"] = round(
            random.uniform(40, 60), 2
        )

        data["evaporator_temp"] = round(
            random.uniform(20, 26), 2
        )

        data["error_code"] = "E1"

    # -----------------------------
    # COMPRESSOR OVERHEAT
    # -----------------------------
    elif scenario == "compressor_overheat":

        data["compressor_frequency"] = random.randint(
            80, 95
        )

        data["power_consumption"] = round(
            random.uniform(2200, 3000), 2
        )

        data["error_code"] = "P4"

    # -----------------------------
    # SENSOR FAILURE
    # -----------------------------
    elif scenario == "sensor_fault":

        data["ambient_temp"] = -5

        data["error_code"] = "E6"

    # -----------------------------
    # MOTOR JAM
    # -----------------------------
    elif scenario == "motor_jam":

        data["compressor_frequency"] = 0

        data["power_consumption"] = round(
            random.uniform(2000, 2600), 2
        )

        data["error_code"] = "F9"

    # -----------------------------
    # SERVER ROOM STRESS SIMULATION
    # -----------------------------
    if building_type == "SERVER_ROOM":

        data["ambient_temp"] += 3

        data["power_consumption"] += 200

    return data


while True:

    # Fetch latest devices every cycle
    devices = supabase.table(
        "devices"
    ).select("*").execute().data

    for device in devices:

        # Skip offline devices
        if device["current_status"] == "OFFLINE":
            continue

        # Weighted probability
        scenario = random.choice([
            "healthy",
            "healthy",
            "healthy",
            "healthy",
            "gas_leak",
            "compressor_overheat",
            "sensor_fault",
            "motor_jam"
        ])

        log = generate_log(device, scenario)

        supabase.table(
            "iot_logs"
        ).insert(log).execute()

        print(
            f"[{device['building_type']}] "
            f"{device['model_number']} | "
            f"{scenario.upper()} | "
            f"{log['error_code']}"
        )

    print("Sleeping for 10 seconds...\n")

    time.sleep(10)