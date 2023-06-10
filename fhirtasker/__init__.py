from flask import Flask

app = Flask(__name__)

import fhirtasker.views
import fhirtasker.utils
import fhirtasker.filters