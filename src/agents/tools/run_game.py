import asyncio
import logging
import subprocess
import sys
import traceback
from termcolor import colored


game_process = None
async def run_game():
    global game_process
    if game_process is None or game_process.poll() is not None:
        logging.info(colored("Running the game...", "magenta"))
    full_output = ""
    full_error = ""
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", "import sys; sys.path.insert(0, 'game'); import main; main.main()"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logging.info("Game is running.")
        
        while True:
            try:
                output = process.stdout.readline()
                error = process.stderr.readline()
                
                if output:
                    full_output += output
                    logging.info(output.strip())
                if error:
                    full_error += error
                    logging.error(colored(f"Runtime error: {error.strip()}", "red"))
                
                if process.poll() is not None:
                    break
                
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                logging.info(colored("\nGame stopped by user.", "yellow"))
                process.terminate()
                break
        
        stdout, stderr = process.communicate()
        full_output += stdout
        full_error += stderr
        
        if process.returncode != 0:
            full_error += f"\nProcess exited with return code {process.returncode}"
        
    except Exception as e:
        full_error += f"\nError running game: {str(e)}\n{traceback.format_exc()}"
    
    error_summary = ""
    if full_error:
        error_summary += f"Runtime errors:\n{full_error}\n"
    if "error" in full_output.lower() or "exception" in full_output.lower():
        error_summary += f"Possible errors in output:\n{full_output}\n"
    
    if error_summary:
        logging.error(colored(error_summary, "red"))
        return error_summary
    else:
        return None

def close_game():
    """Terminates the running game process."""
    global game_process
    if game_process and game_process.poll() is None:  # Check if the process is still running
        game_process.terminate()  # Forcefully close the game
        game_process.wait()  # Ensure the process fully stops
        logging.info("✅ Game closed successfully.")
    else:
        logging.info("⚠ No active game process found to terminate.")
