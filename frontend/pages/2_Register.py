import streamlit as st
import re
from frontend.utils.auth_state import init_session_state, is_logged_in, get_client

# Page configurations
st.set_page_config(page_title="Register — SIP", page_icon="📝")

# Initialize session state
init_session_state()

# Redirect to dashboard if already authenticated
if is_logged_in():
    st.switch_page("pages/3_Dashboard.py")

# Centering layout
_, col_mid, _ = st.columns([1, 2, 1])

with col_mid:
    st.title("Create account")
    
    username = st.text_input(
        "Username",
        help="3–30 characters, letters/numbers/underscore only"
    )
    email = st.text_input("Email address")
    password = st.text_input(
        "Password",
        type="password",
        help="Minimum 8 characters"
    )
    confirm = st.text_input("Confirm password", type="password")
    
    register_btn = st.button("Register", type="primary", use_container_width=True)
    
    if register_btn:
        # Client side validations
        username_clean = username.strip()
        email_clean = email.strip()
        
        if not username_clean or not email_clean or not password or not confirm:
            st.error("All fields are required.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters.")
        elif len(username_clean) < 3:
            st.error("Username must be at least 3 characters.")
        elif len(username_clean) > 30:
            st.error("Username cannot exceed 30 characters.")
        elif not re.match("^[a-zA-Z0-9_]+$", username_clean):
            st.error("Username must contain only letters, numbers, and underscores.")
        elif "@" not in email_clean or "." not in email_clean:
            st.error("Please enter a valid email address.")
        else:
            try:
                client = get_client()
                client.register(username=username_clean, email=email_clean, password=password)
                st.success("Account created successfully! Please log in.")
                st.switch_page("pages/1_Login.py")
            except Exception as e:
                st.error(str(e))
                
    st.divider()
    st.page_link("pages/1_Login.py", label="Already have an account? Sign in →")
