import streamlit as st
from datetime import datetime
from supabase import create_client

# Supabase connection
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MedFollow",
    page_icon="🩺",
    layout="centered"
)

# --------------------------------------------------
# DEMO DATA
# --------------------------------------------------

patients = {
    "demo123": {
        "name": "Ahmed Khan",
        "age": 52,
        "doctor": "Dr. Mustafa",
        "last_consultation": "12 September 2026",
        "reason": "Diabetes follow-up",
        "previous_plan": (
            "Patient was advised to complete HbA1c, "
            "creatinine and lipid profile after follow-up."
        )
    },
    "demo456": {
        "name": "Sara Ali",
        "age": 38,
        "doctor": "Dr. Mustafa",
        "last_consultation": "15 September 2026",
        "reason": "Thyroid follow-up",
        "previous_plan": (
            "Patient was advised to repeat thyroid function tests."
        )
    }
}

# --------------------------------------------------
# DEMO SUBMISSIONS
# --------------------------------------------------

if "submissions" not in st.session_state:
    st.session_state.submissions = []

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🩺 MedFollow")

st.caption(
    "A simple follow-up communication portal for doctors and patients."
)

# --------------------------------------------------
# DEMO WARNING
# --------------------------------------------------

st.warning(
    "DEMO VERSION — Use fictional patient information only. "
    "Do not upload real patient medical records."
)

# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

mode = st.sidebar.radio(
    "Select mode",
    [
        "Patient Follow-up Link",
        "Doctor Dashboard"
    ]
)

# ==================================================
# PATIENT FOLLOW-UP LINK
# ==================================================

if mode == "Patient Follow-up Link":

    st.header("Submit Follow-up Report")

    st.write(
        "Use this page to send a laboratory report, "
        "medical report, or home readings to your doctor."
    )

    st.divider()

    # Patient link/token
    patient_code = st.selectbox(
        "Demo patient link",
        ["demo123", "demo456"]
    )

    patient = patients[patient_code]

    st.info(
        f"This link is for **{patient['doctor']}**"
    )

    st.subheader("Patient information")

    patient_name = st.text_input(
        "Patient name",
        value=patient["name"]
    )

    contact = st.text_input(
        "Phone number or email"
    )

    st.subheader("What are you submitting?")

    submission_type = st.selectbox(
        "Select type",
        [
            "Laboratory report",
            "Blood pressure readings",
            "Blood glucose readings",
            "Imaging report",
            "Medical record",
            "Other"
        ]
    )

    uploaded_file = st.file_uploader(
        "Upload your report or image",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg"
        ]
    )

    message = st.text_area(
        "Message for your doctor",
        placeholder=(
            "Example: I completed the blood tests as advised "
            "during my previous consultation."
        )
    )

    st.divider()

    st.subheader("Previous consultation")

    st.write(
        f"**Last consultation:** "
        f"{patient['last_consultation']}"
    )

    st.write(
        f"**Reason:** {patient['reason']}"
    )

    st.write(
        f"**Previous plan:** {patient['previous_plan']}"
    )

    st.divider()

    if st.button(
        "Submit for Doctor Review",
        type="primary",
        use_container_width=True
    ):

        if not patient_name:
            st.error("Please enter your name.")

        elif uploaded_file is None:
            st.error("Please upload a report or reading.")

        else:

            submission = {
                "patient": patient_name,
                "patient_code": patient_code,
                "contact": contact,
                "type": submission_type,
                "file_name": uploaded_file.name,
                "message": message,
                "time": datetime.now().strftime(
                    "%d %B %Y, %I:%M %p"
                ),
                "status": "Awaiting doctor review"
            }

            st.session_state.submissions.append(
                submission
            )

            st.success(
                "Your report has been submitted successfully."
            )

            st.info(
                "Your doctor will review the submission "
                "and provide further instructions."
            )


# ==================================================
# DOCTOR DASHBOARD
# ==================================================

else:

    # -----------------------------
    # DOCTOR LOGIN
    # -----------------------------

    if "doctor_logged_in" not in st.session_state:
        st.session_state.doctor_logged_in = False

    if not st.session_state.doctor_logged_in:

        st.header("Doctor Login")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Log in", type="primary"):

            try:
                auth_response = supabase.auth.sign_in_with_password(
                    {
                        "email": email,
                        "password": password
                    }
                )

                if auth_response.session:
                    st.session_state.doctor_logged_in = True
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")

            except Exception as e:
                st.error("Login failed. Please check your email and password.")

        st.stop()

    # -----------------------------
    # DOCTOR DASHBOARD
    # -----------------------------
        # -----------------------------
    # TEST SUPABASE DATABASE ACCESS
    # -----------------------------

    try:
        current_user = supabase.auth.get_user().user

        doctor_profile = (
            supabase
            .table("doctors")
            .select("id, name")
            .eq("id", current_user.id)
            .single()
            .execute()
        )

        if doctor_profile.data:
            st.success(
                f"Connected to Supabase — {doctor_profile.data['name']}"
            )
        else:
            st.error("Doctor profile not found.")

    except Exception as e:
    st.error("Could not access the doctor profile.")
    st.exception(e)

    st.header("Doctor Dashboard")

    st.write(
        "Welcome, **Dr. Mustafa**"
    )

    st.divider()

    st.subheader("Follow-up submissions")

    if len(st.session_state.submissions) == 0:

        st.info(
            "No new patient submissions yet."
        )

    else:

        for index, submission in enumerate(
            st.session_state.submissions
        ):

            with st.expander(
                f"🔴 {submission['patient']} — "
                f"{submission['type']}"
            ):

                st.write(
                    f"**Submitted:** "
                    f"{submission['time']}"
                )

                st.write(
                    f"**Contact:** "
                    f"{submission['contact']}"
                )

                st.write(
                    f"**File:** "
                    f"{submission['file_name']}"
                )

                st.write(
                    f"**Patient message:** "
                    f"{submission['message'] or 'No message provided.'}"
                )

                st.divider()

                st.subheader("Doctor response")

                response = st.radio(
                    "Select action",
                    [
                        "Continue previously prescribed treatment",
                        "Book follow-up appointment",
                        "Call clinic promptly",
                        "Custom response"
                    ],
                    key=f"response_{index}"
                )

                if response == "Continue previously prescribed treatment":

                    default_message = (
                        "Your report has been reviewed. "
                        "Please continue your previously "
                        "prescribed treatment as advised."
                    )

                elif response == "Book follow-up appointment":

                    default_message = (
                        "Your report has been reviewed. "
                        "Please book a follow-up appointment "
                        "to discuss the results."
                    )

                elif response == "Call clinic promptly":

                    default_message = (
                        "Your report has been reviewed. "
                        "Please contact the clinic promptly."
                    )

                else:

                    default_message = ""

                doctor_message = st.text_area(
                    "Message to patient",
                    value=default_message,
                    key=f"message_{index}",
                    height=120
                )

                if st.button(
                    "Mark as Reviewed",
                    key=f"review_{index}",
                    type="primary"
                ):

                    submission["status"] = "Reviewed"
                    submission["doctor_response"] = (
                        doctor_message
                    )

                    st.success(
                        "Submission marked as reviewed."
                    )

                    st.write(
                        "**Patient response:**"
                    )

                    st.info(
                        doctor_message
                    )

# ==================================================
# ABOUT
# ==================================================

st.divider()

with st.expander("About MedFollow"):

    st.write(
        """
        MedFollow is a prototype for doctor-patient follow-up
        communication.

        The goal is to allow doctors to give patients a dedicated
        follow-up link instead of sharing their personal phone number.

        Patients can use the link to submit reports or readings
        requested during a previous consultation.

        The doctor then reviews the submission and decides the
        appropriate next step.
        """
    )
