import base64
from fastapi import FastAPI, HTTPException
import requests
import json
import openai
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict

load_dotenv(".env")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY

app = FastAPI()

def list_files(repo_url: str, path="src"):
    """
    List all files in a GitHub repository at a specified path.
    Recursively explores subdirectories.
    """
    parts = repo_url.strip("/").split("/")
    owner, repo = parts[-2], parts[-1]

    files = []
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            if item['type'] == 'file':
                files.append([item['git_url'], item['path']]) 
            elif item['type'] == 'dir':
                files.extend(list_files(repo_url, item['path']))
    else:
        print(f"Failed to list contents for {path}")
    return files

def generate_content(repo_url):
    files = list_files(repo_url)

    content = ""

    for file in files:
        response = requests.get(file[0])
        if response.status_code == 200:
            file_data = response.json()
            file_content = base64.b64decode(file_data['content']).decode('utf-8')
            content = content + f"Path of file: {file[1]}" + "\n" + file_content + "\n"
    
    return content

@app.post("/generate-diff/")
def generate_diff(payload: Dict[str, str]): 
    query = payload.get("prompt")
    repo_url = payload.get("repoUrl")

    if not repo_url or not query:
        raise HTTPException(status_code=400, detail="Both repoUrl and prompt are required")

    llm = OpenAI()
    content = generate_content(repo_url)

    prompt_template = PromptTemplate(
        input_variables=["query", "content"],
        template="""
        Your job is to take in a user prompt and return a diff string representing the changes to be made to the code.
        
        Generate a diff for the following query: {query}
        By accessing the following code which has the path of each file in the src folder with its code below it: 
        {content}
        
        """,
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(query=query, content=content)

    reflection_template = PromptTemplate(
        input_variables=["query", "content", "response"],
        template="""
        This is the diff that you generated for the query {query}: {response}

        The code below has the path of each file in the src folder with its code below it:
        {content}

        Are you sure that this is what the diff should be? If yes, just return the same diff. Otherwise, make the necessary changes.
        """
    )
    reflection_chain = LLMChain(llm=llm, prompt=reflection_template)
    reflection_response = reflection_chain.run(query=query, content=content, response=response)

    return {"original_diff": response, "reflection_diff": reflection_response}



if __name__ == "__main__":
    #print(generate_diff("Also it might be great if the script detects which OS or shell I'm using and try to use the appropriate command e.g. dir instead of ls because I don't want to be adding windows after every prompt.", "https://github.com/jayhack/llm.sh"))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
