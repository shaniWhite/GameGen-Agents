import os
import re
import sys
import time
from termcolor import colored
import openai
import logging
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("⚠ OpenAI API key not found! Exiting...")
    raise ValueError("Missing OPENAI_API_KEY environment variable")


PRINT_RESPONSE = True

async def Code_Repair_Agent(error_message):
    logging.info(colored("Attempting to fix the error...", "yellow"))
    
    # Extract all filenames from the error message
    error_filenames = re.findall(r'.*?([^/\\]+\.py)"', error_message)
    error_filenames = list(set(error_filenames))  # Remove duplicates
    file_contents = {}

    for filename in os.listdir('game'):
        if filename.endswith('.py'):
            with open(os.path.join('game', filename), 'r') as f:
                file_contents[filename] = f.read()
    
    system_message = """
    You are a Python game development expert. Your task is to fix errors in Pygame project files.
    Analyze the error message and the contents of the game files, then provide the corrected versions of the files.
    Remember that the game should start with a main module in the main.py file(main shouldn't take any arguments).
    Write clean, well-commented code that follows best practices.
    The game should support pausing by adding a 'paused' state. Pressing 'P' should toggle pause on/off, stopping all movement and physics updates.
    Ensure that Pygame is properly initialized before using any Pygame functions. The program must call pygame.init() before using pygame.event.get() or any other Pygame-related functions. 
    Additionally, check that the display is initialized using pygame.get_init() before attempting to render menus or handle events. 
    If pygame.quit() has been called, the program should not continue executing functions that rely on an active Pygame session.
    If you get the error "video system not initialized" it means your code is still trying to use Pygame functions after quitting Pygame.
    carefully reason about the error in a step by step manner ahead of providing the corrected code. no external files are allowed within the game. 
    One of the main goals is to review the logic of the code to ensure a playable and enjoyable game play experience for the user.
    <reasoning>
    reasoning about the error
    </reasoning>
    Return the corrected file contents in the following format only for the files that requires correction:
    <file name="filename.py">
    corrected_file_contents
    </file>
    """
    
    prompt = f"""An error occurred while running the Pygame project. Here's the error message:
    {error_message}
    Here are the contents of the files involved in the error:
    {file_contents}
    Please return the full contents of the Python code without any language-specific annotations (like '''python) or markdown formatting. The code should be clean, well-commented, and properly formatted.
    Please analyze the error and provide corrected versions of the files to resolve the error. return the full content of the files Remember that the game should start with a main module in the main.py file(main shouldn't take any arguments)."""
    
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
    # Extract corrected file contents from the response
    corrected_files = re.findall(r'<file name="(.*?)">(.*?)</file>', response.choices[0].message['content'], re.DOTALL)
    
    if corrected_files:
        for filename, content in corrected_files:
            file_path = os.path.join('game', filename)
            with open(file_path, 'w', encoding="utf-8") as f:
                f.write(content.strip())
            logging.info(f"Updated file: {filename}")
            
            # Ensure the file is written by reading it back
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
        logging.warning("No corrected file content found in the response.")
