# RWA Calculator - Bank Al-Maghrib

## Overview

This project is a **Risk-Weighted Assets (RWA) Calculator** application built for Bank Al-Maghrib (Morocco's central bank). It's a Streamlit-based web application that helps financial institutions calculate risk-weighted assets according to Basel banking regulations. The system processes financial data, validates it against regulatory requirements, performs complex RWA calculations across different counterparty segments, and generates comprehensive PDF reports.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a **modular monolithic architecture** with clear separation of concerns:

- **Frontend**: Streamlit web framework providing an interactive dashboard with professional banking UI
- **Backend Logic**: Python modules handling business logic (RWA calculations, data validation, PDF generation)
- **Data Processing**: Pandas-based data manipulation and validation with numpy for numerical operations
- **Visualization**: Plotly for interactive charts and graphs with matplotlib integration
- **Reporting**: ReportLab for PDF generation with integrated chart visualization
- **No Database**: File-based data processing (CSV/Excel uploads)

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Central Streamlit application orchestrating the user interface
- **Features**: 
  - Professional banking-themed UI with custom CSS styling
  - Data upload and display capabilities
  - Real-time RWA calculations and visualizations
  - Integration with all backend modules
  - Wide layout dashboard with collapsible sidebar

### 2. RWA Calculator (`rwa_calculator.py`)
- **Purpose**: Core business logic for calculating Risk-Weighted Assets according to Bank Al-Maghrib regulations
- **Architecture**: Rule-based calculation engine with configurable weighting rules
- **Supported Counterparty Segments**:
  - Sovereign entities (governments, central banks) - 0% to 100% weighting
  - Public organizations - typically 20% weighting
  - Multilateral Development Banks (BMD) - 0% to variable weighting
  - Credit institutions - rating-based weighting
  - Banking entities - location and rating-based weighting
  - Enterprises - rating-based or 100% standard weighting
  - TPE (Very Small Enterprises) - specialized weighting rules
  - Individuals - standardized consumer weighting
  - Real estate - collateral-based weighting

### 3. Data Validator (`data_validator.py`)
- **Purpose**: Ensures data quality and regulatory compliance
- **Required Fields**: 20+ columns including segment classification, ratings, amounts, collateral info
- **Validation Types**:
  - Column presence validation
  - Data type checking
  - Business rule validation (valid ratings: AAA to B-, currencies: MAD/USD/EUR/etc)
  - Regulatory compliance checks
- **Supported Ratings**: Standard credit ratings from AAA to B- plus short-term ratings A-1 to A-3

### 4. PDF Generator (`pdf_generator.py`)
- **Purpose**: Creates professional regulatory reports
- **Features**:
  - Custom styling with Bank Al-Maghrib branding colors
  - Statistical summaries and data tables
  - Integrated chart generation from Plotly/matplotlib
  - Professional document formatting with ReportLab
  - Multi-section reports with proper spacing and typography

## Data Flow

1. **Data Input**: Users upload CSV/Excel files containing loan/credit data
2. **Validation**: Data validator checks for required fields, valid values, and regulatory compliance
3. **Processing**: RWA calculator applies weighting rules based on counterparty segment and ratings
4. **Analysis**: Statistical analysis and risk distribution calculations
5. **Visualization**: Interactive charts showing RWA distribution, segment analysis, and risk metrics
6. **Reporting**: PDF generation with comprehensive analysis and regulatory-compliant formatting

## External Dependencies

### Core Framework
- **Streamlit**: Web application framework for the interactive dashboard
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations for risk calculations

### Visualization
- **Plotly Express/Graph Objects**: Interactive charts and graphs
- **Matplotlib**: Chart generation for PDF reports (using Agg backend)

### PDF Generation
- **ReportLab**: Professional PDF document creation
- **ReportLab Components**: Table styling, paragraph formatting, colors, units

### Data Processing
- **IO/Base64**: File handling and encoding for downloads
- **DateTime**: Timestamp management for reports

## Deployment Strategy

The application is designed as a **single-server deployment** suitable for:

- **Development**: Local Streamlit server (`streamlit run app.py`)
- **Production**: Can be deployed on cloud platforms supporting Python web applications
- **Containerization**: Ready for Docker deployment with requirements.txt
- **Scaling**: Stateless design allows for horizontal scaling if needed

### Key Architectural Decisions

1. **Streamlit Choice**: Selected for rapid development of data-centric applications with minimal frontend complexity
2. **Modular Design**: Separated concerns (validation, calculation, reporting) for maintainability and testing
3. **File-based Processing**: No database dependency simplifies deployment and reduces infrastructure requirements
4. **Professional UI**: Custom CSS provides banking-industry appropriate visual design
5. **Regulatory Compliance**: Built-in validation ensures adherence to Bank Al-Maghrib RWA calculation standards
6. **Comprehensive Reporting**: PDF generation provides audit-trail and regulatory reporting capabilities

## Recent Changes

- **30/07/2025**: Correction critique des règles RWA selon spécifications exactes utilisateur
  - TPE: Pondération fixe 75% (suppression des conditions variables)
  - Souverain: BIS, FMI, BCE, Commission Européenne = 0% systématiquement
  - BMD: Table de pondération spécifique selon notation externe
  - PMAE: Correction des seuils (0-1=0%, 2=20%, 3=50%, 4-6=100%, 7=150%)
  - Variables spécifiques par segment intégrées dans l'affichage

The system prioritizes regulatory accuracy, user experience, and maintainability over complex distributed architecture, making it ideal for financial institutions requiring reliable RWA calculations with professional reporting capabilities.