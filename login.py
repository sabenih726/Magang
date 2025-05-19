import streamlit as st
import utils

def login(username, password):
    user_data = utils.authenticate_user(username, password)
    if user_data:
        st.session_state.user = user_data
        utils.log_user_activity(username, "login")
        return True
    return False

def logout():
    if st.session_state.get("user"):
        utils.log_user_activity(st.session_state["user"]['username'], "logout")
    st.session_state.user = None

def login_screen():
    st.title("🚪 GA Ticket Management Login")
    st.subheader("Login to your account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(username, password):
            st.success("Login successful")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("---")
    st.subheader("Don't have an account?")
    with st.expander("Register here"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        department = st.selectbox("Department", ["IT", "HR", "Finance", "GA", "Marketing"])

        if st.button("Register"):
            if not (new_username and new_password and full_name and email and department):
                st.error("All fields are required.")
            elif not utils.validate_email(email):
                st.error("Invalid email format.")
            else:
                user_data = {
                    "username": new_username,
                    "password": new_password,
                    "full_name": full_name,
                    "email": email,
                    "role": "staff",
                    "department": department
                }
                success, message = utils.add_user(user_data)
                if success:
                    st.success(f"{message}. You can now login.")
                else:
                    st.error(message)
