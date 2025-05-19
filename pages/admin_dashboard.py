import streamlit as st
import pandas as pd
import sys, os
from datetime import datetime
import plotly.express as px
import utils

# Simulasi login (gunakan session_state di implementasi sesungguhnya)
st.set_page_config(page_title="Admin Dashboard", layout="wide")
st.title("Admin Dashboard - GA Ticket Management System")

# Load data (gunakan utils.load_tickets() di produksi)
@st.cache_data
def load_data():
    return pd.read_csv("sample_tickets.csv", parse_dates=["submit_date"])

df = load_data()

# Sidebar - Admin Info Dummy
st.sidebar.header("Admin Info")
st.sidebar.write("Name: Admin User")
st.sidebar.write("Role: Admin")
st.sidebar.write("Dept: IT")
st.sidebar.markdown("---")

# Sidebar - Filters
st.sidebar.subheader("Filters")
category_filter = st.sidebar.selectbox("Filter by Category", ["All"] + sorted(df["category"].unique()))
status_filter = st.sidebar.selectbox("Filter by Status", ["All"] + sorted(df["status"].unique()))
start_date = st.sidebar.date_input("Start Date", df["submit_date"].min().date())
end_date = st.sidebar.date_input("End Date", df["submit_date"].max().date())

# Apply Filters
filtered_df = df.copy()
if category_filter != "All":
    filtered_df = filtered_df[filtered_df["category"] == category_filter]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df["status"] == status_filter]
filtered_df = filtered_df[
    (filtered_df["submit_date"] >= pd.to_datetime(start_date)) & 
    (filtered_df["submit_date"] <= pd.to_datetime(end_date))
]

# Search
search = st.sidebar.text_input("Search")
if search:
    filtered_df = filtered_df[filtered_df["title"].str.contains(search, case=False, na=False)]

# Export
st.sidebar.subheader("Export")
export_format = st.sidebar.radio("Format", ["CSV", "Excel"])
if st.sidebar.button("Export Data"):
    if export_format == "CSV":
        st.download_button("Download CSV", filtered_df.to_csv(index=False), file_name="tickets_export.csv", mime="text/csv")
    else:
        from io import BytesIO
        towrite = BytesIO()
        filtered_df.to_excel(towrite, index=False, sheet_name='Tickets')
        towrite.seek(0)
        st.download_button("Download Excel", towrite, file_name="tickets_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total", len(df))
col2.metric("Pending", len(df[df["status"] == "Pending"]))
col3.metric("In Progress", len(df[df["status"] == "In Progress"]))
col4.metric("Completed", len(df[df["status"] == "Completed"]))

# Chart
st.subheader("Ticket Trends")
trend_data = df.copy()
trend_data["submit_date"] = trend_data["submit_date"].dt.date
chart_df = trend_data.groupby(["submit_date", "status"]).size().reset_index(name="count")
fig = px.bar(chart_df, x="submit_date", y="count", color="status", title="Tickets Over Time")
st.plotly_chart(fig, use_container_width=True)

# Pagination
items_per_page = st.selectbox("Items per page", [10, 25, 50], index=0)
page = st.number_input("Page", min_value=1, max_value=(len(filtered_df) - 1)//items_per_page + 1, value=1)
start = (page - 1) * items_per_page
end = start + items_per_page
paginated_df = filtered_df.iloc[start:end]

# Display Table
st.subheader("Filtered Tickets")
selected = st.multiselect("Select tickets to delete or bulk update:", paginated_df["ticket_id"])
st.dataframe(paginated_df, use_container_width=True)

# Bulk update
st.subheader("Bulk Update")
bulk_status = st.selectbox("New status", ["Pending", "In Progress", "Completed", "Rejected"])
bulk_notes = st.text_area("Update notes (applied to all selected)")
if st.button("Apply Bulk Update"):
    if selected and bulk_notes:
        df.loc[df["ticket_id"].isin(selected), "status"] = bulk_status
        df.loc[df["ticket_id"].isin(selected), "update_notes"] = bulk_notes
        st.success("Tickets updated.")
    else:
        st.error("Select tickets and provide update notes.")

# Delete selected
if st.button("Delete Selected"):
    if selected:
        df = df[~df["ticket_id"].isin(selected)]
        st.success("Selected tickets deleted.")
    else:
        st.warning("No tickets selected.")

# Dummy login history
st.sidebar.markdown("---")
st.sidebar.subheader("Login History")
st.sidebar.write("- 2025-05-18 10:00:01 - Login OK")
st.sidebar.write("- 2025-05-17 18:45:22 - Logout")
st.sidebar.write("- 2025-05-17 08:12:45 - Login OK")

# Refresh data
if st.sidebar.button("Refresh"):
    st.rerun()
