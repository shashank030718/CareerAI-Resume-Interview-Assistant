

import streamlit as st

import requests





# --------------------------------------------------

# 1. CONFIGURATION

# --------------------------------------------------



API_URL = "http://127.0.0.1:8000"

REQUEST_TIMEOUT = (10, 600)



st.set_page_config(

    page_title="AI Resume & Interview Assistant",

    page_icon="🚀",

    layout="wide"

)





# --------------------------------------------------

# 2. BACKEND CONNECTION

# --------------------------------------------------



def check_backend():

    try:

        response = requests.get(

            f"{API_URL}/",

            timeout=(5, 10)

        )

        return response.ok

    except requests.exceptions.RequestException:

        return False





def show_api_error(response):

    try:

        error_data = response.json()

        detail = error_data.get("detail", error_data)

        st.error(f"API Error: {detail}")

    except ValueError:

        st.error(f"API Error: {response.text}")





# --------------------------------------------------

# 3. COMMON DISPLAY HELPERS

# --------------------------------------------------



def display_list(items):

    """Display a list as clean bullet points."""

    if isinstance(items, list):

        if items:

            for item in items:

                st.markdown(f"- {item}")

        else:

            st.caption("No information available.")

    elif items:

        st.write(items)

    else:

        st.caption("No information available.")





def display_skill_tags(skills):

    """Display skills as compact badges."""

    if not isinstance(skills, list) or not skills:

        st.caption("No skills found.")

        return



    st.markdown(

        " ".join([f"`{skill}`" for skill in skills])

    )





# --------------------------------------------------

# 4. RESUME ANALYSIS DISPLAY

# --------------------------------------------------



def display_resume_analysis(result):



    analysis = result.get("analysis", result)



    st.success("Resume analysis completed successfully!")



    st.caption(

        f"Resume file: {result.get('filename', 'Uploaded Resume')}"

    )



    # Candidate overview

    st.divider()

    st.subheader("👤 Candidate Overview")



    st.title(

        analysis.get("candidate_name", "Candidate")

    )



    st.write(

        analysis.get(

            "professional_summary",

            "No professional summary available."

        )

    )



    # Technical skills

    st.divider()

    st.subheader("💻 Technical Skills")



    col1, col2 = st.columns(2)



    with col1:

        st.markdown("**Technical Skills**")

        display_skill_tags(

            analysis.get("technical_skills", [])

        )



        st.markdown("**Programming Languages**")

        display_skill_tags(

            analysis.get("programming_languages", [])

        )



    with col2:

        st.markdown("**Tools and Frameworks**")

        display_skill_tags(

            analysis.get("tools_and_frameworks", [])

        )



    # Education

    st.divider()

    st.subheader("🎓 Education")



    education = analysis.get("education", [])



    if education:

        for item in education:

            with st.container(border=True):

                st.markdown(

                    f"**{item.get('degree', 'Degree not specified')}**"

                )

                st.write(

                    item.get("institution", "Institution not specified")

                )



                details = [

                    item.get("location", ""),

                    item.get("duration", "")

                ]



                st.caption(" | ".join(x for x in details if x))



                if item.get("gpa"):

                    st.write(f"**CGPA:** {item['gpa']}")

    else:

        st.info("No education details found.")



    # Projects

    st.divider()

    st.subheader("🚀 Projects")



    projects = analysis.get("projects", [])



    if projects:

        for project in projects:

            with st.expander(

                project.get("title", "Project"),

                expanded=False

            ):

                st.write(

                    project.get(

                        "objective_and_achievements",

                        "No project description available."

                    )

                )



                technologies = project.get("technologies", [])



                if technologies:

                    st.markdown("**Technologies Used**")

                    display_skill_tags(technologies)



                if project.get("duration"):

                    st.caption(

                        f"Duration: {project['duration']}"

                    )

    else:

        st.info("No projects found.")



    # Experience

    st.divider()

    st.subheader("💼 Professional Experience")



    experience = analysis.get("experience", [])



    if experience:

        for item in experience:

            with st.container(border=True):

                if isinstance(item, dict):

                    st.markdown(

                        f"**{item.get('role', item.get('title', 'Experience'))}**"

                    )



                    for key, value in item.items():

                        if key not in ["role", "title"] and value:

                            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                else:

                    st.write(item)

    else:

        st.info("No professional experience details found in the resume.")



    # Certifications

    st.divider()

    st.subheader("🏆 Certifications")



    certifications = analysis.get("certifications", [])



    if certifications:

        for cert in certifications:

            if isinstance(cert, dict):

                st.markdown(

                    f"**{cert.get('title', 'Certification')}**"

                )

                st.caption(

                    f"{cert.get('issuer', '')} | "

                    f"{cert.get('issued_date', '')}"

                )

            else:

                st.write(cert)

    else:

        st.info("No certifications found.")



    # Strengths and improvements

    st.divider()

    st.subheader("📊 Resume Evaluation")



    col1, col2 = st.columns(2)



    with col1:

        st.markdown("### ✅ Strengths")

        display_list(analysis.get("strengths", []))



    with col2:

        st.markdown("### 📈 Areas to Improve")

        display_list(analysis.get("areas_to_improve", []))





# --------------------------------------------------

# 5. JOB MATCH RESULTS DISPLAY

# --------------------------------------------------



def display_job_match(result):



    st.success("Job matching completed successfully!")



    st.caption(

        f"Resume: {result.get('filename', 'Uploaded Resume')}"

    )



    score = result.get("match_score", 0)



    if isinstance(score, (int, float)):

        score = max(0, min(100, score))



        st.divider()

        st.subheader("🎯 Resume Match Score")



        col1, col2 = st.columns([1, 3])



        with col1:

            st.metric(

                "Match Percentage",

                f"{score:.0f}%"

            )



        with col2:

            st.progress(score / 100)



            if score >= 80:

                st.success("Strong match for this job role.")

            elif score >= 60:

                st.info("Good match, with some skills to improve.")

            else:

                st.warning("Your resume needs improvement for this role.")



    # Overall assessment

    st.divider()

    st.subheader("📋 Overall Assessment")



    st.write(

        result.get(

            "overall_assessment",

            "No assessment available."

        )

    )



    # Skill comparison

    st.divider()

    st.subheader("🧠 Skills Comparison")



    col1, col2, col3 = st.columns(3)



    with col1:

        with st.container(border=True):

            st.markdown("### ✅ Matching Skills")

            display_list(

                result.get("matching_skills", [])

            )



    with col2:

        with st.container(border=True):

            st.markdown("### ❌ Missing Skills")

            display_list(

                result.get("missing_skills", [])

            )



    with col3:

        with st.container(border=True):

            st.markdown("### ⚡ Partially Matching")

            display_list(

                result.get("partially_matching_skills", [])

            )



    # Relevant projects

    st.divider()

    st.subheader("🚀 Relevant Projects")



    display_list(

        result.get("relevant_projects", [])

    )



    # Strengths and recommendations

    st.divider()



    col1, col2 = st.columns(2)



    with col1:

        st.subheader("💪 Your Strengths")

        display_list(

            result.get("strengths", [])

        )



    with col2:

        st.subheader("📝 Recommendations")

        display_list(

            result.get("recommendations", [])

        )



    # Learning suggestions

    st.divider()

    st.subheader("📚 Recommended Learning Topics")



    display_list(

        result.get("learning_suggestions", [])

    )





# --------------------------------------------------

# 6. INTERVIEW QUESTIONS DISPLAY

# --------------------------------------------------



def display_interview_questions(result):



    st.success(

        "Interview questions generated successfully!"

    )



    st.caption(

        f"Target Role: {result.get('job_role', 'Not specified')}"

    )



    categories = [

        ("python_questions", "🐍 Python Interview Questions"),

        ("sql_questions", "🗄️ SQL Interview Questions"),

        ("project_questions", "🚀 Project-Based Questions"),

        ("hr_questions", "🤝 HR Interview Questions")

    ]



    for category, heading in categories:



        questions = result.get(category, [])



        if not isinstance(questions, list):

            continue



        st.divider()

        st.subheader(heading)



        if not questions:

            st.info("No questions available in this category.")

            continue



        for index, item in enumerate(questions, start=1):



            if isinstance(item, dict):

                question = item.get(

                    "question",

                    "Question unavailable"

                )



                answer = item.get(

                    "suggested_answer",

                    "Answer unavailable"

                )



                explanation = item.get(

                    "explanation",

                    "Explanation unavailable"

                )



            elif isinstance(item, str):

                question = item

                answer = "Not available"

                explanation = "Not available"



            else:

                continue



            with st.expander(

                f"Question {index}: {question}",

                expanded=False

            ):



                st.markdown("**💡 Suggested Answer**")

                st.write(answer)



                st.markdown("**📖 Explanation**")

                st.write(explanation)





# --------------------------------------------------

# 7. APPLICATION HEADER

# --------------------------------------------------



st.title("🚀 AI Resume & Interview Preparation Assistant")



st.write(

    "Analyze your resume, match job descriptions, "

    "and prepare for interviews using Gemini AI."

)





# --------------------------------------------------

# 8. SIDEBAR STATUS

# --------------------------------------------------



with st.sidebar:



    st.header("⚙️ System Status")



    if check_backend():

        st.success("Backend Connected")

    else:

        st.error("Backend Not Connected")

        st.caption("Start FastAPI before using the application.")



    st.caption("FastAPI: 127.0.0.1:8000")

    st.caption("Streamlit: 127.0.0.1:8501")



    st.divider()



    st.markdown("### Appearance")
    theme = st.radio(
        "Choose theme",
        ["Light", "Dark"],
        horizontal=True,
        key="app_theme",
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### About")

    st.write(

        "An AI-powered assistant that helps candidates "

        "analyze resumes, evaluate job compatibility "

        "and prepare for technical interviews."

    )





# --------------------------------------------------

# 9. THEME STYLING
# --------------------------------------------------

if theme == "Dark":
    page_bg = "#0E1117"
    panel_bg = "#171B26"
    text_color = "#F3F4F6"
    muted_color = "#A7AFBF"
    border_color = "#303747"
    accent_color = "#A78BFA"
else:
    page_bg = "#F5F7FB"
    panel_bg = "#FFFFFF"
    text_color = "#20263A"
    muted_color = "#687086"
    border_color = "#E4E8F0"
    accent_color = "#6558D3"

st.markdown(
    f"""
    <style>
    .stApp {{ background: {page_bg}; color: {text_color}; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{ background: {panel_bg}; border-right: 1px solid {border_color}; }}
    [data-testid="stSidebar"] * {{ color: {text_color}; }}
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1450px; }}
    h1, h2, h3 {{ color: {text_color}; letter-spacing: -0.03em; }}
    p, li, label, [data-testid="stMarkdownContainer"] {{ color: {text_color}; }}
    [data-testid="stCaptionContainer"] {{ color: {muted_color}; }}
    [data-testid="stMetric"] {{ background: {panel_bg}; padding: 1rem; border-radius: 14px; border: 1px solid {border_color}; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ background: {panel_bg}; border-color: {border_color}; border-radius: 14px; }}
    [data-testid="stFileUploader"] section {{ background: {panel_bg}; border: 1px dashed {border_color}; border-radius: 14px; }}
    .stTextArea textarea, .stTextInput input {{ background: {panel_bg}; color: {text_color}; border-color: {border_color}; border-radius: 10px; }}
    .stButton > button {{ border-radius: 10px; border: 1px solid {accent_color}; font-weight: 600; min-height: 2.7rem; }}
    div[data-testid="stProgressBar"] > div > div {{ background-color: {accent_color}; }}
    [data-testid="stExpander"] {{ background: {panel_bg}; border: 1px solid {border_color}; border-radius: 12px; }}
    [data-baseweb="tab-list"] {{ gap: 0.5rem; }}
    [data-baseweb="tab"] {{ border-radius: 10px 10px 0 0; }}
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 10. CREATE APPLICATION TABS

# --------------------------------------------------



tab1, tab2, tab3 = st.tabs([

    "📄 Resume Analyzer",

    "🎯 Job Matcher",

    "💼 Interview Preparation"

])





# --------------------------------------------------

# 10. TAB 1 - RESUME ANALYZER

# --------------------------------------------------



with tab1:



    st.header("📄 Resume Analysis")



    st.write(

        "Upload your PDF resume to receive an AI-powered "

        "analysis of your professional profile."

    )



    resume = st.file_uploader(

        "Upload your resume (PDF)",

        type=["pdf"],

        key="resume_analyzer"

    )



    if st.button(

        "Analyze Resume",

        key="analyze_button",

        type="primary"

    ):



        if resume is None:

            st.warning("Please upload your resume.")



        else:



            with st.spinner(

                "Analyzing your resume with Gemini AI..."

            ):



                try:

                    response = requests.post(

                        f"{API_URL}/analyze-resume",

                        files={

                            "file": (

                                resume.name,

                                resume.getvalue(),

                                "application/pdf"

                            )

                        },

                        timeout=REQUEST_TIMEOUT

                    )



                    if response.ok:

                        result = response.json()

                        display_resume_analysis(result)



                    else:

                        show_api_error(response)



                except requests.exceptions.ConnectTimeout:

                    st.error(

                        "Could not connect to the backend. "

                        "Check whether FastAPI is running."

                    )



                except requests.exceptions.ReadTimeout:

                    st.error(

                        "The backend did not respond within "

                        "10 minutes. Check the FastAPI terminal "

                        "and Gemini API."

                    )



                except requests.exceptions.RequestException as error:

                    st.error(f"Request failed: {error}")



                except (ValueError, TypeError) as error:

                    st.error(

                        f"Could not display the analysis result: {error}"

                    )





# --------------------------------------------------

# 11. TAB 2 - JOB DESCRIPTION MATCHER

# --------------------------------------------------



with tab2:



    st.header("🎯 Job Description Matching")



    st.write(

        "Compare your resume against a job description "

        "and identify your skill gaps."

    )



    job_resume = st.file_uploader(

        "Upload your resume (PDF)",

        type=["pdf"],

        key="job_matcher"

    )



    job_description = st.text_area(

        "Paste the job description",

        height=200,

        placeholder="Paste the complete job description here..."

    )



    if st.button(

        "Match My Resume",

        key="match_button",

        type="primary"

    ):



        if job_resume is None:

            st.warning("Please upload your resume.")



        elif not job_description.strip():

            st.warning("Please enter a job description.")



        else:



            with st.spinner(

                "Matching your resume with the job..."

            ):



                try:

                    response = requests.post(

                        f"{API_URL}/match-job",

                        files={

                            "file": (

                                job_resume.name,

                                job_resume.getvalue(),

                                "application/pdf"

                            )

                        },

                        data={

                            "job_description": job_description

                        },

                        timeout=REQUEST_TIMEOUT

                    )



                    if response.ok:

                        result = response.json()

                        display_job_match(result)



                    else:

                        show_api_error(response)



                except requests.exceptions.ConnectTimeout:

                    st.error(

                        "Could not connect to the backend. "

                        "Check whether FastAPI is running."

                    )



                except requests.exceptions.ReadTimeout:

                    st.error(

                        "The backend did not respond within "

                        "10 minutes. Check the FastAPI terminal "

                        "and Gemini API."

                    )



                except requests.exceptions.RequestException as error:

                    st.error(f"Request failed: {error}")



                except (ValueError, TypeError) as error:

                    st.error(

                        f"Could not display job match results: {error}"

                    )





# --------------------------------------------------

# 12. TAB 3 - INTERVIEW PREPARATION

# --------------------------------------------------



with tab3:



    st.header("💼 Interview Question Generator")



    st.write(

        "Generate personalized technical and HR interview "

        "questions based on your resume and target job role."

    )



    interview_resume = st.file_uploader(

        "Upload your resume (PDF)",

        type=["pdf"],

        key="interview_prep"

    )



    job_role = st.text_input(

        "Enter the job role",

        placeholder="Example: Python Developer"

    )



    if st.button(

        "Generate Interview Questions",

        key="interview_button",

        type="primary"

    ):



        if interview_resume is None:

            st.warning("Please upload your resume.")



        elif not job_role.strip():

            st.warning("Please enter a job role.")



        else:



            with st.spinner(

                "Generating interview questions using Gemini AI..."

            ):



                try:

                    response = requests.post(

                        f"{API_URL}/generate-questions",

                        files={

                            "file": (

                                interview_resume.name,

                                interview_resume.getvalue(),

                                "application/pdf"

                            )

                        },

                        data={

                            "job_role": job_role

                        },

                        timeout=REQUEST_TIMEOUT

                    )



                    if response.ok:

                        result = response.json()

                        display_interview_questions(result)



                    else:

                        show_api_error(response)



                except requests.exceptions.ConnectTimeout:

                    st.error(

                        "Could not connect to the backend. "

                        "Check whether FastAPI is running."

                    )



                except requests.exceptions.ReadTimeout:

                    st.error(

                        "The backend did not respond within "

                        "10 minutes. Check the FastAPI terminal "

                        "and Gemini API."

                    )



                except requests.exceptions.RequestException as error:

                    st.error(f"Request failed: {error}")



                except (ValueError, TypeError) as error:

                    st.error(

                        f"Could not display interview questions: {error}"

                    )





# --------------------------------------------------

# 13. FOOTER

# --------------------------------------------------



st.divider()



st.caption(

    "AI Resume & Interview Preparation Assistant | "

    "Built with FastAPI, Streamlit and Gemini AI"

)
