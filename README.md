# 🏥 Nurse Scheduling Efficiency Analysis

## 📌 Project Overview
This project analyzes **nurse scheduling and patient visit efficiency** for **LittleSteps**, an at-home healthcare startup.  
The main goals are:
- Understand **patterns in patient visit duration**  
- Identify **efficiency gaps** across nurses, service types, and locations  
- Provide **data-driven recommendations** for better scheduling and patient care  

---

## 📂 Repository Structure
```
NursingHome-Analysis/
├── data/                # Raw and cleaned data files
├── scripts/             # Python scripts for data processing
├── notebooks/           # Jupyter notebooks for analysis
├── outputs/             # Results, reports, and visualizations
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/NursingHome-analysis.git
cd littlesteps-analysis
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate & Clean Data
```bash
# Generate synthetic data
python scripts/generate_data.py

# Clean the data
python scripts/data_cleaning.py

# Run analysis and generate visualizations
python scripts/analysis_visualization.py
```

### 4. Run via Jupyter Notebook
```bash
jupyter notebook notebooks/analysis.ipynb
```

---

## 📊 Key Findings

### ⏱️ Visit Duration Patterns
- **Average duration**: ~45 minutes  
- Strong variation across **service types**  
- **Physical Therapy** sessions are longest  
- **General Check-ups** are shortest  

### 🌍 Geographical Variations
- Duration differs significantly across regions  
- **West region** shows distinct patterns  

### 👩‍⚕️ Nurse Performance
- Top 3 and bottom 3 performers identified  
- Some nurses consistently complete visits faster  
- Insights for **best-practice sharing**  

### 📝 Notes Analysis
- Keywords like **“urgent”** & **“infection”** → longer visits  
- **“Stable”** & **“improvement”** → normal durations  

---

## 🧹 Data Cleaning Approach

### ✅ Handling Missing Values
- **Visit end times**: Imputed using service-type averages  
- **Nurse notes**: Filled with `"No notes provided"`  

### 🚩 Outlier Management
- Defined visit duration bounds: **5 minutes → 4 hours**  
- Outliers flagged (kept for analysis context)  

### 🛠️ Other Fixes
- Removed duplicate records  
- Standardized inconsistent datetime formats  
- Cleaned categorical variables  
- Extracted **keywords from notes**  

---

## 📈 Visualizations
The analysis includes:
- Visit duration distribution  
- Service type comparisons  
- Geographical variations  
- Nurse performance metrics  
- Time-of-day visit patterns  
- Notes keyword correlations  

---

## ⚖️ Assumptions & Limitations

### Assumptions
- Synthetic data closely simulates real-world scenarios  
- 5-minute minimum and 4-hour maximum are reasonable bounds  
- Keywords in nurse notes provide meaningful signals  

### Limitations
- Synthetic data may not capture all real-world complexities  
- Outliers may reflect legitimate long/short visits  
- Basic keyword analysis (no advanced NLP yet)  

---

## 🚀 Recommendations

### 🔧 Resource Optimization
- Allocate **more time for Physical Therapy visits**  
- Standardize durations for common service types  

### 📉 Performance Improvement
- Share practices from **top-performing nurses**  
- Investigate **location-specific delays**  

### 🏗️ Process Enhancements
- Improve **data collection quality**  
- Create standardized **note-taking templates**  
- Regular review of visit duration metrics  

---

## 🔮 Future Work
- Advanced NLP for deeper notes analysis  
- Incorporate **patient satisfaction metrics**  
- Predictive models for **visit duration**  
- Real-time monitoring & alerts for scheduling  

---

## 📬 Contact
For questions or contributions, please reach out to:
-Subhajit Halder
-mail:subhajithalder267@outlook.com
