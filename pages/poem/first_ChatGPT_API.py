# pages/poem/poem.py

def generate_poem_text(client, topic):
  completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant who writes poems in Korean."},
            {"role": "user",
             "content": f"{topic}에 대한 시를 작성해줘."}
        ]
    )

  return completion.choices[0].message.content