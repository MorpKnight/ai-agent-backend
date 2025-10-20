from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

from app.tools import weather_tool, math_tool

load_dotenv()

app = FastAPI(
    title="AI Agent Backend",
    description="An API that routes natural language commands to the correct tool.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tools = [weather_tool, math_tool]

template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(template)

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


@app.post("/query")
async def process_query(request: QueryRequest):
    query = request.query
    
    response = agent_executor.invoke({"input": query})
    
    tool_used = "llm"
    if "Action:" in response.get("intermediate_steps", [("", "")])[0][0].log:
      action_log = response["intermediate_steps"][0][0].log
      action_tool = action_log.split("Action:")[1].split("\n")[0].strip()
      if action_tool in [t.name for t in tools]:
          tool_used = action_tool
            
    return {
        "query": query,
        "tool_used": tool_used,
        "result": response['output']
    }

@app.get("/")
def read_root():
    return {"status": "ok"}