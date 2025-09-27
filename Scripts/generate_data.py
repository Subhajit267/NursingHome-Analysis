# [file name]: scripts/generate_data.py
"""
Synthetic Healthcare Data Generator
This module generates realistic nurse visit data with common data quality issues
found in real healthcare datasets. It creates synthetic data for analysis practice.
 Author: SUBHAJIT HALDER 
       DATE: 27/09/2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_specific_dataset():
    """
    Generates a synthetic dataset of nurse home visits with realistic characteristics.
    
    Returns:
        pandas.DataFrame: A dataframe containing synthetic nurse visit records
    """
    
    # Set random seed for reproducibility - important for academic projects
    np.random.seed(42)
    random.seed(42)
    
    # Define service types with intentional variations (like real-world data)
    # Real healthcare data often has typos and inconsistent naming
    service_types = [
        "Wound Care", "Check up", "Phisycal Therapy", "Wund Care", "Physical Therapy",
        "General Check-up", "Med Admin", "Medication Administration"
    ]
    
    # Location abbreviations that might be used in real systems
    # These simulate common data entry variations
    locations = ["Esst", "Nrth", "South", "West", "Suth", "Weerst", "North", "East"]
    
    # Common nurse notes patterns from actual healthcare records
    notes_options = [
        "Patient stable.", "NA", "Follow-up urgently required", "schedule revisit in 2 days",
        "urgent attention needed", "Wound will be dressed soon", "Nil", "Lorem ipsum text $%^&", ""
    ]
    
    # Generate realistic IDs for nurses and patients
    nurse_ids = [f"N{i:02d}" for i in range(1, 21)]  # 20 nurses
    patient_ids = [f"P{i:03d}" for i in range(1, 101)]  # 100 patients
    
    data = []  # List to store all visit records
    
    # Generate 600 visit records - a reasonable sample size for analysis
    for i in range(1, 601):
        # Create unique visit identifier
        visit_id = f"{i:04d}"
        patient_id = random.choice(patient_ids)
        nurse_id = random.choice(nurse_ids)
        
        # Generate random visit dates within first 3 months of 2024
        month = random.randint(1, 3)   # Jan-Mar 2024
        day = random.randint(1, 28)    # Avoid month-end complications
        hour = random.randint(0, 23)   # Any hour of day
        minute = random.randint(0, 59) # Any minute
        
        # Create visit start time
        start_time = datetime(2024, month, day, hour, minute)
        
        # Generate realistic visit duration (1 minute to 8 hours)
        duration_minutes = random.randint(1, 480)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Randomly select service type and location
        service_type = random.choice(service_types)
        visit_location = random.choice(locations)
        nurse_notes = random.choice(notes_options)
        
        # Simulate real-world data entry inconsistencies
        # Different staff might use different date formats
        start_time_format = random.choice([
            lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'),  # ISO format
            lambda dt: dt.strftime('%d-%m-%Y %H:%M'),     # European format
            lambda dt: dt.strftime('%m-%d-%Y %H:%M')      # US format
        ])
        
        end_time_format = random.choice([
            lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'),
            lambda dt: dt.strftime('%d/%m/%Y %H:%M'),     # Mixed separators
            lambda dt: dt.strftime('%m/%d/%Y %H:%M')
        ])
        
        # Simulate common data issues: missing end times (5% of cases)
        if random.random() < 0.05:
            end_time_str = ""  # Missing data
        else:
            end_time_str = end_time_format(end_time)
        
        # Simulate missing notes (10% of cases)
        if random.random() < 0.1:
            nurse_notes = ""  # Empty notes field
        
        # Create visit record dictionary
        visit_record = {
            'visit_id': visit_id,
            'patient_id': patient_id,
            'nurse_id': nurse_id,
            'visit_start_time': start_time_format(start_time),
            'visit_end_time': end_time_str,
            'service_type': service_type,
            'visit_location': visit_location,
            'nurse_notes': nurse_notes
        }
        
        data.append(visit_record)
    
    # Convert list of dictionaries to pandas DataFrame
    df = pd.DataFrame(data)
    
    # Add specific duplicate records to simulate real data issues
    # In healthcare systems, duplicate entries sometimes occur
    duplicates_indices = [51, 104, 433]
    for idx in duplicates_indices:
        if idx < len(df):
            df = pd.concat([df, df.iloc[[idx-1]]], ignore_index=True)
    
    # Reindex to maintain proper visit_id order after adding duplicates
    df = df.reset_index(drop=True)
    df['visit_id'] = [f"{i+1:04d}" for i in range(len(df))]
    
    return df

def save_data(df, filename):
    """
    Saves the generated dataframe to a CSV file.
    
    Args:
        df (pandas.DataFrame): The dataframe to save
        filename (str): Path where the CSV file should be saved
    """
    df.to_csv(filename, index=False)
    print(f"✓ Data saved to {filename} with {len(df)} records")
    print("✓ This file contains synthetic nurse visit data for analysis")

# Test the data generation if this file is run directly
if __name__ == "__main__":
    print("Testing data generation module...")
    df = generate_specific_dataset()
    save_data(df, 'visits.csv')
    print("Data generation test completed successfully!")
