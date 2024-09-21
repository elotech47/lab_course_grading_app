import streamlit as st
import pandas as pd
import altair as alt
from data_manager import get_students, get_roles, get_grades

def show():
    st.header("Dashboard")

    # Load data
    students_df = get_students()
    roles_df = get_roles()
    grades_df = get_grades()

    # Merge dataframes to get more information
    merged_df = grades_df.merge(students_df, left_on='student_id', right_on='id', suffixes=('', '_student'))
    merged_df = merged_df.merge(roles_df, left_on='role_id', right_on='id', suffixes=('', '_role'))

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Students", len(students_df))
    with col2:
        st.metric("Total Grades Submitted", len(grades_df))
    with col3:
        avg_grade = grades_df['total_score'].mean()
        st.metric("Average Grade", f"{avg_grade:.2f}")

    # Grade distribution
    st.subheader("Grade Distribution")
    grade_chart = alt.Chart(grades_df).mark_bar().encode(
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