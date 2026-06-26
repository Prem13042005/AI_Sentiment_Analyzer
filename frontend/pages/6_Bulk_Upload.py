import os
import streamlit as st
import pandas as pd

from frontend.utils.auth_state import require_auth, get_client

# Page configurations and auth check
st.set_page_config(page_title="Bulk upload — SIP", page_icon="📂", layout="wide")
require_auth()

# Inject style.css
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.title("Bulk CSV analysis")
st.info("Upload a CSV file. Max 100 rows. Each row will be analyzed for sentiment.")

uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
if not uploaded:
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as e:
    st.error(f"Failed to read CSV: {e}")
    st.stop()

st.subheader("Preview")
st.dataframe(df.head(5), use_container_width=True)

text_col = st.selectbox("Which column contains the text?", options=df.columns.tolist())

if st.button("Analyze all rows", type="primary"):
    if len(df) > 100:
        st.error("Max 100 rows supported. Please trim your CSV.")
        st.stop()
        
    texts = df[text_col].fillna("").astype(str).tolist()
    progress_bar = st.progress(0, text="Starting...")
    results = []
    
    client = get_client()
    
    for i, text in enumerate(texts):
        # Truncate to maximum characters support
        truncated_text = text[:2000]
        try:
            r = client.predict(truncated_text, "ensemble")
            results.append({
                "sentiment": r["sentiment"],
                "confidence": round(r["confidence"] * 100, 1)
            })
        except Exception as e:
            results.append({
                "sentiment": "error",
                "confidence": 0.0
            })
        
        # Update progress bar
        progress_val = (i + 1) / len(texts)
        progress_bar.progress(
            progress_val,
            text=f"Processing row {i + 1} of {len(texts)}..."
        )
        
    # Append predictions back to the copied dataframe
    results_df = df.copy()
    results_df["sentiment"] = [r["sentiment"] for r in results]
    results_df["confidence_pct"] = [r["confidence"] for r in results]
    
    st.success(f"Done. Analyzed {len(texts)} rows.")
    st.dataframe(results_df, use_container_width=True)
    
    # Download processed CSV
    processed_csv = results_df.to_csv(index=False)
    st.download_button(
        label="📥 Download results CSV",
        data=processed_csv,
        file_name="sip_bulk_results.csv",
        mime="text/csv",
        use_container_width=True
    )
