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
#from langdetect import detect -> no use for variable format files 


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

moon = ChatOpenAI(
    openai_api_base = "https://openrouter.ai/api/v1",
    model_name="moonshotai/kimi-vl-a3b-thinking:free"
) # latency 4.5s - throughput 50 t/s - context 131,000 tk - good at long context task / multimodal reasonning

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
    return '\n'.join(str(el) for el in partition(filename = path))
    
'''dosum = Tool(
    name="document summarizer",
    func = docsummar,
    description = "retrieve the document's text - function input should be a full file path provided by the user"
)
        useless for now : document is passed raw to the llm 
'''

def mathexp(prompt: str) -> str: 
    return dpskllama.invoke(prompt).content

def codeexp(prompt:str) -> str:
    return qwen1.invoke(prompt).content

mathsubcontr = Tool(
    name="math-task-sub_contractor",
    func=mathexp,
    description=(
        "this tool invoke a math dedicated llm"
        "if you encounter any maths related question : you **do** use the tool"
        "INPUT: a **raw python string** describing the task"
        "IMPORTANT: to use the tool follow these steps"
        "- identify the core problem. You must sort useful elements from the useless ones"
        "- write **yourself** a concise prompt that phrases the problem you identified."
        "- You have to use minimal instructions, variable names and clear equations **only**"
        "- once the prompt fully written, you must pass the prompt you wrote as the **only input**"
        "finally, once you receive the tool's answer, proceed with the final response"
    )
)
    
codesubcontr = Tool(
    name = "coding-task-sub_contractor",
    func=codeexp,
    description=(
        "this tool invoke a code dedicated llm"
        "always use this tool for any code related question"
        "INPUT: a **raw string** containing the related code and the user's question"
        "IMPORTANT: to use the tool, you must follow these steps"
        "- identify the user's problem."
        "- retrieve the relevant section of code from the document previously given"
        "- write **yourself** a prompt that contain : "
        "  1. the user's question"
        "  2. the relevant code section"
        "once the prompt fully written, you must pass the prompt you wrote as the **only input**"
        "finally, once you receive the tool's answer, proceed with the final response"
    )
)

###     AGENTS      ### 

overseer = initialize_agent(
    llm = dphermes,
    agent = AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    handle_parsing_errors = True,
    tools=[mathsubcontr,codesubcontr],
    verbose=True
)

ovsfallback = initialize_agent(
    llm = moon,
    agent = AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    handle_parsing_errors = True,
    tools = [mathsubcontr,codesubcontr],
    verbose = True
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
    avlagents = [overseer,ovsfallback];cra = 0
    clstdout()
    print("document summeriser")
    path = getpath()
    history=[SystemMessage(
        content=(
            "summarize the following document."
            "Your output must be build as the following : "
            "   - write a quick overview of what is the document about"
            "   - identify and breakdown the **main themes** of the document" 
            f"here is the document : \n{docsummar(path)}"
        ))]
    res = llama32.invoke(history)
    #history.append(res) -> useless, the whole document is already in memory : cheap duplication 
    clstdout()
    print(res.content)
    fwup = input("\n'q' to quit > ")
    while(fwup!='q'):
        try :
            res = avlagents[cra].run(input=fwup,chat_history=history)
        except Exception as e:
            print(f"\nagent {cra + 1} failed :\n{e}")
            if input("switch to next model ? y/n : ")=='y':
                cra+=1
        else:
            history.append(HumanMessage(content=fwup))
            history.append(AIMessage(content=res))
            print(f'\n{res}')
        fwup = input("\n'q' to quit > ")
    print("over")
    clstdout()
    


