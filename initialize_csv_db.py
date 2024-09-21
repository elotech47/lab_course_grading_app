import pandas as pd
import os

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Create teachers.csv
teachers_df = pd.DataFrame({
    "id": [1],
    "username": ["teacher1"],
    "password": ["password123"]  # In a real app, use hashed passwords
})
teachers_df.to_csv("data/teachers.csv", index=False)

# Create students.csv
students_df = pd.DataFrame({
    "id": [1, 2],
    "name": ["John Doe", "Jane Smith"],
    "email": ["john@example.com", "jane@example.com"],
    "teacher_id": [1, 1]
})
students_df.to_csv("data/students.csv", index=False)

# Create roles.csv
roles_df = pd.DataFrame({
    "id": [1, 2, 3, 4, 5],
    "name": ["Toastmaster", "Table Topic", "Camera Assistant", "Group Leader", "Group Reporter"]
})
roles_df.to_csv("data/roles.csv", index=False)

# # Create grading_rubrics.csv (simplified for this example)
# rubrics_df = pd.DataFrame({
#     "id": [1, 2, 3, 4, 5],
#     "role_id": [1, 2, 3, 4, 5],
#     "category": ["Moderation", "Presentation Quality", "Video Footage", "Technical Comprehension", "Technical Comprehension"],
#     "max_score": [40, 40, 40, 100, 100]
# })
# rubrics_df.to_csv("data/grading_rubrics.csv", index=False)

# Create empty grades.csv
grades_df = pd.DataFrame({
    "id": [],
    "student_id": [],
    "role_id": [],
    "week": [],
    "total_score": [],
    "comments": [],
    "score_breakdown": [],  # This will be a JSON string containing all individual scores
    "timestamp": []
})
grades_df.to_csv("data/grades.csv", index=False)

print("CSV files created successfully.")