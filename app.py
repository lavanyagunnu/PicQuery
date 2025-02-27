import gradio as gr
import openai
import os
import shutil
import traceback
from io import BytesIO
from PIL import Image
import base64

def answer_query_from_image(image_path: str, api_key: str, question: str) -> str:
    client = openai.OpenAI(api_key=api_key)

    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    },
                ],
            }
        ]

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=300,
            temperature=0.2
        )

        return completion.choices[0].message.content


    #except openai.OpenAIError as e:
        #return f"OpenAI API error: {e}"
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
    Query = gr.Textbox(label="🏢 Ask me", placeholder="Enter your Query")
    btn = gr.Button("Answer")
    output = gr.Textbox(label="📝 Answer", interactive=True)

    btn.click(Answer, inputs=[api_key, Image, Query], outputs=[output])
    



demo.launch()
