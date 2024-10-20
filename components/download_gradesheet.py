import pandas as pd
import io
from datetime import datetime, timedelta
import streamlit as st
from utils.data_manager import get_students, get_grades, get_roles


def get_role_full_scores():
    role_total_scores = {
        "TM": 0,
        "TT": 0,
        "CAMERA": 0,
        "LEAD": 0,
        "REPORTER": 0,
        "SMT": 0
    }
    
    role_full_scores = {
        "TM": 40,
        "TT": 40,
        "CAMERA": 40,
        "LEAD": 200,
        "REPORTER": 200,
        "SMT": 200
    }
    
    return role_total_scores, role_full_scores

def get_holidays():
    holidays = []
    with st.expander("Add Holidays"):
        num_holidays = st.number_input("Number of holidays to add", min_value=0, max_value=10, value=0)
        for i in range(num_holidays):
            col1, col2 = st.columns(2)
            with col1:
                holiday_date = st.date_input(f"Holiday Date {i+1}", key=f"holiday_date_{i}", value=datetime(2024, 8, 26))
            with col2:
                holiday_name = st.text_input(f"Holiday Name {i+1}", key=f"holiday_name_{i}", value="Holiday")
            holidays.append((holiday_date, holiday_name))
    return holidays

def grade_sheet(teacher_id):
    st.header("Download Grade Sheet")

    teacher_students_df = get_students()
    teacher_students_df = teacher_students_df[teacher_students_df['teacher_id'] == teacher_id]
    teacher_grades_df = get_grades()
    teacher_grades_df = teacher_grades_df[teacher_grades_df['student_id'].isin(teacher_students_df['id'])]
    teacher_roles_df = get_roles()
    
    if teacher_students_df.empty:
        st.warning("You have not registered any students yet")
    else:
        role_dict = {
            "Table Topic": "TT",
            "Toastmaster": "TM",
            "Camera Assistant": "CAMERA",
            "SMT Presenter": "SMT",
            "Group Leader": "LEAD",
            "Group Reporter": "REPORTER"
        }
        
        start_date = st.date_input("Start Date", datetime(2024, 8, 26))
        end_date = st.date_input("End Date", datetime(2024, 11, 25))
        
        # Get the holiday weeks
        holidays = get_holidays()
    
        if st.button("Generate Grade Sheet"):
            # Create date range
            date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')
            
            # Create the main DataFrame
            columns = ['DATES', 'TM', 'TT', 'CAMERA', 'LEAD', 'REPORTER', 'SMT', 'Total', 'Score', 'YT LINK', 'Holiday']
            main_df = pd.DataFrame(columns=columns)
            
            # Add the header row
            header_row = pd.DataFrame([['ME 4611 SPRING 24 - SECTION 1 FINAL-TERM GRADES'] + [''] * (len(columns) - 1)], columns=columns)
            main_df = pd.concat([header_row, main_df], ignore_index=True)
            
            student_final_scores = {}
            # Process each student
            for _, student in teacher_students_df.iterrows():
                student_grades = teacher_grades_df[teacher_grades_df['student_id'] == student['id']]
                # Create student DataFrame
                student_df = pd.DataFrame(index=date_range, columns=columns)
                student_df['DATES'] = student_df.index.strftime('%m/%d/%y')
                
                # Fill in grades
                role_total_scores, role_full_scores = get_role_full_scores()
                for _, grade in student_grades.iterrows():
                    role = teacher_roles_df[teacher_roles_df['id'] == grade['role_id']]['name'].iloc[0]
                    role_name = role_dict.get(role, role)
                    week_date = start_date + timedelta(weeks=grade['week']-1)
                    student_df.loc[week_date, role_name] = grade['total_score']
                    role_total_scores[role_name] += 1

                for holiday_date, holiday_name in holidays:
                    # Convert holiday_date to datetime if it's not already
                    if not isinstance(holiday_date, datetime):
                        holiday_date = pd.to_datetime(holiday_date)
                    
                    # Find the Monday of the week containing the holiday
                    holiday_week_start = holiday_date - timedelta(days=holiday_date.weekday())
                    
                    # Convert holiday_week_start to the same format as the index
                    holiday_week_start = pd.to_datetime(holiday_week_start.date())
                    
                    if holiday_week_start in student_df.index:
                        student_df.loc[holiday_week_start, 'TM'] = holiday_name.upper()
                    else:
                        print(f"No matching date found for holiday: {holiday_date}")
                        print(f"Student date index: {student_df.index}")
                        print(f"Holiday week start: {holiday_week_start}")
                        
                        
                # Add total and obtained score rows
                role_scores_total = [role_total_scores[role] * role_full_scores[role] for role in role_total_scores]
                total_row = ['Total Score'] + role_scores_total + [sum(role_scores_total), '', '', '']
                obtained_scores = student_grades.groupby('role_id')['total_score'].sum()
                obtained_row = ['Obtained Score'] + [obtained_scores.get(i, 0) for i in range(1, 7)]
                total_obtained = sum(obtained_row[1:7])
                percentage = (total_obtained / sum(role_scores_total)) * 100 if sum(role_scores_total) != 0 else 0
                
                student_final_scores[student['id']] = percentage
                obtained_row.extend([total_obtained, f"{percentage:.0f}", '', ''])
                
                student_df = pd.concat([student_df, pd.DataFrame([total_row, obtained_row], columns=columns)], ignore_index=True)
                
                # Add student name and empty row
                student_name_row = pd.DataFrame([['STUDENT NAME : ' + student['name']]+ [''] * (len(columns) - 1)], columns=columns)
                empty_row = pd.DataFrame([[''] * len(columns)], columns=columns)
                student_df = pd.concat([empty_row, student_name_row, student_df], ignore_index=True)
                
                # Append to main DataFrame
                main_df = pd.concat([main_df, student_df], ignore_index=True)
            
            # Add ID and Student columns
            main_df['ID'] = ''
            main_df['Student'] = ''
            main_df['Final Score'] = ''
            # Create a space before these rows
            main_df = pd.concat([main_df.iloc[:0], main_df], ignore_index=True)
            for i, student in teacher_students_df.iterrows():
                main_df.loc[i, 'ID'] = i + 1
                main_df.loc[i, 'Student'] = student['name']
                # Add the student score to the total score
                main_df.loc[i, 'Final Score'] = student_final_scores[student['id']]
            
            # Generate Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                main_df.to_excel(writer, sheet_name='Grade Sheet', index=False)
            
            # Download button
            st.download_button(
                label="Download Grade Sheet",
                data=output.getvalue(),
                file_name="grade_sheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Display preview
            st.write("Preview of the Grade Sheet:")
            st.dataframe(main_df)