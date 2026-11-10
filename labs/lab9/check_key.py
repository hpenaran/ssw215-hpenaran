import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

reply = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say OK and nothing else."}],
)
print(reply.choices[0].message.content) 