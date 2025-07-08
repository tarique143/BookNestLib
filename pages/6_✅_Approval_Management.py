# file: pages/6_✅_Approval_Management.py
import streamlit as st
import pandas as pd
import requests
from services.api_client import get_data, get_auth_headers, BASE_URL

# Page ka configuration set karein
st.set_page_config(layout="wide", page_title="Approval Management")

# --- Authentication Check ---
if not st.session_state.get("is_authenticated", False):
    st.error("Please log in to access this page.")
    st.stop()

# --- Page Title ---
st.title("✅ Book Upload Approval Requests")

# --- Data Fetching (with Caching) ---
@st.cache_data(ttl=30)
def load_requests():
    reqs, err = get_data("/api/requests/")
    return reqs, err

requests_data, error = load_requests()

if error:
    st.error(f"Failed to fetch approval requests: {error}")
    st.stop()

# --- Tabs for Pending and Reviewed Requests ---
tab1, tab2 = st.tabs(["⏳ Pending Requests", "🗄️ Reviewed Requests"])

# --- TAB 1: PENDING REQUESTS ---
with tab1:
    st.header("Requests Awaiting Review")
    
    if not requests_data:
        st.info("No approval requests found.")
    else:
        pending_requests = [r for r in requests_data if r.get('status') == 'Pending'] if requests_data else []
        
        if not pending_requests:
            st.success("👍 All caught up! No requests are pending review.")
        else:
            for request in pending_requests:
                # Nested data ko safely access karein
                book = request.get('book', {}) or {}
                submitted_by = request.get('submitted_by', {}) or {}
                
                with st.container(border=True):
                    col1, col2 = st.columns([1, 3])
                    
                    # Column 1: Cover Image and Action Buttons
                    with col1:
                        if book.get('cover_image_url'):
                            st.image(f"{BASE_URL}{book['cover_image_url']}", use_column_width=True)
                        else:
                            st.image("https://placehold.co/300x400?text=No+Cover", use_column_width=True)
                        
                        # --- Approve Button Logic ---
                        if st.button("Approve", key=f"approve_{request['id']}", type="primary", use_container_width=True):
                            with st.spinner("Approving..."):
                                review_data = {"status": "Approved", "remarks": "Approved via UI"}
                                response = requests.put(f"{BASE_URL}/api/requests/{request['id']}/review", json=review_data, headers=get_auth_headers())
                                if response.ok:
                                    st.success("Book Approved!")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {response.json().get('detail', 'Unknown error')}")

                        # --- Reject Button Logic ---
                        if st.button("Reject", key=f"reject_{request['id']}", use_container_width=True):
                            st.session_state.rejecting_id = request.get('id')
                            st.rerun() # Taaki rejection form dikhe

                        # Rejection form (modal jaisa feel dega)
                        if st.session_state.get('rejecting_id') == request.get('id'):
                             with st.form(f"reject_form_{request['id']}"):
                                st.error("Please provide a reason for rejection below.")
                                remarks = st.text_area("Reason for Rejection (Optional)")
                                if st.form_submit_button("Confirm Rejection", type="primary"):
                                    with st.spinner("Rejecting..."):
                                        review_data = {"status": "Rejected", "remarks": remarks}
                                        response = requests.put(f"{BASE_URL}/api/requests/{request['id']}/review", json=review_data, headers=get_auth_headers())
                                        if response.ok:
                                            st.warning("Book Rejected!")
                                            del st.session_state.rejecting_id
                                            st.cache_data.clear()
                                            st.rerun()
                                        else:
                                            st.error(f"Failed: {response.json().get('detail', 'Unknown error')}")


                    # Column 2: Book Details
                    with col2:
                        st.subheader(book.get('title', 'No Title'))
                        st.caption(f"Author: {book.get('author', 'N/A')} | ISBN: {book.get('isbn', 'N/A')}")
                        st.markdown(f"**Description:**\n\n{book.get('description', 'No description provided.')}")
                        st.divider()
                        st.text(f"Request ID: {request['id']} | Submitted by: {submitted_by.get('username', 'N/A')}")

# --- TAB 2: REVIEWED REQUESTS ---
with tab2:
    st.header("Completed Reviews")
    if not requests_data:
        st.info("No requests found.")
    else:
        reviewed_requests = [r for r in requests_data if r.get('status') != 'Pending'] if requests_data else []
        if not reviewed_requests:
            st.info("No requests have been reviewed yet.")
        else:
            # Data ko display karne se pehle use saaf karein
            processed_data = []
            for r in reviewed_requests:
                processed_data.append({
                    'id': r.get('id'),
                    'book_title': r.get('book', {}).get('title', 'N/A') if r.get('book') else 'N/A',
                    'status': r.get('status'),
                    'remarks': r.get('remarks'),
                    'submitted_by': r.get('submitted_by', {}).get('username', 'N/A') if r.get('submitted_by') else 'N/A',
                    'reviewed_by': r.get('reviewed_by', {}).get('username', 'N/A') if r.get('reviewed_by') else 'N/A',
                    'reviewed_at': r.get('reviewed_at')
                })
            
            df = pd.DataFrame(processed_data)
            st.dataframe(df, use_container_width=True, hide_index=True)