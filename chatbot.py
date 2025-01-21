from openai import OpenAI
import streamlit as st 
import os

api_key = st.secrets["API_TOKEN"]

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

