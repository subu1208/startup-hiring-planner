import streamlit as st
from hragent_app import run_agent_workflow
import json  
from jd_template_selector import get_template_for_role

st.title("🧠 Agentic Hiring Plan Generator")
option = st.sidebar.radio("Choose an action:", ["Generate Hiring Plan", "Show JD Templates", "Show Email Templates"])

roles_master = [
    "Founding Engineer", "Software Engineer", "Product Manager", "Data Scientist", "DevOps Engineer",
    "QA Engineer", "UX/UI Designer", "Product Designer", "Growth Engineer", "Sales Representative",
    "Business Development Manager", "Customer Success Manager", "Marketing Specialist",
    "Account Manager", "Office Manager", "Recruiter", "Finance Manager", "Operations Manager",
    "HR Manager", "Software Engineering Intern", "Product Intern", "Marketing Intern", "Operations Intern",
    "GenAI Intern"
]

if option == "Generate Hiring Plan":

    if "roles_entered" not in st.session_state:
        st.session_state.roles_entered = False

    if not st.session_state.roles_entered:
        role_input = st.text_input("Enter role title(s) to hire (comma-separated)", key="role_input")
        if st.button("✅ Confirm Roles"):
            st.session_state.roles = [r.strip() for r in role_input.split(",") if r.strip()]
            st.session_state.roles_entered = True
            st.rerun()

    if st.session_state.roles_entered:
        roles = st.session_state.roles
        # initialize session state for clarifications if missing
        if "clarifications" not in st.session_state:
            st.session_state["clarifications"] = {}

        roles = st.session_state.roles
        clarifications = st.session_state["clarifications"]  # work directly with session state

        st.markdown("---")
        st.subheader("🔍 Clarify Hiring Needs")

        for role in roles:
            # get stored values 
            saved = clarifications.get(role, {})
            with st.expander(f"{role} Clarification", expanded=True):
                summary = st.text_input(f"{role} - 1-line summary", key=f"{role}_summary", value=saved.get("summary", ""))
                budget = st.text_input(f"{role} - Compensation budget?", key=f"{role}_budget", value=saved.get("budget", ""))
                equity = st.selectbox(f"{role} - Equity or tokens?", ["Yes", "No"], key=f"{role}_equity", index=0 if saved.get("equity") != "No" else 1)
                perks = st.text_input(f"{role} - Benefits/perks?", key=f"{role}_perks", value=saved.get("perks", ""))
                timeline = st.text_input(f"{role} - Target hiring timeline", key=f"{role}_timeline", value=saved.get("timeline", ""))
                deadline = st.text_input(f"{role} - Hard deadline?", key=f"{role}_deadline", value=saved.get("deadline", ""))
                setup = st.selectbox(f"{role} - Work setup", ["Remote", "Hybrid", "Onsite"], key=f"{role}_setup", index=["Remote", "Hybrid", "Onsite"].index(saved.get("work_setup", "Remote")))
                location = st.text_input(f"{role} - Location (if not remote)?", key=f"{role}_location", value=saved.get("location", ""))
                must = st.text_input(f"{role} - Must-have skills", key=f"{role}_must", value=saved.get("must_have_skills", ""))
                nice = st.text_input(f"{role} - Nice-to-have skills", key=f"{role}_nice", value=saved.get("nice_to_have_skills", ""))
                domain = st.text_input(f"{role} - Domain experience", key=f"{role}_domain", value=saved.get("domain_experience", ""))
                years = st.text_input(f"{role} - Years of experience", key=f"{role}_years", value=saved.get("years_experience", ""))
                responsibilities = st.text_area(f"{role} - Key responsibilities", key=f"{role}_resp", value=saved.get("key_responsibilities", ""))
                impact = st.text_area(f"{role} - Top 6–12 month outcomes", key=f"{role}_impact", value=saved.get("impact_6months", ""))

                # save the values back to session_state
                clarifications[role] = {
                    "summary": summary,
                    "budget": budget,
                    "equity": equity,
                    "perks": perks,
                    "timeline": timeline,
                    "deadline": deadline,
                    "work_setup": setup,
                    "location": location,
                    "must_have_skills": must,
                    "nice_to_have_skills": nice,
                    "domain_experience": domain,
                    "years_experience": years,
                    "key_responsibilities": responsibilities,
                    "impact_6months": impact
                }

        # offer download of current session state
        if st.session_state.get("clarifications") and st.session_state.get("roles"):
            session_json = json.dumps({
                "roles": st.session_state.roles,
                "clarifications": st.session_state["clarifications"]
            }, indent=2)
            st.download_button("💾 Download Session as JSON", data=session_json, file_name="session_state.json")

        if st.button("🚀 Generate Hiring Plan"):
            with st.spinner("Generating..."):
                result = run_agent_workflow(roles, clarifications)
                st.session_state["result"] = result  # store result persistently
                st.session_state["checklist_state"] = {}  # initialize checklist states

            st.success("✅ Done!")

        if "result" in st.session_state:
            result = st.session_state["result"]

            for role in roles:
                st.subheader(f"📄 {role}")
                st.markdown("**Job Description:**")
                st.markdown(result["job_descriptions"][role])

                st.markdown("**Checklist:**")
                checklist_items = result["checklists"][role]
                completed = 0
                total = len(checklist_items)

                for idx, item in enumerate(checklist_items):
                    key = f"{role}_check_{idx}"
                    if key not in st.session_state["checklist_state"]:
                        st.session_state["checklist_state"][key] = False
                    st.session_state["checklist_state"][key] = st.checkbox(
                        item, key=key, value=st.session_state["checklist_state"][key]
                    )
                    if st.session_state["checklist_state"][key]:
                        completed += 1

                st.markdown(f"**Progress: {completed} of {total} tasks completed**")
                st.progress(completed / total)

        if st.session_state.get("result") and "markdown_output" in st.session_state["result"]:
            st.download_button(
                "📥 Download Full Hiring Plan (.md)",
                data=st.session_state["result"]["markdown_output"],
                file_name="hiring_plan.md"
            )

        if st.button("🔁 Start Over"):
            st.session_state.clear()
            st.rerun()

elif option == "Show JD Templates":
    st.subheader("📚 Browse JD Templates")
    selected_role = st.selectbox("Choose a role", ["-Select-"] + roles_master)
    if selected_role != "-Select-":
        template = get_template_for_role(selected_role)
        st.markdown(f"### {selected_role} JD Template")
        st.markdown(template)

elif option == "Show Email Templates":
    st.subheader("📬 Browse Email Templates")

    # email templates
    email_templates = {
        "Interview Invitation": """Subject: Interview Invitation - [Role] Position at [Company]

                                Dear [Candidate Name],

                                Thank you for your application for the [Role] position at [Company]. We have reviewed your qualifications and would like to invite you for an interview.

                                Interview Details:
                                - Duration: 45-60 minutes
                                - Format: [Video call via Zoom/Google Meet]
                                - Interviewer: [Interviewer Name, Title]
                                - Focus Areas: Role requirements, your experience, and organizational fit

                                Please reply with your availability for the coming week, and we will send you a calendar invitation with the meeting details.

                                Thank you for your interest in [Company].

                                Best regards,  
                                [Your Name]  
                                [Title]  
                                [Company]
                                """,
        "Application Rejection": """Subject: Application Status - [Role] Position at [Company]

                                Dear [Candidate Name],

                                Thank you for your interest in the [Role] position at [Company] and for taking the time to submit your application.

                                After careful consideration, we have decided to proceed with other candidates whose qualifications more closely match our current requirements. This decision does not reflect negatively on your professional background and experience.

                                We encourage you to apply for future opportunities that align with your skills and career objectives. Please feel free to visit our careers page for updates on available positions.

                                We appreciate your interest in [Company] and wish you success in your career endeavors.

                                Sincerely,  
                                [Your Name]  
                                [Title]  
                                [Company]
                                """,
        "Technical Assessment Invitation": """Subject: Technical Assessment - [Role] Position at [Company]

                                Dear [Candidate Name],

                                Following our initial interview, we would like to invite you to complete a technical assessment as the next step in our selection process for the [Role] position.

                                Assessment Details:
                                - Type: [Coding challenge/Take-home project]
                                - Estimated Duration: [90 minutes]
                                - Submission Deadline: [Date and time]
                                - Platform: [Assessment platform/delivery method]

                                Please confirm your participation and let us know if you require any accommodations or have questions regarding the assessment.

                                The assessment link and instructions will be provided upon confirmation.

                                Best regards,  
                                [Your Name]  
                                [Title]  
                                [Company]
                                """,
        "Post-Interview Follow-up": """Subject: Interview Follow-up - [Role] Position at [Company]

                                Dear [Candidate Name],

                                Thank you for taking the time to interview for the [Role] position at [Company]. We appreciate your interest in joining our organization.

                                Our team is currently reviewing all candidate interviews and will provide you with an update on the next steps within [timeframe, e.g., 3-5 business days].

                                If you have any questions in the meantime, please do not hesitate to contact me.

                                Thank you again for your time and consideration.

                                Best regards,  
                                [Your Name]  
                                [Title]  
                                [Company]
                                """,
        "Job Offer": """Subject: Job Offer - [Role] Position at [Company]

                                Dear [Candidate Name],

                                We are pleased to extend an offer of employment for the position of [Role] at [Company].

                                Offer Summary:
                                - Position: [Role]
                                - Compensation: [Salary and benefits package]
                                - Work Location: [Office location/Remote/Hybrid]
                                - Start Date: [Proposed start date]

                                A formal offer letter with complete terms and conditions will be sent via [delivery method] for your review and signature.

                                Please confirm receipt of this offer and advise us of your decision by [deadline date]. Should you have any questions regarding the terms of employment, please contact me directly.

                                We look forward to your positive response and to welcoming you to our team.

                                Sincerely,  
                                [Your Name]  
                                [Title]  
                                [Company]
                                """
    }

    # template dropdown
    selected_template = st.selectbox("Choose an Email Template", ["-Select-"] + list(email_templates.keys()))
    if selected_template != "-Select-":
        st.markdown(f"### 📄 {selected_template}")
        st.text_area("Preview", email_templates[selected_template], height=400, disabled=True)