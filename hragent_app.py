import os
import json
from typing import TypedDict, List, Dict
from dotenv import load_dotenv
import requests
from langgraph.graph import StateGraph, END
from jd_template_selector import get_template_for_role

# ---- configuration & environment ----
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
USE_API = True  

# ---- session persistence ----
SESSION_FILE = "session_state.json"

def save_session(state: dict, path=SESSION_FILE):
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

def load_session(path=SESSION_FILE) -> dict:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def clear_session(path=SESSION_FILE):
    if os.path.exists(path):
        os.remove(path)

# ---- helper functions ----

def call_openrouter(prompt: str) -> str:
    if not USE_API:
        print(f"[Mock LLM Call] Prompt:\n{prompt}")
        return "This is a simulated LLM-generated response."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are an HR assistant helping startups hire."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return "Failed to get response."

# ---- langgraph nodes ----

def clarify_node(state: dict) -> dict:
    if state.get("clarified"):
        return state

    if "clarifications" not in state or not state["clarifications"]:
        raise ValueError("No clarifications found in state. Provide them via frontend.")

    state["clarified"] = True
    return state


def jd_generator_node(state: dict) -> dict:
    roles = state["roles"]
    clar = state.get("clarifications", {})
    job_descriptions = {}

    for role in roles:
        info = clar.get(role, {})

        prompt = f"""
                        Generate a LinkedIn-style job posting for the role: {role}. Use the structure below and incorporate the provided data.

                        **About the Job:**
                        Introduce the role in the context of a startup. Include the mission, growth stage, and team size if appropriate.
                        Mention timeline (e.g., "We're looking to fill this role by {info.get('timeline', 'N/A')}").

                        **What You Will Do:**
                        Write 4–6 bullet points based on:
                        - {info.get('key_responsibilities', 'N/A')}
                        - Expected outcomes: {info.get('impact_6months', 'N/A')}

                        **What You Will Bring to the Team:**
                        Include qualifications from:
                        - Years of experience: {info.get('years_experience', 'N/A')}
                        - Must-have skills: {info.get('must_have_skills', 'N/A')}
                        - Domain experience: {info.get('domain_experience', 'N/A')}

                        **What Gives You an Edge:**
                        Preferred qualifications based on:
                        - {info.get('nice_to_have_skills', 'N/A')}

                        **Compensation & Perks:**
                        - Compensation: {info.get('budget', 'N/A')} {"(Equity included)" if info.get('equity') in ['Yes', 'Y'] else ''}
                        - Perks: {info.get('perks', 'N/A')}
                        - Work Setup: {info.get('work_setup', 'N/A')} at {info.get('location', 'Remote')}
                        - Deadline: {info.get('deadline', 'N/A')}

                        **Equal Opportunity Statement:**
                        [Company] is an equal opportunity employer. We make hiring decisions based on qualifications without regard to race, religion, national origin, gender, sexual orientation, age, disability, or any other protected status.
                        """

        job_descriptions[role] = call_openrouter(prompt)

    state["job_descriptions"] = job_descriptions
    return state

def checklist_node(state: dict) -> dict:
    roles = state["roles"]
    clar = state.get("clarifications", {})
    checklist = {}

    for role in roles:
        info = clar.get(role, {})
        prompt = f"""
You're an expert technical recruiter. Generate a step-by-step hiring checklist (8–12 items) for a **{role}** in a startup. 
Each step should be:

- Specific (mention tools or platforms like LinkedIn, HackerRank, etc.)
- Actionable (e.g., "Draft JD with clear outcomes", "Schedule 60-min system design interview")
- Professional

Clarification Data:
- Summary: {info.get('summary')}
- Budget: {info.get('budget')} {'(Equity)' if info.get('equity') == 'Y' else ''}
- Timeline: {info.get('timeline')}, Deadline: {info.get('deadline')}
- Work Setup: {info.get('work_setup')} @ {info.get('location')}
- Must-Have Skills: {info.get('must_have_skills')}
- Nice-to-Have: {info.get('nice_to_have_skills')}
- Domain Experience: {info.get('domain_experience')}
- Years Exp: {info.get('years_experience')}
- Key Responsibilities: {info.get('key_responsibilities')}
- Outcomes Expected: {info.get('impact_6months')}

Format: Bullet list, one item per line.
Avoid generic phrases like "Hire candidate".
"""

        response = call_openrouter(prompt)
        checklist_items = [item.strip("•- ") for item in response.split("\n") if item.strip()]
        checklist[role] = checklist_items

    state["checklists"] = checklist
    return state


def output_node(state: dict) -> dict:
    roles = state["roles"]
    jds = state["job_descriptions"]
    checklist = state["checklists"]

    # markdown
    md = "# Hiring Plan\n\n"
    for role in roles:
        md += f"## {role}\n\n**Job Description:**\n{jds[role]}\n\n**Checklist:**\n"
        for item in checklist[role]:
            md += f"- {item}\n"
        md += "\n"

    # json
    json_obj = {"roles": [
        {"title": r, "jd": jds[r], "checklist": checklist[r]} for r in roles
    ]}

    state["markdown_output"] = md  
    return state

def email_writer_node(state: dict) -> dict:
    roles = state["roles"]
    email_templates = {}

    for role in roles:
        company = "Infinite"  

        email_templates[role] = {
            "interview_invite": {
                "subject": f"Interview Invitation for {role} at {company}",
                "body": (
                    f"Hello {{candidate_name}},\n\n"
                    f"Thank you for applying to {company}. We’d like to invite you to interview for the {role} position.\n\n"
                    f"Please share your availability this week.\n\n"
                    f"Best regards,\n{company} Hiring Team"
                )
            },
            "rejection": {
                "subject": f"Update on Your Application for {role}",
                "body": (
                    f"Hello {{candidate_name}},\n\n"
                    f"Thank you for your interest in the {role} role at {company}. We appreciate the time and effort you put into your application.\n\n"
                    f"After careful consideration, we’ve decided to move forward with other candidates at this time.\n\n"
                    f"We wish you all the best in your job search.\n\n"
                    f"Sincerely,\n{company} Hiring Team"
                )
            }
        }

    state["email_templates"] = email_templates
    return state

def template_selector_node(state: dict) -> dict:
    templates = {}
    for role in state["roles"]:
        templates[role] = get_template_for_role(role)
    state["jd_templates"] = templates

#    print("\n📚 JD Templates:\n")
#    for role, template in templates.items():
#        print(f"--- {role} ---\n{template}\n")

    return state

# ---- langgraph setup ----

class AgentState(dict):
    roles: list
    clarified: bool
    job_descriptions: dict
    checklists: dict

graph = StateGraph(dict)

graph.add_node("clarify", clarify_node)
graph.add_node("jd_generator", jd_generator_node)
graph.add_node("checklist", checklist_node)
graph.add_node("output", output_node)
graph.add_node("email_writer", email_writer_node)
graph.add_node("template_selector", template_selector_node)

graph.set_entry_point("clarify")
graph.add_edge("clarify", "jd_generator")
graph.add_edge("jd_generator", "checklist")
graph.add_edge("checklist", "output")
graph.add_edge("output", "email_writer")
graph.add_edge("email_writer", "template_selector")
graph.add_edge("template_selector", END)

app = graph.compile()

# ---- run the graph ----

def run_agent_workflow(roles: list[str], clarifications: dict, resume=False) -> dict:
    session_state = {
        "roles": roles,
        "clarifications": clarifications,
        "clarified": resume,
        "job_descriptions": {},
        "checklists": {}
    }

    graph = StateGraph(dict)
    graph.add_node("clarify", clarify_node)
    graph.add_node("jd_generator", jd_generator_node)
    graph.add_node("checklist", checklist_node)
    graph.add_node("output", output_node)
    graph.add_node("email_writer", email_writer_node)
    graph.add_node("template_selector", template_selector_node)

    graph.set_entry_point("clarify")
    graph.add_edge("clarify", "jd_generator")
    graph.add_edge("jd_generator", "checklist")
    graph.add_edge("checklist", "output")
    graph.add_edge("output", "email_writer")
    graph.add_edge("email_writer", "template_selector")
    graph.add_edge("template_selector", END)

    app = graph.compile()
    final_state = app.invoke(session_state)
    return final_state

# ---- main function ----

if __name__ == "__main__":
    print("🧠 Starting Agentic Hiring Flow with LangGraph...\n")

    roles = ["Founding Engineer", "GenAI Intern"]
    resume = False

    use_prev = input("🔁 Resume previous session? (Y/N): ").strip().lower()
    if use_prev == "y":
        session_state = load_session()
        roles = session_state.get("roles", roles)
        resume = True
    else:
        clear_session()

    result = run_agent_workflow(roles, resume=resume)
    save_session(result)

    clear = input("🧹 Clear session file after run? (Y/N): ").strip().lower()
    if clear == "y":
        clear_session()

__all__ = ["run_agent_workflow"]