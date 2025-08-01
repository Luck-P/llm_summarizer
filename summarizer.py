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

def mathexp(prompt) -> str: 
    return dpskllama.invoke(prompt).content


mathsubcontr = Tool(
    name="task sub contractor",
    func=mathexp,
    description=(
        "use this tool when encountering either complex math problem or code handling"
        "it will call an llm subcontractor specialized in advanced maths and coding - consider it better for these tasks" 
        "Narrow context capacity : 8000 / eight thousands words"
        "keep the passed prompt barebone : explicit variable names, equations, minimal instructions"
        "mathexp function expect a plain text input - redact the prompt as asked then pass it raw to the function"
    )
)
    

###     AGENTS      ### 

overseer = initialize_agent(
    llm = llama32,
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
        res = overseer.run(input=fwup,chat_history=history)
        history.append(HumanMessage(content=fwup))
        history.append(AIMessage(res))
        print(f'\n{res}')
        fwup = input("\n'q' to quit > ")
    print("over")
    clstdout()
    


