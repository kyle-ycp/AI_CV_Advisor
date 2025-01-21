from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_TOKEN")

def generate_chat_completion(prompt):
    client = OpenAI(
        api_key=api_key
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message

