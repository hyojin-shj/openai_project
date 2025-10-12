# from openai import OpenAI
# import os
# from dotenv import load_dotenv
# load_dotenv()

# client= OpenAI(api_key = os.environ.get("API_KEY"))

# response = client.images.generate(
#     model="dall-e-3",
#     prompt="a white cute cat",
#     size="1024x1024",
#     quality="standard",
#     n=1
# )

# image_url = response.data[0].url
# print(image_url)

from io import BytesIO
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()

client = OpenAI(api_key = os.environ.get("API_KEY")) 

image = Image.open("white cute cat.png")
width, height = 256, 256 
image = image.resize((width, height)) 
byte_stream = BytesIO()
image.save(byte_stream, format='PNG')
byte_array = byte_stream.getvalue()

response = client.images.create_variation(
image=byte_array, 
n=1,
model="dall-e-2", 
size="1024x1024" 
)
image_url = response.data[0].url
print(image_url)