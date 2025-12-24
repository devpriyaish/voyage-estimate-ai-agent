import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.chat_state import ChatState
from nodes.voyage_estimate import cargo_block

def test_cargo_only():
    state: ChatState = {
        "messages": [],
        "cargo_quantity": 40000,
        "freight_rate": None,
        "load_port": None,
        "discharge_port": None,
        "hire_rate": None,
        "vessel_name": None,
        "dwt": None,
        "vessel_type": None,
        "vessel_particulars": None
    }

    result = cargo_block(state)

    assert "dwt" in result
    assert isinstance(result["dwt"], float)
    assert result["dwt"] == 44000.0


def test_direct_dwt():
    state: ChatState = {
        "messages": [],
        "cargo_quantity": None,
        "freight_rate": None,
        "load_port": None,
        "discharge_port": None,
        "hire_rate": None,
        "vessel_name": None,
        "dwt": "60000",
        "vessel_type": None,
        "vessel_particulars": None
    }

    result = cargo_block(state)

    assert result["dwt"] == 60000.0


def test_empty_input():
    state: ChatState = {
        "messages": [],
        "cargo_quantity": None,
        "freight_rate": None,
        "load_port": None,
        "discharge_port": None,
        "hire_rate": None,
        "vessel_name": None,
        "dwt": None,
        "vessel_type": None,
        "vessel_particulars": None
    }

    result = cargo_block(state)

    assert "messages" in result
    assert len(result["messages"]) == 1

