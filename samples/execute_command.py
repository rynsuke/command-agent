import os
from channels.console import ChannelConsole
from commands.notion.commands import notion_commands
from commands.registry import CommandRegistry

from langchain.embeddings import OpenAIEmbeddings
import pinecone
from langchain import OpenAI
from storage.pinecone import PineconeDB

COMMAND_NAME = "SaveTextToNotionDatbaseAndReturnPageURL"

# Generated by ChatGPT
TEXT = """
Attention is all you need

"Attention is All You Need" is a groundbreaking research paper published in 2017 by researchers at Google Brain. The paper introduced the Transformer model, which revolutionized the field of Natural Language Processing (NLP).

Before this paper, recurrent neural networks (RNNs) and convolutional neural networks (CNNs) were widely used for NLP tasks. However, these models had certain limitations, including difficulty handling long-range dependencies in text and inefficient sequential computation that made it challenging to fully utilize modern parallel computing hardware.

The key insight of "Attention is All You Need" was the introduction of the "Transformer" model, which solely relies on attention mechanisms and eliminates recurrence entirely. The attention mechanism allows the model to focus on different parts of the input sequence when producing an output, enabling it to capture long-range dependencies in the data. Specifically, the paper introduced the concept of "Scaled Dot-Product Attention" and "Multi-Head Attention".

The Transformer model is highly parallelizable (i.e., many operations can be performed simultaneously), leading to more efficient training times compared to RNNs and CNNs. The model also tends to achieve superior results on many NLP tasks.

The Transformer model proposed in this paper serves as the foundation for subsequent models like GPT (Generative Pretrained Transformer) and BERT (Bidirectional Encoder Representations from Transformers), which have further advanced the state-of-the-art in NLP.

However, it's worth noting that while the Transformer model has proven highly successful, the "attention is all you need" mantra isn't taken literally in practice. Many successful models still use other components in addition to attention. For example, they may use positional encodings to capture the order of words in a sequence or feed-forward neural networks to transform the attention outputs.
"""


async def execute_command():
    command_llm = OpenAI(temperature=0, max_tokens=1500)

    pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENVIRONMENT"])
    index = pinecone.Index(os.environ["PINECONE_COMMANDS_INDEX_NAME"])

    emb = OpenAIEmbeddings()
    storage = PineconeDB(index, emb)

    command_registry = CommandRegistry(notion_commands(token=os.environ["NOTION_TOKEN"]), storage, command_llm)
    channel = ChannelConsole()

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
