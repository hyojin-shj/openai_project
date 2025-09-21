from openai import OpenAI
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

client = OpenAI(
  api_key=os.environ.get("API_KEY")
)

def generate_poem():

  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
      {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ]
  )

  return completion.choices[0].message


print(generate_poem())
