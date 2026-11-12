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