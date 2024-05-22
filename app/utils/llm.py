import boto3
import json
import pandas as pd

class Llm:
    

    def __init__(self):
        # Create Bedrock client
        bedrock_client = boto3.client(
            'bedrock-runtime',
            # If Bedrock is not activated in us-east-1 in your account, set this value
            # accordingly
            # region_name='us-east-1',
        )
        self.bedrock_client = bedrock_client
        
        self.messages = []
        self.system_prompt = ''
        
        # Load CUR report
        self.cur_report = pd.read_parquet('./sample/Dec2018-LabsCUR-00001.snappy.parquet')
        self.modelId = 'anthropic.claude-3-haiku-20240307-v1:0'
        
    def set_system_prompt(self, system_prompt):
        self.system_prompt = system_prompt

    def invoke(self, input_text, messages=[], initial=False):
        """
        Make a call to the foundation model through Bedrock
        """
        if initial:
            print('initial...')
            prompt_template = """
            <AWS_cost_usage_report>{$AWS_COST_USAGE_REPORT}</AWS_cost_usage_report>

            <question>{$QUESTION}</question>
            """
            
            # Only loading the first 100 records
            variables_dict = {
                "$AWS_COST_USAGE_REPORT": self.cur_report.head(200).to_csv(),
                "$QUESTION": input_text
            }

            prompt_with_variables = prompt_template
            for variable_name, variable_value in variables_dict.items():
                print(f"variable name {variable_name}")
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
            print('follow up')
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
        # print(f'body: {body}')
        print(len(messages))
        for message in messages:
            print(message['role'])

        response = self.bedrock_client.invoke_model(
            body=json.dumps(body).encode(),
            accept="application/json",
            contentType="application/json",
            modelId=self.modelId
        )

        response_body = json.loads(response["body"].read())
        output = response_body['content'][0]['text']
        
        # Append assistant message
        # self.messages.append(
        #     {
        #             "role": "assistant",
        #             "content": [
        #                 {
        #                     "type": "text",
        #                     "text": output,
        #                 }
        #             ]
        #         }
        # )
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



