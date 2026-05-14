from fastapi import APIRouter
from db import supabase

router = APIRouter()


@router.get("/analytics/failures")
def failure_analytics():

    logs = (
        supabase.table("iot_logs")
        .select("error_code")
        .neq("error_code", "NONE")
        .execute()
    )

    counts = {}

    for log in logs.data:

        code = log["error_code"]

        counts[code] = counts.get(code, 0) + 1

    return {
        "failure_counts": counts
    }