import streamlit as st
from utils.db_manager import (
    get_students, get_student_week_roles, get_roles, delete_student_roles,
    create_student, assign_student_role, update_student, delete_student,
    update_student_role
)
import time

def assign_student_roles_form(teacher_id):
    st.subheader("Assign Student Roles")

    students = get_students(teacher_id)
    roles = get_roles()
    if not students:   
        st.warning("You have not registered any students yet")
    else:
        with st.form("assign_role_form"):
            student = st.selectbox("Select Student", [s['name'] for s in students])
            role = st.selectbox("Select Role", [r['name'] for r in roles])
            week = st.number_input("Week", min_value=1, max_value=52, step=1)
            assign_button = st.form_submit_button("Assign/Update Role")

            if assign_button:
                student_id = next(s['id'] for s in students if s['name'] == student)
                role_id = next(r['id'] for r in roles if r['name'] == role)

                # Check if the student already has a role for this week
                existing_assignments = get_student_week_roles(teacher_id)
                existing_assignment = next((a for a in existing_assignments if a['student_id'] == student_id and a['week'] == week), None)

                if existing_assignment:
                    # Update the existing assignment
                    st.warning(f"{student} already has a role assigned for week {week}. Updating role to {role}.")
                    update_student_role(existing_assignment['id'], role_id, teacher_id)
                    time.sleep(1)
                    st.rerun()
                else:
                    # Assign the new role
                    assign_student_role(student_id, role_id, week, teacher_id)
                    st.success(f"Assigned {student} as {role} for week {week}")
                    time.sleep(1)
                    st.rerun()

        st.subheader("Current Assignments")
        assignments = get_student_week_roles(teacher_id)
        for assignment in assignments:
            student_name = next(s['name'] for s in students if s['id'] == assignment['student_id'])
            role_name = next(r['name'] for r in roles if r['id'] == assignment['role_id'])
            st.write(f"{student_name} as {role_name} for week {assignment['week']}")

def display_existing_students(teacher_id):
    st.subheader("Existing Students")
    students = get_students(teacher_id)
    if students:
        st.table([{'name': s['name'], 'email': s['email']} for s in students])
    else:
        st.warning("You have not registered any students yet")

def add_new_students_form(teacher_id):
    st.subheader("Add New Student")
    
    with st.form("add_student_form"):
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        add_button = st.form_submit_button("Add Student")

    if add_button:
        if new_name and new_email:
            students = get_students(teacher_id)
            if any(s['name'].lower() == new_name.lower() or s['email'].lower() == new_email.lower() for s in students):
                st.error("A student with this name or email already exists")
            else:
                create_student(new_name, new_email, teacher_id)
                st.success(f"Added {new_name} to the list of students")
                st.rerun()
        else:
            st.error("Please enter both name and email")

def edit_existing_student_form(teacher_id):
    st.subheader("Edit Existing Student")
    students = get_students(teacher_id)
    if not students:
        st.warning("You have not registered any students yet")
    else:
        student_names = [student['name'] for student in students]
        edit_student_name = st.selectbox(
            "Select student to edit",
            options=student_names
        )
        
        if edit_student_name:
            student_to_edit = next(s for s in students if s['name'] == edit_student_name)
            with st.form("edit_student_form"):
                edit_name = st.text_input("Name", value=student_to_edit['name'])
                edit_email = st.text_input("Email", value=student_to_edit['email'])
                edit_submitted = st.form_submit_button("Update Student")

                if edit_submitted:
                    if edit_name and edit_email:
                        update_student(student_to_edit['id'], edit_name, edit_email, teacher_id)
                        st.success(f"Updated student: {edit_name}")
                        st.rerun()
                    else:
                        st.error("Please fill in both name and email")

def delete_student_form(teacher_id):
    st.subheader("Delete Student")
    students = get_students(teacher_id)
    if not students:
        st.warning("You have not registered any students yet")
    else:
        delete_student_name = st.selectbox(
            "Select student to delete",
            options=[s['name'] for s in students],
            key="delete_student"
        )
        
        if delete_student_name:
            student_to_delete = next(s for s in students if s['name'] == delete_student_name)
            if st.button(f"Delete {student_to_delete['name']}"):
                delete_student(student_to_delete['id'], teacher_id)
                st.success(f"Deleted student: {student_to_delete['name']}")
                st.rerun()

def show(teacher_id):
    st.header("Student Management")

    display_existing_students(teacher_id)
    add_new_students_form(teacher_id)
    edit_existing_student_form(teacher_id)
    delete_student_form(teacher_id)
    assign_student_roles_form(teacher_id)