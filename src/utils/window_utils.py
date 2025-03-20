
import pygetwindow as gw
import pyautogui
import os
import logging
import cv2
from PIL import Image, ImageDraw
import numpy as np
from mss import mss
import cv2
import time
import subprocess


def get_game_window(game_name):
    """Finds the game window by title."""
    for window in gw.getWindowsWithTitle(game_name):  # Replace with the actual title
        return window
    return None

def capture_screenshot(game_name, index, screenshot_folder):
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

    # Find the largest contour
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

def record_gameplay_video(game_name, video_file_path="gameplay.mp4", duration=5, fps=30):
    """
    Records gameplay video by capturing the game window.

    Parameters:
    - game_name (str): Title of the game window.
    - video_file_path (str): Path to save the recorded video.
    - duration (int): Recording duration in seconds.
    - fps (int): Frames per second for video recording.

    Returns:
    - str: Path to the saved video file or None if the window is not found.
    """
    
    print("🎮 Starting external game...")
    game_process = subprocess.Popen(["python", "game/main.py"])
    time.sleep(2)  
    
    # Get the game window position & size
    game_window = get_game_window(game_name)
    if not game_window:
        print(f"❌ Error: Game window '{game_name}' not found!")
        return None
    
    # Get the game window position & size
    x, y, width, height = game_window.left, game_window.top, game_window.width, game_window.height
    print(f"🎥 Recording game window at ({x}, {y}) with size {width}x{height}...")

    # Setup screen recording
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_file_path, fourcc, fps, (width, height))

    start_time = time.time()
    while time.time() - start_time < 5:
        screenshot = pyautogui.screenshot(region=(x, y, width, height))  # Capture only the game window
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to OpenCV format
        out.write(frame)
        
    # Stop recording and close the game
    out.release()
    
    cv2.destroyAllWindows()

    if game_process:
        game_process.terminate()
        print("✅ Game process terminated.")

    print(f"✅ Recording complete. Video saved to: {video_file_path}")
    return video_file_path
# record_gameplay_video("Grid Escape")