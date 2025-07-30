from colorama import Fore
import inquirer
import os
import subprocess
from art import *
import json

class User_creation:
    def __init__(self):    
        pass

    def initialize():

        questions = [
            inquirer.List('init',
                          message="Choose a operation to perform?",
                          choices=['Create', 'Edit'],
                          default='Create'),
        ]
        answers = inquirer.prompt(questions)
        is_private = answers['init'] 

        if is_private == 'Create':
            print(f"{Fore.RED}Setting up API Key:\t")
            username = input(f"{Fore.YELLOW}Enter Username :\t")
            api_key = input(f"{Fore.YELLOW}Enter your API Key:\t")
            usr_data = {
                "name":username,
                "api":api_key
            }
            path = os.path.join(os.getcwd(),"settings")
            if not os.path.exists(path):
                os.makedirs(path)
            json_file_path = os.path.join(path, "profile.json")
            with open(json_file_path, "w") as json_file:
                json.dump(usr_data, json_file, indent=4)
            
            return api_key
        else:
            print(f"{Fore.RED}Editting up API Key:\t")
            username = input(f"{Fore.YELLOW}Enter Username :\t")
            api_key = input(f"{Fore.YELLOW}Enter your API Key:\t")
            """
            from time import gmtime, strftime
            strftime("%Y-%m-%d %H:%M:%S", gmtime())
            """

            usr_data = {
                "name":username,
                "api":api_key
            }
            path = os.path.join(os.getcwd(),"settings")
            if not os.path.exists(path):
                os.makedirs(path)
            json_file_path = os.path.join(path, "profile.json")
            with open(json_file_path, "w") as json_file:
                json.dump(usr_data, json_file, indent=4)
            
            return api_key