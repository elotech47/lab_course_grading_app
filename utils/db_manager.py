from tinydb import TinyDB, Query, where
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import json
from datetime import date, time
# Load environment variables
load_dotenv()

# Configuration
DATA_DIR = os.getenv("DATA_DIR", "data")
DB_FILE = os.path.join(DATA_DIR, "lab_grading.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize TinyDB
db = TinyDB(DB_FILE)

# Define tables
teachers_table = db.table('teachers')
students_table = db.table('students')
roles_table = db.table('roles')
grades_table = db.table('grades')
student_week_roles_table = db.table('student_week_roles')

# Helper functions
def generate_id():
    return str(uuid.uuid4())


def date_time_serializer(obj):
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
# Teacher operations
def create_teacher(username, password):
    teacher_id = generate_id()
    teachers_table.insert({'id': teacher_id, 'username': username, 'password': password})
    return teacher_id

def get_teacher(teacher_id=None, username=None):
    if teacher_id:
        return teachers_table.get(where('id') == teacher_id)
    elif username:
        return teachers_table.get(where('username') == username)
    return None

def get_all_teachers():
    return teachers_table.all()

# Student operations
def create_student(name, email, teacher_id):
    student_id = generate_id()
    students_table.insert({'id': student_id, 'name': name, 'email': email, 'teacher_id': teacher_id})
    return student_id

def get_students(teacher_id):
    return students_table.search(where('teacher_id') == teacher_id)

# Role operations
def create_roles():
    roles = [
        {"id": 1, "name": "Toastmaster"},
        {"id": 2, "name": "Table Topic"},
        {"id": 3, "name": "Camera Assistant"},
        {"id": 4, "name": "Group Leader"},
        {"id": 5, "name": "Group Reporter"},
        {"id": 6, "name": "SMT"}
    ]
    roles_table.insert_multiple(roles)

def get_roles():
    return roles_table.all()

def update_student_role(assignment_id, new_role_id, teacher_id):
    student_week_roles_table.update({'role_id': new_role_id}, where('id') == assignment_id)

# Grade operations
def update_grade(grade_id, total_score, comments, score_breakdown, role_id, teacher_id):
    grades_table.update({
        'total_score': total_score, 
        'comments': comments, 
        'score_breakdown': json.dumps(score_breakdown, default=date_time_serializer),
        'timestamp': datetime.now().isoformat(),
        'role_id': role_id
    }, where('id') == grade_id)

def save_grade2db(student_id, role_id, week, total_score, comments, score_breakdown, teacher_id):
    grade_id = generate_id()
    grade = {
        'id': grade_id,
        'student_id': student_id,
        'role_id': role_id,
        'week': week,
        'total_score': total_score,
        'comments': comments,
        'score_breakdown': json.dumps(score_breakdown, default=date_time_serializer),
        'teacher_id': teacher_id,
        'timestamp': datetime.now().isoformat()
    }
    grades_table.insert(grade)
    return grade_id

def get_grades(teacher_id):
    return grades_table.search(where('teacher_id') == teacher_id)

# Student week role operations
def assign_student_role(student_id, role_id, week, teacher_id):
    assignment_id = generate_id()
    student_week_roles_table.insert({
        'id': assignment_id,
        'student_id': student_id,
        'role_id': role_id,
        'week': week,
        'teacher_id': teacher_id
    })
    return assignment_id

def update_student_role(assignment_id, new_role_id, teacher_id):
    student_week_roles_table.update({'role_id': new_role_id}, where('id') == assignment_id)

def get_student_week_roles(teacher_id):
    return student_week_roles_table.search(where('teacher_id') == teacher_id)

def delete_student_roles(student_id, week, teacher_id):
    student_week_roles_table.remove(
        (where('student_id') == student_id) & 
        (where('week') == week) & 
        (where('teacher_id') == teacher_id)
    )

def update_student(student_id, name, email, teacher_id):
    students_table.update({'name': name, 'email': email}, where('id') == student_id)

def delete_student(student_id, teacher_id):
    students_table.remove(where('id') == student_id)
    # Remove any associated roles or grades
    student_week_roles_table.remove(where('student_id') == student_id)
    grades_table.remove(where('student_id') == student_id)

# Initialize database (create roles if they don't exist)
def initialize_db():
    if len(roles_table) == 0:
        create_roles()

# Call this function when your application starts
initialize_db()

# Example usage
if __name__ == "__main__":
    # Create a teacher
    teacher_id = create_teacher("johndoe", "password123")
    
    # Create students for this teacher
    student1_id = create_student("Alice", "alice@example.com", teacher_id)
    student2_id = create_student("Bob", "bob@example.com", teacher_id)
    
    # Assign roles to students
    assign_student_role(student1_id, 1, 1, teacher_id)  # Alice as Toastmaster in week 1
    assign_student_role(student2_id, 2, 1, teacher_id)  # Bob as Table Topic in week 1
    
    # Save grades
    save_grade(student1_id, 1, 1, 85, "Good performance", {"criteria1": 40, "criteria2": 45}, teacher_id)
    
    # Retrieve data
    print("Students:")
    print(get_students(teacher_id))
    
    print("\nStudent Week Roles:")
    print(get_student_week_roles(teacher_id))
    
    print("\nGrades:")
    print(get_grades(teacher_id))