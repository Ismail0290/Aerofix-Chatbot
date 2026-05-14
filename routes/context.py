from fastapi import APIRouter
from db import supabase

router = APIRouter()


@router.get("/device/context/{device_id}")
def device_context(device_id: str):

    # Device info
    device = (
        supabase.table("devices")
        .select("*")
        .eq("id", device_id)
        .single()
        .execute()
    )

    # Latest log
    latest_log = (
        supabase.table("iot_logs")
        .select("*")
        .eq("device_id", device_id)
        .order("timestamp", desc=True)
        .limit(1)
        .execute()
    )

    # Maintenance history
    history = (
        supabase.table("maintenance_history")
        .select("*")
        .eq("device_id", device_id)
        .execute()
    )

    device_data = device.data

    log_data = latest_log.data[0] if latest_log.data else {}

    history_data = history.data

    context = f"""
    AC Model: {device_data['model_number']}

    Building Type: {device_data['building_type']}

    Current Status: {device_data['current_status']}

    Compressor Frequency:
    {log_data.get('compressor_frequency')}

    Power Consumption:
    {log_data.get('power_consumption')} W

    Error Code:
    {log_data.get('error_code')}

    Refrigerant Pressure:
    {log_data.get('refrigerant_pressure')} PSI

    Maintenance History:
    {history_data}
    """

    return {
        "device_id": device_id,
        "context": context
    }