# [file name]: scripts/analysis_visualization.py
"""
Data Analysis and Visualization Script
This script performs comprehensive analysis on healthcare visit data
including statistical analysis, performance metrics, and visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import os
warnings.filterwarnings('ignore')

# Set style for better visualizations - using default style for clarity
plt.style.use('default')
sns.set_palette("husl")  # Using husl palette for distinct colors

class DataAnalyzer:
    """
    Main class for analyzing healthcare visit data
    Handles data loading, analysis, and visualization
    """
    def __init__(self, data_path):
        # Load the cleaned data with proper date parsing
        self.df = pd.read_csv(data_path, parse_dates=['visit_start_time', 'visit_end_time'])
        self.analysis_results = {}  # Dictionary to store all analysis results
    
    def descriptive_statistics(self):
        """Calculate descriptive statistics for visit duration - basic overview of data"""
        print("=== DESCRIPTIVE STATISTICS ===")
        
        # Calculate key statistical measures for visit duration
        stats_dict = {
            'mean': self.df['visit_duration_minutes'].mean(),
            'median': self.df['visit_duration_minutes'].median(),
            'std': self.df['visit_duration_minutes'].std(),  # Standard deviation shows variability
            'min': self.df['visit_duration_minutes'].min(),  # Shortest visit
            'max': self.df['visit_duration_minutes'].max(),  # Longest visit
            'count': len(self.df)  # Total number of visits
        }
        
        # Print formatted results for easy reading
        for stat, value in stats_dict.items():
            print(f"{stat.capitalize()}: {value:.2f} minutes")
        
        # Store results for later use in reporting
        self.analysis_results['descriptive_stats'] = stats_dict
        return stats_dict
    
    def analyze_by_service_type(self):
        """Analyze visit duration by service type - compare different medical services"""
        print("\n=== ANALYSIS BY SERVICE TYPE ===")
        
        # Group data by service type and calculate multiple statistics
        service_stats = self.df.groupby('service_type_cleaned')['visit_duration_minutes'].agg([
            'count', 'mean', 'median', 'std'  # Count, average, middle value, and spread
        ]).round(2)  # Round to 2 decimal places for readability
        
        print("Visit duration by service type:")
        print(service_stats)
        
        # Identify which services take the most and least time
        longest_service = service_stats['mean'].idxmax()
        shortest_service = service_stats['mean'].idxmin()
        
        print(f"\nLongest average duration: {longest_service} ({service_stats.loc[longest_service, 'mean']} minutes)")
        print(f"Shortest average duration: {shortest_service} ({service_stats.loc[shortest_service, 'mean']} minutes)")
        
        # Store detailed results for comprehensive reporting
        self.analysis_results['service_analysis'] = {
            'stats': service_stats,
            'longest_service': longest_service,
            'shortest_service': shortest_service
        }
        
        return service_stats
    
    def analyze_by_location(self):
        """Analyze visit duration by location - see if location affects visit time"""
        print("\n=== ANALYSIS BY LOCATION ===")
        
        # Group by location and calculate duration statistics
        location_stats = self.df.groupby('visit_location_cleaned')['visit_duration_minutes'].agg([
            'count', 'mean', 'median', 'std'
        ]).round(2)
        
        print("Visit duration by location:")
        print(location_stats)
        
        # Statistical test to check if location differences are significant
        locations = self.df['visit_location_cleaned'].dropna().unique()
        if len(locations) > 1:
            # Prepare data for ANOVA test (compares means across multiple groups)
            location_groups = [self.df[self.df['visit_location_cleaned'] == loc]['visit_duration_minutes'] for loc in locations]
            f_stat, p_value = stats.f_oneway(*location_groups)  # ANOVA test
            print(f"\nANOVA test for location differences: F-statistic={f_stat:.3f}, p-value={p_value:.3f}")
            
            # Interpret the p-value (common significance level is 0.05)
            if p_value < 0.05:
                print("Significant difference found in visit durations across locations")
            else:
                print("No significant difference found in visit durations across locations")
        else:
            p_value = None
            print("Not enough locations for statistical test")
        
        # Store location analysis results
        self.analysis_results['location_analysis'] = {
            'stats': location_stats,
            'anova_p_value': p_value
        }
        
        return location_stats
    
    def analyze_nurse_performance(self):
        """Analyze nurse performance based on visit duration - efficiency analysis"""
        print("\n=== NURSE PERFORMANCE ANALYSIS ===")
        
        # Only consider nurses with sufficient visits for reliable analysis
        nurse_visit_counts = self.df['nurse_id'].value_counts()
        qualified_nurses = nurse_visit_counts[nurse_visit_counts >= 5].index  # Minimum 5 visits
        
        if len(qualified_nurses) > 0:
            # Calculate performance metrics for each qualified nurse
            nurse_stats = self.df[self.df['nurse_id'].isin(qualified_nurses)].groupby('nurse_id')['visit_duration_minutes'].agg([
                'count', 'mean', 'median', 'std'
            ]).round(2)
            
            # Identify best and worst performers for management review
            top_3_nurses = nurse_stats.nlargest(3, 'mean')  # Nurses with longest average visits
            bottom_3_nurses = nurse_stats.nsmallest(3, 'mean')  # Nurses with shortest average visits
            
            print("Top 3 nurses by average visit duration:")
            print(top_3_nurses)
            print("\nBottom 3 nurses by average visit duration:")
            print(bottom_3_nurses)
            
            # Store nurse performance data
            self.analysis_results['nurse_analysis'] = {
                'stats': nurse_stats,
                'top_3': top_3_nurses.to_dict(),
                'bottom_3': bottom_3_nurses.to_dict()
            }
        else:
            print("No nurses with sufficient visits for analysis")
            self.analysis_results['nurse_analysis'] = {}
        
        return self.analysis_results.get('nurse_analysis', {})
    
    def analyze_notes_insights(self):
        """Extract insights from nurse notes - text analysis for patterns"""
        print("\n=== NURSE NOTES ANALYSIS ===")
        
        # Analyze how specific keywords in notes relate to visit duration
        keyword_columns = [col for col in self.df.columns if col.startswith('note_has_')]
        keyword_analysis = {}
        
        # For each keyword, compare visit durations when keyword is present vs absent
        for keyword_col in keyword_columns:
            keyword = keyword_col.replace('note_has_', '')
            avg_duration = self.df.groupby(keyword_col)['visit_duration_minutes'].mean()
            keyword_analysis[keyword] = avg_duration.to_dict()  # Store as dictionary
        
        print("Average visit duration by keywords in notes:")
        for keyword, durations in keyword_analysis.items():
            print(f"{keyword}: {durations}")
        
        self.analysis_results['notes_analysis'] = keyword_analysis
        return keyword_analysis
    
    def create_visualizations(self):
        """Create comprehensive visualizations - graphs and charts for presentation"""
        print("\n=== CREATING VISUALIZATIONS ===")
        
        try:
            # Set up directory for saving visualization images
            current_dir = os.path.dirname(os.path.abspath(__file__))
            outputs_dir = os.path.join(os.path.dirname(current_dir), 'outputs', 'visualizations')
            os.makedirs(outputs_dir, exist_ok=True)  # Create directory if it doesn't exist
            
            # Create a 2x2 grid of main visualizations
            plt.figure(figsize=(12, 8))
            
            # 1. Histogram of visit durations - shows distribution shape
            plt.subplot(2, 2, 1)
            plt.hist(self.df['visit_duration_minutes'], bins=30, edgecolor='black', alpha=0.7)
            plt.xlabel('Visit Duration (minutes)')
            plt.ylabel('Frequency')
            plt.title('Distribution of Visit Durations')
            plt.axvline(self.df['visit_duration_minutes'].mean(), color='red', linestyle='--', label=f'Mean: {self.df["visit_duration_minutes"].mean():.1f} min')
            plt.legend()
            
            # 2. Average duration by service type - bar chart for comparison
            plt.subplot(2, 2, 2)
            service_means = self.df.groupby('service_type_cleaned')['visit_duration_minutes'].mean().sort_values(ascending=False)
            service_means.plot(kind='bar', color='skyblue')
            plt.xlabel('Service Type')
            plt.ylabel('Average Duration (minutes)')
            plt.title('Average Visit Duration by Service Type')
            plt.xticks(rotation=45, ha='right')  # Rotate labels for readability
            
            # 3. Box plot by location - shows distribution and outliers
            plt.subplot(2, 2, 3)
            sns.boxplot(data=self.df, x='visit_location_cleaned', y='visit_duration_minutes')
            plt.xlabel('Location')
            plt.ylabel('Visit Duration (minutes)')
            plt.title('Visit Duration Distribution by Location')
            
            # 4. Service type distribution - pie chart for proportions
            plt.subplot(2, 2, 4)
            self.df['service_type_cleaned'].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title('Service Type Distribution')
            plt.ylabel('')  # Remove y-axis label for pie chart
            
            plt.tight_layout()  # Adjust spacing between subplots
            main_analysis_path = os.path.join(outputs_dir, 'main_analysis.png')
            plt.savefig(main_analysis_path, dpi=300, bbox_inches='tight')  # High quality save
            plt.show()
            
            # Additional detailed visualizations in a 2x3 grid
            plt.figure(figsize=(15, 10))
            
            # Duration vs time of day - line chart for temporal patterns
            plt.subplot(2, 3, 1)
            self.df['visit_hour'] = self.df['visit_start_time'].dt.hour  # Extract hour from timestamp
            hourly_duration = self.df.groupby('visit_hour')['visit_duration_minutes'].mean()
            hourly_duration.plot(kind='line', marker='o', color='purple')
            plt.xlabel('Hour of Day')
            plt.ylabel('Average Duration (minutes)')
            plt.title('Average Duration by Hour of Day')
            plt.xticks(range(0, 24))  # Show all hours
            
            # Outlier analysis - bar chart showing normal vs outlier visits
            plt.subplot(2, 3, 2)
            outlier_counts = self.df['is_duration_outlier'].value_counts()
            outlier_counts.plot(kind='bar', color=['lightblue', 'salmon'])
            plt.title('Outlier Distribution')
            plt.xlabel('Is Outlier')
            plt.ylabel('Count')
            plt.xticks([0, 1], ['Normal', 'Outlier'], rotation=0)
            
            # Nurse visit counts - bar chart of most active nurses
            plt.subplot(2, 3, 3)
            self.df['nurse_id'].value_counts().head(10).plot(kind='bar', color='lightgreen')
            plt.title('Top 10 Nurses by Number of Visits')
            plt.xlabel('Nurse ID')
            plt.ylabel('Number of Visits')
            plt.xticks(rotation=45)
            
            # Location distribution - which locations are most frequent
            plt.subplot(2, 3, 4)
            self.df['visit_location_cleaned'].value_counts().plot(kind='bar', color='lightcoral')
            plt.title('Visit Location Distribution')
            plt.xlabel('Location')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Notes keyword frequency - which terms appear most in notes
            plt.subplot(2, 3, 5)
            keyword_cols = [col for col in self.df.columns if col.startswith('note_has_')]
            keyword_sums = [self.df[col].sum() for col in keyword_cols]
            keyword_names = [col.replace('note_has_', '') for col in keyword_cols]
            plt.bar(keyword_names, keyword_sums, color='orange')
            plt.title('Frequency of Notes Keywords')
            plt.xlabel('Keyword')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            
            # Duration distribution by service type - boxplot for detailed comparison
            plt.subplot(2, 3, 6)
            sns.boxplot(data=self.df, x='service_type_cleaned', y='visit_duration_minutes')
            plt.xlabel('Service Type')
            plt.ylabel('Visit Duration (minutes)')
            plt.title('Duration Distribution by Service Type')
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            detailed_analysis_path = os.path.join(outputs_dir, 'detailed_analysis.png')
            plt.savefig(detailed_analysis_path, dpi=300, bbox_inches='tight')
            plt.show()
            
            print(f"Visualizations saved to {outputs_dir}")
            
        except Exception as e:
            print(f"Error creating visualizations: {e}")
    
    def generate_report(self):
        """Generate comprehensive analysis report - main function that runs all analyses"""
        print("\n" + "="*50)
        print("COMPREHENSIVE ANALYSIS REPORT")
        print("="*50)
        
        # Execute all analysis methods in sequence
        self.descriptive_statistics()
        self.analyze_by_service_type()
        self.analyze_by_location()
        self.analyze_nurse_performance()
        self.analyze_notes_insights()
        self.create_visualizations()
        
        return self.analysis_results

# Main execution block - runs when script is executed directly
if __name__ == "__main__":
    # Initialize analyzer with cleaned data
    analyzer = DataAnalyzer('visits_cleaned.csv')
    
    # Generate complete report with all analyses
    results = analyzer.generate_report()
    
    # Save results to JSON file for future reference
    import json
    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)  # Pretty print JSON
    
    print("\nAnalysis completed! Results saved to analysis_results.json")