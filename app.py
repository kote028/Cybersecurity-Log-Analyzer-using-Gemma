import streamlit as st
import time
import os
from gemma_log_analyzer import LogAnalyzer

# Set page configuration
st.set_page_config(
    page_title="Gemma Log Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #4CAF50;
    }
    .stAlert {
        border-radius: 8px;
    }
    .log-box {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        border-left: 5px solid #4CAF50;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Cybersecurity Log Analyzer")
st.markdown("**Powered by Google Gemma (Lightweight LLM)**")
st.write("Analyze server logs, firewall events, and application traces to detect potential cybersecurity threats automatically.")

# Sidebar navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select Mode", ["Manual Analysis", "Bulk File Upload", "Real-Time Monitoring"])

st.sidebar.markdown("---")
st.sidebar.markdown("### Settings")
offline_mode = st.sidebar.checkbox("Run Offline ✈️", value=False, help="Enable this if you have already downloaded the model and have no internet connection. It prevents the app from checking for updates.")

if offline_mode:
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
else:
    # Remove if it was set
    os.environ.pop("TRANSFORMERS_OFFLINE", None)
    os.environ.pop("HF_DATASETS_OFFLINE", None)

hf_token = st.sidebar.text_input("Hugging Face Token (Required)", type="password", help="Gemma is a gated model. You need a token from huggingface.co to use it.")

# Cache the model loading so it doesn't reload on every interaction
@st.cache_resource(show_spinner=False)
def load_model(offline, token):
    # 'offline' parameter is just to trigger a reload if the toggle changes, though usually we don't need it.
    if not token and not offline:
        st.warning("⚠️ Please enter your Hugging Face Token in the sidebar. Gemma is a gated model and requires authentication.")
        st.stop()
        
    with st.spinner("Loading Gemma 2B Model... This may take a minute on first run."):
        analyzer = LogAnalyzer(token=token if token else None)
        return analyzer

analyzer = load_model(offline_mode, hf_token)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### About
This tool uses the `google/gemma-2b-it` model to analyze logs and extract:
- Summary of the event
- Risk Level
- Attack Type
- Recommended Actions
""")

if app_mode == "Manual Analysis":
    st.header("🔍 Manual Log Analysis")
    
    log_input = st.text_area("Paste a log entry here:", height=150, 
                             placeholder="Example: Failed login 5 times from 192.168.1.10 in 30 seconds.")
    
    if st.button("Analyze Log", type="primary"):
        if log_input.strip():
            with st.spinner("Analyzing with Gemma..."):
                start_time = time.time()
                result = analyzer.analyze_log(log_input)
                end_time = time.time()
                
            st.success(f"Analysis complete in {end_time - start_time:.2f} seconds!")
            
            st.markdown("### Analysis Result")
            # Display result nicely
            st.info(result)
        else:
            st.warning("Please enter a log to analyze.")

elif app_mode == "Bulk File Upload":
    st.header("📁 Bulk Log File Analysis")
    
    uploaded_file = st.file_uploader("Upload a text file containing logs (one per line)", type=["txt", "log"])
    
    if uploaded_file is not None:
        file_contents = uploaded_file.read().decode("utf-8")
        logs = [log.strip() for log in file_contents.split('\n') if log.strip()]
        
        st.write(f"Found {len(logs)} logs in the file.")
        
        if st.button("Analyze All Logs", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            for i, log in enumerate(logs):
                status_text.text(f"Analyzing log {i+1} of {len(logs)}...")
                res = analyzer.analyze_log(log)
                results.append({"log": log, "analysis": res})
                progress_bar.progress((i + 1) / len(logs))
                
            status_text.text("Analysis complete!")
            
            st.markdown("### Results")
            for item in results:
                with st.expander(f"Log: {item['log'][:50]}..."):
                    st.markdown(f"<div class='log-box'>{item['log']}</div>", unsafe_allow_html=True)
                    st.info(item['analysis'])

elif app_mode == "Real-Time Monitoring":
    st.header("⏱️ Real-Time Log Monitoring")
    st.write("Monitoring `live_logs.txt` for new entries...")
    
    log_file_path = "live_logs.txt"
    
    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as f:
            f.write("")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        auto_refresh = st.checkbox("Auto-Refresh", value=False)
    
    if auto_refresh:
        st_autorefresh = st.empty()
        st_autorefresh.markdown("*Auto-refreshing every 5 seconds...*")
    
    # Read the file
    try:
        with open(log_file_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        st.error(f"Error reading {log_file_path}: {e}")
        lines = []
    
    st.metric("Total Logs Captured", len(lines))
    
    # Analyze the last few logs to save time, or show all if short
    display_count = min(5, len(lines))
    if len(lines) > 0:
        st.subheader(f"Latest {display_count} Logs")
        
        # Reverse to show newest first
        recent_logs = list(reversed(lines))[:display_count]
        
        for i, log in enumerate(recent_logs):
            if log.strip():
                with st.container():
                    st.markdown(f"<div class='log-box'>{log.strip()}</div>", unsafe_allow_html=True)
                    # We might not want to run Gemma on every auto-refresh to save compute, 
                    # but for demonstration we'll show a button or run it if it's new.
                    with st.expander("Show AI Analysis"):
                        with st.spinner("Analyzing..."):
                            analysis = analyzer.analyze_log(log.strip())
                            st.write(analysis)
    else:
        st.info("No logs found in live_logs.txt. Run `python log_generator.py` in another terminal to start generating logs!")
        
    if auto_refresh:
        time.sleep(5)
        st.rerun()
