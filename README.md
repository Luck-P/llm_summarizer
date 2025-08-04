# llm file-summarizer agent using langchain #   
  
  
### llm provided by open router ###  

  1. openrouter/qwen/qwen3-coder:free  
  2. openrouter/deepseek/deepseek-r1-distill-llama-70b:free  
  3. openrouter/meta-llama/llama-3.2-3b-instruct:free  
  4. openrouter/nousresearch/deephermes-3-llama-3-8b-preview:free


## PROJECT LOGS ##  

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
      - either overseer Agent or mathsubcontr Tool issue >> #1 priority  

0.1.4 >  
  - upgraded prompt engineering in 'mathsubcontr' Tool > the llm now can determine whether it should use the tool or not  
  - replaced llm 3. with llm 4. : unforeseen 1-request-per-minute limit  
  - llm now can use its tool properly + satisfying answers for now  
  - issues :  
    - AgentType.CONVERSATIONAL\_REACT\_DESCRIPTION force reasonning-heavy output  
      - simple question crashes / triggers new prompt  
    - ball-implemented try except architecture in loop -> should be tested

0.1.5 >  
  - updated prompt for document summary  
  - 'try except' chunk tested > works / fallback message broken   
  - 'handle\_parsing\_errors = True' added for llm answer malfunction  
  - several clstdout() added for UI clarity/readability
  - issues :  
    - coding tool unstable -> tool calling random + prompt fumbling  
      - /!\ llm get entangled in tool conversation : blatant hallucination + unending prompting rather than answer retrieval  
      - prompt separation -> llm first prompt coding llm the question then prompt it code chunk 
