import streamlit as st

def show_login():
    with st.form("login", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

        if submit_button:
            if username == st.secrets.admin.username and password == st.secrets.admin.password:
                st.success("You're logged in!")
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("The username or password you have entered is invalid.")

def show_logout():
    with st.sidebar:
        logout = st.button("Logout")
        if logout:
            st.session_state.logged_in = False
            st.experimental_rerun()

def show_unauthorized():
    st.error("You are not authorized to view this page. Please login.")
    st.markdown("### [Login](/)")

def authenticate():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        show_login()
        st.stop()
    else:
        show_logout()

def is_authenticated():
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        show_unauthorized()
        st.stop()
    else:
        show_logout()