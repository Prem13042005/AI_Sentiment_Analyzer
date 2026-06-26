import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv

# Load custom styling components
from components.ui import load_css, set_page_config, render_sidebar, metric_card, header_section, render_footer

load_dotenv()

# Setup API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

set_page_config("Home")
load_css()
render_sidebar()

header_section(
    "Sentiment Intelligence Platform", 
    "Enterprise NLP analytics dashboard for multi-model sentiment intelligence at scale."
)

# Shared function to get data from API with mock fallback
def fetch_analytics():
    try:
        response = requests.get(f"{API_URL}/analytics", timeout=2)
        if response.status_code == 200:
            return response.json(), False
    except Exception:
        pass
        
    # Return mock data as fallback
    mock_data = {
        "total_count": 1500,
        "positive_percentage": 68.5,
        "negative_percentage": 31.5,
        "sentiment_distribution": {"Positive": 1028, "Negative": 472},
        "confidence_distribution": {
            "0.5-0.6": 120, "0.6-0.7": 230, "0.7-0.8": 340, "0.8-0.9": 410, "0.9-1.0": 400
        },
        "sentiment_trends": [
            {"date": "2026-06-17", "Positive": 120, "Negative": 50},
            {"date": "2026-06-18", "Positive": 140, "Negative": 60},
            {"date": "2026-06-19", "Positive": 150, "Negative": 70},
            {"date": "2026-06-20", "Positive": 130, "Negative": 55},
            {"date": "2026-06-21", "Positive": 165, "Negative": 80},
            {"date": "2026-06-22", "Positive": 175, "Negative": 85},
            {"date": "2026-06-23", "Positive": 148, "Negative": 72}
        ],
        "top_positive_words": [
            {"word": "amazing", "count": 280},
            {"word": "love", "count": 240},
            {"word": "excellent", "count": 190},
            {"word": "great", "count": 170},
            {"word": "perfect", "count": 150},
            {"word": "easy", "count": 140},
            {"word": "fast", "count": 120}
        ],
        "top_negative_words": [
            {"word": "terrible", "count": 95},
            {"word": "crashes", "count": 88},
            {"word": "waste", "count": 85},
            {"word": "slow", "count": 76},
            {"word": "bloated", "count": 54},
            {"word": "buggy", "count": 48},
            {"word": "failed", "count": 42}
        ],
        "model_average_latencies": {
            "BiLSTM": 12.4,
            "GRU Attention": 17.8,
            "CNN-LSTM": 8.2,
            "DistilBERT": 44.5,
            "Ensemble": 82.1
        }
    }
    return mock_data, True

# Load analytics
data, is_mock = fetch_analytics()

if is_mock:
    st.warning(f"⚠️ Unable to reach sentiment API gateway ({API_URL}). Showing local mock sandbox analytics.")
else:
    st.success("🟢 Connected to live Sentiment API backend server.")

# KPI Blocks
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Total Logs Analyzed", f"{data['total_count']:,}", color="violet")
with col2:
    metric_card("Positive Feedback", f"{data['positive_percentage']}%", delta="+2.4% vs last week", color="green")
with col3:
    metric_card("Negative Feedback", f"{data['negative_percentage']}%", delta="-1.1% vs last week", color="red")
with col4:
    metric_card("Avg Predict Latency", f"{data['model_average_latencies']['Ensemble']:.1f}ms", delta="FastAPI + GPU", color="blue")

st.markdown("---")

# Graphical Layout
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📈 Customer Sentiment Trend")
    trend_df = pd.DataFrame(data["sentiment_trends"])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend_df["date"], y=trend_df["Positive"],
        mode='lines+markers', name='Positive Feedback',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=trend_df["date"], y=trend_df["Negative"],
        mode='lines+markers', name='Negative Feedback',
        line=dict(color='#f43f5e', width=3),
        marker=dict(size=8)
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📊 Sentiment Share")
    dist_df = pd.DataFrame(
        list(data["sentiment_distribution"].items()), 
        columns=["Sentiment", "Count"]
    )
    fig_pie = px.pie(
        dist_df, values="Count", names="Sentiment",
        color="Sentiment",
        color_discrete_map={"Positive": "#10b981", "Negative": "#f43f5e"},
        hole=0.4
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6'),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

col_bottom_1, col_bottom_2 = st.columns(2)

with col_bottom_1:
    st.subheader("⚡ Model Prediction Speeds (ms)")
    latencies = data["model_average_latencies"]
    fig_lat = px.bar(
        x=list(latencies.values()), y=list(latencies.keys()),
        orientation='h',
        labels={'x': 'Latency (ms)', 'y': 'Model'},
        color=list(latencies.keys()),
        color_discrete_sequence=px.colors.sequential.Purples_r
    )
    fig_lat.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        yaxis=dict(gridcolor='rgba(0,0,0,0)'),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_lat, use_container_width=True)

with col_bottom_2:
    st.subheader("🎯 Model Confidence Distribution")
    conf_df = pd.DataFrame(list(data["confidence_distribution"].items()), columns=["Confidence Range", "Reviews Count"])
    fig_conf = px.bar(
        conf_df, x="Confidence Range", y="Reviews Count",
        color="Reviews Count",
        color_continuous_scale="Purples"
    )
    fig_conf.update_layout(
        coloraxis_showscale=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f3f4f6'),
        xaxis=dict(gridcolor='rgba(0,0,0,0)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_conf, use_container_width=True)

# Database seeding controls
if is_mock:
    st.info("💡 Running the API server allows you to test live predictions, run custom LIME word visualizers, and stream bulk files. Start the API backend by running `uvicorn backend.app.main:app --reload`.")
else:
    with st.expander("🛠️ Advanced Database Utilities"):
        st.write("Perform administration actions on the linked Postgres/SQLite databases.")
        if st.button("🔄 Populate Database with Historical Seed Data"):
            try:
                res = requests.post(f"{API_URL}/analytics/seed")
                if res.status_code == 200:
                    st.success("Successfully seeded 120 prediction log logs. Refresh page to update metrics!")
                    st.rerun()
                else:
                    st.error("Failed to execute database seeding.")
            except Exception as e:
                st.error(f"Error calling seeding endpoint: {e}")

render_footer()
