import streamlit as st
import pandas as pd
import altair as alt
from utils.db_manager import get_students, get_roles, get_grades

def show(teacher_id):
    st.header("Dashboard")

    # Load data
    students = get_students(teacher_id)
    roles = get_roles()
    grades = get_grades(teacher_id)

    # Convert to pandas DataFrames
    students_df = pd.DataFrame(students)
    roles_df = pd.DataFrame(roles)
    grades_df = pd.DataFrame(grades)

    # Print DataFrame info for debugging
    st.sidebar.subheader("Debug Information")
    st.sidebar.text("Students DataFrame:")
    st.sidebar.text(students_df.info())
    st.sidebar.text("\nRoles DataFrame:")
    st.sidebar.text(roles_df.info())
    st.sidebar.text("\nGrades DataFrame:")
    st.sidebar.text(grades_df.info())

    if students_df.empty:
        st.info("You do not have any students yet. Please register students first.\n\nGo to Student Management on the sidebar to register students.")
        return

    # Display key metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Students", len(students_df))
    with col2:
        st.metric("Total Grades Submitted", len(grades_df))

    if not grades_df.empty:
        if 'total_score' in grades_df.columns:
            col3, _ = st.columns(2)
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

        # Attempt to merge dataframes
        if all(col in grades_df.columns for col in ['student_id', 'role_id']):
            try:
                merged_df = grades_df.merge(students_df, left_on='student_id', right_on='id', suffixes=('', '_student'))
                merged_df = merged_df.merge(roles_df, left_on='role_id', right_on='id', suffixes=('', '_role'))

                if 'total_score' in merged_df.columns and 'name_role' in merged_df.columns:
                    # Performance by role
                    st.subheader("Average Performance by Role")
                    role_performance = merged_df.groupby('name_role')['total_score'].mean().reset_index()
                    role_chart = alt.Chart(role_performance).mark_bar().encode(
                        x='name_role',
                        y='total_score',
                        color='name_role'
                    ).properties(width=600, height=300)
                    st.altair_chart(role_chart, use_container_width=True)

                if all(col in merged_df.columns for col in ['name', 'name_role', 'week', 'total_score']):
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
                else:
                    st.warning("Some required columns are missing from the merged data.")
            except KeyError as e:
                st.error(f"Error: Unable to merge data. Missing key: {e}")
        else:
            st.warning("Grades data is missing required columns (student_id or role_id).")
    else:
        st.info("No grades have been submitted yet.")

def format_student_name(name):
    return name.split()[0]  # Return first name