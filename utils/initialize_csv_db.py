import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Configuration
USE_GSHEETS = os.getenv("USE_GSHEETS", "True").lower() == "true"
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "me4611-fall-2024")  # Default name if no sheet exists
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")
DATA_DIR = os.getenv("DATA_DIR", "data")

# Set up Google Sheets client
if USE_GSHEETS:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scope)
    client = gspread.authorize(creds)

def get_or_create_sheet(sheet_name, sheet_id=None):
    """Opens an existing Google Sheet or creates a new one if it doesn't exist."""
    try:
        # Try to open the Google Sheet by ID if provided
        if sheet_id:
            sheet = client.open_by_key(sheet_id)
            print(f"Successfully opened sheet with ID: {sheet_id}")
        else:
            # If no sheet ID, open by name
            sheet = client.open(sheet_name)
            print(f"Successfully opened sheet with name: {sheet_name}")
    except gspread.SpreadsheetNotFound:
        sheet = client.create(sheet_name)
    except Exception as e:
        import traceback
        print(f"Error accessing Google Sheet: {e}")
        print(traceback.format_exc())
        return None
        
    return sheet


# Functions to get dataframes from Google Sheets or CSV files
def get_dataframe(name):
    if USE_GSHEETS:
        sheet = get_or_create_sheet(SHEET_NAME, SHEET_ID)
        try:
            worksheet = sheet.worksheet(name)
            return get_as_dataframe(worksheet)
        except gspread.WorksheetNotFound:
            return pd.DataFrame()
    else:
        file_path = os.path.join(DATA_DIR, f"{name}.csv")
        if not os.path.exists(file_path):
            return pd.DataFrame()
        return pd.read_csv(file_path)

def save_dataframe(df, name):
    if USE_GSHEETS:
        try:
            sheet = get_or_create_sheet(SHEET_NAME, SHEET_ID)
        except Exception as e:
            print(f"Error opening sheet: {e}")
            return
        try:
            worksheet = sheet.worksheet(name)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = sheet.add_worksheet(title=name, rows="1000", cols="20")
        set_with_dataframe(worksheet, df)
    else:
        file_path = os.path.join(DATA_DIR, f"{name}.csv")
        df.to_csv(file_path, index=False)

def initialize_db(teacher_info):
    try:
        create_tables(teacher_info)
        return True, f"{'Google Sheets' if USE_GSHEETS else 'CSV files'} created successfully."
    except Exception as e:
        return False, f"An error occurred: {e}"

def create_tables(teacher_info):
    # Create teachers table
    teachers_df = pd.DataFrame({
        "id": [1],
        "username": [teacher_info["username"]],
        "password": [teacher_info["password"]],  # In a real app, use hashed passwords
        "teacher_id": [teacher_info["teacher_id"]]
    })
    save_dataframe(teachers_df, "teachers")

    # Create students table
    students_df = pd.DataFrame({"id": [], "name": [], "email": [], "teacher_id": []})
    save_dataframe(students_df, "students")

    # Create roles table
    roles_df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5, 6],
        "name": ["Toastmaster", "Table Topic", "Camera Assistant", "Group Leader", "Group Reporter", "SMT"]
    })
    save_dataframe(roles_df, "roles")

    # Create student_week_roles table
    student_week_roles_df = pd.DataFrame({"id": [], "student_id": [], "role_id": [], "week": []})
    save_dataframe(student_week_roles_df, "student_week_roles")

    # Create grades table
    grades_df = pd.DataFrame({
        "id": [], "student_id": [], "role_id": [], "week": [], "total_score": [],
        "comments": [], "score_breakdown": [], "timestamp": []
    })
    save_dataframe(grades_df, "grades")

    print(f"{'Google Sheets' if USE_GSHEETS else 'CSV files'} created successfully.")

# Data access functions
def get_teachers():
    return get_dataframe("teachers")

def get_students():
    return get_dataframe("students")

def get_roles():
    return get_dataframe("roles")

def get_grades():
    return get_dataframe("grades")

def get_student_week_roles():
    return get_dataframe("student_week_roles")

def save_teachers(df):
    save_dataframe(df, "teachers")

def save_students(df):
    save_dataframe(df, "students")

def save_grades(df):
    save_dataframe(df, "grades")

def save_student_week_roles(df):
    save_dataframe(df, "student_week_roles")

def delete_student_roles(student_id, week):
    df = get_student_week_roles()
    df = df[(df['student_id'] != student_id) | (df['week'] != week)]
    save_student_week_roles(df)

def get_teacher_info(teacher_id):
    teachers_df = get_teachers()
    return teachers_df[teachers_df['teacher_id'] == teacher_id].iloc[0]

if __name__ == "__main__":
    print(f"This action will delete all existing data and create new {'Google Sheets' if USE_GSHEETS else 'CSV files'}.")
    print("Are you sure you want to continue?")
    response = input("Press Enter to continue... (y/n) ")
    if response.lower() == "y":
        create_new_user = input("Do you want to create a new user? (y/n) ")
        if create_new_user.lower() == "y":
            teacher_info = {
                "username": "admin",
                "password": "admin@123",
                "teacher_id": "000001"
            }
        else:
            teacher_info = {
                "username": input("Enter teacher username: "),
                "password": input("Enter teacher password: "),
                "teacher_id": input("Enter teacher ID: ")
            }
        success, message = initialize_db(teacher_info)
        print(message)
    else:
        print("Operation cancelled.")
