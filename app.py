import streamlit as st
from utils.auth import login, register
from components import dashboard, student_management, grading_interface, download_gradesheet
from utils.initialize_csv_db import initialize_db
from utils.data_manager import get_teacher_info
import time
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    st.set_page_config(page_title="Grading App", page_icon="📚", layout="wide")
    st.title("Grading App")

    if 'user' not in st.session_state:
        st.session_state.user = None
        st.session_state.teacher_id = None
    
    if 'reset_stage' not in st.session_state:
        st.session_state.reset_stage = 0

    if st.session_state.user is None:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            login()
        
        with tab2:
            register()
    else:
        teacher_info = get_teacher_info(st.session_state.teacher_id)
                
                
        st.sidebar.title(f"Welcome, {st.session_state.user}")
        st.sidebar.button("Logout", on_click=logout)
        # Improved reset logic
        if st.session_state.reset_stage == 0:
            if st.sidebar.button("Reset Database"):
                print("Reset stage 1")
                st.session_state.reset_stage = 1
        
        if st.session_state.reset_stage == 1:
            st.error("This action will delete all existing data in the CSV files and create new ones.\nAre you sure you want to continue?")
            col1, col2 = st.columns(2)
            if col1.button("Yes, continue"):
                admin_secret_phrase = st.text_input("Enter Admin Secret Phrase: ")
                if admin_secret_phrase == os.getenv("ADMIN_SECRET_PHRASE"):
                    success, message = initialize_db(teacher_info)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                st.session_state.reset_stage = 0
                # PAUSE FOR A SECOND
                time.sleep(1)
                st.rerun()
            if col2.button("No, cancel"):
                st.session_state.reset_stage = 0
                st.rerun()
                
        
                
                
        menu = ["Dashboard", "Student Management", "Grading", "Download Grade Sheet"]
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Dashboard":
            dashboard.show(st.session_state.teacher_id)
        elif choice == "Student Management":
            student_management.show(st.session_state.teacher_id)
        elif choice == "Grading":
            grading_interface.show(st.session_state.teacher_id)
        elif choice == "Download Grade Sheet":
            download_gradesheet.grade_sheet(st.session_state.teacher_id)
            
            
        # add my branding
        st.sidebar.markdown("---")
        st.sidebar.markdown("Made with ❤️ by [elotech](https://github.com/elotech47)")
        

def logout():
    st.session_state.user = None
    st.session_state.reset_stage = 0

if __name__ == "__main__":
    main()