import os
import streamlit as st
from backend.app.database import Base # placeholder or no import
from frontend.utils.api_client import SIPApiClient

# Get API URL from env
API_URL = os.getenv("API_URL", "http://localhost:8000")

def init_session_state():
    """
    Initializes standard authentication keys in Streamlit's session state.
    """
    defaults = {
        "token": None,
        "username": None,
        "user_id": None,
        "api_client": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def is_logged_in() -> bool:
    """
    Returns True if the operator is authenticated.
    """
    return st.session_state.get("token") is not None

def do_login(token: str, username: str, user_id: str):
    """
    Sets session state variables and instantiates the API client with the token.
    """
    st.session_state.token = token
    st.session_state.username = username
    st.session_state.user_id = user_id
    st.session_state.api_client = SIPApiClient(base_url=API_URL, token=token)

def do_logout():
    """
    Clears all authentication variables and re-runs the page to apply redirects.
    """
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.api_client = None
    st.rerun()

def require_auth():
    """
    FastAPI-like route guard. If the session is unauthenticated,
    displays a login redirect warning and halts page execution.
    """
    init_session_state()
    if not is_logged_in():
        st.warning("You need to log in to access this page.")
        st.page_link("pages/1_Login.py", label="Go to login")
        st.stop()

def get_client() -> SIPApiClient:
    """
    Retrieves the active authenticated API client wrapper.
    """
    if st.session_state.api_client is None:
        # Return unauthenticated client if not logged in
        return SIPApiClient(base_url=API_URL)
    return st.session_state.api_client
