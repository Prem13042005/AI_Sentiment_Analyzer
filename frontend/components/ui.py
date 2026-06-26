import streamlit as st
import os

def load_css():
    """
    Injects Google Fonts and custom CSS styles into the current Streamlit page.
    Ensures a consistent, enterprise-grade dark theme across all subpages.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(os.path.dirname(current_dir), "assets", "styles.css")
    
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found. Falling back to default layout.")

def set_page_config(title: str):
    """
    Applies unified page title and browser tab icon.
    """
    st.set_page_config(
        page_title=f"{title} | Sentiment Intelligence",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_sidebar():
    """
    Renders the consistent enterprise logo, status check, and navigation guide on the sidebar.
    """
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <h1 style="font-size: 2.2rem; color: #7c3aed; margin-bottom: 0px; font-weight: 800;">🧠 SIP</h1>
        <p style="font-size: 0.95rem; color: #9ca3af; font-weight: 500; letter-spacing: 0.05em; margin-top: 5px;">SENTIMENT INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Model statuses on sidebar
    st.sidebar.subheader("System Status")
    st.sidebar.markdown("""
    🟢 **API Gateways**: Active<br>
    🟢 **Postgres Pool**: Running<br>
    🟢 **MLflow Tracker**: Standby
    """, unsafe_allow_html=True)
    
    # Active Models list
    st.sidebar.subheader("Supported Architectures")
    st.sidebar.info("""
    - **BiLSTM** (v1.0.2)
    - **GRU with Attention** (v1.1.0)
    - **CNN-LSTM** (v1.0.1)
    - **DistilBERT** (SST-2)
    - **Ensemble Model** (v1.2.0)
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; color: #9ca3af; font-size: 0.75rem;">
        &copy; 2026 Enterprise NLP Solutions.
    </div>
    """, unsafe_allow_html=True)

def metric_card(title: str, value: str, delta: str = None, color: str = "violet", help_text: str = None):
    """
    Renders a premium glassmorphic statistics card.
    """
    border_color = "rgba(124, 58, 237, 0.3)" # Violet
    if color == "blue":
        border_color = "rgba(6, 182, 212, 0.3)"
    elif color == "green":
        border_color = "rgba(16, 185, 129, 0.3)"
    elif color == "red":
        border_color = "rgba(244, 63, 94, 0.3)"
        
    delta_html = ""
    if delta:
        is_positive = "+" in delta
        delta_color = "#10b981" if is_positive else "#f43f5e"
        delta_html = f"<span style='color: {delta_color}; font-size: 0.85rem; font-weight: 600; margin-left: 8px;'>{delta}</span>"
        
    st.markdown(f"""
    <div class="stCard" style="border-left: 4px solid {border_color}; margin-bottom: 15px;">
        <p style="color: #9ca3af; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 6px 0; font-weight: 500;">
            {title}
        </p>
        <div style="display: flex; align-items: baseline;">
            <span style="color: #f3f4f6; font-size: 2rem; font-weight: 700; line-height: 1;">{value}</span>
            {delta_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

def header_section(title: str, subtitle: str):
    """
    Renders a premium header layout.
    """
    st.markdown(f"""
    <div style="margin-bottom: 30px;">
        <h1 style="font-size: 2.8rem; margin: 0; background: linear-gradient(135deg, #f3f4f6 30%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {title}
        </h1>
        <p style="color: #9ca3af; font-size: 1.15rem; margin-top: 8px; font-weight: 400;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """
    Renders unified footer tags.
    """
    st.markdown("""
    <div class="footer-text">
        Sentiment Intelligence Platform &bull; Built with FastAPI, Streamlit, TensorFlow and Hugging Face &bull; v1.0.0
    </div>
    """, unsafe_allow_html=True)
