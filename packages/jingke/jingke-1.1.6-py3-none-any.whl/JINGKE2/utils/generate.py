import asyncio
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from JINGKE2.utils.codeeditor import Writer
from JINGKE2.utils.external import external_module
from JINGKE2.utils.Code.coderunner import Runner
from JINGKE2.utils.test.fixissues import ErrorId
import subprocess
import os
import json
import re
import sys

class LLM:
    def __init__(self):
        pass
    
    def get_python_code(response):
        code_blocks = re.findall(r"```python\n(.*?)```", response, re.DOTALL)
        return "\n\n".join(code_blocks) if code_blocks else response  # Fallback if no markdown format


    @staticmethod
    def get_last_code(file_path, key) -> str:
        with open(file_path, 'r') as file:
            data = json.load(file)
            last_code = data[key]
            return last_code
    
    @staticmethod
    async def error_fixer_ModuleNotFound(path,model) -> None:
        """output_path = os.path.join(path,"output.txt") 
        with open(output_path, 'r') as f:
            output = f.read()"""
        r = ErrorId.gettype(path,model)
        print(r)
        if r == 'e1' or r == 'E1' :
            await external_module.fix()
            ErrorId.ModuleFix(path,model)
            Runner.coderunner(path)
            await LLM.error_fixer_ModuleNotFound(path,model)
        elif r == 'e2' or r == 'E2':
            await external_module.fix()
            ErrorId.CodeFix(path,model)
            await LLM.error_fixer_ModuleNotFound(path,model)
        else:
            print("\n------------------------", f"<< Error Fixed ✅ >>", "------------------------\n")

    @staticmethod
    async def JinOllama(model: str, path: str) -> str | None:
        """
        Asynchronous method to process a query using ChatOllama and write the response to a file.
        """
        chat = ChatOllama(model=model, temperature=0.5)
        prompt_template = f"""  
        Only provide the code in python, no explanations, no headers, and do not use "``````" while generating the code.
        your project location is {path}. No need to mention the path inside the code, if you want to then comment it out.
        """
        print("\n\n------------------------", f"<< Working on {path} >>", "------------------------\n")
        await external_module.loading()  # Changed from asyncio.run()
        json_name = "query.json"
        temp_loc = os.path.join(path, json_name)
        main_pot = os.path.join(path,"main.py")
        if not os.path.exists(main_pot):
            # Prepare the prompt
            #save the json, if is not created
            if not os.path.exists(temp_loc):
                query = input("Prompt : ")
                query= query+f"my project location is {path}. If you save anything save here. If loaction required, then :Use full location, if you want to store anything. If not required : No need to use"
                system = prompt_template
                human = "{text}"
                prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
                chain = prompt | chat
                # Invoke the chain asynchronously
                response = await chain.ainvoke({"text": query})  # Changed to ainvoke
                res = response.content
                # Install all required dependencies:
                a = LLM.get_python_code(res)
                # Write the response to the specified path
                Writer.writeCode(a, path)
                print(f"Code has been written to {path}")
                data = {
                    "prompt": query,
                    "response": a
                }
                """python_file = os.path.join(path,"main.py")
                command = f"start cmd /k {path}/venv/Scripts/python.exe {python_file}"
                result = subprocess.Popen(command, shell=True)
                py_location = os.path.join(path,"venv/Scripts/python.exe")
                script_path = os.path.join(path, "main.py")
                file_path = os.path.join(path, "error.txt")
                with open(file_path, 'w') as f:
                    subprocess.run([py_location, script_path], stderr=f)
                with open(file_path, 'r') as f:
                    output = f.read()"""
                with open(temp_loc, 'w') as f:
                    json.dump(data, f, indent=4)
                # run the code
                Runner.coderunner(path)
                await LLM.error_fixer_ModuleNotFound(path,model)
        # If the query is empty, return None 
        # If the json file contains the response, then it will run the 
        if os.path.exists(temp_loc):
            query = input("Filtered Prompt : ")
            q1= query+f"my project location is {path}. If you save anything save here. If loaction required, then :Use full location, if you want to store anything. If not required : No need to use"
            last_prompt = LLM.get_last_code(temp_loc, "prompt")
            last_code = LLM.get_last_code(temp_loc, "response")
            prompt_template = f"""  
            Only provide the code in python, no explanations, no headers, and do not use "``````" while generating the code.
            avoid explanation and don't use "``````" even if the context is large.
            avoid this "Here is the code with all comments removed:
                ```python"
                avoid this at the end of the code "```"
            """
            system = prompt_template
            human = "{text}"
            prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
            chain = prompt | chat
            #print(last_code)
            query = f"The last query is {last_prompt},the last code is {last_code}. Now you have to do : {query}"
            response = await chain.ainvoke({"text": query})  # Changed to ainvoke
            a = response.content
            # Write the response to the specified path
            Writer.writeCode(a, path)
            data = {
                "prompt": q1,
                "response": a
            }
            
            with open(temp_loc, 'w') as f:
                json.dump(data, f, indent=4)
                print(f"Code has been written to {path}")
            """python_file = os.path.join(path,"main.py")
            command = f"start cmd /k {path}/venv/Scripts/python.exe {python_file}"
            subprocess.Popen(command, shell=True)
            py_location = os.path.join(path,"venv/Scripts/python.exe")
            script_path = os.path.join(path, "main.py")
            file_path = os.path.join(path, "error.txt")
            with open(file_path, 'w') as f:
            subprocess.run([py_location, script_path], stderr=f)
            with open(file_path, 'r') as f:
                output = f.read()"""
            Runner.coderunner(path)
            #get error type
            #check the error
            await LLM.error_fixer_ModuleNotFound(path,model)
            await LLM.JinOllama(model, path)

