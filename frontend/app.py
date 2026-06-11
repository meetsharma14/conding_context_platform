import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(
    page_title="Contest Platform",
    page_icon="🏆",
    initial_sidebar_state="collapsed"
)



# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://conding-context-platform.onrender.com/")

# ==========================
# SESSION STATE & HELPERS
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = "participant"

def get_auth_headers():
    """Helper to return Bearer token headers if logged in."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def handle_api_response(response):
    """Generic error handling for API responses."""
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
# AUTHENTICATION
# ==========================

def login():
    st.header("Login")
    
    # NEW: Add role selection
    role = st.selectbox(
        "Login As",
        ["participant"]
    )

    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # We send the requested role to the backend
        payload = {
            "username": username,
            "password": password,
            "requested_role": role
        }

        try:
            r = requests.post(f"{API_BASE_URL}/users/login", json=payload)
            
            if r.status_code == 200:
                data = r.json()
                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"] # Backend confirms the role
                st.session_state.logged_in = True
                
                st.success(f"Logged in successfully as {data['role']}")
                st.rerun()
            else:
                # If a normal user tries to login as Admin, backend should return 403
                error_msg = r.json().get("detail", "Login failed")
                st.error(error_msg)
        except Exception as e:
            st.error(f"Error: {e}")

def register():
    st.header("Register")
    with st.form("reg_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")

        if submitted:
            payload = {"username": username, "email": email, "password": password}
            r = requests.post(f"{API_BASE_URL}/users/register", json=payload)
            if r.status_code in [200, 201]:
                st.success("Registration successful! Please login.")
            else:
                st.error(r.text)

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ==========================
# PROBLEM PAGE (With Submission)
# ==========================

def problems_page():
    st.title("📂 Coding Problems")
    
    r = requests.get(f"{API_BASE_URL}/problems/")
    problems = handle_api_response(r)

    if problems:
        df = pd.DataFrame(problems)
        # Select box for better UX instead of typing ID
        problem_titles = {f"{p['id']}: {p['title']}": p['id'] for p in problems}
        selected_title = st.selectbox("Select a problem to view/solve", options=list(problem_titles.keys()))
        problem_id = problem_titles[selected_title]

        if problem_id:
            pr = requests.get(f"{API_BASE_URL}/problems/{problem_id}")
            p = handle_api_response(pr)
            
            if p:
                st.divider()
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(p["title"])
                    st.markdown(p["description"])
                with col2:
                    st.info(f"**Difficulty:** {p['difficulty']}")
                
                st.write("**Sample Input:**")
                st.code(p["sample_input"])
                st.write("**Sample Output:**")
                st.code(p["sample_output"])

                st.divider()
                st.subheader("Submit Solution")
                language = st.selectbox("Language", ["python", "cpp", "java"])
                code = st.text_area("Paste your code here", height=300)
                
                if st.button("Submit Code"):
                    if not st.session_state.logged_in:
                        st.warning("Please login to submit")
                    else:
                        sub_payload = {
                            "problem_id": problem_id,
                            "language": language,
                            "code": code
                        }
                        sr = requests.post(
                            f"{API_BASE_URL}/submissions/", 
                            json=sub_payload, 
                            headers=get_auth_headers()
                        )
                        if sr.status_code in [200, 201]:
                            st.success("Submission received! Check the Submissions tab for results.")
                        else:
                            st.error("Submission failed.")

# ==========================
# ADMIN & DATA VIEWS
# ==========================

def leaderboard_page():
    st.header("🏆 Global Leaderboard")
    r = requests.get(f"{API_BASE_URL}/leaderboard/")
    data = handle_api_response(r)
    if data:
        st.table(pd.DataFrame(data))

def submissions_page():
    st.header("📜 Recent Submissions")
    # Fetch all if admin, fetch personal if participant (backend logic dependent)
    r = requests.get(f"{API_BASE_URL}/submissions/", headers=get_auth_headers())
    data = handle_api_response(r)
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

# ==========================
# MAIN ROUTING
# ==========================

def main():

    st.sidebar.title("Contest Pro")

    # ==========================
    # NOT LOGGED IN
    # ==========================

    if not st.session_state.logged_in:

        menu = [
            "Login",
            "Register",
            "Leaderboard"
        ]

        choice = st.sidebar.radio(
            "Navigation",
            menu
        )

        if choice == "Login":
            login()

        elif choice == "Register":
            register()

        elif choice == "Leaderboard":
            leaderboard_page()

        return


    # ==========================
    # ADMIN MENU
    # ==========================

    if st.session_state.role == "admin":

        st.sidebar.success(
            "Admin Account"
        )

        menu = [
            "Dashboard",
            "Problems",
            "Users",
            "Submissions",
            "Logout"   ]

        admin_menu = st.sidebar.radio(
            "Admin Panel",
            menu
        )

        headers = {
            "Authorization":
            f"Bearer {st.session_state.token}"
        }

        st.title(
            "Admin Management System"
        )

        # ==========================
        # DASHBOARD
        # ==========================

        if admin_menu == "Dashboard":

            st.subheader(
                "System Statistics"
            )

            try:

                prob_res = requests.get(
                    f"{API_BASE_URL}/problems/",
                    headers=headers
                )

                sub_res = requests.get(
                    f"{API_BASE_URL}/submissions/",
                    headers=headers
                )

                total_probs = (
                    len(prob_res.json())
                    if prob_res.status_code == 200
                    else 0
                )

                total_subs = (
                    len(sub_res.json())
                    if sub_res.status_code == 200
                    else 0
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Problems",
                    total_probs
                )

                col2.metric(
                    "Submissions",
                    total_subs
                )

                col3.metric(
                    "Status",
                    "Online"
                )

            except Exception as e:

                st.error(str(e))

        # ==========================
        # PROBLEMS
        # ==========================

        elif admin_menu == "Problems":

            st.subheader(
                "Problem Management"
            )

            tab1, tab2 = st.tabs(
                [
                    "Add Problem",
                    "Manage Problems"
                ]
            )

            with tab1:

                title = st.text_input(
                    "Problem Title"
                )

                difficulty = st.selectbox(
                    "Difficulty",
                    [
                        "Easy",
                        "Medium",
                        "Hard"
                    ]
                )

                description = st.text_area(
                    "Description"
                )

                sample_input = st.text_area(
                    "Sample Input"
                )

                sample_output = st.text_area(
                    "Sample Output"
                )

                if st.button(
                    "Add Problem"
                ):

                    payload = {

                        "title":
                        title,

                        "difficulty":
                        difficulty,

                        "description":
                        description,

                        "sample_input":
                        sample_input,

                        "sample_output":
                        sample_output
                    }

                    r = requests.post(
                        f"{API_BASE_URL}/problems/",
                        json=payload,
                        headers=headers
                    )

                    if r.status_code in [200, 201]:

                        st.success(
                            "Problem Added"
                        )

                    else:

                        st.error(
                            r.text
                        )

            with tab2:

                r = requests.get(
                    f"{API_BASE_URL}/problems/",
                    headers=headers
                )

                if r.status_code == 200:

                    st.dataframe(
                        pd.DataFrame(
                            r.json()
                        ),
                        use_container_width=True
                    )

                    del_id = st.number_input(
                        "Enter ID to Delete",
                        min_value=1,
                        step=1
                    )

                    if st.button(
                        "Delete Problem"
                    ):

                        del_res = requests.delete(
                            f"{API_BASE_URL}/problems/{del_id}",
                            headers=headers
                        )

                        if del_res.status_code == 200:

                            st.success(
                                "Problem Deleted Successfully"
                            )

                            st.rerun()

                        else:

                            st.error(
                                del_res.text
                        )
        # ==========================
        # USERS
        # ==========================

        elif admin_menu == "Users":

            st.subheader(
                "User Management"
            )

            r = requests.get(
                f"{API_BASE_URL}/users/",
                headers=headers
            )

            if r.status_code == 200:

                st.dataframe(
                    pd.DataFrame(
                        r.json()
                    ),
                    use_container_width=True
                )

            else:

                st.error(
                    r.text
                )

        # ==========================
        # SUBMISSIONS
        # ==========================

        elif admin_menu == "Submissions":

            st.subheader(
                "All Submissions"
            )

            r = requests.get(
                f"{API_BASE_URL}/submissions/",
                headers=headers
            )

            if r.status_code == 200:

                st.dataframe(
                    pd.DataFrame(
                        r.json()
                    ),
                    use_container_width=True
                )

            else:

                st.error(
                    r.text
                )

        elif admin_menu == "Logout":

            logout()

        return


    # ==========================
    # PARTICIPANT MENU
    # ==========================

    st.sidebar.info(
        "Participant Account"
    )

    menu = [
        "Home",
        "Problems",
        "Submissions",
        "Leaderboard",
        "Logout"
    ]

    choice = st.sidebar.radio(
        "Navigation",
        menu
    )

    if choice == "Home":

        st.title(
            "Welcome to Contest Platform"
        )

    elif choice == "Problems":

        problems_page()

    elif choice == "Submissions":

        submissions_page()

    elif choice == "Leaderboard":

        leaderboard_page()

    elif choice == "Logout":

        logout()


if __name__ == "__main__":

    main()
