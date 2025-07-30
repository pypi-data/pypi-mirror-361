# JINGKE 2.0

JINGKE 2.0 is a command-line tool designed to streamline project management, environment setup, and GitHub integration.

## Features
- **Project Setup**: Easily initialize and configure your development environment.
- **Project Management**: View, load, and remove projects effortlessly.
- **VS Code Integration**: Open projects directly in Visual Studio Code.
- **GitHub Support**: Push your project to GitHub seamlessly.
- **User Initialization**: Set up your user profile for personalized usage.

## Installation
```sh
pip install jingke
```

## Usage
Run the following command to access the tool:
```sh
jingke --help
```

### Available Commands
- `--init, -i` : Setup Jingke for first-time use.
- `--setup, -s` : Initialize a project in the environment.
- `--view, -v` : View all available projects.
- `--load, -l` : Load a selected project.
- `--remove, -rm` : Remove a project from the environment.
- `--vscode, -vs` : Open the project in VS Code.
- `--git, -git` : Push the project to GitHub.

## Example Usage
```sh
jingke -s  # Setup a new project
jingke -v  # View existing projects
jingke -l  # Load a project
jingke -vs # Open project in VS Code
jingke -git # Push project to GitHub
```

## API Authentication
JINGKE requires an API key for authentication. Ensure you have a valid API key configured before running the tool.

## License
This project is licensed under the MIT License.

## Contributing
Feel free to submit pull requests or report issues. We welcome contributions!

## Contact
For any inquiries, contact the developer or open an issue on GitHub.