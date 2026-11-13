import streamlit as st
from langchain_core.messages import HumanMessage
from chatbot_backend import chatbot
import uuid

# ********************************************************* Utility functions *********************************************************
def generate_thread_id():
    thread_id = uuid.uuid4()
    return str(thread_id)

def reset_chat():
    thread_id = generate_thread_id()  # generate new thread
    st.session_state['thread_id'] = thread_id # add it in session
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = [] # clear up current history

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable':{'thread_id': thread_id}}).values['messages']
# ********************************************************* Session setup *********************************************************

#  A Session State is a dictionary-like container provided by Streamlit that persists data across multiple interactions of the same user session.
# we are not using normal message_history list as it will be erased whenever we do an action like pressing enter.

# create message_history if not initialized
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# generate thread_id if not generated and store in session state
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# create a list of threads to print different converstaions in sidebar
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])


# ********************************************************* Sidebar UI *********************************************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

# display all thread id in sidebar
for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(thread):
        st.session_state['thread_id'] = thread
        messages = load_conversation(thread)
        temp_message = []
        for msg in messages:
            if(isinstance(msg, HumanMessage)):
                role='user'
            else:
                role='ai'
            temp_message.append({'role':role, 'content': msg.content})

        st.session_state['message_history'] = temp_message

# ********************************************************* Main UI *********************************************************

# loading conversation history if message_history is initialized
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

# message history will be a list of dictionaries where each dictionary will look like - > {'role': 'user/assistant', content = '...'}

user_input = st.chat_input("Enter Message")
if user_input:
    # add user message to message_history
    st.session_state['message_history'].append({'role':'user', 'content':user_input})
    # display user message
    with st.chat_message('user'):
        st.text(user_input)

    # get ai responses -> 
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            # it's okay if we didn't write message_chunk.content and just write message_content because st.write_stream() accepts generators that yield strings or supported objects such as LangChain message chunks. It knows how to handle LangChain message chunks and extract/display their text content. 
            message_chunk for message_chunk, metadata in chatbot.stream(
                {'messages': HumanMessage(content=user_input)},
                config=CONFIG,
                stream_mode='messages'
            )
        )
    st.session_state['message_history'].append({'role':'ai', 'content':ai_message})