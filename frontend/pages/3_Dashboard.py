import os
import streamlit as st
import pandas as pd
from datetime import datetime

from frontend.utils.auth_state import require_auth, do_logout, get_client
from frontend.utils.charts import sentiment_bar_chart, activity_line_chart

# Page configuration and authentication check
st.set_page_config(page_title="Dashboard — SIP", page_icon="📊", layout="wide")
require_auth()

# Inject style.css
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Header Row
col_title, col_logout = st.columns([5, 1])
with col_title:
    st.title(f"Welcome back, {st.session_state.username}")
with col_logout:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Log out", type="secondary", use_container_width=True):
        do_logout()

st.divider()

# Load stats & history
try:
    client = get_client()
    stats = client.get_stats()
    history = client.get_history(limit=50)
except Exception as e:
    st.error(f"Failed to fetch dashboard data: {e}")
    st.stop()

# Metric Cards Row
total = stats.get("total_count", 0)
pos_count = stats.get("positive_count", 0)
neg_count = stats.get("negative_count", 0)
neut_count = stats.get("neutral_count", 0)

pos_pct = (pos_count / total * 100) if total > 0 else 0.0
neg_pct = (neg_count / total * 100) if total > 0 else 0.0

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total Analyses", f"{total:,}")
with col_m2:
    st.metric("Positive Sentiment", f"{pos_pct:.1f}%")
with col_m3:
    st.metric("Negative Sentiment", f"{neg_pct:.1f}%")
with col_m4:
    st.metric("Top Model Used", stats.get("most_used_model", "None").upper())

st.markdown("<br>", unsafe_allow_html=True)

# Charts section
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.subheader("Sentiment Distribution Summary")
    fig_bar = sentiment_bar_chart(
        positive=pos_count,
        negative=neg_count,
        neutral=neut_count
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_c2:
    st.subheader("Recent System Activity (Last 7 Days)")
    time_series = stats.get("analyses_last_7_days", [])
    dates = [item["date"] for item in time_series]
    counts = [item["count"] for item in time_series]
    fig_line = activity_line_chart(dates=dates, counts=counts)
    st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# Recent Analyses list
st.subheader("Recent Analyses")

if not history:
    st.info("No analyses yet. Go to the Analyzer to get started.")
    st.page_link("pages/4_Analyzer.py", label="Run single analysis →", icon="🔍")
else:
    df_history = pd.DataFrame(history)
    df_recent = df_history.head(10).copy()
    
    # Format fields
    df_recent["Confidence (%)"] = df_recent["confidence"].apply(lambda x: f"{x*100:.1f}%")
    df_recent["created_at"] = pd.to_datetime(df_recent["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
    
    df_recent = df_recent.rename(columns={
        "text_snippet": "Text Preview",
        "sentiment": "Sentiment Verdict",
        "model_used": "Model Architecture",
        "created_at": "Timestamp"
    })
    
    df_show = df_recent[["Text Preview", "Sentiment Verdict", "Confidence (%)", "Model Architecture", "Timestamp"]]
    
    # Render table
    st.data_editor(
        df_show,
        disabled=True,
        use_container_width=True,
        hide_index=True
    )
