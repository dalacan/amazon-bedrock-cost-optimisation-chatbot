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
st.title("Generative AI Application")

# Ask user for input text
# input_sent = 
# input_sent = st.text_input("Input Sentence", "Identify at least 3 areas where cost savings can be achieved and explain your reasoning. ")

# Create the large language model object
llm = Llm()

system_prompt = f'''
You will be analyzing an AWS (Amazon Web Services) cost and usage report to answer questions in the <question> tag.

An AWS cost and usage report is a detailed record of your AWS usage and associated costs. It
contains information such as the AWS service used, the resource type, the usage quantity, and the
cost incurred. This report can help you understand your AWS spending patterns and identify
opportunities to reduce costs.

Here are the steps you should follow:

1. Carefully review the provided AWS cost and usage report in the <AWS_cost_usage_report> tag in csv format. Familiarize yourself with
the data structure and the different fields present in the report.

2. For each row, carefully consider the properties for each resource. For example the usage type and whether the resource has a reserved instance plan.

3. Only use the data from the <AWS_cost_usage_report> and think step by step in a <thinking> tag to answer the question.

4. Return the answer in an <answers> tag.

5. Only return the <thinking> and <answers>.

<answers example>
<answers>
There were 3 EC2 instances that have reserved instances plan applied to it. This instances are XXX, YYY, ZZZ.
<answers>
</answers example>
'''
llm.set_system_prompt(system_prompt)

# Set initial context
if "inital_context_set" not in st.session_state:
    st.session_state.inital_context_set = True

# # When there is an input text to process
# if input_sent:
#     # Invoke the Bedrock foundation model
#     output = llm.invoke(input_sent, inital_context_set)
    
#     print(f"Output: {output}")

#     # Write response on Streamlit web interface
#     st.write(output)
    
#     inital_context_set = True
    

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
            st.markdown(message["content"][0]["text"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    print(f'message len before: {len(st.session_state.messages)}')

    input_message, output_message, output = llm.invoke(prompt, st.session_state.messages, st.session_state.inital_context_set)
    # Add user message to chat history
    print("Set input message")
    print(f'Message len before append input: {len(st.session_state.messages)}')
    print(st.session_state.messages)
    # st.session_state.messages.append(input_message)
    print(f'Message len after input: {len(st.session_state.messages)}')
    # print(f'output: {output}')
    st.session_state.inital_context_set = False
    print("Session state")
    # print(st.session_state)
    
    with st.chat_message("assistant"):
        st.write(output)
    print("Set output message")
    st.session_state.messages.append(output_message)
    
    print(f'Message len after output: {len(st.session_state.messages)}')