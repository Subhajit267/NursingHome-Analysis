# [file name]: run_analysis.py
"""
Main execution script for LittleSteps Data Analysis Pipeline
This script orchestrates the complete data analysis pipeline from data generation
through cleaning, analysis, and visualization.
"""

import os
import sys
import pandas as pd

def run_analysis():
    """
    Main function that executes the complete data analysis pipeline.
    This function coordinates all steps: data generation, cleaning, analysis, and reporting.
    """
    
    print("LittleSteps Healthcare Data Analysis Pipeline")
    print("=" * 50)
    print("This project analyzes nurse visit data to optimize healthcare delivery efficiency.")
    
    # Get the current script directory for proper path handling
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(current_dir, 'scripts')
    data_dir = os.path.join(current_dir, 'data')
    outputs_dir = os.path.join(current_dir, 'outputs')
    visualizations_dir = os.path.join(outputs_dir, 'visualizations')
    
    # Create necessary directories if they don't exist
    # This ensures the program works even if folders are missing
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(visualizations_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Add scripts directory to Python path so we can import our custom modules
    sys.path.append(scripts_dir)
    
    try:
        # Step 1: Generate synthetic healthcare data
        # This simulates real-world data with realistic patterns and errors
        print("\nStep 1: Generating synthetic healthcare data...")
        print("Purpose: Create a realistic dataset mimicking nurse visit records")
        
        from generate_data import generate_specific_dataset, save_data
        
        # Generate dataset with 600 records (matching typical healthcare data volume)
        df = generate_specific_dataset()
        visits_csv_path = os.path.join(data_dir, 'visits.csv')
        save_data(df, visits_csv_path)
        print("✓ Synthetic data generated successfully")
        print(f"✓ Created {len(df)} patient visit records")
        
        # Step 2: Clean and preprocess the data
        # Real-world data often has errors that need correction
        print("\nStep 2: Cleaning and preprocessing data...")
        print("Purpose: Handle missing values, standardize formats, and remove duplicates")
        
        from data_cleaning import DataCleaner
        
        # Initialize cleaner and process the dataset
        cleaner = DataCleaner(visits_csv_path)
        cleaned_df, report = cleaner.clean_data()
        cleaned_csv_path = os.path.join(data_dir, 'visits_cleaned.csv')
        cleaned_df.to_csv(cleaned_csv_path, index=False)
        print("✓ Data cleaning completed successfully")
        print(f"✓ Removed {report.get('duplicates_removed', 0)} duplicate records")
        
        # Step 3: Analyze the data and create visualizations
        # This step extracts insights and creates reports
        print("\nStep 3: Analyzing data and creating visualizations...")
        print("Purpose: Extract insights about nurse efficiency and service patterns")
        
        from analysis_visualization import DataAnalyzer
        
        # Perform comprehensive analysis
        analyzer = DataAnalyzer(cleaned_csv_path)
        results = analyzer.generate_report()
        print("✓ Data analysis completed successfully")
        print("✓ Visualizations generated and saved")
        
        # Step 4: Save final analysis results
        # Export results for future reference and reporting
        import json
        final_report_path = os.path.join(outputs_dir, 'final_analysis_report.json')
        with open(final_report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Final summary and success message
        print("\n" + "=" * 50)
        print("ANALYSIS PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("\nGenerated Output Files:")
        print(f"- {visits_csv_path} (Original raw data)")
        print(f"- {cleaned_csv_path} (Cleaned and processed data)")
        print(f"- {visualizations_dir}/ (Analysis charts and graphs)")
        print(f"- {final_report_path} (Complete analysis results)")
        print("\nNext Steps: Review the visualizations and analysis report for insights.")
        
    except Exception as e:
        # Error handling: provide helpful information if something goes wrong
        print(f"\n❌ Error during analysis: {e}")
        print("This might be due to missing files or compatibility issues.")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Standard Python practice: only run if this is the main file
if __name__ == "__main__":
    run_analysis()