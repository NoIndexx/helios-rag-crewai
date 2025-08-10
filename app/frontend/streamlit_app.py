import json
import os
import httpx
import sys
from pathlib import Path
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

    # Initialize chat session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None

    # Inject CSS for chat bubble alignment (user right, assistant left)
    st.markdown(
        """
        <style>
        .chat-bubble { padding: 0.6rem 0.8rem; border-radius: 12px; margin: 0.25rem 0; max-width: 90%; }
        .chat-user { background: #DCF8C6; color: #000; margin-left: auto; text-align: left; }
        .chat-assistant { background: #F1F0F0; color: #000; margin-right: auto; text-align: left; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Messages area (scrollable)
    messages_container = st.container()
    with messages_container:
        for message in st.session_state.messages:
            role = message.get("role", "assistant")
            content = message.get("content", "")
            source = message.get("source")
            query = message.get("query")

            if role == "user":
                # Icon at right, bubble aligned to the right within main column
                col_main, col_icon = st.columns([0.9, 0.1])
                with col_main:
                    st.markdown(f'<div class="chat-bubble chat-user">{content}</div>', unsafe_allow_html=True)
                    if source:
                        with st.expander("📊 Data Source"):
                            st.json(source)
                    if query:
                        with st.expander("🔎 Query"):
                            st.json(query)
                with col_icon:
                    st.markdown("🧑")
            else:
                # Icon at left, bubble on the left
                col_icon, col_main = st.columns([0.1, 0.9])
                with col_icon:
                    st.markdown("🤖")
                with col_main:
                    st.markdown(f'<div class="chat-bubble chat-assistant">{content}</div>', unsafe_allow_html=True)
                    if source:
                        with st.expander("📊 Data Source"):
                            st.json(source)
                    if query:
                        with st.expander("🔎 Query"):
                            st.json(query)

    # Determine prompt source: sidebar example or user typing
    pending = st.session_state.pending_prompt
    user_prompt = pending if pending else st.chat_input(
        "Ask about climate risk... (e.g., 'Which country has the highest current risk for Cocoa beans?')",
        key="chat_input"
    )

    # React to prompt
    if user_prompt:
        # Reset pending flag (if any)
        st.session_state.pending_prompt = None
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        # Call agent
        with st.spinner("Analyzing climate data... (see logs in terminal)"):
            try:
                from app.crew.run_agent import kickoff_example
                history = st.session_state.get("messages", [])
                result = kickoff_example(user_prompt, history=history)
                response = result.answer
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "source": getattr(result, 'source', None),
                    "query": getattr(result, 'query', None),
                })
            except Exception as e:
                error_msg = f"Sorry, an error occurred: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.rerun()

    # Sidebar with example questions
    with st.sidebar:
        st.header("💡 Example Questions")
        # Main example questions with expected answers
        example_questions = [
            {
                "question": "What country has the highest current climate risk?",
                "expected": "Pakistan (PK) with 48.8 WAPR for Rice (absolute highest across all commodities)"
            },
            {
                "question": "How does Brazil's 2025 climate risk compare to its 10-year average?",
                "expected": "Brazil: 16.6 WAPR vs 14.2 historical (+16.9% increase)"
            },
            {
                "question": "What year was most similar to this season in terms of climate risk?",
                "expected": "2018 was most similar to 2025 growing season (Low risk, 3 stars)"
            },
            {
                "question": "What's the global average climate risk forecast for September 2025?",
                "expected": "Global avg: 26.4 WAPR, Global max: 56.1 WAPR for Cocoa beans"
            },
            {
                "question": "How does the EU's risk today compare with last year?",
                "expected": "EU Wheat unchanged: 23.5 WAPR (2026 vs 2025, delta: 0.0, trend: unchanged)"
            },
            {
                "question": "What are the top 3 countries with the lowest historical risk?",
                "expected": "1. Peru (13.4), 2. Brazil (14.2), 3. Ecuador (14.8)"
            },
            {
                "question": "What's the trend in maximum climate risk from 2016 to 2025?",
                "expected": "Declining trend: 100.0 WAPR (2016) → 56.1 WAPR (2025)"
            },
            {
                "question": "Did India's risk increase or decrease from the previous growing season?",
                "expected": "India unchanged: 38.0 WAPR (overall avg, 2026 vs 2025, delta: 0.0)"
            },
            {
                "question": "What is the current yield rating and how does it relate to risk?",
                "expected": "Oil palm: 'Good' yield, 2.88 mt/ha, 16.5 WAPR"
            },
            {
                "question": "Which regions are showing a spike in upcoming seasonal risk?",
                "expected": "Bangladesh (+4.9 diff, 41.2 upcoming), Brazil (+3.5 diff)"
            }
        ]
        
        # Optional additional questions for testing
        optional_questions = [
            {
                "question": "What are the top 5 countries with highest climate risk for Rice?",
                "expected": "1. Pakistan (48.8), 2. US (45.4), 3. Myanmar (43.2)"
            },
            {
                "question": "How does Indonesia's climate risk for Oil palm fruit compare between 2024 and 2025?",
                "expected": "Only 2025 available: 11.5 WAPR vs 18.0 historical (-36.11%)"
            },
            {
                "question": "What is the global production volume for Soya beans and its risk category?",
                "expected": "Global yield: 2.74 mt/ha, Neutral rating, 27.4 WAPR"
            }
        ]
        
        # Initialize session state for showing expected answers
        if "show_expected" not in st.session_state:
            st.session_state.show_expected = {}
        
        for i, item in enumerate(example_questions, 1):
            question = item["question"]
            expected = item["expected"]
            key = f"example_{i}"
            
            if st.button(f"📝 **Q{i}:** {question}", key=key):
                # Queue prompt to be sent automatically
                st.session_state.pending_prompt = question
                st.session_state.show_expected[key] = True
                st.rerun()
            
            # Show expected answer if this question was clicked
            if st.session_state.show_expected.get(key, False):
                st.info(f"📋 **Expected Answer:** {expected}")
        
        st.divider()
        st.subheader("🔬 Optional Test Questions")
        for i, item in enumerate(optional_questions, 1):
            question = item["question"]
            expected = item["expected"]
            key = f"optional_{i}"
            
            if st.button(f"🧪 **T{i}:** {question}", key=key):
                # Queue prompt to be sent automatically
                st.session_state.pending_prompt = question
                st.session_state.show_expected[key] = True
                st.rerun()
            
            # Show expected answer if this question was clicked
            if st.session_state.show_expected.get(key, False):
                st.info(f"📋 **Expected Answer:** {expected}")
        
        st.divider()
        col_clear1, col_clear2 = st.columns(2)
        with col_clear1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        with col_clear2:
            if st.button("📋 Hide Answers", use_container_width=True):
                st.session_state.show_expected = {}
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

        with st.expander("5b. Top-K highest current risk (NEW)"):
            st.caption("Example: Top 5 countries with highest current risk for Rice")
            th_commodity = st.text_input("Commodity", value="Rice", key="q5b_commodity")
            th_k = st.number_input("K", value=5, min_value=1, max_value=10, key="q5b_k")
            if st.button("Query", key="q5b_btn"):
                res = post("/api/v1/query/top-k-highest-current-risk", 
                          {"commodity": th_commodity, "k": int(th_k)})
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


