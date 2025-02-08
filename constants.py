import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration constants
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
# USER_PROMPT = os.getenv("USER_PROMPT")
# JSON_TEMPLATE = os.getenv("JSON_TEMPLATE")
# JSON_TEMPLATE = json.loads(os.getenv("JSON_TEMPLATE"))

SYSTEM_PROMPT = """
You are tasked with extracting and organizing personal, academic, and employment information from candidate resumes. Your goal is to identify relevant details and categorize them into sections such as personal information, educational background, skills, and employment history.
Give all dates in dd/MM/yyyy format.
Stick to the given json template only.
Provide the output as valid JSON. Do not include any markdown formatting, such as triple backticks or other extra characters. Respond with only the JSON content.
"""

USER_PROMPT = "User is requesting to extract the following details from the resume text:"


JSON_TEMPLATE = {
    "City": "",
    "PersonalDetails": {
        "Name": {"FirstName": "", "LastName": "", "MiddleName": "", "FullName": "", "TitleName": ""},
        "DateOfBirth": "",
        "Mobile": [],
        "Email": [],
        "Nationality": ""
    },
    "Academics": [
        {
            "Degree": "",
            "Branch": "",
            "StartDate": "",
            "EndDate": "",
            "Institute": "",
            "Score": ""
        }
    ],
    "CurrentEmployer": "",
    "CurrentSalary": "",
    "ExpectedSalary": "",
    "WorkedPeriod": {"TotalExperienceInMonths": "", "TotalExperienceInYear": "",
                     "TotalExperienceRange": ""},
    "Skills": [],
    "WorkExperience": [
        {
            "Organization": "",
            "StartDate": "",
            "EndDate": "",
            "Designation": ""
        }
    ]
}