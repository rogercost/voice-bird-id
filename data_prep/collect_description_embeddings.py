import os
import time

import pandas as pd
import vertexai
from vertexai.language_models import TextEmbeddingModel

from utils import read_aba_checklist

vertexai.init(project='arboreal-vision-451920-k1', location='us-central1')
model = TextEmbeddingModel.from_pretrained('text-embedding-005')

"""
This script will submit the scraped bird descriptions to an embedding model to obtain embeddings of each description,
to be used as inputs to a clustering algorithm that will attempt to derive sensible clusters of birds that may not
align perfectly with the taxonomic family species, but which may work better for prediction purposes. 
"""
work_dir = "C:\\Users\\Roger\\Dropbox\\DOCUMENTS\\voice-bird-id"
output_dir = f"{work_dir}\\bird_descriptions"
output_pickle = f"{work_dir}\\bird_descriptions.pkl"

aba_checklist = read_aba_checklist("C:\\Users\\Roger\\Downloads\\ABA_Checklist-8.17.csv")

with open('prompt_root.txt', 'r') as f:
    prompt_root = f.read()

failed_birds = []
names = []
families = []
descriptions = []

for family, bird_list in aba_checklist.items():
    for name, scientific, code in bird_list:
        description_file = f"{output_dir}\\{name}.txt"
        if not (os.path.exists(description_file) and os.path.getsize(description_file) > 0):
            message = f"Did not find description for {name} in {description_file}"
            failed_birds.append(message)
            print(message)
            continue

        try:
            with open(description_file, 'r', encoding='utf-8') as f:
                description = f.read()
        except Exception as e:
            message = f"Failed to read synthetic recordings for {name} in {description_file}: {e}"
            failed_birds.append(message)
            print(message)
            continue

        names.append(name)
        families.append(family)
        descriptions.append(description)

# Initialize an empty list to store all embeddings
embeddings = []

# Process descriptions in batches of 25
for i in range(0, len(descriptions), 25):
    batch = descriptions[i:i + 25]
    print(f"Submitting {len(batch)} descriptions to embedding model...")
    batch_embeddings = model.get_embeddings(batch)
    embeddings.extend(batch_embeddings)

data = {
    "name": names,
    "family": families,
    "embedding": [x.values for x in embeddings],
    "raw_recording": descriptions
}
df = pd.DataFrame(data)
df.to_pickle(output_pickle)
print(f"Extracted {len(df)} description embeddings; wrote pickle file: {output_pickle}")
print(df.head())

if len(failed_birds) > 0:
    for bird in failed_birds:
        print(bird)

