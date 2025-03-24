from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import os
import shutil
import logging
import time

# Local imports
import agents.code_repair 
import agents.code_updater 
import agents.video_analizer
import utils.file_utils 
import utils.game_utils 
import agents.developers 
import agents.planners
import agents.control_test
import utils.game_database

app = FastAPI()

# Initialize database and logging on startup
@app.on_event("startup")
async def startup_event():
    utils.game_database.init_db()
    if os.path.exists("game"):
        def remove_readonly(func, path, _):
            os.chmod(path, 0o777)
            func(path)
        shutil.rmtree("game", onerror=remove_readonly)
    os.makedirs("game")

    with open("game_log.txt", "w") as log_file:
        log_file.write("")

    logging.basicConfig(
        filename="game_log.txt",  
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler())

class GameRequest(BaseModel):
    description: str
    iterations: int

@app.post("/create-game")
async def create_game(request: GameRequest):
    try:
        user_input = request.description
        iterations = request.iterations

        final_plan = await agents.planners.plan_project(user_input, iterations)
        with open("game_plan.xml", "w", encoding="utf-8") as f:
            f.write(final_plan)

        game_name, window_size, file_structure = utils.file_utils.parse_file_structure(final_plan)
        os.makedirs("game", exist_ok=True)

        tasks = []
        for file_name, file_description in file_structure:
            task = asyncio.create_task(agents.developers.developer_agent(file_name, file_description, final_plan))
            tasks.append(task)
        await asyncio.gather(*tasks)

        max_attempts = 10
        while True:
            error_message = await utils.game_utils.run_game()

            if error_message is None:
                for _ in range(3):
                    error_details = agents.control_test.ControlTesterAgent(game_name)
                    if error_details is None:
                        break
                    await agents.code_updater.GameUpdater_Agent(error_details)

                analize = agents.video_analizer.analyze_game_video(game_name)
                await agents.code_updater.GameUpdater_Agent(analize)

                utils.game_database.save_game(game_name)
                return {"status": "success", "message": "Game created and saved successfully."}
            else:
                for attempt in range(max_attempts):
                    await agents.code_repair.Code_Repair_Agent(error_message)
                    time.sleep(1)
                    error_message = await utils.game_utils.run_game()
                    if error_message is None:
                        break
                else:
                    return {"status": "error", "message": "Could not fix errors after multiple attempts."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
