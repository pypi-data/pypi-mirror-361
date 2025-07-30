from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
import os
import subprocess
import json
from JINGKE2.utils.codeeditor import Writer

class ErrorId:
    @staticmethod
    def get_last_code(file_path, key) -> str:
        with open(file_path, 'r') as file:
            data = json.load(file)
            last_code = data[key]
            return last_code
        
    @staticmethod
    def gettype(path, model):
        json_name = "query.json"
        temp_loc = os.path.join(path, json_name)
        chat = ChatOllama(model=model)
        error_file = os.path.join(path, "output.txt")
        
        with open(error_file, 'r') as f:
            error_output = f.read().lower()
        
        # Direct error pattern matching
        if "modulenotfounderror" in error_output:
            return "e1"
        
        # LLM classification for other errors
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Analyze this error strictly. Return ONLY the error code:
            - 'e1' ONLY for ModuleNotFoundError
            - 'e2' for ImportError
            - 'e3' for PermissionError
            - 'e0' for any other error
            No explanations, just the code."""),
            ("human", "Error log: {error_log}")
        ])
        
        chain = prompt_template | chat
        return chain.invoke({"error_log": error_output}).content

    
    @staticmethod
    def ModuleFix(path, model):
        chat = ChatOllama(model=model)
        error = os.path.join(path, "output.txt")

        with open(error, 'r') as f:
            output = f.read()

        template = f""" 
            Provide only the Windows simple command to fix this issue: {output}. Do not include any explanation or commands for Linux or Mac. Do not use any markdown code blocks. Only output the command to install dependencies, and avoid any other extraneous information.
            do not use "``````" while generating the code.
        """

        system = template
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
        chain = prompt | chat

        fix = chain.invoke("").content.strip()

        venv_dir = os.path.join(path, "venv")
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")

        subprocess.run([python_exe, "-m", "ensurepip"], check=True)
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "pip"], check=True)

        command = fix.split()
        subprocess.run([python_exe, "-m"] + command, check=True)

        print("\nFixing More Issues ...\n\n")

    @staticmethod
    def CodeFix(path,model)-> None:
        chat = ChatOllama(model=model)
        error = os.path.join(path, "output.txt")
        json_name = "query.json"
        temp_loc = os.path.join(path, json_name)
        code = ErrorId.get_last_code(temp_loc, "response")
        with open(error, 'r') as f:
            output = f.read()

        template = f"""
        I have a code : {code}. I got this output: {output}.  
        rewrite the code to fix this error. 
        Only provide the code in python, no explanations, no headers, and do not use "``````" while generating the code.
            avoid explanation and don't use "``````" even if the context is large.
            avoid this "Here is the code with all comments removed:
                ```python"
                avoid this at the end of the code "```"
        """

        system = template
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
        chain = prompt | chat

        fix = chain.invoke("").content.strip()
        Writer.writeCode(code,path)
        print("\nFixing More Issues ...\n\n")

