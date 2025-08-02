from dotenv import load_dotenv
import os 


#langchain libraries

from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType 
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

#tools
from langchain.tools.tavily_search import TavilySearchResults
from unstructured.partition.auto import partition


load_dotenv()

#print(f"checkup : \nOPENAI_API_KEY : {os.environ["OPENAI_API_KEY"]}\nTAVILY_API_KEY : {os.environ["TAVILY_API_KEY"]}");input("...type...")

###     MODELS      ###
'''
openrouter.ai : many models available with own pros n cons

    document summarization  > high throughput - latency less relevant - large context - tuned for better document processing

    follow-up questions     > low latency - throughput / context less relevant - engineering studies : good-at-maths model 

'''

qwen1 = ChatOpenAI(
    openai_api_base= "https://openrouter.ai/api/v1",
    model_name = "qwen/qwen3-coder:free"
)#said to be fine-tuned for coding 

llama32 = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="meta-llama/llama-3.2-3b-instruct:free"
) #low latency (0.5s) - high throughput (223.5 t/s) - large context (131,000 tk) - good at advanced natural language processing  

dpskllama = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="deepseek/deepseek-r1-distill-llama-70b:free"
) #low latency (0.85) - decent throughput (52 t/s) - small context (8,192 tk) - (very) good at maths  

dphermes = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    model_name="nousresearch/deephermes-3-llama-3-8b-preview:free"
) #low latency (1.0s) - high throughput (286 t/s) - large context (131,000 tk) - long chains of thought + function calling capabilities  

###     TOOLS       ###
'''
onlinesearch = TavilySearchResults() #unaligned / unmanaged

ctrlbrowse= Tool.from_function(
    name = "online searching tool",
    description =("" \
    "use this tool when an information "
    )
)

work in progress > wrapper tool that completes TavilySearchResult() with proper name/description + implements user approval check 

'''
def docsummar(path):
    return '\n'.join(str(el) for el in partition(filename = path))[:4000]
    
'''dosum = Tool(
    name="document summarizer",
    func = docsummar,
    description = "retrieve the document's text - function input should be a full file path provided by the user"
)
        useless for now : document is passed raw to the llm 
'''

def mathexp(prompt: str) -> str: 
    return dpskllama.invoke(prompt).content


mathsubcontr = Tool(
    name="task-sub_contractor",
    func=mathexp,
    description=(
        "this tool invoke a math and code dedicated llm"
        "if you encounter any maths or code related question : you **do** use the tool"
        "INPUT: a **raw python string** describing the task"
        "IMPORTANT: to use the tool follow these steps"
        "- identify the core problem. You must sort useful elements from the useless ones"
        "- write **yourself** a concise prompt that phrases the problem you identified. You have to use minimal instructions, variable names and clear equations **only**"
        "- once the prompt fully written, you must pass the prompt you wrote as the **only input**"
    )
)
    

###     AGENTS      ### 

overseer = initialize_agent(
    llm = dphermes,
    agent = AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    tools=[mathsubcontr],
    verbose=True
)

###     LOW FUNCTIONS       ###

def getpath():
    path = input("give file's path (windows format): ")
    if os.path.isfile(path):
        return path
    else : 
        print("incorrect input")
        return getpath() 
        
def clstdout():
    os.system('cls' if os.name=='nt' else 'clear')

if __name__=="__main__":
    print("document summeriser")
    path = getpath()
    print(path)
    print(docsummar(path))
    history=[SystemMessage(content=f"summarize the following document. Your output should consist in : a quick overview (type, theme) - a light resume breaking the main points down - a short conclusion ||| document : {docsummar(path)}")]
    res = llama32.invoke(history)
    #history.append(res) -> useless, the whole document is already in memory : cheap duplication 
    clstdout()
    print(res.content)
    fwup = input("\n'q' to quit > ")
    while(fwup!='q'):
        try :
            res = overseer.run(input=fwup,chat_history=history)
        except:
            print(f"\nagent / langchain failure :\n{Exception}")
        else:
            history.append(HumanMessage(content=fwup))
            history.append(AIMessage(res))
            print(f'\n{res}')
        fwup = input("\n'q' to quit > ")
    print("over")
    clstdout()
    


