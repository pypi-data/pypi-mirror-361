# Kobai SDK for Python (Alpha)

Alpha: This SDK is not currently supported for production use while we stabilize the interface.

The Kobai SDK for Python includes functionality to accelerate development with Python on the Kobai Semantic Layer. It does not cover all Kobai Studio features, but rather focuses on integrating a Kobai tenant with data science and AI activities on the backend.

## Getting Started

This exercise demonstrates using the Kobai SDK to create a Databricks "Genie" Data Room environment, enabling users to interact with Kobai data in an AI Chat interface.

1. Please install Kobai SDK for Python via `pip install kobai-sdk`, gather some configuration details of the Kobai instance and tenant to connect to, and instantiate `TenantClient`:

```python
from kobai import tenant_client, spark_client, databricks_client

schema = 'main.demo'
uri = 'https://demo.kobai.io'
tenant_id = '1'
tenant_name = 'My Demo Tenant'

k = tenant_client.TenantClient(tenant_name, tenant_id, uri, schema)
```

2. Authenticate with the Kobai instance:

```python
client_id = 'your_Entra_app_id_here'
tenant_id = 'your_Entra_directory_id_here'

k.authenticate(client_id, tenant_id)
```

3. Initialize a Spark client using your current `SparkSession`, and generate semantically-rich SQL views describing this Kobai tenant:

```python
k.spark_init_session(spark)
k.spark_generate_genie_views()
```

4. Initialize a Databricks API client using your Notebook context, and create a Genie Data Rooms environment for this Kobai tenant.

```python
notebook_context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
sql_warehouse = '8834d98a8agffa76'

k.databricks_init_notebook(notebook_context, sql_warehouse)
k.databricks_build_genie()
```

## AI Functionality
The Kobai SDK enables users to ask follow-up questions based on the results of previous queries. This functionality currently supports models hosted on Databricks and Azure OpenAI. 

#### Prerequisites
Before asking a follow-up question, ensure that you have instantiated the TenantClient and completed the authentication process.

#### Steps to Ask a Follow-Up Question

1. List Questions: Retrieve the questionId or questionName. You can list all questions or filter by domain.

```python
k.list_questions() # List all questions
k.list_domains() # To get the domain labels
k.list_questions(domain_label="LegoCollecting") # List questions by domain
```

2. Ask a Question: Use either the questionId or questionName to submit your query.

```python
question_json = k.run_question_remote(2927) # By questionId
kobai_query_name = "Set ownership"
question_json = k.run_question_remote(k.get_question_id(kobai_query_name)) # By questionName
```

3. Ask a Follow-Up Question: Based on the initial results, you can ask a follow-up question using either Azure OpenAI, Databricks or a user-provided chat model.

#### Using Azure OpenAI

###### Authentication Methods:

1. ApiKey

```python
from kobai import ai_query, llm_config
import json

followup_question = "Which owner owns the most sets?"

llm_config = llm_config.LLMConfig(endpoint="https://kobaipoc.openai.azure.com/", api_key="YOUR_API_KEY", deployment="gpt-4o-mini", llm_provider="azure_openai")

output = ai_query.followup_question(followup_question, json.dumps(question_json), kobai_query_name, llm_config=llm_config)
print(output)
```

2. Azure Active Directory Authentication

Ensure that the logged-in tenant has access to Azure OpenAI.
In case of databricks notebook, the logged in service principal should have access to Azure OpenAI.

```python
from kobai import ai_query, llm_config
import json

followup_question = "Which owner owns the most sets?"

llm_config = llm_config.LLMConfig(endpoint="https://kobaipoc.openai.azure.com/", deployment="gpt-4o-mini", llm_provider="azure_openai")
llm_config.get_azure_ad_token()

output = ai_query.followup_question(followup_question, json.dumps(question_json), kobai_query_name, llm_config=llm_config)
print(output)
```

#### Using Databricks (Default Configuration)

```python
from kobai import ai_query, llm_config
import json

followup_question = "Which owner owns the most sets?"

llm_config = llm_config.LLMConfig()

output = ai_query.followup_question(followup_question, json.dumps(question_json), kobai_query_name, llm_config=llm_config)
print(output)
```

#### User Provided Chat Model

```python
from kobai import ai_query, llm_config
import json
from langchain_openai import AzureChatOpenAI

followup_question = "Which owner owns the most sets?"

llm_config = llm_config.LLMConfig(debug=True)

chat_model = AzureChatOpenAI(
azure_endpoint="https://kobaipoc.openai.azure.com/", azure_deployment="gpt-4o-mini",
api_key = "YOUR_API_KEY",
openai_api_version="2024-02-15-preview",
temperature=0.5, 
max_tokens=150,)

output = ai_query.followup_question(followup_question, json.dumps(question_json), kobai_query_name, override_model=chat_model, llm_config=llm_config)
print(output)
```

## Limitations

This version of the SDK is limited to use in certain contexts, as described below:

- Authentication is limited to MS Entra AD.
- Functionality limited to Databricks Notebook environments at this time.
