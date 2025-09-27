# [file name]: scripts/data_cleaning.py
"""
Data Cleaning and Preprocessing Module
This module handles data cleaning tasks including handling missing values,
standardizing formats, correcting inconsistencies, and preparing data for analysis.
 Author: SUBHAJIT HALDER 
       DATE: 27/09/2025
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')  # Suppress warnings for cleaner output

class DataCleaner:
    """
    A class to clean and preprocess healthcare visit data.
    
    This class provides methods to handle common data quality issues
    found in real-world healthcare datasets.
    """
    
    def __init__(self, file_path):
        """
        Initialize the DataCleaner with a dataset.
        
        Args:
            file_path (str): Path to the CSV file containing the raw data
        """
        self.df = pd.read_csv(file_path)
        self.cleaning_report = {}  # Dictionary to track cleaning operations

    def explore_data(self):
        """
        Perform initial exploration of the dataset.
        
        This method examines the data structure, types, and initial quality issues.
        It's good practice to understand your data before cleaning.
        """
        print("=== INITIAL DATA EXPLORATION ===")
        print(f"Dataset shape: {self.df.shape} (rows, columns)")
        print("\nColumn data types:")
        print(self.df.dtypes)
        print("\nMissing values per column:")
        print(self.df.isnull().sum())
        
        # Store initial metrics for reporting
        self.cleaning_report['initial_rows'] = len(self.df)
        self.cleaning_report['initial_missing'] = self.df.isnull().sum().to_dict()

    def handle_datetime_inconsistencies(self):
        """
        Standardize datetime formats across the dataset.
        
        Real-world data often has multiple date formats from different systems.
        This method parses and standardizes them into proper datetime objects.
        """
        print("\n=== STANDARDIZING DATETIME FORMATS ===")
        
        def parse_flexible_date(date_str):
            """
            Helper function to parse dates in multiple possible formats.
            
            Args:
                date_str (str): Date string to parse
                
            Returns:
                datetime: Parsed datetime object or NaT if parsing fails
            """
            if pd.isna(date_str) or date_str == "" or date_str == " ":
                return pd.NaT  # Not a Time (pandas representation for missing datetime)
                
            # Try different date formats commonly found in healthcare data
            formats = [
                '%Y-%m-%d %H:%M:%S',  # ISO format
                '%d-%m-%Y %H:%M',     # Day-month-year
                '%m-%d-%Y %H:%M',     # Month-day-year
                '%d/%m/%Y %H:%M',     # With slashes
                '%m/%d/%Y %H:%M'      # US format with slashes
            ]
            
            # Attempt parsing with each format
            for fmt in formats:
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue  # Try next format if this one fails
            
            return pd.NaT  # Return missing if no format works

        # Apply parsing to both start and end time columns
        self.df['visit_start_time'] = self.df['visit_start_time'].apply(parse_flexible_date)
        self.df['visit_end_time'] = self.df['visit_end_time'].apply(parse_flexible_date)

        print(f"✓ Datetime standardization completed")
        print(f"✓ Missing start times: {self.df['visit_start_time'].isna().sum()}")
        print(f"✓ Missing end times: {self.df['visit_end_time'].isna().sum()}")

    def remove_duplicates(self):
        """
        Remove duplicate records from the dataset.
        
        In healthcare data, duplicate entries can occur due to system errors.
        This method identifies and removes them based on visit_id.
        """
        print("\n=== REMOVING DUPLICATE RECORDS ===")
        initial_count = len(self.df)
        
        # Remove duplicates keeping the first occurrence
        self.df = self.df.drop_duplicates(subset=['visit_id'], keep='first')
        removed_count = initial_count - len(self.df)
        
        print(f"✓ Removed {removed_count} duplicate records")
        self.cleaning_report['duplicates_removed'] = removed_count

    def handle_missing_values(self):
        """
        Handle missing values using appropriate strategies.
        
        For missing end times: impute based on average service duration
        For missing notes: fill with placeholder text
        """
        print("\n=== HANDLING MISSING VALUES ===")

        # Calculate durations where both start and end times are available
        valid_durations = self.df.dropna(subset=['visit_start_time', 'visit_end_time']).copy()
        valid_durations['duration'] = (valid_durations['visit_end_time'] - 
                                     valid_durations['visit_start_time']).dt.total_seconds() / 60
        
        # Calculate average duration per service type for imputation
        service_avg_duration = valid_durations.groupby('service_type')['duration'].mean()
        
        # Identify records with missing end times but valid start times
        missing_end_mask = self.df['visit_end_time'].isna() & self.df['visit_start_time'].notna()
        
        # Impute missing end times using service-specific averages
        for idx in self.df[missing_end_mask].index:
            service = self.df.loc[idx, 'service_type']
            avg_duration = service_avg_duration.get(service, 60)  # Default 60 minutes
            start_time = self.df.loc[idx, 'visit_start_time']
            if pd.notna(start_time):
                self.df.loc[idx, 'visit_end_time'] = start_time + pd.Timedelta(minutes=avg_duration)

        # Handle missing nurse notes by filling with descriptive text
        self.df['nurse_notes'] = self.df['nurse_notes'].fillna('No notes provided')
        self.df['nurse_notes'] = self.df['nurse_notes'].replace('', 'No notes provided')

        print("✓ Missing values handled using appropriate imputation strategies")

    def clean_categorical_variables(self):
        """
        Standardize categorical variables by correcting typos and inconsistencies.
        
        Real-world data often has variations in categorical values that need
        to be standardized for proper analysis.
        """
        print("\n=== STANDARDIZING CATEGORICAL VARIABLES ===")

        # Correct common typos and variations in service types
        service_corrections = {
            'Wund Care': 'Wound Care',
            'Phisycal Therapy': 'Physical Therapy',
            'Med Admin': 'Medication Administration',
            'Check up': 'General Check-up'
        }
        self.df['service_type_cleaned'] = self.df['service_type'].replace(service_corrections)

        # Standardize location abbreviations to full names
        location_corrections = {
            'Esst': 'East',
            'Nrth': 'North',
            'Suth': 'South',
            'Weerst': 'West'
        }
        self.df['visit_location_cleaned'] = self.df['visit_location'].replace(location_corrections)

        print("✓ Categorical variables standardized for consistent analysis")

    def extract_notes_keywords(self):
        """
        Extract meaningful keywords from nurse notes for analysis.
        
        Text analysis of clinical notes can provide insights into visit characteristics.
        This method identifies key phrases that might indicate visit urgency or type.
        """
        print("\n=== EXTRACTING KEYWORDS FROM NURSE NOTES ===")

        # Define patterns for important clinical phrases
        keyword_patterns = {
            'urgent': r'urgent',
            'followup': r'follow.up|revisit|reschedule',
            'stable': r'stable',
            'wound_dressing': r'wound.*dress|dress.*wound',
            'patient_ok': r'nil|patient stable|no issues',
            'lorem': r'lorem ipsum'  # Placeholder text indicator
        }

        # Create boolean columns indicating keyword presence
        for keyword, pattern in keyword_patterns.items():
            self.df[f'note_has_{keyword}'] = self.df['nurse_notes'].str.contains(
                pattern, case=False, na=False, regex=True
            )

        print("✓ Clinical keywords extracted from nurse notes")

    def calculate_visit_duration(self):
        """
        Calculate visit duration and identify statistical outliers.
        
        Duration analysis helps understand efficiency and identify unusual cases
        that might need further investigation.
        """
        print("\n=== CALCULATING VISIT DURATIONS ===")
        
        # Calculate duration in minutes
        self.df['visit_duration_minutes'] = (
            self.df['visit_end_time'] - self.df['visit_start_time']
        ).dt.total_seconds() / 60
        
        # Identify outliers: visits shorter than 1 minute or longer than 8 hours
        # These might be data errors or special cases worth investigating
        self.df['is_duration_outlier'] = (
            (self.df['visit_duration_minutes'] < 1) | 
            (self.df['visit_duration_minutes'] > 480)
        )
        
        outlier_count = self.df['is_duration_outlier'].sum()
        print(f"✓ Found {outlier_count} duration outliers (potential data issues)")
        self.cleaning_report['duration_outliers'] = outlier_count

    def clean_data(self):
        """
        Execute the complete data cleaning pipeline.
        
        This method coordinates all cleaning steps in the proper sequence.
        Returns the cleaned dataframe and a report of cleaning operations.
        """
        print("Starting comprehensive data cleaning pipeline...")
        
        # Execute cleaning steps in logical order
        self.explore_data()                   # Step 1: Understand the data
        self.handle_datetime_inconsistencies() # Step 2: Fix date formats
        self.remove_duplicates()              # Step 3: Remove duplicates
        self.handle_missing_values()          # Step 4: Handle missing data
        self.clean_categorical_variables()    # Step 5: Standardize categories
        self.extract_notes_keywords()         # Step 6: Extract text features
        self.calculate_visit_duration()       # Step 7: Calculate derived metrics

        print("\n=== DATA CLEANING COMPLETED ===")
        print(f"✓ Final dataset shape: {self.df.shape}")
        print(f"✓ Remaining missing values: {self.df.isnull().sum().sum()}")

        return self.df, self.cleaning_report

# Example usage when run directly
if __name__ == "__main__":
    print("Testing data cleaning module...")
    cleaner = DataCleaner('visits.csv')
    cleaned_df, report = cleaner.clean_data()
    cleaned_df.to_csv('visits_cleaned.csv', index=False)
    print("Data cleaning test completed successfully!")
