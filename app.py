"""
Business Intelligence Dashboard
--------------------------------
This dashboard provides:
- Data upload for CSV/Excel files
- Automatic dataset profiling
- Statistical summaries (numeric and categorical)
- Missing value reports and correlation matrix
- Interactive filtering (categorical, numeric, date-based)
- Modular, maintainable structure suitable for academic submission

Author: Omar G.
Course: Applied Programming and Data Processing for AI (CS5130)
"""

import gradio as gr
import pandas as pd

from data_processor import (
    load_data,
    get_basic_info,
    preview_data,
    numeric_summary,
    categorical_summary,
    missing_values_report,
    correlation_matrix,
)

from utils import get_filter_options


def create_dashboard():
    """Constructs the full multi-tab Business Intelligence Dashboard UI."""

    with gr.Blocks(theme=gr.themes.Soft()) as demo:

        gr.Markdown("# Business Intelligence Dashboard")

        # DataFrame is stored in Gradio state so all tabs can access it
        df_state = gr.State(value=None)

        file_input = gr.File(label="Upload CSV or Excel File")

        # ===============================================================
        # 1. DATA UPLOAD TAB
        # ===============================================================
        with gr.Tab("Data Upload"):
            gr.Markdown("### Upload and Preview Your Dataset")

            basic_info_output = gr.JSON(label="Dataset Information")
            preview_output = gr.DataFrame(label="Data Preview")

            def handle_upload(file):
                """Load dataset and return its structure and preview."""
                if file is None:
                    return None, {}, None

                df = load_data(file)
                info = get_basic_info(df)
                preview = preview_data(df)
                return df, info, preview

            file_input.change(
                fn=handle_upload,
                inputs=file_input,
                outputs=[df_state, basic_info_output, preview_output]
            )

        # ===============================================================
        # 2. STATISTICS TAB
        # ===============================================================
        with gr.Tab("Statistics"):
            gr.Markdown("### Summary Statistics")

            stats_button = gr.Button("Generate Statistics")

            numeric_output = gr.DataFrame(label="Numeric Summary")
            categorical_output = gr.JSON(label="Categorical Summary")
            missing_output = gr.JSON(label="Missing Values")
            corr_output = gr.DataFrame(label="Correlation Matrix")

            def generate_statistics(df):
                """Compute and return summary statistics."""
                if df is None:
                    return None, None, None, None

                num = numeric_summary(df)
                num = num.reset_index().rename(columns={"index": "Metric"})

                cat = categorical_summary(df)
                missing = missing_values_report(df)
                corr = correlation_matrix(df)

                return num, cat, missing, corr

            stats_button.click(
                fn=generate_statistics,
                inputs=df_state,
                outputs=[numeric_output, categorical_output, missing_output, corr_output]
            )

        # ===============================================================
        # 3. FILTER & EXPLORE TAB
        # ===============================================================
        with gr.Tab("Filter & Explore"):
            gr.Markdown("### Interactive Filtering")

            with gr.Row():
                # -------------------------------------------------------
                # Left Column: Filter Inputs
                # -------------------------------------------------------
                with gr.Column(scale=1):
                    gr.Markdown("**Categorical Filter**")
                    cat_column = gr.Dropdown(label="Select Column", choices=[], interactive=True)
                    cat_values = gr.Dropdown(label="Select Values", choices=[], multiselect=True, interactive=True)

                    gr.Markdown("---")
                    gr.Markdown("**Numeric Filter**")
                    num_column = gr.Dropdown(label="Select Column", choices=[], interactive=True)
                    with gr.Row():
                        num_min = gr.Number(label="Min", interactive=True)
                        num_max = gr.Number(label="Max", interactive=True)

                    gr.Markdown("---")
                    gr.Markdown("**Date Filter**")
                    date_column = gr.Dropdown(label="Select Column", choices=[], interactive=True)
                    with gr.Row():
                        date_start = gr.Textbox(label="From (YYYY-MM-DD)", placeholder="2010-12-01", interactive=True)
                        date_end = gr.Textbox(label="To (YYYY-MM-DD)", placeholder="2011-12-09", interactive=True)

                    gr.Markdown("---")
                    apply_btn = gr.Button("Apply Filters", variant="primary")
                    clear_btn = gr.Button("Clear All Filters")

                # -------------------------------------------------------
                # Right Column: Filtered Results
                # -------------------------------------------------------
                with gr.Column(scale=2):
                    row_count = gr.Markdown("**Upload a file to begin**")
                    filtered_data = gr.DataFrame(interactive=False)

            # Button to reload filter options manually
            init_btn = gr.Button("Load Filters", variant="secondary")

            # -----------------------------------------------------------
            # Populate filter dropdown options when dataset loads
            # -----------------------------------------------------------
            def setup_filters(df):
                if df is None:
                    return (
                        gr.update(choices=[]),
                        gr.update(choices=[]),
                        gr.update(choices=[]),
                        "Upload a file to begin",
                        None,
                    )

                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                date_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64", "datetime"]).columns.tolist()

                # Also detect string-based datetime columns
                for col in df.columns:
                    if "datetime" in str(df[col].dtype) and col not in date_cols:
                        date_cols.append(col)

                return (
                    gr.update(choices=cat_cols, value=None),
                    gr.update(choices=numeric_cols, value=None),
                    gr.update(choices=date_cols, value=None),
                    f"{len(df):,} rows total - Select filters and click Apply",
                    df.head(100),
                )

            file_input.change(
                fn=setup_filters,
                inputs=df_state,
                outputs=[cat_column, num_column, date_column, row_count, filtered_data]
            )

            init_btn.click(
                fn=setup_filters,
                inputs=df_state,
                outputs=[cat_column, num_column, date_column, row_count, filtered_data]
            )

            # -----------------------------------------------------------
            # Update category values after selecting a categorical column
            # -----------------------------------------------------------
            def update_cat_values(df, col):
                if df is None or col is None:
                    return gr.update(choices=[], value=[])

                values = sorted(df[col].dropna().astype(str).unique().tolist())
                return gr.update(choices=values, value=[])

            cat_column.change(
                fn=update_cat_values,
                inputs=[df_state, cat_column],
                outputs=cat_values
            )

            # -----------------------------------------------------------
            # Apply selected filters
            # -----------------------------------------------------------
            def apply_filters(df, cat_col, cat_vals, num_col, n_min, n_max, date_col, d_start, d_end):
                if df is None:
                    return "Upload a file to begin", None

                filtered = df.copy()

                # Categorical filter
                if cat_col and cat_vals:
                    filtered = filtered[filtered[cat_col].astype(str).isin(cat_vals)]

                # Numeric filter
                if num_col:
                    if n_min is not None:
                        filtered = filtered[filtered[num_col] >= n_min]
                    if n_max is not None:
                        filtered = filtered[filtered[num_col] <= n_max]

                # Date filter
                if date_col:
                    if d_start:
                        try:
                            start_dt = pd.to_datetime(d_start)
                            filtered = filtered[filtered[date_col] >= start_dt]
                        except:
                            pass
                    if d_end:
                        try:
                            end_dt = pd.to_datetime(d_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                            filtered = filtered[filtered[date_col] <= end_dt]
                        except:
                            pass

                total = len(df)
                count = len(filtered)
                status = f"{count:,} of {total:,} rows match your filters"

                return status, filtered.head(100)

            apply_btn.click(
                fn=apply_filters,
                inputs=[
                    df_state,
                    cat_column, cat_values,
                    num_column, num_min, num_max,
                    date_column, date_start, date_end
                ],
                outputs=[row_count, filtered_data]
            )

            # -----------------------------------------------------------
            # Clear all filters and reset view
            # -----------------------------------------------------------
            def clear_filters(df):
                if df is None:
                    return (
                        None, [], None, None, None, None, None, None,
                        "Upload a file to begin",
                        None
                    )

                return (
                    None, [], None, None, None, None, None, None,
                    f"{len(df):,} rows total",
                    df.head(100)
                )

            clear_btn.click(
                fn=clear_filters,
                inputs=df_state,
                outputs=[
                    cat_column, cat_values,
                    num_column, num_min, num_max,
                    date_column, date_start, date_end,
                    row_count, filtered_data
                ]
            )

        # ===============================================================
        # 4. VISUALIZATIONS TAB
        # ===============================================================
        with gr.Tab("Visualizations"):
            gr.Markdown("### Visualizations (Coming Soon)")

        # ===============================================================
        # 5. INSIGHTS TAB
        # ===============================================================
        with gr.Tab("Insights"):
            gr.Markdown("### Insights (Coming Soon)")

    return demo


if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
