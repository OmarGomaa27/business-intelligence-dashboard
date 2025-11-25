import gradio as gr
import pandas as pd
df = None

from data_processor import (
    load_data,
    get_basic_info,
    preview_data,
    numeric_summary,
    categorical_summary,
    missing_values_report,
    correlation_matrix
)


def create_dashboard():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Business Intelligence Dashboard")
        
        # ---------------------------
        # DATA UPLOAD TAB
        # ---------------------------
        with gr.Tab("Data Upload"):
            gr.Markdown("### Upload your dataset")

            file_input = gr.File(label="Upload CSV or Excel")
            basic_info_output = gr.JSON(label="Dataset Information")
            preview_output = gr.DataFrame(label="Data Preview")

            def handle_upload(file):
                global df
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


        # ---------------------------
        # STATISTICS TAB
        # ---------------------------
        with gr.Tab("Statistics"):
            gr.Markdown("### Statistical Summaries")

            stats_button = gr.Button("Generate Statistics")

            numeric_output = gr.DataFrame(label="Numeric Summary")
            categorical_output = gr.JSON(label="Categorical Summary")
            missing_output = gr.JSON(label="Missing Values Report")
            corr_output = gr.DataFrame(label="Correlation Matrix")

            def generate_statistics():
                global df
                if df is None:
                    return None, None, None, None

                # Numeric summary
                num = numeric_summary(df)
                num = num.reset_index().rename(columns={"index": "Metric"})

                # Categorical summary
                cat = categorical_summary(df)

                # Missing values report
                missing = missing_values_report(df)

                # Correlation matrix
                corr = correlation_matrix(df)

                return num, cat, missing, corr

            stats_button.click(
                fn=generate_statistics,
                inputs=None,
                outputs=[numeric_output, categorical_output, missing_output, corr_output]
            )

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
