from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model='openai/gpt-oss-20b')

# define state
class ChatState(TypedDict):
    messages: Annotated[list[str], add_messages]

# make node function
def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}

# define graph, checkpointer, nodes and edges
graph = StateGraph(ChatState)
checkpointer = InMemorySaver()

graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# compile graph with checkpointer
chatbot = graph.compile(checkpointer=checkpointer)