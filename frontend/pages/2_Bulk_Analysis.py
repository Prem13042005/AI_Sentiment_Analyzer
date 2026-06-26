import streamlit as st
import requests
import pandas as pd
import io
import os
import plotly.express as px
from dotenv import load_dotenv

# Shared UI components
from components.ui import load_css, set_page_config, render_sidebar, header_section, render_footer

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

set_page_config("Bulk CSV Analysis")
load_css()
render_sidebar()

header_section(
    "Bulk Review Analysis", 
    "Upload a CSV review dataset, run NLP predictions, and download the processed files."
)

st.markdown("### Upload CSV Dataset")
uploaded_file = st.file_uploader(
    "Select a CSV file containing user reviews. The system will automatically detect the review column.",
    type=["csv"]
)

col_model, col_spacer = st.columns([2, 2])
with col_model:
    model_name = st.selectbox(
        "Select NLP Classification Model:",
        options=["Ensemble Model", "DistilBERT", "GRU with Attention", "Bidirectional LSTM", "CNN-LSTM"]
    )

def run_bulk_csv_api(file_bytes, filename: str, model_key: str):
    try:
        files = {"file": (filename, file_bytes, "text/csv")}
        data = {"model_name": model_key}
        res = requests.post(
            f"{API_URL}/predict/bulk-csv",
            files=files,
            data=data,
            timeout=15
        )
        if res.status_code == 200:
            return pd.read_csv(io.BytesIO(res.content)), False
    except Exception as e:
        print(f"API Bulk CSV run failed: {e}")
    return None, True

def run_bulk_csv_local(df: pd.DataFrame, model_key: str):
    from backend.app.services.model_service import ModelService
    from backend.app.database.connection import SessionLocal
    from backend.app.services.db_service import DatabaseService
    
    # 1. Detect column
    possible_cols = ['text', 'review', 'reviews', 'comment', 'comments', 'feedback', 'text_content']
    text_column = None
    for col in df.columns:
        if col.lower() in possible_cols:
            text_column = col
            break
    if text_column is None:
        string_cols = df.select_dtypes(include=['object']).columns
        if len(string_cols) > 0:
            text_column = string_cols[0]
        else:
            raise ValueError("Could not find a valid text or review column in the CSV.")
            
    # Extract list
    texts = df[text_column].fillna("").astype(str).tolist()
    
    # Run batch predictions
    service = ModelService()
    predictions = service.predict_batch(texts=texts, model_name=model_key)
    
    # Append
    df["predicted_sentiment"] = [res["sentiment"] for res in predictions]
    df["confidence"] = [res["confidence"] for res in predictions]
    
    # Log to DB in bulk
    db = SessionLocal()
    try:
        db_logs = [
            {
                "text": res["text"],
                "model_name": res["model_name"],
                "sentiment": res["sentiment"],
                "confidence": res["confidence"],
                "probabilities": res["probabilities"],
                "execution_time_ms": res["execution_time_ms"]
            }
            for res in predictions
        ]
        DatabaseService.log_bulk_predictions(db, db_logs)
    finally:
        db.close()
        
    return df

if uploaded_file is not None:
    # Read files in frontend memory
    file_bytes = uploaded_file.getvalue()
    try:
        input_df = pd.read_csv(io.BytesIO(file_bytes))
        st.success(f"Successfully loaded CSV containing {len(input_df)} records.")
        st.dataframe(input_df.head(5), use_container_width=True)
        
        run_analysis = st.button("📊 Run Bulk Sentiment Analysis", use_container_width=True)
        
        if run_analysis:
            # Map model names
            model_map = {
                "Ensemble Model": "ensemble",
                "DistilBERT": "distilbert",
                "GRU with Attention": "gru_attention",
                "Bidirectional LSTM": "bilstm",
                "CNN-LSTM": "cnn_lstm"
            }
            model_key = model_map[model_name]
            
            with st.spinner("Processing CSV file and running batch model predictions..."):
                # Try API
                processed_df, is_fallback = run_bulk_csv_api(file_bytes, uploaded_file.name, model_key)
                
                # Fallback to local
                if is_fallback:
                    try:
                        processed_df = run_bulk_csv_local(input_df.copy(), model_key)
                        st.info("ℹ️ Running inference via local direct Python runtime fallback (API is down).")
                    except Exception as e:
                        st.error(f"Failed to process CSV file locally: {e}")
                        processed_df = None
            
            if processed_df is not None:
                st.markdown("---")
                st.subheader("✅ Analysis Summary")
                
                # Visualizations of results
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    # Pie chart
                    sent_counts = processed_df["predicted_sentiment"].value_counts().reset_index()
                    sent_counts.columns = ["Sentiment", "Count"]
                    fig_pie = px.pie(
                        sent_counts, values="Count", names="Sentiment",
                        color="Sentiment",
                        color_discrete_map={"Positive": "#10b981", "Negative": "#f43f5e"},
                        title="Sentiment Class Distribution"
                    )
                    fig_pie.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#f3f4f6')
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with col_c2:
                    # Histogram
                    fig_hist = px.histogram(
                        processed_df, x="confidence",
                        nbins=10,
                        title="Confidence Score Ranges",
                        color_discrete_sequence=["#7c3aed"]
                    )
                    fig_hist.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#f3f4f6'),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.08)'),
                        yaxis=dict(gridcolor='rgba(255,255,255,0.08)')
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                # Table Preview
                st.subheader("🔍 Processed Dataset Preview")
                st.dataframe(processed_df.head(20), use_container_width=True)
                
                # Download Button
                csv_buffer = io.StringIO()
                processed_df.to_csv(csv_buffer, index=False)
                csv_bytes = csv_buffer.getvalue().encode('utf-8')
                
                st.download_button(
                    label="📥 Download Analyzed CSV Dataset",
                    data=csv_bytes,
                    file_name=f"analyzed_{uploaded_file.name}",
                    mime="text/csv",
                    use_container_width=True
                )
                
    except Exception as e:
        st.error(f"Error parsing CSV: {e}")
else:
    # Renders placeholder dashboard instructions
    st.info("ℹ️ Please upload a CSV file to begin. Make sure the file contains at least one column named: 'text', 'review', or 'feedback'.")

render_footer()
