
import os
import re
import openai

async def action_fix_agent(failed_actions):
    print("🔧 Fixing failed actions...")
    
    # Read all game files
    game_files = {}
    for file in os.listdir("game"):
        if file.endswith(".py"):
            with open(f"game/{file}", "r", encoding="utf-8") as f:
                game_files[file] = f.read()

    # Prepare system message
    system_message = """
    You are a Python and Pygame expert. Your task is to fix game actions that are not working correctly.
    - You will receive a list of failed actions (without explanations).
    - You will receive the current game files.
    - Your goal is to fix the necessary files so that these actions work correctly.
    - Ensure no circular imports or broken logic occur.
    - Make sure that the game starts with a main module in the main.py file!(main shouldn't take any arguments).
    """

    failed_action_text = "\n".join(failed_actions)  # Only action names
    file_contents = "\n".join([f"File: {name}\n\n{code}" for name, code in game_files.items()])

    # Prepare prompt
    prompt = f"""
    The following game actions failed during testing: {failed_action_text}
    
    Here are the current game files:
    
    {file_contents}
    
    Please fix the failed actions and update the necessary files.
    Return **only the corrected files** in this format:
    <file name="filename.py">
    corrected_file_contents
    </file>
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        max_tokens=4000,
    )

    print(response.choices[0].message.content)

    # Extract updated files from response
    updated_files = re.findall(r'<file name="(.*?)">(.*?)</file>', response.choices[0].message.content, re.DOTALL)

    if updated_files:
        for filename, content in updated_files:
            file_path = os.path.join("game", filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"Updated file: {filename}")
    
    else:
        print("No updates were necessary or detected.")