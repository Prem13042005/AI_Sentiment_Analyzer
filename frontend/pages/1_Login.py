import streamlit as st
from frontend.utils.auth_state import init_session_state, is_logged_in, do_login, get_client, nav_to, link_button

# Page configurations
st.set_page_config(page_title="Login — SIP", page_icon="🔐")

# Initialize session state
init_session_state()

# Redirect to dashboard if already authenticated
if is_logged_in():
    nav_to("pages/3_Dashboard.py")

# Centering layout
_, col_mid, _ = st.columns([1, 2, 1])

with col_mid:
    st.title("Sign in")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        login_btn = st.button("Sign In", type="primary", use_container_width=True)
        if login_btn:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                try:
                    # Authenticate
                    client = get_client()
                    res = client.login(username=username, password=password)
                    do_login(
                        token=res["access_token"],
                        username=res["username"],
                        user_id=res["user_id"]
                    )
                    st.success("Successfully logged in!")
                    nav_to("pages/3_Dashboard.py")
                except Exception as e:
                    st.error(str(e))
                    
    with col2:
        demo_btn = st.button("Demo Access", use_container_width=True)
        if demo_btn:
            try:
                # Login as default demo credentials
                client = get_client()
                res = client.login(username="demo", password="demo123")
                do_login(
                    token=res["access_token"],
                    username=res["username"],
                    user_id=res["user_id"]
                )
                st.success("Welcome, Demo User!")
                nav_to("pages/3_Dashboard.py")
            except Exception as e:
                st.error(str(e))
                
    st.divider()
    link_button("Create an account →", "pages/2_Register.py")
