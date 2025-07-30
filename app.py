import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime

# Import custom modules
from data_validator import DataValidator
from rwa_calculator import RWACalculator
from pdf_generator import PDFGenerator

# Page configuration
st.set_page_config(
    page_title="RWA Calculator - Bank Al-Maghrib",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional banking interface
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 600;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #FF6B35;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e3c72;
        margin: 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Counterparty cards */
    .counterparty-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
    }
    
    .counterparty-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    .counterparty-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3c72;
        margin-bottom: 0.5rem;
    }
    
    .counterparty-amount {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2a5298;
        margin-bottom: 0.3rem;
    }
    
    .counterparty-subtitle {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e3c72;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #FF6B35;
    }
    
    /* Navigation */
    .nav-button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 5px;
        font-weight: 600;
        cursor: pointer;
        margin: 0.5rem;
    }
    
    .nav-button:hover {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
    }
    
    /* Data table styling */
    .dataframe {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
    
    /* Upload section */
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin: 2rem 0;
    }
    
    /* Alert styling */
    .alert-success {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .alert-error {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'upload'
if 'data' not in st.session_state:
    st.session_state.data = None
if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None
if 'rwa_results' not in st.session_state:
    st.session_state.rwa_results = None

# Initialize components
validator = DataValidator()
calculator = RWACalculator()
pdf_generator = PDFGenerator()

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🏦 Calculateur RWA</h1>
        <p>Bank Al-Maghrib - Analyse des Actifs Pondérés par les Risques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("📁 Téléchargement", key="nav_upload"):
            st.session_state.page = 'upload'
    
    with col2:
        if st.button("📊 Analyse", key="nav_analysis", disabled=st.session_state.data is None):
            st.session_state.page = 'analysis'
    
    with col3:
        if st.button("🧮 Calculer RWA", key="nav_rwa", disabled=st.session_state.data is None):
            st.session_state.page = 'rwa'
    
    with col4:
        if st.button("📄 Rapports", key="nav_reports", disabled=st.session_state.rwa_results is None):
            st.session_state.page = 'reports'
    
    st.markdown("---")
    
    # Page routing
    if st.session_state.page == 'upload':
        show_upload_page()
    elif st.session_state.page == 'analysis':
        show_analysis_page()
    elif st.session_state.page == 'rwa':
        show_rwa_page()
    elif st.session_state.page == 'reports':
        show_reports_page()

def show_upload_page():
    st.markdown('<div class="section-header">Téléchargement des Données</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="upload-section">
        <h3>📋 Instructions</h3>
        <p>Téléchargez un fichier Excel (.xlsx) ou CSV (.csv) contenant les données d'exposition.</p>
        <p>Le fichier doit contenir les colonnes suivantes :</p>
        <ul style="text-align: left; display: inline-block;">
            <li>segment, sous_segment, monnaie, note_externe, note_pmae</li>
            <li>remboursement_budget, creance_souffrance, echeance_initiale, echeance</li>
            <li>note_inf_1_an, note_sup_1_an, accord_bank_maghrib, appart_grpe</li>
            <li>dette_banc, montant, garanti_hypotheque, usage, convention_etat</li>
            <li>valeur_bien_hypoteq, valeur_encours_creance, provision_constitue</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier",
        type=['xlsx', 'csv'],
        help="Formats acceptés: Excel (.xlsx) ou CSV (.csv)"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ Fichier chargé avec succès! {len(df)} lignes détectées.")
            
            # Validate data
            with st.spinner("Validation des données en cours..."):
                validation_results = validator.validate_dataframe(df)
                
            # Store in session state
            st.session_state.data = df
            st.session_state.validation_results = validation_results
            
            # Show validation results
            if validation_results['errors']:
                st.error("❌ Erreurs critiques détectées:")
                for error in validation_results['errors']:
                    st.write(f"• {error}")
            
            if validation_results['warnings']:
                st.warning("⚠️ Avertissements:")
                for warning in validation_results['warnings']:
                    st.write(f"• {warning}")
            
            if validation_results['info']:
                st.info("ℹ️ Informations:")
                for info in validation_results['info']:
                    st.write(f"• {info}")
            
            # Show data preview
            st.markdown('<div class="section-header">Aperçu des Données</div>', unsafe_allow_html=True)
            st.dataframe(df.head(10), use_container_width=True)
            
            # Clean data if no critical errors
            if not validation_results['errors']:
                cleaned_df = validator.clean_dataframe(df)
                st.session_state.data = cleaned_df
                st.success("✅ Données nettoyées et prêtes pour l'analyse!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Analyser les données", type="primary"):
                        st.session_state.page = 'analysis'
                        st.rerun()
                
                with col2:
                    if st.button("🧮 Calculer RWA directement", type="secondary"):
                        st.session_state.page = 'rwa'
                        st.rerun()
            
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du fichier: {str(e)}")

def show_analysis_page():
    if st.session_state.data is None:
        st.error("Aucune donnée disponible. Veuillez d'abord télécharger un fichier.")
        return
    
    df = st.session_state.data
    
    st.markdown('<div class="section-header">Analyse Statistique des Données</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Total Expositions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_amount = df['montant'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_amount:,.0f}</div>
            <div class="metric-label">Exposition Totale (MAD)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        unique_segments = df['segment'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_segments}</div>
            <div class="metric-label">Types de Contreparties</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_amount = df['montant'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_amount:,.0f}</div>
            <div class="metric-label">Exposition Moyenne (MAD)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Répartition par Segment</div>', unsafe_allow_html=True)
        segment_counts = df['segment'].value_counts()
        fig_pie = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title="Distribution des Segments"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-header">Exposition par Segment</div>', unsafe_allow_html=True)
        segment_amounts = df.groupby('segment')['montant'].sum().sort_values(ascending=False)
        fig_bar = px.bar(
            x=segment_amounts.index,
            y=segment_amounts.values,
            title="Montants par Segment (MAD)"
        )
        fig_bar.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed analysis
    st.markdown('<div class="section-header">Analyse Détaillée</div>', unsafe_allow_html=True)
    
    # Segment analysis
    segment_analysis = df.groupby('segment').agg({
        'montant': ['count', 'sum', 'mean'],
        'note_externe': lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A'
    }).round(0)
    
    segment_analysis.columns = ['Nombre', 'Total (MAD)', 'Moyenne (MAD)', 'Note Dominante']
    st.dataframe(segment_analysis, use_container_width=True)
    
    # Rating distribution
    if 'note_externe' in df.columns:
        st.markdown('<div class="section-header">Distribution des Notations</div>', unsafe_allow_html=True)
        rating_dist = df['note_externe'].value_counts().head(10)
        fig_rating = px.bar(
            x=rating_dist.values,
            y=rating_dist.index,
            orientation='h',
            title="Top 10 des Notations Externes"
        )
        st.plotly_chart(fig_rating, use_container_width=True)
    
    # Next step button
    st.markdown("---")
    if st.button("🧮 Procéder au Calcul RWA", type="primary", use_container_width=True):
        st.session_state.page = 'rwa'
        st.rerun()

def show_rwa_page():
    if st.session_state.data is None:
        st.error("Aucune donnée disponible. Veuillez d'abord télécharger un fichier.")
        return
    
    df = st.session_state.data
    
    st.markdown('<div class="section-header">Calcul des Actifs Pondérés par les Risques (RWA)</div>', unsafe_allow_html=True)
    
    # Calculate RWA if not already done
    if st.session_state.rwa_results is None:
        with st.spinner("Calcul des RWA en cours..."):
            rwa_results = calculator.calculate_rwa(df)
            st.session_state.rwa_results = rwa_results
    
    rwa_results = st.session_state.rwa_results
    results_df = rwa_results['results_df']
    
    # Key RWA metrics - exactly like the reference image
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #2196F3; font-size: 2rem;">📊</div>
            <div class="metric-label">Total Expositions</div>
            <div class="metric-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #4CAF50; font-size: 2rem;">💰</div>
            <div class="metric-label">Total RWA</div>
            <div class="metric-value">{rwa_results['total_rwa']:,.2f} MAD</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #FF9800; font-size: 2rem;">%</div>
            <div class="metric-label">Pondération Moyenne</div>
            <div class="metric-value">{rwa_results['average_weighting']:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #9C27B0; font-size: 2rem;">🏢</div>
            <div class="metric-label">Types Uniques</div>
            <div class="metric-value">{rwa_results['unique_counterparty_types']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Counterparty analysis section - matching the reference image
    st.markdown('<div class="section-header">Analyse par Type de Contrepartie</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; margin-bottom: 2rem;">Cliquez sur un type pour voir l\'analyse détaillée</p>', unsafe_allow_html=True)
    
    # Create counterparty cards in a grid layout
    counterparty_data = []
    for segment, analysis in rwa_results['counterparty_analysis'].items():
        counterparty_data.append({
            'segment': segment,
            'count': analysis['count'],
            'total_exposure': analysis['total_exposure'],
            'total_rwa': analysis['total_rwa'],
            'avg_weighting': analysis['avg_weighting']
        })
    
    # Sort by total exposure
    counterparty_data.sort(key=lambda x: x['total_exposure'], reverse=True)
    
    # Create grid of cards
    cols = st.columns(3)
    colors = ['#4CAF50', '#607D8B', '#607D8B', '#2196F3', '#9C27B0', '#607D8B', '#607D8B']
    
    for i, cp_data in enumerate(counterparty_data):
        col_idx = i % 3
        color = colors[i % len(colors)]
        
        with cols[col_idx]:
            # Create clickable card
            card_key = f"card_{cp_data['segment']}"
            
            if st.button(
                f"🏢\n{cp_data['segment'].title()}\n{cp_data['count']} expositions\n{cp_data['total_exposure']:,.0f} MAD",
                key=card_key,
                help=f"Cliquez pour voir les détails de {cp_data['segment']}"
            ):
                st.session_state.selected_segment = cp_data['segment']
    
    # Detailed analysis for selected segment
    if 'selected_segment' in st.session_state:
        selected_segment = st.session_state.selected_segment
        
        st.markdown(f'<div class="section-header">Détail - {selected_segment.title()}</div>', unsafe_allow_html=True)
        
        # Filter data for selected segment
        segment_data = results_df[results_df['segment'] == selected_segment]
        segment_analysis = rwa_results['counterparty_analysis'][selected_segment]
        
        # Summary for selected segment
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="color: #1e3c72; margin-bottom: 1rem;">{selected_segment.title()}</h4>
                <p><strong>{segment_analysis['count']}</strong> expositions</p>
                <p style="font-size: 1.5rem; color: #2a5298; font-weight: bold; margin: 1rem 0;">
                    {segment_analysis['total_exposure']:,.0f} MAD
                </p>
                <p style="font-size: 0.9rem; color: #666;">Pondération: {segment_analysis['avg_weighting']:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h4 style="color: #1e3c72; margin-bottom: 1rem;">État Étranger</h4>
                <p><strong>1</strong> expositions</p>
                <p style="font-size: 1.5rem; color: #2a5298; font-weight: bold; margin: 1rem 0;">
                    {segment_analysis['total_rwa']:,.0f} MAD
                </p>
                <p style="font-size: 0.9rem; color: #666;">Pondération: 50%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Detailed table
        st.markdown("### Détail par Exposition")
        
        # Format the detailed table
        display_df = segment_data.copy()
        display_df['montant'] = display_df['montant'].apply(lambda x: f"{x:,.0f}")
        display_df['ponderation'] = display_df['ponderation'].apply(lambda x: f"{x:.0%}")
        display_df['rwa'] = display_df['rwa'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(
            display_df[['sous_segment', 'monnaie', 'note_externe', 'montant', 'ponderation', 'rwa']],
            use_container_width=True,
            column_config={
                'sous_segment': 'Sous-segment',
                'monnaie': 'Monnaie',
                'note_externe': 'Note',
                'montant': 'Exposition',
                'ponderation': 'Pondération',
                'rwa': 'RWA'
            }
        )
        
        # Summary for selected segment
        st.markdown(f"""
        <div style="background: #fff; padding: 2rem; border-radius: 10px; border: 1px solid #e0e0e0; margin-top: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="color: #1e3c72; margin: 0;">Résumé RWA - {selected_segment.title()}</h4>
                    <p style="color: #666; margin: 0.5rem 0 0 0;">Calcul basé sur les règles Bâle II/III</p>
                </div>
                <div style="text-align: right;">
                    <p style="font-size: 2rem; font-weight: bold; color: #e53e3e; margin: 0;">
                        {segment_analysis['total_rwa']:,.2f} MAD
                    </p>
                    <p style="color: #666; margin: 0.5rem 0 0 0;">Total RWA calculé</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Overall RWA summary chart
    st.markdown('<div class="section-header">Répartition RWA par Type de Contrepartie</div>', unsafe_allow_html=True)
    
    # Create RWA distribution chart
    rwa_by_segment = []
    labels = []
    values = []
    
    for segment, analysis in rwa_results['counterparty_analysis'].items():
        labels.append(segment.title())
        values.append(analysis['total_rwa'])
    
    fig = px.pie(
        values=values,
        names=labels,
        title="Distribution du RWA Total par Segment"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Navigation to reports
    st.markdown("---")
    if st.button("📄 Générer les Rapports", type="primary", use_container_width=True):
        st.session_state.page = 'reports'
        st.rerun()

def show_reports_page():
    if st.session_state.rwa_results is None:
        st.error("Aucun calcul RWA disponible. Veuillez d'abord calculer les RWA.")
        return
    
    st.markdown('<div class="section-header">Génération de Rapports</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Rapport Statistique</h3>
            <p>Analyse détaillée des données d'exposition avec graphiques et tableaux.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Télécharger Rapport Statistique", use_container_width=True):
            try:
                pdf_buffer = pdf_generator.generate_statistics_report(st.session_state.data)
                
                st.download_button(
                    label="💾 Télécharger PDF Statistique",
                    data=pdf_buffer.getvalue(),
                    file_name=f"rapport_statistique_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Rapport statistique généré avec succès!")
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Rapport RWA</h3>
            <p>Rapport complet des calculs RWA selon les normes Bank Al-Maghrib.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🧮 Télécharger Rapport RWA", use_container_width=True):
            try:
                pdf_buffer = pdf_generator.generate_rwa_report(
                    st.session_state.data, 
                    st.session_state.rwa_results
                )
                
                st.download_button(
                    label="💾 Télécharger PDF RWA",
                    data=pdf_buffer.getvalue(),
                    file_name=f"rapport_rwa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Rapport RWA généré avec succès!")
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")
    
    # Export raw data
    st.markdown('<div class="section-header">Export des Données</div>', unsafe_allow_html=True)
    
    if st.session_state.rwa_results:
        results_df = st.session_state.rwa_results['results_df']
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        results_df.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label="📁 Télécharger Résultats (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"resultats_rwa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.info("💡 Le fichier CSV contient tous les calculs détaillés ligne par ligne.")

if __name__ == "__main__":
    main()
