from langchain_core.messages import AIMessage
from typing import Any, Dict

from models.chat_state import ChatState
from tools.voyage_estimate import calculate_dwt, get_vessel_particulars, get_vessels_by_name

def cargo_block(state: ChatState, config=None) -> Dict[str, Any]:
    """
    Implements:
    A -> B? -> C1 / C / D / E / F / G paths for cargo / DWT / vessel.
    Enforces cargo_quantity and dwt as float at runtime.
    """

    messages = state["messages"]

    # ✅ CASE 1 — Cargo Qty Present → Force Float → Calculate DWT → G Path
    if state.get("cargo_quantity") is not None:
        try:
            cargo_qty = float(state["cargo_quantity"])   # 🔒 HARD TYPE ENFORCEMENT
        except (ValueError, TypeError):
            return {
                "dead_reason": "Cargo quantity must be a numeric value in MT.",
                "messages": messages
            }

        dwt_result = calculate_dwt.invoke({
            "cargo_quantity": cargo_qty
        })

        if isinstance(dwt_result, dict) and "dwt" in dwt_result:
            try:
                dwt_val = float(dwt_result["dwt"])   # ✅ FORCE FLOAT
            except (ValueError, TypeError):
                return {
                    "dead_reason": "Calculated DWT is not a valid numeric value.",
                    "messages": messages
                }

            return {
                "messages": messages,
                "cargo_quantity": cargo_qty,   # ✅ normalized and stored
                "dwt": dwt_val                 # ✅ guaranteed float
            }

        return {
            "dead_reason": "DWT calculation failed due to invalid cargo quantity.",
            "messages": messages
        }

    # ✅ CASE 2 — DWT Already Present → Ensure Float → C → Yes → F
    if state.get("dwt") is not None:
        try:
            dwt_val = float(state["dwt"])   # ✅ ENSURE FLOAT EVEN IF COMING FROM ELSEWHERE
        except (ValueError, TypeError):
            return {
                "dead_reason": "Stored DWT value is not a valid numeric value.",
                "messages": messages
            }

        return {
            "messages": messages,
            "dwt": dwt_val
        }

    # ✅ CASE 3 — Vessel Name Present → D → E → F
    if state.get("vessel_name"):
        vessel_match = get_vessels_by_name.invoke({
            "vessel_name": state["vessel_name"]
        })

        if vessel_match.get("status") != "success":
            return {
                "dead_reason": vessel_match.get("message", "Unable to resolve vessel."),
                "messages": messages
            }

        if not vessel_match.get("mmsi"):
            return {
                "dead_reason": "Resolved vessel has no valid MMSI.",
                "messages": messages
            }

        vp = get_vessel_particulars.invoke({
            "mmsi": vessel_match.get("mmsi"),
            "imo": vessel_match.get("imo"),
            "ship_id": vessel_match.get("ship_id"),
            "vessel_name": state["vessel_name"]
        })

        if not vp:
            return {
                "dead_reason": "Vessel particulars API returned empty response.",
                "messages": messages
            }

        if "error" in vp:
            return {
                "dead_reason": vp.get("message", "Vessel particulars API error."),
                "messages": messages
            }

        if not isinstance(vp.get("data"), list) or len(vp["data"]) == 0:
            return {
                "dead_reason": "Vessel particulars API returned no usable data.",
                "messages": messages
            }


        vessel_data = vp["data"][0]
        dwt = vessel_data.get("FORMULA_DWT") or vessel_data.get("SUMMER_DWT")
        vessel_type = (
            str(vessel_data.get("VESSEL_TYPE"))
            if vessel_data.get("VESSEL_TYPE") is not None
            else None
        )
        vessel_type = str(vessel_type).strip().title() if vessel_type else None
        

        if not dwt:
            return {
                "dead_reason": "Unable to fetch vessel particulars (DWT) from API.",
                "messages": messages
            }

        update: Dict[str, Any] = {
            "messages": messages,
            "vessel_particulars": vessel_data,  # ✅ FULL OBJECT STORED HERE
            "dwt": dwt,
            "vessel_type": vessel_type
        }

        # ✅ Enforce FLOAT for DWT
        try:
            update["dwt"] = float(dwt)
        except (ValueError, TypeError):
            return {
                "dead_reason": "Fetched vessel DWT is not a valid numeric value.",
                "messages": messages
            }

        # ✅ THIS is what actually updates ChatState
        return update

    # ✅ CASE 4 — Nothing Provided → B → No → C1
    ask_msg = AIMessage(
        content=(
            "Please provide at least one of the following:\n"
            "- Cargo quantity in MT, or\n"
            "- Vessel DWT, or\n"
            "- Vessel name (so I can fetch particulars).\n\n"
            "Without one of these, I cannot proceed with the voyage estimate."
        )
    )

    return {"messages": messages + [ask_msg]}
