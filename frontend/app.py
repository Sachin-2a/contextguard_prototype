import streamlit as st
import pandas as pd
import sqlite3
import json
import sys
import os

# Add root directory to path to support absolute module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.deterministic import detect_structured_ids
from backend.ner import detect_entities
from backend.llm_context import analyze_context
from backend.policy import apply_policy
from backend.vault import log_audit, get_db_path

st.set_page_config(
    page_title="ContextGuard | Privacy Gateway", 
    page_icon="🛡️", 
    layout="wide"
)

# UI Stylesheet
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 20px; }
    .card { background-color: #F8FAFC; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🛡️ ContextGuard Gateway</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Privacy that understands intent, not just patterns. Protecting your AI workflows in real-time[cite: 4, 5].</p>', unsafe_allow_html=True)

# --- SIDEBAR: Context Envelope ---
st.sidebar.header("⚙️ Context Envelope")
requester_role = st.sidebar.selectbox("👤 Requester Role", ["Employee", "HR Manager", "IT Support", "Public User"])
data_source = st.sidebar.selectbox("📂 Data Source", ["Private Email", "Public Team Channel", "Customer Database"])
destination = st.sidebar.selectbox("🚀 Destination", ["Internal LLM (Authorised)", "External AI API", "Public Dashboard"])
purpose = st.sidebar.selectbox("🎯 Purpose", ["Summarisation", "Drafting Reply", "Data Analysis"])

context = {
    "requester_role": requester_role,
    "data_source": data_source,
    "destination": destination,
    "purpose": purpose
}

st.sidebar.divider()
st.sidebar.markdown("### 🎬 Quick Scenarios")
if st.sidebar.button("Load HR Scenario"):
    st.session_state["default_text"] = "Her salary is 18 LPA and her PAN is ABCDE1234F."
if st.sidebar.button("Load Health Scenario"):
    st.session_state["default_text"] = "The report on my sugar levels came back high at 240 mg/dL."

default_input = st.session_state.get("default_text", "Her salary is 18 LPA and her PAN is ABCDE1234F.")

# --- MAIN LAYOUT ---
col_input, col_flow = st.columns([1, 1], gap="medium")

with col_input:
    st.markdown("### ✍️ Input Prompt or Document")
    input_text = st.text_area("Paste text intended for the AI tool:", height=130, value=default_input)
    run_button = st.button("🚀 Process through ContextGuard", type="primary", use_container_width=True)

with col_flow:
    st.markdown("### 🔄 Active Privacy Pipeline")
    st.markdown("""
    <div class="card" style="font-size: 0.9rem;">
        <b>1. Context Envelope:</b> Metadata bound to request[cite: 4].<br>
        <b>2. Deterministic Layer:</b> Regex and checksum verification[cite: 4].<br>
        <b>3. NER Layer:</b> Presidio & spaCy scanning[cite: 4].<br>
        <b>4. Contextual LLM:</b> Gemini intent analysis[cite: 4].<br>
        <b>5. Policy Engine:</b> Rule enforcement & Token Vault[cite: 4].
    </div>
    """, unsafe_allow_html=True)

if run_button:
    with st.spinner("Analyzing context and evaluating security policies..."):
        hard_hits = detect_structured_ids(input_text)
        ner_hits = detect_entities(input_text)
        llm_analysis = analyze_context(input_text, context)
        
        all_findings = hard_hits + ner_hits + llm_analysis.get("findings", [])

        final_text, actions_taken = apply_policy(input_text, all_findings, context)
        log_audit(input_text, final_text, actions_taken, context)

        st.divider()
        st.markdown("### 📊 Security & Processing Results")
        
        res_col1, res_col2 = st.columns(2, gap="large")
        
        with res_col1:
            st.markdown("#### 🔒 Safe Payload Delivered to LLM[cite: 4]")
            st.code(final_text, language="markdown")
            
        with res_col2:
            st.markdown("#### 🧠 Contextual Intelligence")
            risk_level = llm_analysis.get('risk_level', 'None')
            if risk_level == "High":
                st.error(f"**Risk Level:** {risk_level} 🚨")
            elif risk_level == "Medium":
                st.warning(f"**Risk Level:** {risk_level} ⚠️")
            else:
                st.success(f"**Risk Level:** {risk_level} ✅")
                
            st.write(f"**Sensitivity Category:** `{llm_analysis.get('category', 'None')}`")
            st.info(f"**Reasoning:** {llm_analysis.get('reason', 'Standard policy applied.')}")

        st.markdown("#### 🛠️ Action Breakdown Matrix")
        if actions_taken:
            st.table(pd.DataFrame(actions_taken))
        else:
            st.success("No sensitive triggers found. Text allowed in full format.")

# --- AUDIT TRAIL ---
st.divider()
st.markdown("### 📈 Audit Log & System Counters[cite: 4]")

try:
    conn = sqlite3.connect(get_db_path())
    total_processed = pd.read_sql_query("SELECT COUNT(*) as count FROM audit_log", conn).iloc[0]['count']
    
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Total Gateway Requests Logged", value=total_processed)
    m2.metric(label="System Status", value="Operational 🟢")
    m3.metric(label="Active Layers", value="3 (Deterministic + NER + LLM)[cite: 4]")
    
    df = pd.read_sql_query("SELECT id, original, secured, actions, context FROM audit_log ORDER BY id DESC LIMIT 5", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
except Exception:
    st.info("💡 Submit your first prompt above to initialize the audit log database.")
