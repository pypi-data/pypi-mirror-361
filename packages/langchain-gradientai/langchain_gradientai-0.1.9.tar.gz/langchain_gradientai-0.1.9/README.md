# langchain-gradientai

This package contains the LangChain integration with Digitalocean

## Installation

```bash
pip install -U langchain-gradientai
```

And you should configure credentials by setting the `DIGITALOCEAN_MODEL_ACCESS_KEY` environment variable:

1. Login to DigitalOcean Cloud console
2. Go to the **GradienAI Platform** and navigate to **Serverless Inference**.
2. Click on **Create model access key**, enter a name, and create the key.
3. Use the generated key as your `DIGITALOCEAN_MODEL_ACCESS_KEY`:



Create a .env file and add your access key:
DIGITALOCEAN_MODEL_ACCESS_KEY=your_access_key_here

## Chat Models

`ChatGradientAI` class exposes chat models from langchain-gradientai.

### Invoke

```python
from langchain_gradientai import ChatGradientAI

llm = ChatGradientAI(
    model="llama3.3-70b-instruct",
    api_key=os.getenv("DIGITALOCEAN_MODEL_ACCESS_KEY")
)

result = llm.invoke("What is the capital of France?.")
print(result)
```

### Stream

```python
from langchain_gradientai import ChatGradientAI

llm = ChatGradientAI(
    model="llama3.3-70b-instruct",
    api_key=os.getenv("DIGITALOCEAN_MODEL_ACCESS_KEY")
)

for chunk in llm.stream("Tell me what happened to the Dinosaurs?"):
    print(chunk.content, end="", flush=True)

```



More features coming soon.