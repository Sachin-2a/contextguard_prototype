import streamlit as st
import pandas as pd
import sqlite3
import json
import sys
import os

# Add the backend folder to the Python path so Streamlit can use your backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from deterministic import detect_structured_ids
from ner import detect_entities
from llm_context import analyze_context
from policy import apply_policy
from vault import log_audit

st.set_page_config(page_title="ContextGuard Prototype", layout="wide")

st.title("🛡️ ContextGuard Gateway")
st.markdown("Privacy that understands intent, not just patterns.[cite: 5]")

# --- SIDEBAR: Context Envelope ---
st.sidebar.header("Context Envelope")
requester_role = st.sidebar.selectbox("Requester Role", ["Employee", "HR Manager", "IT Support", "Public User"])
data_source = st.sidebar.selectbox("Data Source", ["Private Email", "Public Team Channel", "Customer Database"])
destination = st.sidebar.selectbox("Destination", ["Internal LLM (Authorised)", "External AI API", "Public Dashboard"])
purpose = st.sidebar.selectbox("Purpose", ["Summarisation", "Drafting Reply", "Data Analysis"])

context = {
    "requester_role": requester_role,
    "data_source": data_source,
    "destination": destination,
    "purpose": purpose
}

# --- MAIN DASHBOARD ---
st.subheader("1. Request Input[cite: 4]")
input_text = st.text_area("Paste text intended for the AI tool:", height=100, 
                          value="Her salary is 18 LPA and her PAN is ABCDE1234F.")

if st.button("Process through ContextGuard"):
    with st.spinner("Analyzing context and applying policies..."):
        
        # 1. Detection Layers[cite: 4]
        hard_hits = detect_structured_ids(input_text)
        ner_hits = detect_entities(input_text)
        llm_analysis = analyze_context(input_text, context)
        
        all_findings = hard_hits + ner_hits + llm_analysis.get("findings", [])

        # 2. Policy Engine & Vault[cite: 4]
        final_text, actions_taken = apply_policy(input_text, all_findings, context)
        log_audit(input_text, final_text, actions_taken, context)

        # 3. Output Display
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("Safe Text Delivered to LLM[cite: 4]")
            st.code(final_text, language="markdown")
            
        with col2:
            st.warning("Contextual AI Reasoning[cite: 4]")
            st.write(f"**Sensitivity Category:** {llm_analysis.get('category', 'None')}")
            st.write(f"**Risk Level:** {llm_analysis.get('risk_level', 'None')}")
            st.info(f"**Reasoning:** {llm_analysis.get('reason', 'No reasoning provided.')}")
            
        st.subheader("Actions Taken[cite: 4]")
        st.table(actions_taken)

# --- AUDIT LOG ---
st.divider()
st.subheader("Audit Log & Counters[cite: 4]")

try:
    conn = sqlite3.connect('../backend/audit.db')
    df = pd.read_sql_query("SELECT id, original, secured, actions, context FROM audit_log ORDER BY id DESC LIMIT 10", conn)
    st.dataframe(df, use_container_width=True)
    
    total_processed = pd.read_sql_query("SELECT COUNT(*) as count FROM audit_log", conn).iloc[0]['count']
    st.metric(label="Total Gateway Requests Logged", value=total_processed)
    conn.close()
except Exception as e:
    st.info("Submit a request to generate the first audit log entry.")
