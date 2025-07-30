from setuptools import setup, find_packages

# Read dependencies from requirements.txt
def read_requirements():
    try:
        with open("requirements.txt", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

setup(
    name="jingke",
    version="1.1.6",
    packages=find_packages(),
    install_requires=read_requirements(),  # Load dependencies dynamically
    entry_points={
        "console_scripts": [
            "jingke = JINGKE2.main:main",  # Calls the `main` function in main.py
        ],
    },
    author="R Kiran Kumar Reddy",
    author_email="ki2003167@gmail.com",
    description="A Python Developer, Used to generate, debug and upload the code in GITHUB.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.10",
)
