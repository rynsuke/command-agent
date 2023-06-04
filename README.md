# command-agent

🤖 An agent capable of memorizing reusable procedure as "command", built on [langchain](https://github.com/hwchase17/langchain).

## Introduction

This is an automonous agent based on [the Agent implementation of langchain](https://python.langchain.com/en/latest/modules/agents.html), but with the ability of memorizing reusable procedures as "commands".

<div align="center">
    <img src="https://github.com/rynsuke/command-agent/assets/3126563/8cd2314c-cf75-4b61-ba4d-6e2b2173f9a0" width="750">
</div>

**How it works**

- Separated components of PlanningAgent and CommandExecutor. This is inspired by the architecture of [BabyAGI](https://github.com/yoheinakajima/babyagi), but more micro one on the task level.

- The inputs and outputs of tasks / commands are all parametrized as variables, which is a core concept for reusablity.

- PlanningAgent fetches commands relevant to the given task, querying to CommandRegistry where commands are stored.

- PlanningAgent decides which command and input variables to use as the next step, based on the task and the step history so far.

- CommandExecutor takes the command and input variables selected by PlanningAgent, and generates a desirable input for the command to execute.

- The output of the command is saved as a variable, and can be used in the following steps.

- The final output is generated by ReturnCommand with the relevant variables.

- A command corresponding to the given task is generated from the executed steps, and stored in CommandRegistry in a reusable way.

- Channel is used for Agent to communicate with the user, when requesting input check or additional prompts.

**Benefits**

- Planning steps can be skipped for the similar tasks, which improves execution stability drastically, as well as reducing token consumption.

- Store commands can be utilized as a building block for more complex commands.

- Commands can be handled in a more structured way compared to langchain tools, whereas keeping the compatibility (i.e. langchain tools can still be used as commands with a single string input / output).

## Demo

> **Warning**
> This demo consumes related API, which may result in some charges for API usage. The repository owner is not responsible for any charges or problems associated with this demo.

### 1. Requirements

This demo requires the access to the following APIs:

- OpenAI API (works with GPT-3.5)
- NOTION API
- PINECONE API

Make sure to set the relevant environment variables in `.env`, copying from `.env.sample`.

In addition, you will need:

- A Notion database for the demo (default name: `Test`). For example, you can use an empty database with "Title" (title) and "Keywords" (multiselect) columns. Note that you can use any shape of database, but its structure should be something easy to understand for the agent (LLM).

- An integration set up for the agent. Please refer to the [Notion official document](https://developers.notion.com/docs/create-a-notion-integration).

- Pinecone Index with 1536 dimensions to store command entries (default name: `commmands`).

### 2. Run the agent

(main.py)

```python
import asyncio
from dotenv import load_dotenv
from samples.run_agent import run_agent

if __name__ == "__main__":
    # make sure to set the environment variables in .env
    load_dotenv(verbose=True)
    asyncio.run(run_agent())
```

<details>
<summary>Execution logs</summary>

First planning prompt:

```
Perform the following task as best as you can. You have access to the following commands and variables:

[Commands]
InsertNotionDatabasePageCommand
- Description: Insert a new page to a Notion database
- Input: { "page_data": { "content": <content of the page (str)>, "properties": [ { "name": <name of the property (str)>, "type": <type of the property, should be one of [rich_text,multi_select,url,title,created_time,created_by]>, "value": <value of the property (str)> } ]) }, "database_schema": { "id": <id of the database (str)>, "title": <title of the database (str)>, "properties": [ { "name": <name of the property (str)>, "type": <type of the property, should be one of [rich_text,multi_select,url,title,created_time,created_by]> } ]) } }
- Output: { "url": <url of the created page (str)> }

SearchNotionDatabasesCommand
- Description: Search Notion databases and return the database schema
- Input: { "database_name": <name of the database to search (str)> }
- Output: { "id": <id of the database (str)>, "title": <title of the database (str)>, "properties": [ { "name": <name of the property (str)>, "type": <type of the property, should be one of [rich_text,multi_select,url,title,created_time,created_by]> } ]) }

ReturnCommand
- Description: Finish the whole process. Use this command when you get the desired output.
- Input: { "page_url": <the URL of the created page (str)> }
- Output: { "page_url": <the URL of the created page (str)> }

[Variables]
text: the given text
database_name: the given Notion database

Use the following format:

Task: the given task you must perform
Thought: you should always think about what to do
Command: the command to execute, should be one of [InsertNotionDatabasePageCommand,SearchNotionDatabasesCommand,ReturnCommand]
Input variables: the variables you can use in the command, should be a subset of ["text","database_name"]. For example, ["text","database_name"].
Observation: the result of the command
... (this Thought/Command/Input variables/Observation can repeat N times)
Thought: I now know the final answer
Command: ReturnCommand
Input variables: [<variables to use>]

Task: Save [the given text](text) into [the given Notion database](database_name). Output [the URL of the created page](page_url).
Thought:
```

First step:

```
> Finished chain.
AgentAction(thought='I need to search for the Notion database and get its schema, then insert a new page with the given text and properties.', command='SearchNotionDatabasesCommand', input_variables=['database_name'])
Command was successful, saving the result to steps.0.output variable
```

Second planning prompt:

```
> Entering new LLMChain chain...
> Prompt after formatting:
> ...

Task: Save [the given text](text) into [the given Notion database](database_name). Output [the URL of the created page](page_url).Thought: I need to search for the Notion database and get its schema, then insert a new page with the given text and properties.
Command: SearchNotionDatabasesCommand
Input variables: ['database_name']
Observation: Command was successful, saving the result to steps.0.output variable
Thought:
```

Second step:

```

> Finished chain.
> AgentAction(thought='I now need to insert a new page to the Notion database with the given text and properties.', command='InsertNotionDatabasePageCommand', input_variables=['steps.0.output', 'text'])

Enter "OK" if the input looks good, otherwise put the reason for rejection or details on how to fix the input:
Command: InsertNotionDatabasePageCommand
Inputs:
{'page_data': {'content': 'An introduction to Large Language Model...', 'properties': [{'name': 'Keywords', 'type': 'multi_select', 'value': 'Large Language Model, GPT, Generative Pretrained Transformer, Machine Learning, Neural Network, Transformer, Text Generation, Prediction'}, {'name': 'Title', 'type': 'title', 'value': 'An Introduction to Large Language Model'}]}, 'database_schema': {'id': '8b5755bb-5423-4a79-a840-27c9f45fc6f5', 'title': 'Test', 'properties': [{'name': 'Keywords', 'type': 'multi_select'}, {'name': 'Title', 'type': 'title'}]}}
```

Please check the input to `InsertNotionDatabasePageCommand` and enter OK if it looks good. Otherwise, Please input the feedback to the agent, then the agent will make another request with modified input.

Third planning prompt:

```
> Entering new LLMChain chain...
> Prompt after formatting:
> ...

> Finished chain.
AgentAction(thought='I now know the final answer', command='ReturnCommand', input_variables=['steps.1.output'])
Command was successful, saving the result to steps.2.output variable
{'page_url': 'https://www.notion.so/An-Introduction-to-Large-Language-Model-fd5755c454754ed1bcd6aa6ce819f733'}
```

</details>

This will create the Notion page into the designated database. You can jump into the content from the link generated by the agent (`page_url`).

After the execution, you are asked if you want to save the command. Please enter "YES" and the command name (`SaveTextToNotionDatbaseAndReturnPageURL`), then the command is saved to the designated Pinecone Index.

### 3. Execute the command directly

Then, you can execute the saved command directly from the code.

(main.py)

```python
import asyncio
from dotenv import load_dotenv
from samples.execute_command import execute_command

if __name__ == "__main__":
    # make sure to set the environment variables in .env
    load_dotenv(verbose=True)
    asyncio.run(execute_command())
```

(samples/execute_command.py)

```python
async def execute_command():
    # Set up LLM
    command_llm = OpenAI(temperature=0, max_tokens=1500)

    # Set up Pinecone
    pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENVIRONMENT"])
    index = pinecone.Index(os.environ["PINECONE_COMMANDS_INDEX_NAME"])

    emb = OpenAIEmbeddings()
    storage = PineconeDB(index, emb)

    # Set up CommandRegistry & Channel
    command_registry = CommandRegistry(notion_commands(token=os.environ["NOTION_TOKEN"]), storage, command_llm)
    channel = ChannelConsole()

    # Look up the saved command and execute
    command = command_registry.resolve(COMMAND_NAME)
    if command is None:
        raise Exception(f"Command {COMMAND_NAME} not found")

    print(
        await command.run(
            {
                "text": TEXT,
                "database_name": os.environ["NOTION_DATABASE_NAME"],
            },
            channel,
        )
    )
```

This will execute the above task with a different input, without planning process. This functionality realizes memorization of reusable procedures as commands.

## Future improvements

- [ ] Support for local CommandRegistry
- [ ] Support for langchain tools
- [ ] Slack integration
- [ ] More robust error fixing
- [ ] Support for control flows (if / for)
