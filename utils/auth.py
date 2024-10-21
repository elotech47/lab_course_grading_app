import streamlit as st
import hashlib
import uuid
from utils.db_manager import (
    get_teacher, create_teacher, get_all_teachers,
    initialize_db
)

def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_teacher(username=username)
        
        if user:
            stored_password = user['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            if stored_password == hashed_password:
                st.session_state.user = username
                st.session_state.teacher_id = user['id']
                st.success(f"Logged in as {username}")
                st.rerun()
            else:
                st.error("Incorrect password")
        else:
            st.error("User not found")

def register():
    st.subheader("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if new_password != confirm_password:
            st.error("Passwords do not match")
            return

        existing_teacher = get_teacher(username=new_username)
        if existing_teacher:
            st.error("Username already exists")
            return

        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        teacher_id = create_teacher(new_username, hashed_password)
        
        st.success("Registration successful. You can now log in.")

def logout():
    st.session_state.user = None
    st.session_state.teacher_id = None
    st.success("Logged out successfully")
    st.rerun()

def is_logged_in():
    return st.session_state.user is not None

def get_current_user():
    return st.session_state.user

# Initialize the database when the app starts
initialize_db()