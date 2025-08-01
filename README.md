llm file-summarizer agent using langchain

llm provided by open router  
  1. openrouter/qwen/qwen3-coder:free  

0.1.1 >  
  - no agent / no tool
    - parse document into str using unstructured package partition()  
    - add parsed str to first prompt  
    - basic llm request using langchain llm.invoke()  
  - follow up questions  
    - whole conversation stored in list  
    - list passed as input
0.1.2 >  
  - 2-llm solution  
    - llama3.2 for wide context / text computing  
    - deepseek R1 for maths capacity  
  - issues :  
    - incremental %history% quickly saturate llm context capacity  
0.1.3 >  
  - modified 2-llm architecture : now overseer llm + math/code dedicated llm  
  - implemented agent framework for follow-up questions  
    - deepseek math crack now called as tool by text-managing llama3.2
  - issues :  
    - invoking raw llm (not agent yet) for document summarization -> cheap result  
      - agent-ify the process with additionnal tools if necessary   
    - Agent won't use its tool : might be prompt engineering issue  
    - /!\ Agent loop itself up when suggested to call tool : major issue  
      - either overseer Agent or mathsubcontr Tool issue  

