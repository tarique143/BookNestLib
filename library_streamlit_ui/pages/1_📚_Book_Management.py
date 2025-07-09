 # file: pages/1_📚_Book_Management.py
import streamlit as st
import pandas as pd
import requests
from services.api_client import get_data, post_data, get_auth_headers, BASE_URL

# Page ka configuration set karein
st.set_page_config(layout="wide", page_title="Book Management")

# --- Authentication Check ---
if not st.session_state.get("is_authenticated", False):
    st.error("Please log in to access this page."); st.stop()

# --- Page Title ---
st.title("📚 Book Management")

# --- Data Fetching (with Caching) ---
@st.cache_data(ttl=60)
def load_all_data():
    books, b_err = get_data("/api/books/?approved_only=false")
    languages, l_err = get_data("/api/languages/")
    subcategories, s_err = get_data("/api/subcategories/")
    return books, b_err, languages, l_err, subcategories, s_err

books, b_err, languages, l_err, subcategories, s_err = load_all_data()

if b_err or l_err or s_err:
    st.error("Could not load necessary data. Please check the API and refresh."); st.stop()

# --- Tabs for Different Actions ---
tab1, tab2, tab3 = st.tabs(["View All Books", "Add New Book", "Edit / Delete Book"])


# --- TAB 1: VIEW ALL BOOKS (with Search) ---
with tab1:
    st.header("All Books in the Library")
    
    if st.button("Refresh Book List"):
        st.cache_data.clear(); st.rerun()

    if books:
        search_query = st.text_input("Search by Title, Author, or ISBN", placeholder="Type here to search...")
        
        df = pd.DataFrame(books)
        
        # Search functionality
        if search_query:
            mask = (
                df['title'].str.contains(search_query, case=False, na=False) |
                df['author'].str.contains(search_query, case=False, na=False) |
                df['isbn'].str.contains(search_query, case=False, na=False)
            )
            df_search = df[mask]
        else:
            df_search = df

        st.dataframe(df_search[['id', 'title', 'author', 'isbn', 'is_approved', 'is_restricted']], use_container_width=True, hide_index=True)
    else:
        st.info("No books found in the library.")


# --- TAB 2: ADD NEW BOOK (Improved) ---
with tab2:
    st.header("Add a New Book")
    # ... (Add New Book ka poora code jaisa pehle tha, usme koi khaas badlav nahi) ...
    # Main isse yahan dobara likh raha hoon for completeness
    uploaded_file = st.file_uploader("Choose a book cover image", type=['png', 'jpg', 'jpeg'])
    if 'cover_image_url' not in st.session_state: st.session_state.cover_image_url = ""
    if uploaded_file is not None:
        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
        with st.spinner('Uploading image...'):
            try:
                response = requests.post(f"{BASE_URL}/api/upload/image", files=files, headers=get_auth_headers())
                response.raise_for_status()
                st.session_state.cover_image_url = response.json().get('url')
                st.success("Image uploaded!"); st.image(uploaded_file, width=200)
            except Exception as e:
                st.error(f"Image upload failed: {e}"); st.session_state.cover_image_url = ""

    with st.form("add_book_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Title *")
            author = st.text_input("Author")
            publisher = st.text_input("Publisher")
            publication_year = st.number_input("Publication Year", 1500, 2099, 2024, 1)
        with col2:
            isbn = st.text_input("ISBN")
            lang_options = {lang['name']: lang['id'] for lang in languages} if languages else {}
            selected_language_name = st.selectbox("Language *", lang_options.keys(), index=None)
            sub_options = {sub['name']: sub['id'] for sub in subcategories} if subcategories else {}
            selected_subcategory_names = st.multiselect("Subcategories", sub_options.keys())
        description = st.text_area("Description")
        
        if st.form_submit_button("Add Book and Create Approval Request", type="primary"):
            if not title or not selected_language_name: st.error("Title and Language are required.")
            else:
                book_data = {
                    "title": title, "author": author, "publisher": publisher,
                    "publication_year": int(publication_year), "isbn": isbn,
                    "language_id": lang_options[selected_language_name],
                    "subcategory_ids": [sub_options[name] for name in selected_subcategory_names],
                    "description": description, "is_digital": False,
                    "is_restricted": False, # Default value for new book
                    "cover_image_url": st.session_state.cover_image_url
                }
                with st.spinner("Processing..."):
                    b_res, b_err = post_data("/api/books/", book_data)
                    if b_err: st.error(f"Failed to add book: {b_err}")
                    else:
                        st.success(f"Book '{b_res.get('title')}' added.")
                        req_res, req_err = post_data("/api/requests/", {"book_id": b_res.get('id')})
                        if req_err: st.warning(f"Book created, but failed to create approval request: {req_err}")
                        else: st.info("Approval request created successfully!")
                        st.session_state.cover_image_url = ""
                        st.cache_data.clear(); st.rerun()

# --- TAB 3: EDIT / DELETE BOOK (Naya Hissa) ---
with tab3:
    st.header("Edit or Delete a Book")
    if not books:
        st.info("No books to edit or delete.")
    else:
        book_map = {f"{b['title']} (ID: {b['id']})": b for b in books}
        selected_book_display = st.selectbox("Select a Book to Modify", options=book_map.keys(), index=None)

        if selected_book_display:
            selected_book = book_map[selected_book_display]
            
            with st.form(f"edit_book_{selected_book['id']}"):
                st.subheader(f"Editing: *{selected_book['title']}*")
                
                # --- Edit Form Fields ---
                title = st.text_input("Title", value=selected_book['title'])
                author = st.text_input("Author", value=selected_book.get('author', ''))
                is_restricted = st.checkbox("Is this a Restricted Book?", value=selected_book.get('is_restricted', False))

                # Yahan aap baaki fields (publisher, isbn, etc.) bhi add kar sakte hain
                
                if st.form_submit_button("Save Changes"):
                    update_data = {
                        "title": title, "author": author, "publisher": selected_book.get('publisher'),
                        "publication_year": selected_book.get('publication_year'), "isbn": selected_book.get('isbn'),
                        "is_digital": selected_book.get('is_digital'), "description": selected_book.get('description'),
                        "cover_image_url": selected_book.get('cover_image_url'),
                        "language_id": selected_book.get('language', {}).get('id'),
                        "subcategory_ids": [sub['id'] for sub in selected_book.get('subcategories', [])],
                        "is_restricted": is_restricted
                    }
                    with st.spinner("Saving..."):
                        response = requests.put(f"{BASE_URL}/api/books/{selected_book['id']}", json=update_data, headers=get_auth_headers())
                        if response.ok:
                            st.success("Book updated!"); st.cache_data.clear(); st.rerun()
                        else: st.error(f"Update failed: {response.json().get('detail')}")

            # --- Delete Section ---
            st.divider()
            st.subheader("Delete Book")
            if st.checkbox("Show Delete Option", key=f"del_book_{selected_book['id']}"):
                st.error("Warning: This will permanently soft-delete the book.")
                if st.button("DELETE This Book Permanently", type="primary"):
                    with st.spinner("Deleting..."):
                        response = requests.delete(f"{BASE_URL}/api/books/{selected_book['id']}", headers=get_auth_headers())
                        if response.status_code == 204:
                            st.success("Book deleted!"); st.cache_data.clear(); st.rerun()
                        else: st.error(f"Deletion failed: {response.json().get('detail')}")