import os
import logging
import openai
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("⚠ OpenAI API key not found! Exiting...")
    raise ValueError("Missing OPENAI_API_KEY environment variable")

async def developer_agent(file_name, file_description, game_plan, actions):
    # create game folder if it doesnt exist
    os.makedirs("game", exist_ok=True)
    # Ensure the full directory exists before writing the file
    file_path = os.path.join("game", file_name)  # Get full path
    directory = os.path.dirname(file_path)  # Extract directory path

    if not os.path.exists(directory):  # Check if directory exists
        os.makedirs(directory, exist_ok=True)  # Create missing directories

    system_message = f"""
    You are a Python game development expert. Your task is to write a error free Python file for a Pygame game based on the overall project structure. 
    Always return the full contents of the file. One of the main goals is to review the logic of the code to ensure a playable and enjoyable game play experience for the user.
    Do not include any external media files or images in your code.
    Write clean, well-commented code that follows best practices.
    Ensure that Pygame is properly initialized before using any Pygame functions. The program must call pygame.init() before using pygame.event.get() or any other Pygame-related functions. 
    Additionally, check that the display is initialized using pygame.get_init() before attempting to render menus or handle events. 
    ensure that when pygame.quit() is detected, the game should stop immediately by exiting the main loop and properly shutting down Pygame.
    If pygame.quit() has been called, the program should not continue executing functions that rely on an active Pygame session.
    *** There maust be 'paused' and 'exit' actions in addition to the game actions - Pressing 'P' in the keyboard should toggle pause on/off, stopping all movement and physics updates, and pressing 'escape' on the keyboard should exit the game.***
    Use the actions provided by the planners in the XML file, {actions} ensure the described behavior is correctly mapped to the specified key press within the game.
    The game should start with a main module in the main.py file!(main shouldn't take any arguments).
    return the code for the file in the following format, Do not include markdown syntax like ```python or ```:
    <code>
    file_code
    </code>
    """
    
    prompt = f"""Create a Python file named '{file_name}' with the following description: {file_description}
    
    Here's the overall game plan which you should follow while writing the file:
    {game_plan}
    Please return the full contents of the Python code without any language-specific annotations (like '''python) or markdown formatting. The code should be clean, well-commented, and properly formatted.
    
    Remember, the game should start with a main module in the main.py file!(main shouldn't take any arguments). Always return the full contents of the file. Ensure all imports reference the correct filenames. Write clean, well-commented code that follows best practices.
    """
    
    response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
    )
    
    code = response.choices[0].message['content']
    code = code.split("<code>")[1].split("</code>")[0]
    with open(f"game/{file_name}", "w", encoding="utf-8") as f:
        f.write(code)
    
    logging.info(f"File '{file_name}' has been created.")
