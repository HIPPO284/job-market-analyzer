from ollama import chat

response = chat(
    model="gpt-oss:20b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Python can call Ollama"
        }
    ],
)

print(response.message.content)
