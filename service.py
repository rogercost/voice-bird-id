import os

from ebird.api import get_nearby_observations
from fastapi import FastAPI, Query
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

api_key = os.environ['EBIRD_API_KEY']

print("Building FAISS vector store...")
loader = DirectoryLoader('C:\\Users\\Roger\\bird_descriptions', glob="**/*.txt")
docs = loader.load()
print(f"Loaded {len(docs)} bird descriptions, building embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="thenlper/gte-small")  # TODO experiment w/ different embeddings
vectorstore = FAISS.from_documents(docs, embeddings)  # TODO pickle upfront and retrieve for faster startup
print(f"Finished embedding descriptions, starting application...")

# LGA Airport coordinates
DEFAULT_LAT = 40.7747
DEFAULT_LON = -73.8719

app = FastAPI()


@app.post("/get_closest_matches")
async def get_closest_matches_endpoint(user_description: str,
                                       n: int = Query(1),
                                       lat: float = Query(DEFAULT_LAT),
                                       lon: float = Query(DEFAULT_LON)):
    """
    Returns the n closest matches for the provided text description, filtering out any that do not appear in recent
    observations for the provided lat/long.
    """
    records = get_nearby_observations(api_key, lat, lon, dist=50)  # TODO add caching using grid-normalized lat long
    observations = count_observations(records)
    print(f"Captured {len(observations)} recent observations near {lat}/{lon}, e.g.: {list(observations.keys())[:3]}")

    matching_birds = vectorstore.similarity_search(user_description)

    returned_birds = []
    for bird in matching_birds:
        common_name = bird.page_content.split('\n')[0].replace('Name: ', '')  # TODO use metadata, cleaner
        rank = len(returned_birds) + 1

        if common_name in observations:
            print(f"{common_name} was observed recently")
            returned_birds.append({
                "rank": rank,
                "bird": bird.page_content[:100],
                "n_obs": observations[common_name]})  # TODO why is n_obs always 1? API gives only most recent?
        else:
            print(f"{common_name} was not observed recently")

        if rank >= n:
            break

    return returned_birds


def count_observations(records: list):
    observations = {}
    for record in records:
        common_name = record['comName']
        if common_name not in observations:
            observations[common_name] = 1
        else:
            observations[common_name] = observations[common_name] + 1

    return observations
