from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI
import os

# Set env variables here or in .env
os.environ["OPENAI_API_BASE"] = "http://localhost:443/v1"
os.environ["OPENAI_API_KEY"] = "../llama.cpp/models/wizardLM/7B/wizardLM-7B.GGML.q5_1.bin"

# Simple completion example
llm = OpenAI(temperature=0.9)
text = "What would be a good company name for a company that makes colorful socks?"
result = llm(text)
print(result)


# Prompt template
template = """Question: {question}
Answer: Let's think step by step."""

# Create prompt template and chain
prompt = PromptTemplate(template=template, input_variables=["question"])
llm_chain = LLMChain(prompt=prompt, llm=llm)

# Ask question with the prompt template
question = "What NFL team won the Super Bowl in the year Justin Beiber was born?"
result = llm_chain.run(question)
print(result)
