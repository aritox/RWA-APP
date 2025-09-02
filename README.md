# RWA Calculator - Bank Al-Maghrib

## Overview
This project is a **Risk-Weighted Assets (RWA) Calculator** application built for **Bank Al-Maghrib** (Morocco's central bank).  
It's a **Streamlit-based web application** that helps financial institutions calculate risk-weighted assets according to **Basel banking regulations**.  

The system processes financial data, validates it against regulatory requirements, performs complex RWA calculations across different counterparty segments, and generates comprehensive PDF reports.

---

## System Architecture
The application follows a **modular monolithic architecture** with clear separation of concerns:

- **Frontend**: Streamlit web framework providing an interactive dashboard with professional banking UI  
- **Backend Logic**: Python modules handling business logic (RWA calculations, data validation, PDF generation)  
- **Data Processing**: Pandas-based data manipulation and validation with NumPy for numerical operations  
- **Visualization**: Plotly for interactive charts and graphs with Matplotlib integration  
- **Reporting**: ReportLab for PDF generation with integrated chart visualization  
- **No Database**: File-based data processing (CSV/Excel uploads)  

---

## Key Components

### 1. Main Application (`app.py`)
- Central Streamlit application orchestrating the user interface  
- Banking-themed UI with custom CSS styling  
- Data upload & display  
- Real-time RWA calculations & visualizations  
- Integration with all backend modules  

### 2. RWA Calculator (`rwa_calculator.py`)
- Core business logic for calculating RWAs according to Bank Al-Maghrib regulations  
- Rule-based calculation engine with configurable weighting rules  

**Supported Counterparty Segments**:
- Sovereign entities (0% to 100% weighting)  
- Public organizations (typically 20%)  
- Multilateral Development Banks (BMD)  
- Credit institutions (rating-based)  
- Enterprises (rating-based or 100% standard)  
- TPE (Very Small Enterprises, fixed 75%)  
- Individuals (consumer credit)  
- Real estate (collateral-based)  

### 3. Data Validator (`data_validator.py`)
- Ensures data quality and regulatory compliance  
- 20+ required fields (segment classification, ratings, amounts, collateral info)  
- Validation: column presence, data type, business rules, regulatory checks  
- Supported ratings: AAA → B-, short-term ratings A-1 to A-3  

### 4. PDF Generator (`pdf_generator.py`)
- Creates professional reports in PDF format  
- Bank Al-Maghrib branding colors  
- Statistical summaries & tables  
- Integrated charts from Plotly/Matplotlib  
- Multi-section reports with clear formatting  

---

## Data Flow
1. Upload CSV/Excel file with exposure data  
2. Validate against regulatory requirements  
3. Apply RWA weighting rules  
4. Perform statistical analysis  
5. Generate interactive charts  
6. Export detailed PDF reports  

---

## External Dependencies
- **Core**: Streamlit, Pandas, NumPy  
- **Visualization**: Plotly, Matplotlib  
- **PDF**: ReportLab  
- **Utilities**: IO/Base64, DateTime  

---

## Deployment
- Local:  
  ```bash
  streamlit run app.py
