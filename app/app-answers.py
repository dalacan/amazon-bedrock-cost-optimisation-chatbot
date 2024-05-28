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

json_config_file = open('config-test.json')
configs = json.load(json_config_file)

# Create the large language model object
llm = Llm(configs)

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
        3. When thinking about what cost optimisation techniques to use, use the information from <policies> tag if applicable.
        4. Only apply the policy if it matches a relevant resources in the cost and usage report.
        5. When generating the recommendation, apply any policies that may influence the guidance generated. 
        6. Only use the data from the <AWS_cost_usage_report> and <policies> tags and think step by step in a <thinking> tag.
        7. Return the answer in an <answers> tag.
        8. Only return the <thinking> and <answers>.
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
