import click
from art import text2art
import keyboard
import asyncio
import subprocess
import os
# Corrected imports with absolute paths
from JINGKE2.utils.manageenv import Setup, Projectoperation
from JINGKE2.utils.external import external_module
from JINGKE2.utils.git import GitHubLoginApp
from JINGKE2.utils.API import Jingke_api_key, get_api, get_name
from JINGKE2.utils.user import User_creation
from time import gmtime, strftime
time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

@click.command()
@click.option('--init', '-i', is_flag=True, help=': Setup Jing ke for you.')
@click.option('--setup', '-s', is_flag=True, help=': Setup a project in the Environment.')
@click.option('--view', '-v', is_flag=True, help=': View the projects.')
@click.option('--load', '-l', is_flag=True, help=': Load the selected project.')
@click.option('--remove', '-rm', is_flag=True, help=': Remove the Project.')
@click.option('--vscode', '-vs', is_flag=True, help=': To Open the project in VS Code.')
@click.option('--git', '-git', is_flag=True, help=': Push the code into GITHUB.')
def Instruction(setup, view, load, remove, vscode, git, init):
    if setup:
        print("\n------------------------", "Setup Project >>>", "------------------------\n")
        if controller() == 200:
            a = Setup()
        else:
            print("Config your API,\nCheck your network connection.")
    elif view:
        print("\n------------------------", "View Projects >>>", "------------------------\n")
        if controller() == 200:
            Projectoperation.ViewProject()
        else:
            print("Config your API,\nCheck your network connection.")
    elif load:
        print("\n------------------------", "Load Project >>>", "------------------------\n")
        if controller() == 200:
            a = Projectoperation.LoadProject()
        else:
            print("Config your API,\nCheck your network connection.")
        print(a)
    elif remove:
        print("\n------------------------", "Remove a Project >>>", "------------------------\n")
        if controller() == 200:
            a = Projectoperation.RemoveProject()
            print(f"\nProject removed : {a}\n")
        else:
            print("Config your API,\nCheck your network connection.")
    elif vscode:
        print("\n------------------------", "Open Project in VS Code >>>", "------------------------\n")
        Projectoperation.Code()
    elif git:
        print("\n------------------------", "Push to GitHub >>>", "------------------------\n")
        if controller() == 200:
            project_list = Projectoperation.getEnvfolder()
            print(project_list)
            path = external_module.optionSelector(project_list)
            print(f"{path} is selected")
            new_path = os.path.join(os.getcwd(), "Environment", path)
            GitHubLoginApp.create_git(new_path)
        else:
            print("Config your API,\nCheck your network connection.")
    elif init:
        User_creation.initialize()

def main():
    Art = text2art("JINGKE 2.0")
    print(Art)
    Instruction()

def controller():
    api_key = get_api()  # Fetch API key from file or prompt user
    if api_key:
        status = Jingke_api_key(api_key)
        return status

if __name__ == "__main__":
    main()
