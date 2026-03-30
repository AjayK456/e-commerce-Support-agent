import streamlit as st
import json
import os
from agency import run_agency  # Ensure your 4-agent logic is in agency.py

st.set_page_config(page_title="E-Commerce Policy Auditor", layout="wide")

st.title("🛡️ AI Support Compliance & Policy Auditor")
st.markdown("Enter a natural language complaint and order metadata to generate a policy-backed response.")

# --- 5 PRE-DEFINED TEST CASES ---
test_scenarios = {
    "Case 1: Perishable Logic": {
        "text": "My order arrived late and the cookies are melted. I want a full refund and to keep the item.",
        "context": {
            "order_date": "2026-03-20", "delivery_date": "2026-03-25",
            "item_category": "perishable", "fulfillment_type": "first-party",
            "shipping_region": "US", "order_status": "delivered"
        }
    },
    "Case 2: High-Value Theft": {
        "text": "My $650 camera was stolen from my porch. Give me my money back now!",
        "context": {
            "order_date": "2026-03-22", "item_category": "electronics",
            "fulfillment_type": "first-party", "shipping_region": "US",
            "order_status": "delivered", "item_value": 650
        }
    },
    "Case 3: Regional Law (EU)": {
        "text": "I received this watch 10 days ago. I just don't like it. I want a full refund.",
        "context": {
            "order_date": "2026-03-10", "delivery_date": "2026-03-18",
            "item_category": "electronics", "fulfillment_type": "first-party",
            "shipping_region": "EU", "order_status": "delivered"
        }
    },
    "Case 4: Marketplace Hygiene": {
        "text": "I bought this swimsuit from a marketplace seller. It doesn't fit, I want to return it.",
        "context": {
            "item_category": "hygiene", "fulfillment_type": "marketplace",
            "shipping_region": "US", "order_status": "delivered"
        }
    },
    "Case 5: Ambiguous Request": {
        "text": "It doesn't work. Fix it.",
        "context": {
            "item_category": "appliances", "fulfillment_type": "first-party",
            "shipping_region": "US", "order_status": "delivered"
        }
    }
}

# --- UI LAYOUT ---
with st.sidebar:
    st.header("Test Scenarios")
    selected_name = st.selectbox("Load a scenario:", list(test_scenarios.keys()))
    scenario = test_scenarios[selected_name]

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Customer Ticket")
    ticket_text = st.text_area("Natural Language Input:", value=scenario["text"], height=150)
    
    st.subheader("Structured Context")
    context_text = st.text_area("Order JSON:", value=json.dumps(scenario["context"], indent=4), height=250)

with col2:
    st.subheader("Agent Output")
    if st.button("🚀 Process Ticket"):
        try:
            context_json = json.loads(context_text)
            with st.spinner("4 Agents are analyzing policy chunks..."):
                response = run_agency(ticket_text, context_json)
                st.markdown(response)
        except Exception as e:
            st.error(f"Error: {e}")