import streamlit as st
import os
from dotenv import load_dotenv

# Shared UI components
from components.ui import load_css, set_page_config, render_sidebar, header_section, render_footer

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

set_page_config("API Documentation")
load_css()
render_sidebar()

header_section(
    "Developer API Gateway", 
    "Integrate real-time sentiment predictions and explainability reports directly into your external services."
)

st.markdown(f"""
<div style="background: rgba(18, 24, 41, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 20px; margin-bottom: 25px;">
    <p style="margin: 0; color: #9ca3af;"><strong>Base Gateway URL</strong>: <code>{API_URL}</code></p>
    <p style="margin: 10px 0 0 0; color: #9ca3af;">
        <strong>Interactive OpenAPI Specifications</strong>: 
        <a href="{API_URL}/docs" target="_blank" style="color: #a78bfa; font-weight:600; text-decoration: none;">Interactive Swagger UI &rarr;</a>
    </p>
</div>
""", unsafe_allow_html=True)

st.subheader("📡 Available Endpoints")

# Endpoint 1: POST /predict
with st.expander("🟢 POST /predict - Single Text Prediction", expanded=True):
    st.write("Executes model predictions on a single text sentence and logs history logs.")
    
    col_req, col_res = st.columns(2)
    with col_req:
        st.markdown("**Request Payload (JSON)**")
        st.code("""
{
  "text": "This application works perfectly!",
  "model_name": "ensemble"
}
        """, language="json")
        
    with col_res:
        st.markdown("**Response Body (JSON)**")
        st.code("""
{
  "text": "This application works perfectly!",
  "model_name": "ensemble",
  "sentiment": "Positive",
  "confidence": 0.985,
  "probabilities": {
    "positive": 0.985,
    "negative": 0.015
  },
  "execution_time_ms": 14.5
}
        """, language="json")

    # Code Snippets tab
    st.markdown("**Example Code Integration**")
    lang_tabs = st.tabs(["cURL", "Python (requests)"])
    with lang_tabs[0]:
        st.code(f"""
curl -X POST "{API_URL}/predict" \\
     -H "Content-Type: application/json" \\
     -d '{{"text": "This application works perfectly!", "model_name": "ensemble"}}'
        """, language="bash")
    with lang_tabs[1]:
        st.code(f"""
import requests

url = "{API_URL}/predict"
payload = {{
    "text": "This application works perfectly!",
    "model_name": "ensemble"
}}
response = requests.post(url, json=payload)
print(response.json())
        """, language="python")

st.markdown("<br>", unsafe_allow_html=True)

# Endpoint 2: POST /explain
with st.expander("🟢 POST /explain - Sentiment Explanation Details", expanded=False):
    st.write("Calculates LIME token attributions and GRU attention vectors.")
    
    col_req, col_res = st.columns(2)
    with col_req:
        st.markdown("**Request Payload (JSON)**")
        st.code("""
{
  "text": "The setup was slow, but the product is great.",
  "model_name": "gru-attention"
}
        """, language="json")
        
    with col_res:
        st.markdown("**Response Body (JSON)**")
        st.code("""
{
  "text": "The setup was slow, but the product is great.",
  "model_name": "gru-attention",
  "sentiment": "Positive",
  "confidence": 0.854,
  "lime_explanation": {
    "words": ["The", "setup", "was", "slow,", "but", "the", "product", "is", "great."],
    "positive_contributions": [{"word": "great", "weight": 0.32}],
    "negative_contributions": [{"word": "slow", "weight": 0.18}],
    "sequence_attributions": [...]
  },
  "attention_weights": [
    {"word": "product", "weight": 0.12},
    {"word": "great", "weight": 0.38},
    ...
  ]
}
        """, language="json")

    # Code Snippets tab
    st.markdown("**Example Code Integration**")
    lang_tabs = st.tabs(["cURL", "Python (requests)"])
    with lang_tabs[0]:
        st.code(f"""
curl -X POST "{API_URL}/explain" \\
     -H "Content-Type: application/json" \\
     -d '{{"text": "The setup was slow, but the product is great.", "model_name": "gru-attention"}}'
        """, language="bash")
    with lang_tabs[1]:
        st.code(f"""
import requests

url = "{API_URL}/explain"
payload = {{
    "text": "The setup was slow, but the product is great.",
    "model_name": "gru-attention"
}}
response = requests.post(url, json=payload)
data = response.json()
print("LIME weights:", data["lime_explanation"]["positive_contributions"])
        """, language="python")

st.markdown("<br>", unsafe_allow_html=True)

# Endpoint 3: GET /analytics
with st.expander("🔵 GET /analytics - Aggregated Business Metrics", expanded=False):
    st.write("Fetches overall count statistics, sentiment distribution counters, word cloud frequencies, and model average latency metrics.")
    
    st.markdown("**Response Body (JSON)**")
    st.code("""
{
  "total_count": 120,
  "positive_percentage": 65.4,
  "negative_percentage": 34.6,
  "sentiment_distribution": {"Positive": 80, "Negative": 40},
  "confidence_distribution": {"0.5-0.6": 10, "0.6-0.7": 20, ...},
  "sentiment_trends": [
    {"date": "2026-06-23", "Positive": 15, "Negative": 5}
  ],
  "top_positive_words": [{"word": "amazing", "count": 12}],
  "top_negative_words": [{"word": "slow", "count": 8}],
  "model_average_latencies": {"Ensemble": 82.5}
}
    """, language="json")

render_footer()
