import streamlit as st
import requests
import os
import re
import numpy as np
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Shared UI components
from components.ui import load_css, set_page_config, render_sidebar, header_section, render_footer

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

set_page_config("Explainable AI")
load_css()
render_sidebar()

header_section(
    "Explainable AI (XAI) Engine", 
    "Decode NLP models and explore word-level attribution weights using LIME and Attention Layer heatmaps."
)

st.markdown("### Input Review text to Explain")
xai_text = st.text_area(
    "Write review text below:",
    value="This product is an amazing and excellent tool, but the setup was slow and customer service was terrible.",
    placeholder="Write your feedback here...",
    height=100
)

col_model, col_action = st.columns([2, 1])
with col_model:
    model_name = st.selectbox(
        "Explainable Model:",
        options=["GRU with Attention", "Ensemble Model", "DistilBERT", "Bidirectional LSTM", "CNN-LSTM"]
    )
with col_action:
    st.markdown("<br>", unsafe_allow_html=True)
    explain_btn = st.button("🔍 Explain Predictions", use_container_width=True)

def run_explain_api(text: str, model_val: str):
    try:
        res = requests.post(
            f"{API_URL}/explain",
            json={"text": text, "model_name": model_val},
            timeout=8
        )
        if res.status_code == 200:
            return res.json(), False
    except Exception as e:
        print(f"API Explain run failed: {e}")
    return None, True

def run_explain_local(text: str, model_val: str):
    from backend.app.services.model_service import ModelService
    from backend.app.utils.lime_explain import LimeTextExplainer
    
    service = ModelService()
    base_prediction = service.predict(text=text, model_name=model_val)
    
    def lime_predict_fn(texts: List[str]) -> np.ndarray:
        batch_res = service.predict_batch(texts, model_name=model_val)
        probs = np.zeros((len(texts), 2))
        for i, res in enumerate(batch_res):
            probs[i, 0] = res["probabilities"]["negative"]
            probs[i, 1] = res["probabilities"]["positive"]
        return probs
        
    explainer = LimeTextExplainer(num_samples=150, keep_prob=0.75)
    lime_explanation = explainer.explain(text, lime_predict_fn)
    
    attention_weights = None
    if model_val in ["gru_attention", "ensemble"]:
        attention_weights = service.extract_attention_weights(text)
        
    return {
        "text": text,
        "model_name": model_val,
        "sentiment": base_prediction["sentiment"],
        "confidence": base_prediction["confidence"],
        "lime_explanation": lime_explanation,
        "attention_weights": attention_weights
    }

def render_lime_html(words: list, seq_attributions: list):
    # Find max weight for normalization
    weights = [abs(item["weight"]) for item in seq_attributions]
    max_weight = max(weights) if weights else 1.0
    if max_weight == 0.0:
        max_weight = 1.0
        
    html = '<div style="background: rgba(18, 24, 41, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 20px; line-height: 2.2; color: #f3f4f6; font-size: 1.1rem;">'
    
    for item in seq_attributions:
        word = item["word"]
        weight = item["weight"]
        
        # Calculate opacity
        norm_weight = min(1.0, abs(weight) / max_weight)
        opacity = 0.1 + 0.7 * norm_weight # scale to range [0.1, 0.8]
        
        if weight > 0.005:
            # Positive contributing word (Green)
            html += f'<span style="background-color: rgba(16, 185, 129, {opacity:.2f}); border-bottom: 2px solid #10b981; border-radius: 4px; padding: 2px 6px; margin: 0 3px; font-weight: 500;">{word}</span>'
        elif weight < -0.005:
            # Negative contributing word (Red)
            html += f'<span style="background-color: rgba(244, 63, 94, {opacity:.2f}); border-bottom: 2px solid #f43f5e; border-radius: 4px; padding: 2px 6px; margin: 0 3px; font-weight: 500;">{word}</span>'
        else:
            # Normal word
            html += f'<span>{word} </span>'
            
    html += '</div>'
    return html

def render_attention_html(attention_weights: list):
    # Find max weight
    weights = [item["weight"] for item in attention_weights]
    max_weight = max(weights) if weights else 1.0
    if max_weight == 0.0:
        max_weight = 1.0
        
    html = '<div style="background: rgba(18, 24, 41, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 20px; line-height: 2.2; color: #f3f4f6; font-size: 1.1rem;">'
    
    for item in attention_weights:
        word = item["word"]
        weight = item["weight"]
        
        # Soft blue glow representing attention focus
        norm_weight = min(1.0, weight / max_weight)
        opacity = 0.05 + 0.8 * norm_weight
        
        html += f'<span style="background-color: rgba(6, 182, 212, {opacity:.2f}); border-bottom: 2px solid #06b6d4; border-radius: 4px; padding: 2px 6px; margin: 0 3px; font-weight: 500;">{word}</span>'
        
    html += '</div>'
    return html

if explain_btn and xai_text.strip():
    model_map = {
        "Ensemble Model": "ensemble",
        "DistilBERT": "distilbert",
        "GRU with Attention": "gru_attention",
        "Bidirectional LSTM": "bilstm",
        "CNN-LSTM": "cnn_lstm"
    }
    model_key = model_map[model_name]
    
    with st.spinner("Executing LIME perturbations and computing word coefficients..."):
        result, is_fallback = run_explain_api(xai_text, model_key)
        
        if is_fallback:
            try:
                result = run_explain_local(xai_text, model_key)
                st.info("ℹ️ Running explainability pipeline via local direct Python fallback (API down).")
            except Exception as e:
                st.error(f"Failed to execute local explainability engine: {e}")
                result = None
                
    if result is not None:
        st.markdown("---")
        
        # Display Prediction Badge
        is_pos = result["sentiment"] == "Positive"
        badge_class = "sentiment-badge-pos" if is_pos else "sentiment-badge-neg"
        badge_icon = "🟢" if is_pos else "🔴"
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"**Target Prediction**: <span class='sentiment-badge {badge_class}'>{badge_icon} {result['sentiment']}</span>", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"**Model Confidence**: **`{result['confidence']*100:.1f}%`**")
            
        st.markdown("---")
        
        # Section 1: LIME Word attribution highlight
        st.subheader("🕵️ LIME Word Highlights (Local Feature Importance)")
        st.write("Words highlighted in **green** push the model towards a **Positive** score; words in **red** push it towards **Negative**. Intensity indicates word contribution strength.")
        
        lime_data = result["lime_explanation"]
        lime_html = render_lime_html(lime_data["words"], lime_data["sequence_attributions"])
        st.markdown(lime_html, unsafe_allow_html=True)
        
        # Section 2: Bar charts of top coefficients
        st.markdown("<br>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.markdown("##### 🟢 Top Positive Word Influence")
            pos_df = pd.DataFrame(lime_data["positive_contributions"])
            if not pos_df.empty:
                fig_pos = px.bar(
                    pos_df.head(8), x="weight", y="word",
                    orientation="h",
                    color_discrete_sequence=["#10b981"]
                )
                fig_pos.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f3f4f6'), margin=dict(l=0, r=0, t=10, b=0), height=250,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.08)'), yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_pos, use_container_width=True)
            else:
                st.write("No positive word contributors found.")
                
        with col_b2:
            st.markdown("##### 🔴 Top Negative Word Influence")
            neg_df = pd.DataFrame(lime_data["negative_contributions"])
            if not neg_df.empty:
                fig_neg = px.bar(
                    neg_df.head(8), x="weight", y="word",
                    orientation="h",
                    color_discrete_sequence=["#f43f5e"]
                )
                fig_neg.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#f3f4f6'), margin=dict(l=0, r=0, t=10, b=0), height=250,
                    xaxis=dict(gridcolor='rgba(255,255,255,0.08)'), yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_neg, use_container_width=True)
            else:
                st.write("No negative word contributors found.")
                
        # Section 3: Attention Weight Heatmap
        attn_data = result.get("attention_weights")
        if attn_data:
            st.markdown("---")
            st.subheader("💡 Sequence Attention Weights Heatmap")
            st.write("For the **GRU with Attention** model, this shows where the model focused its mathematical 'attention' when integrating sequences. Intensity indicates layer weight values.")
            
            attn_html = render_attention_html(attn_data)
            st.markdown(attn_html, unsafe_allow_html=True)
            
            # Show Plotly distribution of attention weights
            st.markdown("<br>", unsafe_allow_html=True)
            attn_df = pd.DataFrame(attn_data)
            fig_attn = px.bar(
                attn_df, x="word", y="weight",
                title="Word-Level Attention Coefficient Distribution",
                color_discrete_sequence=["#06b6d4"]
            )
            fig_attn.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f3f4f6'), margin=dict(l=0, r=0, t=30, b=0), height=280,
                xaxis=dict(gridcolor='rgba(0,0,0,0)'), yaxis=dict(gridcolor='rgba(255,255,255,0.08)')
            )
            st.plotly_chart(fig_attn, use_container_width=True)
else:
    st.info("💡 Write a sentence and click 'Explain Predictions' to trace the model's word attributions and attention weights.")
    
render_footer()
