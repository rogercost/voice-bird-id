import os
import time

import pandas as pd
import vertexai
from vertexai.language_models import TextEmbeddingModel

from utils import read_aba_checklist

vertexai.init(project='arboreal-vision-451920-k1', location='us-central1')
model = TextEmbeddingModel.from_pretrained('text-embedding-005')

"""
This script will submit the synthetic recording transcripts generated by `generate_synthetic_recordings.py` to an
embedding model to obtain embeddings of each recording, to be used as training data to predict the bird family and
species. 
"""
work_dir = "C:\\Users\\Roger\\Dropbox\\DOCUMENTS\\voice-bird-id"
output_dir = f"{work_dir}\\training_data\\synthetic_recordings"
output_pickle = f"{output_dir}\\synthetic_recordings.pkl"

aba_checklist = read_aba_checklist("C:\\Users\\Roger\\Downloads\\ABA_Checklist-8.17.csv")

with open('prompt_root.txt', 'r') as f:
    prompt_root = f.read()

failed_birds = []
embedding_pickles = []
for family, bird_list in aba_checklist.items():

    embeddings = []
    for name, scientific, code in bird_list:
        synth_rec_file = f"{output_dir}\\{name}.txt"
        embedding_pickle = f"{output_dir}\\{name}.pkl"
        embedding_pickles.append(embedding_pickle)

        # Backfill failures from the last run. Remove for a full run.
        # if os.path.exists(embedding_pickle) and os.path.getsize(embedding_pickle) > 0:
        #     continue

        if not (os.path.exists(synth_rec_file) and os.path.getsize(synth_rec_file) > 0):
            message = f"Did not find synthetic recordings for {name} in {synth_rec_file}"
            failed_birds.append(message)
            print(message)
            continue

        try:
            with open(synth_rec_file, 'r') as f:
                recordings = [x.strip() for x in f.read().split('--')]
        except Exception as e:
            message = f"Failed to read synthetic recordings for {name} in {synth_rec_file}: {e}"
            failed_birds.append(message)
            print(message)
            continue

        used_recordings = []
        for recording in recordings:
            if len(recording) > 0 and not recording.isspace():
                used_recordings.append(recording)

        try:
            time.sleep(5)
            embeddings = model.get_embeddings(used_recordings)
        except Exception as e:
            print(f"Caught exception attempting to embed for {name}: {e}")
            continue

        data = {
            "name": name,
            "family": family,
            "embedding": [x.values for x in embeddings],
            "raw_recording": used_recordings
        }
        df = pd.DataFrame(data)
        df.to_pickle(embedding_pickle)
        print(f"Processed {len(df)} recordings for {name} of family {family}; wrote pickle file: {embedding_pickle}")

print(f"Finished embedding all birds; generating unified pickle...")

dataframes = []
processed = 0
for file in embedding_pickles:
    try:
        df = pd.read_pickle(file)
        dataframes.append(df)
        processed += 1
    except Exception as e:
        print(f"Error reading {file}: {e}")

combined_df = pd.concat(dataframes, ignore_index=True)
combined_df.to_pickle(output_pickle)
print(f"Wrote unified training data for {processed} birds, total length {len(combined_df)}, to {output_pickle}")
print(combined_df.head())
