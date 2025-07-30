import click
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
import subprocess
import os
import json
from dotenv import load_dotenv
import asyncio
import sys
from consolemenu import *
from consolemenu.items import *
from rich.console import Console
from rich.prompt import Prompt
from JINGKE2.utils.external import external_module
from JINGKE2.utils.generate import LLM
import shutil

console = Console()
load_dotenv()

# Load the API key from the .env file
API_KEY = os.getenv("GROQ_API_KEY")
SETTINGS_FILE = "utils/settings/credentials.json"

class Setup:
    def __init__(self):
        self.working_env = ""

        # Create the Environment folder
        environment_folder = os.path.join(os.getcwd(), "Environment")
        if not os.path.exists(environment_folder):
            os.makedirs(environment_folder)

        # Collect metadata from the user
        name_dir = input("Enter the name of the Project: ")
        user_dir = input("Enter the name of the User: ")
        version_dir = input("Enter the version of the Project: ")
        license_dir = input("Enter the License: ")

        # Use an arrow-key-controlled menu for VENV selection
        env_dir = input("Do you need to install VENV?(y / n): ")
        groq_usage = input("Do you want to use Groq?(y / n): ")
        ollama_usage = input("Do you want to use Ollama?(y / n): ")
        git_login = input("Do you want to login?(y / n): ")

        self.name = name_dir
        self.user = user_dir
        self.version = version_dir
        self.license = license_dir
        self.env_dir = env_dir  
        self.groq_usage = groq_usage
        self.ollama_usage = ollama_usage
        self.git_login = git_login

        subfolder_path = os.path.join(environment_folder, name_dir)
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)

        data = {
            "name": name_dir,
            "user": user_dir,
            "version": version_dir,
            "License": license_dir,
            "venv_required": env_dir,
            "directory": subfolder_path,
            "groq_usage": groq_usage,
            "ollama_usage": ollama_usage,
            "git_login":git_login
        }

        # Run the create_venv coroutine
        asyncio.run(self.create_venv(subfolder_path, env_dir))
        if (git_login == 'y' or git_login == 'Y'):
            try:
                """
                credentials = Setup.get_github_credentials()
                print("Retrieved credentials:")
                print(f"Username: {credentials['username']}")
                print(f"API Key: {credentials['api_key'][:4]}...")  # Partial key display

                # Example API usage
                import requests
                response = requests.get(
                    "https://api.github.com/user",
                    auth=(credentials['username'], credentials['api_key'])
                )
                print(f"\nGitHub User Data:\n{json.dumps(response.json(), indent=2)}")
                if response.status_code == 200:"""
                print("------------------------","\n<< This Feature is currently unavailable! >>","\n------------------------\n\n")
            except:
                print(f"Error Occured during login.")
        json_file_path = os.path.join(subfolder_path, "project_info.json")
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        self.working_env = subfolder_path
        print("------------------------","\n<< Setup Complete >>","\n------------------------\n\n")
    

    def get_github_credentials():
        """
        Retrieve GitHub credentials with comprehensive error handling
        Returns validated credentials dictionary
        """
        credentials = None
        
        try:
            # Check if credentials exist and are valid
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    credentials = json.load(f)
                    
                    # Basic validation
                    if not all(key in credentials for key in ('username', 'api_key')):
                        raise ValueError("Invalid credential format")
                    
                    return credentials

            # If no credentials found, launch auth flow
            print("No valid credentials found, launching login...")
            script_dir = os.path.dirname(os.path.realpath(__file__))
            print(sys.executable)
            git_script_path = os.path.join(os.getcwd(),"JINGKE2")
            git_script_path = os.path.join(git_script_path,"utils")
            git_script_path = os.path.join(git_script_path,"git.py")
            print(git_script_path)
            # Run the git.py script
            result = subprocess.run(
                [sys.executable, git_script_path],
                check=True,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Login failed: {result.stderr}")


        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            print(f"Invalid credentials file: {str(e)}")
            if os.path.exists(SETTINGS_FILE):
                os.remove(SETTINGS_FILE)
                print("Removed corrupted credentials file")
            return Setup.get_github_credentials()  # Restart auth flow

        except subprocess.CalledProcessError as e:
            print(f"Login process failed: {e.stderr}")
            sys.exit(1)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            sys.exit(1)


    async def create_venv(self, subfolder_path, env_dir):
        if env_dir.lower() == "y":
            print("Creating a virtual environment...")
            subprocess.run(["python", "-m", "venv", os.path.join(subfolder_path, "venv")])

            if os.name == "nt":
                venv_path = os.path.join(subfolder_path, "venv", "Scripts", "activate")
            else:
                venv_path = os.path.join(subfolder_path, "venv", "bin", "activate")
            subprocess.run([venv_path], shell=True)
            await asyncio.gather(
                external_module.loading_animation("Please Wait!", 5),
                asyncio.sleep(5)
            )
            print("------------------------","\n<< Virtual ENV created >>","\n------------------------\n\n")
    


    def JinOllama(self, model: str) -> str | None:
        chat = ChatOllama(model=model, temperature=0.5)

        prompt_template = """  
        Only provide the code in python, no explanations, no headers, and do not use "```". Avoid "```" while generating the code.
        """
        query = input("Enter the query: ")
        if query:
            system = prompt_template
            human = "{text}"
            prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
            chain = prompt | chat
            response = chain.invoke({"text": query})
            print(response.content)

"""class external_module:
    def optionSelector(options: list) -> str | None:
        console.print("Select an option:")
        for i, option in enumerate(options):
            console.print(f"{i+1}. {option}")
        console.print(f"{len(options)+1}. Exit")
        choice = Prompt.ask("Choose a option: ", choices=[str(i+1) for i in range(len(options))])
        if choice == str(len(options)+1):
            return None
        return options[int(choice) - 1]

    async def loading_animation(message: str, duration: int):
        "
        Display a loading animation asynchronously.

        Args:
            message (str): The message to display before the animation.
            duration (int): The duration of the animation in seconds.
        "
        animation = "|/-\\"
        print(message, end="", flush=True)
        for i in range(duration * 10): 
            sys.stdout.write(f"\r{message} {animation[i % len(animation)]}")
            sys.stdout.flush()
            await asyncio.sleep(0.1)  
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")"""

class Projectoperation:
    def getEnvfolder():
        environment_folder = os.path.join(os.getcwd(), "Environment")
        if not os.path.exists(environment_folder):
            print("No projects found. The 'Environment' folder does not exist.")
            return
        
        projects = os.listdir(environment_folder)  
        return projects
    #view the projects
    @staticmethod
    def ViewProject():
        projects = Projectoperation.getEnvfolder()
        if not projects:
            print("No projects found in the 'Environment' folder.")
        else:
            for i, project in enumerate(projects, start=1):
                if i == None:
                    pass
                print(f"{i}. {project}")

    @staticmethod
    def LoadProject()-> str | None:
        options = Projectoperation.getEnvfolder()
        a = external_module.optionSelector(options)
        dir = os.path.join(os.getcwd(), "Environment", a, "project_info.json")
        with open(dir, "r") as json_file:
            data = json.load(json_file)
            env = data.get("directory")
        """if data.get("groq_usage").lower() == "n":
            return ("Groq is not avaialble")"""
        if data.get("ollama_usage").lower() == "y":
            result = subprocess.run("ollama list", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.splitlines()
                model_names = []
                for line in lines[1:]:  
                    columns = line.split()
                    if columns:
                        model_names.append(columns[0])  
                print("------------------------","\n<<< Choose your model (ollama) >>>","\n------------------------")
                model = external_module.optionSelector(model_names)
                asyncio.run(LLM.JinOllama(model, env))
            else:
                print("Error running 'ollama list':", result.stderr)
                return []
        else:
            print("Ollama usage is not enabled for this project.")
            return []
        
    @staticmethod
    def RemoveProject()-> str | None:
        options = Projectoperation.getEnvfolder()
        a = external_module.optionSelector(options)
        path_a = os.path.join(os.getcwd(),"Environment",a)
        shutil.rmtree(path_a)
        return a
    
    @staticmethod
    def Code()-> str | None:
        options = Projectoperation.getEnvfolder()
        a = external_module.optionSelector(options)
        path = os.getcwd()
        new_path = os.path.join(path,"Environment",a)
        print(new_path)
        subprocess.run(["code", new_path], shell=True)