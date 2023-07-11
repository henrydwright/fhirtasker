from datetime import date

from fhirtasker import app

SECONDS_IN_A_YEAR = 31536000

STATUS_TO_VERB_MAP = {
    "draft": "Drafting in progress with",
    "requested": "Awaiting assignment from",
    "received": "Received by",
    "accepted": "Awaiting completion by",
    "rejected": "Rejected by",
    "ready": "Awaiting completion by",
    "cancelled": "Cancelled by",
    "in-progress": "Action owner",
    "on-hold": "Action owner",
    "failed": "Attempted by",
    "completed": "Completed by",
    "entered-in-error": "Last updated by"
}

STATUS_TO_GOVUK_TAG_COLOR = {
    "draft": "grey",
    "requested": "pink",
    "received": "blue",
    "accepted": "yellow",
    "rejected": "red",
    "ready": "yellow",
    "cancelled": "red",
    "in-progress": "turquoise",
    "on-hold": "yellow",
    "failed": "red",
    "completed": "green",
    "entered-in-error": "grey"
}

@app.template_filter("birth_date_to_age")
def birth_date_to_age(birth_date : date) -> str:
    difference = date.today() - birth_date
    return str(int(difference.total_seconds() // SECONDS_IN_A_YEAR))

@app.template_filter("to_govuk_date")
def to_govuk_date(date_obj : date) -> str:
    return date_obj.strftime("%d %B %Y at %-I:%M%p")

@app.template_filter("status_to_verb")
def status_to_verb(status: str) -> str:
    return STATUS_TO_VERB_MAP[status]

@app.template_filter("status_to_govuk_tag_color")
def status_to_govuk_tag_color(status: str) -> str:
    return STATUS_TO_GOVUK_TAG_COLOR[status]

@app.template_filter("to_practitioner_role_reference")
def to_practitioner_role_reference(id: str) -> str:
    return f"PractitionerRole/{id}"