
import subprocess
import pyautogui
import time
import sys
import openai
import base64
from io import BytesIO
from PIL import Image
import os
import pygetwindow as gw
import keyboard
from PIL import  ImageDraw
import cv2
import string
import logging
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("⚠ OpenAI API key not found! Exiting...")
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# Global variable for game process
game_process = None

def start_game():
    """Starts the game process if not already running."""
    global game_process
    if game_process is None or game_process.poll() is not None:
        logging.info("🎮 Starting the game...")
        game_process = subprocess.Popen([sys.executable, "game/main.py"])
        time.sleep(2)  # Allow time for the game to load


def get_game_window(game_name):
    """Finds the game window by title."""
    for window in gw.getWindowsWithTitle(game_name):  # Replace with the actual title
        return window
    return None

# Create a folder for saving screenshots (if it doesn’t exist)
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

paused = False  # ✅ Tracks whether the game is paused or running

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

def capture_screenshot(game_name, index):
    """Captures a screenshot of the game window."""
    game_window = get_game_window(game_name)
    if game_window:
        x, y, width, height = game_window.left, game_window.top, game_window.width, game_window.height
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{index}.png")
        screenshot.save(screenshot_path)
        logging.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    return None

def delete_screenshot(file_path):
    """Deletes the movement_diff.png file if it exists."""
    # file_path = "screenshots/movement_diff.png"
    
    if os.path.exists(file_path):
        os.remove(file_path)
        # print(f"🗑️ Deleted: {file_path}")
    else:
        logging.error(f"⚠ No file found: {file_path}")
        
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


def detect_and_mark_movement(before, after, output_path):
    """Detect the main moving object (e.g., the blue square) and mark both its previous and new positions."""
    
    # Load images in grayscale
    before_img = cv2.imread(before, cv2.IMREAD_GRAYSCALE)
    after_img = cv2.imread(after, cv2.IMREAD_GRAYSCALE)

    # Use Canny edge detection to find edges
    before_edges = cv2.Canny(before_img, 50, 150)
    after_edges = cv2.Canny(after_img, 50, 150)

    # Compute absolute difference between the edge images
    diff = cv2.absdiff(before_edges, after_edges)

    # Find contours in the difference image
    contours, _ = cv2.findContours(diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        logging.error("⚠ No movement detected!")
        return None

    # Find the largest contour (assuming it's the blue square)
    largest_contour = max(contours, key=cv2.contourArea)

    # Get bounding box around the detected object
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Convert the after image to PIL for drawing
    pil_img = Image.open(after).convert("RGB")
    draw = ImageDraw.Draw(pil_img)

    # Draw a **red circle** at the previous position (center of detected object)
    center_x, center_y = x + w // 2, y + h // 2
    draw.ellipse((center_x - 10, center_y - 10, center_x + 10, center_y + 10), outline="red", width=3)

    # Save result
    pil_img.save(output_path)
    logging.info(f" Movement detected and marked at: {output_path}")
    return output_path

def load_game_plan():
    """Loads the game_plan.xml file content as text."""
    xml_path = "game_plan.xml"
    try:
        with open(xml_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logging.warning("⚠ Warning: game_plan.xml not found. AI will not have game context.")
        return None

def ControlTesterAgent(game_name):
    """Runs the game loop until a problem occurs."""
    start_game()  # Start the game if not already running
    game_plan_text = load_game_plan()
    
    for i in range(3):  
        
        screenshot_before = capture_screenshot(game_name, "before")
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

        screenshot_after = capture_screenshot(game_name,"after")
        if not screenshot_after:
            logging.error("Game window not found after action. Skipping verification.")
            continue
        
        screenshot_diff = "screenshots/movement_diff.png"
        delete_screenshot(screenshot_diff)  # Delete previous diff image if exists
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
        logging.info(f"GPT Response: {verification_response}")

        if "problem occurred" in verification_response:
            
            logging.error("❌ Problem detected! Stopping game for repair.")
            if game_process and game_process.poll() is None:
                game_process.terminate()
                
            return verification_response
        
        logging.info("✅ No problem detected. Continuing game...")
        time.sleep(3)  # Wait before next move
# run_game("Moving Adventures")
# simulate_input("click")