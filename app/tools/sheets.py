"""Save a customer's booking into Google Sheets via SheetDB."""
from datetime import datetime
import requests
from langchain_core.tools import tool

# Put your SheetDB API endpoint here
SHEETDB_API = "https://sheetdb.io/api/v1/1jwvbhi2iyqpb2"

@tool
def save_booking(name: str, phone: str, service: str,
                 preferred_time: str, notes: str = "") -> str:
    """
    Save a customer's grooming booking to the salon's records.
    Call this ONLY after you have the customer's name, phone, the service,
    and their preferred date/time.

    Args:
        name: customer's full name
        phone: customer's phone number
        service: the grooming service requested
        preferred_time: preferred date and/or time
        notes: any extra details (breed, size, special requests)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = {
        "data": [{
            "Timestamp": timestamp,
            "Name": name,
            "Phone": phone,
            "Service": service,
            "PreferredTime": preferred_time,
            "Notes": notes
        }]
    }

    try:
        requests.post(SHEETDB_API, json=new_row)
        return f"Booking saved for {name} ({service}, {preferred_time})."
    except Exception as e:
        return f"Failed to save booking: {e}"
