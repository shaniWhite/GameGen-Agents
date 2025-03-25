
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import sys
import os
# Add the 'src' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
import main


app = FastAPI()

# Input model for the API request
class GameRequest(BaseModel):
    game_description: str
    iterations: int = 3  # default value

@app.post("/generate_game")
async def generate_game(request: GameRequest):
    try:
        logging.info(f"🎮 Generating game: {request.game_description} (iterations={request.iterations})")
        await main.generate_game_from_api(request.game_description, request.iterations)
        return {"message": "✅ Game created successfully!"}
    except Exception as e:
        logging.exception("❌ Game generation failed.")
        raise HTTPException(status_code=500, detail=f"Game generation failed: {str(e)}")
