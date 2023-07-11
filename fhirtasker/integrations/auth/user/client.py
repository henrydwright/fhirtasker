from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.practitionerrole import PractitionerRole
from fhir.resources.R4B.reference import Reference

class UserAuthClient():

    def _generate_test_council_user(self) -> PractitionerRole:
        test_council_user = PractitionerRole(
            id="RBC00238",
            active=True,
            practitioner=Reference(
                reference="Practitioner/68fdb49d-a5b0-4cd7-ac7c-5c4ad7d4a091",
                display="TUCKER, MALCOLM"
            ),
            organization=Reference(
                type="Organization",
                identifier=Identifier(
                    system="https://fhir.nhs.uk/Id/ods-organization-code",
                    value="616"
                ),
                display="Reading Borough Council (616)"
            )
        )
        return test_council_user
    
    def _generate_test_hospital_user(self) -> PractitionerRole:
        test_hospital_user = PractitionerRole(
            id="RHW00002",
            active=True,
            practitioner=Reference(
                reference="Practitioner/27c08060-d14f-4076-acf6-cb455caced82",
                display="COVERLEY, TERRI"
            ),
            organization=Reference(
                type="Organization",
                identifier=Identifier(
                    system="https://fhir.nhs.uk/Id/ods-organization-code",
                    value="RHW"
                ),
                display="Royal Berkshire NHS Foundation Trust (RHW)"   
            )
        )
        return test_hospital_user
    
    def _generate_test_social_care_user(self) -> PractitionerRole:
        test_social_care_user = PractitionerRole(
            id="HH09667",
            active=True,
            practitioner=Reference(
                reference="Practitioner/56750d9b-f1e2-45e7-aa3a-90d65b8ee20f",
                display="MURDOCH, ROBYN"
            ),
            organization=Reference(
                type="Organization",
                identifier=Identifier(
                    system="https://fhir.nhs.uk/Id/ods-organization-code",
                    value="VNJ3K"
                ),
                display="Helping Hands Reading (VNJ3K)"
            )
        )
        return test_social_care_user
    
    def get_test_user_by_id(self, id:int) -> PractitionerRole:
        if id == 0:
            return self._generate_test_council_user()
        elif id == 1:
            return self._generate_test_hospital_user()
        else:
            return self._generate_test_social_care_user()

    def get_logged_in_user(self) -> PractitionerRole:
        return self.get_test_user_by_id(0)