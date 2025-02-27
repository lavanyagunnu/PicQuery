import gradio as gr
import openai
import os
import shutil
import traceback
from io import BytesIO
from PIL import Image
import base64
import PyPDF2

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text if text else "No text found in PDF."
    except Exception as e:
        return f"Error extracting text: {e}"

def answer_query_from_pdf(pdf_path: str, api_key: str, question: str) -> str:
    client = openai.OpenAI(api_key=api_key)
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if "Error extracting text" in pdf_text or pdf_text.strip() == "No text found in PDF.":
        return pdf_text
    
    messages = [{"role": "user", "content": question + "\n\n" + pdf_text}]
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Unexpected error: {e}"

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

def Answer(api_key, file, Query):
    try:
        if not api_key:
            return "⚠️ Please enter your OpenAI API Key."
        if not file:
            return "⚠️ Please upload a PDF or an Image."
        
        save_dir = "temp_files"
        os.makedirs(save_dir, exist_ok=True)
        pdf_path = None
        image_path = None
        
        save_dir = "temp_files"
        os.makedirs(save_dir, exist_ok=True)
        if isinstance(file, str):
            file_path = os.path.join(save_dir, file.name)
            return answer_query_from_pdf(file_path, api_key, Query)
        else:
            file_path = os.path.join(save_dir, file.name)
            file.save(file_path)
            return answer_query_from_image(file_path, api_key, Query)
    except Exception as e:
        error_msg = f"❌ An error occurred:\n\n{str(e)}\n\n{traceback.format_exc()}"
        return error_msg, ""

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    fn=Answer,
    with gr.Row():
        with gr.Column(scale=1):
            pass

        with gr.Column(scale=7): 
            api_key = gr.Textbox(label="🔑 OpenAI API Key", placeholder="Enter your API Key securely", type="password")
            file = gr.File(label="📄 Upload PDF or Image", height=300)
            query = gr.Textbox(label="🏢 Ask Me", placeholder="Ask Me")
            btn = gr.Button("Answer")
            output = gr.Textbox(label="📝 Answer", interactive=True)
        with gr.Column(scale=1):
            pass

    btn.click(Answer, inputs=[api_key, file, query], outputs=[output])
    



demo.launch()
