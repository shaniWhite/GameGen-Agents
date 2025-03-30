
import logging
import re
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.error("⚠ OpenAI API key not found! Exiting...")
    raise ValueError("Missing OPENAI_API_KEY environment variable")

PRINT_RESPONSE = False

async def plan_project(user_input, iterations):
    system_message_1 = f"""
    You are a logical, critical game design expert. Your role is to discuss and plan with a critical and rigorous eye, a Pygame project based on user input. 
    -One of the main goals is to review the logic of the code to ensure a playable and enjoyable game play experience for the user.
    -Focus on game mechanics, structure, and overall design and function and method inputs(proper inputs and number of inputs) and returns of functions and methods. 
    -Do not suggest external media files or images.make sure no code files need any external files. all assets must be generated within pygame. 
    -you must select a meaningful and relevant game name that fits the gameplay theme.
    -Main purpose is to review and evaluate the project structure so that when the final files and their descriptions are prepared the code will function without any errors.
    -Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur. No need to discuss timelines or git commands.
    
    -When writing the game plan, concider the following instructions:
        1.Ensure that the game properly handles quitting. If the player closes the window by pressing 'X' button  or selects 'Quit' from a menu, the game must exit cleanly without trying to continue execution.
        2.The game should support pausing by adding a 'paused' state. Pressing 'P' should toggle pause on/off, stopping all movement and physics updates.
        3.You must follow this : Ensure that the actions provided follow this format exactly:
            actions = [('Move paddle up', 'P ARROW'), ('Move paddle down', 'DOWN ARROW'), ('Toggle pause', 'P'), ('Exit game', 'ESCAPE')]
        4.The game should support exiting it by adding a 'exit' action. pressing 'escape' on the keyboard should exit the game.
        5.Remember that the game should start with a main module in the main.py file! (main shouldn't take any arguments).


    here is the user input: {user_input}
    """
    
    system_message_2 = f"""
    You are a logical, critical Python architecture expert. Your role is to discuss and plan with a critical and rigorous eye the file structure for a Pygame project. 
    One of the main goals is to review the logic of the code to ensure a playable and enjoyable game play experience for the user.
    Focus on code organization, modularity, and best practices and function and method inputs(proper inputs and number of inputs) and returns of functions and methods . 
    Do not suggest external media files or images. make sure no code files need any external files. all assets must be generated within pygame. 
    you must select a meaningful and relevant game name that fits the gameplay theme.
    Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur. No need to discuss timelines or git commands.  
    Main purpose is to review and evaluate the project structure so that when the final files and their descriptions are prepared the code will function without any errors.
    
    When writing the game plan, concider the following instructions:
        1.Ensure that the game properly handles quitting. If the player closes the window by pressing 'X' button  or selects 'Quit' from a menu, the game must exit cleanly without trying to continue execution.
        2.The game should support pausing by adding a 'paused' state. Pressing 'P' should toggle pause on/off, stopping all movement and physics updates.
        3.The game should support exiting it by adding a 'exit' action. pressing 'escape' on the keyboard should exit the game.
        4.You must follow this : Ensure that the actions provided follow this format exactly:
            actions = [('Move paddle up', 'P ARROW'), ('Move paddle down', 'DOWN ARROW'), ('Toggle pause', 'P'), ('Exit game', 'ESCAPE')]
        5.Remember that the game should start with a main module in the main.py file! (main shouldn't take any arguments).
    here is the user input: {user_input}
    """
    messages_1 = [{"role": "user", "content": f"please plan a Pygame project based on the following user input: {user_input}. Remember that the game should start with a main module in the main.py file!"}]
    messages_2 = []
    
    for i in range(iterations):
        logging.info(f"Iteration {i+1} of {iterations} planning iterations")
        is_final = i == iterations - 1
        
        if is_final:
            
            messages_1.append({"role": "user", "content": "this is the final iteration. please provide your final game structure along with file structure you think is best for the game."
                               "don't return any directories but just the file names,descriptions, required actions and imports and the logic if required. Make sure to mention what imports are necessary for each file. Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur. "
                               "There should be 'paused' and 'exit' actions in addition to the game actions - Pressing 'P' in the keyboard should toggle pause on/off, stopping all movement and physics updates, and pressing 'escape' on the keyboard should exit the game."
                               "ensure function and method inputs are accurate as well as their returns. Remember that the game should start with a *main* module in the main.py file!(main shouldn't take any arguments)."})
        
        # messages_1 = insert_message_separator(messages_1)
        
        response_1 = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message_1}, *messages_1
            ],
            max_tokens=4000
        )

        if PRINT_RESPONSE:
            print(response_1.choices[0].message['content'])
        messages_1.append({"role": "assistant", "content": response_1.choices[0].message['content']})
        messages_2.append({"role": "user", "content": response_1.choices[0].message['content']})
        
        if is_final:
            messages_2.append({"role": "user", "content": 
                               """This is the final iteration. Please review the game design carefully and provide your final response in the XML format as in the end of this message. Follow these instructions in your response:\n
                                    1. All files should be in the same directory, provide only the file name without it's route!!!\n
                                    2. Don't return any additional directories but just the file names and descriptions along with simple description of functions and methods along with their inputs and returns. Please return descriptions for all files.\n
                                    3. Provide all game actions and there keys.\n
                                    4. The actions: 'paused' and 'exit' must appear in addition to the game actions - Pressing 'P' in the keyboard should toggle pause on/off, stopping all movement and physics updates, and pressing 'escape' on the keyboard should exit the game.\n
                                    5. You must follow this : Ensure that the actions provided follow this format exactly:
                                        actions = [('Move paddle up', 'P ARROW'), ('Move paddle down', 'DOWN ARROW'), ('Toggle pause', 'P'), ('Exit game', 'ESCAPE')]\n
                                    6. Make sure to mention what imports are necessary for each file.\n
                                    7. Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur as well as the clear and accurate definition of function and method inputs.\n
                                    8. Make sure that the game starts with a main module in the main.py file!(main shouldn't take any arguments).\n

                                    Your response needs to be in this XML format:\n
                                    <game_plan>\n  <overview>Overall game description</overview>\n  <game_name>Meaningful and relevant game name</game_name>\n  <window_size width="600" height="600"/>\n  <mechanics>Key game mechanics</mechanics>\n  <actions>\n    <action>Player action, button name</action>\n    <!-- Repeat <action> element for each action -->\n  </actions>\n  <files>\n    <file>\n      <name>filename.py</name>\n      <description>File purpose and contents</description>\n    </file>\n    <!-- Repeat <file> element for each file -->\n  </files>\n</game_plan>

                               """})
        
        # messages_2 = insert_message_separator(messages_2)
        
        response_2 = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message_2},
                *messages_2
            ],
            max_tokens=4000
        )
        
        if PRINT_RESPONSE:
            print(response_2.choices[0].message['content'])
        messages_2.append({"role": "assistant", "content": response_2.choices[0].message['content']})
        messages_1.append({"role": "user", "content": response_2.choices[0].message['content']})
    
    # Extract the XML content from the response
    xml_content = re.search(r'<game_plan>.*?</game_plan>', response_2.choices[0].message['content'], re.DOTALL)
    if xml_content:
        return xml_content.group(0)
    else:
        raise ValueError("No valid XML content found in the response")