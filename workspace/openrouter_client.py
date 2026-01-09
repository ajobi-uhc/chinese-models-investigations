"""
OpenRouter client initialization for Kimi model access.
Usage:
    from openrouter_client import client

    response = client.chat.completions.create(
        model="moonshotai/kimi-k2-0905",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"},
            {"role": "assistant", "content": "So hows it going?"},
        ],
    )

    print(response.choices[0].message.content)

"""

import os
from openai import OpenAI

# Initialize and return OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)
