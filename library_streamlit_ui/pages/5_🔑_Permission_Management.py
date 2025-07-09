# file: pages/5_🔑_Permission_Management.py
import streamlit as st
import pandas as pd
import requests
from services.api_client import get_data, post_data, get_auth_headers, BASE_URL

st.set_page_config(layout="wide", page_title="Permission Management")
if not st.session_state.get("is_authenticated", False): st.error("Please log in."); st.stop()
st.title("🔑 Role & Permission Management")

@st.cache_data(ttl=30)
def load_data():
    roles, r_err = get_data("/api/users/roles/")
    perms, p_err = get_data("/api/permissions/permissions")
    return roles, r_err, perms, p_err

roles, role_error, permissions, perm_error = load_data()
if role_error or perm_error: st.error("Could not load data."); st.stop()

tab1, tab2 = st.tabs(["⚙️ Manage Permissions", "👥 Assign Permissions to Roles"])

# --- TAB 1: PERMISSION MANAGEMENT ---
with tab1:
    st.header("Define System Permissions")
    with st.expander("➕ Add New Permission"):
        with st.form("add_perm_form", clear_on_submit=True):
            name = st.text_input("Permission Name * (e.g., USER_MANAGE)")
            desc = st.text_input("Description")
            if st.form_submit_button("Add Permission", type="primary"):
                if name:
                    res, err = post_data("/api/permissions/permissions", {"name": name, "description": desc})
                    if err: st.error(f"Failed: {err}")
                    else: st.success("Added!"); st.cache_data.clear(); st.rerun()
                else: st.warning("Name is required.")

    st.subheader("Existing Permissions")
    if permissions:
        for perm in permissions:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"**{perm['name']}** (ID: {perm['id']})")
                if c2.button("Edit", key=f"edit_perm_{perm['id']}"): st.session_state.editing_id = f"perm_{perm['id']}"
                if c3.button("Delete", key=f"del_perm_{perm['id']}", type="primary"):
                    st.warning("Delete for Permission requires a backend endpoint.")

                if st.session_state.get('editing_id') == f"perm_{perm['id']}":
                    with st.form(f"edit_form_perm_{perm['id']}"):
                        new_name = st.text_input("New Name", value=perm['name'])
                        new_desc = st.text_input("New Desc", value=perm.get('description', ''))
                        if st.form_submit_button("Save"):
                            st.warning("Edit for Permission requires a backend endpoint.")

# --- TAB 2: ASSIGN PERMISSIONS TO ROLES ---
with tab2:
    st.header("Assign Permissions to Roles")
    if roles:
        role_map = {role['name']: role for role in roles}
        selected_role_name = st.selectbox("Select a Role to Edit", options=role_map.keys())
        
        if selected_role_name:
            selected_role = role_map[selected_role_name]
            st.subheader(f"Editing permissions for role: **{selected_role_name}**")
            
            # Get current permissions for the role
            current_perms_data, err = get_data(f"/api/permissions/roles/{selected_role['id']}/permissions")
            if err:
                st.error("Could not fetch current permissions for this role.")
            else:
                current_perm_ids = {p['id'] for p in current_perms_data.get('permissions', [])}

                with st.form("assign_perms_form"):
                    perm_options = {p['name']: p['id'] for p in permissions}
                    all_perm_names = list(perm_options.keys())
                    
                    # Create columns for better layout
                    num_columns = 3
                    cols = st.columns(num_columns)
                    
                    # Divide permissions into columns
                    permissions_per_col = (len(all_perm_names) + num_columns - 1) // num_columns
                    
                    selected_permissions = []
                    for i in range(num_columns):
                        with cols[i]:
                            for perm_name in all_perm_names[i*permissions_per_col:(i+1)*permissions_per_col]:
                                perm_id = perm_options[perm_name]
                                # Check if this permission is already assigned
                                is_checked = perm_id in current_perm_ids
                                if st.checkbox(perm_name, value=is_checked, key=f"perm_{selected_role['id']}_{perm_id}"):
                                    selected_permissions.append(perm_id)

                    if st.form_submit_button("Update Permissions", type="primary"):
                        with st.spinner("Updating..."):
                            data = {"permission_ids": selected_permissions}
                            res, err = post_data(f"/api/permissions/roles/{selected_role['id']}/permissions", data)
                            if err: st.error(f"Failed: {err}")
                            else: st.success("Updated!"); st.cache_data.clear(); st.rerun()