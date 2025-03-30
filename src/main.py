
import asyncio
import os
import shutil
from dotenv import load_dotenv
import time
import logging
import agents.action_check
import agents.action_fix
import agents.code_repair 
import agents.code_updater 
import agents.video_analizer
import utils.file_utils 
import utils.game_utils 
import agents.developers 
import agents.planners
import utils.game_database
import sys
 


# Initialize the database once when the program starts
utils.game_database.init_db()

def setup_environment():
    # Clear the log file
    with open("game_log.txt", "w") as log_file:
        log_file.write("")

    # Configure logging
    logging.basicConfig(
        filename="game_log.txt",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Remove and recreate the 'game' directory
    clear_game_directory()
    os.makedirs("game", exist_ok=True)
    
    # Suppress debug logs from external libraries
    logging.getLogger("openai").setLevel(logging.WARNING)  # Ignore AI tool logs
    logging.getLogger("httpx").setLevel(logging.WARNING)   # Suppress network logs
    logging.getLogger("urllib3").setLevel(logging.WARNING) # Suppress HTTP logs
    logging.getLogger("PIL").setLevel(logging.WARNING)     # Suppress image processing logs

    # Redirect stderr to prevent AI debug logs from appearing
    sys.stderr = open(os.devnull, "w")  # Suppress background error messages

    logging.info("✅ Game environment setup complete!")  # Add confirmation log

def clear_game_directory():
    if os.path.exists("game"):
        try:
            def remove_readonly(func, path, _):
                os.chmod(path, 0o777)
                func(path)
            shutil.rmtree("game", onerror=remove_readonly)
        except Exception as e:
            logging.error(f"❌ Error deleting 'game' directory: {str(e)}")

async def main(user_input: str = None, iterations: int = 1):
    setup_environment()
    clear_game_directory()
    if user_input is None:
        user_input = input("Describe the Pygame game you want to create: ")
    if not iterations:
        iterations = int(input("How many planning iterations do you want? "))
    
    logging.info("Planning the game structure...")
    final_plan = await agents.planners.plan_project(user_input, iterations)
    logging.info("game plan written to game_plan.xml")
    with open("game_plan.xml", "w", encoding="utf-8") as f:
        f.write(final_plan)
    
    game_name, window_size, file_structure, actions = utils.file_utils.parse_file_structure(final_plan)
    logging.info(f"Game Name: {game_name}")
    logging.info(f"ACTIONS: {actions}")
    logging.info(f"ACTIONS: {actions}")
    logging.info("Creating game files...")
    os.makedirs("game", exist_ok=True)
    
    tasks = []
    for file_name, file_description in file_structure:
        task = asyncio.create_task(agents.developers.developer_agent(file_name, file_description, final_plan, actions))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
 
    logging.info("Game creation complete!")
    logging.info("Final game plan:")
    # Run the game in a loop to catch and fix errors, then enter feedback loop
    max_attempts = 10
    while True:
        
        error_message = await utils.game_utils.run_game()
        if error_message is None:
            logging.info("Game ran successfully!")
            for _ in range(2):
                for _ in range(2):
                    logging.info("Running control tests...")
                    # Run the game with the image analysis agent
                    action_results, failed_actions = await agents.action_check.action_check_agent(game_name, actions)
                    if failed_actions is None:
                        logging.info("✅ All actions passed successfully!")
                        break
                    logging.error(f"❌ Some actions failed: {failed_actions}") 
                    await agents.action_fix.action_fix_agent(failed_actions)  
                    time.sleep(1)
                # Video analyzer 
                analize = agents.video_analizer.analyze_game_video(game_name)
                await agents.code_updater.GameUpdater_Agent(analize,actions)
                time.sleep(1)
                
                # Run the game again to verify the changes
                while True:
                    logging.info("🔁 Re-running game to verify all changes...")
                    final_error = await utils.game_utils.run_game()
                    if final_error is None:
                        logging.info("✅ Final check passed. No errors found!")
                        break  

                    logging.warning(f"⚠️ New error detected after fixes: {final_error}")
                    await agents.code_repair.Code_Repair_Agent(final_error,actions)
                    time.sleep(1)      
                        
            print("🎉 Game created successfully! You can now play.")
            utils.game_database.save_game(game_name)
            logging.info("Game saved to the database.")
            break    
            
        else:
            logging.error(f"Error detected: {error_message}")
            for attempt in range(max_attempts):
                logging.info(f"Attempt {attempt + 1} to fix the errors...")
                await agents.code_repair.Code_Repair_Agent(error_message,actions)
                time.sleep(1)  
                               
                # Try running the game again after fixing
                logging.info("Running the game after fixing the errors...")
                error_message = await utils.game_utils.run_game()
                if error_message is None:
                    logging.info("Errors fixed successfully!")
                    break
                  
            else:
                logging.error(f"Failed to fix all errors after {max_attempts} attempts.")
                user_choice = input("Press Enter to continue error correcting, or type 'no' to quit: ").lower()
                if user_choice == 'no':
                    return

# Run the game creation process
if __name__ == "__main__":
    asyncio.run(main())

# New entry point for API
async def generate_game_from_api(description: str, iterations: int):
    await main(description, iterations)
    return {"message": "✅ Game creation started from API!"}