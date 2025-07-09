# file: pages/4_🌍_Language_&_Location.py
import streamlit as st
import pandas as pd
import requests
from services.api_client import get_data, post_data, get_auth_headers, BASE_URL

st.set_page_config(layout="wide", page_title="Settings")
if not st.session_state.get("is_authenticated", False): st.error("Please log in."); st.stop()
st.title("🌍 Languages & Locations")

@st.cache_data(ttl=60)
def load_data():
    langs, l_err = get_data("/api/languages/")
    locs, loc_err = get_data("/api/locations/")
    return langs, l_err, locs, loc_err

languages, lang_error, locations, loc_error = load_data()
if lang_error or loc_error: st.error("Could not load data."); st.stop()

tab1, tab2 = st.tabs(["🌐 Manage Languages", "📍 Manage Locations"])

# --- TAB 1: LANGUAGE MANAGEMENT ---
with tab1:
    st.header("Languages")
    with st.expander("➕ Add New Language"):
        with st.form("add_lang_form", clear_on_submit=True):
            name = st.text_input("Language Name *")
            desc = st.text_area("Description")
            if st.form_submit_button("Add Language", type="primary"):
                if name:
                    res, err = post_data("/api/languages/", {"name": name, "description": desc})
                    if err: st.error(f"Failed: {err}")
                    else: st.success("Added!"); st.cache_data.clear(); st.rerun()
                else: st.warning("Name is required.")
    
    st.subheader("Existing Languages")
    if languages:
        for lang in languages:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"**{lang['name']}** (ID: {lang['id']})")
                if c2.button("Edit", key=f"edit_lang_{lang['id']}"): st.session_state.editing_id = f"lang_{lang['id']}"
                if c3.button("Delete", key=f"del_lang_{lang['id']}", type="primary"):
                    st.warning("Delete functionality for Language requires a backend endpoint.")
                
                if st.session_state.get('editing_id') == f"lang_{lang['id']}":
                    with st.form(f"edit_form_lang_{lang['id']}"):
                        new_name = st.text_input("New Name", value=lang['name'])
                        new_desc = st.text_area("New Desc", value=lang.get('description', ''))
                        if st.form_submit_button("Save"):
                            st.warning("Edit functionality for Language requires a backend endpoint.")

# --- TAB 2: LOCATION MANAGEMENT ---
with tab2:
    st.header("Locations")
    with st.expander("➕ Add New Location"):
        with st.form("add_loc_form", clear_on_submit=True):
            loc_name = st.text_input("Location Name * (e.g., Main Hall - Shelf S2)")
            loc_room = st.text_input("Room Name")
            loc_shelf = st.text_input("Shelf Number")
            loc_section = st.text_input("Section Name")
            loc_desc = st.text_area("Description")
            if st.form_submit_button("Add Location", type="primary"):
                if loc_name:
                    data = {"name": loc_name, "room_name": loc_room, "shelf_number": loc_shelf, "section_name": loc_section, "description": loc_desc}
                    res, err = post_data("/api/locations/", data)
                    if err: st.error(f"Failed: {err}")
                    else: st.success("Added!"); st.cache_data.clear(); st.rerun()
                else: st.warning("Name is required.")

    st.subheader("Existing Locations")
    if locations:
        for loc in locations:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.write(f"**{loc['name']}** (ID: {loc['id']})")
                if c2.button("Edit", key=f"edit_loc_{loc['id']}"): st.session_state.editing_id = f"loc_{loc['id']}"
                if c3.button("Delete", key=f"del_loc_{loc['id']}", type="primary"):
                     st.warning("Delete functionality for Location requires a backend endpoint.")

                if st.session_state.get('editing_id') == f"loc_{loc['id']}":
                    with st.form(f"edit_form_loc_{loc['id']}"):
                        new_name = st.text_input("New Name", value=loc['name'])
                        new_room = st.text_input("Room", value=loc.get('room_name', ''))
                        new_shelf = st.text_input("Shelf", value=loc.get('shelf_number', ''))
                        new_section = st.text_input("Section", value=loc.get('section_name', ''))
                        new_desc = st.text_area("New Desc", value=loc.get('description', ''))
                        if st.form_submit_button("Save"):
                            st.warning("Edit functionality for Location requires a backend endpoint.")