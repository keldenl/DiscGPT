from langchain.schema import (
    HumanMessage,
)
from langchain.chat_models import ChatOpenAI
import os

# Set local env here or in the .env file
os.environ["OPENAI_API_BASE"] = "http://localhost:443/v1"
os.environ["OPENAI_API_KEY"] = "../llama.cpp/models/wizardLM/7B/wizardLM-7B.GGML.q5_1.bin"


chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.9)
results = chat([HumanMessage(content="Translate this sentence from English to French. I love programming.")])
print(results)