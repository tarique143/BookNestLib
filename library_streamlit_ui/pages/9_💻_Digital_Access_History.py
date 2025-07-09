# file: pages/8_📚_Copies_&_Issuing.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from services.api_client import get_data, post_data, get_auth_headers, BASE_URL

st.set_page_config(layout="wide", page_title="Copies & Issuing")
if not st.session_state.get("is_authenticated", False): st.error("Please log in."); st.stop()
st.title("📚 Book Copies & Issuing System")

@st.cache_data(ttl=30)
def load_data():
    books, b_err = get_data("/api/books/?approved_only=true")
    locations, l_err = get_data("/api/locations/")
    copies, c_err = get_data("/api/copies/")
    users, u_err = get_data("/api/users/")
    issues, i_err = get_data("/api/issues/")
    return books, b_err, locations, l_err, copies, c_err, users, u_err, issues, i_err

books, b_err, locations, l_err, copies, c_err, users, u_err, issues, i_err = load_data()
if any([b_err, l_err, c_err, u_err, i_err]): st.error("Could not load necessary data."); st.stop()

tab1, tab2, tab3 = st.tabs(["Manage Book Copies", "Issue a Book", "Return a Book"])

# --- TAB 1: MANAGE BOOK COPIES ---
with tab1:
    st.header("Add & View Book Copies")
    with st.expander("➕ Add New Copy"):
        with st.form("add_copy_form", clear_on_submit=True):
            book_options = {f"{b['title']} (ID: {b['id']})": b['id'] for b in books} if books else {}
            location_options = {f"{l['name']} (ID: {l['id']})": l['id'] for l in locations} if locations else {}
            selected_book_display = st.selectbox("Select Book *", book_options.keys(), index=None)
            selected_location_display = st.selectbox("Select Location *", location_options.keys(), index=None)
            if st.form_submit_button("Add Copy", type="primary"):
                if not all([selected_book_display, selected_location_display]):
                    st.warning("Please select a book and a location.")
                else:
                    data = {"book_id": book_options[selected_book_display], "location_id": location_options[selected_location_display]}
                    res, err = post_data("/api/copies/", data)
                    if err: st.error(f"Failed: {err}")
                    else: st.success("Copy added!"); st.cache_data.clear(); st.rerun()

    st.subheader("All Book Copies")
    if copies:
        search_query = st.text_input("Search Copies by Book Title", key="copy_search")
        df_copies = pd.DataFrame(copies)
        df_copies['book_title'] = df_copies['book'].apply(lambda x: x.get('title', 'N/A') if x else 'N/A')
        df_copies['location_name'] = df_copies['location'].apply(lambda x: x.get('name', 'N/A') if x else 'N/A')
        
        if search_query:
            df_copies = df_copies[df_copies['book_title'].str.contains(search_query, case=False, na=False)]
        
        st.dataframe(df_copies[['id', 'book_title', 'location_name', 'status']], use_container_width=True, hide_index=True)
    else: st.info("No book copies found.")

# --- TAB 2: ISSUE A BOOK ---
with tab2:
    st.header("Issue a Book to a Client")
    with st.form("issue_book_form", clear_on_submit=True):
        available_copies = [c for c in copies if c.get('status') == 'Available'] if copies else []
        copy_options = {f"Copy ID: {c['id']} ({c.get('book', {}).get('title', 'N/A')})": c['id'] for c in available_copies}
        user_options = {f"{u['username']} (ID: {u['id']})": u['id'] for u in users} if users else {}
        
        selected_copy_display = st.selectbox("Select Available Book Copy *", copy_options.keys(), index=None)
        selected_user_display = st.selectbox("Select Client *", user_options.keys(), index=None)
        due_date = st.date_input("Due Date *", value=datetime.now() + timedelta(days=14))

        if st.form_submit_button("Issue Book", type="primary"):
            if not all([selected_copy_display, selected_user_display]):
                st.warning("Please select both a book copy and a client.")
            else:
                data = {"copy_id": copy_options[selected_copy_display], "client_id": user_options[selected_user_display], "due_date": due_date.isoformat() + "T00:00:00"}
                res, err = post_data("/api/issues/issue", data)
                if err: st.error(f"Failed: {err}")
                else: st.success("Book issued!"); st.cache_data.clear(); st.rerun()

# --- TAB 3: RETURN A BOOK ---
with tab3:
    st.header("Return an Issued Book")
    on_loan_books = [b for b in issues if b.get('status') == 'Issued'] if issues else []

    if not on_loan_books:
        st.info("No books are currently on loan.")
    else:
        df_issued = pd.DataFrame(on_loan_books)
        df_issued['client_username'] = df_issued['client'].apply(lambda x: x.get('username') if x else 'N/A')
        df_issued['book_title'] = df_issued['book_copy'].apply(lambda x: x.get('book', {}).get('title', 'N/A') if x else 'N/A')
        
        st.write("Books Currently On Loan:")
        st.dataframe(df_issued[['id', 'client_username', 'book_title', 'copy_id', 'issue_date', 'due_date']], use_container_width=True, hide_index=True)

        return_options = {f"Issue ID: {b['id']} (Book: {b.get('book_copy', {}).get('book',{}).get('title', 'N/A')})": b['id'] for b in on_loan_books}
        selected_issue_display = st.selectbox("Select an Issue to Return", return_options.keys(), index=None)

        if st.button("Mark as Returned", type="primary"):
            if not selected_issue_display:
                st.warning("Please select an issue to return.")
            else:
                issue_id = return_options[selected_issue_display]
                response = requests.post(f"{BASE_URL}/api/issues/return/{issue_id}", headers=get_auth_headers())
                if response.ok:
                    st.success("Book returned!"); st.cache_data.clear(); st.rerun()
                else: st.error(f"Failed: {response.json().get('detail')}")