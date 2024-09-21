import pandas as pd
import os

DATA_DIR = "data"

def get_dataframe(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_csv(file_path)

def save_dataframe(df, file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    df.to_csv(file_path, index=False)

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

def save_teachers(df):
    save_dataframe(df, "teachers.csv")

def save_students(df):
    save_dataframe(df, "students.csv")

def save_grades(df):
    save_dataframe(df, "grades.csv")

# Add more specific data operations as needed