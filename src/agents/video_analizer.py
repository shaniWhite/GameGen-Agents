

import time
import google.generativeai as genai
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.window_utils import record_gameplay_video
import logging

def analyze_game_video(game_name, game_plan_path="game_plan.xml"):
    """
    Uploads a recorded gameplay video and the game plan XML file to Gemini AI and gets feedback with timestamps.
    """
    video_file_path= record_gameplay_video(game_name)
    
    # Upload the video file
    logging.info(f"📤 Uploading video file: {video_file_path}...")
    if not os.path.exists(video_file_path):
        logging.error("❌ Error: Video file does not exist!")
        return None
    
    video_file = genai.upload_file(path=video_file_path)
    game_plan_file = genai.upload_file(path=game_plan_path)

    # Check the file processing state
    for file in [video_file, game_plan_file]:
        while file.state.name == "PROCESSING":
            logging.info(f"⏳ Processing file: {file.name}... Waiting...")
            time.sleep(10)
            file = genai.get_file(file.name)

        if file.state.name == "FAILED":
            raise ValueError(f"❌ [ERROR] File processing failed: {video_file.state.name}")
           
    # Read the game plan XML content
    with open(game_plan_path, "r", encoding="utf-8") as f:
        game_plan_content = f.readlines()
        
    # print("📄 Game Plan Content:\n","".join(game_plan_content[:10]))
    game_plan_text = "".join(game_plan_content)
       
    # Construct the AI prompt
    prompt = prompt = f"""
    Watch this gameplay video and describe in **one sentence** what is visible on the screen - everything that you saw.
    Then, provide the most critical improvement suggestions. Prioritize aspects that will have the biggest impact on the player's experience.
    
    Review **only** based on what you see in the video — do not assume features or use previous responses.

    1. Screen Description - Summarize in one sentence what is visible in the gameplay footage (e.g., "A character is jumping on platforms in a dark cave setting with no visible UI").

    22. Game Mechanics** - Are the controls intuitive? Is the game balanced and engaging? Are there any noticeable issues with movement, physics, or interactions? 

    32. User Interface (UI) - Is the UI clear, responsive, and user-friendly? Are important game elements (e.g., health bars, scores, instructions) easily visible?
    give up to 3 improvement suggestions.
    
    4. provide 2 good points about the game that should be maintained.
    
    5. This is the game plan for the game. Please analyze the gameplay video and verify that the game functions as planned. 
    Identify any inconsistencies or missing elements.
    Game Plan:
    {game_plan_text}
    
    Focus on **actionable feedback** that can lead to significant improvements. Be concise and to the point. Avoid generic advice—tailor suggestions specifically to the observed gameplay.
    """
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    # Generate content (Ask Gemini to analyze the video)
    # print("🔍 Asking Gemini")
    try:
        response = model.generate_content(
            [video_file, prompt],
            request_options={"timeout": 600}  # 10-minute timeout for video processing
            
        )
        logging.info("📢 Gemini Feedback on video:\n%s\n--- End of feedback ---", response.text)

        return response.text  # ✅ Return AI feedback
    except Exception as e:
        logging.error(f"❌ [ERROR] Failed to analyze video: {e}")
        return None
    

# analyze_game_video("Pong Battle")