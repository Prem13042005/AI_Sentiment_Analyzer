import os
import streamlit as st
import pandas as pd

# Page configurations
st.set_page_config(page_title="About — SIP", page_icon="ℹ️")

# Inject style.css
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.title("About Sentiment Intelligence Platform")
st.markdown("""
SIP is an enterprise-grade NLP analytics platform built for real-time sentiment classification of customer reviews, feedback forms, and user-generated text.
""")

st.subheader("Architecture")
st.code("""
┌─────────────────────────────┐
│    Streamlit Frontend        │
│  8 pages · JWT auth state   │
└──────────┬──────────────────┘
           │ HTTP + Bearer token
           ▼
┌─────────────────────────────┐
│    FastAPI REST API          │
│  /auth /predict /history    │
└──┬───────────┬──────────────┘
   │           │
   ▼           ▼
┌──────┐   ┌──────────────────┐
│  DB  │   │   ML Models      │
│ PG / │   │ BiLSTM · GRU     │
│SQLite│   │ CNN-LSTM         │
└──────┘   │ DistilBERT       │
           │ Ensemble         │
           └──────────────────┘
""", language=None)

st.subheader("Model Architectures Comparison")
about_model_data = {
    "Name": ["DistilBERT", "Ensemble", "BiLSTM", "GRU+Attention", "CNN-LSTM"],
    "Architecture": ["Transformer 66M", "Weighted voting", "Embedding→BiLSTM(128)", "Embedding→GRU(128)", "Conv1D→MaxPool→LSTM"],
    "Dataset": ["SST-2", "SST-2", "SST-2", "SST-2", "SST-2"],
    "Accuracy": ["91.4%", "92.1%", "85.2%", "83.7%", "81.9%"],
    "F1": ["91.2%", "91.9%", "84.9%", "83.4%", "81.5%"],
    "Speed": ["48ms", "78ms", "12ms", "10ms", "8ms"]
}
df_models = pd.DataFrame(about_model_data)
st.dataframe(df_models, hide_index=True, use_container_width=True)

st.subheader("Technology Stack")
col_t1, col_t2, col_t3, col_t4 = st.columns(4)
with col_t1:
    st.markdown("""
    **Core Backend**
    - FastAPI
    - Hugging Face
    """)
with col_t2:
    st.markdown("""
    **Visual Front**
    - Streamlit
    - Docker
    """)
with col_t3:
    st.markdown("""
    **ML / DL Engine**
    - TensorFlow
    - PostgreSQL
    """)
with col_t4:
    st.markdown("""
    **Ops & Tracking**
    - PyTorch
    - MLflow
    """)

st.markdown("<br>", unsafe_allow_html=True)
st.link_button("View on GitHub", "https://github.com/Prem13042005/AI_Sentiment_Analyzer")
