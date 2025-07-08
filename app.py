# file: app.py
import streamlit as st
from services.api_client import login, logout, get_data

st.set_page_config(layout="wide", page_title="Library Management System")

# Session state ko initialize karna
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False

# --- LOGIN FORM ---
if not st.session_state.is_authenticated:
    st.title("Library Management System Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                with st.spinner("Logging in..."):
                    success, message = login(username, password)
                    if success:
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error(message)

# --- DASHBOARD / MAIN PAGE ---
else:
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}!")
        st.write(f"Role: **{st.session_state.role}**")
        st.divider()
        st.page_link("app.py", label="Dashboard", icon="🏠")
        st.page_link("pages/1_📚_Book_Management.py", label="Book Management", icon="📚")
        st.page_link("pages/2_👥_User_Management.py", label="User Management", icon="👥")
        st.page_link("pages/3_🗂️_Category_Management.py", label="Category Management", icon="🗂️")
        st.page_link("pages/4_🌍_Language_&_Location.py", label="Language & Location", icon="🌍")
        st.page_link("pages/5_🔑_Permission_Management.py", label="Permission Management", icon="🔑")
        st.page_link("pages/6_✅_Approval_Management.py", label="Approval Management", icon="✅")
        st.page_link("pages/7_📜_Audit_Logs.py", label="Audit Logs", icon="📜")
        st.page_link("pages/8_📚_Copies_&_Issuing.py", label="Copies & Issuing", icon="📚")
        st.page_link("pages/9_💻_Digital_Access_History.py", label="Digital Access", icon="💻")
        st.page_link("pages/10_🛡️_Restricted_Books.py", label="Restricted Books", icon="🛡️")

        st.divider()
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

    # Main content
    st.title("🏠 Dashboard")
    st.header("Library System Overview")

    # --- REAL-TIME METRICS ---
    @st.cache_data(ttl=120) # Data ko 2 minutes ke liye cache karein
    def get_dashboard_metrics():
        books, _ = get_data("/api/books/?approved_only=false")
        users, _ = get_data("/api/users/")
        issued, _ = get_data("/api/issues/")
        return books, users, issued

    books, users, issued = get_dashboard_metrics()
    
    total_books = len(books) if books else 0
    total_users = len(users) if users else 0
    issued_count = len([b for b in issued if b.get('status') == 'Issued']) if issued else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Books in System", value=total_books)
    with col2:
        st.metric(label="Total Registered Users", value=total_users)
    with col3:
        st.metric(label="Books Currently on Loan", value=issued_count)
    
    st.divider()
    st.info("Use the navigation panel on the left to manage different parts of the library system.")