from fhirtasker import app
from fhirtasker.utils import generate_test_patient
from fhirtasker.integrations.auth.user.client import UserAuthClient
from fhirtasker.integrations.fhir.client import get_fhir_client, FHIRClientOperationError
from fhirtasker.integrations.fhir.resources import ActivePatient

import json

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.practitionerrole import PractitionerRole
from fhir.resources.R4B.task import Task
from flask import render_template, request
from markupsafe import escape
import requests

FHIR_CLIENT = get_fhir_client()

def get_user() -> PractitionerRole:
    id = request.args.get("user", default=2, type=int)
    auth = UserAuthClient()
    return auth.get_test_user_by_id(id)

@app.route("/")
def index():
    return render_template("index.html", user=get_user())

@app.route("/trigger")
def trigger():
    """
    This is just a random method for use during development to trigger some Python action
    """
    new_res_content = {
    "resourceType": "Task",
    "id": "D000-003-243",
    "status": "in-progress",
    "intent": "order",
    "code": {
        "text": "Discharge"
    },
    "for": {
        "type": "Patient",
        "reference": "Patient/9449305552",
        "display": "CHISLETT, OCTAVIA"
    },
    "authoredOn": "2019-05-21T13:15:00Z",
    "lastModified": "2019-06-14T14:01:00Z",
    "reasonReference": {
        "type": "Observation",
        "reference": "Observation/D000-003-243R"
    },
    "note": [
        {
            "text": "Awaiting 'Approve Referral' by Helping Hands Reading (VNJ3K)"
        }
    ]
    }
    resp = FHIR_CLIENT.put_resource("Task/D000-003-243", new_res_content)
    return f"<h1>Action Performed</h1><p>Result is:</p><code>{resp.content}</code>"

@app.route("/Task/test")
def task_test():
    return render_template("resources/task.html")

@app.route("/Patient/test")
def patient_test():
    return render_template("resources/patient.html", user=get_user(), patient=generate_test_patient())

@app.route("/Patient/<unsafe_nhs_number>")
def patient(unsafe_nhs_number):
    nhs_number = str(escape(unsafe_nhs_number))
    try:    
        active_patient = ActivePatient(nhs_number)

        # if any active pathways exist
        pathways_for_patient = FHIR_CLIENT.search("Task", 
                                                  {"subject": f"Patient/{nhs_number}", 
                                                   "status": "in-progress"})
        pathways_parsed = None
        if pathways_for_patient:
            pathways_parsed = Bundle.parse_raw(pathways_for_patient)

        return render_template("resources/patient.html", user=get_user(), patient=active_patient.patient, pathways=pathways_parsed)     
    except FHIRClientOperationError as ex:
        if ex.status_code == 404:
            return render_template("errors/404.html", error_text=f"The patient with NHS Number {nhs_number} could not be found.")
        
@app.route("/Task/<unsafe_task_id>")
def task(unsafe_task_id):
    task_id = str(escape(unsafe_task_id))
    try:
        task = Task.parse_raw(FHIR_CLIENT.get_resource_content(f"Task/{task_id}", none_on_404=False))
        search_results = Bundle.parse_raw(FHIR_CLIENT.search("Task", {
            "part-of": f"Task/{task_id}"
        },
        sort_rules=["-modified"]))


        subtasks = None
        if search_results.entry:
            subtasks = list(map((lambda bundle_entry: bundle_entry.resource), search_results.entry))

        reason = ""
        if task.reasonReference:
            reason =  Observation.parse_raw(FHIR_CLIENT.get_resource_content(task.reasonReference.reference))

        return render_template("resources/task.html", user=get_user(), task=task, subtasks=subtasks, reason=reason)
    except FHIRClientOperationError as ex:
        if ex.status_code == 404:
            return render_template("errors/404.html", error_text=f"The task with ID {task_id} could not be found.")
    
# this is all horrible, and temporary to avoid needing to
#  use postman all the time...
PERMITTED_RESOURCE_TYPES = [
    "Patient",
    "Task",
    "Practitioner",
    "PractitionerRole",
    "Observation"
]

@app.route("/edit/<unsafe_resource_type>/<unsafe_resource_id>")
def resource_editor(unsafe_resource_type, unsafe_resource_id):
    resource_type = escape(unsafe_resource_type)
    if resource_type not in PERMITTED_RESOURCE_TYPES:
        return render_template("errors/404.html", error_text=f"The resource type \"{resource_type}\" is either not a valid FHIR resource type, or is not supported by fhirtasker.")
    
    resource_id = escape(unsafe_resource_id)
    relative_path = f"{resource_type}/{resource_id}"
    response_content = FHIR_CLIENT.get_resource_content(relative_path)
    resource_json = None

    if response_content:
        resource_json = json.dumps(json.loads(FHIR_CLIENT.get_resource_content(relative_path)), indent=2)

    return render_template("admin/resource_editor.html", user=get_user(), relative_path=relative_path, resource_json=resource_json)

@app.route("/save/<unsafe_resource_type>/<unsafe_resource_id>", methods=['POST'])
def resource_saver(unsafe_resource_type, unsafe_resource_id):
    resource_type = escape(unsafe_resource_type)
    if resource_type not in PERMITTED_RESOURCE_TYPES:
        return render_template("errors/404.html", error_text=f"The resource type \"{resource_type}\" is either not a valid FHIR resource type, or is not supported by fhirtasker.")
    
    resource_id = escape(unsafe_resource_id)
    relative_path = f"{resource_type}/{resource_id}"

    resource = json.loads(request.get_json()["resource"])
    print(resource)
    response = FHIR_CLIENT.put_resource(relative_path, resource)
    print(str(response))
    return json.dumps({
        "statusCode": response.status_code,
        "body": response.json()
        })