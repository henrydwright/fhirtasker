import os

from fhir.resources.R4B.patient import Patient
from flask import render_template
from markupsafe import escape
import requests

from fhirtasker import app
from fhirtasker.utils import generate_test_patient

FHIR_BASE_URL = os.environ["FHIR_BASE_URL"]
AUTH_BASE_URL = os.environ["AUTH_BASE_URL"]
AUTH_CLIENT_ID = os.environ["AUTH_CLIENT_ID"]
AUTH_CLIENT_SECRET = os.environ["AUTH_CLIENT_SECRET"]

@app.route("/patient/test")
def patient_test():
    return render_template("resources/patient.html", patient=generate_test_patient())

@app.route("/patient/<unsafe_nhs_number>")
def patient(unsafe_nhs_number):
    nhs_number = escape(unsafe_nhs_number)
    print("[INFO] Fetching OAuth Token")
    oauth_token_request = requests.post(url = f"{AUTH_BASE_URL}/oauth2/token", 
                                data = {
                                    "grant_type": "client_credentials",
                                    "resource": FHIR_BASE_URL,
                                    "audience": FHIR_BASE_URL,
                                    "client_id": AUTH_CLIENT_ID,
                                    "client_secret": AUTH_CLIENT_SECRET
                                },
                                headers={
                                    "content-type": "application/x-www-form-urlencoded"
                                })
    if oauth_token_request.status_code == 200:
        token = oauth_token_request.json()['access_token']
        patient_request = requests.get(url = f"{FHIR_BASE_URL}/Patient/{nhs_number}",
                                       headers = {
                                           "Authorization" : "Bearer " + token
                                       })
        if patient_request.status_code == 200:
            patient_parsed = Patient.parse_raw(patient_request.content)
            return render_template("resources/patient.html", patient=patient_parsed)
        else:
            return patient_request.json()
    else:
        return "Error!"
    