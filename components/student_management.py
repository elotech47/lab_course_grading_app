import streamlit as st
import pandas as pd
from data_manager import get_students, save_students

def show():
    st.header("Student Management")

    # Load existing students
    students_df = get_students()

    # Display existing students
    st.subheader("Existing Students")
    st.dataframe(students_df)

    # Add new student
    st.subheader("Add New Student")
    with st.form("add_student_form"):
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        submitted = st.form_submit_button("Add Student")

        if submitted:
            if new_name and new_email:
                new_id = students_df['id'].max() + 1 if not students_df.empty else 1
                new_student = pd.DataFrame({
                    'id': [new_id],
                    'name': [new_name],
                    'email': [new_email]
                })
                updated_students = pd.concat([students_df, new_student], ignore_index=True)
                save_students(updated_students)
                st.success(f"Added student: {new_name}")
                st.rerun()
            else:
                st.error("Please fill in both name and email")

    # Edit existing student
    st.subheader("Edit Existing Student")
    edit_student_id = st.selectbox("Select student to edit", students_df['id'].tolist(), format_func=lambda x: students_df[students_df['id'] == x]['name'].values[0])
    
    if edit_student_id:
        student_to_edit = students_df[students_df['id'] == edit_student_id].iloc[0]
        with st.form("edit_student_form"):
            edit_name = st.text_input("Name", value=student_to_edit['name'])
            edit_email = st.text_input("Email", value=student_to_edit['email'])
            edit_submitted = st.form_submit_button("Update Student")

            if edit_submitted:
                if edit_name and edit_email:
                    students_df.loc[students_df['id'] == edit_student_id, 'name'] = edit_name
                    students_df.loc[students_df['id'] == edit_student_id, 'email'] = edit_email
                    save_students(students_df)
                    st.success(f"Updated student: {edit_name}")
                    st.rerun()
                else:
                    st.error("Please fill in both name and email")

    # Delete student
    st.subheader("Delete Student")
    delete_student_id = st.selectbox("Select student to delete", students_df['id'].tolist(), format_func=lambda x: students_df[students_df['id'] == x]['name'].values[0], key="delete_student")
    
    if delete_student_id:
        student_to_delete = students_df[students_df['id'] == delete_student_id].iloc[0]
        if st.button(f"Delete {student_to_delete['name']}"):
            students_df = students_df[students_df['id'] != delete_student_id]
            save_students(students_df)
            st.success(f"Deleted student: {student_to_delete['name']}")
            st.rerun()

    # Assign roles to students (weekly)
    st.subheader("Assign Roles to Students")
    with st.form("assign_roles_form"):
        week = st.number_input("Week", min_value=1, max_value=52, step=1)
        roles = ["Toastmaster", "Table Topic", "Camera Assistant", "Group Leader", "Group Reporter"]
        
        role_assignments = {}
        for role in roles:
            role_assignments[role] = st.selectbox(f"{role}", students_df['id'].tolist(), format_func=lambda x: students_df[students_df['id'] == x]['name'].values[0], key=f"role_{role}")
        
        assign_submitted = st.form_submit_button("Assign Roles")

        if assign_submitted:
            # Here you would typically save these assignments to a database or file
            # For this example, we'll just display the assignments
            st.write(f"Role assignments for Week {week}:")
            for role, student_id in role_assignments.items():
                student_name = students_df[students_df['id'] == student_id]['name'].values[0]
                st.write(f"{role}: {student_name}")
            
            # In a real application, you would save these assignments to a CSV file or database
            # For example:
            # save_role_assignments(week, role_assignments)
            st.success("Roles assigned successfully")