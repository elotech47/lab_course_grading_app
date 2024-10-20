import streamlit as st
import pandas as pd
import altair as alt
from utils.data_manager import get_students, get_roles, get_grades

def show(teacher_id):
    st.header("Dashboard")

    # Load data
    students_df = get_students()
    teacher_students_df = students_df[students_df['teacher_id'] == teacher_id]
    
    if teacher_students_df.empty:
        st.info("You do not have any students yet. Please register students first.\n\nGo to Student Management on the sidebar to register students.")
        return
    
    roles_df = get_roles()
    grades_df = get_grades()
    teacher_grades_df = grades_df[grades_df['student_id'].isin(teacher_students_df['id'])]

    # Merge dataframes to get more information
    merged_df = teacher_grades_df.merge(teacher_students_df, left_on='student_id', right_on='id', suffixes=('', '_student'))
    merged_df = merged_df.merge(roles_df, left_on='role_id', right_on='id', suffixes=('', '_role'))

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", len(teacher_students_df))
    with col2:
        st.metric("Total Grades Submitted", len(teacher_grades_df))
    with col3:
        avg_grade = teacher_grades_df['total_score'].mean()
        st.metric("Average Grade", f"{avg_grade:.2f}")

    # Grade distribution
    st.subheader("Grade Distribution")
    grade_chart = alt.Chart(teacher_grades_df).mark_bar().encode(
        alt.X("total_score", bin=True),
        y='count()',
    ).properties(width=600, height=300)
    st.altair_chart(grade_chart, use_container_width=True)

    # Performance by role
    st.subheader("Average Performance by Role")
    role_performance = merged_df.groupby('name_role')['total_score'].mean().reset_index()
    role_chart = alt.Chart(role_performance).mark_bar().encode(
        x='name_role',
        y='total_score',
        color='name_role'
    ).properties(width=600, height=300)
    st.altair_chart(role_chart, use_container_width=True)

    # Recent grades
    st.subheader("Recent Grades")
    recent_grades = merged_df.sort_values('week', ascending=False).head(10)
    st.dataframe(recent_grades[['name', 'name_role', 'week', 'total_score']])

    # Student performance
    st.subheader("Student Performance")
    selected_student = st.selectbox("Select a student", students_df['name'].tolist())
    student_grades = merged_df[merged_df['name'] == selected_student]
    
    if not student_grades.empty:
        student_chart = alt.Chart(student_grades).mark_line(point=True).encode(
            x='week',
            y='total_score',
            color='name_role'
        ).properties(width=600, height=300)
        st.altair_chart(student_chart, use_container_width=True)
    else:
        st.write("No grades available for this student.")

def format_student_name(name):
    return name.split()[0]  # Return first name