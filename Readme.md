# 🚢 Voyage Estimate AI Agent

## Overview

The **Voyage Estimate AI Agent** is an intelligent automation module designed to generate **end-to-end voyage estimates** from unstructured inputs such as chartering emails, cargo descriptions, or free-text voyage requirements.

The agent extracts key voyage parameters, integrates with voyage estimation logic, performs commercial and operational calculations, and presents structured results through a **Streamlit-based UI**.

---

## Key Objectives

- Automate voyage estimation from unstructured commercial inputs  
- Reduce manual data entry and human error  
- Accelerate chartering and commercial decision-making  
- Provide consistent, explainable, and auditable estimates  

---

## Core Capabilities

### 1. Input Understanding
- Chartering emails  
- Cargo offers / requirements  
- Free-text voyage descriptions  
- Structured API inputs (optional)

### 2. Intelligent Extraction
- Load & discharge ports  
- Cargo type and quantity  
- Laycan / date references  
- Voyage direction and constraints  

### 3. Voyage Estimation
- Distance & routing logic  
- Fuel consumption & bunker cost  
- Port & operational costs  
- Voyage duration  
- TCE and Voyage P&L  

### 4. Confidence & Validation
- Field-level confidence scoring  
- Overall estimate reliability score  
- Flags for assumptions or missing data  

---

## High-Level Architecture

```
User Input (Text / Email / UI)
↓
AI Extraction & Parsing
↓
Normalization & Validation
↓
Voyage Estimation Logic
↓
Cost & Performance Calculation
↓
Streamlit UI Output
```

---

## Output

The agent returns a structured voyage estimate including:
- Extracted voyage parameters  
- Cost breakdown (fuel, port, other costs)  
- Commercial metrics (TCE, P&L)  
- Confidence scores & assumptions  

---

## Use Cases

- Chartering desk quick evaluations  
- Pre-fixture voyage analysis  
- Broker email-to-estimate automation  
- Internal commercial decision support  
- What-if scenario simulations  

---

## 🛠️ How to Clone & Run the Project

### 1️⃣ Clone the Repository
```bash
git clone <REPOSITORY_URL>
cd voyage_estimation_ai_agent
```
Replace <REPOSITORY_URL> with your actual Git repository URL.
---

### 2️⃣ Create & Activate Virtual Environment (Recommended)

Windows
```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```
---

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
---

### 4️⃣ Configure Environment Variables (If Applicable)
Copy the example environment file:
```bash
cp example.env .env
```
Update the .env file with valid values:
```env
API_BASE_URL=<backend_api_url>
API_KEY=<api_key_if_required>
YOUR_KEY=<personalized_keys>
```
#### ⚠️ Important:
Do remember to replace the placeholder keys in example.env with your original / valid keys before running the application.
---

### 5️⃣ Run the Streamlit Application
Main UI:
```
streamlit run frontend.py
```
Alternative entry file:
```
streamlit run tend.py
```
---

### 6️⃣ Access the Application
After successful startup, you will see:
```ngnix
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.12:8501

* History restored
```

Open in browser:
Local: http://localhost:8501
Network (same LAN): http://192.168.1.12:8501
---

## 📂 Project Structure
```
voyage_estimation_ai_agent/
│
├── frontend.py        # Main Streamlit UI
├── tend.py            # Alternate / experimental UI
├── backend/           # Estimation logic & API integrations
├── utils/             # Helper utilities & validators
├── requirements.txt
├── .env               # Environment variables
└── README.md
```

## ⚠️ Common Issues
### Streamlit Not Found
```bash
pip install streamlit
```
### Port Already in Use
```
streamlit run frontend.py --server.port 8502
```
### Virtual Environment Not Active
Ensure (venv) is visible in your terminal before running Streamlit.
---

## Security & Access
- API-level authentication (if enabled)
- Input validation & sanitization
- No direct modification of master commercial data
---

## Limitations
- Outputs are indicative and require human validation
- Accuracy depends on input clarity and assumptions
- Market conditions must be updated periodically
---

## Disclaimer
This AI Agent is a **decision-support tool only**.
All voyage estimates should be reviewed and approved by qualified maritime professionals before commercial commitment

## Support
For configuration changes, enhancements, or issues, contact the internal product or engineering team.
