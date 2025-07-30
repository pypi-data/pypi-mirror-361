"""
Utility class that provides various data visualization functions.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import traceback
from typing import Dict, List, Tuple, Any, Union, Optional
from pm_studio_mcp.config import config

def safe_read_excel(file_path, engine_preference=None):
    """
    This function replaces the original safe_read_excel functionality.
    It now returns an error message for Excel files and recommends using CSV instead.
    
    Args:
        file_path (str): Path to the file
        engine_preference (str, optional): Not used, kept for backward compatibility
        
    Returns:
        tuple: (dataframe, error_message)
            - dataframe: None for Excel files, Pandas DataFrame for CSV files
            - error_message: Error message for Excel files, None for CSV files
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Attempting to read file: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return None, f"File not found: {file_path}"
        
    # Check if file has Excel extension
    if file_path.lower().endswith('.xlsx') or file_path.lower().endswith('.xls'):
        error_message = f"Excel files are not supported. Please convert '{file_path}' to CSV format and try again."
        logger.error(f"Excel files not supported: {file_path}")
        return None, error_message
    
    # If it's a CSV file, try to read it
    if file_path.lower().endswith('.csv'):
        try:
            df = pd.read_csv(file_path)
            # Global dropna() - Remove rows and columns with NaN values to prevent errors
            df = df.dropna()
            logger.debug(f"Successfully read CSV file: {file_path}, shape after dropna(): {df.shape}")
            return df, None
        except Exception as e:
            error_msg = f"Failed to read CSV file: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    # If it's not CSV, return an error
    return None, f"Unsupported file format: {file_path}. Please use CSV files."

class DataVisualizationUtils:
    """
    A utility class that provides various data visualization functions.
    Supports generating charts from different data sources (dictionaries, CSV files)
    and different chart types (pie charts, bar charts, line charts, scatter plots).
    Note: Excel files are not supported. Please use CSV format instead.
    
    Includes support for McKinsey-style visualization with clear, professional designs
    and data labels for better readability and interpretation.
    
    Generate data visualizations using the DataVisualizationUtils unified chart generation interface.
    
    Args:
        visualization_type: Type of visualization to generate ('bar', 'line', 'pie', 'scatter')
        data_source: Path to the data source file (.csv or .xlsx), or a dictionary of data
        chart_options: Dictionary containing options for the chart:
            - title: Chart title (optional, defaults to a suitable title based on chart type)
            - working_path: Directory to save the output chart (optional, defaults to WORKING_PATH)
            - filename: Name for the output file (optional, defaults to a suitable name based on chart type)
            - figsize: Figure size as a tuple of (width, height) in inches (optional)
            - dpi: Resolution in dots per inch (optional)
            - Various chart-specific parameters:
                - For pie charts: category_column, value_column, autopct, startangle, etc.
                - For bar charts: x_column, y_column, orientation, etc.
                - For line charts: x_column, y_columns, markers, etc.
                - For scatter plots: x_column, y_column, hue_column, size_column, etc.
            
    Returns:
        dict: Dictionary containing:
            - success (bool): Whether the chart was generated successfully
            - output_path (str): Path to the generated chart file
            - message (str): Success or error message
            - data: The extracted data used to generate the chart
            - chart_type: The type of chart generated
            - timestamp: ISO format timestamp when the chart was generated
    """

    @staticmethod
    def convert_visualization_type(visualization_type: str) -> str:
        """
        Maps user-friendly visualization type names to their internal chart type equivalents.
        
        Args:
            visualization_type (str): User-friendly visualization type name 
                                     (e.g., 'bar_chart', 'line_chart', etc.)
            
        Returns:
            str: The corresponding internal chart type ('bar', 'line', 'pie', 'scatter')
        """
        # Map visualization_type to the expected chart_type format
        chart_type_map = {
            "bar_chart": "bar",
            "line_chart": "line", 
            "pie_chart": "pie",
            "scatter_plot": "scatter"
        }
        
        # Convert visualization_type to the format expected by generate_chart
        return chart_type_map.get(visualization_type, visualization_type)

    @staticmethod
    def clean_data_for_visualization(df, value_columns=None, exclude_phrases=None, replace_invalid_with=None, 
                                   process_percentages=True, process_currency=True, process_units=True):
        """
        Enhanced data cleaning for visualization with support for percentage values and more edge cases:
        1. Remove rows with missing values in key columns
        2. Filter out rows containing specific phrases
        3. Handle non-numeric values in numeric columns
        4. Convert strings that look like numbers (with commas) to actual numbers
        5. Process percentage values (remove % and convert to decimals)
        6. Process currency symbols and formatting
        7. Handle international number formats with different decimal separators
        8. Process units (K, M, B, etc. for thousands, millions, billions)
        
        Args:
            df (pd.DataFrame): DataFrame to clean
            value_columns (list, optional): Columns that should contain numeric values
            exclude_phrases (list, optional): List of phrases to filter out
            replace_invalid_with (float, optional): Value to replace invalid numeric values with (default: NaN)
            process_percentages (bool): Whether to convert percentage values (e.g., "45%") to decimals (0.45)
            process_currency (bool): Whether to remove currency symbols and convert to numeric
            process_units (bool): Whether to process K/M/B/T suffixes for thousands/millions/billions/trillions
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        import logging
        import re
        logger = logging.getLogger(__name__)
        logger.debug(f"clean_data_for_visualization: Starting enhanced data cleaning")
        
        if df is None:
            logger.warning("clean_data_for_visualization: Input DataFrame is None")
            return df
        
        if df.empty:
            logger.warning("clean_data_for_visualization: Input DataFrame is empty")
            return df
        
        logger.debug(f"clean_data_for_visualization: Initial DataFrame shape: {df.shape}")
        logger.debug(f"clean_data_for_visualization: Columns: {df.columns.tolist()}")
        logger.debug(f"clean_data_for_visualization: Value columns: {value_columns}")
        logger.debug(f"clean_data_for_visualization: Exclude phrases: {exclude_phrases}")
        
        # Make a copy to avoid modifying the original dataframe
        cleaned_df = df.copy()
        
        # 1. Handle excluded phrases if specified
        if exclude_phrases and isinstance(exclude_phrases, list):
            logger.debug(f"clean_data_for_visualization: Processing exclude_phrases: {exclude_phrases}")
            rows_before = len(cleaned_df)
            
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == 'object':  # Only apply to string columns
                    # Create a mask for rows to keep (those NOT containing excluded phrases)
                    mask = ~cleaned_df[col].astype(str).str.contains('|'.join(exclude_phrases), case=False, na=False)
                    cleaned_df = cleaned_df[mask]
            
            rows_after = len(cleaned_df)
            logger.debug(f"clean_data_for_visualization: Excluded phrases filter removed {rows_before - rows_after} rows")
        
        # 2. Handle numeric columns if specified
        if value_columns and isinstance(value_columns, list):
            logger.debug(f"clean_data_for_visualization: Processing value columns: {value_columns}")
            
            for col in value_columns:
                if col in cleaned_df.columns:
                    logger.debug(f"clean_data_for_visualization: Processing column '{col}' with dtype {cleaned_df[col].dtype}")
                    
                    # Only process string columns
                    if cleaned_df[col].dtype == 'object':
                        
                        # Store original values for logging conversion success
                        original_values = cleaned_df[col].copy()
                        
                        # Make a copy of the column for processing
                        processed_col = cleaned_df[col].astype(str)
                        
                        # Process percentage values if enabled
                        needs_percentage_scaling = False
                        if process_percentages:
                            # Check if column contains % symbols
                            has_percentages = processed_col.str.contains('%').any()
                            if has_percentages:
                                logger.debug(f"clean_data_for_visualization: Found percentage values in '{col}'")
                                
                                # Convert percentages to decimal values - remove % symbol
                                processed_col = processed_col.str.replace('%', '', regex=False)
                                
                                # Flag to check if we should divide by 100 later
                                # (only do this after numeric conversion)
                                needs_percentage_scaling = has_percentages
                        
                        # Process currency symbols if enabled
                        if process_currency:
                            # Common currency symbols
                            currency_symbols = ['$', '€', '£', '¥', '₹', '₽', '₩', '₪', 'zł', '฿', '₫', '₴', 'kr', 'Kč']
                            
                            # Check if column contains currency symbols
                            has_currency = False
                            for symbol in currency_symbols:
                                if processed_col.str.contains(re.escape(symbol)).any():
                                    has_currency = True
                                    break
                                    
                            if has_currency:
                                logger.debug(f"clean_data_for_visualization: Found currency symbols in '{col}'")
                                
                                # Remove currency symbols
                                for symbol in currency_symbols:
                                    processed_col = processed_col.str.replace(re.escape(symbol), '', regex=True)
                        
                        # Process unit suffixes like K, M, B, T if enabled
                        unit_multipliers = {}
                        if process_units:
                            # Check for K/M/B/T suffixes
                            k_pattern = r'(\d+\.?\d*)K'
                            m_pattern = r'(\d+\.?\d*)M'
                            b_pattern = r'(\d+\.?\d*)B'
                            t_pattern = r'(\d+\.?\d*)T'
                            
                            has_k = processed_col.str.contains(k_pattern, case=False, regex=True).any()
                            has_m = processed_col.str.contains(m_pattern, case=False, regex=True).any()
                            has_b = processed_col.str.contains(b_pattern, case=False, regex=True).any()
                            has_t = processed_col.str.contains(t_pattern, case=False, regex=True).any()
                            
                            if has_k or has_m or has_b or has_t:
                                logger.debug(f"clean_data_for_visualization: Found unit suffixes (K/M/B/T) in '{col}'")
                                
                                # Create a mask for each unit type
                                k_mask = processed_col.str.contains(k_pattern, case=False, regex=True)
                                m_mask = processed_col.str.contains(m_pattern, case=False, regex=True)
                                b_mask = processed_col.str.contains(b_pattern, case=False, regex=True)
                                t_mask = processed_col.str.contains(t_pattern, case=False, regex=True)
                                
                                # Extract values before the suffix
                                k_values = processed_col[k_mask].str.extract(k_pattern, flags=re.IGNORECASE)
                                m_values = processed_col[m_mask].str.extract(m_pattern, flags=re.IGNORECASE)
                                b_values = processed_col[b_mask].str.extract(b_pattern, flags=re.IGNORECASE)
                                t_values = processed_col[t_mask].str.extract(t_pattern, flags=re.IGNORECASE)
                                
                                # Store indices and multipliers for later application
                                if not k_values.empty:
                                    for idx, val in k_values.dropna().items():
                                        unit_multipliers[idx] = (float(val[0]), 1000)  # Multiply by 1,000
                                        
                                if not m_values.empty:
                                    for idx, val in m_values.dropna().items():
                                        unit_multipliers[idx] = (float(val[0]), 1000000)  # Multiply by 1,000,000
                                        
                                if not b_values.empty:
                                    for idx, val in b_values.dropna().items():
                                        unit_multipliers[idx] = (float(val[0]), 1000000000)  # Multiply by 1 billion
                                        
                                if not t_values.empty:
                                    for idx, val in t_values.dropna().items():
                                        unit_multipliers[idx] = (float(val[0]), 1000000000000)  # Multiply by 1 trillion
                                
                                # Remove the suffixes for numeric conversion
                                processed_col = processed_col.str.replace(r'K$|M$|B$|T$', '', regex=True)
                                
                                logger.debug(f"clean_data_for_visualization: Processed {len(unit_multipliers)} values with unit suffixes")
                        
                        # Remove thousand separators (commas)
                        processed_col = processed_col.str.replace(',', '', regex=False)
                        
                        # Handle spaces (e.g., "1 234.56")
                        processed_col = processed_col.str.replace(' ', '', regex=False)
                        
                        # Handle ranges (e.g., "10-15" or "5~10") - use average
                        range_pattern = r'(\d+\.?\d*)[~\-](\d+\.?\d*)'
                        has_ranges = processed_col.str.contains(range_pattern, regex=True).any()
                        range_averages = {}
                        
                        if has_ranges:
                            logger.debug(f"clean_data_for_visualization: Found range values in '{col}'")
                            range_mask = processed_col.str.contains(range_pattern, regex=True)
                            range_values = processed_col[range_mask].str.extract(range_pattern, expand=True)
                            
                            # Calculate averages for ranges and store for later application
                            for idx, (min_val, max_val) in range_values.dropna().iterrows():
                                try:
                                    min_num = float(min_val)
                                    max_num = float(max_val)
                                    average = (min_num + max_num) / 2
                                    range_averages[idx] = average
                                except (ValueError, TypeError):
                                    continue
                            
                            logger.debug(f"clean_data_for_visualization: Processed {len(range_averages)} range values")
                        
                        # Handle trailing symbols (e.g., "5+", "10*", "15^")
                        processed_col = processed_col.str.replace(r'[\+\*\^\#]$', '', regex=True)
                        
                        # Handle scientific notation in strings (e.g., "1.23e+6")
                        # This is handled automatically by pd.to_numeric, no special processing needed
                        
                        # Try to convert strings to numeric values
                        try:
                            numeric_values = pd.to_numeric(processed_col, errors='coerce')
                            
                            # Apply unit multipliers if any
                            if unit_multipliers:
                                for idx, (value, multiplier) in unit_multipliers.items():
                                    if idx in numeric_values.index:
                                        numeric_values.loc[idx] = value * multiplier
                            
                            # Apply range averages if any
                            if range_averages:
                                for idx, average in range_averages.items():
                                    if idx in numeric_values.index:
                                        numeric_values.loc[idx] = average
                            
                            # If we found percentages, divide by 100 to get decimal values
                            if needs_percentage_scaling:
                                numeric_values = numeric_values / 100
                                logger.debug(f"clean_data_for_visualization: Converted percentages to decimal values in '{col}'")
                            
                            # Log the conversion success rate
                            success_count = numeric_values.notna().sum()
                            total_count = len(numeric_values)
                            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
                            
                            logger.debug(f"clean_data_for_visualization: Converted column '{col}' to numeric with {success_rate:.2f}% success rate")
                            logger.debug(f"clean_data_for_visualization: {success_count}/{total_count} values successfully converted")
                            
                            # Apply the converted values to the cleaned dataframe
                            cleaned_df[col] = numeric_values
                            
                        except Exception as e:
                            logger.warning(f"clean_data_for_visualization: Error converting column '{col}' to numeric: {str(e)}")
                    
                    # Replace invalid values if specified
                    if replace_invalid_with is not None:
                        na_count = cleaned_df[col].isna().sum()
                        cleaned_df[col] = cleaned_df[col].fillna(replace_invalid_with)
                        logger.debug(f"clean_data_for_visualization: Replaced {na_count} NaN values in column '{col}' with {replace_invalid_with}")
                else:
                    logger.warning(f"clean_data_for_visualization: Specified value column '{col}' not found in DataFrame")
        
        logger.debug(f"clean_data_for_visualization: Final DataFrame shape: {cleaned_df.shape}")
        return cleaned_df
        
        logger.debug(f"clean_data_for_visualization: Final DataFrame shape: {cleaned_df.shape}")
        return cleaned_df
    
    # @staticmethod
    # def read_excel_file(file_path):
    #     """
    #     Safely read an Excel file with proper error handling and engine selection.
    #     Tries multiple engines and provides detailed error information.
        
    #     Args:
    #         file_path (str): Path to the Excel file
            
    #     Returns:
    #         tuple: (dataframe, error_message)
    #             - dataframe: Pandas DataFrame or None if error
    #             - error_message: None if successful, error string if failed
    #     """
    #     import logging
    #     logger = logging.getLogger(__name__)
    #     logger.debug(f"DataVisualizationUtils.read_excel_file: Reading file from {file_path}")
        
    #     if not os.path.exists(file_path):
    #         logger.error(f"DataVisualizationUtils.read_excel_file: File not found: {file_path}")
    #         return None, f"File not found: {file_path}"
            
    #     # Check if file has Excel extension
    #     if not (file_path.lower().endswith('.xlsx') or file_path.lower().endswith('.xls')):
    #         logger.error(f"DataVisualizationUtils.read_excel_file: Not an Excel file: {file_path}")
    #         return None, f"Not an Excel file: {file_path}"
        
    #     # Try with openpyxl first (for .xlsx files)
    #     try:
    #         logger.debug(f"DataVisualizationUtils.read_excel_file: Attempting with openpyxl engine")
    #         df = pd.read_excel(file_path, engine='openpyxl')
    #         logger.debug(f"DataVisualizationUtils.read_excel_file: Successfully read with openpyxl")
    #         return df, None  # Success
    #     except Exception as e1:
    #         # Log the error and try with xlrd
    #         logger.warning(f"DataVisualizationUtils.read_excel_file: openpyxl engine failed: {str(e1)}")
            
    #         try:
    #             # Try with xlrd (for .xls files)
    #             logger.debug(f"DataVisualizationUtils.read_excel_file: Attempting with xlrd engine")
    #             df = pd.read_excel(file_path, engine='xlrd')
    #             logger.debug(f"DataVisualizationUtils.read_excel_file: Successfully read with xlrd")
    #             return df, None  # Success
    #         except Exception as e2:
    #             # Both engines failed
    #             error_msg = f"Failed to read Excel file: {str(e2)}"
    #             logger.error(f"DataVisualizationUtils.read_excel_file: {error_msg}")
    #             return None, error_msg
    
    @staticmethod
    def apply_mckinsey_style():
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # Enhanced professional color palette - more vibrant but still professional
        # Combines McKinsey blue tones with complementary colors
        enhanced_colors = [
            "#2878BD",            "#FF8C00",            "#2CA02C",            "#9467BD",            "#D62728",            "#8C564B",            "#1F77B4",            "#FF7F0E",            "#17BECF",            "#E377C2",        ]
                         
        # Set color cycle
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=enhanced_colors)
        
        # Set fonts
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
        
        # Title and labels styling
        plt.rcParams['font.weight'] = 'bold'
        plt.rcParams['axes.titleweight'] = 'bold'
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelweight'] = 'bold'
        
        # Grid styling - horizontal only, light grey
        plt.rcParams['axes.grid'] = True
        plt.rcParams['axes.grid.axis'] = 'y'
        plt.rcParams['grid.color'] = '#DDDDDD'
        plt.rcParams['grid.linestyle'] = '--'
        
        # Remove top and right spines
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        
        # Figure background
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = '#F9F9F9'

  
    
   
    @staticmethod
    def generate_pie_chart_tool(
        data: Dict[str, Union[int, float]], 
        title: str = "User Feedback Distribution",
        filename: str = "piechart_output.jpg",
        figsize: Tuple[int, int] = (8, 8),
        dpi: int = 300,
        autopct: str = '%1.1f%%',
        startangle: int = 90,
        shadow: bool = False,
        explode: Optional[List[float]] = None,
        color_palette: str = 'Set2',
        working_path: str = None  # Kept for backward compatibility but no longer used
    ) -> Dict[str, Any]:
        """
        Generate a pie chart from dictionary data.
        
        Args:
            data (Dict[str, Union[int, float]]): Dictionary with categories as keys and values/counts as values
            title (str, optional): Title for the chart. Defaults to "User Feedback Distribution".
            filename (str, optional): Name of the output file. Defaults to "piechart_output.jpg".
            figsize (Tuple[int, int], optional): Figure size as (width, height). Defaults to (8, 8).
            dpi (int, optional): DPI (dots per inch) for the output image. Defaults to 300.
            autopct (str, optional): Format string for percentage labels. Defaults to '%1.1f%%'.
            startangle (int, optional): Starting angle for the first slice. Defaults to 90 (12 o'clock).
            shadow (bool, optional): Whether to draw a shadow beneath the pie. Defaults to False.
            explode (Optional[List[float]], optional): List of values to offset each wedge. Defaults to None.
            color_palette (str, optional): Seaborn color palette to use. Defaults to 'Set2'.
            working_path (str, optional): Deprecated. Path is now determined by _ensure_output_path().
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'success' (bool): Whether the chart was generated successfully
                - 'output_path' (str): Path to the generated chart file
                - 'message' (str): Success or error message
        """
        # Get path from config
        working_path = DataVisualizationUtils._ensure_output_path()
        
        print(f"DEBUG: generate_pie_chart_tool: Starting with {len(data) if isinstance(data, dict) else 'invalid'} categories")
        print(f"DEBUG: generate_pie_chart_tool: Working path: {working_path}")
        print(f"DEBUG: generate_pie_chart_tool: Title: {title}")
        print(f"DEBUG: generate_pie_chart_tool: Filename: {filename}")
        print(f"DEBUG: generate_pie_chart_tool: Shadow enabled: {shadow}")
        
        try:
            # Validate input data
            if not isinstance(data, dict) or not data:
                print("DEBUG: generate_pie_chart_tool: Invalid data - not a dict or empty")
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Input data must be a non-empty dictionary with categories and values."
                }
            
            # Apply McKinsey style
            print("DEBUG: generate_pie_chart_tool: Applying McKinsey style")
            DataVisualizationUtils.apply_mckinsey_style()
            
            # Create a figure with specified size
            plt.figure(figsize=figsize)
            
            # Extract categories and values
            categories = list(data.keys())
            values = list(data.values())
            print(f"DEBUG: generate_pie_chart_tool: Categories: {categories}")
            print(f"DEBUG: generate_pie_chart_tool: Values: {values}")
            
            # Handle explode parameter to ensure uniform pie appearance
            if explode is None:
                # Default to no explosion for uniform appearance unless specifically requested
                explode = [0] * len(values)
                print("DEBUG: generate_pie_chart_tool: Using no explode for uniform circle appearance")
            else:
                # If explode is provided, ensure it has the correct length
                if len(explode) != len(values):
                    # Truncate or extend explode list to match values length
                    if len(explode) > len(values):
                        explode = explode[:len(values)]
                        print("DEBUG: generate_pie_chart_tool: Truncated explode list")
                    else:
                        explode = explode + [0] * (len(values) - len(explode))
                        print("DEBUG: generate_pie_chart_tool: Extended explode list")
            
            # Get a color palette - either use provided one or default
            if isinstance(color_palette, str):
                try:
                    print(f"DEBUG: generate_pie_chart_tool: Using seaborn palette {color_palette}")
                    colors = sns.color_palette(color_palette, len(categories))
                except:
                    print("DEBUG: generate_pie_chart_tool: Falling back to Set2 palette")
                    colors = sns.color_palette('Set2', len(categories))
            else:
                # Use McKinsey enhanced colors
                print("DEBUG: generate_pie_chart_tool: Using McKinsey enhanced colors")
                enhanced_colors = [
                    "#2878BD", "#FF8C00", "#2CA02C", "#9467BD", "#D62728",
                    "#8C564B", "#1F77B4", "#FF7F0E", "#17BECF", "#E377C2"
                ]
                # If we need more colors than available, fall back to seaborn
                if len(categories) > len(enhanced_colors):
                    print("DEBUG: generate_pie_chart_tool: More categories than colors, using seaborn")
                    colors = sns.color_palette('Set2', len(categories))
                else:
                    print("DEBUG: generate_pie_chart_tool: Using subset of McKinsey colors")
                    colors = enhanced_colors[:len(categories)]
            
            # Create the pie chart with McKinsey styling
            print("DEBUG: generate_pie_chart_tool: Creating pie chart")
            # Configure shadow properties if enabled
            shadow_props = {}
            if shadow:
                shadow_props = {
                    'shadow': True,
                    'shadowprops': {'color': 'lightgrey', 'alpha': 0.5, 'linewidth': 0}
                }
            
            # Enhanced pie chart configuration for better geometry
            wedges, texts, autotexts = plt.pie(
                values,
                explode=explode,
                labels=categories,
                colors=colors,
                autopct=autopct,
                startangle=startangle,
                **shadow_props,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1.5, 'antialiased': True},
                textprops={'fontsize': 12, 'fontweight': 'bold'},
                radius=0.9,  # Slightly smaller radius for better proportions
                frame=False,  # No frame around the pie
                normalize=True  # Ensure values are normalized properly
            )
            
            # Customize percentage labels (autotexts)
            for autotext in autotexts:
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')
                autotext.set_color('white')
            
            # Add a title with McKinsey styling
            plt.title(title, fontsize=14, fontweight='bold', pad=20)
            
            # Ensure perfect circular appearance with adjusted settings
            plt.axis('equal')  # Equal aspect ratio ensures pie is circular
            plt.gca().set_aspect('equal')  # Reinforcing equal aspect
            
            # Ensure no distortion by setting proper figure size
            if figsize[0] != figsize[1]:
                # If width and height are not equal, log warning and adjust for next time
                print("DEBUG: generate_pie_chart_tool: Warning - For perfect circles, figure width should equal height")
            
            # Adjust layout with additional padding to prevent clipping
            plt.tight_layout(pad=1.5)
            
            # Generate a unique filename with timestamp
            unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
            
            # Create output directory only when saving the file
            DataVisualizationUtils._create_output_directory(working_path)
            
            # Save the pie chart with enhanced settings for better output quality
            output_file = os.path.join(working_path, unique_filename)
            print(f"DEBUG: generate_pie_chart_tool: Saving to {output_file}")
            
            # Save with improved parameters for better quality and geometry
            plt.savefig(
                output_file, 
                dpi=dpi, 
                bbox_inches='tight', 
                pad_inches=0.25,  # Add padding around the chart
                facecolor='white',  # Ensure white background
                edgecolor='none',  # No edge color around the figure
                transparent=False  # Non-transparent background
            )
            
            # Verify file was created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"DEBUG: generate_pie_chart_tool: File saved successfully, size: {file_size} bytes")
            else:
                print(f"DEBUG: generate_pie_chart_tool: File wasn't created: {output_file}")
                
            # Close the figure to free memory
            plt.close('all')
            
            return {
                "success": True,
                "output_path": output_file,
                "message": f"Pie chart saved at: {output_file}"
            }
        except Exception as e:
            import traceback
            print(f"DEBUG: generate_pie_chart_tool: Error: {str(e)}")
            print(f"DEBUG: generate_pie_chart_tool: Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "output_path": None,
                "message": f"Error generating pie chart: {str(e)}"
            }
            
    
    @staticmethod 
    def generate_pie_chart_from_csv(
        file_path: str, 
        category_column: str, 
        value_column: str, 
        title: str = "Data Distribution",
        filename: str = "piechart_from_csv.jpg",
        figsize: Tuple[int, int] = (8, 8),
        dpi: int = 300,
        autopct: str = '%1.1f%%',
        startangle: int = 90,
        shadow: bool = False,
        explode: Optional[List[float]] = None,
        color_palette: str = 'Set2'
    ) -> Dict[str, Any]:
        """
        Generate a pie chart from CSV file data
        
        Args:
            file_path (str): Path to the CSV file
            category_column (str): Name of the column containing categories
            value_column (str): Name of the column containing values
            title (str, optional): Title for the chart. Defaults to "Data Distribution".
            filename (str, optional): Name of the output file. Defaults to "piechart_from_csv.jpg".
            figsize (Tuple[int, int], optional): Figure size as (width, height). Defaults to (8, 8).
            dpi (int, optional): DPI (dots per inch) for the output image. Defaults to 300.
            autopct (str, optional): Format string for percentage labels. Defaults to '%1.1f%%'.
            startangle (int, optional): Starting angle for the first slice. Defaults to 90 (12 o'clock).
            shadow (bool, optional): Whether to draw a shadow beneath the pie. Defaults to False.
            explode (Optional[List[float]], optional): List of values to offset each wedge. Defaults to None.
            color_palette (str, optional): Seaborn color palette to use. Defaults to 'Set2'.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'success' (bool): Whether the chart was generated successfully
                - 'output_path' (str): Path to the generated chart file
                - 'message' (str): Success or error message
        """
        print(f"DEBUG: generate_pie_chart_from_csv: Starting with file {file_path}")
        print(f"DEBUG: generate_pie_chart_from_csv: Using columns: {category_column}, {value_column}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"DEBUG: generate_pie_chart_from_csv: File not found: {file_path}")
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: File not found: {file_path}"
                }
                
            # Read CSV file
            # Always make a copy to prevent modification of original data for multiple chart generation
            print(f"DEBUG: generate_pie_chart_from_csv: Reading CSV file")
            df = pd.read_csv(file_path, thousands=',').copy()
            # Global dropna() - Remove rows and columns with NaN values to prevent errors
            df = df.dropna()
            print(f"DEBUG: generate_pie_chart_from_csv: Read DataFrame with shape {df.shape} after dropna()")
            print(f"DEBUG: generate_pie_chart_from_csv: Columns: {df.columns.tolist()}")
            
            # Validate column names
            if category_column not in df.columns or value_column not in df.columns:
                print(f"DEBUG: generate_pie_chart_from_csv: Columns not found - Category: {category_column in df.columns}, Value: {value_column in df.columns}")
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: One or both columns ({category_column}, {value_column}) not found in the CSV file."
                }
            
            # Convert to dictionary
            data_dict = dict(zip(df[category_column], df[value_column]))
            print(f"DEBUG: generate_pie_chart_from_csv: Created dictionary with {len(data_dict)} items")
            sample_items = list(data_dict.items())[:min(5, len(data_dict))]
            print(f"DEBUG: generate_pie_chart_from_csv: Sample data: {sample_items}")
            
            # Generate pie chart using the existing method
            print(f"DEBUG: generate_pie_chart_from_csv: Calling generate_pie_chart_tool")
            
            # Ensure figsize is square for perfect circle geometry
            square_figsize = (figsize[0], figsize[0]) if figsize and figsize[0] == figsize[1] else (8, 8)
            if figsize and figsize[0] != figsize[1]:
                print(f"DEBUG: generate_pie_chart_from_csv: Adjusting to square figsize {square_figsize} for better circle geometry")
            
            # Generate pie chart using the existing method with improved parameters
            return DataVisualizationUtils.generate_pie_chart_tool(
                data=data_dict, 
                title=title,
                filename=filename,
                figsize=square_figsize,
                dpi=dpi,
                autopct=autopct,
                startangle=startangle,
                shadow=shadow,
                explode=explode,  # Now this will be kept as None unless explicitly provided
                color_palette=color_palette
                # working_path is not passed as it's handled internally by generate_pie_chart_tool
            )
        
        except Exception as e:
            import traceback
            print(f"DEBUG: generate_pie_chart_from_csv: Error: {str(e)}")
            print(f"DEBUG: generate_pie_chart_from_csv: Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "output_path": None,
                "message": f"Error processing CSV file: {str(e)}"
            }
    
    @staticmethod
    def generate_line_chart(data: dict, x_values: list, title: str = "Line Chart",
                           xlabel: str = "X Axis", ylabel: str = "Y Axis",
                           filename: str = "linechart_output.jpg", multiple_series: bool = False,
                           working_path: str = None):
        """
        Generate a line chart from dictionary data
        
        Args:
            data (dict): Dictionary with series names as keys and lists of values as values
                         If multiple_series is False, there should be only one key in the dictionary
            x_values (list): List of x-axis values (e.g. dates, categories)
            title (str): Title for the chart
            xlabel (str): Label for X axis
            ylabel (str): Label for Y axis
            filename (str): Name of the output file
            multiple_series (bool): Whether the data contains multiple series
            working_path (str, optional): Deprecated. Path is now determined by _ensure_output_path().
            
        Returns:
            dict: Result dictionary with success status, output path, and message
        """
        try:
            # Validate input data
            if not isinstance(data, dict) or not data:
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Input data must be a non-empty dictionary with series and values."
                }
                
            if not isinstance(x_values, list) or len(x_values) == 0:
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: X values must be a non-empty list."
                }
            
            # Apply McKinsey style
            DataVisualizationUtils.apply_mckinsey_style()
            
            # Create figure with a reasonable size
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Generate colors for multiple series - vibrant professional palette
            # Enhanced professional color palette - more vibrant but still professional
            enhanced_colors = [
                "#2878BD",  # McKinsey blue
                "#FF8C00",  # Dark orange
                "#2CA02C",  # Green
                "#9467BD",  # Purple
                "#D62728",  # Red
                "#8C564B",  # Brown
                "#1F77B4",  # Steel blue
                "#FF7F0E",  # Light orange
                "#17BECF",  # Cyan
                "#E377C2",  # Pink
            ]
            
            # If we need more colors than available, fall back to seaborn
            if len(data) > len(enhanced_colors):
                colors = sns.color_palette('viridis', len(data))
            else:
                colors = enhanced_colors[:len(data)]                # Plot each series with McKinsey-style formatting
            for i, (series_name, y_values) in enumerate(data.items()):
                if len(y_values) != len(x_values):
                    return {
                        "success": False,
                        "output_path": None,
                        "message": f"Error: Series '{series_name}' has {len(y_values)} values but there are {len(x_values)} x values."
                    }
                
                line = ax.plot(
                    x_values, 
                    y_values, 
                    marker='o',  # Data point markers
                    markersize=5,  # Slightly larger markers
                    linestyle='-', 
                    linewidth=2.5,  # Thicker lines for clarity
                    color=colors[i], 
                    label=series_name,
                    alpha=0.9  # Slight transparency
                )[0]
                
                # Add data point labels for ALL or most points
                if len(y_values) > 0:
                    # Find special points
                    max_idx = np.argmax(y_values)
                    min_idx = np.argmin(y_values)
                    
                    # For small datasets, show labels for all points
                    if len(y_values) <= 12:
                        indices_to_label = list(range(len(y_values)))
                    else:
                        # For medium datasets, show a significant portion of labels
                        if len(y_values) <= 20:
                            # Label about half the points
                            step = 2
                        else:
                            # For larger datasets, use an adaptive approach
                            step = max(2, len(y_values) // 10)
                        
                      # Generate indices with step
                        indices_to_label = list(range(0, len(y_values), step))
                        
                        # Always include max, min, first and last points
                        if max_idx not in indices_to_label:
                            indices_to_label.append(max_idx)
                        if min_idx not in indices_to_label:
                            indices_to_label.append(min_idx)
                        if 0 not in indices_to_label:
                            indices_to_label.append(0)
                        if len(y_values) - 1 not in indices_to_label:
                            indices_to_label.append(len(y_values) - 1)
                        
                        # Sort the indices
                        indices_to_label = sorted(set(indices_to_label))
                    
                    # Add labels for all selected points
                    for idx in indices_to_label:
                        # Different formatting for key points vs. regular points
                        is_special_point = (idx == max_idx or idx == min_idx or idx == 0 or idx == len(y_values) - 1)
                        
                        # Determine position to minimize overlap
                        # Create different positions for labels
                        position_type = idx % 4
                        
                        if idx == max_idx:
                            # Max value gets top position
                            xytext = (0, 10)
                            ha, va = 'center', 'bottom'
                        elif idx == min_idx:
                            # Min value gets bottom position
                            xytext = (0, -10)
                            ha, va = 'center', 'top'
                        elif idx == len(y_values) - 1:
                            # Last point gets right position
                            xytext = (8, 0)
                            ha, va = 'left', 'center'
                        elif position_type == 0:
                            # Top
                            xytext = (0, 8)
                            ha, va = 'center', 'bottom'
                        elif position_type == 1:
                            # Bottom
                            xytext = (0, -8)
                            ha, va = 'center', 'top'
                        elif position_type == 2:
                            # Right
                            xytext = (8, 0)
                            ha, va = 'left', 'center'
                        else:
                            # Left
                            xytext = (-8, 0)
                            ha, va = 'right', 'center'
                        
                        # All labels get a background for better visibility
                        # Special points get more prominent styling
                        fontsize = 9 if is_special_point else 8
                        fontweight = 'bold' if is_special_point else 'normal'
                        bbox_props = dict(
                            boxstyle="round,pad=0.3" if is_special_point else "round,pad=0.2",
                            fc="white",
                            alpha=0.8,
                            ec=colors[i],
                            lw=1 if is_special_point else 0.5
                        )
                        
                        # Format number to avoid showing .0 if it's a whole number
                        value = y_values[idx]
                        formatted_val = f'{value:,.0f}' if value == int(value) else f'{value:,.2f}'
                        
                        # Annotate the point
                        ax.annotate(
                            formatted_val,
                            xy=(x_values[idx], y_values[idx]),
                            xytext=xytext,
                            textcoords='offset points',
                            ha=ha, va=va,
                            fontsize=fontsize,
                            fontweight=fontweight,
                            color=colors[i],
                            bbox=bbox_props
                        )
            
            # Add labels and title with McKinsey styling
            ax.set_xlabel(xlabel, fontweight='bold', fontsize=11)
            ax.set_ylabel(ylabel, fontweight='bold', fontsize=11)
            ax.set_title(title, fontweight='bold', fontsize=14, pad=20)
            
            # Add legend if there are multiple series, with McKinsey styling
            if multiple_series or len(data) > 1:
                ax.legend(
                    loc='upper left',
                    frameon=True,
                    framealpha=0.95,
                    edgecolor='#DDDDDD'
                )
            
            # Rotate x-axis labels for better readability
            if len(x_values) > 5:
                plt.xticks(rotation=45, ha='right')
            
            # McKinsey style has clean horizontal grid lines only
            ax.yaxis.grid(True, linestyle='--', alpha=0.7, color='#DDDDDD')
            ax.set_axisbelow(True)  # Make sure grid is below data
            
            # Adjust layout to make sure everything fits
            plt.tight_layout()
            # Save the line chart
            working_path = DataVisualizationUtils._ensure_output_path()
            # Generate a unique filename with timestamp
            unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
            # Create output directory only when saving the file
            DataVisualizationUtils._create_output_directory(working_path)
            output_file = os.path.join(working_path, unique_filename)
            plt.savefig(output_file, dpi=300)
            plt.close()
            
            return {
                "success": True,
                "output_path": output_file,
                "message": f"Line chart saved at: {output_file}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error generating line chart: {str(e)}"
            }
    
    # Excel chart generation functions have been removed
    # The data visualization tool now only supports CSV files
    
    @staticmethod
    def generate_line_chart_from_csv(file_path: str, x_column: str, y_columns: list,
                                    title: str = "Line Chart", xlabel: str = "X Axis", 
                                    ylabel: str = "Y Axis", filename: str = "linechart_from_csv.jpg",
                                    working_path: str = None):
        """
        Generate a line chart from CSV file data
        
        Args:
            file_path (str): Path to the CSV file
            x_column (str): Name of the column containing x-axis values
            y_columns (list): List of column names containing y-axis values (series)
            title (str): Title for the chart
            xlabel (str): Label for X axis
            ylabel (str): Label for Y axis
            filename (str): Name of the output file
            working_path (str, optional): Deprecated. Path is now determined by _ensure_output_path().
            
        Returns:
            dict: Result dictionary with success status, output path, and message
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: File not found: {file_path}"
                }
                
            # Read CSV file with comma as thousands separator
            # Always make a copy to prevent modification of original data for multiple chart generation
            df = pd.read_csv(file_path, thousands=',').copy()
            # Global dropna() - Remove rows and columns with NaN values to prevent errors
            df = df.dropna()
            
            # Validate column names
            if x_column not in df.columns:
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: X column '{x_column}' not found in the CSV file."
                }
                
            for col in y_columns:
                if col not in df.columns:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": f"Error: Y column '{col}' not found in the CSV file."
                    }
            
            # Extract data from DataFrame - handle different data types
            x_data_original = df[x_column].tolist()
            x_data = x_data_original.copy()  # Create a copy to preserve original data
            
            # Create data dictionary for the line chart function
            data_dict = {}
            for col in y_columns:
                # Handle potential non-numeric y values
                try:
                    # Try to convert y values to numeric if they're not already
                    if df[col].dtype == 'object':
                        data_dict[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).tolist()
                    else:
                        data_dict[col] = df[col].tolist()
                except Exception:
                    # If conversion fails, use original values
                    data_dict[col] = df[col].tolist()
            
            # Auto-detect and handle string values for x-axis data
            # First check if x_data contains string values
            is_categorical = False
            converted_x_data = None
            
            # Check if data is categorical (either string, category, or has few unique values)
            if df[x_column].dtype == 'object' or df[x_column].dtype.name == 'category' or (
                pd.api.types.is_numeric_dtype(df[x_column]) and 
                # If there are few unique values compared to total count, it might be categorical
                len(df[x_column].unique()) <= min(10, len(df[x_column]) * 0.2)
            ):
                # Try different conversion approaches - but don't modify the original DataFrame
                
                # Try numeric conversion
                try:
                    converted_x_data = pd.to_numeric(df[x_column], errors='coerce')
                    if not converted_x_data.isna().any():  # If all values were converted successfully
                        x_data = converted_x_data.tolist()
                    else:
                        is_categorical = True
                except Exception:
                    is_categorical = True
                
                # If numeric conversion failed, try datetime
                if is_categorical:
                    try:
                        converted_x_data = pd.to_datetime(df[x_column], errors='coerce')
                        if not converted_x_data.isna().any():  # If all values were converted successfully
                            x_data = converted_x_data.tolist()
                            is_categorical = False
                        else:
                            is_categorical = True
                    except Exception:
                        is_categorical = True
            
            # Handle categorical x-axis data (using the special approach)
            if is_categorical:
                # Use categorical x-axis with positions
                x_positions = list(range(len(x_data_original)))
                
                # Create figure for categorical plotting
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Apply McKinsey style
                DataVisualizationUtils.apply_mckinsey_style()
                
                # Generate colors
                enhanced_colors = [
                    "#2878BD", "#FF8C00", "#2CA02C", "#9467BD", "#D62728",
                    "#8C564B", "#1F77B4", "#FF7F0E", "#17BECF", "#E377C2"
                ]
                
                # Plot each series with categorical x-axis
                for i, (series_name, y_values) in enumerate(data_dict.items()):
                    color = enhanced_colors[i % len(enhanced_colors)]
                    ax.plot(x_positions, y_values, marker='o', markersize=5, 
                            linestyle='-', linewidth=2.5, color=color, 
                            label=series_name, alpha=0.9)
                
                # Set x-ticks to string labels with proper rotation
                ax.set_xticks(x_positions)
                ax.set_xticklabels(x_data_original, rotation=45, ha='right')
                
                # Format plot
                ax.set_title(title, fontweight='bold', fontsize=14, pad=20)
                ax.set_xlabel(xlabel, fontweight='bold', fontsize=11)
                ax.set_ylabel(ylabel, fontweight='bold', fontsize=11)
                ax.yaxis.grid(True, linestyle='--', alpha=0.7, color='#DDDDDD')
                ax.set_axisbelow(True)
                
                # Add legend if there are multiple series
                if len(y_columns) > 1:
                    ax.legend(loc='best', frameon=True, framealpha=0.95, edgecolor='#DDDDDD')
                
                # Adjust layout and save
                plt.tight_layout()
                working_path = DataVisualizationUtils._ensure_output_path()
                # Generate a unique filename with timestamp
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                # Create output directory only when saving the file
                DataVisualizationUtils._create_output_directory(working_path)
                output_file = os.path.join(working_path, unique_filename)
                plt.savefig(output_file, dpi=300)
                plt.close()
                
                return {
                    "success": True,
                    "output_path": output_file,
                    "message": f"Line chart with categorical x-axis saved at: {output_file}"
                }
            
            # If we reach here, x_data is numeric or datetime - use standard line chart
            return DataVisualizationUtils.generate_line_chart(
                data=data_dict,
                x_values=x_data,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                filename=filename,
                multiple_series=(len(y_columns) > 1)
            )
        
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error processing CSV file: {str(e)}"
            }
    
    @staticmethod
    def generate_scatter_plot(x_data: list, y_data: list, title: str = "Scatter Plot",
                             xlabel: str = "X Axis", ylabel: str = "Y Axis",
                             labels: list = None, filename: str = "scatterplot_output.jpg",
                             working_path: str = None):
        """
        Generate a scatter plot with comprehensive data labels
        
        Args:
            x_data (list): List of x coordinates
            y_data (list): List of y coordinates
            title (str): Title for the chart
            xlabel (str): Label for X axis
            ylabel (str): Label for Y axis
            labels (list): Optional list of point labels or categories
            filename (str): Name of the output file
            working_path (str, optional): Deprecated. Path is now determined by _ensure_output_path().
            
        Returns:
            str: Success message or error message
        """
        try:
            # Validate input data
            if not isinstance(x_data, list) or not x_data:
                return "Error: X data must be a non-empty list."
                
            if not isinstance(y_data, list) or not y_data:
                return "Error: Y data must be a non-empty list."
                
            if len(x_data) != len(y_data):
                return f"Error: X data has {len(x_data)} points but Y data has {len(y_data)} points."
            
            # Apply McKinsey style
            DataVisualizationUtils.apply_mckinsey_style()
            
            # Create figure with a reasonable size
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Enhanced professional color palette - more vibrant but still professional
            enhanced_colors = [
                "#2878BD",  # McKinsey blue
                "#FF8C00",  # Dark orange
                "#2CA02C",  # Green
                "#9467BD",  # Purple
                "#D62728",  # Red
                "#8C564B",  # Brown
                "#1F77B4",  # Steel blue
                "#FF7F0E",  # Light orange
                "#17BECF",  # Cyan
                "#E377C2",  # Pink
            ]
            
            # If labels are provided, use them to color the points
            if labels and len(labels) == len(x_data):
                # Get unique labels
                unique_labels = list(set(labels))
                
                # Use enhanced colors or fallback to seaborn for large sets
                if len(unique_labels) <= len(enhanced_colors):
                    colors = enhanced_colors[:len(unique_labels)]
                else:
                    colors = sns.color_palette('viridis', len(unique_labels))
                
                # Create a scatter plot for each label with McKinsey styling
                for i, label in enumerate(unique_labels):
                    indices = [j for j, l in enumerate(labels) if l == label]
                    x_subset = [x_data[j] for j in indices]
                    y_subset = [y_data[j] for j in indices]
                    
                    # Create scatter with larger markers and edge color
                    ax.scatter(
                        x_subset, 
                        y_subset, 
                        color=colors[i], 
                        label=label, 
                        alpha=0.8,
                        s=80,  # Larger point size for visibility
                        edgecolor='white',  # White edges around points
                        linewidth=0.8
                    )
                
                # Add legend with McKinsey styling
                ax.legend(
                    loc='upper right',
                    frameon=True,
                    framealpha=0.95,
                    edgecolor='#DDDDDD'
                )
                
                # Add data labels for each category
                for i, label in enumerate(unique_labels):
                    indices = [j for j, l in enumerate(labels) if l == label]
                    if not indices:  # Skip if no points for this label
                        continue
                        
                    x_subset = [x_data[j] for j in indices]
                    y_subset = [y_data[j] for j in indices]
                    
                    # Find max and min points for this category
                    max_idx = np.argmax(y_subset)
                    min_idx = np.argmin(y_subset)
                    
                    # Label ALL or most points based on dataset size
                    if len(x_subset) <= 15:
                        # For smaller datasets, label all points
                        points_to_label = list(range(len(x_subset)))
                    else:
                        # For larger datasets, label a significant portion
                        # Always include max and min points
                        points_to_label = [max_idx, min_idx]
                        
                        # Include additional points at regular intervals
                        step = max(1, len(x_subset) // 8)  # Label about 12.5% of points
                        points_to_label.extend([j for j in range(0, len(x_subset), step) 
                                              if j != max_idx and j != min_idx])
                    
                    # Add labels for selected points
                    for j in points_to_label:
                        # Special formatting for max/min points
                        is_special = (j == max_idx or j == min_idx)
                        
                        # Point coordinates
                        x, y = x_subset[j], y_subset[j]
                        
                        # Different positions to reduce overlap
                        if j == max_idx:
                            # Max point gets top-right annotation with box
                            ax.annotate(
                                f'{label} max: ({x:.1f}, {y:.1f})',
                                xy=(x, y),
                                xytext=(10, 10),
                                textcoords='offset points',
                                color=colors[i],
                                fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec=colors[i], lw=1),
                                arrowprops=dict(arrowstyle='->', color=colors[i], alpha=0.7)
                            )
                        elif j == min_idx:
                            # Min point gets bottom-right annotation with box
                            ax.annotate(
                                f'{label} min: ({x:.1f}, {y:.1f})',
                                xy=(x, y),
                                xytext=(10, -15),
                                textcoords='offset points',
                                color=colors[i],
                                fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec=colors[i], lw=1),
                                arrowprops=dict(arrowstyle='->', color=colors[i], alpha=0.7)
                            )
                        else:
                            # Other points get simpler annotations
                            # Alternate positions for better spacing
                            position_idx = j % 4
                            if position_idx == 0:
                                xytext = (0, 10)  # Above
                                ha, va = 'center', 'bottom'
                            elif position_idx == 1:
                                xytext = (10, 0)  # Right
                                ha, va = 'left', 'center'
                            elif position_idx == 2:
                                xytext = (0, -10)  # Below
                                ha, va = 'center', 'top'
                            else:
                                xytext = (-10, 0)  # Left
                                ha, va = 'right', 'center'
                            
                            # Add background box for better visibility
                            ax.annotate(
                                f'({x:.1f}, {y:.1f})',
                                xy=(x, y),
                                xytext=xytext,
                                textcoords='offset points',
                                ha=ha, va=va,
                                fontsize=8,
                                color=colors[i],
                                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, ec=colors[i], lw=0.5)
                            )
                
            else:
                # If no labels provided, create a single scatter plot
                scatter = ax.scatter(
                    x_data, 
                    y_data, 
                    color=enhanced_colors[0], 
                    alpha=0.8,
                    s=80,  # Larger point size
                    edgecolor='white',
                    linewidth=0.8
                )
                
                # Add labels to several points
                # For small datasets (<= 20 points), label all points
                # For larger datasets, label a selection of points
                if len(x_data) <= 20:
                    points_to_label = list(range(len(x_data)))
                else:
                    # Find key points (max Y, min Y, max X, min X)
                    max_y_idx = np.argmax(y_data)
                    min_y_idx = np.argmin(y_data)
                    max_x_idx = np.argmax(x_data)
                    min_x_idx = np.argmin(x_data)
                    
                    # Include key points and others at regular intervals
                    key_indices = [max_y_idx, min_y_idx, max_x_idx, min_x_idx]
                    step = max(1, len(x_data) // 10)  # Label about 10% of points
                    
                    points_to_label = key_indices + [i for i in range(0, len(x_data), step) 
                                                    if i not in key_indices]
                
                # Add labels for selected points
                for i in points_to_label:
                    # Is this a key point?
                    is_key_point = (i == np.argmax(y_data) or i == np.argmin(y_data) or 
                                   i == np.argmax(x_data) or i == np.argmin(x_data))
                    
                    # Position labels to reduce overlap
                    if i == np.argmax(y_data):  # Max Y
                        xytext = (0, 15)
                        text = f'Max Y: ({x_data[i]:.1f}, {y_data[i]:.1f})'
                        ha, va = 'center', 'bottom'
                        font_props = {'fontweight': 'bold', 'fontsize': 9}
                        box_props = dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, 
                                       ec=enhanced_colors[0], lw=1)
                        arrow_props = dict(arrowstyle='->', color=enhanced_colors[0])
                    elif i == np.argmin(y_data):  # Min Y
                        xytext = (0, -15)
                        text = f'Min Y: ({x_data[i]:.1f}, {y_data[i]:.1f})'
                        ha, va = 'center', 'top'
                        font_props = {'fontweight': 'bold', 'fontsize': 9}
                        box_props = dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, 
                                       ec=enhanced_colors[0], lw=1)
                        arrow_props = dict(arrowstyle='->', color=enhanced_colors[0])
                    elif i == np.argmax(x_data):  # Max X
                        xytext = (15, 0)
                        text = f'Max X: ({x_data[i]:.1f}, {y_data[i]:.1f})'
                        ha, va = 'left', 'center'
                        font_props = {'fontweight': 'bold', 'fontsize': 9}
                        box_props = dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, 
                                       ec=enhanced_colors[0], lw=1)
                        arrow_props = dict(arrowstyle='->', color=enhanced_colors[0])
                    elif i == np.argmin(x_data):  # Min X
                        xytext = (-15, 0)
                        text = f'Min X: ({x_data[i]:.1f}, {y_data[i]:.1f})'
                        ha, va = 'right', 'center'
                        font_props = {'fontweight': 'bold', 'fontsize': 9}
                        box_props = dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, 
                                       ec=enhanced_colors[0], lw=1)
                        arrow_props = dict(arrowstyle='->', color=enhanced_colors[0])
                    else:
                        # For regular points, just use coordinates
                        position_idx = i % 4
                        if position_idx == 0:
                            xytext = (0, 10)
                            ha, va = 'center', 'bottom'
                        elif position_idx == 1:
                            xytext = (10, 0)
                            ha, va = 'left', 'center'
                        elif position_idx == 2:
                            xytext = (0, -10)
                            ha, va = 'center', 'top'
                        else:
                            xytext = (-10, 0)
                            ha, va = 'right', 'center'
                            
                        text = f'({x_data[i]:.1f}, {y_data[i]:.1f})'
                        font_props = {'fontsize': 8}
                        box_props = dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, 
                                       ec=enhanced_colors[0], lw=0.5)
                        arrow_props = None
                    
                    # Create annotation
                    if arrow_props:
                        ax.annotate(
                            text,
                            xy=(x_data[i], y_data[i]),
                            xytext=xytext,
                            textcoords='offset points',
                            ha=ha, va=va,
                            color=enhanced_colors[0],
                            bbox=box_props,
                            arrowprops=arrow_props,
                            **font_props
                        )
                    else:
                        ax.annotate(
                            text,
                            xy=(x_data[i], y_data[i]),
                            xytext=xytext,
                            textcoords='offset points',
                            ha=ha, va=va,
                            color=enhanced_colors[0],
                            bbox=box_props,
                            **font_props
                        )
            
            # Add title and labels with McKinsey styling
            ax.set_title(title, fontweight='bold', fontsize=14, pad=20)
            ax.set_xlabel(xlabel, fontweight='bold', fontsize=11)
            ax.set_ylabel(ylabel, fontweight='bold', fontsize=11)
            
            # McKinsey style has clean horizontal and vertical grid lines
            ax.grid(True, linestyle='--', alpha=0.3, color='#CCCCCC')
            ax.set_axisbelow(True)  # Grid below plot elements
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Add extra breathing room around points
            ax.margins(0.1)
            
            # Adjust layout
            plt.tight_layout()
            # Save the scatter plot
            working_path = DataVisualizationUtils._ensure_output_path()
            
            # Generate a unique filename with timestamp
            unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
            
            # Create output directory only when saving the file
            DataVisualizationUtils._create_output_directory(working_path)
            
            # Save the chart with enhanced settings for better quality
            output_file = os.path.join(working_path, unique_filename)
            plt.savefig(output_file, dpi=300)
            plt.close()
            
            return {
                "success": True,
                "output_path": output_file,
                "message": f"Scatter plot saved at: {output_file}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error generating scatter plot: {str(e)}"
            }
    
    @staticmethod
    def generate_scatter_plot_from_csv(file_path: str, x_column: str, y_column: str,
                                      label_column: str = None, title: str = "Scatter Plot", 
                                      xlabel: str = "X Axis", ylabel: str = "Y Axis", 
                                      filename: str = "scatterplot_from_csv.jpg",
                                      working_path: str = None):
        """
        Generate a scatter plot from CSV file data
        
        Args:
            file_path (str): Path to the CSV file
            x_column (str): Name of the column containing x-axis values
            y_column (str): Name of the column containing y-axis values
            label_column (str): Optional name of column containing point labels/categories
            title (str): Title for the chart
            xlabel (str): Label for X axis
            ylabel (str): Label for Y axis
            filename (str): Name of the output file
            working_path (str, optional): Deprecated. Path is now determined by _ensure_output_path().
            
        Returns:
            dict: Result dictionary with success status, output path, and message
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: File not found: {file_path}"
                }
                
            # Read CSV file with comma as thousands separator
            # Always make a copy to prevent modification of original data for multiple chart generation
            df = pd.read_csv(file_path, thousands=',').copy()
            
            # Validate column names
            if x_column not in df.columns:
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: X column '{x_column}' not found in the CSV file."
                }
                
            if y_column not in df.columns:
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: Y column '{y_column}' not found in the CSV file."
                }
                
            if label_column is not None and label_column not in df.columns:
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: Label column '{label_column}' not found in the CSV file."
                }
            
            # Extract data from DataFrame
            x_data = df[x_column].tolist()
            y_data = df[y_column].tolist()
            
            # Extract labels if provided
            labels = df[label_column].tolist() if label_column else None
            
            # Generate scatter plot using the existing method
            return DataVisualizationUtils.generate_scatter_plot(
                x_data=x_data,
                y_data=y_data,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                labels=labels,
                filename=filename
                # working_path is not passed as it's handled internally by generate_scatter_plot
            )
        
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error processing CSV file: {str(e)}"
            }
    
    @staticmethod
    def generate_bar_chart(data: dict, title: str = "Bar Chart",
                        xlabel: str = "Categories", ylabel: str = "Values",
                        filename: str = "barchart_output.jpg", figsize: Tuple[int, int] = (10, 6),
                        dpi: int = 300, color_palette: str = 'Set2', rotation: int = 45,
                        sort_values: bool = True, grid: bool = False, horizontal: bool = False,
                        stacked: bool = False, sort_data: bool = False, show_values: bool = False,
                        max_bars: int = 15, is_time_series: bool = False, working_path: str = None):
        """
        Generate a professional bar chart from dictionary data with McKinsey styling.
        
        This function creates bar charts with advanced data filtering for large datasets.
        For datasets with many categories, it can automatically aggregate less significant 
        values or group time series data to maintain readability.
        
        Args:
            data (dict): Dictionary with category names as keys and values or lists of values as values.
                         For multiple series, each value should be a list of the same length.
            title (str): Title for the chart. Will be appended with data filtering info if applied.
            title (str): Title for the chart. Will be appended with data filtering info if applied.
            xlabel (str): Label for X axis (category axis).
            ylabel (str): Label for Y axis (value axis).
            filename (str): Name of the output file. Should end with an image extension.
            figsize (Tuple[int, int]): Figure size as (width, height). If None, size is calculated based on data.
            dpi (int): DPI (dots per inch) for the output image. Higher values produce larger files.
            color_palette (str): Seaborn color palette to use. Also accepts built-in color scheme names.
            rotation (int): Rotation angle for x-axis labels. Useful for long category names.
            sort_values (bool): Whether to sort data by value in descending order (for single series only).
            grid (bool): Whether to show grid lines for easier value reading.
            horizontal (bool): Whether to create a horizontal bar chart. Recommended for many categories.
            stacked (bool): Whether to create a stacked bar chart (when values are lists). Alternative is grouped.
            sort_data (bool): Alternative parameter for sorting. Used if sort_values is False.
            show_values (bool): Whether to show values on top of bars. Function will determine which to show.
            max_bars (int): Maximum number of bars to display. Excess categories will be aggregated.
            is_time_series (bool): Whether the data is time series. Affects how data aggregation is performed.
            
        Returns:
            dict: Result containing:
                - success (bool): Whether the operation was successful
                - output_path (str): Path to the saved chart or None if failed
                - message (str): Success or error message
                
        Example:
            >>> data = {"Category A": 100, "Category B": 200, "Category C": 150}
            >>> result = DataVisualizationUtils.generate_bar_chart(
            ...     data=data,
            ...     working_path="/path/to/output",
            ...     horizontal=True,
            ...     title="Sample Bar Chart"
            ... )
        """
        try:
            # Validate input data
            if not isinstance(data, dict):
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Input data must be a dictionary with categories and values."
                }
                
            if not data:
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Input data dictionary cannot be empty."
                }                # Get path from config using _ensure_output_path
            working_path = DataVisualizationUtils._ensure_output_path()
            
            # Apply McKinsey style
            DataVisualizationUtils.apply_mckinsey_style()
            
            # Determine if we have multiple series (list values) or single values
            has_multiple_series = any(isinstance(v, (list, tuple)) for v in data.values())
            
            # Validate multi-series data consistency
            if has_multiple_series:
                first_series = None
                for k, v in data.items():
                    if not isinstance(v, (list, tuple)):
                        return {
                            "success": False,
                            "output_path": None,
                            "message": f"Error: Inconsistent data types. Found non-list value for category '{k}' in multi-series data."
                        }
                    if first_series is None:
                        first_series = len(v)
                    elif len(v) != first_series:
                        return {
                            "success": False,
                            "output_path": None,
                            "message": f"Error: Inconsistent series lengths. Category '{k}' has {len(v)} values, expected {first_series}."
                        }
            
            # If sorting is requested, sort by value (for single series only)
            # Use sort_values if provided, otherwise fall back to sort_data
            should_sort = (sort_values or sort_data) and not has_multiple_series
            if should_sort:
                # Sort by value
                sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
                categories = [item[0] for item in sorted_items]
                values = [item[1] for item in sorted_items]
            else:
                categories = list(data.keys())
                values = list(data.values())
            
            # *** DATA FILTERING AND AGGREGATION LOGIC ***
            # Check if we need to filter/aggregate the data (too many categories)
            if len(categories) > max_bars:
                # Create a message to add to title about data being filtered
                filter_message = f" (Top {max_bars-1} + Others)" if not is_time_series else " (Aggregated)"
                title = title + filter_message
                
                if is_time_series:
                    # Time series aggregation
                    # This is a simplified version - in practice you might want to detect the 
                    # time format and apply appropriate aggregation
                    
                    # Group data into chunks
                    chunk_size = len(categories) // max_bars + 1
                    new_categories = []
                    new_values = []
                    
                    for i in range(0, len(categories), chunk_size):
                        chunk_cats = categories[i:i+chunk_size]
                        chunk_vals = values[i:i+chunk_size]
                        
                        # Create a range label (first-last)
                        if len(chunk_cats) == 1:
                            new_cat = str(chunk_cats[0])
                        else:
                            new_cat = f"{chunk_cats[0]} - {chunk_cats[-1]}"
                        
                        # For values, calculate the average or sum
                        if has_multiple_series:
                            # For multi-series, we need to aggregate each series
                            new_val = []
                            for series_idx in range(len(values[0])):
                                series_vals = [val[series_idx] for val in chunk_vals]
                                new_val.append(sum(series_vals))
                            new_values.append(new_val)
                        else:
                            new_values.append(sum(chunk_vals))
                        
                        new_categories.append(new_cat)
                    categories = new_categories
                    values = new_values
                else:
                    # For non-time series: Keep top N-1 categories and group the rest as "Other"
                    if has_multiple_series:
                        # For multi-series, we need a different approach
                        # Calculate the total for each category across all series
                        totals = []
                        for i, cat in enumerate(categories):
                            total = sum(values[i])
                            totals.append((cat, values[i], total))
                        
                        # Sort by total
                        sorted_totals = sorted(totals, key=lambda x: x[2], reverse=True)
                        
                        # Take top N-1 and aggregate the rest
                        top_cats = []
                        top_vals = []
                        other_vals = [0] * len(values[0])  # Initialize with zeros for each series
                        
                        for i, (cat, vals, _) in enumerate(sorted_totals):
                            if i < max_bars - 1:
                                top_cats.append(cat)
                                top_vals.append(vals)
                            else:
                                # Add to "Other" category
                                for j in range(len(vals)):
                                    other_vals[j] += vals[j]
                        
                        # Add "Other" category
                        top_cats.append("Other")
                        top_vals.append(other_vals)
                        
                        categories = top_cats
                        values = top_vals
                    else:
                        # Single series case
                        sorted_items = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)
                        top_items = sorted_items[:max_bars-1]  # Top N-1 items
                        other_sum = sum(v for _, v in sorted_items[max_bars-1:])
                        
                        categories = [c for c, _ in top_items] + ["Other"]
                        values = [v for _, v in top_items] + [other_sum]
            # *** END DATA FILTERING AND AGGREGATION LOGIC ***
            
            # Use provided figure size or calculate based on content
            if figsize is not None:
                fig_size = figsize
            else:
                if horizontal:
                    fig_size = (10, max(6, len(categories) * 0.5))  # Height scales with number of categories
                else:
                    fig_size = (max(8, len(categories) * 0.6), 6)  # Width scales with number of categories
            
            fig, ax = plt.subplots(figsize=fig_size)
            
            # Enhanced professional color palette - use provided palette or default
            enhanced_colors = [
                "#2878BD",  # McKinsey blue
                "#FF8C00",  # Dark orange
                "#2CA02C",  # Green
                "#9467BD",  # Purple
                "#D62728",  # Red
                "#8C564B",  # Brown
                "#1F77B4",  # Steel blue
                "#FF7F0E",  # Light orange
                "#17BECF",  # Cyan
                "#E377C2",  # Pink
            ]

            # Set bar width
            bar_width = 0.8 if not has_multiple_series else 0.7
            
            # Create the bars
            if has_multiple_series:
                # Multiple series (grouped or stacked)
                num_categories = len(categories)
                num_series = len(next(iter(values)))  # Number of values in first list
                
                # Validate that all series have the same length
                for i, val in enumerate(values):
                    if len(val) != num_series:
                        return {
                            "success": False,
                            "output_path": None,
                            "message": f"Error: Series {categories[i]} has {len(val)} values but should have {num_series}."
                        }
                
                # Extract series data
                series_data = []
                for i in range(num_series):
                    series_data.append([values[j][i] for j in range(num_categories)])
                
                # Create positions for the bars
                if horizontal:
                    positions = np.arange(num_categories)
                else:
                    positions = np.arange(num_categories)
                
                # Create grouped or stacked bars
                if stacked:
                    # Stacked bars
                    bottom = np.zeros(num_categories)
                    bars = []
                    
                    for i, data_series in enumerate(series_data):
                        if horizontal:
                            bar = ax.barh(
                                positions, 
                                data_series, 
                                height=bar_width, 
                                left=bottom, 
                                color=enhanced_colors[i % len(enhanced_colors)],
                                alpha=0.8,
                                edgecolor='white',
                                linewidth=0.7
                            )
                            # Update the bottom for next series
                            bottom = [bottom[j] + data_series[j] for j in range(num_categories)]
                        else:
                            bar = ax.bar(
                                positions, 
                                data_series, 
                                width=bar_width, 
                                bottom=bottom, 
                                color=enhanced_colors[i % len(enhanced_colors)],
                                alpha=0.8,
                                edgecolor='white',
                                linewidth=0.7
                            )
                            # Update the bottom for next series
                            bottom = [bottom[j] + data_series[j] for j in range(num_categories)]
                        
                        bars.append(bar)
                    
                    # Add legend with series names
                    series_names = [f"Series {i+1}" for i in range(num_series)]  # Default series names
                    ax.legend(bars, series_names, loc='upper right')
                    
                    # Add data labels to each segment (total values on top of stack)
                    if horizontal:
                        for i in range(num_categories):
                            total = sum(series_data[j][i] for j in range(num_series))
                            # Format number to avoid showing .0 if it's a whole number
                            formatted_val = f'{total:,.0f}' if total == int(total) else f'{total:,.2f}'
                            
                            ax.annotate(
                                formatted_val,
                                xy=(total, positions[i]),
                                xytext=(5, 0),
                                textcoords='offset points',
                                ha='left', va='center',
                                fontsize=9,
                                fontweight='bold',
                                color='#333333',
                                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
                            )
                    else:
                        for i in range(num_categories):
                            total = sum(series_data[j][i] for j in range(num_series))
                            # Format number to avoid showing .0 if it's a whole number
                            formatted_val = f'{total:,.0f}' if total == int(total) else f'{total:,.2f}'
                            
                            ax.annotate(
                                formatted_val,
                                xy=(positions[i], total),
                                xytext=(0, 5),
                                textcoords='offset points',
                                ha='center', va='bottom',
                                fontsize=9,
                                fontweight='bold',
                                color='#333333',
                                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8)
                            )
                else:
                    # Grouped bars
                    group_width = bar_width / num_series
                    bars = []
                    
                    for i, data_series in enumerate(series_data):
                        if horizontal:
                            # For horizontal grouped bars
                            offset = positions + (i - num_series / 2 + 0.5) * group_width
                            bar = ax.barh(
                                offset, 
                                data_series, 
                                height=group_width,
                                color=enhanced_colors[i % len(enhanced_colors)],
                                alpha=0.8,
                                edgecolor='white',
                                linewidth=0.7
                            )
                            
                            # Add data labels to each bar
                            for j, value in enumerate(data_series):
                                # Only label specific points when there are too many
                                if len(data_series) > 15:
                                    # Label max and min points of this series
                                    max_idx = np.argmax(data_series)
                                    min_idx = np.argmin(data_series)
                                    # Only label max, min, first, last, and every nth point
                                    if j not in [max_idx, min_idx, 0, len(data_series)-1] and j % 3 != 0:
                                        continue
                                
                                is_special = j in [np.argmax(data_series), np.argmin(data_series)]
                                fontsize = 8 if is_special else 7
                                fontweight = 'bold' if is_special else 'normal'
                                bbox_props = dict(
                                    boxstyle="round,pad=0.2",
                                    fc="white", 
                                    alpha=0.8,
                                    ec=enhanced_colors[i % len(enhanced_colors)],
                                    lw=0.8 if is_special else 0.5
                                )
                                
                                # Format number to avoid showing .0 if it's a whole number
                                formatted_val = f'{value:,.0f}' if value == int(value) else f'{value:,.2f}'
                                
                                ax.annotate(
                                    formatted_val,
                                    xy=(value, offset[j]),
                                    xytext=(5, 0),
                                    textcoords='offset points',
                                    ha='left', va='center',
                                    fontsize=fontsize,
                                    fontweight=fontweight,
                                    color='#333333',
                                    bbox=bbox_props
                                )
                        else:
                            # For vertical grouped bars
                            offset = positions + (i - num_series / 2 + 0.5) * group_width
                            bar = ax.bar(
                                offset, 
                                data_series, 
                                width=group_width,
                                color=enhanced_colors[i % len(enhanced_colors)],
                                alpha=0.8,
                                edgecolor='white',
                                linewidth=0.7
                            )
                            
                            # Add data labels to each bar
                            
                            for j, value in enumerate(data_series):
                                # Only label specific points when there are too many
                                if len(data_series) > 15:
                                    # Label max and min points of this series
                                    max_idx = np.argmax(data_series)
                                    min_idx = np.argmin(data_series)
                                    # Only label max, min, first, last, and every nth point
                                    if j not in [max_idx, min_idx, 0, len(data_series)-1] and j % 3 != 0:
                                        continue
                                
                                is_special = j in [np.argmax(data_series), np.argmin(data_series)]
                                fontsize = 8 if is_special else 7
                                fontweight = 'bold' if is_special else 'normal'
                                bbox_props = dict(
                                    boxstyle="round,pad=0.2", 
                                    fc="white", 
                                    alpha=0.8,
                                    ec=enhanced_colors[i % len(enhanced_colors)],
                                    lw=0.8 if is_special else 0.5
                                )
                                
                                # Format number to avoid showing .0 if it's a whole number
                                formatted_val = f'{value:,.0f}' if value == int(value) else f'{value:,.2f}'
                                
                                ax.annotate(
                                    formatted_val,
                                    xy=(offset[j], value),
                                    xytext=(0, 5),
                                    textcoords='offset points',
                                    ha='center', va='bottom',
                                    fontsize=fontsize,
                                    fontweight=fontweight,
                                    color='#333333',
                                    bbox=bbox_props
                                )

                        
                        bars.append(bar)
                    
                    # Add legend with series names
                    series_names = [f"Series {i+1}" for i in range(num_series)]  # Default series names
                    ax.legend(bars, series_names, loc='upper right')
            else:
                # Single series
                if horizontal:
                    bars = ax.barh(
                        categories, 
                        values, 
                        height=bar_width,
                        color=enhanced_colors[0],
                        alpha=0.85,
                        edgecolor='white',
                        linewidth=0.8
                    )
                    
                    # Find special points
                    max_val_idx = np.argmax(values)
                    min_val_idx = np.argmin(values)
                    
                    # Determine which points to label
                    if len(values) <= 12:
                        # For small datasets, label all points
                        indices_to_label = list(range(len(values)))
                    else:
                        # For medium datasets, label about half the points
                        if len(values) <= 20:
                            # Label about half the points
                            step = 2
                        else:
                            # For larger datasets, use an adaptive approach
                            step = max(2, len(values) // 10)
                        
                        # Generate indices with step
                        indices_to_label = list(range(0, len(values), step))
                        
                        # Always include max, min, first and last points
                        if max_val_idx not in indices_to_label:
                            indices_to_label.append(max_val_idx)
                        if min_val_idx not in indices_to_label:
                            indices_to_label.append(min_val_idx)
                        if 0 not in indices_to_label:
                            indices_to_label.append(0)
                        if len(values) - 1 not in indices_to_label:
                            indices_to_label.append(len(values) - 1)
                        
                        # Sort the indices
                        indices_to_label = sorted(set(indices_to_label))
                    
                    # Add data labels to selected bars
                    for i in indices_to_label:
                        value = values[i]
                        # Different formatting for key points vs. regular points
                        is_special_point = (i == max_val_idx or i == min_val_idx or i == 0 or i == len(values) - 1)
                        
                        fontsize = 9 if is_special_point else 8
                        fontweight = 'bold' if is_special_point else 'normal'
                        bbox_props = dict(
                            boxstyle="round,pad=0.3" if is_special_point else "round,pad=0.2",
                            fc="white",
                            alpha=0.8,
                            ec=enhanced_colors[0],
                            lw=1 if is_special_point else 0.5
                        )
                        
                        # Add label with key point emphasis - format without trailing .0
                        # Format number to avoid showing .0 if it's a whole number
                        formatted_val = f'{value:,.0f}' if value == int(value) else f'{value:,.2f}'
                        
                        label_text = formatted_val
                        if is_special_point:
                            if i == max_val_idx:
                                label_text = f'Max: {formatted_val}'
                            elif i == min_val_idx:
                                label_text = f'Min: {formatted_val}'
                            
                        ax.annotate(
                            label_text,
                            xy=(value, i),
                            xytext=(5, 0),
                            textcoords='offset points',
                            ha='left', va='center',
                            fontsize=fontsize,
                            fontweight=fontweight,
                            color='#333333',
                            bbox=bbox_props
                        )
                else:
                    bars = ax.bar(
                        categories, 
                        values, 
                        width=bar_width,
                        color=enhanced_colors[0],
                        alpha=0.85,
                        edgecolor='white',
                        linewidth=0.8
                    )
                    
                    # Find special points
                    max_val_idx = np.argmax(values)
                    min_val_idx = np.argmin(values)
                    
                    # Determine which points to label
                    if len(values) <= 12:
                        # For small datasets, label all points
                        indices_to_label = list(range(len(values)))
                    else:
                        # For medium datasets, label about half the points
                        if len(values) <= 20:
                            # Label about half the points
                            step = 2
                        else:
                            # For larger datasets, use an adaptive approach
                            step = max(2, len(values) // 10)
                        
                        # Generate indices with step
                        indices_to_label = list(range(0, len(values), step))
                        
                        # Always include max, min, first and last points
                        if max_val_idx not in indices_to_label:
                            indices_to_label.append(max_val_idx)
                        if min_val_idx not in indices_to_label:
                            indices_to_label.append(min_val_idx)
                        if 0 not in indices_to_label:
                            indices_to_label.append(0)
                        if len(values) - 1 not in indices_to_label:
                            indices_to_label.append(len(values) - 1)
                        
                        # Sort the indices
                        indices_to_label = sorted(set(indices_to_label))
                    
                    # Add data labels to selected bars
                    for i in indices_to_label:
                        value = values[i]
                        # Different formatting for key points vs. regular points
                        is_special_point = (i == max_val_idx or i == min_val_idx or i == 0 or i == len(values) - 1)
                        
                        fontsize = 9 if is_special_point else 8
                        fontweight = 'bold' if is_special_point else 'normal'
                        bbox_props = dict(
                            boxstyle="round,pad=0.3" if is_special_point else "round,pad=0.2",
                            fc="white",
                            alpha=0.8,
                            ec=enhanced_colors[0],
                            lw=1 if is_special_point else 0.5
                        )
                        
                        # Add label with key point emphasis - format without trailing .0
                        # Format number to avoid showing .0 if it's a whole number
                        formatted_val = f'{value:,.0f}' if value == int(value) else f'{value:,.2f}'
                        
                        label_text = formatted_val
                        if is_special_point:
                            if i == max_val_idx:
                                label_text = f'Max: {formatted_val}'
                            elif i == min_val_idx:
                                label_text = f'Min: {formatted_val}'
                        
                        ax.annotate(
                            label_text,
                            xy=(i, value),
                            xytext=(0, 5),
                            textcoords='offset points',
                            ha='center', va='bottom',
                            fontsize=fontsize,
                            fontweight=fontweight,
                            color='#333333',
                            bbox=bbox_props
                        )
            
            # Add labels and title with McKinsey styling
            ax.set_title(title, fontweight='bold', fontsize=14, pad=20)
            
            if horizontal:
                ax.set_yticks(np.arange(len(categories)))
                ax.set_yticklabels(categories)
                ax.set_xlabel(ylabel, fontweight='bold', fontsize=11)  # Swapped for horizontal
                ax.set_ylabel(xlabel, fontweight='bold', fontsize=11)  # Swapped for horizontal
                
                # For horizontal bars, use vertical grid lines
                ax.yaxis.grid(False)
                ax.xaxis.grid(True, linestyle='--', alpha=0.7, color='#DDDDDD')
            else:
                ax.set_xticks(np.arange(len(categories)))
                # --- Only show part of x labels if too many categories ---
                if len(categories) > 30:
                    interval = 10
                    display_labels = [
                        cat if i % interval == 0 else "" 
                        for i, cat in enumerate(categories)
                    ]
                    ax.set_xticklabels(display_labels)
                else:
                    ax.set_xticklabels(categories)
                ax.set_xlabel(xlabel, fontweight='bold', fontsize=11)
                ax.set_ylabel(ylabel, fontweight='bold', fontsize=11)
                
                # McKinsey style has clean horizontal grid lines only
                ax.yaxis.grid(True, linestyle='--', alpha=0.7, color='#DDDDDD')
            
            # Set grid below data
            ax.set_axisbelow(True)
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Rotate labels if there are many categories
            if len(categories) > 5 and not horizontal:
                plt.xticks(rotation=45, ha='right')
                plt.subplots_adjust(bottom=0.2)  # Add space for rotated labels
            
            # Adjust layout to make sure everything fits
            plt.tight_layout()
            
            # Save the bar chart
            working_path = DataVisualizationUtils._ensure_output_path()
            
            # Generate a unique filename with timestamp
            unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
            
            # Create output directory only when saving the file
            DataVisualizationUtils._create_output_directory(working_path)
            
            # Save the chart
            output_file = os.path.join(working_path, unique_filename)
            plt.savefig(output_file, dpi=300)
            plt.close()

            return {
                "success": True,
                "output_path": output_file,
                "message": f"Bar chart saved at: {output_file}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error generating bar chart: {str(e)}"
            }

   
    # Excel chart generation functions have been removed
    # The data visualization tool now only supports CSV files

    @staticmethod
    def generate_bar_chart_from_csv(file_path: str, category_column: str, value_columns: list,
                                  title: str = "Bar Chart", xlabel: str = "Categories", 
                                  ylabel: str = "Values", filename: str = "barchart_from_csv.jpg",
                                  horizontal: bool = False, stacked: bool = False,
                                  sort_data: bool = False, working_path: str = None):
        """
        Generate a bar chart from CSV file data
        
        Args:
            file_path (str): Path to the CSV file
            category_column (str): Name of the column containing categories
            value_columns (list): List of column names containing values
            title (str): Title for the chart
            xlabel (str): Label for X axis
            ylabel (str): Label for Y axis
            filename (str): Name of the output file
            horizontal (bool): Whether to create a horizontal bar chart
            stacked (bool): Whether to create a stacked bar chart
            sort_data (bool): Whether to sort the data by value (only for single series)
            working_path (str, optional): Deprecated. Path is now determined by _ensure_output_path().
            
        Returns:
            dict: Result dictionary with success status, output path, and message
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: File not found: {file_path}"
                }
                
            # Read CSV file
            # Always make a copy to prevent modification of original data for multiple chart generation
            df = pd.read_csv(file_path, thousands=',').copy()
            
            # Validate column names
            if category_column not in df.columns:
                return {
                    "success": False,
                    "output_path": None,
                    "message": f"Error: Category column '{category_column}' not found in the CSV file."
                }
                
            for col in value_columns:
                if col not in df.columns:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": f"Error: Value column '{col}' not found in the CSV file."
                    }
            
            # Extract data from DataFrame
            categories = df[category_column].tolist()
            
            if len(value_columns) == 1:
                # Single series
                data_dict = {cat: val for cat, val in zip(categories, df[value_columns[0]].tolist())}
            else:
                # Multiple series
                # We need to reshape the data for stacked/grouped bars
                data_dict = {cat: [df.loc[df[category_column] == cat, col].values[0] for col in value_columns] 
                           for cat in categories}
            # Generate bar chart using the existing method
            return DataVisualizationUtils.generate_bar_chart(
                data=data_dict,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                filename=filename,
                horizontal=horizontal,
                stacked=stacked,
                sort_data=sort_data
                # working_path is not passed as it's handled internally by generate_bar_chart
            )
        
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error processing CSV file: {str(e)}"
            }
    
    @staticmethod
    def convert_excel_to_csv(excel_file_path: str, working_path: str = None) -> Dict[str, Any]:
        """
        This function is deprecated as Excel files are no longer supported.
        It now returns an error message recommending to use CSV files directly.
        
        Args:
            excel_file_path (str): Path to the Excel file
            working_path (str): Directory to save the output CSV file (not used anymore)
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Always False since Excel is no longer supported
                - csv_path (str): Always None
                - message (str): Error message recommending to use CSV
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.warning(f"convert_excel_to_csv: Excel files are no longer supported: {excel_file_path}")
        
        return {
            "success": False,
            "csv_path": None,
            "message": f"Excel files are no longer supported. Please use CSV files directly instead of '{excel_file_path}'."
        }
            
    @staticmethod
    def _detect_data_source(data_source):
        """
        Detects the type of data source provided.
        Excel files are not supported and will return an error message.
        
        Args:
            data_source: The data source to detect. Can be a dictionary, CSV file path, or DataFrame.
            
        Returns:
            tuple: (source_type, source_info)
                - source_type: 'dict', 'csv', 'dataframe', or 'unknown'
                - source_info: Additional information about the source
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.debug(f"_detect_data_source: Starting data source detection")
        logger.debug(f"_detect_data_source: Data source type: {type(data_source)}")
        
        if isinstance(data_source, dict):
            logger.debug(f"_detect_data_source: Detected dictionary source with {len(data_source)} keys")
            return "dict", {"format": "dictionary"}
        
        elif isinstance(data_source, pd.DataFrame):
            logger.debug(f"_detect_data_source: Detected DataFrame source with shape {data_source.shape}")
            logger.debug(f"_detect_data_source: DataFrame columns: {data_source.columns.tolist()}")
            return "dataframe", {"format": "pandas_dataframe"}
        
        elif isinstance(data_source, str):
            logger.debug(f"_detect_data_source: Detected string source: {data_source}")
            # Check if it's a file path
            if os.path.exists(data_source):
                logger.debug(f"_detect_data_source: File exists")
                logger.debug(f"_detect_data_source: File size: {os.path.getsize(data_source)} bytes")
                
                # Check file extension
                if data_source.lower().endswith('.xlsx') or data_source.lower().endswith('.xls'):
                    logger.warning(f"_detect_data_source: Excel files are no longer supported: {data_source}")
                    error_message = f"Excel files are not supported. Please convert '{data_source}' to CSV format and try again."
                    return "unknown", {"error": error_message}
                
                elif data_source.lower().endswith('.csv'):
                    logger.debug(f"_detect_data_source: Detected CSV file: {data_source}")
                    return "csv", {"file_path": data_source}
                else:
                    logger.warning(f"_detect_data_source: Unsupported file type: {data_source}")
                    return "unknown", {"error": f"Unsupported file type: {data_source}"}
            else:
                logger.error(f"_detect_data_source: File not found: {data_source}")
                return "unknown", {"error": f"File not found: {data_source}"}
        
        else:
            logger.error(f"_detect_data_source: Unsupported data source type: {type(data_source).__name__}")
            return "unknown", {"error": f"Unsupported data source type: {type(data_source).__name__}"}

    @staticmethod
    def _ensure_output_path():
        """
        Determines the daily output path structure without creating the directory.
        Uses daily folders instead of per-second timestamped folders for better organization.
        
        Returns:
            str: Path structure (directory is not created yet)
        """
        # Create a daily directory path within WORKING_PATH (only date, not time)
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        path = os.path.join(config.WORKING_PATH, f"charts_{date_str}")
        
        return path
        
    @staticmethod
    def _create_output_directory(path):
        """
        Creates the output directory only when actually saving files.
        
        Args:
            path (str): Directory path to create
            
        Returns:
            str: Created directory path
        """
        if not os.path.exists(path):
            print(f"DEBUG: Creating directory {path}")
            os.makedirs(path)
        return path
    
    @staticmethod
    def _generate_unique_filename(filename):
        """
        Generate a unique filename by always adding a timestamp for uniqueness.
        This ensures files within the same daily folder have distinct names.
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Unique filename with timestamp
        """
        # Split filename and extension
        base_name, extension = os.path.splitext(filename)
        
        # Always add a timestamp to ensure uniqueness (hours, minutes, seconds)
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        new_filename = f"{base_name}_{timestamp}{extension}"
        
        return new_filename
        
        return new_filename

    @staticmethod
    def _extract_data_from_source(data_source, source_type, chart_type, **options):
        """
        Extracts relevant data from the provided data source based on chart type.
        
        Args:
            data_source: Data source (dict, file path, or DataFrame)
            source_type: Type of the source as determined by _detect_data_source()
            chart_type: Type of chart to generate ('pie', 'line', 'scatter', 'bar')
            **options: Additional options including column names
            
        Returns:
            dict: Extracted data ready for chart generation
        """
        result = {"source_type": source_type, "chart_type": chart_type}
        
        if source_type == "dict":
            # For dictionary data source, we can use it directly in most cases
            result["data"] = data_source
            
            # For line charts, we need x_values
            if chart_type == "line" and "x_values" in options:
                result["x_values"] = options["x_values"]
            
            # For scatter plots, we need separate x_data and y_data
            elif chart_type == "scatter":
                # For scatter from dict, we assume x and y are provided as separate arrays
                result["x_data"] = options.get("x_data", list(range(len(data_source))))
                result["y_data"] = options.get("y_data", list(data_source.values()))
                if "labels" in options:
                    result["labels"] = options["labels"]
        
        elif source_type == "csv":
            # Load data from file
            file_path = data_source
            import logging
            logger = logging.getLogger(__name__)
            
            # Use thousands=',' to handle comma as thousands separator
            df = pd.read_csv(file_path, thousands=',')
            
            # Global dropna() - Remove rows and columns with NaN values to prevent errors
            # This is applied to all CSV data processing to ensure clean data for visualization
            original_shape = df.shape
            df = df.dropna()
            logger.debug(f"Applied global dropna() - Original shape: {original_shape}, Final shape after removing NaN: {df.shape}")
            
            # Apply data cleaning for CSV file if value columns specified
            if "value_column" in options:
                value_cols = [options["value_column"]]
            elif "value_columns" in options:
                value_cols = options["value_columns"]
            else:
                value_cols = None
            
            # Define phrases to exclude (empty strings, test data, etc.)
            exclude_phrases = options.get("exclude_phrases", ["test", "example", "N/A"])
            
            # Apply data cleaning
            df = DataVisualizationUtils.clean_data_for_visualization(
                df, 
                value_columns=value_cols,
                exclude_phrases=exclude_phrases,
                process_percentages=True,
                process_currency=True,
                process_units=True
            )
            
            result["dataframe"] = df
            
            # Extract data based on chart type
            if chart_type == "pie":
                category_column = options.get("category_column")
                value_column = options.get("value_column")
                
                if category_column and value_column:
                    if category_column in df.columns and value_column in df.columns:
                        result["data"] = dict(zip(df[category_column], df[value_column]))
                    else:
                        result["error"] = f"Columns not found: {category_column} or {value_column}"
                else:
                    result["error"] = "Missing required columns for pie chart: category_column and value_column"
                    
            elif chart_type == "line":
                x_column = options.get("x_column")
                y_columns = options.get("y_columns")
                
                if x_column and y_columns:
                    if x_column in df.columns and all(col in df.columns for col in y_columns):
                        result["x_values"] = df[x_column].tolist()
                        result["data"] = {col: df[col].tolist() for col in y_columns}
                    else:
                        result["error"] = f"Some columns not found in {list(df.columns)}"
                else:
                    result["error"] = "Missing required columns for line chart: x_column and y_columns"
                    
            elif chart_type == "scatter":
                x_column = options.get("x_column")
                y_column = options.get("y_column")
                label_column = options.get("label_column")
                
                if x_column and y_column:
                    if x_column in df.columns and y_column in df.columns:
                        result["x_data"] = df[x_column].tolist()
                        result["y_data"] = df[y_column].tolist()
                        if label_column and label_column in df.columns:
                            result["labels"] = df[label_column].tolist()
                    else:
                        result["error"] = f"Columns not found: {x_column} or {y_column}"
                else:
                    result["error"] = "Missing required columns for scatter plot: x_column and y_column"
                    
            elif chart_type == "bar":
                category_column = options.get("category_column")
                value_columns = options.get("value_columns")
                
                if category_column and value_columns:
                    if category_column in df.columns and all(col in df.columns for col in value_columns):
                        result["data"] = df.groupby(category_column)[value_columns].sum().reset_index()
                    else:
                        result["error"] = f"Some columns not found in {list(df.columns)}"
        
        elif source_type == "dataframe":
            df = data_source
            result["dataframe"] = df
            
            # The logic is similar to Excel/CSV but we already have the DataFrame
            if chart_type == "pie":
                category_column = options.get("category_column")
                value_column = options.get("value_column")
                
                if category_column and value_column:
                    if category_column in df.columns and value_column in df.columns:
                        result["data"] = dict(zip(df[category_column], df[value_column]))
                    else:
                        result["error"] = f"Columns not found: {category_column} or {value_column}"
                else:
                    result["error"] = "Missing required columns for pie chart: category_column and value_column"
                    
            # Similar logic for other chart types
            elif chart_type == "line":
                x_column = options.get("x_column")
                y_columns = options.get("y_columns")
                
                if x_column and y_columns:
                    if x_column in df.columns and all(col in df.columns for col in y_columns):
                        result["x_values"] = df[x_column].tolist()
                        result["data"] = {col: df[col].tolist() for col in y_columns}
                    else:
                        result["error"] = f"Some columns not found in {list(df.columns)}"
                else:
                    result["error"] = "Missing required columns for line chart: x_column and y_columns"
                
            elif chart_type == "scatter":
                x_column = options.get("x_column")
                y_column = options.get("y_column")
                label_column = options.get("label_column")
                
                if x_column and y_column:
                    if x_column in df.columns and y_column in df.columns:
                        result["x_data"] = df[x_column].tolist()
                        result["y_data"] = df[y_column].tolist()
                        if label_column and label_column in df.columns:
                            result["labels"] = df[label_column].tolist()
                    else:
                        result["error"] = f"Columns not found: {x_column} or {y_column}"
                else:
                    result["error"] = "Missing required columns for scatter plot: x_column and y_column"
                
            elif chart_type == "bar":
                category_column = options.get("category_column")
                value_columns = options.get("value_columns")
                
                if category_column and value_columns:
                    if category_column in df.columns and all(col in df.columns for col in value_columns):
                        result["data"] = df.groupby(category_column)[value_columns].sum().reset_index()
                    else:
                        result["error"] = f"Some columns not found in {list(df.columns)}"
        
        return result

    @staticmethod
    def generate_chart(
        chart_type: str,
        data_source: Union[Dict, str, pd.DataFrame],
        **options
    ) -> Dict[str, Any]:
        """
        Unified chart generation function that supports multiple data sources and chart types.
        
        Args:
            chart_type: Type of chart to generate ('pie', 'line', 'scatter', 'bar')
                       Also supports user-friendly names ('bar_chart', 'line_chart', 'pie_chart', 'scatter_plot')
            data_source: Data source - can be a dictionary, CSV file path, or DataFrame
                         Note: Excel files are no longer supported, please use CSV format
            **options: Chart-specific options, including:
                - title: Chart title
                - filename: Output filename
                - Various chart-specific parameters like columns, labels, etc.
                
        Returns:
            Dict[str, Any]: Dictionary containing:
                - 'success' (bool): Whether the chart was generated successfully
                - 'output_path' (str): Path to the generated chart file
                - 'message' (str): Success or error message
                - 'data': The extracted data used to generate the chart
                - 'chart_type': The type of chart generated
                - 'timestamp': ISO format timestamp when the chart was generated
        """
        # 0. Convert visualization_type to the expected chart_type format if necessary
        chart_type = DataVisualizationUtils.convert_visualization_type(chart_type)
        
        # 1. Determine the output path structure (without creating the directory)
        working_path = DataVisualizationUtils._ensure_output_path()
        
        # 2. Detect data source type
        source_type, source_info = DataVisualizationUtils._detect_data_source(data_source)
        
        if source_type == "unknown":
            return {
                "success": False,
                "output_path": None,
                "message": f"Error: {source_info.get('error', 'Unknown data source type')}",
                "chart_type": chart_type,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Excel to CSV conversion is no longer supported
        # If you have Excel files, please convert them to CSV format manually
        
        # 3. Extract data from source based on chart type
        extracted_data = DataVisualizationUtils._extract_data_from_source(data_source, source_type, chart_type, **options)
        
        if "error" in extracted_data:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error: {extracted_data['error']}",
                "chart_type": chart_type,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # 4. Generate chart based on chart type and extracted data
        result = None
        
        if chart_type == "pie":
            if source_type == "dict":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                result = DataVisualizationUtils.generate_pie_chart_tool(
                    data=extracted_data["data"],
                    title=options.get("title", "Data Distribution"),
                    filename=unique_filename, 
                    figsize=options.get("figsize", (8, 8)),
                    dpi=options.get("dpi", 300),
                    autopct=options.get("autopct", '%1.1f%%'),
                    startangle=options.get("startangle", 90),
                    shadow=options.get("shadow", False),
                    explode=options.get("explode", None),
                    color_palette=options.get("color_palette", 'Set2')
                )
            elif source_type == "excel":
                # Excel is no longer supported, return error
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Excel files are not supported. Please convert to CSV format and try again.",
                    "chart_type": chart_type,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            elif source_type == "csv":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
        
                if "category_column" in options and "value_column" in options:
                    result = DataVisualizationUtils.generate_pie_chart_from_csv(
                        file_path=data_source,
                        category_column=options["category_column"],
                        value_column=options["value_column"],
                        title=options.get("title", "Data Distribution"),
                        filename=unique_filename,
                        figsize=options.get("figsize", (8, 8)),
                        dpi=options.get("dpi", 300),
                        autopct=options.get("autopct", '%1.1f%%'),
                        startangle=options.get("startangle", 90),
                        shadow=options.get("shadow", False),
                        explode=options.get("explode", None),
                        color_palette=options.get("color_palette", 'Set2')
                    )
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for pie chart from CSV: category_column and value_column",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
            elif source_type == "dataframe":
                # For dataframe, first convert to dict
                if "category_column" in options and "value_column" in options:
                    df = data_source
                    category_column = options["category_column"]
                    value_column = options["value_column"]
                    
                    if category_column in df.columns and value_column in df.columns:
                        data_dict = dict(zip(df[category_column], df[value_column]))
                        result = DataVisualizationUtils.generate_pie_chart_tool(
                            data=data_dict,
                            title=options.get("title", "Data Distribution"),
                            filename=unique_filename,
                            figsize=options.get("figsize", (8, 8)),
                            dpi=options.get("dpi", 300),
                            autopct=options.get("autopct", '%1.1f%%'),
                            startangle=options.get("startangle", 90),
                            shadow=options.get("shadow", False),
                            explode=options.get("explode", None),
                            color_palette=options.get("color_palette", 'Set2')
                        )
                    else:
                        return {
                            "success": False,
                            "output_path": None,
                            "message": f"Error: Columns not found: {category_column} or {value_column}",
                            "chart_type": chart_type,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for pie chart from DataFrame: category_column and value_column",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
        
        elif chart_type == "line":
            if source_type == "dict":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                if "x_values" in extracted_data:
                    result = DataVisualizationUtils.generate_line_chart(
                        data=extracted_data["data"],
                        x_values=extracted_data["x_values"],
                        title=options.get("title", "Line Chart"),
                        xlabel=options.get("xlabel", "X Axis"),
                        ylabel=options.get("ylabel", "Y Axis"),
                        filename=unique_filename,
                        multiple_series=options.get("multiple_series", len(extracted_data["data"]) > 1)
                    )
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing x_values for line chart from dictionary",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
            elif source_type == "excel":
                # Excel is no longer supported, return error
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Excel files are not supported. Please convert to CSV format and try again.",
                    "chart_type": chart_type,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            elif source_type == "csv":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                if "x_column" in options and "y_columns" in options:
                    result = DataVisualizationUtils.generate_line_chart_from_csv(
                        file_path=data_source,
                        x_column=options["x_column"],
                        y_columns=options["y_columns"],
                        title=options.get("title", "Line Chart"),
                        xlabel=options.get("xlabel", "X Axis"),
                        ylabel=options.get("ylabel", "Y Axis"),
                        filename=unique_filename,
                    )
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for line chart from CSV: x_column and y_columns",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
            elif source_type == "dataframe":
                if "x_column" in options and "y_columns" in options:
                    df = data_source
                    x_column = options["x_column"]
                    y_columns = options["y_columns"]
                    
                    if x_column in df.columns and all(col in df.columns for col in y_columns):
                        x_values = df[x_column].tolist()
                        data = {col: df[col].tolist() for col in y_columns}
                        result = DataVisualizationUtils.generate_line_chart(
                            data=data,
                            x_values=x_values,
                            title=options.get("title", "Line Chart"),
                            xlabel=options.get("xlabel", "X Axis"),
                            ylabel=options.get("ylabel", "Y Axis"),
                            filename=options.get("filename", "linechart_from_dataframe.jpg"),
                            multiple_series=len(y_columns) > 1
                        )
                    else:
                        return {
                            "success": False,
                            "output_path": None,
                            "message": f"Error: Some columns not found in {list(df.columns)}",
                            "chart_type": chart_type,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for line chart from DataFrame: x_column and y_columns",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
        
        elif chart_type == "scatter":
            if source_type == "dict":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                result = DataVisualizationUtils.generate_scatter_plot(
                    x_data=extracted_data["x_data"],
                    y_data=extracted_data["y_data"],
                    title=options.get("title", "Scatter Plot"),
                    xlabel=options.get("xlabel", "X Axis"),
                    ylabel=options.get("ylabel", "Y Axis"),
                    labels=extracted_data.get("labels"),
                    filename=unique_filename,
                )
            elif source_type == "excel":
                # Excel is no longer supported, return error
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Excel files are not supported. Please convert to CSV format and try again.",
                    "chart_type": chart_type,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            elif source_type == "csv":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                if "x_column" in options and "y_column" in options:
                    result = DataVisualizationUtils.generate_scatter_plot_from_csv(
                        file_path=data_source,
                        x_column=options["x_column"],
                        y_column=options["y_column"],
                        label_column=options.get("label_column"),
                        title=options.get("title", "Scatter Plot"),
                        xlabel=options.get("xlabel", "X Axis"),
                        ylabel=options.get("ylabel", "Y Axis"),
                        filename=unique_filename
                    )
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for scatter plot from CSV: x_column and y_column",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
            elif source_type == "dataframe":
                if "x_column" in options and "y_column" in options:
                    df = data_source
                    x_column = options["x_column"]
                    y_column = options["y_column"]
                    label_column = options.get("label_column")
                    
                    if x_column in df.columns and y_column in df.columns:
                        x_data = df[x_column].tolist()
                        y_data = df[y_column].tolist()
                        labels = None
                        if label_column and label_column in df.columns:
                            labels = df[label_column].tolist()
                            
                        result = DataVisualizationUtils.generate_scatter_plot(
                            x_data=x_data,
                            y_data=y_data,
                            title=options.get("title", "Scatter Plot"),
                            xlabel=options.get("xlabel", "X Axis"),
                            ylabel=options.get("ylabel", "Y Axis"),
                            labels=labels,
                            filename=options.get("filename", "scatterplot_from_dataframe.jpg")
                        )
                    else:
                        return {
                            "success": False,
                            "output_path": None,
                            "message": f"Error: Columns not found: {x_column} or {y_column}",
                            "chart_type": chart_type,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for scatter plot from DataFrame: x_column and y_column",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
        
        elif chart_type == "bar":

            if source_type == "dict":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                result = DataVisualizationUtils.generate_bar_chart(
                    data=extracted_data["data"],
                    title=options.get("title", "Bar Chart"),
                    xlabel=options.get("xlabel", "Categories"),
                    ylabel=options.get("ylabel", "Values"),
                    filename=unique_filename,
                    figsize=options.get("figsize", (10, 6)),
                    dpi=options.get("dpi", 300),
                    color_palette=options.get("color_palette", 'Set2'),
                    rotation=options.get("rotation", 0),
                    sort_values=options.get("sort_values", False),
                    grid=options.get("grid", True),
                    horizontal=options.get("horizontal", False),
                    stacked=options.get("stacked", False),
                    sort_data=options.get("sort_data", False),
                    show_values=options.get("show_values", False)
                )
            elif source_type == "excel":
                # Excel is no longer supported, return error
                return {
                    "success": False,
                    "output_path": None,
                    "message": "Error: Excel files are not supported. Please convert to CSV format and try again.",
                    "chart_type": chart_type,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            elif source_type == "csv":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                if "category_column" in options and "value_columns" in options:
                    
                    df = extracted_data["dataframe"]
                    category_column = options["category_column"]
                    value_columns = options["value_columns"]
                    categories = df[category_column].tolist()
                    
                    if len(value_columns) == 1:
                        
                        data_dict = {cat: df.loc[df[category_column] == cat, value_columns[0]].values[0] 
                                    for cat in categories}
                    else:
                       
                        data_dict = {cat: [df.loc[df[category_column] == cat, col].values[0] for col in value_columns] 
                                    for cat in categories}
                                    
                    
                    result = DataVisualizationUtils.generate_bar_chart(
                        data=data_dict,  
                        title=options.get("title", "Bar Chart"),
                        xlabel=options.get("xlabel", "Categories"),
                        ylabel=options.get("ylabel", "Values"),
                        filename=unique_filename,
                        figsize=options.get("figsize", (10, 6)),
                        dpi=options.get("dpi", 300),
                        color_palette=options.get("color_palette", 'Set2'),
                        rotation=options.get("rotation", 0),
                        sort_values=options.get("sort_values", False),
                        grid=options.get("grid", True),
                        horizontal=options.get("horizontal", False),
                        stacked=options.get("stacked", False),
                        sort_data=options.get("sort_data", False),
                        show_values=options.get("show_values", False)
                    )
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for bar chart from CSV: category_column and value_columns",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
            elif source_type == "dataframe":
                filename = options.get("filename", "piechart_output.jpg")
                unique_filename = DataVisualizationUtils._generate_unique_filename(filename)
                if "category_column" in options and "value_columns" in options:
                    df = data_source
                    category_column = options["category_column"]
                    value_columns = options["value_columns"]
                    
                    if category_column in df.columns and all(col in df.columns for col in value_columns):
                        # For bar chart from dataframe, prepare data in the format expected by generate_bar_chart
                        categories = df[category_column].tolist()
                        data = {}
                        for col in value_columns:
                            data[col] = dict(zip(categories, df[col].tolist()))
                            
                        result = DataVisualizationUtils.generate_bar_chart(
                            data=data,
                            title=options.get("title", "Bar Chart"),
                            xlabel=options.get("xlabel", "Categories"),
                            ylabel=options.get("ylabel", "Values"),
                            filename=unique_filename,  
                            figsize=options.get("figsize", (10, 6)),
                            dpi=options.get("dpi", 300),
                            color_palette=options.get("color_palette", 'Set2'),
                            rotation=options.get("rotation", 0),
                            sort_values=options.get("sort_values", False),
                            grid=options.get("grid", True),
                            horizontal=options.get("horizontal", False),
                            stacked=options.get("stacked", False),
                            sort_data=options.get("sort_data", False),
                            show_values=options.get("show_values", False)
                        )
                    else:
                        return {
                            "success": False,
                            "output_path": None,
                            "message": f"Error: Some columns not found in {list(df.columns)}",
                            "chart_type": chart_type,
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                else:
                    return {
                        "success": False,
                        "output_path": None,
                        "message": "Error: Missing required parameters for bar chart from DataFrame: category_column and value_columns",
                        "chart_type": chart_type,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
        
        else:
            return {
                "success": False,
                "output_path": None,
                "message": f"Error: Unsupported chart type: {chart_type}",
                "chart_type": chart_type,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # 5. Enhance result with additional data
        if result:
            result["data"] = extracted_data
            result["chart_type"] = chart_type
            result["timestamp"] = datetime.datetime.now().isoformat()
        
        return result
