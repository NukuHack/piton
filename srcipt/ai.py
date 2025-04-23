#pip install --upgrade huggingface_hub
from huggingface_hub import InferenceClient
import os

# Step out of the current script folder and go into the resources folder then get out the key
file_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'resources'), 'key.txt')

# Check if the file exists
if os.path.exists(file_path):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read the first line
        first_line = file.readline().strip()
else:
    print(f"The file {file_path} does not exist.")


client = InferenceClient(
	provider="nebius",
	api_key=first_line #lol api key
)

messages = [
	{
		"role": "user",
		"content": "Hello, can you tell me an interesting thing about the world we live in?"
	}
]

response = client.chat.completions.create(
	model="deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct", 
	messages=messages, 
	temperature=0.1,
	max_tokens=4096,
	top_p=0.5,
	stream=True
)

#increadibly fast, even tho "streaming" does not really works

for chunk in response:
    print(chunk.choices[0].delta.content, end="")