
import xml.etree.ElementTree as ET

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
        
    return game_name, window_size, files 

# Function to check for consecutive user messages and add a separator
def insert_message_separator(messages):
    for i in range(len(messages) - 1):
        if messages[i]["role"] == "user" and messages[i+1]["role"] == "user":
            messages.insert(i+1, {"role": "assistant", "content": "--- Next Message ---"})
    return messages
