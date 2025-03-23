

import asyncio
import logging
import os
import subprocess
import sys
import traceback
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from termcolor import colored
from utils.game_utils import stop_game
import time




# async def run_game():
#     logging.info("🎮 Starting game...")

#     process = subprocess.Popen(
#         [sys.executable, "game/main.py"],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )

#     logging.info("🕒 Letting the game run for 10 seconds...")
#     time.sleep(10)

#     logging.info("🛑 Time's up! Attempting to stop the game...")
#     stop_game(process)

#     full_output = ""
#     full_error = ""

#     try:
#         stdout, stderr = process.communicate(timeout=3)
#         full_output += stdout or ""
#         full_error += stderr or ""

#         logging.info("📝 Output:\n" + stdout)
#         logging.info("🛑 Errors:\n" + stderr)
#     except subprocess.TimeoutExpired:
#         full_error += "\n⚠️ Could not read output (timeout)"
#         logging.warning("⚠️ Could not read output (timeout)")

#     if process.returncode and process.returncode != 0:
#         full_error += f"\n🚨 Process exited with return code {process.returncode}"

#     error_summary = ""
#     if full_error.strip():
#         error_summary += f"Runtime errors:\n{full_error.strip()}\n"
#     if "error" in full_output.lower() or "exception" in full_output.lower():
#         error_summary += f"Possible errors in output:\n{full_output.strip()}\n"

#     if error_summary:
#         logging.error(colored(error_summary, "red"))
#         return error_summary
#     else:
#         return None

async def run_game():
    
    
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
        start_time = time.time()
        
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
                # 💡 Optional: auto-stop after 10 seconds
                if time.time() - start_time > 5:
                    logging.info("🛑 Auto-stopping game after 10 seconds...")
                    if process and process.poll() is None:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                            logging.info("✅ Game process terminated.")
                        except subprocess.TimeoutExpired:
                            logging.warning("⚠️ Game did not close. Forcing kill.")
                            process.kill()
                            logging.warning("☠️ Game process force-killed.")
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
    

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_game())
