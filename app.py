import streamlit as st
import login
import pandas as pd
from datetime import datetime
import utils

# Page config
st.set_page_config(
    page_title="GA Ticket Management System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "user" not in st.session_state or st.session_state.user is None:
    login.login_screen()
    st.stop()

# Load tickets if not in session
if 'tickets_df' not in st.session_state:
    st.session_state.tickets_df = utils.load_tickets()

st.title("🎫 General Affairs Ticket Management System")
st.markdown("Submit and track service requests for the General Affairs Division")

tab1, tab2 = st.tabs(["📝 Submit Ticket", "🔍 Track Ticket"])

with tab1:
    st.subheader("Submit a New Ticket")
    with st.form("ticket_submission_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title *")
            category = st.selectbox("Category *", options=utils.get_ticket_categories())
            priority = st.select_slider("Priority *", options=["Low", "Medium", "High", "Urgent"], value="Medium")
        with col2:
            requester_name = st.text_input("Your Name *")
            requester_email = st.text_input("Your Email *")
            department = st.text_input("Department *")
        description = st.text_area("Description *", height=150)

        submitted = st.form_submit_button("Submit Ticket")

    if submitted:
        required = {
            "Title": title, "Category": category, "Priority": priority,
            "Name": requester_name, "Email": requester_email,
            "Department": department, "Description": description
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            st.error(f"Missing required fields: {', '.join(missing)}")
        else:
            ticket_data = {
                "ticket_id": utils.generate_ticket_id(),
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "status": "Pending",
                "requester_name": requester_name,
                "requester_email": requester_email,
                "department": department,
                "submit_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "updated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "update_notes": ""
            }
            ticket_id = utils.save_ticket(ticket_data)
            st.success(f"Ticket submitted! Your ticket ID is `{ticket_id}`")
            with st.expander("View Ticket Details"):
                st.json(ticket_data)

with tab2:
    st.subheader("Track Your Ticket")
    ticket_id_input = st.text_input("Enter your ticket ID")
    if st.button("Check Status") and ticket_id_input:
        ticket = utils.get_ticket_by_id(ticket_id_input)
        if ticket:
            with st.expander("Ticket Details", expanded=True):
                st.write(f"**ID:** {ticket['ticket_id']}")
                st.write(f"**Title:** {ticket['title']}")
                st.write(f"**Category:** {ticket['category']}")
                st.write(f"**Status:** {ticket['status']}")
                st.write(f"**Priority:** {ticket['priority']}")
                st.write(f"**Submitted:** {ticket['submit_date']}")
                st.write(f"**Requester:** {ticket['requester_name']} ({ticket['department']})")
                st.write("**Description:**")
                st.write(ticket['description'])
                if ticket.get('update_notes'):
                    st.write("**Update Notes:**")
                    for line in ticket['update_notes'].split("\n"):
                        st.markdown(f"- {line}")
        else:
            st.error(f"No ticket found with ID: `{ticket_id_input}`")

# Admin Login button
st.sidebar.title("🔐 Admin Access")

if "user" in st.session_state and st.session_state.user is not None:
    st.sidebar.write(f"👤 Logged in sebagai: {st.session_state.user['full_name']} ({st.session_state.user['role']})")
    if st.sidebar.button("Logout"):
        login.logout()
        st.experimental_rerun()

if st.sidebar.button("Login as Admin"):
    st.switch_page("pages/admin_dashboard.py")
