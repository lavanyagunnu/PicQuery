import gradio as gr
from openai import OpenAI
import os
import shutil
import traceback
import requests
from io import BytesIO
from PIL import Image

def answer_query_from_image(image_path: str, api_key: str, question: str) -> str:
    """
    Extracts text from an image and answers the given question.
    """
    client = OpenAI(api_key=api_key)  # ✅ Use OpenAI() class directly

    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract text from the image and answer the question."},
                {"role": "user", "content": question},
            ],
            max_tokens=500
        )
        
        return completion.choices[0].message.content
    
    except openai.OpenAIError as e:
        return f"OpenAI API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def Answer(api_key, image, Query):
    try:
        if not api_key:
            return "⚠️ Please enter your OpenAI API Key.", ""

        if image is None:
            return "⚠️ Please upload an Image.", ""

        save_dir = "temp_images"
        os.makedirs(save_dir, exist_ok=True)
        image_path = os.path.join(save_dir, "uploaded_image.png")
        image.save(image_path)
        return answer_query_from_image(image_path, api_key, Query)


    except Exception as e:
        error_msg = f"❌ An error occurred:\n\n{str(e)}\n\n{traceback.format_exc()}"
        return error_msg, ""

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    fn=Answer,

    api_key = gr.Textbox(label="🔑 OpenAI API Key", placeholder="Enter your API Key securely")
    Image = gr.Image(label="📄 Upload Image", type="pil")
    Query = gr.Textbox(label="🏢 Query", placeholder="Enter your Query")
    btn = gr.Button("Answer the Query")
    output = gr.Textbox(label="📝 Answer", interactive=True)

    btn.click(Answer, inputs=[api_key, Image, Query], outputs=[output])
    



demo.launch()
