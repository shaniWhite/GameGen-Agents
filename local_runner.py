from fastapi import FastAPI
from pydantic import BaseModel

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))
import main

app = FastAPI()

class GameRequest(BaseModel):
    game_description: str
    iterations: int = 3

@app.post("/generate_game")
async def run_locally(request: GameRequest):
    print(f"📩 Received API request: {request.game_description}, {request.iterations}")
    await main.generate_game_from_api(request.game_description, request.iterations)
    print("✅ Game creation function executed")
    return {"message": "Game created on local machine"}
