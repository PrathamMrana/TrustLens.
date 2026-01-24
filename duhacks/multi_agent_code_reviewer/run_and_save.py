import subprocess
import os

print("Running test script...")
with open('test_output.txt', 'w') as f:
    subprocess.run(['python', 'verify_controller_git_s3.py'], stdout=f, stderr=subprocess.STDOUT)
print("Finished. Check test_output.txt")
