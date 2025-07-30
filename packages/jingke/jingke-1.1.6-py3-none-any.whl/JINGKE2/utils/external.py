import sys
import asyncio
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class external_module:
    @staticmethod
    def optionSelector(options: list) -> str | None:
        """
        Display a list of options and allow the user to select one.
        """
        console.print("Select an option:")
        for i, option in enumerate(options):
            console.print(f"{i+1}. {option}")
        console.print(f"{len(options)+1}. Exit")
        choice = Prompt.ask("Choose an option: ", choices=[str(i+1) for i in range(len(options)+1)])
        if choice == str(len(options)+1):
            return None
        return options[int(choice) - 1]

    @staticmethod
    async def loading_animation(message: str, duration: int):
        """
        Display a loading animation asynchronously.

        Args:
            message (str): The message to display before the animation.
            duration (int): The duration of the animation in seconds.
        """
        animation = "|/-\\"
        print(message, end="", flush=True)
        for i in range(duration * 10):
            sys.stdout.write(f"\r{message} {animation[i % len(animation)]}")
            sys.stdout.flush()
            await asyncio.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
    
    @staticmethod
    async def loading():
        await asyncio.gather(
            external_module.loading_animation("Please Wait!", 5),
            asyncio.sleep(5)
        )
    async def fix():
        await asyncio.gather(
            external_module.loading_animation("Fixing issue ⚠️\t", 5),
            asyncio.sleep(5)
        )