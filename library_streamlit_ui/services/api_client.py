# file: services/api_client.py
import requests
import streamlit as st

# Aapke FastAPI backend ka URL
BASE_URL = "https://library-api-nb4f.onrender.com"

def get_session_state():
    """Streamlit ke session state ko access karta hai."""
    return st.session_state

def login(username, password):
    """Login karke token haasil karta hai."""
    try:
        # Streamlit me data form-encoded format me bhejna padta hai
        response = requests.post(
            f"{BASE_URL}/token",
            data={"grant_type": "password", "username": username, "password": password}
        )
        response.raise_for_status()  # Agar 4xx/5xx error ho toh exception raise karega
        
        data = response.json()
        
        # Token aur user details ko session state me save karein
        session = get_session_state()
        session.token = data.get("access_token")
        session.role = data.get("role")
        session.username = username
        session.is_authenticated = True
        
        return True, None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return False, "Incorrect username or password."
        return False, f"An error occurred: {e.response.json().get('detail', 'Unknown error')}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

def logout():
    """User ko logout karta hai."""
    session = get_session_state()
    keys_to_delete = ["token", "role", "username", "is_authenticated"]
    for key in keys_to_delete:
        if key in session:
            del session[key]

def get_auth_headers():
    """Har request ke liye authentication header banata hai."""
    session = get_session_state()
    token = session.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def get_data(endpoint):
    """Backend se data (GET request) fetch karta hai."""
    try:
        headers = get_auth_headers()
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, str(e)

def post_data(endpoint, data):
    """Backend par data (POST request) bhejta hai."""
    try:
        headers = get_auth_headers()
        response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
         return None, e.response.json().get('detail', str(e))
    except Exception as e:
        return None, str(e)
