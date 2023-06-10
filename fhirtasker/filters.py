from datetime import date

from fhirtasker import app

SECONDS_IN_A_YEAR = 31536000

@app.template_filter("birth_date_to_age")
def birth_date_to_age(birth_date : date) -> str:
    difference = date.today() - birth_date
    return str(int(difference.total_seconds() // SECONDS_IN_A_YEAR))
