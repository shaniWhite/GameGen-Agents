
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import requests


app = FastAPI()

# Input model for the API request
class GameRequest(BaseModel):
    game_description: str
    iterations: int = 1  # default value

@app.post("/generate_game")
async def generate_game(request: GameRequest):
    try:
        # Forward the request to your local runner
        local_url = "http://192.168.10.105:8001/generate_game"
        response = requests.post(local_url, json=request.dict())
        response.raise_for_status()

        return {"message": "✅ Game creation started on local machine!"}
    except Exception as e:
        logging.exception("❌ Failed to forward request to local runner.")
        raise HTTPException(status_code=500, detail=str(e))