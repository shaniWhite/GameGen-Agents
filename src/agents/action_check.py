import os
import sys
import time
import base64
import pyautogui
import asyncio
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.window_utils import get_game_window, capture_screenshot, delete_screenshot, detect_and_mark_movement
from utils.file_utils import normalize_action_key
from utils.game_utils import start_game, stop_game, simulate_input
from utils.image_utils import encode_image_to_base64
import google.generativeai as genai

# Create a folder for saving screenshots (if it doesn’t exist)
screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

async def action_check_agent(game_name, actions):
    
    action_results = {}
    failed_actions = []
    
    game_process = start_game()
    time.sleep(1)
        
    # ✅ Simulate pressing 'P' to pause the game
    logging.info("Pausing the game...")
    simulate_input("p")
                
    game_window = get_game_window(game_name)
    if not game_window:
        logging.error(f"⚠️ Could not find window: {game_name}")
        return
    
    filtered_actions = [
        (action, button) for action, button in actions 
        if "pause" not in action.lower() and "close" not in action.lower() and "quit" not in action.lower() and "exit" not in action.lower()
    ]

    time.sleep(1)
    for action_name, action_key in filtered_actions:
        attempt = 0
        success = False
               
        while attempt < 3 and not success:
            
            logging.info(f"🔁 Testing: {action_name} ({action_key}) — Attempt {attempt + 1}")
            screenshot_before = capture_screenshot(game_name, "before", screenshot_folder)
            if not screenshot_before:
                logging.error("⚠ Could not capture 'before' screenshot.")
                break
                
            pyautogui.press("p")  #resume game
            logging.info("resuming game...")    
            time.sleep(0.2)
            simulate_input("p")  # resume game
            logging.info("resume game...")    
            time.sleep(0.2)

            simulate_input(normalize_action_key(action_key))
            time.sleep(0.2)

            simulate_input("p")  # pause game again
            time.sleep(0.5)

            screenshot_after = capture_screenshot(game_name, "after", screenshot_folder)
            if not screenshot_after:
                print("⚠ Could not capture 'after' screenshot.")
                break

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
                
            if screenshot_before and screenshot_after:
                prompt = f"""
                You will verify the correctness of the action: '{action_name}'.
                "Here are 3 screenshots from the game: {game_name}.:\n"
                    "1. The first image is the game screen **before** pressing the key '{action_key}' to make the action '{action_name}'.\n"
                    "2. The second image is the game screen **after** pressing the key '{action_key}.\n"
                    "3.The third image is an **annotated version** where the player's position **before movement** is highlighted with a red mark.\n\n"
                        "so in the third image, if the player is not where the red mark is, it means that he moved and you determine if the movement was correct or not."
                    "Your Task:\n"
                        "- Analyze the images to verify if the movement occurred as expected based on the action provided.\n"
                        "- Then, confirm whether the movement aligns with the key action that was suggested.\n\n"
                        
                        "How to Respond:\n"
                        "✅ If the expected movement **did** happen correctly, explicitly state that the movement worked.\n"
                        "❌ If the expected movement **did not** occur, provide a clear and specific explanation:\n"
                        "   - **Identify the key action that failed** (e.g., 'The left arrow key did not move the character left.')\n"
                        "   - **Describe what should have happened vs. what actually happened**\n"
                        "   - **Suggest possible reasons why the movement did not work** (e.g., key event not detected, movement function not updating, collision preventing movement)\n"
                        "   - **Most importantly, if a movement failure is detected, end your response with:** `PROBLEM OCCURRED`\n\n"
                        
                        "⚠ Important: Do **not** say 'no problem occurred' or the sequence 'problem occurred' if the movement happened as expected.
                        """
                

                # Encode the images correctly
                base64_image_before = encode_image_to_base64(screenshot_before)
                base64_image_after = encode_image_to_base64(screenshot_after)
                base64_diff = encode_image_to_base64(highlighted_path)

                
                contents = [
                    "This is the **before-action screenshot** (before pressing the movement key).",
                    {"mime_type": "image/jpeg", "data": base64.b64decode(base64_image_before)},
                    
                    "This is the **after-action screenshot** (after pressing the movement key).",
                    {"mime_type": "image/jpeg", "data": base64.b64decode(base64_image_after)},

                    "This is the **difference image** where movement is highlighted in white.",
                    {"mime_type": "image/jpeg", "data": base64.b64decode(base64_diff)},

                    prompt
                ]
            
                # Ask Gemini to evaluate
            try:
                response = model.generate_content(contents)
                verification_result = response.text.strip().lower()
                logging.info(f"🧠 Gemini response: {verification_result}")

                if "the movement worked" in verification_result:
                    success = True
                    action_results[action_name] = "Success"
                elif "problem occurred" in verification_result:
                    attempt += 1
                    if attempt >= 3:
                        action_results[action_name] = f"Failed: {verification_result}"
                        failed_actions.append(action_name)

            except Exception as e:
                logging.error(f"⚠ Gemini error: {e}")
                attempt += 1

        if not success:
            logging.error(f"❌ Action '{action_name}' failed after 3 attempts.\n")

    stop_game(game_process)
    logging.info("✅ All actions tested.")
    return action_results, failed_actions



# if __name__ == "__main__":
#     actions =[]
#     asyncio.run(action_check_agent("Pong Challenge", actions))
