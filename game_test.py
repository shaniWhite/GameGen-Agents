import subprocess
import time

proc = subprocess.Popen(["python", "game/main.py"])
print("Started game...")
time.sleep(5)

print("Terminating...")
proc.terminate()
try:
    proc.wait(timeout=3)
    print("Terminated cleanly.")
except subprocess.TimeoutExpired:
    print("Didn't die. Killing it.")
    proc.kill()
