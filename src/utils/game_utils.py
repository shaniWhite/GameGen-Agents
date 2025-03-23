import asyncio
import logging
import os
import subprocess
import sys
import time
import keyboard
import pyautogui
import string


def start_game():
    """Starts the game and returns the subprocess handle."""
    print("🎮 Starting the game...")
    game_process = subprocess.Popen([sys.executable, "game/main.py"])
    time.sleep(2)  # Let the game boot up
    return game_process
        
def stop_game(process):
    """Stops the game process if it's running."""
    if process and process.poll() is None:
        # print("🛑 Attempting to terminate game process...")
        process.terminate()
        try:
            process.wait(timeout=5)
            logging.info("✅ Game process terminated.")
        except subprocess.TimeoutExpired:
            logging.warning("⚠️ Game not responding. Forcing kill.")
            process.kill()
            logging.warning("☠️ Game process force-killed.")      
        


async def run_game():
    logging.info("🎮 Starting game...")

    process = subprocess.Popen(
        [sys.executable, "game/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    logging.info("🕒 Letting the game run for 5 seconds...")
    time.sleep(10)

    logging.info("🛑 Time's up! Attempting to stop the game...")
    stop_game(process)

    # ✅ Now it's safe to collect remaining output
    try:
        stdout, stderr = process.communicate(timeout=3)
        logging.info("📝 Output:\n" + stdout)
        logging.info("🛑 Errors:\n" + stderr)
    except subprocess.TimeoutExpired:
        logging.warning("⚠️ Could not read output (timeout)")

    logging.info("✅ Game run completed.")
    
    
# async def run_game():
    
#     logging.info("Running the game...")
#     full_output = ""
#     full_error = ""
#     try:
#         process = subprocess.Popen(
#         [sys.executable, "-c", "import sys; sys.path.insert(0, 'game'); import main; main.main()"],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )
#         logging.info("Game is running.")
        
#         while True:
            
#             output = process.stdout.readline()
#             error = process.stderr.readline()
            
#             if output:
#                 full_output += output
#                 logging.info(output.strip())
#             if error:
#                 full_error += error
#                 logging.error(colored(f"Runtime error: {error.strip()}", "red"))
            
#             if process.poll() is not None:
#                 break
            
#             await asyncio.sleep(0.1)
            
#         # Wait for 5 seconds before terminating the game
#         await asyncio.sleep(15)

#         stdout, stderr = process.communicate()
#         full_output += stdout
#         full_error += stderr
        
#         # Send a close event like clicking X
#         logging.info(colored("🛑 Closing the game window after 5 seconds...", "yellow"))
#         stop_game(process)
#         logging.info(colored("✅ Game closed.", "green"))
        
#         if process.returncode != 0:
#             full_error += f"\nProcess exited with return code {process.returncode}"
        
#     except Exception as e:
#         full_error += f"\nError running game: {str(e)}\n{traceback.format_exc()}"
    
#     error_summary = ""
#     if full_error:
#         error_summary += f"Runtime errors:\n{full_error}\n"
#     if "error" in full_output.lower() or "exception" in full_output.lower():
#         error_summary += f"Possible errors in output:\n{full_output}\n"
    
#     if error_summary:
#         logging.error(colored(error_summary, "red"))
#         return error_summary
#     else:
#         return None


def simulate_input(action):
    """Simulates a keyboard press or mouse click based on AI instructions."""
    action = action.lower().strip()  # Normalize input

    # Keyboard actions
    if action in ["left", "right", "up", "down"]:
        logging.info(f"Pressing {action} key...")
        pyautogui.keyDown(action)
        time.sleep(0.3)
        pyautogui.keyUp(action)

    elif action in ["enter", "space"] or action in string.ascii_lowercase:
        logging.info(f"Pressing {action.capitalize()} key...")
        keyboard.press(action)
        time.sleep(0.2)
        keyboard.release(action)

    # Mouse actions
    elif action == "click":
        logging.info("Performing mouse click...")
        pyautogui.click()

    elif action == "double click":
        logging.info("Performing mouse double click...")
        pyautogui.doubleClick()

    elif action == "right click":
        logging.info("Performing right-click...")
        pyautogui.rightClick()

    elif action == "move mouse":
        logging.info("Moving mouse to center of the screen...")
        screen_width, screen_height = pyautogui.size()
        pyautogui.moveTo(screen_width // 2, screen_height // 2, duration=0.5)

    else:
        logging.error(f"⚠ Unknown action: {action}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_game())

