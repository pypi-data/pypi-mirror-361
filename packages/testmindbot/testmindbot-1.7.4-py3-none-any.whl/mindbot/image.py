from google.genai import types
from PIL import Image
from io import BytesIO
import requests

class ImageManipulation:
    def __init__(self, mindbot_instance):
        self.client = mindbot_instance.client

    def edit_image(self, image_path, prompt, model="mindstyle-2.5"):
        image = Image.open(image_path)
        
        contents = [prompt, image]
        
        response = self.client.generate_content(
            model="gemini-2.5-flash-preview-image-generation",
            contents=contents,
            generation_config=types.GenerateContentConfig(
              response_modalities=['TEXT', 'IMAGE']
            )
        )

        text_response = ""
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text_response += part.text
            elif part.inline_data is not None:
                edited_image = Image.open(BytesIO((part.inline_data.data)))
                edited_image.save("edited_image.png")
        
        return text_response, "edited_image.png"

    def generate_image(self, prompt, model="mindpaint-2.5"):
        url = f"https://pollinations.ai/p/{prompt}"
        response = requests.get(url)
        with open('generated_image.jpg', 'wb') as file:
            file.write(response.content)
        
        image_link = f"mindpaint.mindbotai.pro/prompt/{prompt.replace(' ', '_')}"
        return "Image downloaded!", 'generated_image.jpg', image_link
