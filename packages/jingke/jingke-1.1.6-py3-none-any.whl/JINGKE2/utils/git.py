import os
import requests
import subprocess
import json
from colorama import Fore, Style, init
import inquirer
import shutil
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Initialize colorama
init(autoreset=True)

class GitHubLoginApp:
    @staticmethod
    def check_repo_exists(repo_name, token, username=None):
        """
        Check if a repository already exists for the user.
        """
        # If username not provided, get it from GitHub API
        if not username:
            user_url = "https://api.github.com/user"
            user_headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            user_response = requests.get(user_url, headers=user_headers)
            if user_response.status_code == 200:
                username = user_response.json()["login"]
            else:
                print(f"{Fore.RED}Failed to get user information.")
                return False, None
        
        # Check if the repository exists
        repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(repo_url, headers=headers)
        
        if response.status_code == 200:
            return True, response.json()["clone_url"]
        else:
            return False, None

    @staticmethod
    def create_github_repo(repo_name, token, description="", private=False):
        """
        Create a new GitHub repository using the GitHub API.
        """
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "name": repo_name,
            "description": description,
            "private": private
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 201:
            print(f"{Fore.GREEN}Repository '{repo_name}' created successfully!")
            return response.json()["clone_url"]
        else:
            print(f"{Fore.RED}Failed to create repository. Status code: {response.status_code}")
            print(f"{Fore.RED}Response: {response.text}")
            return None

    @staticmethod
    def is_git_repo(folder_path):
        """
        Check if the folder is already a git repository
        """
        original_dir = os.getcwd()
        try:
            os.chdir(folder_path)
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
        finally:
            os.chdir(original_dir)

    @staticmethod
    def remove_git_folder(path):
        """
        Cross-platform way to remove .git folder
        """
        git_folder = os.path.join(path, ".git")
        if os.path.exists(git_folder):
            try:
                shutil.rmtree(git_folder)
                return True
            except Exception as e:
                print(f"{Fore.RED}Error removing .git folder: {e}")
                return False
        return True
    
    @staticmethod
    def handle_venv_gitignore(folder_path):
        """
        Check if the folder contains a venv directory and add it to .gitignore if needed
        """
        # Check if venv folder exists
        venv_folder = os.path.join(folder_path, "venv")
        if os.path.exists(venv_folder) and os.path.isdir(venv_folder):
            gitignore_path = os.path.join(folder_path, ".gitignore")
            
            # Check if .gitignore exists and if venv is already in it
            venv_already_ignored = False
            if os.path.exists(gitignore_path):
                with open(gitignore_path, 'r') as f:
                    content = f.read()
                    # Check for common venv patterns in gitignore
                    venv_patterns = ["/venv/", "venv/", "/venv", "venv"]
                    for pattern in venv_patterns:
                        if pattern in content:
                            venv_already_ignored = True
                            break
            
            # Add venv to .gitignore if needed
            if not venv_already_ignored:
                print(f"{Fore.YELLOW}Found 'venv' folder. Adding to .gitignore...")
                
                # Prepare content to append
                append_content = "\n# Virtual Environment\nvenv/\n"
                
                # Ensure we don't add duplicate newlines
                if os.path.exists(gitignore_path):
                    with open(gitignore_path, 'r') as f:
                        existing_content = f.read()
                    if not existing_content.endswith('\n'):
                        append_content = '\n' + append_content
                
                # Append to .gitignore
                with open(gitignore_path, 'a+') as f:
                    f.write(append_content)
                print(f"{Fore.GREEN}Successfully added 'venv/' to .gitignore")
            else:
                print(f"{Fore.CYAN}'venv' already exists in .gitignore, no changes needed")

    @staticmethod
    def push_folder_to_github(folder_path, repo_url, token, force_reinit=False, force_add=True):
        """
        Initialize a Git repository in the folder (if needed) and push it to GitHub.
        
        Args:
            folder_path: Path to the folder to push
            repo_url: URL of the GitHub repository
            token: GitHub personal access token
            force_reinit: Force reinitialization even if it's a git repo
            force_add: Force add files even if they are in .gitignore
        """
        # Add token to the URL for authentication
        repo_url_with_token = repo_url.replace("https://", f"https://{token}@")
        
        # Save current directory
        original_dir = os.getcwd()
        
        try:
            # Change to the specified folder
            os.chdir(folder_path)
            
            # Check and handle venv folder in gitignore
            GitHubLoginApp.handle_venv_gitignore(folder_path)
            
            # Check if it's already a git repository
            is_repo = GitHubLoginApp.is_git_repo(".")
            
            if not is_repo or force_reinit:
                if is_repo and force_reinit:
                    print(f"{Fore.YELLOW}Reinitializing existing git repository...")
                    # Use cross-platform method to remove .git folder
                    GitHubLoginApp.remove_git_folder(".")
                
                # Initialize Git repository
                print(f"{Fore.CYAN}Initializing git repository...")
                subprocess.run(["git", "init"], check=True)
                
                # Configure remote
                print(f"{Fore.CYAN}Adding remote origin...")
                try:
                    subprocess.run(["git", "remote", "add", "origin", repo_url_with_token], check=True)
                except subprocess.CalledProcessError:
                    # If remote already exists, set its URL
                    subprocess.run(["git", "remote", "set-url", "origin", repo_url_with_token], check=True)
            else:
                # Repository already exists, just update the remote URL
                print(f"{Fore.CYAN}Using existing git repository...")
                try:
                    subprocess.run(["git", "remote", "add", "origin", repo_url_with_token], check=True)
                except subprocess.CalledProcessError:
                    # If remote already exists, set its URL
                    subprocess.run(["git", "remote", "set-url", "origin", repo_url_with_token], check=True)
            
            # Set Git config for first-time users if needed
            try:
                # Check if user.email is set
                email_check = subprocess.run(
                    ["git", "config", "user.email"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if not email_check.stdout.strip():
                    email = input(f"{Fore.YELLOW}Enter your email for Git commits: ")
                    subprocess.run(["git", "config", "user.email", email], check=True)
                    
                # Check if user.name is set
                name_check = subprocess.run(
                    ["git", "config", "user.name"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if not name_check.stdout.strip():
                    name = input(f"{Fore.YELLOW}Enter your name for Git commits: ")
                    subprocess.run(["git", "config", "user.name", name], check=True)
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Unable to set Git user config: {e}")
            
            # Add all files - use -f to force adding files that might be in .gitignore
            print(f"{Fore.CYAN}Adding files...")
            add_command = ["git", "add", "."]
            if force_add:
                add_command = ["git", "add", "-f", "."]
                print(f"{Fore.YELLOW}Forcing add of all files (including ignored files)...")
            
            try:
                subprocess.run(add_command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"{Fore.YELLOW}Warning: Some files may be ignored: {e}")
                
                # Ask user if they want to force add
                if not force_add:
                    questions = [
                        inquirer.List('force_add',
                                     message="Some files may be ignored. Force add all files?",
                                     choices=['Yes', 'No'],
                                     default='Yes'),
                    ]
                    answers = inquirer.prompt(questions)
                    if answers['force_add'] == 'Yes':
                        print(f"{Fore.CYAN}Forcing add of all files...")
                        subprocess.run(["git", "add", "-f", "."], check=True)
                    else:
                        print(f"{Fore.YELLOW}Using standard git add, some files may not be included...")
                        # Use a different approach - add only tracked files or those not in .gitignore
                        subprocess.run(["git", "add", "-u"], check=True)  # Update tracked files
            
            # Check if there are changes to commit
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                stdout=subprocess.PIPE,
                text=True
            )
            
            if status.stdout.strip():
                print(f"{Fore.CYAN}Committing changes...")
                try:
                    subprocess.run(["git", "commit", "-m", "Update project files"], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"{Fore.RED}Commit failed: {e}")
                    
                    # If commit fails, try to set up git user config and retry
                    try:
                        email = input(f"{Fore.YELLOW}Commit failed. Enter your email for Git commits: ")
                        name = input(f"{Fore.YELLOW}Enter your name for Git commits: ")
                        subprocess.run(["git", "config", "user.email", email], check=True)
                        subprocess.run(["git", "config", "user.name", name], check=True)
                        subprocess.run(["git", "commit", "-m", "Update project files"], check=True)
                    except subprocess.CalledProcessError:
                        print(f"{Fore.RED}Failed to commit changes even after setting user config")
                        raise
            else:
                print(f"{Fore.YELLOW}No changes to commit")
            
            # Push to GitHub
            print(f"{Fore.CYAN}Pushing to GitHub...")
            try:
                # Try to push to the current branch
                current_branch = subprocess.run(
                    ["git", "branch", "--show-current"],
                    stdout=subprocess.PIPE,
                    text=True,
                    check=True
                ).stdout.strip()
                
                if not current_branch:
                    current_branch = "main"  # Default to main if no branch is found
                    
                subprocess.run(["git", "push", "-u", "origin", current_branch], check=True)
                
            except subprocess.CalledProcessError:
                # If the push fails, try pushing to main/master
                try:
                    print(f"{Fore.YELLOW}Push failed, trying main branch...")
                    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
                except subprocess.CalledProcessError:
                    print(f"{Fore.YELLOW}Push to main failed, trying master branch...")
                    try:
                        subprocess.run(["git", "push", "-u", "origin", "master"], check=True)
                    except subprocess.CalledProcessError:
                        # As a last resort, try force push
                        print(f"{Fore.YELLOW}Standard push failed, attempting force push (use with caution)...")
                        try:
                            subprocess.run(["git", "push", "-f", "-u", "origin", current_branch or "main"], check=True)
                        except subprocess.CalledProcessError as e:
                            print(f"{Fore.RED}All push attempts failed: {e}")
                            raise
            
            print(f"{Fore.GREEN}Successfully pushed folder '{folder_path}' to GitHub repository!")
            
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Git operation failed: {e}")
        finally:
            # Change back to original directory
            os.chdir(original_dir)

    @staticmethod
    def create_git(folder_path):
        """
        Main function to handle GitHub repository creation and pushing.
        This is what will be called from the CLI.
        """
        print(f"{Fore.CYAN}GitHub Repository Setup")
        print(f"{Fore.CYAN}======================")
        
        dire = os.path.join(os.getcwd(),"settings")
        file = os.path.join(dire, "project_info.json")
        try:
            with open(file,'r') as f:
                data = json.load(f)
                token = data.get("TOKEN")
        except:
            token = ""        

        if not token:
            # Get GitHub token
            root = tk.Tk()
            app = GitHubUI(root)
            root.mainloop()
            #token = input(f"{Fore.YELLOW}Enter your GitHub token: ")
        
        # Get repository name (default to folder name)
        folder_name = os.path.basename(folder_path)
        repo_name = input(f"{Fore.YELLOW}Enter repository name [{folder_name}]: ") or folder_name
        
        # Get repository description
        repo_description = input(f"{Fore.YELLOW}Enter repository description (optional): ")
        
        # Ask if private
        questions = [
            inquirer.List('private',
                          message="Should the repository be private?",
                          choices=['No', 'Yes'],
                          default='No'),
        ]
        answers = inquirer.prompt(questions)
        is_private = answers['private'] == 'Yes'
        
        # Check if repository already exists
        print(f"{Fore.CYAN}Checking if repository already exists...")
        exists, repo_url = GitHubLoginApp.check_repo_exists(repo_name, token)
        
        if exists:
            print(f"{Fore.GREEN}Repository '{repo_name}' already exists, using it.")
        else:
            # Create GitHub repository
            print(f"{Fore.YELLOW}Repository '{repo_name}' doesn't exist, creating it.")
            repo_url = GitHubLoginApp.create_github_repo(repo_name, token, repo_description, is_private)
        
        if repo_url:
            # Ask if want to force reinitialize
            questions = [
                inquirer.List('reinit',
                            message="Force reinitialize git repository (if it exists)?",
                            choices=['No', 'Yes'],
                            default='No'),
            ]
            answers = inquirer.prompt(questions)
            force_reinit = answers['reinit'] == 'Yes'
            
            # Ask if want to force add files
            questions = [
                inquirer.List('force_add',
                            message="Force add all files (including ignored files)?",
                            choices=['Yes', 'No'],
                            default='Yes'),
            ]
            answers = inquirer.prompt(questions)
            force_add = answers['force_add'] == 'Yes'
            
            # Push folder to GitHub
            GitHubLoginApp.push_folder_to_github(folder_path, repo_url, token, force_reinit, force_add)
        else:
            print(f"{Fore.RED}Failed to get or create repository. Cannot push folder.")

class GitHubUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub Login")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        self.root.configure(bg="white")

        # Load and display the GitHub logo
        try:
            logo_url = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
            response = requests.get(logo_url)
            logo_image = Image.open(BytesIO(response.content))
            logo_image = logo_image.resize((100, 100), Image.ANTIALIAS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            self.logo_label = tk.Label(root, image=logo_photo)
            self.logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
            self.logo_label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load logo: {e}")

        # Create a frame for the login form
        self.frame = tk.Frame(root, padx=20, pady=20)
        self.frame.pack(expand=True)
        self.frame.configure(bg="white")

        # Title Label
        self.title_label = tk.Label(self.frame, text="GitHub Login", font=("Arial", 16, "bold"))
        self.title_label.configure(bg="white")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Username Label and Entry
        self.username_label = tk.Label(self.frame, text="Username:", font=("Arial", 12))
        self.username_label.configure(bg="white")
        self.username_label.grid(row=1, column=0, sticky="w", pady=5)

        self.username_entry = tk.Entry(self.frame, width=30, font=("Arial", 12))
        self.username_entry.grid(row=1, column=1, pady=5)

        # Password Label and Entry
        self.password_label = tk.Label(self.frame, text="Token:", font=("Arial", 12))
        self.password_label.configure(bg="white")
        self.password_label.grid(row=2, column=0, sticky="w", pady=5)

        self.password_entry = tk.Entry(self.frame, width=30, show="*", font=("Arial", 12))
        self.password_entry.grid(row=2, column=1, pady=5)

        # Login Button
        self.login_button = tk.Button(self.frame, text="Login", font=("Arial", 12), bg="#4CAF50", fg="white", command=self.validate_login)
        self.login_button.grid(row=3, column=0, columnspan=2, pady=20)

    def validate_login(self):
        try:
            username = self.username_entry.get()
            password = self.password_entry.get()

            path = os.path.join(os.getcwd(),"settings")
            if not os.path.exists(path):
                os.makedirs(path)
            data = {
                "USER_NAME" : username,
                "TOKEN" : password
            }
            json_file_path = os.path.join(path, "project_info.json")
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            messagebox.showinfo("Success", f"Information Added. You can close the login menu")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")



if __name__ == '__main__':
    root = tk.Tk()
    app = GitHubUI(root)
    root.mainloop()