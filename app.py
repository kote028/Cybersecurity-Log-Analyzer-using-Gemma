import streamlit as st
import time
import os
import re
import pandas as pd
from gemma_log_analyzer import LogAnalyzer

# Set page configuration - must be first
st.set_page_config(
    page_title="Threat Intelligence Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for LLM-Stats Aesthetic
st.markdown("""
<style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
        font-family: 'Inter', 'Roboto', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="metric-container"] label {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Tables/Dataframes */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #334155;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }
    
    /* Badges */
    .badge-high { background-color: #EF4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
    .badge-medium { background-color: #F59E0B; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
    .badge-low { background-color: #10B981; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
    .badge-unknown { background-color: #64748B; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
    
    /* Glowing accents */
    .glow-text {
        color: #38BDF8;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }
</style>
""", unsafe_allow_html=True)

def parse_gemma_output(output_text, raw_log):
    """Parses the Gemma numbered list output into a structured dictionary."""
    parsed = {
        "Log": raw_log,
        "Risk": "Unknown",
        "Attack Type": "Unknown",
        "Summary": "N/A",
        "Actions": "N/A"
    }
    
    lines = output_text.split('\n')
    for line in lines:
        line = line.strip()
        if re.search(r'1\.\s*Summary:', line, re.IGNORECASE):
            parsed["Summary"] = line.split(':', 1)[1].strip()
        elif re.search(r'2\.\s*Risk\s*Level', line, re.IGNORECASE):
            risk = line.split(':', 1)[1].strip()
            if "high" in risk.lower(): parsed["Risk"] = "High"
            elif "medium" in risk.lower(): parsed["Risk"] = "Medium"
            elif "low" in risk.lower(): parsed["Risk"] = "Low"
        elif re.search(r'3\.\s*Attack\s*Type:', line, re.IGNORECASE):
            parsed["Attack Type"] = line.split(':', 1)[1].strip()
        elif re.search(r'4\.\s*Recommended\s*Actions?:', line, re.IGNORECASE):
            parsed["Actions"] = line.split(':', 1)[1].strip()
            
    return parsed

def get_risk_badge(risk):
    if risk == "High": return "<span class='badge-high'>High</span>"
    if risk == "Medium": return "<span class='badge-medium'>Medium</span>"
    if risk == "Low": return "<span class='badge-low'>Low</span>"
    return "<span class='badge-unknown'>Unknown</span>"

# Top Bar (Title and Token)
col_title, col_auth = st.columns([2, 1])
with col_title:
    st.markdown("<h1><span class='glow-text'>⚡ ThreatIntel</span> by Gemma</h1>", unsafe_allow_html=True)
    st.write("Live AI-powered cybersecurity log analysis leaderboard.")
with col_auth:
    hf_token = st.text_input("🔑 Hugging Face Token", type="password", help="Required for gated Gemma model access.", placeholder="hf_xxxxxxxxxxxxxxxxxxx")

st.markdown("<hr style='border-color: #334155; margin-top: 0px;'>", unsafe_allow_html=True)

# Navigation
tabs = st.tabs(["⏱️ Live Leaderboard", "📁 Bulk Analysis", "🔍 Manual Threat Check"])

# Settings Sidebar
st.sidebar.markdown("### ⚙️ Settings")
inference_mode = st.sidebar.radio(
    "Inference Engine", 
    ["Cloud API (Instant)", "Local Model (6GB Download)"],
    help="Cloud API runs instantly but requires internet. Local Model downloads 6GB to your machine but allows offline mode."
)

offline_mode = False
if inference_mode == "Local Model (6GB Download)":
    offline_mode = st.sidebar.checkbox("Run Offline ✈️", value=False, help="Enable this if you've already downloaded the model and have no internet.")

if offline_mode:
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
else:
    os.environ.pop("TRANSFORMERS_OFFLINE", None)
    os.environ.pop("HF_DATASETS_OFFLINE", None)

# Cache the model loading
@st.cache_resource(show_spinner=False)
def load_model(token, mode_string):
    if not token:
        st.warning("⚠️ Please enter your Hugging Face Token in the top right to initialize the AI.")
        st.stop()
        
    is_local = (mode_string == "Local Model (6GB Download)")
    
    with st.spinner("Initializing Gemma 2B Inference Engine... (Local mode may take 15 mins to download 6GB)"):
        return LogAnalyzer(token=token if token else None, local_mode=is_local)

# Only initialize if token is provided
if hf_token:
    analyzer = load_model(hf_token, inference_mode)

# --- TAB 1: REAL-TIME MONITORING (The Leaderboard) ---
with tabs[0]:
    col1, col2 = st.columns([1, 5])
    with col1:
        auto_refresh = st.checkbox("Auto-Refresh 🔄", value=False)
        if auto_refresh:
            st.empty().markdown("*Live polling active...*")
            
    log_file_path = "live_logs.txt"
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as f: f.write("")
        
    try:
        with open(log_file_path, "r") as f:
            lines = f.readlines()
    except: lines = []
    
    # Process latest logs
    display_count = min(10, len(lines))
    recent_logs = list(reversed(lines))[:display_count]
    
    # KPI Cards
    if hf_token and recent_logs:
        with st.spinner("Analyzing live feed..."):
            parsed_results = []
            high_risk_count = 0
            
            for log in recent_logs:
                if log.strip():
                    raw_out = analyzer.analyze_log(log.strip())
                    parsed = parse_gemma_output(raw_out, log.strip())
                    parsed_results.append(parsed)
                    if parsed["Risk"] == "High": high_risk_count += 1
            
            # Metrics Row
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Logs Monitored", len(lines))
            m2.metric("Recent Threats", len(parsed_results))
            m3.metric("High Risk", high_risk_count)
            m4.metric("Engine", "Gemma 2B")
            
            st.markdown("### 🚨 Threat Leaderboard")
            
            # Display as a styled HTML table for ultimate sleekness
            html_table = """
            <table style='width:100%; text-align:left; border-collapse: collapse;'>
                <tr style='background-color:#1E293B; color:#94A3B8; border-bottom:1px solid #334155;'>
                    <th style='padding:12px;'>Risk</th>
                    <th style='padding:12px;'>Attack Type</th>
                    <th style='padding:12px;'>Summary</th>
                    <th style='padding:12px;'>Raw Log</th>
                </tr>
            """
            for res in parsed_results:
                html_table += f"""
                <tr style='border-bottom:1px solid #1E293B; background-color:#0B0F19;'>
                    <td style='padding:12px;'>{get_risk_badge(res['Risk'])}</td>
                    <td style='padding:12px; font-weight:500; color:#F8FAFC;'>{res['Attack Type']}</td>
                    <td style='padding:12px; color:#CBD5E1; font-size:0.9em;'>{res['Summary']}</td>
                    <td style='padding:12px; color:#64748B; font-family:monospace; font-size:0.8em;'>{res['Log'][:50]}...</td>
                </tr>
                """
            html_table += "</table>"
            st.markdown(html_table, unsafe_allow_html=True)
            
    elif not hf_token:
        st.info("Waiting for API Token...")
    else:
        st.info("No logs found. Run `python log_generator.py` in your terminal to start the live feed!")

    if auto_refresh:
        time.sleep(5)
        st.rerun()

# --- TAB 2: BULK ANALYSIS ---
with tabs[1]:
    st.markdown("### 📁 Batch Log Processing")
    uploaded_file = st.file_uploader("Drop a .txt or .log file here", type=["txt", "log"])
    
    if uploaded_file and hf_token:
        logs = [log.strip().decode('utf-8') for log in uploaded_file.readlines() if log.strip()]
        st.write(f"Detected **{len(logs)}** log entries.")
        
        if st.button("🚀 Execute Bulk Analysis"):
            progress_bar = st.progress(0)
            parsed_results = []
            
            start_time = time.time()
            for i, log in enumerate(logs):
                raw_out = analyzer.analyze_log(log)
                parsed_results.append(parse_gemma_output(raw_out, log))
                progress_bar.progress((i + 1) / len(logs))
            duration = time.time() - start_time
            
            st.success(f"Analysis completed in {duration:.2f} seconds.")
            
            df = pd.DataFrame(parsed_results)
            st.dataframe(df, use_container_width=True, hide_index=True)

# --- TAB 3: MANUAL CHECK ---
with tabs[2]:
    st.markdown("### 🔍 Sandbox Analysis")
    log_input = st.text_area("Input Raw Log Data", height=150, placeholder="Failed login 5 times from 192.168.1.10...")
    
    if st.button("Analyze Threat", type="primary") and hf_token:
        if log_input.strip():
            with st.spinner("Processing through Gemma (This might take 10-30 seconds if Cloud API is waking up)..."):
                raw_out = analyzer.analyze_log(log_input)
                
                # If there's an error from the API, show it directly
                if "Error" in raw_out:
                    st.error(raw_out)
                else:
                    parsed = parse_gemma_output(raw_out, log_input)
                    
                    st.markdown(f"### {get_risk_badge(parsed['Risk'])} {parsed['Attack Type']}", unsafe_allow_html=True)
                    st.markdown(f"**Summary:** {parsed['Summary']}")
                    st.markdown(f"**Recommended Action:** {parsed['Actions']}")
                    
                    with st.expander("Raw Model Output"):
                        st.code(raw_out)
