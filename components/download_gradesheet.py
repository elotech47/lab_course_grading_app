import pandas as pd
import io
from datetime import datetime, timedelta
import streamlit as st
from data_manager import get_students, get_grades, get_roles

def grade_sheet():
    st.header("Download Grade Sheet")

    students = get_students()
    grades = get_grades()
    roles = get_roles()
    
    role_dict = {
        "Table Topics": "TT",
        "Toastmaster": "TM",
        "Camera": "CAMERA",
        "SMT Presenter": "SMT",
        "Group Leader": "LEAD",
        "Group Reporter": "REPORTER"
    }

    if st.button("Generate Grade Sheet"):
        # Create a DataFrame with dates as index and roles as columns
        start_date = datetime(2024, 1, 29)
        end_date = datetime(2024, 4, 29)
        date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')
        
        columns = ['STUDENT NAME', 'DATES', 'TT', 'TM', 'CAMERA', 'SMT', 'LEAD', 'REPORTER', 'Total', 'Score', 'YT LINK']
        grade_sheet = pd.DataFrame(index=date_range, columns=columns)

        # Fill in the grade sheet
        for _, grade in grades.iterrows():
            student = students[students['id'] == grade['student_id']]['name'].iloc[0]
            role = roles[roles['id'] == grade['role_id']]['name'].iloc[0]
            role_name = role_dict.get(role, role)
            week_date = start_date + timedelta(weeks=grade['week']-1)
            grade_sheet.loc[week_date, role_name] = grade['total_score']
            

        # Add special rows
        st.write(grade_sheet)
        grade_sheet.loc['Total Score'] = ['', '', 200, 200, 40, 40, 400, 400, 1280, '', '']
        
        # Calculate obtained scores
        obtained_scores = grades.groupby('role_id')['total_score'].sum()
        obtained_row = ['Obtained Score', ''] + [obtained_scores.get(i, 0) for i in range(1, 7)]
        total_obtained = sum(obtained_row[2:8])
        percentage = (total_obtained / 1280) * 100
        obtained_row.extend([total_obtained, f"{percentage:.1f}%", ''])
        grade_sheet.loc['Obtained Score'] = obtained_row

        # Add student names and other information
        grade_sheet['STUDENT NAME'] = students['name']
        # grade_sheet['DATES'] = grade_sheet.index.strftime('%m/%d/%y')
        grade_sheet.loc[grade_sheet.index[0], 'STUDENT NAME'] = "ME 4611 SPRING 24 - SECTION 1 FINAL-TERM GRADES"
        # Generate Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            grade_sheet.to_excel(writer, sheet_name='Grade Sheet', index=False)

        # create two buttons 1) view grade sheet 2) download grade sheet
        col1, col2 = st.columns(2)
        with col1:
            view_grade_sheet = st.button("View Grade Sheet")
        with col2:
            download_grade_sheet = st.download_button(
                label="Download Grade Sheet",
                data=output.getvalue(),
                file_name="grade_sheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        if view_grade_sheet:
            # display grade sheet in a table
            st.table(grade_sheet)
