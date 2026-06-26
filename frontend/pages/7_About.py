import streamlit as st

# Shared UI components
from components.ui import load_css, set_page_config, render_sidebar, header_section, render_footer

set_page_config("About Project")
load_css()
render_sidebar()

header_section(
    "About Sentiment Intelligence Platform", 
    "Technical specifications, system architectures, explainability details, and project roadmap."
)

st.markdown("""
<div style="background: rgba(18, 24, 41, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 25px; margin-bottom: 30px;">
    <h3 style="margin-top: 0; color: #7c3aed;">Platform Objective</h3>
    <p style="font-size: 1.05rem; line-height: 1.6; color: #f3f4f6; margin-bottom: 0;">
        The Sentiment Intelligence Platform (SIP) is designed as a production-grade NLP analytics dashboard and REST API gateway. By integrating classical deep learning architectures (LSTMs, GRUs, CNNs) alongside state-of-the-art Transformer models (DistilBERT), SIP provides real-time predictions, bulk processing capacities, and granular explainability indicators that build user trust.
    </p>
</div>
""", unsafe_allow_html=True)

st.subheader("🤖 Supported Model Architectures")

# Tabbed detailed specs
spec_tabs = st.tabs(["BiLSTM", "GRU Attention", "CNN-LSTM", "DistilBERT", "Ensemble"])

with spec_tabs[0]:
    st.markdown("""
    #### Bidirectional LSTM (Long Short-Term Memory)
    Excellent at capturing long-term dependencies in sequential text in both forward and backward passes.
    - **Layers**: 
      1. *Embedding* Layer (Vocab: 10,000, Dim: 128)
      2. *Bidirectional LSTM* (128 units, dropout=0.2)
      3. *Dropout* Layer (0.3)
      4. *Dense* Hidden Layer (64 units, ReLU)
      5. *Dense* Output Layer (1 unit, Sigmoid)
    - **Use Case**: General-purpose sequence classification and review evaluation.
    """)

with spec_tabs[1]:
    st.markdown("""
    #### GRU (Gated Recurrent Unit) with custom Attention Layer
    Combines the computational efficiency of GRUs with an alignment attention layer that extracts word importance.
    - **Layers**:
      1. *Embedding* Layer (Vocab: 10,000, Dim: 128)
      2. *GRU* Sequence Layer (128 units, returning sequences)
      3. *Attention Layer* (Calculates $\\text{softmax}(\\tanh(X \\cdot W))$ attention weights)
      4. *Dense* Hidden Layer (64 units, ReLU)
      5. *Dense* Output Layer (1 unit, Sigmoid)
    - **Use Case**: Review classification with dynamic attention heatmap visualization.
    """)

with spec_tabs[2]:
    st.markdown("""
    #### CNN-LSTM (Convolutional + Long Short-Term Memory)
    Uses 1D Convolutions to extract local n-gram features combined with an LSTM layer for temporal sequence mapping.
    - **Layers**:
      1. *Embedding* Layer (Vocab: 10,000, Dim: 128)
      2. *Conv1D* Conv Layer (64 filters, kernel size=5, padding=same, ReLU)
      3. *MaxPooling1D* Pooling Layer (pool size=4)
      4. *LSTM* Recurrent Layer (128 units)
      5. *Dense* Hidden Layer (64 units, ReLU)
      6. *Dense* Output Layer (1 unit, Sigmoid)
    - **Use Case**: Fast inference on longer review documents.
    """)

with spec_tabs[3]:
    st.markdown("""
    #### DistilBERT (Transformer-based)
    State-of-the-art Transformer language model fine-tuned on the SST-2 sentiment classification corpus.
    - **Architecture**: A distilled, lightweight variant of BERT (Bidirectional Encoder Representations from Transformers). Retains 97% of BERT's language understanding capabilities while being 40% smaller and 60% faster.
    - **Parameters**: 66 Million parameters.
    - **Use Case**: High-accuracy sentiment parsing, serving as the benchmark standard.
    """)

with spec_tabs[4]:
    st.markdown("""
    #### Ensemble Model
    A meta-model combining predictions from the other four models to reduce variance and improve generalizability.
    - **Aggregator**: Weighted average of prediction probabilities:
      - $\\text{Weight}_{\\text{DistilBERT}} = 0.40$
      - $\\text{Weight}_{\\text{GRU Attention}} = 0.25$
      - $\\text{Weight}_{\\text{BiLSTM}} = 0.20$
      - $\\text{Weight}_{\\text{CNN-LSTM}} = 0.15$
    - **Use Case**: Production consensus-based predictions.
    """)

st.markdown("---")

st.subheader("🕵️ Explainable AI (XAI) Methods")
col_x1, col_x2 = st.columns(2)
with col_x1:
    st.markdown("""
    ##### 1. Local Interpretable Model-Agnostic Explanations (LIME)
    LIME works by perturbing the input text (randomly masking words), running predictions on these perturbed samples, and fitting a local, weighted linear Ridge regression model on the presence/absence of tokens. The resulting coefficients indicate the directional contribution of each word towards the final sentiment classification.
    """)
with col_x2:
    st.markdown("""
    ##### 2. Recurrent Attention Weights
    For our GRU with Attention model, we extract the raw outputs of the custom Attention layer. This layer calculates an alignment vector over the GRU sequences, assigning a mathematical importance weight to each token. High attention weights highlight tokens that dominate the final dense layer classification.
    """)

st.markdown("---")

# Tech stack visual grid
st.subheader("🛠️ Technology Stack")
col_ts1, col_ts2, col_ts3, col_ts4 = st.columns(4)
with col_ts1:
    st.markdown("""
    **Core Backend**
    - FastAPI
    - Uvicorn
    - Pydantic
    """)
with col_ts2:
    st.markdown("""
    **ML / NLP Frameworks**
    - TensorFlow / Keras
    - PyTorch
    - HF Transformers
    - Scikit-learn
    """)
with col_ts3:
    st.markdown("""
    **Database & MLOps**
    - PostgreSQL
    - SQLAlchemy
    - SQLite Fallback
    - MLflow Tracker
    """)
with col_ts4:
    st.markdown("""
    **Visual Frontend**
    - Streamlit UI
    - Plotly Charts
    - custom HSL / CSS
    """)

render_footer()
