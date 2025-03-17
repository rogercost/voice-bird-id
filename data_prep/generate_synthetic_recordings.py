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
    family_size = len(bird_list)
    for name, scientific, code in bird_list:

        description_file = f"{description_dir}\\{name}.txt"
        target_file = f"{output_dir}\\{name}.txt"

        # Backfill failures from the last run. Remove for a full run.
        # if os.path.exists(target_file) and os.path.getsize(target_file) > 0:
        #     continue

        try:
            with open(description_file, 'r', encoding='utf-8') as f:
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

        # Address class imbalance by taking a uniform number of samples per family.
        num_samples = max(1, int(40 / family_size))
        prompt = prompt_root.replace('__NUM__', '20') + description  # Run in batches of 20

        output_lines = []
        for sample in range(num_samples):
            # 15 request per model per minute usage limit for the free tier:
            # https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas?project=gen-lang-client-0835379782
            time.sleep(5)
            try:
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            except Exception as e:
                message = f"Failed to invoke one Gemini batch for {name}: {e}"
                failed_birds.append(message)
                print(message)
                continue

            for line in response.text.splitlines():

                # Quality control: the model sometimes ignores the prompt and puts preliminary header lines in anyway.
                if len(line) > 10 and not line.startswith("OK, here are") and not line.startswith("Okay, here are"):
                    output_lines.append(line + os.linesep)

        with open(target_file, 'w') as f:
            f.writelines(output_lines)

        ts = time.ctime()
        print(f"{ts}: Generated {len(output_lines)} recordings for {name} (one of {family_size} in family {family}")

if len(failed_birds) > 0:
    print(f"Failed to generate training data for {len(failed_birds)} birds:")
    with open(f"{output_dir}\\failed_birds.txt", 'w') as f:
        for bird in failed_birds:
            print(bird)
            f.write(bird)
