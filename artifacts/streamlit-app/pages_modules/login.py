import streamlit as st
import pyrebase

def render():

    # ---------- Hide Streamlit UI ----------
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display:none;}
    header {visibility:hidden;}
    footer {visibility:hidden;}
    </style>
    
    """, unsafe_allow_html=True)


    # ---------- Firebase ----------
    firebase_config = {
        "apiKey": "AIzaSyBTCyNSumI1jG-virrYe9w452TI24mULKU",
        "authDomain": "statyxai.firebaseapp.com",
        "projectId": "statyxai",
        "storageBucket": "statyxai.firebasestorage.app",
        "databaseURL": ""
    }

    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()

    # ---------- SESSION ----------
    if "user" not in st.session_state:
        st.session_state.user = None

    # ---------- UI ----------

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    st.markdown("<h2>⚡ STATYX AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; margin-bottom:20px;'>Smart AI Platform</p>", unsafe_allow_html=True)

    mode = st.radio(
        "",
        ["Login", "Register"],
        horizontal=True
    )

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # ---------- LOGIN ----------
    if mode == "Login":

        if st.button("🚀 Login", use_container_width=True):

            if email == "" or password == "":
                st.warning("Please enter email and password")

            else:
                try:
                    user = auth.sign_in_with_email_and_password(email, password)

                    st.session_state.user = user
                    st.session_state.email = email
                    st.session_state.logged_in = True
                    st.session_state.step = "upload"

                    st.rerun()

                except Exception:
                    st.error("Invalid email or password")

    # ---------- REGISTER ----------
    else:

        if st.button("✨ Create Account", use_container_width=True):

            if not email or not password:
                st.warning("Enter email & password")

            else:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    st.success("Account created. Please login.")

                except Exception as e:
                    error_str = str(e)

                    if "EMAIL_EXISTS" in error_str:
                        st.error("Email already registered. Please login instead.")
                    elif "WEAK_PASSWORD" in error_str:
                        st.error("Password must be at least 6 characters.")
                    else:
                        st.error("Registration failed. Try again.")

    st.markdown('</div>', unsafe_allow_html=True)
