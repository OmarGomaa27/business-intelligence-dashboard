"""
Business Intelligence Dashboard
-------------------------------
This dashboard provides:
- Data upload for CSV/Excel files
- Automatic dataset profiling
- Statistical summaries (numeric and categorical)
- Missing value reports and correlation matrix
- Interactive filtering (categorical, numeric, date-based)
- Modular structure suitable for academic submission

Author: Omar Gomaa
Course: CS 5130 - Applied Programming and Data Processing for AI
Institution: Northeastern University
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

from visualizations import (
    create_time_series_plot,
    create_distribution_plot,
    create_category_bar_chart,
    create_scatter_plot,
    create_correlation_heatmap,
    save_plot_as_png,
)

from insights import generate_all_insights
from utils import get_filter_options

# Constants
DEFAULT_PREVIEW_ROWS = 5
DEFAULT_FILTER_DISPLAY_ROWS = 100
MAX_SCATTER_POINTS = 5000
TOP_N_CATEGORIES = 20
CHART_DPI = 150


def create_dashboard():
    """Constructs and returns the full multi-tab Business Intelligence Dashboard interface."""
    with gr.Blocks(theme=gr.themes.Soft()) as demo:

        gr.Markdown("# Business Intelligence Dashboard")
        gr.Markdown("Upload a dataset to generate summary statistics, visualizations, and insights.")

        # Application state
        df_state = gr.State(value=None)                # Full dataset
        filtered_state = gr.State(value=None)          # Filtered dataset

        file_input = gr.File(label="Upload CSV or Excel File")

        # ===============================================================
        # 1. DATA UPLOAD TAB
        # ===============================================================
        with gr.Tab("Data Upload"):
            gr.Markdown("### Upload and Preview Dataset")

            basic_info_output = gr.JSON(label="Dataset Information")
            preview_output = gr.DataFrame(label="Data Preview")

            def handle_upload(file):
                """Loads the dataset and returns metadata and a preview."""
                if file is None:
                    return None, {}, None

                df = load_data(file)
                info = get_basic_info(df)
                preview = preview_data(df, n=DEFAULT_PREVIEW_ROWS)
                return df, info, preview

            file_input.change(
                fn=handle_upload,
                inputs=file_input,
                outputs=[df_state, basic_info_output, preview_output],
            )

        # ===============================================================
        # 2. STATISTICS TAB
        # ===============================================================
        with gr.Tab("Statistics"):
            gr.Markdown("### Summary Statistics")

            stats_button = gr.Button("Generate Statistics", variant="primary")

            numeric_output = gr.DataFrame(label="Numeric Summary")
            categorical_output = gr.JSON(label="Categorical Summary")
            missing_output = gr.JSON(label="Missing Values")
            corr_output = gr.DataFrame(label="Correlation Matrix")

            def generate_statistics(df):
                """Computes summary statistics for the dataset."""
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
                outputs=[numeric_output, categorical_output, missing_output, corr_output],
            )

        # ===============================================================
        # 3. FILTER & EXPLORE TAB
        # ===============================================================
        with gr.Tab("Filter & Explore"):
            gr.Markdown("### Interactive Data Filtering")

            with gr.Row():

                # -------------------------------------------------------
                # Left column: Filter Controls
                # -------------------------------------------------------
                with gr.Column(scale=1):
                    filter_load_btn = gr.Button("Load Filter Options", variant="secondary")

                    gr.Markdown("**Categorical Filter**")
                    cat_column = gr.Dropdown(label="Column", choices=[], interactive=True)
                    cat_values = gr.Dropdown(
                        label="Values", choices=[], multiselect=True, interactive=True
                    )

                    gr.Markdown("---")

                    gr.Markdown("**Numeric Filter**")
                    num_column = gr.Dropdown(label="Column", choices=[], interactive=True)
                    with gr.Row():
                        num_min = gr.Number(label="Min", interactive=True)
                        num_max = gr.Number(label="Max", interactive=True)

                    gr.Markdown("---")

                    gr.Markdown("**Date Filter**")
                    date_column = gr.Dropdown(label="Column", choices=[], interactive=True)
                    with gr.Row():
                        date_start = gr.Textbox(
                            label="From (YYYY-MM-DD)",
                            placeholder="YYYY-MM-DD",
                            interactive=True,
                        )
                        date_end = gr.Textbox(
                            label="To (YYYY-MM-DD)",
                            placeholder="YYYY-MM-DD",
                            interactive=True,
                        )

                    gr.Markdown("---")

                    apply_btn = gr.Button("Apply Filters", variant="primary")
                    clear_btn = gr.Button("Clear Filters")

                # -------------------------------------------------------
                # Right column: Filter Results
                # -------------------------------------------------------
                with gr.Column(scale=2):
                    row_count = gr.Markdown("Click 'Load Filter Options' to begin.")
                    filtered_data = gr.DataFrame(interactive=False)

            def setup_filters(df):
                """Initializes filter dropdown options based on dataset columns."""
                if df is None:
                    return (
                        gr.update(choices=[]),
                        gr.update(choices=[]),
                        gr.update(choices=[]),
                        "Upload a dataset to begin.",
                        None,
                    )

                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                date_cols = [
                    col for col in df.columns if "datetime" in str(df[col].dtype)
                ]

                # Remove date-like columns from categorical list
                date_keywords = ["date", "time", "timestamp", "created", "updated"]
                cat_cols = [
                    col for col in cat_cols
                    if not any(keyword in col.lower() for keyword in date_keywords)
                ]

                # Add string-based date-like columns to date candidates
                for col in df.columns:
                    if (
                        col not in date_cols
                        and any(keyword in col.lower() for keyword in date_keywords)
                        and df[col].dtype == "object"
                    ):
                        date_cols.append(col)

                return (
                    gr.update(choices=cat_cols, value=None),
                    gr.update(choices=numeric_cols, value=None),
                    gr.update(choices=date_cols, value=None),
                    f"{len(df):,} rows available. Select filters and apply.",
                    df.head(DEFAULT_FILTER_DISPLAY_ROWS),
                )

            file_input.change(
                fn=setup_filters,
                inputs=df_state,
                outputs=[cat_column, num_column, date_column, row_count, filtered_data],
            )
            filter_load_btn.click(
                fn=setup_filters,
                inputs=df_state,
                outputs=[cat_column, num_column, date_column, row_count, filtered_data],
            )

            def update_cat_values(df, col):
                """Returns unique values for the selected categorical column."""
                if df is None or col is None:
                    return gr.update(choices=[], value=[])

                values = sorted(df[col].dropna().astype(str).unique().tolist())
                return gr.update(choices=values, value=[])

            cat_column.change(
                fn=update_cat_values,
                inputs=[df_state, cat_column],
                outputs=cat_values,
            )

            def apply_filters(df, cat_col, cat_vals, num_col, n_min, n_max, date_col, d_start, d_end):
                """Applies categorical, numeric, and date filters to the dataset."""
                if df is None:
                    return "Upload a dataset to begin.", None, None

                filtered = df.copy()

                # Categorical filtering
                if cat_col and cat_vals:
                    filtered = filtered[filtered[cat_col].astype(str).isin(cat_vals)]

                # Numeric filtering
                if num_col in filtered.columns:
                    if n_min is not None:
                        filtered = filtered[filtered[num_col] >= n_min]
                    if n_max is not None:
                        filtered = filtered[filtered[num_col] <= n_max]

                # Date filtering
                if date_col in filtered.columns:
                    if not pd.api.types.is_datetime64_any_dtype(filtered[date_col]):
                        filtered[date_col] = pd.to_datetime(filtered[date_col], errors="coerce")

                    if d_start:
                        try:
                            start_dt = pd.to_datetime(d_start)
                            filtered = filtered[filtered[date_col] >= start_dt]
                        except Exception:
                            pass

                    if d_end:
                        try:
                            end_dt = pd.to_datetime(d_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                            filtered = filtered[filtered[date_col] <= end_dt]
                        except Exception:
                            pass

                total = len(df)
                count = len(filtered)

                return (
                    f"{count:,} of {total:,} rows match the applied filters.",
                    filtered.head(DEFAULT_FILTER_DISPLAY_ROWS),
                    filtered,
                )

            apply_btn.click(
                fn=apply_filters,
                inputs=[
                    df_state,
                    cat_column,
                    cat_values,
                    num_column,
                    num_min,
                    num_max,
                    date_column,
                    date_start,
                    date_end,
                ],
                outputs=[row_count, filtered_data, filtered_state],
            )

            def clear_filters(df):
                """Resets all filter controls to their default state."""
                if df is None:
                    return (
                        None, [], None, None, None, None, "", "",
                        "Upload a dataset to begin.",
                        None, None,
                    )

                return (
                    None, [], None, None, None, None, "", "",
                    f"{len(df):,} rows available. Select filters and apply.",
                    df.head(DEFAULT_FILTER_DISPLAY_ROWS),
                    df,
                )

            clear_btn.click(
                fn=clear_filters,
                inputs=df_state,
                outputs=[
                    cat_column, cat_values,
                    num_column, num_min, num_max,
                    date_column, date_start, date_end,
                    row_count, filtered_data,
                    filtered_state,
                ],
            )

            # Export CSV
            gr.Markdown("---")
            gr.Markdown("### Export Filtered Data")

            with gr.Row():
                export_csv_btn = gr.Button("Export Filtered Data as CSV")
                csv_output = gr.File(label="Download CSV")

            def export_csv(filtered_df, full_df):
                """Exports the filtered dataset or the full dataset as a CSV file."""
                df = filtered_df if filtered_df is not None else full_df
                if df is None:
                    return None

                filepath = "filtered_data.csv"
                df.to_csv(filepath, index=False)
                return filepath

            export_csv_btn.click(
                fn=export_csv,
                inputs=[filtered_state, df_state],
                outputs=csv_output,
            )

        # ===============================================================
        # 4. VISUALIZATIONS TAB
        # ===============================================================
        with gr.Tab("Visualizations"):
            gr.Markdown("### Data Visualizations")

            viz_load_btn = gr.Button("Load Visualization Options", variant="secondary")

            with gr.Tabs():

                # Time Series
                with gr.Tab("Time Series"):
                    gr.Markdown("Visualize aggregated trends over time.")
                    with gr.Row():
                        ts_date_col = gr.Dropdown(label="Date Column", choices=[], interactive=True)
                        ts_value_col = gr.Dropdown(label="Value Column", choices=[], interactive=True)
                        ts_agg = gr.Dropdown(
                            label="Aggregation",
                            choices=["sum", "mean", "count", "median"],
                            value="sum",
                            interactive=True,
                        )
                    ts_btn = gr.Button("Generate Time Series", variant="primary")
                    ts_plot = gr.Plot()

                # Distribution
                with gr.Tab("Distribution"):
                    gr.Markdown("Explore the distribution of numerical values.")
                    with gr.Row():
                        dist_col = gr.Dropdown(label="Numeric Column", choices=[], interactive=True)
                        dist_type = gr.Dropdown(
                            label="Chart Type",
                            choices=["histogram", "box"],
                            value="histogram",
                            interactive=True,
                        )
                    dist_btn = gr.Button("Generate Distribution", variant="primary")
                    dist_plot = gr.Plot()

                # Category Analysis
                with gr.Tab("Category Analysis"):
                    gr.Markdown("Analyze aggregated values for categorical variables.")
                    with gr.Row():
                        cat_viz_col = gr.Dropdown(label="Category Column", choices=[], interactive=True)
                        cat_value_col = gr.Dropdown(label="Value Column", choices=[], interactive=True)
                        cat_agg = gr.Dropdown(
                            label="Aggregation",
                            choices=["sum", "mean", "count", "median"],
                            value="sum",
                            interactive=True,
                        )
                    cat_btn = gr.Button("Generate Category Chart", variant="primary")
                    cat_plot = gr.Plot()

                # Scatter & Correlation
                with gr.Tab("Scatter & Correlation"):
                    gr.Markdown("Visualize relationships between numerical variables.")
                    with gr.Row():
                        scatter_x = gr.Dropdown(label="X Axis", choices=[], interactive=True)
                        scatter_y = gr.Dropdown(label="Y Axis", choices=[], interactive=True)
                    with gr.Row():
                        scatter_btn = gr.Button("Scatter Plot", variant="primary")
                        corr_btn = gr.Button("Correlation Heatmap", variant="secondary")
                    scatter_plot = gr.Plot()

            def setup_viz_dropdowns(df):
                """Populates visualization dropdowns based on data types."""
                if df is None:
                    empty = gr.update(choices=[])
                    return [empty] * 7

                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                date_cols = [c for c in df.columns if "datetime" in str(df[c].dtype)]

                # Add string-based date-like columns
                date_keywords = ["date", "time", "timestamp", "created", "updated"]
                for col in df.columns:
                    if col not in date_cols:
                        if any(keyword in col.lower() for keyword in date_keywords):
                            date_cols.append(col)
                            if col in cat_cols:
                                cat_cols.remove(col)

                # Exclude ID-like columns from distribution charts
                id_keywords = ["id", "invoice", "code", "number", "no", "num"]
                numeric_for_dist = [
                    col for col in numeric_cols
                    if not any(keyword in col.lower() for keyword in id_keywords)
                ]
                if not numeric_for_dist:
                    numeric_for_dist = numeric_cols

                return (
                    gr.update(choices=date_cols),
                    gr.update(choices=numeric_cols),
                    gr.update(choices=numeric_for_dist),
                    gr.update(choices=cat_cols),
                    gr.update(choices=numeric_cols),
                    gr.update(choices=numeric_cols),
                    gr.update(choices=numeric_cols),
                )

            file_input.change(
                fn=setup_viz_dropdowns,
                inputs=df_state,
                outputs=[
                    ts_date_col,
                    ts_value_col,
                    dist_col,
                    cat_viz_col,
                    cat_value_col,
                    scatter_x,
                    scatter_y,
                ],
            )
            viz_load_btn.click(
                fn=setup_viz_dropdowns,
                inputs=df_state,
                outputs=[
                    ts_date_col,
                    ts_value_col,
                    dist_col,
                    cat_viz_col,
                    cat_value_col,
                    scatter_x,
                    scatter_y,
                ],
            )

            # Visualization generation
            ts_btn.click(
                fn=create_time_series_plot,
                inputs=[df_state, ts_date_col, ts_value_col, ts_agg],
                outputs=ts_plot,
            )

            dist_btn.click(
                fn=create_distribution_plot,
                inputs=[df_state, dist_col, dist_type],
                outputs=dist_plot,
            )

            cat_btn.click(
                fn=lambda df, cat_col, val_col, agg: create_category_bar_chart(
                    df, cat_col, val_col, agg, TOP_N_CATEGORIES
                ),
                inputs=[df_state, cat_viz_col, cat_value_col, cat_agg],
                outputs=cat_plot,
            )

            scatter_btn.click(
                fn=lambda df, x, y: create_scatter_plot(df, x, y, MAX_SCATTER_POINTS),
                inputs=[df_state, scatter_x, scatter_y],
                outputs=scatter_plot,
            )

            corr_btn.click(
                fn=create_correlation_heatmap,
                inputs=[df_state],
                outputs=scatter_plot,
            )

            # Export visualizations
            gr.Markdown("---")
            gr.Markdown("### Export Visualization")
            gr.Markdown("Generate a chart above, then export it as a PNG file.")

            with gr.Row():
                export_ts_btn = gr.Button("Export Time Series")
                export_dist_btn = gr.Button("Export Distribution")
                export_cat_btn = gr.Button("Export Category Chart")
                export_scatter_btn = gr.Button("Export Scatter or Correlation")

            png_output = gr.File(label="Download PNG")

            def export_time_series_png(df, date_col, value_col, agg):
                """Exports a time series plot as a PNG file."""
                fig = create_time_series_plot(df, date_col, value_col, agg)
                if fig is None:
                    return None
                return save_plot_as_png(fig, "time_series.png")

            export_ts_btn.click(
                fn=export_time_series_png,
                inputs=[df_state, ts_date_col, ts_value_col, ts_agg],
                outputs=png_output,
            )

            def export_distribution_png(df, col, chart_type):
                """Exports a distribution plot as a PNG file."""
                fig = create_distribution_plot(df, col, chart_type)
                if fig is None:
                    return None
                return save_plot_as_png(fig, "distribution.png")

            export_dist_btn.click(
                fn=export_distribution_png,
                inputs=[df_state, dist_col, dist_type],
                outputs=png_output,
            )

            def export_category_png(df, cat_col, value_col, agg):
                """Exports a category chart as a PNG file."""
                fig = create_category_bar_chart(df, cat_col, value_col, agg, TOP_N_CATEGORIES)
                if fig is None:
                    return None
                return save_plot_as_png(fig, "category_chart.png")

            export_cat_btn.click(
                fn=export_category_png,
                inputs=[df_state, cat_viz_col, cat_value_col, cat_agg],
                outputs=png_output,
            )

            def export_scatter_png(df, x_col, y_col):
                """Exports a scatter plot as a PNG file."""
                fig = create_scatter_plot(df, x_col, y_col, MAX_SCATTER_POINTS)
                if fig is None:
                    return None
                return save_plot_as_png(fig, "scatter_plot.png")

            export_scatter_btn.click(
                fn=export_scatter_png,
                inputs=[df_state, scatter_x, scatter_y],
                outputs=png_output,
            )

        # ===============================================================
        # 5. INSIGHTS TAB
        # ===============================================================
        with gr.Tab("Insights"):
            gr.Markdown("### Automated Insights")
            gr.Markdown("Generates summary insights, top and bottom performers, and anomaly notes.")

            insights_btn = gr.Button("Generate Insights", variant="primary")

            with gr.Row():
                with gr.Column():
                    gr.Markdown("Top Performers")
                    top_performers = gr.DataFrame(label="Highest Values")

                with gr.Column():
                    gr.Markdown("Bottom Performers")
                    bottom_performers = gr.DataFrame(label="Lowest Values")

            gr.Markdown("---")
            gr.Markdown("Trends and Anomalies")
            anomalies_output = gr.Markdown()

            insights_btn.click(
                fn=generate_all_insights,
                inputs=df_state,
                outputs=[top_performers, bottom_performers, anomalies_output],
            )

    return demo


if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()