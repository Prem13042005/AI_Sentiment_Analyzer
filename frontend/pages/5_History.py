import os
import streamlit as st
import pandas as pd

from frontend.utils.auth_state import require_auth, get_client

# Page configurations and checks
st.set_page_config(page_title="History — SIP", page_icon="📋", layout="wide")
require_auth()

# Inject style.css
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

st.title("Analysis history")

try:
    client = get_client()
    history = client.get_history(limit=200)
except Exception as e:
    st.error(f"Failed to fetch history logs: {e}")
    st.stop()

if not history:
    st.info("No analyses yet.")
    st.stop()

# Convert list of dicts to DataFrame
df = pd.DataFrame(history)

# Header columns for search, filter, and export
top_row = st.columns([2, 1, 1])

with top_row[0]:
    search = st.text_input("Search", placeholder="Filter by text content...")
with top_row[1]:
    sentiment_filter = st.selectbox("Sentiment", ["All", "positive", "negative", "neutral"])
with top_row[2]:
    st.markdown("<br>", unsafe_allow_html=True)
    # Download as CSV button
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Export CSV",
        data=csv_data,
        file_name="sip_history.csv",
        mime="text/csv",
        use_container_width=True
    )

# Apply filters locally on the DataFrame
df_filtered = df.copy()
if search:
    df_filtered = df_filtered[df_filtered["text_snippet"].str.contains(search, case=False, na=False)]
if sentiment_filter != "All":
    df_filtered = df_filtered[df_filtered["sentiment"] == sentiment_filter]

st.caption(f"Showing {len(df_filtered)} results")

if df_filtered.empty:
    st.info("No logs matched the selected filters.")
else:
    # Prepare DataFrame for data_editor
    df_filtered["Delete"] = False
    
    # Format and rename columns
    df_filtered["created_at"] = pd.to_datetime(df_filtered["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
    df_filtered["confidence"] = df_filtered["confidence"].apply(lambda x: f"{x*100:.1f}%")
    
    df_display = df_filtered.rename(columns={
        "text_snippet": "Text",
        "sentiment": "Sentiment",
        "confidence": "Confidence",
        "model_used": "Model",
        "created_at": "Date"
    })
    
    # Sort and slice
    df_display = df_display[["Delete", "id", "Text", "Sentiment", "Confidence", "Model", "Date"]]
    
    # Data editor with interactive checkbox column config
    edited_df = st.data_editor(
        df_display,
        column_config={
            "id": None,  # Hide the ID column
            "Delete": st.column_config.CheckboxColumn(
                "Delete",
                help="Mark checkbox to delete this log entry",
                default=False
            )
        },
        disabled=["Text", "Sentiment", "Confidence", "Model", "Date"],
        hide_index=True,
        use_container_width=True
    )
    
    # Apply deletes if any rows are selected
    deleted_rows = edited_df[edited_df["Delete"] == True]
    if not deleted_rows.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        confirm_delete = st.button(
            f"🗑️ Delete {len(deleted_rows)} Selected Entry/Entries",
            type="primary",
            use_container_width=True
        )
        if confirm_delete:
            with st.spinner("Deleting records..."):
                try:
                    for _, row in deleted_rows.iterrows():
                        client.delete_history(row["id"])
                    st.success("Successfully deleted selected logs!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete records: {e}")
