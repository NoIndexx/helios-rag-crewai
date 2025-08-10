import json
import os
import httpx
import sys
from pathlib import Path
import io
from contextlib import redirect_stdout
from dotenv import load_dotenv
import streamlit as st

# Resolve API base without requiring secrets; fall back to env var then default
load_dotenv()
try:
    API_BASE = st.secrets["api_base"]
except Exception:
    API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="Helios Climate Risk", layout="wide")

# Ensure project root is on sys.path so `import app.*` works when running Streamlit from subdir
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.title("🌍 Helios Climate Risk")
st.caption("Powered by CrewAI • Climate risk analysis platform for commodity crops")

def post(endpoint: str, payload: dict):
    url = f"{API_BASE}{endpoint}"
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(url, json=payload)
            if r.status_code != 200:
                # Log to terminal/console, not Streamlit
                print(f"API Error {r.status_code}: {r.text}")
                return {"error": f"API returned {r.status_code}", "details": r.text}
            response_data = r.json()
            return response_data
    except Exception as e:
        # Log to terminal/console, not Streamlit
        print(f"Request failed: {str(e)}")
        return {"error": "Request failed", "details": str(e)}

# Create tabs for the original design
tab_chat, tab_queries = st.tabs(["🤖 Chatbot", "🔧 API Tests"])

with tab_chat:
    st.subheader("Climate Risk Chatbot")
    st.caption("Ask questions in natural language about climate risk data")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "source" in message and message["source"]:
                with st.expander("📊 Data Source"):
                    st.json(message["source"])

    # Accept user input
    if prompt := st.chat_input("Ask about climate risks... (e.g., 'What country has the highest current climate risk for Cocoa beans?')"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Analyzing climate data..."):
                try:
                    from app.crew.run_agent import kickoff_example
                    
                    # Capture logs
                    stdout_buf = io.StringIO()
                    with redirect_stdout(stdout_buf):
                        result = kickoff_example(prompt)
                    
                    # Display the answer
                    response = result.answer
                    st.markdown(response)
                    
                    # Show data source if available
                    if hasattr(result, 'source') and result.source:
                        with st.expander("📊 Data Source"):
                            st.json(result.source)
                    
                    # Show logs if needed (optional)
                    logs = stdout_buf.getvalue()
                    if logs:
                        with st.expander("🔧 Processing Logs"):
                            st.code(logs)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "source": getattr(result, 'source', None)
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

    # Sidebar with example questions
    with st.sidebar:
        st.header("💡 Example Questions")
        example_questions = [
            "What country has the highest current climate risk for Cocoa beans?",
            "How does Brazil's 2025 climate risk compare to its historical average for Cocoa beans?",
            "What year was most similar to this season for Oil palm fruit?",
            "What's the global average climate risk for Cocoa beans in January 2025?",
            "What are the top 3 countries with the lowest historical risk for Cocoa beans?",
            "What's the trend in maximum climate risk for Cocoa beans from 2016 to 2025?",
            "Did Brazil's risk increase or decrease from the previous growing season for Cocoa beans?",
            "What is the current yield rating for Oil palm fruit and how does it relate to risk?",
            "Which regions are showing a spike in upcoming seasonal risk for Rice?",
            "How does the EU's risk for Wheat in 2026 compare with 2025?"
        ]
        
        for i, question in enumerate(example_questions):
            if st.button(f"📝 {question}", key=f"example_{i}"):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
        
        st.divider()
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

with tab_queries:
    st.subheader("API Endpoint Testing")
    st.caption("Directly test individual API endpoints for validation and debugging")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("1. Highest current risk"):
            st.caption("Based on real data: Cote d'Ivoire has highest risk for Cocoa beans (WAPR: 74.2)")
            commodity = st.text_input("Commodity (optional)", value="Cocoa beans", key="q1_commodity")
            if st.button("Query", key="q1_btn"):
                res = post("/api/v1/query/highest-current-risk", {"commodity": commodity or None})
                st.json(res)

        with st.expander("2. Compare country year vs hist"):
            st.caption("Example: Brazil 2025 vs historical average for Cocoa beans (16.9% above)")
            c_commodity = st.text_input("Commodity", value="Cocoa beans", key="q2_commodity")
            c_country = st.text_input("Country code", value="BR", key="q2_country")
            c_year = st.number_input("Year", value=2025, key="q2_year")
            if st.button("Query", key="q2_btn"):
                res = post("/api/v1/query/compare-country-year-vs-hist", 
                          {"commodity": c_commodity, "country_code": c_country, "year": int(c_year)})
                st.json(res)

        with st.expander("3. Most similar year"):
            st.caption("Example: Oil palm fruit globally (similar to 2021)")
            s_commodity = st.text_input("Commodity", value="Oil palm fruit", key="q3_commodity")
            s_scope = st.selectbox("Scope", ["global", "country"], index=0, key="q3_scope")
            s_country = st.text_input("Country code (if country)", value="GLB", key="q3_country")
            if st.button("Query", key="q3_btn"):
                res = post("/api/v1/query/most-similar-year", 
                          {"commodity": s_commodity, "scope": s_scope, "country_code": s_country or None})
                st.json(res)

        with st.expander("4. Global avg for month"):
            st.caption("Example: Cocoa beans global average for January 2025")
            g_commodity = st.text_input("Commodity", value="Cocoa beans", key="q4_commodity")
            g_year = st.number_input("Year", value=2025, key="q4_year")
            g_month = st.number_input("Month", value=1, min_value=1, max_value=12, key="q4_month")
            if st.button("Query", key="q4_btn"):
                res = post("/api/v1/query/global-avg-for-month", 
                          {"commodity": g_commodity, "year": int(g_year), "month": int(g_month)})
                st.json(res)

        with st.expander("5. Top-K lowest hist risk"):
            st.caption("Example: Top 3 countries with lowest risk for Rice")
            t_commodity = st.text_input("Commodity", value="Rice", key="q5_commodity")
            t_k = st.number_input("K", value=3, min_value=1, max_value=10, key="q5_k")
            if st.button("Query", key="q5_btn"):
                res = post("/api/v1/query/top-k-lowest-hist-risk", 
                          {"commodity": t_commodity, "k": int(t_k)})
                st.json(res)

    with col2:
        with st.expander("6. Trend max risk"):
            st.caption("Example: Cocoa beans trend from 2016 to 2025")
            tr_commodity = st.text_input("Commodity", value="Cocoa beans", key="q6_commodity")
            tr_start = st.number_input("Start year", value=2016, key="q6_start")
            tr_end = st.number_input("End year", value=2025, key="q6_end")
            if st.button("Query", key="q6_btn"):
                res = post("/api/v1/query/trend-max-risk", 
                          {"commodity": tr_commodity, "start_year": int(tr_start), "end_year": int(tr_end)})
                st.json(res)

        with st.expander("7. Country season change"):
            st.caption("Example: Brazil's Cocoa beans seasonal changes")
            sc_commodity = st.text_input("Commodity", value="Cocoa beans", key="q7_commodity")
            sc_country = st.text_input("Country code", value="BR", key="q7_country")
            if st.button("Query", key="q7_btn"):
                res = post("/api/v1/query/country-season-change", 
                          {"commodity": sc_commodity, "country_code": sc_country})
                st.json(res)

        with st.expander("8. Yield and risk relation"):
            st.caption("Example: Oil palm fruit global yield (Good rating, 2.88 mt/ha)")
            yr_commodity = st.text_input("Commodity", value="Oil palm fruit", key="q8_commodity")
            yr_scope = st.selectbox("Scope", ["global", "country"], index=0, key="q8_scope")
            yr_country = st.text_input("Country code", value="GLB", key="q8_country")
            if st.button("Query", key="q8_btn"):
                res = post("/api/v1/query/yield-and-risk-relation", 
                          {"commodity": yr_commodity, "scope": yr_scope, "country_code": yr_country or None})
                st.json(res)

        with st.expander("9. Upcoming spike regions"):
            st.caption("Example: Rice in Indonesia (upcoming risk spike)")
            us_commodity = st.text_input("Commodity", value="Rice", key="q9_commodity")
            us_threshold = st.number_input("Threshold (diff)", value=-4.0, key="q9_threshold")
            if st.button("Query", key="q9_btn"):
                res = post("/api/v1/query/upcoming-spike-regions", 
                          {"commodity": us_commodity, "threshold": float(us_threshold)})
                st.json(res)

        with st.expander("10. EU risk comparison"):
            st.caption("Example: How does EU's risk for Wheat compare 2026 vs 2025")
            eu_commodity = st.text_input("Commodity", value="Wheat", key="q10_commodity")
            eu_current = st.number_input("Current year", value=2026, key="q10_current")
            eu_previous = st.number_input("Previous year", value=2025, key="q10_previous")
            if st.button("Query", key="q10_btn"):
                res = post("/api/v1/query/eu-risk-comparison", 
                          {"commodity": eu_commodity, "current_year": int(eu_current), "previous_year": int(eu_previous)})
                st.json(res)


