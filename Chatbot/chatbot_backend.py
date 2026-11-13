from langgraph.graph import StateGraph, START, END, add_messages
# from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGroq(model='openai/gpt-oss-20b')

# define state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# make node function
def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']
    response = llm.invoke(messages)
    return {'messages': [response]}

# define graph, checkpointer, nodes and edges
graph = StateGraph(ChatState)
#checkpointer = InMemorySaver()

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False) #Setting check_same_thread=False allows a SQLite connection created in one thread to be accessed by other threads. By default, Python's sqlite3 library sets check_same_thread=True and throws a ProgrammingError if a different thread tries to use that connection. and we want to use multiple threads for multiple conversations
checkpointer = SqliteSaver(conn=conn)

graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# compile graph with checkpointer
chatbot = graph.compile(checkpointer=checkpointer)


# response = chatbot.invoke({'messages':'what is my name'}, config={'configurable':{'thread_id':'2'}})
# print(chatbot.get_state(config={'configurable':{'thread_id':'1'}}))
# print(response)


# we need all existing threads because when we were using ram to store we were clearing chat_threads in frontend as we were intializing it with empty thread but now we will extract all threads from database, checkpointer.list() gives all checkpoints. if we want all checkpoints of a particular thread we can give that thread inside it otherwise if we want all we can write "None". it returns a generator

def retrieve_all_threads():
    all_threads = set() # made a set to store unique thread ids
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)