from fastapi import APIRouter
from db import supabase

router = APIRouter()


@router.get("/logs/latest/{device_id}")
def get_latest_logs(device_id: str):

    response = (
        supabase.table("iot_logs")
        .select("*")
        .eq("device_id", device_id)
        .order("timestamp", desc=True)
        .limit(10)
        .execute()
    )

    return {
        "device_id": device_id,
        "logs": response.data
    }