import os
import streamlit as st
import pandas as pd

from frontend.utils.auth_state import require_auth, get_client
from frontend.utils.charts import model_scores_chart

# Page config and authorization check
st.set_page_config(page_title="Analyzer — SIP", page_icon="🔍", layout="wide")
require_auth()

# Inject style.css
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.title("Sentiment analyzer")

left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader("Input Feedback")
    text = st.text_area(
        "Enter text to analyze",
        height=180,
        placeholder="Paste a review, comment, or any text here...",
        max_chars=2000
    )
    
    char_count = len(text)
    st.caption(f"{char_count} / 2000 characters")
    if char_count > 1900:
        st.warning("Approaching 2000 character limit")
        
    model_name = st.selectbox(
        "Model",
        options=["ensemble", "distilbert", "bilstm", "gru", "cnn_lstm"],
        format_func=lambda x: {
            "ensemble": "Ensemble (recommended)",
            "distilbert": "DistilBERT",
            "bilstm": "BiLSTM",
            "gru": "GRU + Attention",
            "cnn_lstm": "CNN-LSTM"
        }[x]
    )
    
    analyze_btn = st.button("Analyze", type="primary", disabled=(len(text.strip()) == 0))

with right_col:
    st.subheader("Analysis Output")
    if analyze_btn and text.strip():
        with st.spinner("Analyzing..."):
            try:
                client = get_client()
                result = client.predict(text=text.strip(), model_name=model_name)
            except RuntimeError as e:
                st.error(str(e))
                st.stop()
                
        sentiment = result["sentiment"]
        confidence = result["confidence"]
        
        # Get emoji and color map
        emoji_map = {"positive": "😊", "negative": "😞", "neutral": "😐"}
        color_map = {"positive": "#22c55e", "negative": "#ef4444", "neutral": "#6b7280"}
        
        emoji = emoji_map.get(sentiment, "😐")
        color = color_map.get(sentiment, "#6b7280")
        
        st.markdown(f"<div style='text-align:center;font-size:3rem'>{emoji}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;font-size:1.4rem;font-weight:600;color:{color}'>{sentiment.upper()}</div>", unsafe_allow_html=True)
        
        st.progress(confidence, text=f"Confidence: {confidence*100:.1f}%")
        st.caption(f"Processed in {result['processing_time_ms']:.0f}ms using {result['model_used']}")
        
        # Display model breakdown if Ensemble was selected
        if result.get("model_scores") and len(result["model_scores"]) > 1:
            st.subheader("Model breakdown")
            st.plotly_chart(model_scores_chart(result["model_scores"]), use_container_width=True)
            
        # Display LIME word highlights
        if result.get("lime_words"):
            st.subheader("Word attribution (LIME)")
            words = result["lime_words"]
            highlighted = ""
            for item in words:
                w, weight = item["word"], item["weight"]
                if weight > 0.05:
                    highlighted += f'<span class="lime-pos">{w}</span> '
                elif weight < -0.05:
                    highlighted += f'<span class="lime-neg">{w}</span> '
                else:
                    highlighted += f'{w} '
            st.markdown(highlighted, unsafe_allow_html=True)
            st.caption("Green = contributes to positive · Red = contributes to negative")
            
        # Display GRU Attention mapping
        if result.get("attention_weights"):
            st.subheader("Attention weights (GRU)")
            attn = result["attention_weights"]
            attn_df = pd.DataFrame(list(attn.items()), columns=["Word", "Attention"]).sort_values("Attention", ascending=False).head(10)
            st.dataframe(attn_df, hide_index=True, use_container_width=True)
    else:
        st.info("Input a review and click 'Analyze' to classify and view details.")
