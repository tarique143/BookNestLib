# file: pages/3_🗂️_Category_Management.py
import streamlit as st
import pandas as pd
import requests
from services.api_client import get_data, post_data, get_auth_headers, BASE_URL

st.set_page_config(layout="wide", page_title="Category Management")
if not st.session_state.get("is_authenticated", False): st.error("Please log in."); st.stop()
st.title("🗂️ Category & Subcategory Management")

@st.cache_data(ttl=30)
def load_data():
    cats, c_err = get_data("/api/categories/")
    subcats, s_err = get_data("/api/subcategories/")
    return cats, c_err, subcats, s_err

categories, cat_error, subcategories, sub_error = load_data()
if cat_error or sub_error: st.error("Could not load data."); st.stop()

tab1, tab2 = st.tabs(["📁 Manage Categories", "📂 Manage Subcategories"])

# --- TAB 1: CATEGORY MANAGEMENT ---
with tab1:
    st.header("Categories")
    with st.expander("➕ Add New Category"):
        with st.form("add_cat_form", clear_on_submit=True):
            cat_name = st.text_input("Category Name *")
            cat_desc = st.text_area("Description")
            if st.form_submit_button("Add Category", type="primary"):
                if cat_name:
                    res, err = post_data("/api/categories/", {"name": cat_name, "description": cat_desc})
                    if err: st.error(f"Failed: {err}")
                    else: st.success("Added!"); st.cache_data.clear(); st.rerun()
                else: st.warning("Name is required.")

    st.subheader("Existing Categories")
    if categories:
        for cat in categories:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"**{cat['name']}** (ID: {cat['id']})")
                if c2.button("Edit", key=f"edit_cat_{cat['id']}"): st.session_state.editing_id = f"cat_{cat['id']}"
                if c3.button("Delete", key=f"del_cat_{cat['id']}", type="primary"):
                    response = requests.delete(f"{BASE_URL}/api/categories/{cat['id']}", headers=get_auth_headers())
                    if response.ok: st.success("Deleted!"); st.cache_data.clear(); st.rerun()
                    else: st.error(f"Failed: {response.json().get('detail')}")

                if st.session_state.get('editing_id') == f"cat_{cat['id']}":
                    with st.form(f"edit_form_{cat['id']}"):
                        new_name = st.text_input("New Name", value=cat['name'])
                        new_desc = st.text_area("New Desc", value=cat.get('description', ''))
                        if st.form_submit_button("Save"):
                            data = {"name": new_name, "description": new_desc}
                            response = requests.put(f"{BASE_URL}/api/categories/{cat['id']}", json=data, headers=get_auth_headers())
                            if response.ok: st.success("Updated!"); del st.session_state.editing_id; st.cache_data.clear(); st.rerun()
                            else: st.error(f"Failed: {response.json().get('detail')}")

# --- TAB 2: SUBCATEGORY MANAGEMENT ---
with tab2:
    st.header("Subcategories")
    with st.expander("➕ Add New Subcategory"):
        with st.form("add_subcat_form", clear_on_submit=True):
            sub_name = st.text_input("Subcategory Name *")
            sub_desc = st.text_area("Subcategory Description")
            if categories:
                cat_options = {cat['name']: cat['id'] for cat in categories}
                selected_cat_name = st.selectbox("Parent Category *", options=cat_options.keys(), index=None)
            else:
                st.warning("Please add a category first.")
                selected_cat_name = None
            if st.form_submit_button("Add Subcategory", type="primary"):
                if not sub_name or not selected_cat_name: st.error("All fields are required.")
                else:
                    data = {"name": sub_name, "description": sub_desc, "category_id": cat_options[selected_cat_name]}
                    res, err = post_data("/api/subcategories/", data)
                    if err: st.error(f"Failed: {err}")
                    else: st.success(f"Subcategory '{res.get('name')}' added!"); st.cache_data.clear(); st.rerun()
    
    st.subheader("Existing Subcategories")
    if subcategories:
        for sub in subcategories:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"**{sub['name']}** in *{sub.get('category', {}).get('name', 'N/A')}* (ID: {sub['id']})")
                if c2.button("Edit", key=f"edit_sub_{sub['id']}"): st.session_state.editing_id = f"sub_{sub['id']}"
                if c3.button("Delete", key=f"del_sub_{sub['id']}", type="primary"):
                    response = requests.delete(f"{BASE_URL}/api/subcategories/{sub['id']}", headers=get_auth_headers())
                    if response.ok: st.success("Deleted!"); st.cache_data.clear(); st.rerun()
                    else: st.error(f"Failed: {response.json().get('detail')}")

                if st.session_state.get('editing_id') == f"sub_{sub['id']}":
                    with st.form(f"edit_form_sub_{sub['id']}"):
                        new_sub_name = st.text_input("New Name", value=sub['name'])
                        new_sub_desc = st.text_area("New Desc", value=sub.get('description', ''))
                        
                        cat_map = {cat['name']: cat['id'] for cat in categories}
                        parent_names = list(cat_map.keys())
                        current_parent = sub.get('category', {}).get('name')
                        try: default_idx = parent_names.index(current_parent)
                        except ValueError: default_idx = 0
                        new_parent_name = st.selectbox("Parent Category", parent_names, index=default_idx)

                        if st.form_submit_button("Save"):
                            data = {"name": new_sub_name, "description": new_sub_desc, "category_id": cat_map[new_parent_name]}
                            response = requests.put(f"{BASE_URL}/api/subcategories/{sub['id']}", json=data, headers=get_auth_headers())
                            if response.ok: st.success("Updated!"); del st.session_state.editing_id; st.cache_data.clear(); st.rerun()
                            else: st.error(f"Failed: {response.json().get('detail')}")