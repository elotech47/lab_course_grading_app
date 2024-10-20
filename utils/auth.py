import streamlit as st
import pandas as pd
from utils.data_manager import get_teachers, save_teachers
import hashlib
import uuid

def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        teachers_df = get_teachers()
        user = teachers_df[teachers_df['username'] == username]
        
        if not user.empty:
            stored_password = user.iloc[0]['password']
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            if stored_password == hashed_password:
                st.session_state.user = username
                st.session_state.teacher_id = user.iloc[0]['teacher_id']
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

        teachers_df = get_teachers()
        if new_username in teachers_df['username'].values:
            st.error("Username already exists")
            return

        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        teacher_id = uuid.uuid4()
        new_teacher = pd.DataFrame({
            'id': [teachers_df['id'].max() + 1 if not teachers_df.empty else 1],
            'username': [new_username],
            'password': [hashed_password],
            'teacher_id': [teacher_id]
        })
        
        updated_teachers = pd.concat([teachers_df, new_teacher], ignore_index=True)
        save_teachers(updated_teachers)
        
        st.success("Registration successful. You can now log in.")

def logout():
    st.session_state.user = None
    st.success("Logged out successfully")
    st.rerun()

def is_logged_in():
    return st.session_state.user is not None

def get_current_user():
    return st.session_state.user