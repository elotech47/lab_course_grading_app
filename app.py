import streamlit as st
from auth import login, register
from components import dashboard, student_management, grading_interface, download_gradesheet

def main():
    st.set_page_config(page_title="Grading App", page_icon="📚", layout="wide")
    st.title("Grading App")

    if 'user' not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            login()
        
        with tab2:
            register()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.user}")
        st.sidebar.button("Logout", on_click=logout)

        menu = ["Dashboard", "Student Management", "Grading", "Download Grade Sheet"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Dashboard":
            dashboard.show()
        elif choice == "Student Management":
            student_management.show()
        elif choice == "Grading":
            grading_interface.show()
        elif choice == "Download Grade Sheet":
            download_gradesheet.grade_sheet()

def logout():
    st.session_state.user = None

if __name__ == "__main__":
    main()