# Voice Bird ID

*** WORK IN PROGRESS ***

A FastAPI service to match a user-provided bird description with a database of known descriptions, using embedding
similarity search. This project is the back end only and can be used to serve a front end that accepts voice-to-text
for use in the field.

## Setup Instructions

1. Create a Python virtual environment and install the dependencies using `pip install -r requirements.txt`.
2. Obtain an ebird API key and store it in an environment variable called `EBIRD_API_KEY`.
3. Run `data_prep/extract_text_descriptions_allaboutbirds.py` to create a directory of text bird descriptions.
4. Start the service using `uvicorn service:app` from the home directory.
5. Navigate to http://localhost:8000/docs in a browser to interact with the service.
