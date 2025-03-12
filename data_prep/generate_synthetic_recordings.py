import os
import sys
import time

from google import genai
from utils import read_aba_checklist
"""
This script will generate sets of synthetic recording transcripts of birders describing birds being observed in the
field, by prompting Gen AI to generate the transcripts given the text descriptions of the birds harvested via
`extract_text_descriptions_allaboutbirds.py`. 
"""
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)
work_dir = "C:\\Users\\Roger\\Dropbox\\DOCUMENTS\\voice-bird-id"
description_dir = f"{work_dir}\\bird_descriptions"
output_dir = f"{work_dir}\\training_data\\synthetic_recordings"

aba_checklist = read_aba_checklist("C:\\Users\\Roger\\Downloads\\ABA_Checklist-8.17.csv")

with open('prompt_root.txt', 'r') as f:
    prompt_root = f.read()

failed_birds = []
for family, bird_list in aba_checklist.items():
    for name, scientific, code in bird_list:

        description_file = f"{description_dir}\\{name}.txt"
        try:
            with open(description_file, 'r') as f:
                description = f.read()
        except Exception as e:
            message = f"Failed to extract description from {description_file}: {e}"
            failed_birds.append(message)
            print(message)
            continue

        if description is None or len(description) == 0:
            message = f"Got a zero length description from {description_file}"
            failed_birds.append(message)
            print(message)
            continue

        prompt = prompt_root + description
        try:
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        except Exception as e:
            message = f"Failed to invoke Gemini for {name}: {e}"
            failed_birds.append(message)
            print(message)
            continue

        print(f"Received synthetic descriptions for {name}")
        with open(f"{output_dir}\\{name}.txt", 'w') as f:
            f.write(response.text)

        # Short circuit for testing; remove for full run.
        sys.exit(0)

        # 15 request per model per minute usage limit for the free tier:
        # https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas?project=gen-lang-client-0835379782
        time.sleep(5)

if len(failed_birds) > 0:
    print(f"Failed to generate training data for {len(failed_birds)} birds:")
    for bird in failed_birds:
        print(bird)
