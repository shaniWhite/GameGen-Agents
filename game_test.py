

import keyboard  # Make sure this is imported
import traceback  # Also make sure this is imported
import sys
import subprocess
import asyncio
import logging
from termcolor import colored
import time


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

        print(colored("🎮 Game is running...", "magenta"))
        start_time = time.time()

        # Loop without blocking on output
        while True:
            if process.poll() is not None:
                logging.info("✅ Game process has exited on its own.")
                break

            if time.time() - start_time > 10:
                print(colored("⏳ 10 seconds passed. Sending ESC to close the game...", "yellow"))
                keyboard.press("esc")
                time.sleep(0.1)
                keyboard.release("esc")

                break

            await asyncio.sleep(0.1)

        # Read remaining output after process exits
        try:
            stdout, stderr = process.communicate(timeout=3)
            full_output += stdout or ""
            full_error += stderr or ""
        except subprocess.TimeoutExpired:
            full_error += "\n⚠️ Timeout reading process output"

        if process.returncode and process.returncode != 0:
            full_error += f"\n🚨 Process exited with return code {process.returncode}"

    except Exception as e:
        full_error += f"\n💥 Exception: {str(e)}\n{traceback.format_exc()}"

    # Build error summary
    error_summary = ""
    if full_error.strip():
        error_summary += f"Runtime errors:\n{full_error.strip()}\n"
    if "error" in full_output.lower() or "exception" in full_output.lower():
        error_summary += f"Possible errors in output:\n{full_output.strip()}\n"

    if error_summary:
        logging.error(colored(error_summary, "red"))
        return error_summary
    else:
        return None

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(run_game())


