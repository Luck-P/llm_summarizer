llm file-summarizer agent using langchain

llm provided by open router  
  1. openrouter/qwen/qwen3-coder:free  

0.1.x >  
  - no agent / no tool
    - parse document into str using unstructured package partition()  
    - add parsed str to first prompt  
    - basic llm request using langchain llm.invoke()  
  - follow up questions  
    - whole conversation stored in list  
    - list passed as input
