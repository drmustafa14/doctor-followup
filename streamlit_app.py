import streamlit as st
from urllib.parse import quote
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from supabase import create_client

# Supabase connection
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# Restore Supabase session after Streamlit reruns
if (
    "supabase_access_token" in st.session_state
    and "supabase_refresh_token" in st.session_state
):
    try:
        supabase.auth.set_session(
            st.session_state.supabase_access_token,
            st.session_state.supabase_refresh_token
        )
    except Exception:
        pass

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MedFollow",
    page_icon="🩺",
    layout="centered"
)
# -----------------------------
# PATIENT FOLLOW-UP LINK
# -----------------------------

patient_token = st.query_params.get("token")

if patient_token:

    st.header("MedFollow")

    try:
        request_response = (
            supabase
            .rpc(
                "get_follow_up_request_by_token",
                {"p_token": patient_token}
            )
            .execute()
        )

        request_data = request_response.data

        if not request_data:
            st.error(
                "This follow-up link is invalid, expired, or has already been used."
            )
            st.stop()

        request = request_data[0]

        st.subheader("Follow-up Request")

        st.write(
            f"**Patient:** {request['patient_name']}"
        )

        st.write(
            f"**Requested submission:** {request['request_type']}"
        )

        if request.get("instructions"):
            st.info(request["instructions"])

        st.success("This follow-up link is active.")

        st.divider()

        st.subheader("Submit Your Report")

        uploaded_file = st.file_uploader(
            "Upload your report",
            type=["pdf", "png", "jpg", "jpeg"],
            key="patient_report"
        )

        patient_message = st.text_area(
            "Message for the doctor (optional)",
            placeholder="Add any information you would like the doctor to know.",
            key="patient_message"
        )

        if st.button(
            "Submit Follow-up",
            type="primary",
            key="submit_followup"
        ):

            if uploaded_file is None:
                st.warning("Please upload your report before submitting.")

            else:

                try:
                    file_name = uploaded_file.name
                    file_path = (
                        f"{patient_token}/"
                        f"{token_urlsafe(8)}_{file_name}"
                    )

                    supabase.storage.from_(
                        "patient-reports"
                    ).upload(
                        file_path,
                        uploaded_file.getvalue(),
                        {
                            "content-type": uploaded_file.type,
                            "upsert": "false"
                        }
                    )

                    submission_response = (
                        supabase
                        .rpc(
                            "submit_follow_up",
                            {
                                "p_token": patient_token,
                                "p_message": patient_message,
                                "p_file_name": file_name,
                                "p_file_path": file_path
                            }
                        )
                        .execute()
                    )

                    result = submission_response.data

                    if result and result.get("success"):
                        st.success(
                            "Your report has been submitted successfully."
                        )
                        st.info(
                            "The doctor will review your submission."
                        )
                        st.stop()

                    else:
                        st.error(
                            result.get(
                                "error",
                                "The submission could not be completed."
                            )
                        )

                except Exception:
                    st.error(
                        "We could not submit your report. "
                        "Please try again."
                    )

        st.stop()

    except Exception:
        st.error("Unable to load this follow-up request.")
        st.stop()

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
# =================================================
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
                    st.session_state.supabase_access_token = auth_response.session.access_token
                    st.session_state.supabase_refresh_token = auth_response.session.refresh_token
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")

            except Exception as e:
                st.error("Login failed. Please check your email and password.")

        st.stop()

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

    # -----------------------------
    # DOCTOR DASHBOARD
    # -----------------------------

    st.header("Doctor Dashboard")



    st.write(
        "Welcome, **Dr. Mustafa**"
    )
        # -----------------------------
    # PATIENTS
    # -----------------------------

    st.divider()
    st.subheader("Patients")

    try:
        current_user = supabase.auth.get_user().user

        patients_response = (
            supabase
            .table("patients")
            .select("id, name, contact, created_at")
            .eq("doctor_id", current_user.id)
            .order("created_at", desc=True)
            .execute()
        )

        patients_data = patients_response.data or []

        if patients_data:
            for patient in patients_data:
                with st.expander(patient["name"]):
                    st.write(
                        f"**Contact:** "
                        f"{patient.get('contact') or 'Not provided'}"
                    )
        else:
            st.info("No patients added yet.")

    except Exception as e:
        st.error("Could not load patients.")
        st.exception(e)

    # -----------------------------
    # ADD PATIENT
    # -----------------------------

    st.subheader("Add Patient")

    patient_name = st.text_input(
        "Patient name",
        key="new_patient_name"
    )

    patient_contact = st.text_input(
        "Phone number or email",
        key="new_patient_contact"
    )

    if st.button("Add patient", type="primary"):

        if not patient_name.strip():
            st.warning("Please enter the patient's name.")

        else:
            try:
                current_user = supabase.auth.get_user().user

                supabase.table("patients").insert(
                    {
                        "doctor_id": current_user.id,
                        "name": patient_name.strip(),
                        "contact": patient_contact.strip() or None
                    }
                ).execute()

                st.success(
                    f"Patient '{patient_name.strip()}' added successfully."
                )

                st.rerun()

            except Exception as e:
                st.error("Could not add the patient.")
                st.exception(e)
        # -----------------------------
    # CREATE FOLLOW-UP REQUEST
    # -----------------------------

    st.divider()
    st.subheader("Create Follow-up Request")

    try:
        current_user = supabase.auth.get_user().user

        request_patients_response = (
            supabase
            .table("patients")
            .select("id, name")
            .eq("doctor_id", current_user.id)
            .order("name")
            .execute()
        )

        request_patients = request_patients_response.data or []

        if not request_patients:
            st.info("Add a patient first before creating a follow-up request.")

        else:
            patient_options = {
                patient["name"]: patient["id"]
                for patient in request_patients
            }

            selected_patient_name = st.selectbox(
                "Select patient",
                list(patient_options.keys()),
                key="request_patient"
            )

            request_type = st.selectbox(
                "What should the patient submit?",
                [
                    "Laboratory report",
                    "Blood pressure reading",
                    "Blood glucose reading",
                    "Imaging report",
                    "Medical report",
                    "Other"
                ],
                key="request_type"
            )

            instructions = st.text_area(
                "Instructions for patient",
                placeholder=(
                    "Example: Please upload your HbA1c and lipid profile "
                    "results."
                ),
                key="request_instructions"
            )

            if st.button(
                "Generate Follow-up Link",
                type="primary",
                key="generate_followup"
            ):

                token = token_urlsafe(32)
                expires_at = datetime.now(timezone.utc) + timedelta(days=14)

                try:
                    new_request = (
                        supabase
                        .table("follow_up_requests")
                        .insert(
                            {
                                "doctor_id": current_user.id,
                                "patient_id": patient_options[
                                    selected_patient_name
                                ],
                                "token": token,
                                "request_type": request_type,
                                "instructions": instructions.strip() or None,
                                "expires_at": expires_at.isoformat(),
                                "status": "active"
                            }
                        )
                        .execute()
                    )

                    if new_request.data:
                        base_url = st.context.url
                        followup_link = f"{base_url}?token={token}"

                        st.success(
                            "Follow-up request created successfully."
                        )

                        st.text_input(
                            "Patient follow-up link",
                            value=followup_link,
                            key="generated_link"
                        )

                        st.caption(
                            "This link expires in 14 days and is intended "
                            "for one submission."
                        )

                except Exception as e:
                    st.error("Could not create the follow-up request.")
                    st.exception(e)

    except Exception as e:
        st.error("Could not load patients for follow-up request.")
        st.exception(e)

    st.divider()

        # -----------------------------
    # FOLLOW-UP SUBMISSIONS
    # -----------------------------

    st.divider()
    st.subheader("Follow-up submissions")

    try:
        current_user = supabase.auth.get_user().user

        submissions_response = (
            supabase
            .table("follow_up_requests")
            .select(
                """
                id,
                patient_id,
                request_type,
                instructions,
                status,
                created_at,
                submitted_at,
                patients(name),
                submissions(
                    id,
                    message,
                    file_name,
                    file_path,
                    created_at
                )
                """
            )
            .eq("doctor_id", current_user.id)
            .eq("status", "submitted")
            .order("submitted_at", desc=True)
            .execute()
        )

        submitted_requests = submissions_response.data or []

        if not submitted_requests:

            st.info("No new patient submissions yet.")

        else:

            for request in submitted_requests:

                patient_info = request.get("patients") or {}
                patient_name = patient_info.get(
                    "name",
                    "Unknown patient"
                )

                submission_list = request.get("submissions") or []

                if not submission_list:
                    continue

                submission = submission_list[0]

                with st.expander(
                    f"🔴 {patient_name} — "
                    f"{request.get('request_type', 'Follow-up')}"
                ):

                    st.write(
                        f"**Submitted:** "
                        f"{request.get('submitted_at', 'Unknown')}"
                    )

                    st.write(
                        f"**File:** "
                        f"{submission.get('file_name') or 'No file'}"
                    )

                    st.write(
                        f"**Patient message:** "
                        f"{submission.get('message') or 'No message provided.'}"
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
                        key=f"response_{request['id']}"
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
                        key=f"message_{request['id']}",
                        height=120
                    )

                    if st.button(
                        "Mark as Reviewed",
                        key=f"review_{request['id']}",
                        type="primary"
                    ):

                        try:

                            supabase.table("responses").insert(
                                {
                                    "submission_id": submission["id"],
                                    "doctor_id": current_user.id,
                                    "response_type": response,
                                    "message": doctor_message.strip()
                                }
                            ).execute()

                            supabase.table(
                                "follow_up_requests"
                            ).update(
                                {
                                    "status": "reviewed",
                                    "reviewed_at": datetime.now(
                                        timezone.utc
                                    ).isoformat()
                                }
                            ).eq(
                                "id",
                                request["id"]
                            ).execute()

                            st.success(
                                "Submission marked as reviewed."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                "Could not save the doctor response."
                            )

                            st.exception(e)

    except Exception as e:

        st.error(
            "Could not load follow-up submissions."
        )

        st.exception(e)
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
