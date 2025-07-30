import os
import subprocess

class Runner:
    @staticmethod
    def coderunner(path):
        print("\n\n------------------------", f"<< Running {path}\\main.py >>", "------------------------\n")
        
        python_file = os.path.join(path, "main.py")
        error_file = os.path.join(path, "output.txt")
        command = [os.path.join(path, "venv", "Scripts", "python.exe"), python_file]

        # Run the command and capture stdout and stderr separately
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Print stdout to console
        print(process.stdout)
        
        # Only save stderr to output.txt
        with open(error_file, 'w') as f:
            f.write(process.stderr)
        
        # If there were errors, print them as well
        if process.stderr:
            print("Errors encountered:")
            print(process.stderr)
        
        # Return both stdout and stderr
        return process.stderr