import os
from ibm_watson_machine_learning import APIClient

# Fetching credentials from environment variables
wml_credentials = {
    "apikey": os.getenv("WML_APIKEY"),
    "url": os.getenv("WML_URL"),
    "project_id": os.getenv("WML_PROJECT_ID")
}

# Initialize the IBM Watson Machine Learning Client
client = APIClient(wml_credentials)
