from datetime import date
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier

def generate_test_patient() -> Patient:
    pat = Patient()
    name = HumanName(family="Chislett", given=["Octavia"], use="usual")
    name2 = HumanName(family="Chislett", given=["Tav"], use="nickname")
    pat.name = [name, name2]

    nhs_number = Identifier(system="https://fhir.nhs.uk/Id/nhs-number", value=9449305552)
    pat.identifier = [nhs_number]

    pat.birthDate = date.fromisoformat("2008-09-20")
    pat.gender = "female"

    return pat