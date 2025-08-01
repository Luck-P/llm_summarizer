from dotenv import load_dotenv
import os 
import subprocess

#langchain libraries

from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType 
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

#tools
from langchain.tools.tavily_search import TavilySearchResults
from unstructured.partition.auto import partition


load_dotenv()

print(f"checkup : \nOPENAI_API_KEY : {os.environ["OPENAI_API_KEY"]}\nTAVILY_API_KEY : {os.environ["TAVILY_API_KEY"]}");input("...type...")

querytl = TavilySearchResults()

filetl = 1

qwen1 = ChatOpenAI(
    openai_api_base= "https://openrouter.ai/api/v1",
    model_name = "qwen/qwen3-coder:free"
)

def docsummar(path):
    return '\n'.join(str(el) for el in partition(filename = path))[:4000]
    
'''dosum = Tool(
    name="document summarizer",
    func = docsummar,
    description = "retrieve the document's text - input should be the full file path provided by the user"
)

synt = initialize_agent(
    llm = qwen1,
    agent = AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    tools=[dosum]
)'''

def getpath():
    path = input("give file's path (windows format): ")
    if os.path.isfile(path):
        return path
    else : 
        print("incorrect input")
        return getpath() 
        

if __name__=="__main__":
    print("document summeriser")
    path = getpath()
    print(path)
    history=[SystemMessage(content=f"summarize the following document. Your output should consist in : a quick overview (type, theme) - a light resume breaking the main points down - a short conclusion ||| document : {docsummar(path)}")]
    res = qwen1.invoke(history)
    history.append(res)
    print(res.content)
    fwup = input("'q' to quit > ")
    while(fwup!='q'):
        history.append(HumanMessage(content=fwup))
        res = qwen1.invoke(history);history.append(res);print(res.content)
        fwup = input("'q' to quit > ")
    print("over")
    


