import gradio as gr

def Answer(image, Query):
    return "Query"

demo = gr.Interface(
    fn=Answer,
    inputs=["image", "text"],
    outputs=["text"],
)

demo.launch()
