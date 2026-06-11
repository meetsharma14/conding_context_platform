import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(
    page_title="Admin Panel",
    page_icon="🔐",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ==========================
# SESSION STATE
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None

def get_auth_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def handle_api_response(response):
    if response.status_code in [200, 201]:
        return response.json()
    else:
        try:
            error_detail = response.json().get("detail", response.text)
        except:
            error_detail = response.text
        st.error(f"Error {response.status_code}: {error_detail}")
        return None

# ==========================
# ADMIN LOGIN
# ==========================

def admin_login():
    st.header("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        payload = {
            "username": username,
            "password": password,
            "requested_role": "admin"
        }

        try:
            r = requests.post(f"{API_BASE_URL}/users/login", json=payload, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.session_state.logged_in = True
                
                st.success("Admin logged in successfully!")
                st.rerun()
            else:
                error_msg = r.json().get("detail", "Login failed")
                st.error(error_msg)
        except Exception as e:
            st.error(f"Error: {e}")

def logout():
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.role = None
    st.rerun()

# ==========================
# ADMIN PAGES
# ==========================

def admin_dashboard():
    st.subheader("System Statistics")
    
    try:
        headers = get_auth_headers()
        prob_res = requests.get(f"{API_BASE_URL}/problems/", headers=headers, timeout=10)
        sub_res = requests.get(f"{API_BASE_URL}/submissions/", headers=headers, timeout=10)

        total_probs = len(prob_res.json()) if prob_res.status_code == 200 else 0
        total_subs = len(sub_res.json()) if sub_res.status_code == 200 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Problems", total_probs)
        col2.metric("Submissions", total_subs)
        col3.metric("Status", "Online")

    except Exception as e:
        st.error(str(e))

def manage_problems():
    st.subheader("Problem Management")
    
    tab1, tab2 = st.tabs(["Add Problem", "Manage Problems"])
    
    headers = get_auth_headers()

    with tab1:
        title = st.text_input("Problem Title")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        description = st.text_area("Description")
        sample_input = st.text_area("Sample Input")
        sample_output = st.text_area("Sample Output")

        if st.button("Add Problem"):
            payload = {
                "title": title,
                "difficulty": difficulty,
                "description": description,
                "sample_input": sample_input,
                "sample_output": sample_output
            }

            r = requests.post(
                f"{API_BASE_URL}/problems/",
                json=payload,
                headers=headers,
                timeout=10
            )

            if r.status_code in [200, 201]:
                st.success("Problem Added")
            else:
                st.error(r.text)

    with tab2:
        r = requests.get(f"{API_BASE_URL}/problems/", headers=headers, timeout=10)

        if r.status_code == 200:
            problems = r.json()
            st.dataframe(pd.DataFrame(problems), use_container_width=True)

            del_id = st.number_input("Enter ID to Delete", min_value=1, step=1)

            if st.button("Delete Problem"):
                del_res = requests.delete(
                    f"{API_BASE_URL}/problems/{del_id}",
                    headers=headers,
                    timeout=10
                )

                if del_res.status_code == 200:
                    st.success("Problem Deleted Successfully")
                    st.rerun()
                else:
                    st.error(del_res.text)
        else:
            st.error(r.text)

def manage_users():
    st.subheader("User Management")
    
    headers = get_auth_headers()
    r = requests.get(f"{API_BASE_URL}/users/", headers=headers, timeout=10)

    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error(r.text)

def view_submissions():
    st.subheader("All Submissions")
    
    headers = get_auth_headers()
    r = requests.get(f"{API_BASE_URL}/submissions/", headers=headers, timeout=10)

    if r.status_code == 200:
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)
    else:
        st.error(r.text)

# ==========================
# MAIN ROUTING
# ==========================

def main():
    st.sidebar.title("🔐 Admin Panel")

    if not st.session_state.logged_in:
        admin_login()
    else:
        st.sidebar.success(f"✅ Logged in as Admin")
        choice = st.sidebar.radio("Admin Menu", ["Dashboard", "Problems", "Users", "Submissions", "Logout"])
        
        st.title("Admin Management System")
        
        if choice == "Dashboard":
            admin_dashboard()
        elif choice == "Problems":
            manage_problems()
        elif choice == "Users":
            manage_users()
        elif choice == "Submissions":
            view_submissions()
        elif choice == "Logout":
            logout()

if __name__ == "__main__":
    main()