
import xml.etree.ElementTree as ET
import logging


def parse_file_structure(xml_string):
    """Parses game details, including game name, window size, and file structure."""
    root = ET.fromstring(xml_string)
    
    # Extract game name
    game_name_elem = root.find("game_name")
    game_name = game_name_elem.text if game_name_elem is not None else "Unknown"

    # Extract window size
    window_size_elem = root.find("window_size")
    if window_size_elem is not None:
        width = window_size_elem.get("width")
        height = window_size_elem.get("height")
        window_size = (int(width), int(height)) if width and height else None
    else:
        window_size = None
        
    # Extract files
    files = []
    for file_elem in root.findall('.//file'):
        name = file_elem.find('name').text
        description = file_elem.find('description').text
        files.append((name, description))

    # Extract actions
    actions = []
    for action_elem in root.findall('.//actions/action'):
        action_text = action_elem.text.strip()
        if "," in action_text:
            action_name, button = map(str.strip, action_text.split(",", 1))  # Split into tuple
            actions.append((action_name, button))  # Store as tuple
            
    return game_name, window_size, files, actions


# Function to check for consecutive user messages and add a separator
def insert_message_separator(messages):
    for i in range(len(messages) - 1):
        if messages[i]["role"] == "user" and messages[i+1]["role"] == "user":
            messages.insert(i+1, {"role": "assistant", "content": "--- Next Message ---"})
    return messages

def load_game_plan():
    """Loads the game_plan.xml file content as text."""
    xml_path = "game_plan.xml"
    try:
        with open(xml_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        logging.warning("⚠ Warning: game_plan.xml not found. AI will not have game context.")
        return None
    
def normalize_action_key(action_key):
    """Maps keys to correct pyautogui key presses."""
    if not action_key:
        logging.warning("⚠ Warning: action_key is None or empty.")
        return None  

    key_mappings = {
        "left arrow": "left",
        "right arrow": "right",
        "space bar": "space",
        "up arrow": "up",
        "down arrow": "down",
        "enter": "enter",
    }
    # Remove "key: " prefix if present
    if action_key.lower().startswith("key: "):
        action_key = action_key[5:].strip()

    return key_mappings.get(action_key.lower(), action_key)
  

# normalize_action_key('key: UP ARROW')