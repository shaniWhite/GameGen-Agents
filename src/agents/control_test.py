

import time
import openai
import base64
from io import BytesIO
from PIL import Image
import os
import string
import logging
import sys
import keyboard
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
from utils.window_utils import capture_screenshot, detect_and_mark_movement, delete_screenshot
from utils.file_utils import load_game_plan
from utils.game_utils import  start_game, simulate_input


# Configure logging
logging.basicConfig(
    filename="game_log2.txt",  
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


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("⚠ OpenAI API key not found! Exiting...")
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# Global variable for game process
game_process = None



# Create a folder for saving screenshots (if it doesn’t exist)
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

def extract_action(answer):
    """Extracts the relevant action (key or mouse command) from the AI response."""
    answer = answer.lower().strip()  # Normalize input

    # Define valid actions
    valid_actions = ["left", "right", "up", "down", "enter", "space",
                     "click", "double click", "right click", "move mouse"] + list(string.ascii_lowercase)

    # Find which valid action appears in the response
    for action in valid_actions:
        if action in answer:
            return action  # Return the first matching action

    return None  # Return None if no valid action is found

def toggle_pause():
    """Toggles the game's pause state using the 'P' key."""
    global paused

    if paused:
        logging.info("Resuming game...")  # ✅ Only resume if game is actually paused
    else:
        logging.info("Pausing game...")   # ✅ Only pause if game is running

    keyboard.press("p")
    time.sleep(0.3)
    keyboard.release("p")
    time.sleep(0.5)  # ✅ Allow time for the game to register pause/unpause

    paused = not paused  # ✅ Toggle the pause state


paused = False  # ✅ Tracks whether the game is paused or running
def ControlTesterAgent(game_name):
    """Runs the game loop until a problem occurs."""
    game_plan_text = load_game_plan()
    start_game()  # Start the game if not already running
    
    for i in range(3):  
        screenshot_before = capture_screenshot(game_name,"before",screenshot_folder)
        if not paused:
            toggle_pause()
        if not screenshot_before:
            logging.error("Game window not found. Skipping iteration.")
            continue
        
        buffered = BytesIO()
        Image.open(screenshot_before).save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        messages = [
        {"role": "system", "content": "You are playing a game. I will show you a screenshot of the game and you will tell me how to proceed."}
        ]
        
        if game_plan_text:
            messages.append(
                {"role": "user", "content": [
                    {"type": "text", "text": "To help you understand the game, here is the game plan, read it carefuly:\n\n" + game_plan_text}
                ]}
            )
        messages.append(
        {"role": "user", "content": [
            {"type": "text", "text": "This is the game screenshot. What button should I press next? you have to provide any of the following commands: right, left, up, down, enter, space, click, double click, right click, move mouse"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"}}
        ]})
        messages.append(
        {"role": "assistant", "content": " response example: press 'left' " }  
        )
        
        # Send image to OpenAI API (GPT-4 Vision)
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        
        answer = response.choices[0].message.content.lower()
        print(f"Model suggestion: {answer}")
        logging.info(f"Model suggestion: {answer}")
        action = extract_action(answer)
        if not action:
            logging.error("⚠ Unable to extract action from response. Skipping iteration.")
            continue
        else:
            toggle_pause()  # resume the game before taking action
            simulate_input(action)        
            toggle_pause () # pause the game after taking action
            time.sleep(1)  

        screenshot_after = capture_screenshot(game_name,"after", screenshot_folder)
        if not screenshot_after:
            logging.error("Game window not found after action. Skipping verification.")
            continue
        
        screenshot_diff = "screenshots/movement_diff.png"
        if os.path.exists(screenshot_diff):
            delete_screenshot(screenshot_diff)  # Delete previous diff image if exists
        else:
            logging.info(f"⚠ File {screenshot_diff} does not exist. Skipping deletion.")
        highlighted_path = detect_and_mark_movement(screenshot_before, screenshot_after, screenshot_diff)

        # Check if the function successfully created the file
        if highlighted_path:
            logging.info(f" Highlighted movement image saved: {highlighted_path}")
        else:
            logging.error("⚠ Movement highlight image was not created!")
        
        messages=[
            {"role": "system", "content": "You are analyzing a game screen to verify if the movement happened as expected, if not, you should report the problem to the repair team."},
        ]
        # Prepare the list of images
        image_data = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(open(screenshot_before, 'rb').read()).decode()}"}},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(open(screenshot_after, 'rb').read()).decode()}"}}
        ]
        # Only add the highlighted movement image if the file exists
        if os.path.exists(screenshot_diff):
            image_data.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(open(screenshot_diff, 'rb').read()).decode()}"}}
            )
        messages.append(
            {"role": "user", "content": [
                {"type": "text", "text": (
                    "I am sending you three images:\n"
                    "1. The first image is the game screen **before** pressing the key you suggested.\n"
                    "2. The second image is the game screen **after** pressing the key.\n"
                    "3.The third image is an **annotated version** where the player's position **before movement** is highlighted with a red mark.\n\n"
                        "so in the third image, if the player is not where the red mark is, it means that he moved and you determine if the movement was correct or not."
                    "Your Task:\n"
                        "- Analyze the images to verify if the movement occurred as expected based on the suggested key action.\n"
                        "- Then, confirm whether the movement aligns with the key action that was suggested.\n\n"
                        
                        "How to Respond:\n"
                        "✅ If the expected movement **did** happen correctly, explicitly state that the movement worked.\n"
                        "❌ If the expected movement **did not** occur, provide a clear and specific explanation:\n"
                        "   - **Identify the key action that failed** (e.g., 'The left arrow key did not move the character left.')\n"
                        "   - **Describe what should have happened vs. what actually happened**\n"
                        "   - **Suggest possible reasons why the movement did not work** (e.g., key event not detected, movement function not updating, collision preventing movement)\n"
                        "   - **Most importantly, if a movement failure is detected, end your response with:** `PROBLEM OCCURRED`\n\n"
                        
                        "⚠ Important: Do **not** say 'no problem occurred' or the sequence 'problem occurred' if the movement happened as expected."
                )}, *image_data
            ]}
        ),
        messages.append(
        {"role": "assistant", "content": (
            "**Example of a response when movement works:**\n"
            "\"The movement happened as expected. The character moved from position A to position B, aligning with the suggested action.\"\n\n"
            "**Example of a response when movement fails**\n"
            "\"The movement did not happen as expected. After pressing the left arrow key, the character remained at the same position instead of moving left**.\n "
            "Possible causes: key event is not being detected properly.\n The movement function is not updating the character’s position.\n"
            "There is a collision or restriction preventing movement.\n\n"
            "Action Required: Investigate why the left arrow key does not move the character.\n"
            "PROBLEM OCCURRED"
        )})
        
        if game_plan_text:
            logging.info("Game plan text found.")
            messages.append(
                {"role": "user", "content": [
                    {"type": "text", "text": "To help you understand the game, here is the game plan, read it carefuly:\n\n" + game_plan_text}
                ]}
            )
            
        # Send screenshots to GPT-4 Vision to check if the movement happened
        response = openai.ChatCompletion.create(
        model="gpt-4o", 
        messages=messages
    )
        
        verification_response = response.choices[0].message.content.lower()
        print(f"GPT Response: {verification_response}")
        logging.info(f"GPT Response: {verification_response}")

        if "problem occurred" in verification_response:
            
            logging.error("❌ Problem detected! Stopping game for repair.")
            if game_process and game_process.poll() is None:
                game_process.terminate()
                
            return verification_response
        
        logging.info("✅ No problem detected. Continuing game...")
        time.sleep(3)  # Wait before next move

# ControlTesterAgent("Grid Escape")