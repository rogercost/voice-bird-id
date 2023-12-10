from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List

app = FastAPI()


class InputText(BaseModel):
    text: str


class MatchResult(BaseModel):
    object_id: int
    similarity_score: float


def get_closest_matches(input_text: str, n: int) -> List[MatchResult]:
    # Replace this function with your own matching logic
    # This is a placeholder implementation
    # In a real scenario, you would compare input_text with your internal library
    # and return a list of MatchResult objects with actual similarity scores
    # Here, it simply returns some dummy data for demonstration purposes
    dummy_data = [
        {"object_id": 1, "similarity_score": 0.9},
        {"object_id": 2, "similarity_score": 0.85},
        {"object_id": 3, "similarity_score": 0.80},
    ]
    return dummy_data[:n]


@app.post("/get_closest_matches", response_model=List[MatchResult])
async def get_closest_matches_endpoint(
        input_text: InputText,
        n: int = Query(1, title="Number of Matches", description="Number of closest matches to retrieve"),
):
    try:
        result = get_closest_matches(input_text.text, n)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
