# Inscendia - Interactive Data Storyteller
<img src="https://raw.githubusercontent.com/kushagra-arya/Inscendia/refs/heads/main/data/Image%201.png">

![Inscendia](https://img.shields.io/badge/Inscendia-Data%20Storyteller-brightgreen)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0%2B-red)

## 📊 Overview

Inscendia is a powerful, interactive data visualization and analysis application built with Streamlit. It transforms raw data into compelling visual stories, enabling users to explore, clean, analyze, and visualize their datasets without writing code. From quick data exploration to creating beautiful interactive dashboards, Inscendia makes data storytelling effortless.

## ✨ Features

### 📥 Data Import
- Support for CSV and Excel files
- Automatic detection of data types
- Persistent data state management

### 🧹 Data Cleaning
- Comprehensive missing value handling
  - Drop null values (all or in selected columns)
  - Fill missing values with statistical measures (mean, median, mode)
  - Custom value replacement
  - Column-specific filling strategies for both numeric and categorical data
- Restore original dataset with a single click

### 📈 Data Visualization
- Interactive chart builder with multiple visualization types:
  - Bar charts with automatic grouping
  - Line and area charts for trend analysis
  - Scatter plots for relationship exploration
  - Histograms and distribution plots (box, violin)
  - Correlation heatmaps and pair plots
- Intelligent chart type recommendations based on data types
- Statistical validation to prevent misleading visualizations
- Educational guidance on best practices for data visualization

<img src="https://raw.githubusercontent.com/kushagra-arya/Inscendia/refs/heads/main/data/Image%202.png">

### 🔍 Data Analysis
- Automatic data profiling:
  - Summary statistics for numeric and categorical columns
  - Detailed data structure information
  - Missing value analysis
- Smart insights detection:
  - Outlier identification with statistical methods
  - Distribution skewness analysis
  - High correlation discovery
  - Data quality assessment

### 📌 Dashboard Creation
- Pin multiple charts to a customizable dashboard
- Automatic chart rendering based on saved configurations
- Responsive layout with consistent styling
- One-click dashboard reset

### 💾 Export Options
- Download original or processed datasets
- Export in CSV format

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/kushagra-arya/Inscendia.git
cd inscendia
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to `http://localhost:8501`

## 📋 Usage Guide

### Loading Data
1. Use the sidebar file uploader to import your CSV or Excel file
2. The app automatically loads and displays your data in various tabs

### Cleaning Data
1. Expand the "Handle Missing Values" section in the sidebar
2. Choose your preferred handling approach (drop or fill)
3. For filling values:
   - Select specific strategies for numeric columns (mean, median, zero)
   - Select specific strategies for categorical columns (mode, custom value)
   - Choose which columns to apply these strategies to
4. Click "Apply Changes" to process the data

### Creating Visualizations
1. Navigate to the "Interactive Chart" tab
2. Select a chart type from the sidebar
3. Choose appropriate columns for X-axis, Y-axis, and grouping (color)
4. Review the chart and any statistical warnings or suggestions
5. Pin useful charts to your dashboard for later reference

### Using the Dashboard
1. Check "Show Dashboard" in the sidebar to view your pinned charts
2. All charts update automatically when you modify your data
3. Use "Clear Dashboard" to remove all pinned charts

### Exporting Results
1. Expand the "Export Data" section in the sidebar
2. Choose to download either the original data or your cleaned/processed data

## 🔧 Technical Details

Inscendia is built with the following technologies:
- **Streamlit**: For the interactive web interface
- **Pandas**: For data manipulation and analysis
- **Plotly**: For interactive charts and visualizations
- **Seaborn/Matplotlib**: For statistical visualizations
- **NumPy**: For numerical operations

The application utilizes Streamlit's session state management to preserve data and user selections between interactions, creating a seamless user experience.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📬 Contact

For questions or feedback, please [open an issue](https://github.com/kushagra-arya/Inscendia/issues) or contact [kushagraarya1801@gmail.com](mailto:kushagraarya1801@gmail.com).

---

<p align="center">
  Made with ❤️ for data enthusiasts and storytellers
</p>
