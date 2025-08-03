from jd_templates import JD_TEMPLATES

def get_template_for_role(role_name: str) -> str:
    name = role_name.lower()
    for key in JD_TEMPLATES:
        if key in name:
            return JD_TEMPLATES[key]
    return "No predefined template found for this role."
