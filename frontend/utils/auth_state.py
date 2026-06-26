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
        link_button("Go to login", "pages/1_Login.py")
        st.stop()

def get_client() -> SIPApiClient:
    """
    Retrieves the active authenticated API client wrapper.
    """
    if st.session_state.api_client is None:
        # Return unauthenticated client if not logged in
        return SIPApiClient(base_url=API_URL)
    return st.session_state.api_client

def nav_to(page_name: str):
    """
    Programmatic navigation helper for Streamlit 1.28.2.
    """
    if page_name in ["app.py", "Home", "/"]:
        url = "/"
    else:
        clean_name = page_name.split("/")[-1].replace(".py", "")
        if "_" in clean_name and clean_name.split("_")[0].isdigit():
            clean_name = "_".join(clean_name.split("_")[1:])
        url = f"/{clean_name}"
    
    js = f"""
    <script type="text/javascript">
        window.parent.location.href = "{url}";
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def link_button(label: str, page_name: str, icon: str = ""):
    """
    Standard anchor link formatted as a button for Streamlit 1.28.2.
    """
    if page_name in ["app.py", "Home", "/"]:
        url = "/"
    else:
        clean_name = page_name.split("/")[-1].replace(".py", "")
        if "_" in clean_name and clean_name.split("_")[0].isdigit():
            clean_name = "_".join(clean_name.split("_")[1:])
        url = f"/{clean_name}"
    
    icon_str = f"{icon} " if icon else ""
    st.markdown(f'<a href="{url}" target="_self" style="text-decoration:none;"><button style="align-items: center; justify-content: center; background-color: rgb(255, 255, 255); border: 1px solid rgb(230, 234, 241); border-radius: 4px; color: rgb(49, 51, 63); display: inline-flex; font-size: 14px; font-weight: 400; padding: 0.25rem 0.75rem; text-decoration: none; cursor: pointer;">{icon_str}{label}</button></a>', unsafe_allow_html=True)
