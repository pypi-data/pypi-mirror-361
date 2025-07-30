import requests
import json
import os
from art import *
from JINGKE2.utils.user import User_creation

def verify_api_key(api_key):
    """
    Verify if the API key is valid by calling the dynamic Next.js API route.

    Args:
        api_key (str): The API key to verify.

    Returns:
        dict: The response from the API.
    """
    url = f"https://jingke-server.vercel.app/api/verify/{api_key}"  # Dynamic API route

    try:
        response = requests.get(url)  # No explicit method like POST
        response.raise_for_status()  # Raise error if request fails

        return response.json() if response.text.strip() else {"success": False, "message": "Empty response"}

    except requests.exceptions.JSONDecodeError:
        print("Error: Response is not valid JSON.")
        print("Response text:", response.text)
        return {"success": False, "message": "Invalid JSON response"}

    except requests.exceptions.RequestException as e:
        print(f"Error: Unable to connect to API. {str(e)}")
        return {"success": False, "message": str(e)}

def Jingke_api_key(api_key):
    result = verify_api_key(api_key)
    if result.get("success"):
        return 200
    else:
        print(f"Error: {result.get('message')}")
        return 404

def get_api():
    settings_dir = os.path.join(os.getcwd(), "settings")
    file_path = os.path.join(settings_dir, "profile.json")
    if not os.path.exists(file_path):
        User_creation.initialize()
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("api")
    except (FileNotFoundError, json.JSONDecodeError):
        print("\nError: Unable to load API key from profile.json.\n")
        return None

def get_name():
    settings_dir = os.path.join(os.getcwd(), "settings")
    file_path = os.path.join(settings_dir, "profile.json")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get("name")
    except (FileNotFoundError, json.JSONDecodeError):
        return None
