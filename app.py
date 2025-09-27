import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import io
import os
import base64
from io import BytesIO

st.set_page_config(page_title="Inscendia", layout="wide")
st.title("Inscendia")
st.markdown("> Let truth in numbers speak through your stories.")
if 'original_df' not in st.session_state:
    st.session_state.original_df = None
if 'current_df' not in st.session_state:
    st.session_state.current_df = None
if 'dashboard_charts' not in st.session_state:
    st.session_state.dashboard_charts = []
if 'previous_file' not in st.session_state:
    st.session_state.previous_file = None
def reset_session_state():
    st.session_state.original_df = None
    st.session_state.current_df = None
    st.session_state.dashboard_charts = []

uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
df = None
if st.session_state.previous_file is not None and uploaded_file is None:
    reset_session_state()
    st.session_state.previous_file = None
if uploaded_file and st.session_state.previous_file != uploaded_file:
    reset_session_state()
    st.session_state.previous_file = uploaded_file

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    if st.session_state.original_df is None:
        st.session_state.original_df = df.copy()
        st.session_state.current_df = df.copy()
    
    df = st.session_state.current_df.copy()
    
    with st.sidebar.expander("🛠️ Handle Missing Values", expanded=False):
        handling_approach = st.selectbox(
            "Missing Value Handling Approach",
            ["No handling", "Drop null values", "Fill missing values"]
        )
        
        df_handled = df.copy()
        
        if handling_approach == "Drop null values":
            drop_option = st.radio("Drop option", ["Drop all rows with any null", "Drop rows with nulls in selected columns"])
            if drop_option == "Drop rows with nulls in selected columns":
                columns_to_check = st.multiselect("Select columns to check for nulls", df.columns.tolist())
            
        elif handling_approach == "Fill missing values":
            st.subheader("Numeric columns")
            num_strategy = st.selectbox("Fill numeric columns with", ["None", "Mean", "Median", "Zero"])
            
            # Option to select specific numeric columns
            num_fill_option = st.radio("Apply to numeric columns", ["Apply to all numeric columns", "Apply to selected numeric columns"])
            if num_fill_option == "Apply to selected numeric columns":
                numeric_cols_list = df.select_dtypes(include='number').columns.tolist()
                selected_num_cols = st.multiselect("Select numeric columns to fill", numeric_cols_list, 
                                                 default=[col for col in numeric_cols_list if df[col].isna().any()])
            
            st.subheader("Categorical columns")
            cat_strategy = st.selectbox("Fill categorical columns with", ["None", "Mode", "Custom value"])
            
            # Option to select specific categorical columns
            cat_fill_option = st.radio("Apply to categorical columns", ["Apply to all categorical columns", "Apply to selected categorical columns"])
            if cat_fill_option == "Apply to selected categorical columns":
                cat_cols_list = df.select_dtypes(include=['object', 'category']).columns.tolist()
                selected_cat_cols = st.multiselect("Select categorical columns to fill", cat_cols_list,
                                                 default=[col for col in cat_cols_list if df[col].isna().any()])
            
            if cat_strategy == "Custom value":
                custom_fill = st.text_input("Custom fill value", "missing")
        
        if st.button("Apply Changes"):
            if handling_approach == "No handling":
                pass   
            
            elif handling_approach == "Drop null values":
                if drop_option == "Drop all rows with any null":
                    df_handled = df_handled.dropna()
                else:
                    if columns_to_check:
                        df_handled = df_handled.dropna(subset=columns_to_check)
            
            elif handling_approach == "Fill missing values":
                if num_strategy != "None":
                    # Determine which columns to process
                    if num_fill_option == "Apply to all numeric columns":
                        num_cols = df_handled.select_dtypes(include='number').columns
                    else:
                        # Use only selected numeric columns if they were specified
                        num_cols = selected_num_cols if 'selected_num_cols' in locals() and selected_num_cols else []
                    
                    if len(num_cols) > 0:
                        if num_strategy == "Mean":
                            # Calculate mean for each column individually
                            for col in num_cols:
                                mean_val = df_handled[col].mean()
                                df_handled[col] = df_handled[col].fillna(mean_val)
                        elif num_strategy == "Median":
                            # Calculate median for each column individually
                            for col in num_cols:
                                median_val = df_handled[col].median()
                                df_handled[col] = df_handled[col].fillna(median_val)
                        elif num_strategy == "Zero":
                            df_handled[num_cols] = df_handled[num_cols].fillna(0)
                
                if cat_strategy != "None":
                    # Determine which categorical columns to process
                    if cat_fill_option == "Apply to all categorical columns":
                        cat_cols = df_handled.select_dtypes(include=['object', 'category']).columns
                    else:
                        # Use only selected categorical columns if they were specified
                        cat_cols = selected_cat_cols if 'selected_cat_cols' in locals() and selected_cat_cols else []
                    
                    if len(cat_cols) > 0:
                        if cat_strategy == "Mode":
                            for col in cat_cols:
                                modes = df_handled[col].mode()
                                if not modes.empty:
                                    df_handled[col] = df_handled[col].fillna(modes[0])
                        elif cat_strategy == "Custom value":
                            df_handled[cat_cols] = df_handled[cat_cols].fillna(custom_fill)
            
            st.session_state.current_df = df_handled.copy()
            df = df_handled
            st.success("Missing value handling applied!")
    
    if st.sidebar.button("Reset to Original Dataset"):
        st.session_state.current_df = st.session_state.original_df.copy()
        df = st.session_state.current_df.copy()
        st.success("Dataset reset to original state!")
    data_tab1, data_tab2, data_tab3, data_tab4, data_tab5 = st.tabs(["Raw Data", "Statistical Summary", "Data Summary", "Smart Insights", "Interactive Chart"])
    
    with data_tab1:
        st.subheader("Raw Data")
        st.dataframe(df)
    
    with data_tab2:
        st.subheader("Statistical Summary")
        
        with st.expander("Numeric Columns Statistics", expanded=True):
            numeric_desc = df.describe().T
            st.write(numeric_desc)
        
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            with st.expander("Categorical Columns Statistics", expanded=True):
                st.write(df.describe(include=['object', 'category']).T)
    
    with data_tab3:
        st.subheader("Data Summary")
        cols = df.columns.tolist()
        dtypes = df.dtypes.tolist()
        non_null = df.count().tolist()
        info_dict = {
            "Column": cols,
            "Non-Null Count": [f"{nn}/{len(df)}" for nn in non_null],
            "Dtype": [str(dt) for dt in dtypes],
            "Missing": [(len(df) - nn) for nn in non_null]
        }
        info_df = pd.DataFrame(info_dict)
        st.table(info_df)
        
        buffer = io.StringIO()
        df.info(buf=buffer)
    
    with data_tab4:
        st.subheader("💡 Smart Insights")
        
        missing_cols = [col for col in df.columns if df[col].isna().any()]
        total_missing = df.isna().sum().sum()
        total_data_points = df.shape[0] * df.shape[1]
        missing_pct = (total_missing / total_data_points) * 100 if total_data_points > 0 else 0
    
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        outlier_cols = []
        
        if len(numeric_cols) > 0:
            for col in numeric_cols:
                try:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outlier_count = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                    if outlier_count > 0:
                        outlier_pct = (outlier_count / len(df)) * 100
                        outlier_cols.append((col, outlier_count, outlier_pct))
                except:
                    continue
        
        skewed_cols = []
        for col in numeric_cols:
            try:
                skew = df[col].skew()
                if abs(skew) > 1: 
                    direction = "right" if skew > 0 else "left"
                    skewed_cols.append((col, skew, direction))
            except:
                continue
                
        high_correlations = []
        if len(numeric_cols) >= 2:  
            try:
                corr_matrix = df[numeric_cols].corr()
                corr_matrix = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                high_corr_pairs = [(i, j, corr_matrix.loc[i, j]) 
                                for i in corr_matrix.index 
                                for j in corr_matrix.columns 
                                if abs(corr_matrix.loc[i, j]) > 0.7] 
                
                high_corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                high_correlations = high_corr_pairs[:3]
            except:
                pass
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Dataset Overview")
            st.markdown(f"• **{df.shape[0]}** rows and **{df.shape[1]}** columns")
            st.markdown(f"• **{len(numeric_cols)}** numeric and **{len(df.select_dtypes(include=['object', 'category']).columns)}** categorical columns")
            
            if total_missing > 0:
                st.markdown(f"• **{total_missing}** missing values ({missing_pct:.1f}% of all data)")
                
                if missing_cols:
                    worst_col = max(missing_cols, key=lambda col: df[col].isna().sum())
                    worst_pct = df[worst_col].isna().mean() * 100
                    st.markdown(f"• Column '**{worst_col}**' has the most missing values: **{worst_pct:.1f}%**")
                    
            if high_correlations:
                st.markdown("#### 🔄 Variable Relationships")
                for i, (var1, var2, corr) in enumerate(high_correlations):
                    corr_type = "positive" if corr > 0 else "negative"
                    corr_strength = "strong" if abs(corr) > 0.8 else "moderate"
                    st.markdown(f"• **{corr_strength.title()} {corr_type}** correlation between '**{var1}**' and '**{var2}**' ({corr:.2f})")

                    if i == 0:
                        st.markdown(f"  *Suggestion: Create a scatter plot to visualize this relationship*")
        

        with col2:
            if outlier_cols:
                st.markdown("#### ⚠️ Potential Issues")
                st.markdown(f"• **{len(outlier_cols)}** columns have outliers")
                
                worst_outlier = max(outlier_cols, key=lambda x: x[1])
                st.markdown(f"• Column '**{worst_outlier[0]}**' has **{worst_outlier[1]}** outliers ({worst_outlier[2]:.1f}% of data)")
                
                if skewed_cols:
                    most_skewed = max(skewed_cols, key=lambda x: abs(x[1]))
                    st.markdown(f"• Column '**{most_skewed[0]}**' is {most_skewed[2]}-skewed (skew={most_skewed[1]:.2f})")
            else:
                st.markdown("#### ✓ Data Quality")
                st.markdown("• No significant outliers detected")
                if not missing_cols:
                    st.markdown("• No missing values in the dataset")
    
    st.sidebar.header("Chart Builder")
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    col_options = []
    for col in df.columns:
        if col in numeric_cols:
            col_options.append(f"{col} (numeric)")
        elif col in categorical_cols:
            col_options.append(f"{col} (categorical)")
        elif col in datetime_cols:
            col_options.append(f"{col} (date/time)")
        else:
            col_options.append(col)
    
    col_name_mapping = {option: option.split(" (")[0] for option in col_options}
    chart_type = st.sidebar.selectbox("Chart Type", ["Bar", "Line", "Area", "Scatter", "Histogram", "Box Plot", "Violin Plot", "Heatmap", "Pair Plot"])
    
    chart_descriptions = {
        "Bar": "Compares values across categories. Requires categorical X-axis or grouped numerical X-axis.",
        "Line": "Shows trends over time or continuous values. Best with numerical or datetime X-axis.",
        "Area": "Similar to line chart but with filled area below the line. Good for showing volume over time.",
        "Scatter": "Shows relationship between two numerical variables.",
        "Histogram": "Shows distribution of a single numerical variable.",
        "Box Plot": "Shows distribution statistics (median, quartiles, outliers).",
        "Violin Plot": "Shows distribution density and statistical summary. Requires numerical Y-axis.",
        "Heatmap": "Shows correlation between numerical variables.",
        "Pair Plot": "Shows pairwise relationships across multiple variables."
    }
    

    if chart_type == "Histogram":
        x_options = [col for col in col_options if col.split(" (")[0] in numeric_cols]
        if not x_options:
            st.sidebar.warning("⚠️ Histogram requires numerical variables. Your dataset has no numerical columns.")
            x_options = col_options  
    elif chart_type == "Scatter":
        x_options = [col for col in col_options if col.split(" (")[0] in numeric_cols]
        if not x_options:
            st.sidebar.warning("⚠️ Scatter plots work best with numerical X and Y variables.")
            x_options = col_options  
    elif chart_type == "Line":
        x_options = [col for col in col_options if col.split(" (")[0] in numeric_cols + datetime_cols]
        if not x_options:
            st.sidebar.warning("⚠️ Line charts work best with numerical or datetime X-axis.")
            x_options = col_options
    elif chart_type == "Heatmap" or chart_type == "Pair Plot":
        x_options = col_options
    else:
        x_options = col_options
    

    x_col_display = st.sidebar.selectbox("X Axis", x_options)
    x_col = col_name_mapping[x_col_display]
    if chart_type not in ["Histogram", "Pair Plot", "Heatmap"]:
        if chart_type == "Scatter":
            y_options = [col for col in col_options if col.split(" (")[0] in numeric_cols]
            if not y_options:
                st.sidebar.warning("⚠️ Scatter plots require numerical Y variable.")
                y_options = col_options  
        elif chart_type == "Box Plot":
            y_options = [col for col in col_options if col.split(" (")[0] in numeric_cols]
            if not y_options:
                st.sidebar.warning("⚠️ Box plots require numerical Y variable for distribution analysis.")
                y_options = col_options  
        else:
            y_options = col_options
        
        y_col_display = st.sidebar.selectbox("Y Axis", y_options)
        y_col = col_name_mapping[y_col_display] 
    else:
        y_col = None
    
    group_col_display = st.sidebar.selectbox("Group/Color", [None] + col_options)
    group_col = None if group_col_display is None else col_name_mapping[group_col_display]

    with data_tab5:
        st.subheader("Interactive Chart")
        fig = None
        chart_error = False
        st.info(chart_descriptions[chart_type])
        
        def is_valid_for_chart(chart_type, x_col, y_col=None):
            is_x_numeric = x_col in numeric_cols
            is_y_numeric = y_col in numeric_cols if y_col else False
            is_x_categorical = x_col in categorical_cols
            is_y_categorical = y_col in categorical_cols if y_col else False
            is_x_datetime = x_col in datetime_cols
            
            if chart_type == "Histogram" and not is_x_numeric:
                return False, "Histogram requires a numerical variable for the X-axis."
            elif chart_type == "Scatter" and (not is_x_numeric or not is_y_numeric):
                return False, "Scatter plots require numerical variables for both X and Y axes."
            elif chart_type == "Line" and not (is_x_numeric or is_x_datetime):
                return False, "Line charts work best with numerical or datetime X-axis."
            elif chart_type == "Area" and not (is_x_numeric or is_x_datetime):
                return False, "Area charts work best with numerical or datetime X-axis."
            elif chart_type == "Box Plot" and not is_y_numeric:
                return False, "Box plots require a numerical variable for the Y-axis."
            elif chart_type == "Violin Plot" and not is_y_numeric:
                return False, "Violin plots require a numerical variable for the Y-axis."
            return True, ""
        
        valid_chart, error_message = is_valid_for_chart(chart_type, x_col, y_col)
        
        if not valid_chart:
            st.warning(f"⚠️ {error_message}")
            st.info("The chart may not represent the data correctly. Consider selecting a different chart type or variables.")
            chart_error = True
        
        try:
            if chart_type == "Bar":
                if x_col in numeric_cols and df[x_col].nunique() > 15:
                    st.info("Tip: Bar charts work best with categorical variables or numeric variables with few unique values. Your selected X-axis has many unique values.")
                
                if y_col in numeric_cols:
                    grouped_df = df.groupby([x_col, group_col] if group_col else [x_col])[y_col].sum().reset_index()
                    fig = px.bar(grouped_df, x=x_col, y=y_col, color=group_col if group_col else None,
                                 error_y=None,
                                 title=f"Total {y_col} by {x_col}")
                else:
                    fig = px.bar(df, x=x_col, y=y_col, color=group_col if group_col else None, error_y=None)
                
                fig.update_traces(hovertemplate="%{y}<extra></extra>", marker_line_width=0)
            
            elif chart_type == "Line":
                if x_col in categorical_cols and df[x_col].nunique() > 20:
                    st.info("Tip: Line charts work best with ordered data (time series, sequential values). Your X-axis is categorical with many values.")
                fig = px.line(df, x=x_col, y=y_col, color=group_col if group_col else None)
            
            elif chart_type == "Area":
                if x_col in categorical_cols and df[x_col].nunique() > 20:
                    st.info("Tip: Area charts work best with ordered data (time series, sequential values). Your X-axis is categorical with many values.")
                fig = px.area(df, x=x_col, y=y_col, color=group_col if group_col else None)
            
            elif chart_type == "Scatter":
                if x_col in numeric_cols and y_col in numeric_cols:
                    fig = px.scatter(df, x=x_col, y=y_col, color=group_col if group_col else None)
                else:
                    st.warning("Scatter plots require numerical variables for both axes for proper statistical interpretation.")
                    fig = px.scatter(df, x=x_col, y=y_col, color=group_col if group_col else None)
            
            elif chart_type == "Histogram":
                if x_col in numeric_cols:
                    fig = px.histogram(df, x=x_col, color=group_col if group_col else None)
                else:
                    st.warning("Histograms should only be used with numerical variables.")

                    st.info("Showing a count plot instead, which is appropriate for categorical data.")
                    plt.figure(figsize=(10,6))
                    sns.countplot(data=df, x=x_col, hue=group_col)
                    st.pyplot(plt)
            
            elif chart_type == "Box Plot":
                if y_col in numeric_cols:
                    fig = px.box(df, x=x_col, y=y_col, color=group_col if group_col else None)
                else:
                    st.warning("Box plots require a numerical Y-variable to show distribution.")
                    fig = px.box(df, x=x_col, y=y_col, color=group_col if group_col else None)
                    
            elif chart_type == "Violin Plot":
                if y_col in numeric_cols:
                    fig = px.violin(df, x=x_col, y=y_col, color=group_col if group_col else None,
                                   box=True,
                                   points="all"
                                  )
                else:
                    st.warning("Violin plots require a numerical Y-variable to show distribution density.")
                    fig = px.violin(df, x=x_col, y=y_col, color=group_col if group_col else None)
            
            elif chart_type == "Heatmap":
                numeric_df = df.select_dtypes(include=['int64', 'float64'])
                if not numeric_df.empty:
                    if numeric_df.shape[1] < 2:
                        st.warning("Heatmap requires at least 2 numeric columns for correlation analysis.")
                    elif numeric_df.shape[1] > 20:
                        st.warning("Large heatmaps with many variables may be difficult to interpret.")
                    
                    plt.figure(figsize=(10,6))
                    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm')
                    st.pyplot(plt)
                else:
                    st.error("No numeric columns available for heatmap visualization.")
                    chart_error = True
            
            elif chart_type == "Pair Plot":
                if len(numeric_cols) == 0:
                    st.error("Pair plots require numerical variables. No numerical columns found in the dataset.")
                    chart_error = True
                elif len(numeric_cols) > 10:
                    st.warning(f"Dataset has {len(numeric_cols)} numerical columns, which would create a very large pair plot.")
                    st.info("Limiting to first 5 numerical columns for readability.")
                    selected_cols = numeric_cols[:5]
                    if group_col:
                        selected_cols.append(group_col)
                    plt.figure(figsize=(12, 8))
                    sns.pairplot(df[selected_cols], hue=group_col)
                    st.pyplot(plt)
                else:
                    selected_cols = numeric_cols.copy()
                    if group_col:
                        selected_cols.append(group_col)
                    plt.figure(figsize=(12, 8))
                    sns.pairplot(df[selected_cols], hue=group_col)
                    st.pyplot(plt)
        
        except Exception as e:
            st.error(f"Error generating chart: {str(e)}")
            st.info("This combination of variables and chart type may not be statistically appropriate. Try different variables or chart types.")
            chart_error = True
        
        with st.expander("📊 Chart Selection Guide"):
            st.markdown("""
            ### Statistical Visualization Best Practices
            
            Different chart types are designed for specific types of data and analyses:
            
            | Chart Type | Appropriate For | Not Appropriate For |
            |------------|-----------------|---------------------|
            | **Bar Chart** | Comparing values across categories | Continuous numerical data with many unique values |
            | **Line Chart** | Time series, trends over ordered variables | Unordered categorical variables |
            | **Area Chart** | Volume or cumulative values over time, stacked comparisons | Unordered data or too many categories (becomes cluttered) |
            | **Scatter Plot** | Relationships between two numerical variables | Categorical vs categorical relationships |
            | **Histogram** | Distribution of a single numerical variable | Categorical data or comparing multiple distributions |
            | **Box Plot** | Distribution statistics of numerical data (five-number summary) | Categorical data or when detailed distribution shape matters |
            | **Violin Plot** | Distribution shape and density of numerical data | Categorical data or very small sample sizes |
            | **Heatmap** | Correlation between multiple numerical variables | Non-numerical data |
            | **Pair Plot** | Exploring relationships between multiple numerical variables | Datasets with too many variables (becomes unreadable) |
            
            **Common Mistakes to Avoid:**
            * Using a line chart for unordered categorical data
            * Creating histograms of categorical variables
            * Using scatter plots for categorical vs categorical comparisons
            * Including too many variables in visualizations
            * Using violin plots with insufficient data (need enough points to estimate distribution)
            * Using area charts with too many overlapping categories
            """)
            
        if fig and not chart_error:
            unique_key = f"main_chart_{chart_type}_{x_col}_{y_col if y_col else 'none'}"
            st.plotly_chart(fig, use_container_width=True, key=unique_key)
            
            if st.button("📌 Pin to Dashboard"):
                chart_config = {
                    "type": chart_type,
                    "x_col": x_col,
                    "y_col": y_col,
                    "group_col": group_col,
                    "title": f"{chart_type} of {y_col if y_col else ''} by {x_col}"
                }
                st.session_state.dashboard_charts.append(chart_config)
                st.success(f"Chart pinned to dashboard! Total charts: {len(st.session_state.dashboard_charts)}")

    with st.sidebar.expander("Export Data", expanded=False):
        if st.session_state.original_df is not None:
            original_data = st.session_state.original_df.copy()
            original_csv = original_data.to_csv(index=False).encode('utf-8')
            st.download_button("Download Original Data", original_csv, file_name="original_data.csv")
        
        filtered_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Current Data", filtered_csv, file_name="current_data.csv")
else:
    st.info("Please upload a CSV or Excel file to begin.")

st.sidebar.markdown("---")
st.sidebar.header("📊 Dashboard")
show_dashboard = st.sidebar.checkbox("Show Dashboard", value=False)

if show_dashboard and st.session_state.dashboard_charts:
    st.markdown("---")
    st.header("📌 Your Dashboard")
    st.write(f"You have {len(st.session_state.dashboard_charts)} chart(s) pinned to your dashboard.")
    
    if len(st.session_state.dashboard_charts) > 0:
        charts_per_row = 2
        
        for i in range(0, len(st.session_state.dashboard_charts), charts_per_row):
            cols = st.columns(charts_per_row)
            
            for j in range(charts_per_row):
                idx = i + j
                if idx < len(st.session_state.dashboard_charts):
                    with cols[j]:
                        chart_config = st.session_state.dashboard_charts[idx]
                        st.subheader(chart_config["title"])
                        
                        chart_type = chart_config["type"]
                        x_col = chart_config["x_col"]
                        y_col = chart_config["y_col"]
                        group_col = chart_config["group_col"]
                        
                        if df is not None:
                            if chart_type == "Bar":
                                if y_col in numeric_cols:
                                    grouped_df = df.groupby([x_col, group_col] if group_col else [x_col])[y_col].sum().reset_index()
                                    fig = px.bar(grouped_df, x=x_col, y=y_col, color=group_col if group_col else None,
                                                title=f"Total {y_col} by {x_col}")
                                else:
                                    fig = px.bar(df, x=x_col, y=y_col, color=group_col if group_col else None)
                                fig.update_traces(hovertemplate="%{y}<extra></extra>", marker_line_width=0)
                            elif chart_type == "Line":
                                fig = px.line(df, x=x_col, y=y_col, color=group_col if group_col else None)
                            elif chart_type == "Area":
                                fig = px.area(df, x=x_col, y=y_col, color=group_col if group_col else None)
                            elif chart_type == "Scatter":
                                fig = px.scatter(df, x=x_col, y=y_col, color=group_col if group_col else None)
                            elif chart_type == "Histogram":
                                fig = px.histogram(df, x=x_col, color=group_col if group_col else None)
                            elif chart_type == "Box Plot":
                                fig = px.box(df, x=x_col, y=y_col, color=group_col if group_col else None)
                            elif chart_type == "Violin Plot":
                                fig = px.violin(df, x=x_col, y=y_col, color=group_col if group_col else None,
                                               box=True,
                                               points="all"
                                              )
                            
                            if fig:
                                unique_key = f"dash_chart_{idx}_{chart_type}_{x_col}_{y_col if y_col else 'none'}"
                                st.plotly_chart(fig, use_container_width=True, key=unique_key)
        if st.button("🗑️ Clear Dashboard"):
            st.session_state.dashboard_charts = []
            st.success("Dashboard cleared!")
            st.rerun()
else:
    if show_dashboard:
        st.markdown("---")
        st.header("📌 Your Dashboard")
        st.info("Pin some charts to your dashboard to see them here!")

st.markdown("---")
st.markdown("Project by Kushagra")