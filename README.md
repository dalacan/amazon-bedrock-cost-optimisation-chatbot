# AWS Cost Optimisation Chatbot Workshop

In this workshop, you will learn how to deploy, build and test a Generative AI chatbot with Amazon Bedrock through a streamlit app in Amazon SageMaker Studio. 
As a practical example, we will be iterating over a pre-built chatbot app to analyze a sample AWS cost and usage (CUR) sample report and generate some AWS cost optimisation recommendations.

## Workshop Content
The workshop will consist of 3 exercises:
1. Exercise 1: Write a prompt to analyze a cost and usage report and provide some cost optimisation recommendations.
2. Exercise 2: Extend the chatbot to utilise Amazon Befrock Knowledge Base to enhance the cost optimisation recommendations.
3. Exercise 3: Open book challenge - Improve the cost optimisation recommendation. Fine tune the prompts, chain prompts or add new data sources, let's see if you can improve the cost optimisation recommendations.

---

## Getting Started

### Step 1: Clone the repository
1. In Amazon SageMaker Studio, select `File` -> `New` -> `Terminal`
2. Clone the repository
```
git clone https://github.com/aws-samples/amazon-bedrock-workshop.git
```

### Step 2: Setup your environment
Once you've checked out the repository, you will need to setup your Amazon SageMaker studio environment to run the streamlit app.

1. Navigate to the app folder i.e. 
```
cd amazon-bedrock-cost-optimisation-chatbot/app
```
2. In the terminal, install the dependencies by running the following:

```
pip install --no-cache-dir -r requirements.txt
```
3. Install required packages by running the `setup.sh` script
```
sh setup.sh
```

### Step 3: Run your app
3. Verify that your app is correctly setup by running the following:

```
sh run.sh
```

The url and port number hosting the app will be displayed. Copy and paste the url in a new browser tab to preview your app.

![run.sh](./images/streamlit-demo-1.png)

### Step 4: Run your app in development mode
While developing, it might be helpful to automatically rerun the script when app.py is modified on disk. To do, so we can modify the runOnSave configuration option by adding the --server.runOnSave true flag to our command:

```
streamlit run app.py --server.runOnSave true
```
---
## Exercises

### Exercise 1: Write a system prompt that will analyze a cost and usage

In this exercise, you will be writing a prompt by updating the `system_prompt` variable in the `app.py` file to instruct the Generative AI model to analyze a cost and usage report provided in a `<AWS_cost_usage_report>` tag and answer a question in the `<question>` tag. You must also instruct the model to return the answer in an `<answers>` tags.

You can also optionally ask the model to provide it's thought process by saving it a `<thinking>` tag.

**Note** 

By default, the chat app is configured to use the Claude 3 Sonnet model. If you want to change this, update the value of `model_id` variable in the `config.json` file. This value refers to a model id in Amazon Bedrock.

**Tips**

For help on how to write a prompt for claude, refer to the following documentations:

- Claude Prompt Engineering: https://docs.anthropic.com/en/docs/prompt-engineering
- Use XML tags: https://docs.anthropic.com/en/docs/use-xml-tags

Once you have updated your prompt, refresh your strealit app and start asking it questions for cost optimisation recommendations.

---

### Exercise 2: Update your chat app to utilise an Amazon Bedrock knowledge base to enhance your cost optimisation recommendation
    
In this exercise, you will be:

1. Creating a knowledge base with Amazon Bedrock knowledge base
2. Setting up your streamlit app to utilise the knowledge base
3. Review how the app uses the knowledge base to retrieve information relevant to cost optimisation
4. Update your `system_prompt` variable to take the knowledge base into consideration
    
    
#### Step 1: Setup knowledge base
    
In the `amazon-bedrock-cost-optimisation-chatbot` folder, open the notebook `Create_knowledge_base.ipynb` and run through the steps to setup your knowledge base

#### Step 2: Setup your streamlit with the knowledge base feature

Open the `configs.json` and set the following

1. Set `knowledge_base_enabled` to true
2. Set your knowledge base id `knowledge_base_id` to the knowledge base you just created

#### Step 3: Update your system prompt to take the knowledge base information into consideration

In this section, you will be updating the `system_prompt` variable in the `app.py` file to take the information from the knowledge base into consideration. 

To get started, first review the `utils/llm.py` to `get_policies` function to understand how it is retrieving the information from the knowledge base. This information will be populated into the `<policies>` tag. Once you understand how this work, update the `system_prompt` variable to take the policies information into account.

Once you have updated your app, refresh your strealit app and start asking questions for cost optimisation recommendations to see if it uses the information from your knowledge base.

---

### Exercise 3: Improve the cost optimisation chatbot

Now that you have ran through the basics of implementing a streamlit app with a Amazon Bedrock and a knowledge base, see if you can enhance the chatbot to perform better cost optimisations. Some suggestions to get you started:

1. Enhance system prompt or chain multiple prompts to improve the recommendation
2. Improve how the application reads the cost and usage report (Hint: the current implementation is limited to the first 2000 records due to Claude's context limitation, see if you can improve this with function calling and csv queries - reference: https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/function_calling.ipynb)
3. Enhance the knowledge base with more information (i.e. upload more documents)
4. Implement tooling to query external data sources to improve context

### Clean up
Once we are done using the app, we want to free up the listening ports. To get all the processes running streamlit and free them up for use we can run our cleanup script: 
```
sh cleanup.sh
```

---

## References

 - Build Streamlit apps in Amazon SageMaker Studio: https://aws.amazon.com/blogs/machine-learning/build-streamlit-apps-in-amazon-sagemaker-studio/
 - Amazon Bedrock streamlit demo: https://github.com/aws/amazon-sagemaker-examples/tree/main/aws_sagemaker_studio/streamlit_demo
