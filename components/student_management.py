import streamlit as st
import pandas as pd
from utils.data_manager import get_students, save_students, get_student_week_roles, save_student_week_roles, get_roles, delete_student_roles
import time

def get_teacher_id(student_id):
    students_df = get_students()
    return students_df[students_df['id'] == student_id]['teacher_id'].values[0]


def assign_student_roles(student_id, role_id, week, overwrite=False, teacher_id=None):
    if get_teacher_id(student_id) != teacher_id:
        st.error("You are not authorized to assign roles to this student")
        return

    if overwrite:
        delete_student_roles(student_id, week)
    new_id = get_student_week_roles()['id'].max() + 1 if not get_student_week_roles().empty else 1
    new_student_week_roles = pd.DataFrame({
        'id': [new_id],
        'student_id': [student_id],
        'role_id': [role_id],
        'week': [week]
    })
    save_student_week_roles(pd.concat([get_student_week_roles(), new_student_week_roles], ignore_index=True))


def assign_student_roles_form(teacher_id, students_df, roles_df):
    st.subheader("Assign Student Roles")

    # Initialize session state for role assignments if it doesn't exist
    if 'role_assignments' not in st.session_state:
        st.session_state.role_assignments = []


    # Form for assigning a single role
    with st.form("assign_role_form"):
        student = st.selectbox("Select Student", students_df['name'].tolist())
        role = st.selectbox("Select Role", roles_df['name'].tolist())
        week = st.number_input("Week", min_value=1, max_value=52, step=1)
        assign_button = st.form_submit_button("Add Assignment")

    if assign_button:
        student_id = students_df[students_df['name'] == student]['id'].iloc[0]
        role_id = roles_df[roles_df['name'] == role]['id'].iloc[0]

        if get_teacher_id(student_id) != teacher_id:
            st.error("You are not authorized to assign roles to this student")
        else:
            # Check for existing assignment
            existing = any(
                (a['student_id'] == student_id and a['week'] == week) 
                for a in st.session_state.role_assignments
            )
            if existing:
                st.warning(f"An assignment for {student} in week {week} already exists in the current list. It will be overwritten.")
                st.session_state.role_assignments = [
                    a for a in st.session_state.role_assignments 
                    if not (a['student_id'] == student_id and a['week'] == week)
                ]

            st.session_state.role_assignments.append({
                'student_id': student_id,
                'role_id': role_id,
                'week': week
            })
            st.success(f"Added assignment: {student} as {role} for week {week}")

    # Display current list of assignments
    if st.session_state.role_assignments:
        st.write("Current assignments to be saved:")
        for i, assignment in enumerate(st.session_state.role_assignments):
            student_name = students_df[students_df['id'] == assignment['student_id']]['name'].iloc[0]
            role_name = roles_df[roles_df['id'] == assignment['role_id']]['name'].iloc[0]
            st.write(f"{i+1}. {student_name} as {role_name} for week {assignment['week']}")

        # Button to remove the last added assignment
        if st.button("Remove Last Assignment"):
            st.session_state.role_assignments.pop()
            st.success("Removed the last assignment from the list")

        # Final submit button to save all assignments
        if st.button("Submit All Assignments"):
            current_roles = get_student_week_roles()
            new_id = current_roles['id'].max() + 1 if not current_roles.empty else 1

            for assignment in st.session_state.role_assignments:
                # Check if assignment already exists and remove it
                current_roles = current_roles[
                    ~((current_roles['student_id'] == assignment['student_id']) & 
                      (current_roles['week'] == assignment['week']))
                ]

                # Add new assignment
                new_assignment = pd.DataFrame({
                    'id': [new_id],
                    'student_id': [assignment['student_id']],
                    'role_id': [assignment['role_id']],
                    'week': [assignment['week']]
                })
                current_roles = pd.concat([current_roles, new_assignment], ignore_index=True)
                new_id += 1

            save_student_week_roles(current_roles)
            st.success(f"Saved {len(st.session_state.role_assignments)} role assignments")
            st.session_state.role_assignments = []  # Clear the list after saving
            st.rerun()

    # Option to view current assignments
    if st.checkbox("View Current Assignments"):
        st.write(get_student_week_roles())
        
        
def display_existing_students(teacher_students_df):
    st.subheader("Existing Students")
    st.dataframe(teacher_students_df)

def add_new_students_form(teacher_id, students_df):
    st.subheader("Add New Students")
    
    # Initialize session state for new students if it doesn't exist
    if 'new_students' not in st.session_state:
        st.session_state.new_students = []

    # Form for adding a single student
    with st.form("add_student_form"):
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        add_button = st.form_submit_button("Add to List")

    if add_button:
        if new_name and new_email:
            if students_df['name'].str.lower().eq(new_name.lower()).any():
                st.error(f"Student with name {new_name} already exists")
            elif students_df['email'].str.lower().eq(new_email.lower()).any():
                st.error(f"Student with email {new_email} already exists")
            elif any(student['name'].lower() == new_name.lower() or student['email'].lower() == new_email.lower() for student in st.session_state.new_students):
                st.error(f"Student with name {new_name} or email {new_email} already in the list to be added")
            else:
                st.session_state.new_students.append({
                    'name': new_name,
                    'email': new_email,
                    'teacher_id': teacher_id
                })
                st.success(f"Added {new_name} to the list")
        else:
            st.error("Please enter both name and email")

    # Display current list of students to be added
    if st.session_state.new_students:
        st.write("Students to be added:")
        for i, student in enumerate(st.session_state.new_students):
            st.write(f"{i+1}. {student['name']} ({student['email']})")

        # Button to remove the last added student
        if st.button("Remove Last Student"):
            st.session_state.new_students.pop()
            st.success("Removed the last student from the list")

        # Final submit button to save all new students
        if st.button("Submit All New Students"):
            new_students_df = pd.DataFrame(st.session_state.new_students)
            new_students_df['id'] = range(int(students_df['id'].max()) + 1, 
                                          int(students_df['id'].max()) + 1 + len(new_students_df))
            updated_students = pd.concat([students_df, new_students_df], ignore_index=True)
            save_students(updated_students)
            st.success(f"Added {len(st.session_state.new_students)} new students")
            st.session_state.new_students = []  # Clear the list after saving
            st.rerun()

    # Option to view current students
    if st.checkbox("View Current Students"):
        st.write(students_df)
            

def edit_existing_student_form(teacher_students_df):
    st.subheader("Edit Existing Student")
    if teacher_students_df.empty:
        st.warning("You have not registered any students yet")
    else:
        edit_student_id = st.selectbox("Select student to edit", teacher_students_df['id'].tolist(), format_func=lambda x: teacher_students_df[teacher_students_df['id'] == x]['name'].values[0])
        
        if edit_student_id:
            student_to_edit = teacher_students_df[teacher_students_df['id'] == edit_student_id].iloc[0]
            with st.form("edit_student_form"):
                edit_name = st.text_input("Name", value=student_to_edit['name'])
                edit_email = st.text_input("Email", value=student_to_edit['email'])
                edit_submitted = st.form_submit_button("Update Student")

                if edit_submitted:
                    if edit_name and edit_email:
                        teacher_students_df.loc[teacher_students_df['id'] == edit_student_id, 'name'] = edit_name
                        teacher_students_df.loc[teacher_students_df['id'] == edit_student_id, 'email'] = edit_email
                        save_students(teacher_students_df)
                        st.success(f"Updated student: {edit_name}")
                        st.rerun()
                    else:
                        st.error("Please fill in both name and email")

def delete_student_form(teacher_students_df):
    st.subheader("Delete Student")
    if teacher_students_df.empty:
        st.warning("You have not registered any students yet")
    else:
        delete_student_id = st.selectbox("Select student to delete", teacher_students_df['id'].tolist(), format_func=lambda x: teacher_students_df[teacher_students_df['id'] == x]['name'].values[0], key="delete_student")
        
        if delete_student_id:
            student_to_delete = teacher_students_df[teacher_students_df['id'] == delete_student_id].iloc[0]
            if st.button(f"Delete {student_to_delete['name']}"):
                teacher_students_df = teacher_students_df[teacher_students_df['id'] != delete_student_id]
                save_students(teacher_students_df)
                st.success(f"Deleted student: {student_to_delete['name']}")
                st.rerun()

def assign_roles_form(teacher_students_df):
    st.subheader("Assign Roles to Students")
    if teacher_students_df.empty:
        st.warning("You have not registered any students yet")
    else:
        with st.form("assign_roles_form"):
            week = st.number_input("Week", min_value=1, max_value=52, step=1)
            students_names = teacher_students_df['name'].tolist()
            selected_student = st.selectbox("Select student", students_names)
            selected_student_id = teacher_students_df[teacher_students_df['name'] == selected_student]['id'].values[0]
            
            roles = ["Toastmaster", "Table Topic", "Camera Assistant", "Group Leader", "Group Reporter"]
            selected_role = st.selectbox("Select role", roles)
            selected_role_id = get_roles()[get_roles()['name'] == selected_role]['id'].values[0]
            
            assign_submitted = st.form_submit_button("Assign Role")

            if assign_submitted:
                assign_student_roles(selected_student_id, selected_role_id, week, teacher_id=teacher_students_df['teacher_id'].iloc[0])
                st.success(f"Assigned role {selected_role} to {selected_student}")

def show(teacher_id):
    st.header("Student Management")

    students_df = get_students()
    roles_df = get_roles()
    teacher_students_df = students_df[students_df['teacher_id'] == teacher_id]

    display_existing_students(teacher_students_df)
    add_new_students_form(teacher_id, students_df)
    edit_existing_student_form(teacher_students_df)
    delete_student_form(teacher_students_df)
    assign_student_roles_form(teacher_id, teacher_students_df, roles_df)
