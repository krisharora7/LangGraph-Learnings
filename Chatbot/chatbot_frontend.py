import streamlit as st
from langchain_core.messages import HumanMessage
from chatbot_backend import chatbot

CONFIG = {'configurable': {'thread_id':'thread-1'}}

#  A Session State is a dictionary-like container provided by Streamlit that persists data across multiple interactions of the same user session.
# we are not using normal message_history list as it will be erased whenever we do an action like pressing enter.

# create message_history if not initialized
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

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
    response = chatbot.invoke({'messages': HumanMessage(content=user_input)}, config=CONFIG)
    ai_message = response['messages'][-1].content
    st.session_state['message_history'].append({'role':'ai', 'content':ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)
