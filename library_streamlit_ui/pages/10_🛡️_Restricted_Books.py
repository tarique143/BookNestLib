# file: pages/10_🛡️_Restricted_Books.py
import streamlit as st
import pandas as pd
import requests
from services.api_client import get_data, post_data, get_auth_headers, BASE_URL

st.set_page_config(layout="wide", page_title="Restricted Book Permissions")
if not st.session_state.get("is_authenticated", False): st.error("Please log in."); st.stop()
st.title("🛡️ Manage Access for Restricted Books")
st.info("Grant specific users or roles permission to view books marked as 'Restricted'.")

# --- Data Fetching ---
@st.cache_data(ttl=30)
def load_data():
    all_books, b_err = get_data("/api/books/?approved_only=true")
    users, u_err = get_data("/api/users/")
    roles, r_err = get_data("/api/users/roles/")
    return all_books, b_err, users, u_err, roles, r_err

all_books, b_err, users, u_err, roles, r_err = load_data()
if any([b_err, u_err, r_err]): st.error("Could not load data."); st.stop()

restricted_books = [b for b in all_books if b.get('is_restricted')]

if not restricted_books:
    st.warning("**No Restricted Books Found.**\n\nTo use this feature, first mark a book as 'restricted' from the 'Edit / Delete Book' tab in the Book Management page.")
    st.stop()

# --- Main UI ---
book_options = {f"{b['title']} (ID: {b['id']})": b for b in restricted_books}
selected_book_display = st.selectbox("Select a Restricted Book to Manage", options=book_options.keys(), index=None)

if selected_book_display:
    selected_book = book_options[selected_book_display]
    book_id = selected_book['id']
    st.header(f"Permissions for: *{selected_book['title']}*")
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Assign New Permission")
        assign_to = st.radio("Assign to:", ["A Specific User", "An Entire Role"], key=f"assign_type_{book_id}", horizontal=True)
        
        with st.form("assign_perm_form", clear_on_submit=True):
            user_id, role_id = None, None
            if assign_to == "A Specific User" and users:
                user_map = {f"{u['username']} (ID: {u['id']})": u['id'] for u in users}
                selected_user = st.selectbox("Select User", user_map.keys(), index=None)
                user_id = user_map.get(selected_user)
            if assign_to == "An Entire Role" and roles:
                role_map = {f"{r['name']} (ID: {r['id']})": r['id'] for r in roles}
                selected_role = st.selectbox("Select Role", role_map.keys(), index=None)
                role_id = role_map.get(selected_role)

            if st.form_submit_button("Assign Permission", type="primary"):
                if not user_id and not role_id: st.warning("Please select a user or a role.")
                else:
                    data = {"book_id": book_id, "user_id": user_id, "role_id": role_id}
                    res, err = post_data("/api/book-permissions/", data)
                    if err: st.error(f"Failed: {err}")
                    else: st.success("Permission assigned!"); st.cache_data.clear(); st.rerun()

    with col2:
        st.subheader("Current Permissions")
        permissions, p_err = get_data(f"/api/book-permissions/book/{book_id}")
        if p_err: st.error("Could not load permissions.")
        elif permissions:
            df = pd.DataFrame(permissions)
            
            # User aur Role ke naam laane ke liye mappings
            user_id_to_name = {u['id']: u['username'] for u in users}
            role_id_to_name = {r['id']: r['name'] for r in roles}

            df['Assigned To'] = df.apply(lambda row: user_id_to_name.get(row['user_id']) if pd.notna(row['user_id']) else f"Role: {role_id_to_name.get(row['role_id'])}", axis=1)
            
            st.write("Click a button to revoke permission:")
            for index, row in df.iterrows():
                perm_id = row['id']
                perm_desc = row['Assigned To']
                if st.button(f"Revoke from: {perm_desc}", key=f"revoke_{perm_id}", use_container_width=True):
                    with st.spinner("Revoking..."):
                        response = requests.delete(f"{BASE_URL}/api/book-permissions/{perm_id}", headers=get_auth_headers())
                        if response.ok:
                            st.success("Permission revoked!"); st.cache_data.clear(); st.rerun()
                        else: st.error(f"Failed: {response.json().get('detail')}")
        else:
            st.info("No special permissions assigned to this book yet.")