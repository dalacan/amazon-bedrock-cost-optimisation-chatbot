import streamlit as st
import json
import boto3
from utils.llm import Llm
import re

def extract_between_tags(tag: str, string: str, strip: bool = False) -> list[str]:
    ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
    if strip:
        ext_list = [e.strip() for e in ext_list]
    return ext_list


# Add title on the page
st.title("Gen AI Cost Optimisation App")

json_config_file = open('config.json')
configs = json.load(json_config_file)

# Create the large language model object
llm = Llm(configs)

system_prompt = f'''
        Write your system prompt here
        '''

llm.set_system_prompt(system_prompt)

# Set initial context
if "inital_context_set" not in st.session_state:
    st.session_state.inital_context_set = True

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == 'user':
            # Check if can extract question
            text = extract_between_tags('question', message["content"][0]["text"])
            
            if len(text) > 0:
                st.markdown(text[0])
            else:
                st.markdown(message["content"][0]["text"])
        else:
            # Check if can extract answer
            text = extract_between_tags('answers', message["content"][0]["text"])

            if len(text) > 0:
                st.markdown(text[0])
                # Check if can extract thinking text
                thinking_text = extract_between_tags('thinking', message["content"][0]["text"])
                
                if len(thinking_text) > 0:
                    st.divider()
                    st.subheader("Reasoning")
                    st.markdown(thinking_text[0])
                
            else:
                st.markdown(message["content"][0]["text"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    input_message, output_message, output = llm.invoke(prompt, st.session_state.messages, st.session_state.inital_context_set)
    st.session_state.inital_context_set = False
    
    with st.chat_message("assistant"):
        # Check if can extract answer
        text = extract_between_tags('answers', output)

        if len(text) > 0:
            st.markdown(text[0])
            # Check if can extract thinking text
            thinking_text = extract_between_tags('thinking', output)

            if len(thinking_text) > 0:
                # Return the thinking text
                st.divider()
                st.subheader("Reasoning")
                st.markdown(thinking_text[0])

        else:
            st.markdown(output)
    st.session_state.messages.append(output_message)
