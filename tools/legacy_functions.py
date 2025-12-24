from json import tool
import re
from typing import Dict

import requests

from tools.voyage_estimate import OCEANN_JWT_TOKEN


@tool
def get_pnl_voyage_data(ae: str, pl: int = 1) -> dict:
    """
    Retrieves Time Charter Out Voyage (TCOV) data.
    """

    url = "https://devapiservices.theoceann.com/api/v1/tcov/edit"

    headers = {
        "Authorization": OCEANN_JWT_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "endpoint": "Chartering Dashboard",
        "Origin": "http://localhost:3000",
        "Referer": "http://localhost:3000/"
    }

    params = {
        "ae": ae,
        "pl": pl
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        return {
            "status": "error",
            "type": "http_error",
            "message": str(http_err),
            "url": url,
            "params": params
        }

    except requests.exceptions.ConnectionError as conn_err:
        return {
            "status": "error",
            "type": "connection_error",
            "message": "Failed to connect to P&L Voyage API (TCOV Edit).",
            "details": str(conn_err),
            "url": url,
            "params": params
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "type": "timeout",
            "message": "TCOV Edit API request timed out.",
            "url": url,
            "params": params
        }

    except Exception as e:
        return {
            "status": "error",
            "type": "unknown_error",
            "message": str(e),
            "url": url,
            "params": params
        }

@tool
def calculate_voyage_pnl(tce: float, voyage_days: int, voyage_cost: float) -> dict:
    """
    Calculates Net Revenue and Profit/Loss for a voyage.
    
    Formula:
    Net Revenue = TCE * Voyage Days
    Profit/Loss = Net Revenue - Voyage Cost
    """

    try:
        # Step 1 — Net Revenue
        net_revenue = tce * voyage_days

        # Step 2 — Profit or Loss
        pnl = net_revenue - voyage_cost

        status = "profit" if pnl >= 0 else "loss"

        return {
            "status": "success",
            "tce": tce,
            "voyage_days": voyage_days,
            "voyage_cost": voyage_cost,
            "net_revenue": net_revenue,
            "pnl": pnl,
            "pnl_status": status,
        }

    except Exception as e:
        return {
            "status": "error",
            "type": "calculation_error",
            "message": str(e),
            "inputs": {
                "tce": tce,
                "voyage_days": voyage_days,
                "voyage_cost": voyage_cost
            }
        }
    

@tool
def compute_voyage_days(route_distance: float, speed_and_consumption: str) -> Dict[str, float]:
    """
    Computes voyage days using route distance and extracted speeds.

    Example input string:
    "14. 0kts ( b ) / 13. 5kts ( l ) on 24. 0 mt ( b ) / 26. 0 mt ( l ) vlsfo eco ( wog ) : 12. 5kts ( b ) / 12. 0kts ( l ) on 18. 5 mt ( b ) / 20. 0 mt ( l ) vlsfo"

    Extracted:
        ballast_speed = 14.0
        laden_speed   = 13.5

    Formula:
        voyage_days = (route_distance / ballast_speed) + (route_distance / laden_speed)
    """
    print("===========", speed_and_consumption)

    if not route_distance or route_distance <= 0:
        raise ValueError("route_distance must be a positive number")

    if not speed_and_consumption or not isinstance(speed_and_consumption, str):
        raise ValueError("speed_and_consumption must be a valid string")

    # Normalize string by removing extra spaces like "14. 0" → "14.0"
    normalized = re.sub(r"(\d)\s+\.\s+(\d)", r"\1.\2", speed_and_consumption)

    # Extract FIRST ballast and laden speeds
    speed_pattern = r"(\d+\.?\d*)\s*kts\s*\(\s*b\s*\)\s*/\s*(\d+\.?\d*)\s*kts\s*\(\s*l\s*\)"
    match = re.search(speed_pattern, normalized, re.IGNORECASE)

    if not match:
        raise ValueError("Could not extract ballast & laden speeds from input string")

    ballast_speed = float(match.group(1))
    laden_speed = float(match.group(2))

    if ballast_speed <= 0 or laden_speed <= 0:
        raise ValueError("Extracted speeds must be positive numbers")

    voyage_days = (route_distance / ballast_speed) + (route_distance / laden_speed)

    return {
        "route_distance": round(route_distance, 2),
        "ballast_speed": ballast_speed,
        "laden_speed": laden_speed,
        "voyage_days": round(voyage_days, 2)
    }

@tool
def compute_bunker_consumption(voyage_days: float, speed_and_consumption: str) -> Dict[str, float]:
    """
    Computes bunker consumption using voyage days and extracted consumption values.

    Example input:
    "14. 0kts ( b ) / 13. 5kts ( l ) on 24. 0 mt ( b ) / 26. 0 mt ( l ) vlsfo eco ( wog )"

    Extracted:
        ballast_consumption = 24.0 mt/day
        laden_consumption   = 26.0 mt/day
        fuel_type           = "vlsfo"

    Formula:
        total_bunker = (voyage_days * ballast_consumption) +
                       (voyage_days * laden_consumption)
    """

    if not voyage_days or voyage_days <= 0:
        raise ValueError("voyage_days must be a positive number")

    if not speed_and_consumption or not isinstance(speed_and_consumption, str):
        raise ValueError("speed_and_consumption must be a valid string")

    # ✅ Normalize broken decimals: "24. 0" → "24.0"
    normalized = re.sub(r"(\d)\s+\.\s+(\d)", r"\1.\2", speed_and_consumption.lower())

    # ✅ Extract FIRST ballast & laden CONSUMPTION pair (mt/day)
    consumption_pattern = r"on\s*(\d+\.?\d*)\s*mt\s*\(.*?b.*?\)\s*/\s*(\d+\.?\d*)\s*mt\s*\(.*?l.*?\)"
    match = re.search(consumption_pattern, normalized, re.IGNORECASE)

    if not match:
        raise ValueError("Could not extract ballast & laden bunker consumption from input string")

    ballast_consumption = float(match.group(1))
    laden_consumption = float(match.group(2))

    if ballast_consumption <= 0 or laden_consumption <= 0:
        raise ValueError("Extracted consumption values must be positive")

    # ✅ Extract fuel type (vlsfo, lsfo, hsfo, mgo, lsmgo)
    fuel_match = re.search(r"(vlsfo|lsfo|hsfo|lsmgo|mgo)", normalized, re.IGNORECASE)
    fuel_type = fuel_match.group(1).upper() if fuel_match else "VLSFO"

    total_bunker = (voyage_days * ballast_consumption) + (voyage_days * laden_consumption)

    return {
        "voyage_days": round(voyage_days, 2),
        "ballast_consumption_mt_per_day": ballast_consumption,
        "laden_consumption_mt_per_day": laden_consumption,
        "total_bunker_mt": round(total_bunker, 2),
        "fuel_type": fuel_type
    }



@tool
def get_vessels_by_name(query: str) -> dict:
    """
    Fetch vessel list by vessel name or partial name with error handling.
    """
    url = f"https://prodapi.theoceann.ai/marine/get-vessels-name/{query}"

    headers = {
        "accept": "*/*",
        "authorization": OCEANN_JWT_TOKEN,
        "endpoint": "Map Intelligence",
    }

    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        return r.json()

    except requests.exceptions.HTTPError as http_err:
        return {
            "status": "error",
            "type": "http_error",
            "message": str(http_err),
            "url": url,
        }

    except requests.exceptions.ConnectionError as conn_err:
        return {
            "status": "error",
            "type": "connection_error",
            "message": "Failed to connect to TheOceann API",
            "details": str(conn_err),
            "url": url,
        }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "type": "timeout",
            "message": "Request to TheOceann API timed out",
            "url": url,
        }

    except Exception as e:
        return {
            "status": "error",
            "type": "unknown_error",
            "message": str(e),
            "url": url,
        }
