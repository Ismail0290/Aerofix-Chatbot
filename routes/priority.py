from fastapi import APIRouter
from db import supabase

router = APIRouter()


@router.get("/priority-tickets")
def priority_tickets():

    devices = (
        supabase.table("devices")
        .select("*")
        .execute()
    )

    result = []

    for device in devices.data:

        latest_log = (
            supabase.table("iot_logs")
            .select("*")
            .eq("device_id", device["id"])
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )

        if not latest_log.data:
            continue

        log = latest_log.data[0]

        severity = 0

        error = log["error_code"]

        # Error severity
        if error == "P4":
            severity += 90

        elif error == "E1":
            severity += 70

        elif error == "F9":
            severity += 80

        elif error == "E6":
            severity += 60

        # Building priority
        building = device["building_type"]

        if building == "SERVER_ROOM":
            severity += 50

        elif building == "HOSPITAL":
            severity += 40

        elif building == "OFFICE":
            severity += 20

        result.append({
            "device_id": device["id"],
            "model": device["model_number"],
            "building": building,
            "error_code": error,
            "priority_score": severity
        })

    result.sort(
        key=lambda x: x["priority_score"],
        reverse=True
    )

    return {
        "tickets": result
    }