import streamlit as st

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Doctor Follow-up",
    page_icon="🩺",
    layout="centered"
)

# -----------------------------
# Demo patient data
# -----------------------------
patients = {
    "Ahmed Khan": {
        "age": 52,
        "last_visit": "12 September 2026",
        "reason": "Diabetes follow-up",
        "investigations": ["HbA1c", "Creatinine", "Lipid profile"],
        "treatment": "Continue previously prescribed treatment.",
        "previous_results": {
            "HbA1c": "7.8%",
            "Creatinine": "0.9 mg/dL",
            "LDL": "128 mg/dL"
        }
    },
    "Sara Ali": {
        "age": 38,
        "last_visit": "15 September 2026",
        "reason": "Thyroid follow-up",
        "investigations": ["TSH", "Free T4"],
        "treatment": "Continue current treatment as previously prescribed.",
        "previous_results": {
            "TSH": "4.8 mIU/L",
            "Free T4": "1.1 ng/dL"
        }
    },
    "Ali Raza": {
        "age": 61,
        "last_visit": "18 September 2026",
        "reason": "Hypertension follow-up",
        "investigations": ["Creatinine", "Electrolytes", "Lipid profile"],
        "treatment": "Continue current treatment.",
        "previous_results": {
            "Creatinine": "1.0 mg/dL",
            "LDL": "135 mg/dL"
        }
    }
}

# -----------------------------
# Header
# -----------------------------
st.title("🩺 Doctor Follow-up")

st.caption(
    "A simple portal for doctors to review patient follow-up reports."
)

st.warning(
    "DEMO VERSION — Use fictional patient information only. "
    "Do not upload real patient records."
)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Doctor Dashboard")
st.sidebar.write("Dr. Mustafa")

page = st.sidebar.radio(
    "Navigation",
    ["Patients", "About"]
)

# -----------------------------
# Patients page
# -----------------------------
if page == "Patients":

    st.subheader("My Patients")

    patient_name = st.selectbox(
        "Select a patient",
        list(patients.keys())
    )

    patient = patients[patient_name]

    st.divider()

    # Patient information
    st.subheader(patient_name)

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Age**")
        st.write(patient["age"])

    with col2:
        st.write("**Last consultation**")
        st.write(patient["last_visit"])

    st.write("**Reason for consultation**")
    st.write(patient["reason"])

    st.divider()

    # Previous consultation
    st.subheader("Previous Consultation")

    st.write("**Investigations requested:**")

    for investigation in patient["investigations"]:
        st.write("•", investigation)

    st.write("**Previous treatment:**")
    st.info(patient["treatment"])

    st.write("**Previous results:**")

    for test, value in patient["previous_results"].items():
        st.write(f"**{test}:** {value}")

    st.divider()

    # Report upload
    st.subheader("Upload Follow-up Report")

    uploaded_file = st.file_uploader(
        "Patient report",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Demo only — do not upload real patient records."
    )

    if uploaded_file is not None:

        st.success(
            f"Report uploaded: {uploaded_file.name}"
        )

        st.subheader("Report Review")

        st.info(
            "AI report extraction will be added in the next version."
        )

        st.write("For now, the doctor can review the uploaded document manually.")

        st.divider()

        # Doctor response
        st.subheader("Doctor Response")

        response = st.radio(
            "Choose an action",
            [
                "Continue current treatment",
                "Book follow-up appointment",
                "Send custom message"
            ]
        )

        if response == "Continue current treatment":

            st.success(
                "Response prepared: Continue current treatment."
            )

            st.text_area(
                "Message to patient",
                value=(
                    "Your report has been reviewed. "
                    "Please continue your previously prescribed treatment "
                    "and follow the instructions provided during your consultation."
                ),
                height=120
            )

        elif response == "Book follow-up appointment":

            st.info(
                "Response prepared: Patient should book a follow-up appointment."
            )

            st.text_area(
                "Message to patient",
                value=(
                    "Your report has been reviewed. "
                    "Please book a follow-up appointment to discuss the results."
                ),
                height=120
            )

        else:

            st.text_area(
                "Write your message to the patient",
                height=150
            )

        if st.button("Prepare Response", type="primary"):
            st.success(
                "Response prepared successfully. "
                "Patient messaging will be connected in a future version."
            )

# -----------------------------
# About page
# -----------------------------
else:

    st.subheader("About Doctor Follow-up")

    st.write(
        """
        Doctor Follow-up is a prototype designed to help doctors
        communicate with regular patients without relying on personal
        phone numbers or messaging accounts.
        """
    )

    st.write("### Planned features")

    st.write("• Patient report uploads")
    st.write("• AI-assisted report extraction")
    st.write("• Previous-result comparison")
    st.write("• Doctor-approved patient responses")
    st.write("• Follow-up appointment requests")
    st.write("• Patient history")
