# file: pages/7_📜_Audit_Logs.py
import streamlit as st
import pandas as pd
from services.api_client import get_data

st.set_page_config(layout="wide", page_title="Audit Logs")

if not st.session_state.get("is_authenticated", False):
    st.error("Please log in to access this page."); st.stop()

st.title("📜 System Audit Logs")
st.info("This page shows a record of all important activities performed in the system.")

# --- Filters ---
st.sidebar.header("Filter Logs")
selected_user = st.sidebar.text_input("Filter by Username")
selected_action = st.sidebar.text_input("Filter by Action Type")

# --- Data Fetching ---
@st.cache_data(ttl=60)
def load_logs():
    logs, err = get_data("/api/logs/")
    return logs, err

logs, error = load_logs()

if error:
    st.error(f"Failed to fetch logs: {error}")
elif logs:
    df = pd.DataFrame(logs)
    
    # Process nested data
    df['action_by'] = df['action_by'].apply(lambda x: x.get('username') if isinstance(x, dict) else 'System')
    
    # Apply filters
    if selected_user:
        df = df[df['action_by'].str.contains(selected_user, case=False, na=False)]
    if selected_action:
        df = df[df['action_type'].str.contains(selected_action, case=False, na=False)]

    # --- Pagination ---
    if not df.empty:
        items_per_page = 20
        total_items = len(df)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Initialize page number in session state
        if 'log_page_number' not in st.session_state:
            st.session_state.log_page_number = 1
        
        page_number = st.session_state.log_page_number
        
        # Display controls
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            if st.button("⬅️ Previous Page", disabled=(page_number <= 1)):
                st.session_state.log_page_number -= 1
                st.rerun()
        with col2:
            st.write(f"Page {page_number} of {total_pages}")
        with col3:
            if st.button("Next Page ➡️", disabled=(page_number >= total_pages)):
                st.session_state.log_page_number += 1
                st.rerun()

        # Slice dataframe for the current page
        start_idx = (page_number - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = df.iloc[start_idx:end_idx]

        # Reorder columns for better readability
        display_df = paginated_df[['timestamp', 'action_by', 'action_type', 'description', 'target_type', 'target_id']]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No logs found matching the current filters.")

else:
    st.info("No logs found in the system.")