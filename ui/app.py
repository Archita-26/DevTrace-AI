"""
DevTrace AI - Interactive Streamlit Dashboard.
Visual interface for autonomous bug localization, code repair,
and closed-loop verification.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.ast_parser import ASTParser
from core.orchestrator import DevTraceOrchestrator

# Streamlit Page Configuration
st.set_page_config(
    page_title="DevTrace AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-header">🔍 DevTrace AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Software Understanding, Bug Localization & Verification Assistant</div>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")

# Benchmark Discovery
benchmarks_dir = PROJECT_ROOT / "benchmarks"
available_repos = []
if benchmarks_dir.exists():
    for item in benchmarks_dir.iterdir():
        if item.is_dir() and not item.name.startswith("__"):
            available_repos.append(f"benchmarks/{item.name}")

if not available_repos:
    available_repos = ["benchmarks/calculator"]

selected_repo = st.sidebar.selectbox("Select Target Repository", available_repos)
max_retries = st.sidebar.slider("Max Self-Repair Attempts", min_value=1, max_value=3, value=2)

st.sidebar.divider()
st.sidebar.markdown("""
**Core Architecture:**
- 🌳 **Parser:** Python AST Module
- 🧪 **Verification:** Pytest Telemetry
- 🧠 **AI Intelligence:** Google Gemini API
- 🔄 **Pipeline:** Closed-Loop Feedback
""")

# Main Content Tabs
tab_repair, tab_scan = st.tabs(["🚀 Autonomous Repair Loop", "🔬 AST Code Explorer"])

# --- TAB 1: Autonomous Repair Loop ---
with tab_repair:
    st.markdown(f"### Target Repository: `{selected_repo}`")
    st.info("Click the button below to initiate closed-loop bug detection, patch generation, and real-time verification.")

    if st.button("🚀 Start Autonomous Repair Pipeline", type="primary", use_container_width=True):
        status_container = st.container()

        with st.spinner("Executing DevTrace AI closed-loop pipeline..."):
            orchestrator = DevTraceOrchestrator(selected_repo)
            result = orchestrator.run_repair_loop(max_retries=max_retries)

        if result.get("status") == "VERIFIED_SUCCESS":
            st.success("🎉 Autonomous Repair Verified Successfully! All tests now pass.")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Target Function", value=result.get("function_name", "N/A"))
            with col2:
                st.metric(label="Tests Passing", value=f"{result.get('passed_tests', 0)} Passed")
            with col3:
                st.metric(label="AI Attempts Needed", value=result.get("attempts", 1))

            st.divider()
            st.subheader("📝 Code Modification Diff")

            col_before, col_after = st.columns(2)
            with col_before:
                st.markdown("**❌ Original Faulty Code**")
                st.code(result.get("original_code", ""), language="python")

            with col_after:
                st.markdown("**✅ AI-Verified Fixed Code**")
                st.code(result.get("fixed_code", ""), language="python")

        elif result.get("status") == "SUCCESS":
            st.info(result.get("message", "All tests already pass. No fixes needed."))
        else:
            st.error(f"❌ Repair failed: {result.get('message', 'Unknown error')}")

# --- TAB 2: AST Code Explorer ---
with tab_scan:
    st.subheader("🔬 Structural Code Inspection (AST)")
    file_to_scan = st.text_input("Enter Python file relative path to scan:", value=f"{selected_repo}/calculator.py")

    if st.button("Scan File Structure"):
        target_path = PROJECT_ROOT / file_to_scan
        if target_path.exists():
            parser = ASTParser(str(target_path))
            scan_data = parser.parse()

            st.write(f"**Total Lines of Code:** {scan_data['total_lines']}")
            st.write(f"**Imports Detected:** `{', '.join(scan_data['imports']) if scan_data['imports'] else 'None'}`")

            st.markdown("#### Detected Functions & Line Boundaries:")
            for fn in scan_data["functions"]:
                with st.expander(f"def {fn['name']}({', '.join(fn['arguments'])}) — Lines {fn['start_line']} to {fn['end_line']}"):
                    st.code(fn["code_snippet"], language="python")
        else:
            st.error(f"File not found: {file_to_scan}")
