import os
import streamlit as st
import pandas as pd
from frontend.utils.auth_state import init_session_state, is_logged_in, link_button

# Page configuration
st.set_page_config(
    page_title="SIP — Sentiment Intelligence Platform",
    page_icon="🧠",
    layout="wide"
)

# Load and inject custom CSS
current_dir = os.path.dirname(os.path.abspath(__file__))
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning("Warning: Custom style.css assets file not found.")

# Initialize session state
init_session_state()

# Navigation helper for logged-in operators
if is_logged_in():
    st.info(f"Authenticated as {st.session_state.username}")
    link_button("Go to Dashboard →", "pages/3_Dashboard.py", icon="📊")
    st.divider()

# Hero Section
st.markdown("""
<div style="padding: 20px 0 40px 0;">
    <h1 class="hero-title">Sentiment Intelligence Platform</h1>
    <p class="hero-sub">Enterprise-grade NLP analytics powered by BiLSTM, GRU, CNN-LSTM, and DistilBERT</p>
</div>
""", unsafe_allow_html=True)

# Call to Action Links
col_cta1, col_cta2, _ = st.columns([1.5, 1.5, 7])
with col_cta1:
    link_button("Get started", "pages/1_Login.py", icon="🔐")
with col_cta2:
    link_button("Try demo", "pages/4_Analyzer.py", icon="🔍")

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

# Feature Cards Row
st.subheader("Platform Capabilities")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("""
    <div class="feature-card">
        <h4 style="color:#6366f1; margin-top:0;">⚡ Real-time Analysis</h4>
        <p style="color:#4b5563; font-size:0.95rem; line-height:1.5;">
            Analyze any customer feedback or review in milliseconds using 5 state-of-the-art model architectures.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
    <div class="feature-card">
        <h4 style="color:#6366f1; margin-top:0;">🕵️ Explainable AI</h4>
        <p style="color:#4b5563; font-size:0.95rem; line-height:1.5;">
            Leverage local word-level attributions via LIME and recurrent sequence attention heatmaps to trace model outputs.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
    <div class="feature-card">
        <h4 style="color:#6366f1; margin-top:0;">🧠 Multi-model Ensemble</h4>
        <p style="color:#4b5563; font-size:0.95rem; line-height:1.5;">
            Run predictions through a weighted consensus mechanism to maximize generalizability and prediction accuracy.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

# Performance Benchmark Table
st.subheader("Model Performance & Latency")
benchmark_data = {
    "Model": ["DistilBERT", "Ensemble", "BiLSTM", "GRU+Attention", "CNN-LSTM"],
    "Accuracy": ["91.4%", "92.1%", "85.2%", "83.7%", "81.9%"],
    "F1 Score": ["91.2%", "91.9%", "84.9%", "83.4%", "81.5%"],
    "Inference": ["48ms", "78ms", "12ms", "10ms", "8ms"]
}
df_bench = pd.DataFrame(benchmark_data)
st.dataframe(df_bench, hide_index=True, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()

# How it works section
st.subheader("How It Works")
col_step1, col_step2, col_step3 = st.columns(3)

with col_step1:
    st.markdown("""
    <div style="text-align: center; padding: 15px;">
        <h1 style="color: #6366f1; font-weight: 800; margin-bottom: 5px;">1</h1>
        <h5 style="margin-top:0; color:#111827;">Paste your text</h5>
        <p style="color:#6b7280; font-size:0.9rem;">Submit any review, feedback form, user comment, or text document.</p>
    </div>
    """, unsafe_allow_html=True)

with col_step2:
    st.markdown("""
    <div style="text-align: center; padding: 15px;">
        <h1 style="color: #6366f1; font-weight: 800; margin-bottom: 5px;">2</h1>
        <h5 style="margin-top:0; color:#111827;">Choose a model</h5>
        <p style="color:#6b7280; font-size:0.9rem;">Select one of our specialized deep learning architectures or the Ensemble consensus.</p>
    </div>
    """, unsafe_allow_html=True)

with col_step3:
    st.markdown("""
    <div style="text-align: center; padding: 15px;">
        <h1 style="color: #6366f1; font-weight: 800; margin-bottom: 5px;">3</h1>
        <h5 style="margin-top:0; color:#111827;">Get insights</h5>
        <p style="color:#6b7280; font-size:0.9rem;">Receive immediate sentiment verdicts, confidence ratings, and word highlights.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 20px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 0.85rem;">
    Built with FastAPI · Streamlit · TensorFlow · PyTorch · Docker
</div>
""", unsafe_allow_html=True)
