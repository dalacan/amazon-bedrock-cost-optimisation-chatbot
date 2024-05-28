import boto3
import json
import pandas as pd
import re

class Llm:
    

    def __init__(self, configs):
        # Create Bedrock client
        bedrock_client = boto3.client(
            'bedrock-runtime',
        )
        self.bedrock_client = bedrock_client
        
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')
        
        self.messages = []
        self.system_prompt = ''
        
        # Load CUR report
        # self.cur_report = pd.read_parquet('./sample/Dec2018-LabsCUR-00001.snappy.parquet')
        self.cur_report = pd.read_csv(configs["cur_report_filename"])
        self.max_records = configs["max_records"]
        
        self.modelId = configs["model_id"]
        
        self.knowledge_base_enabled = configs["knowledge_base_enabled"]
        self.knowledge_base_id=configs["knowledge_base_id"]
        
    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt
        
    def extract_between_tags(self, tag: str, string: str, strip: bool = False) -> list[str]:
        ext_list = re.findall(f"<{tag}>(.+?)</{tag}>", string, re.DOTALL)
        if strip:
            ext_list = [e.strip() for e in ext_list]
        return ext_list
        
    def get_policies(self, query):
        # Function that will look up policies from the knowledge base
        system_prompt = """
        Given the question in the <question> tag. Generate a search keywords that can be used to search for policies related to the question.

        Output the query in the <query> tag.
        """

        prompt_template = """
        <question>{$QUESTION}</question>
        """

        variables_dict = {
            "$QUESTION": query
        }

        prompt_with_variables = prompt_template
        for variable_name, variable_value in variables_dict.items():
            prompt_with_variables = prompt_with_variables.replace("{" + variable_name + "}", variable_value)

        query_messages = []
        query_messages.append(
            {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_with_variables,
                        }
                    ]
                }
        )

        body = {
            "system": system_prompt,
            "messages": query_messages,
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "temperature": 0,
            "top_k": 250,
            "top_p": 0.999,
            "stop_sequences": ["Human:"]
        }

        response = self.bedrock_client.invoke_model(
            body=json.dumps(body).encode(),
            accept="application/json",
            contentType="application/json",
            modelId=self.modelId
        )

        response_body = json.loads(response["body"].read())
        output = response_body['content'][0]['text']

        # Extract query
        generated_query = self.extract_between_tags('query', output)[0]

        # Perform knowledge base lookup 
        retriever_response = self.bedrock_agent_runtime.retrieve(
            knowledgeBaseId=self.knowledge_base_id,
            retrievalConfiguration={
                'vectorSearchConfiguration': {}
            },
            retrievalQuery={
                'text': generated_query
            }
        )

        return retriever_response['retrievalResults']

    def invoke(self, input_text, messages=[], initial=False):
        """
        Make a call to the foundation model through Bedrock
        """
        if initial:
            # Get policies
            if self.knowledge_base_enabled:
                print("Retrieving policies from knowledge base")
                policies_response = self.get_policies(input_text)
                policies = policies_response[0]['content']['text']
            else:
                policies = ""

            prompt_template = """
            <AWS_cost_usage_report>{$AWS_COST_USAGE_REPORT}</AWS_cost_usage_report>

            <question>{$QUESTION}</question>
            
            <policies>{$POLICIES}</policies>
            """
            
            variables_dict = {
                "$AWS_COST_USAGE_REPORT": self.cur_report.head(self.max_records).to_csv(),
                "$QUESTION": input_text,
                "$POLICIES": policies
            }

            prompt_with_variables = prompt_template
            for variable_name, variable_value in variables_dict.items():
                prompt_with_variables = prompt_with_variables.replace("{" + variable_name + "}", variable_value)

            input_message = {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_with_variables,
                            }
                        ]
                    }
            messages.append(input_message)
        else:
            # Follow up chat
            input_message = {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": input_text,
                            }
                        ]
                    }
            messages.append(input_message)

        # Prepare a Bedrock API call to invoke a foundation model
        body = {
            "system": self.system_prompt,
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "temperature": 0,
            "top_k": 250,
            "top_p": 0.999,
            "stop_sequences": ["Human:"]
        }

        response = self.bedrock_client.invoke_model(
            body=json.dumps(body).encode(),
            accept="application/json",
            contentType="application/json",
            modelId=self.modelId
        )

        response_body = json.loads(response["body"].read())
        output = response_body['content'][0]['text']
        
        output_message = {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": output,
                        }
                    ]
                }
        
        return input_message, output_message, output



