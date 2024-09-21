import streamlit as st
import pandas as pd
import datetime
from data_manager import get_students, get_roles, get_grading_rubrics, save_grades, get_grades
from rubric_generator import generate_rubric_pdf
import json
from datetime import date, time



def show():
    st.header("Grading Interface")

    tab1, tab2 = st.tabs(["Grade Student", "Download Graded Rubric"])

    with tab1:
        grade_student()

    with tab2:
        download_rubric()
        
def grade_student():
    st.header("Grade Student")

    # Select student and role
    students = get_students()
    roles = get_roles()
    grades = get_grades()
    
    student = st.selectbox("Select Student", students['name'].tolist())
    role = st.selectbox("Select Role", roles['name'].tolist())
    print(role)
    week = st.number_input("Week", min_value=1, max_value=52, step=1)
    
    existing_grade = grades[(grades['student_id'] == students[students['name'] == student]['id'].iloc[0]) & 
                            (grades['role_id'] == roles[roles['name'] == role]['id'].iloc[0]) & 
                            (grades['week'] == week)]
    
    if not existing_grade.empty:
        st.warning(f"A grade already exists for {student} in week {week} for role {role}.")
        edit = st.checkbox("Edit existing grade?")
        if edit:
            # Pre-fill the form with existing data
            grade_data = existing_grade.iloc[0]
            # Use grade_data to pre-fill the form fields
        else:
            grade_data = {}
    else:
        grade_data = {}

    # Display the appropriate grading form based on the selected role
    if role == "Toastmaster":
        toastmaster_grading_form(student, week, grade_data)
    elif role == "Table Topic":
        table_topic_grading_form(student, week, grade_data)
    elif role == "Camera Assistant":
        camera_assistant_grading_form(student, week, grade_data)
    elif role == "Group Leader":
        group_leader_grading_form(student, week, grade_data)
    elif role == "Group Reporter":
        group_reporter_grading_form(student, week, grade_data)
    elif role == "SMT":
        smt_presenter_grading_form(student, week, grade_data)
    # Add more elif statements for other roles...
    else:
        st.write("Grading form for this role is not implemented yet.")

def toastmaster_grading_form(student, week, grade_data):
    st.subheader(f"Toastmaster Grading Form for {student} - Week {week}")
    score_breakdown = {}
    pdf_buffer = None
    with st.form("toastmaster_grading_form"):
        st.write("a. Moderation of the Speaking Session:")
        first_last_impression = st.slider("First/Last Impression", 0, 10, grade_data.get('first_last_impression', 5))
        transitions = st.slider("Transitions between Speakers", 0, 10, grade_data.get('transitions', 5))
        timing_questions = st.slider("Timing and Follow-up Questions", 0, 10, grade_data.get('timing_questions', 5))
        stature_vocal = st.slider("Stature and Vocal Quality", 0, 10, grade_data.get('stature_vocal', 5))

        score_breakdown['first_last_impression'] = first_last_impression
        score_breakdown['transitions'] = transitions
        score_breakdown['timing_questions'] = timing_questions
        score_breakdown['stature_vocal'] = stature_vocal

        subtotal_moderation = first_last_impression + transitions + timing_questions + stature_vocal
        st.write(f"Subtotal - Moderation: {subtotal_moderation} out of 40pts")

        st.write("b. Feedback on YouTube:")
        feedback_1 = st.number_input("Feedback for Speaker 1", 0, 10, grade_data.get('feedback_1', 5))
        feedback_2 = st.number_input("Feedback for Speaker 2", 0, 10, grade_data.get('feedback_2', 5))
        self_assessment = st.number_input("Self-Assessment", 0, 10, grade_data.get('self_assessment', 5))

        score_breakdown['feedback_1'] = feedback_1
        score_breakdown['feedback_2'] = feedback_2
        score_breakdown['self_assessment'] = self_assessment

        subtotal_comments = feedback_1 + feedback_2 + self_assessment
        st.write(f"Subtotal - Comments: {subtotal_comments} out of 30pts")

        st.write("c. Deductions:")
        table_topics_not_approved = st.checkbox("Table Topics not approved 24 hours prior to class")
        late_comments = st.number_input("Number of late comments", 0, 10, 0)

        deductions = (20 if table_topics_not_approved else 0) + (5 * late_comments)
        st.write(f"Total Deductions: {deductions}pts")

        score_breakdown['table_topics_not_approved'] = table_topics_not_approved
        score_breakdown['late_comments'] = late_comments
        score_breakdown['deductions'] = deductions

        total_grade = subtotal_moderation + subtotal_comments - deductions
        st.write(f"d. Total Grade: {total_grade} out of 70pts")

        comments = st.text_area("e. Comments:", value=grade_data.get('comments', ''))

        score_breakdown['total_grade'] = total_grade
        score_breakdown['comments'] = comments

        submitted = st.form_submit_button("Submit Grade")
        
        if submitted:
            rubric_data = {
                'first_last_impression': first_last_impression,
                'transitions': transitions,
                'timing_questions': timing_questions,
                'stature_vocal': stature_vocal,
                'subtotal_moderation': subtotal_moderation,
                'subtotal_comments': subtotal_comments,
                'deductions': deductions,
                'total_grade': total_grade,
                'comments': comments,
            }
            pdf_buffer = save_grade(student, "Toastmaster", week, total_grade, comments, score_breakdown)
            st.success("Grade submitted successfully!")

    if pdf_buffer:
        st.download_button(
            label="Download Graded Rubric",
            data=pdf_buffer,
            file_name=f"{student}_Toastmaster_Week{week}_Rubric.pdf",
            mime="application/pdf"
        )

def table_topic_grading_form(student, week, grade_data):
    st.subheader(f"Table Topic Grading Form for {student} - Week {week}")

    score_breakdown = {}
    with st.form("table_topic_grading_form"):
        topic = st.text_input("Topic", value=grade_data.get('topic', ''))
        time = st.time_input("Time", value=grade_data.get('time', datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)))

        score_breakdown['topic'] = topic
        score_breakdown['time'] = time

        st.write("a. Presentation Quality:")
        first_last_impression = st.slider("First/Last Impression", 0, 10, grade_data.get('first_last_impression', 5))
        balanced_argument = st.slider("Balanced Argument", 0, 10, grade_data.get('balanced_argument', 5))
        follow_up_questions = st.slider("Follow-up Questions", 0, 10, grade_data.get('follow_up_questions', 5))
        stature_vocal = st.slider("Stature and Vocal Quality", 0, 10, grade_data.get('stature_vocal', 5))

        score_breakdown['first_last_impression'] = first_last_impression
        score_breakdown['balanced_argument'] = balanced_argument
        score_breakdown['follow_up_questions'] = follow_up_questions
        score_breakdown['stature_vocal'] = stature_vocal

        subtotal_presentation = first_last_impression + balanced_argument + follow_up_questions + stature_vocal
        st.write(f"Subtotal - Presentation Quality: {subtotal_presentation} out of 40pts")

        st.write("b. Feedback on YouTube:")
        feedback_1 = st.number_input("Feedback for Speaker 1", 0, 10, grade_data.get('feedback_1', 5))
        feedback_2 = st.number_input("Feedback for Speaker 2", 0, 10, grade_data.get('feedback_2', 5))
        self_assessment = st.number_input("Self-Assessment", 0, 10, grade_data.get('self_assessment', 5))

        score_breakdown['feedback_1'] = feedback_1
        score_breakdown['feedback_2'] = feedback_2
        score_breakdown['self_assessment'] = self_assessment

        subtotal_comments = feedback_1 + feedback_2 + self_assessment
        st.write(f"Subtotal - Comments: {subtotal_comments} out of 30pts")

        st.write("c. Deductions:")
        time_deviation = st.number_input("Time deviation from 2 min limit (in 15 sec intervals)", 0, 20, grade_data.get('time_deviation', 0))
        late_comments = st.number_input("Number of late comments", 0, 10, grade_data.get('late_comments', 0))

        score_breakdown['time_deviation'] = time_deviation
        score_breakdown['late_comments'] = late_comments

        deductions = (5 * time_deviation) + (5 * late_comments)
        st.write(f"Total Deductions: {deductions}pts")

        total_grade = subtotal_presentation + subtotal_comments - deductions
        st.write(f"d. Total Grade: {total_grade} out of 70pts")

        comments = st.text_area("e. Comments:", value=grade_data.get('comments', ''))

        score_breakdown['total_grade'] = total_grade
        score_breakdown['comments'] = comments

        submitted = st.form_submit_button("Submit Grade")

        if submitted:
            save_grade(student, "Table Topic", week, total_grade, comments, score_breakdown)
            st.success("Grade submitted successfully!")
            
def camera_assistant_grading_form(student, week, grade_data):
    st.subheader(f"Camera Assistant Grading Form for {student} - Week {week}")
    score_breakdown = {}
    with st.form("camera_assistant_grading_form"):
        st.write("a. Video Footage:")
        video_is_recorded = st.slider("Video is recorded", 0, 20, grade_data.get('video_is_recorded', 10))
        video_is_posted_on_youtube = st.slider("Video is posted on YouTube", 0, 20, grade_data.get('video_is_posted_on_youtube', 10))
        private_video_link_shared = st.slider("Private video link shared", 0, 20, grade_data.get('private_video_link_shared', 10))

        score_breakdown['video_is_recorded'] = video_is_recorded
        score_breakdown['video_is_posted_on_youtube'] = video_is_posted_on_youtube
        score_breakdown['private_video_link_shared'] = private_video_link_shared

        subtotal_video = video_is_recorded + video_is_posted_on_youtube + private_video_link_shared
        st.write(f"Subtotal - Video: {subtotal_video} out of 60pts")

        st.write("b. Deductions:")
        # Video clip posted late is -20pt per day
        video_clip_posted_after_deadline = st.number_input("Number of days video clip posted late", 0, 7, grade_data.get('video_clip_posted_after_deadline', 0))
        data_not_erased_from_sd_card = st.checkbox("Data not erased from SD card", grade_data.get('data_not_erased_from_sd_card', False))
        sd_card_not_returned = st.checkbox("SD card not returned", grade_data.get('sd_card_not_returned', False))
        deductions = (20 * video_clip_posted_after_deadline) + (10 * (data_not_erased_from_sd_card + sd_card_not_returned))
        st.write(f"Total Deductions: {deductions}pts")
        
        score_breakdown['video_clip_posted_after_deadline'] = video_clip_posted_after_deadline
        score_breakdown['data_not_erased_from_sd_card'] = data_not_erased_from_sd_card
        score_breakdown['sd_card_not_returned'] = sd_card_not_returned
        score_breakdown['deductions'] = deductions

        total_grade = subtotal_video - deductions
        st.write(f"d. Total Grade: {total_grade} out of 60pts")
        score_breakdown['total_grade'] = total_grade
        comments = st.text_area("e. Comments:")

        score_breakdown['comments'] = comments
        submitted = st.form_submit_button("Submit Grade")

        if submitted:
            save_grade(student, "Camera Assistant", week, total_grade, comments, score_breakdown)
            st.success("Grade submitted successfully!")
            
            
def group_leader_grading_form(student, week, grade_data):
    st.subheader(f"Group Leader Grading Form for {student} - Week {week}")
    score_breakdown = {}
    
    with st.form("group_leader_grading_form"):
        experiment = st.text_input("Experiment", value=grade_data.get('experiment', ''))
        date = st.date_input("Date", value=grade_data.get('date', datetime.date.today()))
        time = st.time_input("Time", value=grade_data.get('time', datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)))

        score_breakdown['experiment'] = experiment
        score_breakdown['date'] = date
        score_breakdown['time'] = time

        st.write("a. Technical Comprehension:")
        theoretical_background = st.slider("Theoretical Background", 0, 20, grade_data.get('theoretical_background', 10))
        relevance_discussion = st.slider("Discussion of Relevance", 0, 20, grade_data.get('relevance_discussion', 10))
        experiment_description = st.slider("Description of Experiment", 0, 20, grade_data.get('experiment_description', 10))
        calculations_outline = st.slider("Outline of Required Calculations", 0, 20, grade_data.get('calculations_outline', 10))
        result_predictions = st.slider("Predictions for exp. results", 0, 20, grade_data.get('result_predictions', 10))

        score_breakdown['theoretical_background'] = theoretical_background
        score_breakdown['relevance_discussion'] = relevance_discussion
        score_breakdown['experiment_description'] = experiment_description
        score_breakdown['calculations_outline'] = calculations_outline
        score_breakdown['result_predictions'] = result_predictions

        subtotal_technical = theoretical_background + relevance_discussion + experiment_description + calculations_outline + result_predictions
        st.write(f"Subtotal - Technical Comprehension: {subtotal_technical} out of 100pts")

        st.write("b. Speaking Style:")
        personal_presence = st.slider("Personal Presence", 0, 20, grade_data.get('personal_presence', 10))
        professionalism = st.slider("Professionalism", 0, 20, grade_data.get('professionalism', 10))

        score_breakdown['personal_presence'] = personal_presence
        score_breakdown['professionalism'] = professionalism

        subtotal_speaking = personal_presence + professionalism
        st.write(f"Subtotal - Speaking Style: {subtotal_speaking} out of 40pts")

        st.write("c. Quality of Slides:")
        layout_design = st.slider("Layout and Design", 0, 10, grade_data.get('layout_design', 5)) 
        structure_organization = st.slider("Structure and Organization", 0, 10, grade_data.get('structure_organization', 5))
        graphics_quality = st.slider("Quality of Graphics/Tables", 0, 10, grade_data.get('graphics_quality', 5))
        focused_content = st.slider("Focused Content", 0, 10, grade_data.get('focused_content', 5))

        score_breakdown['layout_design'] = layout_design
        score_breakdown['structure_organization'] = structure_organization
        score_breakdown['graphics_quality'] = graphics_quality
        score_breakdown['focused_content'] = focused_content

        subtotal_slides = layout_design + structure_organization + graphics_quality + focused_content
        st.write(f"Subtotal - Quality of Slides: {subtotal_slides} out of 40pts")

        st.write("d. Efficiency of Experiment:")
        experiment_knowledge = st.slider("Knowledge of Experiment", 0, 10, grade_data.get('experiment_knowledge', 5))
        experiment_efficiency = st.slider("Experiment Run Efficiently", 0, 10, grade_data.get('experiment_efficiency', 5))

        score_breakdown['experiment_knowledge'] = experiment_knowledge
        score_breakdown['experiment_efficiency'] = experiment_efficiency

        subtotal_efficiency = experiment_knowledge + experiment_efficiency
        st.write(f"Subtotal - Efficiency of Experiment: {subtotal_efficiency} out of 20pts")

        st.write("e. Feedback on YouTube:")
        no_footage = st.checkbox("No footage available")
        if not no_footage:
            feedback_1 = st.number_input("Technical Feedback for Speaker 1", 0, 10, grade_data.get('feedback_1', 5))
            feedback_2 = st.number_input("Feedback for Speaker 2", 0, 10, grade_data.get('feedback_2', 5))
            feedback_3 = st.number_input("Feedback for Speaker 3", 0, 10, grade_data.get('feedback_3', 5))
            self_assessment = st.number_input("Self-Assessment", 0, 10, grade_data.get('self_assessment', 5))

            score_breakdown['feedback_1'] = feedback_1
            score_breakdown['feedback_2'] = feedback_2
            score_breakdown['feedback_3'] = feedback_3
            score_breakdown['self_assessment'] = self_assessment

            subtotal_feedback = feedback_1 + feedback_2 + feedback_3 + self_assessment
            st.write(f"Subtotal - Feedback: {subtotal_feedback} out of 40pts")
        else:
            st.write("Average score will be credited at the end of the semester")
            subtotal_feedback = 0

            score_breakdown['feedback_1'] = 0
            score_breakdown['feedback_2'] = 0
            score_breakdown['feedback_3'] = 0
            score_breakdown['self_assessment'] = 0

        st.write("f. Deductions:")
        time_deviation = st.number_input("Speaking time deviation from 6 min limit (in 15 sec intervals)", 0, 20, grade_data.get('time_deviation', 0))
        slides_late = st.checkbox("Slides posted less than 24 hrs in advance", grade_data.get('slides_late', False))
        no_handout = st.checkbox("No printed slide handout provided to instructor", grade_data.get('no_handout', False))
        late_comments = st.number_input("Number of late comments", 0, 10, grade_data.get('late_comments', 0))

        score_breakdown['time_deviation'] = time_deviation
        score_breakdown['slides_late'] = slides_late
        score_breakdown['no_handout'] = no_handout
        score_breakdown['late_comments'] = late_comments

        deductions = (5 * time_deviation) + (50 if slides_late else 0) + (20 if no_handout else 0) + (5 * late_comments)
        st.write(f"Total Deductions: {deductions}pts")

        total_grade = subtotal_technical + subtotal_speaking + subtotal_slides + subtotal_efficiency + subtotal_feedback - deductions
        st.write(f"g. Total Grade: {total_grade} out of 200pts")
        score_breakdown['deductions'] = deductions
        score_breakdown['total_grade'] = total_grade

        comments = st.text_area("h. Comments:", value=grade_data.get('comments', ''))
        score_breakdown['comments'] = comments

        submitted = st.form_submit_button("Submit Grade")

        if submitted:
            save_grade(student, "Group Leader", week, total_grade, comments, score_breakdown)
            st.success("Grade submitted successfully!")
            
def group_reporter_grading_form(student, week, grade_data):
    st.subheader(f"Group Reporter Grading Form for {student} - Week {week}")
    score_breakdown = {}
    with st.form("group_reporter_grading_form"):
        experiment = st.text_input("Experiment", value=grade_data.get('experiment', ''))
        date = st.date_input("Date", value=grade_data.get('date', datetime.date.today()))
        time = st.time_input("Time", value=grade_data.get('time', datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)))
        
        score_breakdown['experiment'] = experiment
        score_breakdown['date'] = date
        score_breakdown['time'] = time

        st.write("a. Technical Comprehension:")
        theoretical_background = st.slider("Theoretical Background", 0, 20, grade_data.get('theoretical_background', 10), help="Relationship to Thermodynamics")
        relevance_discussion = st.slider("Discussion of Relevance", 0, 20, grade_data.get('relevance_discussion', 10), help="Goals of experiment, practical applications")
        experiment_description = st.slider("Description of Experiment", 0, 20, grade_data.get('experiment_description', 10), help="Apparatus, procedure, relevant data")
        calculations_outline = st.slider("Outline of Required Calculations", 0, 20, grade_data.get('calculations_outline', 10), help="Relevant equations")
        result_discussion = st.slider("Discussion of Results", 0, 20, grade_data.get('result_discussion', 10), help="Compare results to predictions, discuss errors")

        score_breakdown['theoretical_background'] = theoretical_background
        score_breakdown['relevance_discussion'] = relevance_discussion
        score_breakdown['experiment_description'] = experiment_description
        score_breakdown['calculations_outline'] = calculations_outline
        score_breakdown['result_discussion'] = result_discussion

        subtotal_technical = theoretical_background + relevance_discussion + experiment_description + calculations_outline + result_discussion
        st.write(f"Subtotal - Technical Comprehension: {subtotal_technical} out of 100pts")

        st.write("b. Speaking Style:")
        personal_presence = st.slider("Personal Presence", 0, 20, grade_data.get('personal_presence', 10), help="Self-introduction, introduce topic, wrap-up; eye contact, body movements, voice level, 'ums'")
        professionalism = st.slider("Professionalism", 0, 20, grade_data.get('professionalism', 10), help="Know material without memorization; handling of questions from audience")

        score_breakdown['personal_presence'] = personal_presence
        score_breakdown['professionalism'] = professionalism

        subtotal_speaking = personal_presence + professionalism
        st.write(f"Subtotal - Speaking Style: {subtotal_speaking} out of 40pts")

        st.write("c. Quality of Slides:")
        layout_design = st.slider("Layout and Design", 0, 10, grade_data.get('layout_design', 5), help="Layout/color choice, appropriate font size")
        structure_organization = st.slider("Structure and Organization", 0, 10, grade_data.get('structure_organization', 5), help="Title page, introduction, discussion, conclusion")
        graphics_quality = st.slider("Quality of Graphics/Tables", 0, 10, grade_data.get('graphics_quality', 5), help="Information clearly visible, axes/labels used")
        focused_content = st.slider("Focused Content", 0, 10, grade_data.get('focused_content', 5), help="Key points are clearly made")

        score_breakdown['layout_design'] = layout_design
        score_breakdown['structure_organization'] = structure_organization
        score_breakdown['graphics_quality'] = graphics_quality
        score_breakdown['focused_content'] = focused_content
        subtotal_slides = layout_design + structure_organization + graphics_quality + focused_content
        st.write(f"Subtotal - Quality of Slides: {subtotal_slides} out of 40pts")

        st.write("d. Feedback on YouTube:")
        no_footage = st.checkbox("No footage available", grade_data.get('no_footage', False))
        if not no_footage:
            feedback_1 = st.number_input("Technical Feedback for Speaker 1", 0, 10, grade_data.get('feedback_1', 5))
            feedback_2 = st.number_input("Feedback for Speaker 2", 0, 10, grade_data.get('feedback_2', 5))
            feedback_3 = st.number_input("Feedback for Speaker 3", 0, 10, grade_data.get('feedback_3', 5))
            self_assessment = st.number_input("Self-Assessment", 0, 10, grade_data.get('self_assessment', 5))
            
            score_breakdown['feedback_1'] = feedback_1
            score_breakdown['feedback_2'] = feedback_2
            score_breakdown['feedback_3'] = feedback_3
            score_breakdown['self_assessment'] = self_assessment

            subtotal_feedback = feedback_1 + feedback_2 + feedback_3 + self_assessment
            st.write(f"Subtotal - Feedback: {subtotal_feedback} out of 40pts")
        else:
            st.write("Average score will be credited at the end of the semester")
            subtotal_feedback = 0

            score_breakdown['feedback_1'] = 0
            score_breakdown['feedback_2'] = 0
            score_breakdown['feedback_3'] = 0
            score_breakdown['self_assessment'] = 0

        st.write("e. Deductions:")
        time_deviation = st.number_input("Speaking time deviation from 6 min limit (in 15 sec intervals)", 0, 20, grade_data.get('time_deviation', 0))
        slides_late = st.checkbox("Slides posted less than 24 hrs in advance", grade_data.get('slides_late', False))
        no_handout = st.checkbox("No printed slide handout provided to instructor", grade_data.get('no_handout', False))
        late_comments = st.number_input("Number of late comments", 0, 10, grade_data.get('late_comments', 0))

        score_breakdown['time_deviation'] = time_deviation
        score_breakdown['slides_late'] = slides_late
        score_breakdown['no_handout'] = no_handout
        score_breakdown['late_comments'] = late_comments

        deductions = (5 * time_deviation) + (50 if slides_late else 0) + (20 if no_handout else 0) + (5 * late_comments)
        st.write(f"Total Deductions: {deductions}pts")

        total_grade = subtotal_technical + subtotal_speaking + subtotal_slides + subtotal_feedback - deductions
        st.write(f"f. Total Grade: {total_grade} out of 220pts")
        score_breakdown['deductions'] = deductions
        score_breakdown['total_grade'] = total_grade

        comments = st.text_area("g. Comments:", value=grade_data.get('comments', ''))
        score_breakdown['comments'] = comments

        submitted = st.form_submit_button("Submit Grade")

        if submitted:
            save_grade(student, "Group Reporter", week, total_grade, comments, score_breakdown)
            st.success("Grade submitted successfully!")

def smt_presenter_grading_form(student, week, grade_data):
    st.subheader(f"SMT Presenter Grading Form for {student} - Week {week}")

    score_breakdown = {}
    with st.form("smt_presenter_grading_form"):
        topic = st.text_input("Topic", value=grade_data.get('topic', ''))
        score_breakdown['topic'] = topic
        date = st.date_input("Date", value=grade_data.get('date', datetime.date.today()))
        score_breakdown['date'] = date
        time = st.time_input("Time", value=grade_data.get('time', datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)))
        score_breakdown['time'] = time

        st.write("a. Technical Comprehension:")
        theoretical_background = st.slider("Theoretical Background", 0, 20, grade_data.get('theoretical_background', 10), help="Relationship to Thermodynamics")
        subject_description = st.slider("Description of Subject", 0, 20, grade_data.get('subject_description', 10), help="Depends on topic")
        important_equations = st.slider("Important Equations", 0, 20, grade_data.get('important_equations', 10), help="Relevant equations")
        relevance_discussion = st.slider("Discussion of Relevance", 0, 20, grade_data.get('relevance_discussion', 10), help="Practical applications")
        subject_knowledge = st.slider("Knowledge of Subject", 0, 20, grade_data.get('subject_knowledge', 10), help="Preparedness of the Speaker")
        score_breakdown['theoretical_background'] = theoretical_background
        score_breakdown['subject_description'] = subject_description
        score_breakdown['important_equations'] = important_equations
        score_breakdown['relevance_discussion'] = relevance_discussion
        score_breakdown['subject_knowledge'] = subject_knowledge

        subtotal_technical = theoretical_background + subject_description + important_equations + relevance_discussion + subject_knowledge
        st.write(f"Subtotal - Technical Comprehension: {subtotal_technical} out of 100pts")

        st.write("b. Speaking Style:")
        personal_presence = st.slider("Personal Presence", 0, 20, grade_data.get('personal_presence', 10), help="Self-introduction, introduce topic, wrap-up; eye contact, body movements, voice level, 'ums'")
        professionalism = st.slider("Professionalism", 0, 20, grade_data.get('professionalism', 10), help="Know material without memorization; handling of questions from audience")
        score_breakdown['personal_presence'] = personal_presence
        score_breakdown['professionalism'] = professionalism

        subtotal_speaking = personal_presence + professionalism
        st.write(f"Subtotal - Speaking Style: {subtotal_speaking} out of 40pts")

        st.write("c. Quality of Slides:")
        layout_design = st.slider("Layout and Design", 0, 10, grade_data.get('layout_design', 5), help="Layout/color choice, appropriate font size")
        structure_organization = st.slider("Structure and Organization", 0, 10, grade_data.get('structure_organization', 5), help="Title page, introduction, discussion, conclusion")
        graphics_quality = st.slider("Quality of Graphics/Tables", 0, 10, grade_data.get('graphics_quality', 5), help="Information clearly visible, axes/labels used")
        focused_content = st.slider("Focused Content", 0, 10, grade_data.get('focused_content', 5), help="Key points are clearly made")
        
        score_breakdown['layout_design'] = layout_design
        score_breakdown['structure_organization'] = structure_organization
        score_breakdown['graphics_quality'] = graphics_quality
        score_breakdown['focused_content'] = focused_content

        subtotal_slides = layout_design + structure_organization + graphics_quality + focused_content
        st.write(f"Subtotal - Quality of Slides: {subtotal_slides} out of 40pts")

        st.write("d. Appropriateness of Topic:")
        topic_suitability = st.slider("Topic suitable for 6 min. talk?", 0, 10, grade_data.get('topic_suitability', 5))
        topic_relevance = st.slider("Relevance to Thermodynamics", 0, 10, grade_data.get('topic_relevance', 5))

        score_breakdown['topic_suitability'] = topic_suitability
        score_breakdown['topic_relevance'] = topic_relevance

        subtotal_topic = topic_suitability + topic_relevance
        st.write(f"Subtotal - Appropriateness of Topic: {subtotal_topic} out of 20pts")

        st.write("e. Feedback on YouTube:")
        no_footage = st.checkbox("No footage available")
        if not no_footage:
            feedback_1 = st.number_input("Feedback for Speaker 1", 0, 10, grade_data.get('feedback_1', 5))
            feedback_2 = st.number_input("Feedback for Speaker 2", 0, 10, grade_data.get('feedback_2', 5))
            feedback_3 = st.number_input("Feedback for Speaker 3", 0, 10, grade_data.get('feedback_3', 5))
            self_assessment = st.number_input("Self-Assessment", 0, 10, grade_data.get('self_assessment', 5))

            subtotal_feedback = feedback_1 + feedback_2 + feedback_3 + self_assessment
            st.write(f"Subtotal - Feedback: {subtotal_feedback} out of 40pts")
            
            score_breakdown['feedback_1'] = feedback_1
            score_breakdown['feedback_2'] = feedback_2
            score_breakdown['feedback_3'] = feedback_3
            score_breakdown['self_assessment'] = self_assessment
        else:
            st.write("Average score will be credited at the end of the semester")
            subtotal_feedback = 0
            
            score_breakdown['feedback_1'] = 0
            score_breakdown['feedback_2'] = 0
            score_breakdown['feedback_3'] = 0
            score_breakdown['self_assessment'] = 0
            score_breakdown['feedback_1'] = 0

        st.write("f. Deductions:")
        
        time_deviation = st.number_input("Speaking time deviation from 6 min limit (in 15 sec intervals)", 0, 20, grade_data.get('time_deviation', 0))
        slides_late = st.checkbox("Slides posted less than 24 hrs in advance", grade_data.get('slides_late', False))
        no_handout = st.checkbox("No printed slide handout provided to instructor", grade_data.get('no_handout', False))
        subject_not_approved = st.number_input("Days subject not approved one week in advance", 0, 7, grade_data.get('subject_not_approved', 0))
        late_comments = st.number_input("Number of late comments", 0, 10, grade_data.get('late_comments', 0))
        
        score_breakdown['time_deviation'] = time_deviation
        score_breakdown['slides_late'] = slides_late
        score_breakdown['no_handout'] = no_handout
        score_breakdown['subject_not_approved'] = subject_not_approved
        score_breakdown['late_comments'] = late_comments

        deductions = (5 * time_deviation) + (50 if slides_late else 0) + (20 if no_handout else 0) + (50 * subject_not_approved) + (5 * late_comments)
        st.write(f"Total Deductions: {deductions}pts")

        total_grade = subtotal_technical + subtotal_speaking + subtotal_slides + subtotal_topic + subtotal_feedback - deductions
        st.write(f"g. Total Grade: {total_grade} out of 220pts")
        score_breakdown['deductions'] = deductions
        score_breakdown['total_grade'] = total_grade

        comments = st.text_area("h. Comments:", value=grade_data.get('comments', ''))
        score_breakdown['comments'] = comments
        submitted = st.form_submit_button("Submit Grade")
        
        if submitted:
            save_grade(student, "SMT", week, total_grade, comments, score_breakdown)
            st.success("Grade submitted successfully!")
            
def download_rubric():
    st.subheader("Download Graded Rubric")

    students = get_students()
    roles = get_roles()
    grades = get_grades()

    student = st.selectbox("Select Student", students['name'].tolist(), key="download_student")
    role = st.selectbox("Select Role", roles['name'].tolist(), key="download_role")
    available_weeks = grades[(grades['student_id'] == students[students['name'] == student]['id'].iloc[0]) & 
                             (grades['role_id'] == roles[roles['name'] == role]['id'].iloc[0])]['week'].tolist()
    week = st.selectbox("Select Week", available_weeks, key="download_week")

    if st.button("Generate Rubric"):
        grade_data = grades[(grades['student_id'] == students[students['name'] == student]['id'].iloc[0]) & 
                            (grades['role_id'] == roles[roles['name'] == role]['id'].iloc[0]) & 
                            (grades['week'] == week)].iloc[0]

        rubric_data = {
            'first_last_impression': grade_data['first_last_impression'],
            'transitions': grade_data['transitions'],
            'timing_questions': grade_data['timing_questions'],
            'stature_vocal': grade_data['stature_vocal'],
            'subtotal_moderation': grade_data['subtotal_moderation'],
            'subtotal_comments': grade_data['subtotal_comments'],
            'deductions': grade_data['deductions'],
            'total_grade': grade_data['score'],
            'comments': grade_data['comments'],
        }

        pdf_buffer = generate_rubric_pdf(role, rubric_data)
        st.download_button(
            label="Download Graded Rubric",
            data=pdf_buffer,
            file_name=f"{student}_{role}_Week{week}_Rubric.pdf",
            mime="application/pdf"
        )


def date_time_serializer(obj):
    if isinstance(obj, (date, time)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def save_grade(student, role, week, total_grade, comments, score_breakdown):
    print(score_breakdown)
    grades_df = pd.read_csv("data/grades.csv")
    new_grade = pd.DataFrame({
        "id": [len(grades_df) + 1],
        "student_id": [get_students()[get_students()['name'] == student].iloc[0]['id']],
        "role_id": [get_roles()[get_roles()['name'] == role].iloc[0]['id']],
        "week": [week],
        "total_score": [total_grade],
        "comments": [comments],
        "score_breakdown": [json.dumps(score_breakdown, default=date_time_serializer)],
        "timestamp": [pd.Timestamp.now()]
    })
    grades_df = pd.concat([grades_df, new_grade], ignore_index=True)
    save_grades(grades_df)
    return None
    