import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nodes.voyage_estimate import cargo_block
from models.chat_state import ChatState
from langchain_core.messages import HumanMessage

# ✅ Simulated user input
state: ChatState = {
    "messages": [HumanMessage(content="I have 36000 MT cargo")],
    "cargo_quantity": 36000.0,
    "freight_rate": None,
    "load_port": None,
    "discharge_port": None,
    "hire_rate": None,
    "vessel_name": None,
    "dwt": None,
    "vessel_type": None,
    "vessel_particulars": None,
}

result = cargo_block(state)

print("\n===== RESULT =====\n")
print(result)
