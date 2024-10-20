import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
USE_GSHEETS = os.getenv("USE_GSHEETS", "False").lower() == "true"
SHEET_ID = os.getenv("SHEET_ID", "your-default-sheet-id")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")
DATA_DIR = "data"

# Set up Google Sheets client if enabled
if USE_GSHEETS:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scope)
    client = gspread.authorize(creds)

def get_dataframe_from_sheet(sheet_name):
    """Fetch a dataframe from a Google Sheet."""
    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet(sheet_name)
        return get_as_dataframe(worksheet)
    except gspread.WorksheetNotFound:
        return pd.DataFrame()

def save_dataframe_to_sheet(df, sheet_name):
    """Save a dataframe to a Google Sheet."""
    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet(sheet_name)
        worksheet.clear()  # Clear the worksheet before saving
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
    set_with_dataframe(worksheet, df)

def get_dataframe(file_name):
    """Fetch a dataframe from a CSV file or Google Sheets."""
    if USE_GSHEETS:
        return get_dataframe_from_sheet(file_name.split(".")[0])  # Removing ".csv" if Google Sheets
    else:
        file_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(file_path):
            return pd.DataFrame()
        return pd.read_csv(file_path)

def save_dataframe(df, file_name):
    """Save a dataframe to a CSV file or Google Sheets."""
    if USE_GSHEETS:
        save_dataframe_to_sheet(df, file_name.split(".")[0])  # Removing ".csv" if Google Sheets
    else:
        file_path = os.path.join(DATA_DIR, file_name)
        df.to_csv(file_path, index=False)

# Data retrieval functions
def get_teachers():
    return get_dataframe("teachers.csv")

def get_students():
    return get_dataframe("students.csv")

def get_roles():
    return get_dataframe("roles.csv")

def get_grading_rubrics():
    return get_dataframe("grading_rubrics.csv")

def get_grades():
    return get_dataframe("grades.csv")

def get_student_week_roles():
    return get_dataframe("student_week_roles.csv")

# Data saving functions
def save_teachers(df):
    save_dataframe(df, "teachers.csv")

def save_students(df):
    save_dataframe(df, "students.csv")

def save_grades(df):
    save_dataframe(df, "grades.csv")

def save_student_week_roles(df):
    save_dataframe(df, "student_week_roles.csv")

# Additional operations
def delete_student_roles(student_id, week):
    df = get_student_week_roles()
    df = df[(df['student_id'] != student_id) | (df['week'] != week)]
    save_student_week_roles(df)

def get_teacher_info(teacher_id):
    teachers_df = get_teachers()
    return teachers_df[teachers_df['teacher_id'] == teacher_id].iloc[0]

# Add more specific data operations as needed
