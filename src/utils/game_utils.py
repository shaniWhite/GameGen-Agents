import asyncio
import logging
import os
import subprocess
import sys
import time
import keyboard
import pyautogui
import string
import traceback
from termcolor import colored


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
    full_output = ""
    full_error = ""

    try:
        process = subprocess.Popen(
            [sys.executable, "-c", "import sys; sys.path.insert(0, 'game'); import main; main.main()"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(colored("🎮 Game is running...", "magenta"))
        start_time = time.time()

        # Loop without blocking on output
        while True:
            if process.poll() is not None:
                logging.info("✅ Game process has exited on its own.")
                break

            if time.time() - start_time > 6:
                print(colored("⏳ 10 seconds passed. Sending ESC to close the game...", "yellow"))
                keyboard.press("esc")
                time.sleep(0.1)
                keyboard.release("esc")

                break

            await asyncio.sleep(0.1)

        # Read remaining output after process exits
        try:
            stdout, stderr = process.communicate(timeout=3)
            full_output += stdout or ""
            full_error += stderr or ""
        except subprocess.TimeoutExpired:
            full_error += "\n⚠️ Timeout reading process output"

        if process.returncode and process.returncode != 0:
            full_error += f"\n🚨 Process exited with return code {process.returncode}"

    except Exception as e:
        full_error += f"\n💥 Exception: {str(e)}\n{traceback.format_exc()}"

    # Build error summary
    error_summary = ""
    if full_error.strip():
        error_summary += f"Runtime errors:\n{full_error.strip()}\n"
    if "error" in full_output.lower() or "exception" in full_output.lower():
        error_summary += f"Possible errors in output:\n{full_output.strip()}\n"

    if error_summary:
        logging.error(error_summary)
        return error_summary
    else:
        return None
 

def simulate_input(action):
    """Simulates a keyboard press or mouse click based on AI instructions."""
    
    if not action:
        logging.warning("⚠ simulate_input was given None or empty action. Skipping...")
        return
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


# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(run_game())

