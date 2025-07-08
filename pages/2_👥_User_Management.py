# file: pages/2_👥_User_Management.py
import streamlit as st
import pandas as pd
import requests
from services.api_client import get_data, post_data, get_auth_headers, BASE_URL

# Page ka configuration set karein
st.set_page_config(layout="wide", page_title="User Management")

# --- Authentication Check ---
if not st.session_state.get("is_authenticated", False):
    st.error("Please log in to access this page."); st.stop()

st.title("👥 User & Role Management")

# --- Data Fetching (with Caching) ---
@st.cache_data(ttl=60)
def load_data():
    users, u_err = get_data("/api/users/")
    roles, r_err = get_data("/api/users/roles/")
    return users, u_err, roles, r_err

users, user_error, roles, role_error = load_data()

if user_error or role_error:
    st.error("Could not load initial data. Please check API connection and permissions."); st.stop()

# --- Naya Layout: 3 TABS ---
tab1, tab2, tab3 = st.tabs(["View / Edit Users", "Add New User", "Manage Roles"])


# --- TAB 1: VIEW / EDIT USERS ---
with tab1:
    st.header("All Registered Users")
    if st.button("Refresh User List"):
        st.cache_data.clear(); st.rerun()

    if users:
        search_query = st.text_input("Search by Name, Username, or Email", placeholder="Type here to search...")
        
        df = pd.DataFrame(users)
        
        if search_query:
            mask = (df['fullName'].str.contains(search_query, case=False, na=False) |
                    df['username'].str.contains(search_query, case=False, na=False) |
                    df['email'].str.contains(search_query, case=False, na=False))
            df_search = df[mask]
        else:
            df_search = df

        df_search['role_name'] = df_search['role'].apply(lambda r: r.get('name', 'N/A') if isinstance(r, dict) else 'N/A')
        st.dataframe(df_search[['id', 'fullName', 'username', 'email', 'role_name', 'status']], use_container_width=True, hide_index=True)
    else:
        st.info("No users found.")
    
    # Inline Edit/Delete Section
    st.divider()
    st.subheader("Modify a User")
    if users:
        user_map = {f"{u['username']} (ID: {u['id']})": u for u in users}
        selected_user_display = st.selectbox("Select a User to Modify", options=user_map.keys(), index=None)

        if selected_user_display:
            selected_user = user_map[selected_user_display]
            with st.form(f"edit_user_{selected_user['id']}"):
                st.write(f"**Editing:** {selected_user['username']}")
                fullName = st.text_input("Full Name", value=selected_user.get('fullName', ''))
                st.text_input("Username (cannot be changed)", value=selected_user['username'], disabled=True)
                st.text_input("Email (cannot be changed)", value=selected_user['email'], disabled=True)
                
                role_map = {role['name']: role['id'] for role in roles}
                role_names = list(role_map.keys())
                current_role = selected_user.get('role', {}).get('name')
                try: default_idx = role_names.index(current_role)
                except: default_idx = 0
                selected_role_name = st.selectbox("Role", options=role_names, index=default_idx)

                status_options = ["Active", "Inactive", "Suspended"]
                current_status = selected_user.get('status', 'Active')
                try: default_status_idx = status_options.index(current_status)
                except: default_status_idx = 0
                selected_status = st.selectbox("Status", options=status_options, index=default_status_idx)

                if st.form_submit_button("Save Changes"):
                    st.warning("Edit User requires a `PUT /api/users/{id}` endpoint.")

            if st.button("DELETE This User", type="primary", key=f"del_user_{selected_user['id']}"):
                st.warning("Delete User requires a `DELETE /api/users/{id}` endpoint.")

# --- TAB 2: ADD NEW USER ---
with tab2:
    st.header("Add a New User")
    with st.form("add_user_form", clear_on_submit=True):
        fullName = st.text_input("Full Name")
        username = st.text_input("Username *")
        email = st.text_input("Email *")
        password = st.text_input("Password *", type="password")
        role_options = {role['name']: role['id'] for role in roles} if roles else {}
        selected_role_name = st.selectbox("Assign Role *", options=role_options.keys(), index=None)
        if st.form_submit_button("Add User", type="primary"):
            if not all([username, email, password, selected_role_name]):
                st.error("Please fill all required fields.")
            else:
                user_data = {"fullName": fullName, "username": username, "email": email, "password": password, "role_id": role_options[selected_role_name]}
                with st.spinner("Creating..."):
                    res, err = post_data("/api/users/", user_data)
                    if err: st.error(f"Failed: {err}")
                    else: st.success(f"User '{res.get('username')}' created!"); st.cache_data.clear(); st.rerun()

# --- TAB 3: MANAGE ROLES ---
with tab3:
    st.header("Manage Roles")
    with st.expander("➕ Add New Role"):
        with st.form("add_role_form", clear_on_submit=True):
            role_name = st.text_input("New Role Name *")
            if st.form_submit_button("Create Role", type="primary"):
                if role_name:
                    res, err = post_data("/api/users/roles/", {"name": role_name})
                    if err: st.error(f"Failed: {err}")
                    else: st.success(f"Role '{res.get('name')}' created!"); st.cache_data.clear(); st.rerun()
                else: st.warning("Role name cannot be empty.")

    st.subheader("Existing Roles")
    if roles:
        for role in roles:
            if role['name'].lower() in ['admin', 'librarian']:
                st.markdown(f"- **{role['name']}** (ID: {role['id']}) - `Core Role`")
            else:
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"- **{role['name']}** (ID: {role['id']})")
                if c2.button("Delete", key=f"del_role_{role['id']}", type="primary"):
                    st.warning("Delete Role requires a backend endpoint.")
    else:
        st.info("No roles found.")