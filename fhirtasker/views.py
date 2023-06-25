from fhirtasker import app
from fhirtasker.utils import generate_test_patient
from fhirtasker.integrations.fhir.client import get_fhir_client, FHIRClientOperationError
from fhirtasker.integrations.fhir.resources import ActivePatient

import os

from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.patient import Patient
from flask import render_template
from markupsafe import escape
import requests

FHIR_CLIENT = get_fhir_client()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/task/test")
def task_test():
    return render_template("resources/task.html")

@app.route("/patient/test")
def patient_test():
    return render_template("resources/patient.html", patient=generate_test_patient())

@app.route("/patient/<unsafe_nhs_number>")
def patient(unsafe_nhs_number):
    nhs_number = str(escape(unsafe_nhs_number))
    try:    
        active_patient = ActivePatient(nhs_number)
        active_patient.refresh()

        # if any active pathways exist
        pathways_for_patient = FHIR_CLIENT.search("Task", 
                                                  {"subject": f"Patient/{nhs_number}", 
                                                   "status": "in-progress"})
        pathways_parsed = None
        if pathways_for_patient:
            pathways_parsed = Bundle.parse_raw(pathways_for_patient)

        return render_template("resources/patient.html", patient=active_patient.patient, pathways=pathways_parsed)     
    except FHIRClientOperationError as ex:
        if ex.status_code == 404:
            return render_template("errors/404.html", error_text=f"The patient with NHS Number {nhs_number} could not be found.")
        


    