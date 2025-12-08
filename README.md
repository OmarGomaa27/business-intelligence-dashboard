# Business Intelligence Dashboard

A modular, interactive Business Intelligence dashboard built with Gradio.
The application enables users to upload datasets, generate descriptive statistics, apply filters, create visualizations, and obtain automated insights through a browser-based interface.

**Author:** Omar Gomaa
**GitHub:** [https://github.com/OmarGomaa27/business-intelligence-dashboard](https://github.com/OmarGomaa27/business-intelligence-dashboard)

---

## Project Overview

This dashboard provides a complete workflow for basic business data exploration and analysis.
The system includes:

* Automated data profiling
* Statistical summaries and data validation
* Interactive filtering with multiple filter types
* Configurable visualizations
* Automated insight generation
* Data and chart export functionality

Designed for general business analytics tasks such as sales analysis, customer segmentation, and operational reporting.

---

## Features

### Data Upload and Validation

* Support for CSV and Excel (`.xlsx`, `.xls`) files
* Automatic type inference (numeric, categorical, datetime)
* Data preview with structural information
* Flexible date parsing
* Error messages for unsupported formats or invalid input

### Data Profiling and Statistics

* Numeric summaries (mean, median, quartiles, standard deviation)
* Categorical summaries (unique values and most frequent values)
* Missing value reporting
* Correlation matrix for numerical fields

### Interactive Filtering

* Categorical filtering 
* Numeric filtering through minimum/maximum value ranges
* Date range filtering using textual date inputs
* Real-time updates to row counts and previews
* Full filter reset functionality

### Visualizations

Five visualization types:

1. Time series plots with aggregation functions
2. Histogram or boxplot distributions
3. Category aggregation bar charts
4. Scatter plots for variable comparison
5. Correlation heatmaps

All charts include:

* Consistent styling
* Grid lines and readable axes
* Support for exporting figures as PNG

### Insight Generation and Export

Automated insights include:

* Top and bottom performers
* Missing data summaries
* Outlier detection using a standard deviation-based heuristic
* Basic date range insights
* Overall dataset summary

Export features:

* Filtered dataset export as CSV
* Visualization export as PNG

---

## Quick Start

### Installation

```bash
git clone https://github.com/OmarGomaa27/business-intelligence-dashboard.git
cd business-intelligence-dashboard

pip install -r requirements.txt
python app.py
```

The dashboard will open at:
`http://127.0.0.1:7860`

### Workflow

1. Upload a CSV or Excel file
2. View dataset statistics
3. Apply filters
4. Generate visualizations
5. Review automated insights

---

## Project Structure

```
business-intelligence-dashboard/
│
├── app.py                      # Gradio UI 
├── data_processor.py           # Data loading, cleaning, profiling
├── visualizations.py           # Visualization utilities
├── insights.py                 # Automated insight generation
├── utils.py                    # Helper functions
├── requirements.txt            # Dependencies
├── README.md                   # Documentation
└── .gitignore
```

---

## Technical Stack

| Component           | Technology          | Purpose                |
| ------------------- | ------------------- | ---------------------- |
| UI Framework        | Gradio 4.x          | Web interface          |
| Data Processing     | pandas 2.x          | Data manipulation      |
| Visualization       | matplotlib, seaborn | Chart generation       |
| Numerical Computing | NumPy               | Statistical operations |
| Language            | Python 3.8+         | Core implementation    |

---

## Example Use Cases

### Sales Data Analysis

* Upload transaction data
* Filter by categories or date ranges
* Plot sales trends or category totals
* Identify top-performing products

### Retail Store Analysis

* Compare store-level metrics
* Detect anomalies in sales distribution
* Analyze temporal trends

### Customer Analysis

* Segment customers
* Inspect numeric distributions (e.g., order counts or spending)
* Identify high-activity or low-activity segments

---


GitHub: [https://github.com/OmarGomaa27](https://github.com/OmarGomaa27)
Repository: [https://github.com/OmarGomaa27/business-intelligence-dashboard](https://github.com/OmarGomaa27/business-intelligence-dashboard)
