
import os
import sys
import time
import re
import logging
from termcolor import colored
import openai

PRINT_RESPONSE = False

async def GameUpdater_Agent(user_feedback):
    # Gather all existing game files
    game_files = {}
    for root, dirs, files in os.walk('game'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    game_files[file] = f.read()

    # Prepare the prompt for the API
    file_contents = "\n\n".join([f"File: {filename}\n\n{content}" for filename, content in game_files.items()])
    
    prompt = f"""Here are the current contents of the Pygame project files:

    {file_contents}

    The user has provided the following feedback about the game:

    {user_feedback}

    Please analyze the feedback and suggest updates to the game files to address the user's comments. 
    Provide the full updated content for any files that need changes. 
    Return the updated file contents in the following format only for the files that require updates:
    <file name="filename.py">
    updated_file_contents
    </file>
    always return the full content of the files
    The game should support pausing by adding a 'paused' state. Pressing 'P' should toggle pause on/off, stopping all movement and physics updates.
    game should start with a main module in the main.py file(main shouldn't take any arguments).Write clean, well-commented code that follows best practices.
    Please return the full contents of the Python code without any language-specific annotations (like '''python) or markdown formatting. The code should be clean, well-commented, and properly formatted. 
    """
    
    system_message = """You are an expert Python and Pygame developer. Your task is to update a Pygame project based on user feedback. 
    Analyze the current game files and the user's feedback, then provide updated versions of any files that need changes to address the feedback. Always return the full content of the files. 
    One of the main goals is to review the logic of the code to ensure a playable and enjoyable game play experience for the user. no external files are allowed within the game
    Ensure that your changes are consistent with the existing code structure and Pygame best practices. Remember that the game should start with a main module in the main.py file(main shouldn't take any arguments)."""

    response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
    )
    
    if PRINT_RESPONSE:
        logging.info(colored(response.choices[0].message['content'], "magenta"))

    # Extract updated file contents from the response
    updated_files = re.findall(r'<file name="(.*?)">(.*?)</file>', response.choices[0].message['content'], re.DOTALL)

    if updated_files:
        for filename, content in updated_files:
            file_path = os.path.join('game', filename)
            with open(file_path, 'w', encoding="utf-8") as f:
                f.write(content.strip())
            logging.info(f"Updated file: {filename}")

            # Ensure the file is written correctly by reading it back
            with open(file_path, 'r') as f:
                written_content = f.read()
            if written_content.strip() != content.strip():
                logging.warning(f"Warning: File {filename} may not have been written correctly.")

        # Clear Python's module cache for the game directory, this may not be necessary
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('game.'):
                del sys.modules[module_name]

        time.sleep(1)  # Add a small delay to ensure files are fully written
    else:
        logging.info("No updates were necessary based on the user's feedback.")

