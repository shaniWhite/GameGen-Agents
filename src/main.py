
import asyncio
import os
import shutil
from dotenv import load_dotenv
import time
import logging
import agents.code_repair 
import agents.code_updater 
import tools.file_tools 
import tools.run_game 
import agents.developers 
import agents.planners
import agents.control_test
from termcolor import colored



with open("game_log.txt", "w") as log_file:
    log_file.write("")

# Configure logging
logging.basicConfig(
    filename="game_log.txt",  
    level=logging.DEBUG,  # Set the log level (DEBUG, INFO, WARNING, ERROR)
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only show errors in the console
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)
logging.getLogger("openai").setLevel(logging.WARNING)  # Hide INFO logs from OpenAI API
logging.getLogger("httpx").setLevel(logging.WARNING)  # For newer OpenAI SDK versions
logging.getLogger("urllib3").setLevel(logging.WARNING)  # If using requests directly
logging.getLogger("PIL").setLevel(logging.WARNING)

# Remove the 'game' directory and its contents if it exists
if os.path.exists("game"):
    try:
        def remove_readonly(func, path, _):
            """Forces removal of read-only files."""
            os.chmod(path, 0o777)
            func(path)

        shutil.rmtree("game", onerror=remove_readonly)  # Force delete
    except Exception as e:
        logging.error(f"❌ Error deleting 'game' directory: {str(e)}") 
        
# Recreate an empty directory
os.makedirs("game")  

async def main():
    user_input = input(colored("Describe the Pygame game you want to create: ", "magenta"))
    iterations = int(input(colored("How many planning iterations do you want? ","magenta")))
    
    logging.info("Planning the game structure...")
    final_plan = await agents.planners.plan_project(user_input, iterations)
    logging.info(colored("game plan written to game_plan.xml", "yellow"))
    with open("game_plan.xml", "w", encoding="utf-8") as f:
        f.write(final_plan)
    
    game_name, window_size, file_structure = tools.file_tools.parse_file_structure(final_plan)
    logging.info(f"Game Name: {game_name}")
    logging.info("Creating game files...")
    os.makedirs("game", exist_ok=True)
    
    tasks = []
    for file_name, file_description in file_structure:
        task = asyncio.create_task(agents.developers.developer_agent(file_name, file_description, final_plan))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
 
    logging.info("Game creation complete!")
    logging.info("Final game plan:")
    
    # Run the game in a loop to catch and fix errors, then enter feedback loop
    max_attempts = 10
    while True:
        error_message = await tools.run_game.run_game()
        tools.run_game.close_game()
        if error_message is None:
            logging.info(colored("Game ran successfully!", "green"))
            
            # Run the game with the image analysis agent
            error_details = agents.control_test.ControlTesterAgent(game_name)
            if error_details is None:
                logging.info(colored("✅ Game ran successfully! No issues detected.", "green"))
                print(colored("🎉 Game created successfully! You can now play.", "cyan"))  # ✅ User feedback
                break  
            logging.error(colored(f"❌ Movement issue detected: {error_details}", "red"))
            # Send the error message 
            await agents.code_updater.GameUpdater_Agent(error_details)  
            
        else:
            logging.error(colored(f"Error detected: {error_message}", "red"))
            for attempt in range(max_attempts):
                logging.info(f"Attempt {attempt + 1} to fix the errors...")
                await agents.code_repair.Code_Repair_Agent(error_message)
                time.sleep(1)  
                               
                # Try running the game again after fixing
                error_message = await tools.run_game.run_game()
                tools.run_game.close_game()
                if error_message is None:
                    logging.info(colored("Errors fixed successfully!", "green"))
                    break
                  
            else:
                logging.error(colored(f"Failed to fix all errors after {max_attempts} attempts.", "red"))
                user_choice = input(colored("Press Enter to continue error correcting, or type 'no' to quit: ", "yellow")).lower()
                if user_choice == 'no':
                    return

# Run the game creation process
if __name__ == "__main__":
    asyncio.run(main())