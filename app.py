import gradio as gr
import pandas as pd

from data_processor import load_data, get_basic_info, preview_data


def create_dashboard():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Business Intelligence Dashboard")
        
        with gr.Tab("Data Upload"):
            gr.Markdown("### Upload your dataset")

            file_input = gr.File(label="Upload CSV or Excel")
            basic_info_output = gr.JSON(label="Dataset Information")
            preview_output = gr.DataFrame(label="Data Preview")

            def handle_upload(file):
                if file is None:
                    return {}, None
                
                df = load_data(file)
                info = get_basic_info(df)
                preview = preview_data(df)

                return info, preview

            file_input.change(
                fn=handle_upload,
                inputs=file_input,
                outputs=[basic_info_output, preview_output]
            )

        with gr.Tab("Statistics"):
            pass

        with gr.Tab("Filter & Explore"):
            pass

        with gr.Tab("Visualizations"):
            pass

        with gr.Tab("Insights"):
            pass

    return demo


if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()