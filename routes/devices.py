from fastapi import APIRouter
from db import supabase

router = APIRouter()


@router.get("/devices")
def list_devices():
    response = (
        supabase.table("devices")
        .select("*")
        .order("model_number")
        .execute()
    )

    return {"devices": response.data}
