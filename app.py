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

Author: Omar Gomaa
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
    """Construct the full multi-tab Business Intelligence Dashboard user interface."""

    with gr.Blocks(theme=gr.themes.Soft()) as demo:

        gr.Markdown("# Business Intelligence Dashboard")

        # Global dataframe stored in application state
        df_state = gr.State(value=None)

        file_input = gr.File(label="Upload CSV or Excel File")

        # ===============================================================
        # 1. DATA UPLOAD TAB
        # ===============================================================
        with gr.Tab("Data Upload"):
            gr.Markdown("### Upload and Preview Dataset")

            basic_info_output = gr.JSON(label="Dataset Information")
            preview_output = gr.DataFrame(label="Data Preview")

            def handle_upload(file):
                """Load dataset, return metadata and preview."""
                if file is None:
                    return None, {}, None

                df = load_data(file)
                info = get_basic_info(df)
                preview = preview_data(df)
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

            stats_button = gr.Button("Generate Statistics")

            numeric_output = gr.DataFrame(label="Numeric Summary")
            categorical_output = gr.JSON(label="Categorical Summary")
            missing_output = gr.JSON(label="Missing Values")
            corr_output = gr.DataFrame(label="Correlation Matrix")

            def generate_statistics(df):
                """Compute summary statistics for currently loaded dataset."""
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
                # Left Column: Filter Controls
                # -------------------------------------------------------
                with gr.Column(scale=1):
                    filter_load_btn = gr.Button("Load Filter Options", variant="secondary")
                    
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
                    clear_btn = gr.Button("Clear Filters")

                # -------------------------------------------------------
                # Right Column: Filter Results
                # -------------------------------------------------------
                with gr.Column(scale=2):
                    row_count = gr.Markdown("**Click 'Load Filter Options' to begin**")
                    filtered_data = gr.DataFrame(interactive=False)

            # -----------------------------------------------------------
            # Populate selectable filter values based on dataset
            # -----------------------------------------------------------
            def setup_filters(df):
                if df is None:
                    return (
                        gr.update(choices=[]),
                        gr.update(choices=[]),
                        gr.update(choices=[]),
                        "**Upload a file first**",
                        None,
                    )

                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                date_cols = [col for col in df.columns if "datetime" in str(df[col].dtype)]

                return (
                    gr.update(choices=cat_cols, value=None),
                    gr.update(choices=numeric_cols, value=None),
                    gr.update(choices=date_cols, value=None),
                    f"**{len(df):,} rows** - Select filters and click Apply",
                    df.head(100),
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

            # -----------------------------------------------------------
            # Update available category values when user selects a column
            # -----------------------------------------------------------
            def update_cat_values(df, col):
                if df is None or col is None:
                    return gr.update(choices=[], value=[])

                values = sorted(df[col].dropna().astype(str).unique().tolist())
                return gr.update(choices=values, value=[])

            cat_column.change(
                fn=update_cat_values,
                inputs=[df_state, cat_column],
                outputs=cat_values,
            )

            # -----------------------------------------------------------
            # Apply all user-selected filters
            # -----------------------------------------------------------
            def apply_filters(df, cat_col, cat_vals, num_col, n_min, n_max, date_col, d_start, d_end):
                if df is None:
                    return "**Upload a file first**", None

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
                    if d_start and d_start.strip():
                        try:
                            start_dt = pd.to_datetime(d_start.strip())
                            filtered = filtered[filtered[date_col] >= start_dt]
                        except:
                            pass
                    if d_end and d_end.strip():
                        try:
                            end_dt = pd.to_datetime(d_end.strip()) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                            filtered = filtered[filtered[date_col] <= end_dt]
                        except:
                            pass

                total = len(df)
                count = len(filtered)

                return f"**{count:,} of {total:,} rows** match your filters", filtered.head(100)

            apply_btn.click(
                fn=apply_filters,
                inputs=[df_state, cat_column, cat_values, num_column, num_min, num_max, date_column, date_start, date_end],
                outputs=[row_count, filtered_data],
            )

            # -----------------------------------------------------------
            # Clear all filters and reset view
            # -----------------------------------------------------------
            def clear_filters(df):
                if df is None:
                    return (
                        None, [], None, None, None, None, "", "",
                        "**Upload a file first**",
                        None,
                    )

                return (
                    None, [], None, None, None, None, "", "",
                    f"**{len(df):,} rows** - Select filters and click Apply",
                    df.head(100),
                )

            clear_btn.click(
                fn=clear_filters,
                inputs=df_state,
                outputs=[
                    cat_column, cat_values,
                    num_column, num_min, num_max,
                    date_column, date_start, date_end,
                    row_count, filtered_data,
                ],
            )

        # ===============================================================
        # 4. VISUALIZATIONS TAB
        # ===============================================================
        with gr.Tab("Visualizations"):
            gr.Markdown("### Data Visualizations")
            
            viz_load_btn = gr.Button("Load Visualization Options", variant="secondary")

            with gr.Tabs():

                # --- Time Series ---
                with gr.Tab("Time Series"):
                    gr.Markdown("**Trends Over Time**")
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

                # --- Distribution ---
                with gr.Tab("Distribution"):
                    gr.Markdown("**Distribution of Values**")
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

                # --- Category Analysis ---
                with gr.Tab("Category Analysis"):
                    gr.Markdown("**Analysis by Category**")
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

                # --- Scatter & Correlation ---
                with gr.Tab("Scatter & Correlation"):
                    gr.Markdown("**Relationships Between Variables**")
                    with gr.Row():
                        scatter_x = gr.Dropdown(label="X Axis", choices=[], interactive=True)
                        scatter_y = gr.Dropdown(label="Y Axis", choices=[], interactive=True)
                    with gr.Row():
                        scatter_btn = gr.Button("Scatter Plot", variant="primary")
                        corr_btn = gr.Button("Correlation Heatmap", variant="secondary")
                    scatter_plot = gr.Plot()

            # Populate dropdowns for visualizations
            def setup_viz_dropdowns(df):
                if df is None:
                    empty = gr.update(choices=[])
                    return [empty] * 7

                numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                date_cols = [c for c in df.columns if "datetime" in str(df[c].dtype)]

                return (
                    gr.update(choices=date_cols),      # ts_date_col
                    gr.update(choices=numeric_cols),   # ts_value_col
                    gr.update(choices=numeric_cols),   # dist_col
                    gr.update(choices=cat_cols),       # cat_viz_col
                    gr.update(choices=numeric_cols),   # cat_value_col
                    gr.update(choices=numeric_cols),   # scatter_x
                    gr.update(choices=numeric_cols),   # scatter_y
                )

            file_input.change(
                fn=setup_viz_dropdowns,
                inputs=df_state,
                outputs=[ts_date_col, ts_value_col, dist_col, cat_viz_col, cat_value_col, scatter_x, scatter_y],
            )
            
            viz_load_btn.click(
                fn=setup_viz_dropdowns,
                inputs=df_state,
                outputs=[ts_date_col, ts_value_col, dist_col, cat_viz_col, cat_value_col, scatter_x, scatter_y],
            )

            # --- Visualization functions ---

            def create_time_series(df, date_col, value_col, agg):
                if df is None or not date_col or not value_col:
                    return None

                import matplotlib.pyplot as plt

                temp = df.copy()
                temp["_date"] = pd.to_datetime(temp[date_col]).dt.to_period("D").astype(str)

                if agg == "sum":
                    grouped = temp.groupby("_date")[value_col].sum()
                elif agg == "mean":
                    grouped = temp.groupby("_date")[value_col].mean()
                elif agg == "count":
                    grouped = temp.groupby("_date")[value_col].count()
                else:
                    grouped = temp.groupby("_date")[value_col].median()

                fig, ax = plt.subplots(figsize=(10, 5))
                grouped.plot(ax=ax)
                ax.set_title(f"{value_col} ({agg}) Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel(f"{value_col} ({agg})")
                plt.xticks(rotation=45)
                plt.tight_layout()
                return fig

            ts_btn.click(
                fn=create_time_series,
                inputs=[df_state, ts_date_col, ts_value_col, ts_agg],
                outputs=ts_plot,
            )

            def create_distribution(df, col, chart_type):
                if df is None or not col:
                    return None

                import matplotlib.pyplot as plt

                fig, ax = plt.subplots(figsize=(10, 5))

                if chart_type == "histogram":
                    df[col].hist(ax=ax, bins=50, edgecolor="black")
                    ax.set_xlabel(col)
                    ax.set_ylabel("Frequency")
                else:
                    df.boxplot(column=col, ax=ax)

                ax.set_title(f"Distribution of {col}")
                plt.tight_layout()
                return fig

            dist_btn.click(
                fn=create_distribution,
                inputs=[df_state, dist_col, dist_type],
                outputs=dist_plot,
            )

            def create_category_chart(df, cat_col, value_col, agg):
                if df is None or not cat_col or not value_col:
                    return None

                import matplotlib.pyplot as plt

                if agg == "sum":
                    grouped = df.groupby(cat_col)[value_col].sum()
                elif agg == "mean":
                    grouped = df.groupby(cat_col)[value_col].mean()
                elif agg == "count":
                    grouped = df.groupby(cat_col)[value_col].count()
                else:
                    grouped = df.groupby(cat_col)[value_col].median()

                grouped = grouped.sort_values(ascending=False).head(20)

                fig, ax = plt.subplots(figsize=(10, 6))
                grouped.plot(kind="bar", ax=ax, edgecolor="black")
                ax.set_title(f"{value_col} ({agg}) by {cat_col}")
                ax.set_xlabel(cat_col)
                ax.set_ylabel(f"{value_col} ({agg})")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                return fig

            cat_btn.click(
                fn=create_category_chart,
                inputs=[df_state, cat_viz_col, cat_value_col, cat_agg],
                outputs=cat_plot,
            )

            def create_scatter(df, x_col, y_col):
                if df is None or not x_col or not y_col:
                    return None

                import matplotlib.pyplot as plt

                sample = df if len(df) < 5000 else df.sample(5000)

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(sample[x_col], sample[y_col], alpha=0.5, s=10)
                ax.set_title(f"{y_col} vs {x_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                plt.tight_layout()
                return fig

            scatter_btn.click(
                fn=create_scatter,
                inputs=[df_state, scatter_x, scatter_y],
                outputs=scatter_plot,
            )

            def create_correlation_heatmap(df):
                if df is None:
                    return None

                import matplotlib.pyplot as plt
                import seaborn as sns

                numeric_df = df.select_dtypes(include=["number"])
                if numeric_df.empty:
                    return None

                corr = numeric_df.corr()

                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax, fmt=".2f")
                ax.set_title("Correlation Heatmap")
                plt.tight_layout()
                return fig

            corr_btn.click(
                fn=create_correlation_heatmap,
                inputs=[df_state],
                outputs=scatter_plot,
            )

        # ===============================================================
        # 5. INSIGHTS TAB
        # ===============================================================
        with gr.Tab("Insights"):
            gr.Markdown("### Insights (Coming Soon)")

    return demo


if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()