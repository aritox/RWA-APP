import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
from rwa_calculator import RWACalculator
from pdf_generator import PDFGenerator
from data_validator import DataValidator

# Configuration de la page
st.set_page_config(
    page_title="RWA Calculator - Bank Al-Maghrib",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un look professionnel
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #FF6B35;
    }
    .counterparty-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .counterparty-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialiser les variables de session"""
    if 'df' not in st.session_state:
        st.session_state['df'] = None
    if 'rwa_calculated' not in st.session_state:
        st.session_state['rwa_calculated'] = False
    if 'rwa_results' not in st.session_state:
        st.session_state['rwa_results'] = None
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'upload'

def validate_columns(df):
    """Valider que toutes les colonnes requises sont présentes"""
    required_columns = [
        'segment', 'sous_segment', 'monnaie', 'note_externe', 'note_pmae',
        'remboursement_budget', 'creance_souffrance', 'echeance_initiale',
        'echeance', 'note_inf_1_an', 'note_sup_1_an', 'accord_bank_maghrib',
        'appart_grpe', 'dette_banc', 'montant', 'garanti_hypotheque',
        'usage', 'convention_etat', 'valeur_bien_hypoteq', 
        'valeur_encours_creance', 'provision_constitue'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    return missing_columns

def display_upload_page():
    """Page d'upload des données"""
    st.markdown('<div class="main-header"><h1>🏦 RWA Calculator - Bank Al-Maghrib</h1><p>Calculateur de Risk Weighted Assets</p></div>', unsafe_allow_html=True)
    
    st.markdown("### 📁 Upload de la Base de Données")
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier Excel ou CSV",
        type=['xlsx', 'xls', 'csv'],
        help="Le fichier doit contenir toutes les colonnes requises pour le calcul RWA"
    )
    
    if uploaded_file is not None:
        try:
            # Lecture du fichier
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Validation des colonnes
            missing_columns = validate_columns(df)
            
            if missing_columns:
                st.error(f"❌ Colonnes manquantes: {', '.join(missing_columns)}")
                st.info("📋 Colonnes requises: segment, sous_segment, monnaie, note_externe, note_pmae, remboursement_budget, creance_souffrance, echeance_initiale, echeance, note_inf_1_an, note_sup_1_an, accord_bank_maghrib, appart_grpe, dette_banc, montant, garanti_hypotheque, usage, convention_etat, valeur_bien_hypoteq, valeur_encours_creance, provision_constitue")
            else:
                st.success(f"✅ Fichier chargé avec succès! {len(df)} lignes trouvées.")
                st.session_state['df'] = df
                st.session_state['current_page'] = 'analysis'
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier: {str(e)}")

def display_data_analysis():
    """Page d'analyse des données"""
    df = st.session_state['df']
    
    st.markdown('<div class="main-header"><h1>📊 Analyse des Données</h1></div>', unsafe_allow_html=True)
    
    # Boutons de navigation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👁️ Voir Base de Données", use_container_width=True):
            st.session_state['show_data'] = True
    
    with col2:
        if st.button("📈 Statistiques Descriptives", use_container_width=True):
            st.session_state['show_stats'] = True
    
    with col3:
        if st.button("📄 Export PDF Statistiques", use_container_width=True):
            generate_stats_pdf(df)
    
    with col4:
        if st.button("🧮 Calculer RWA", use_container_width=True):
            st.session_state['current_page'] = 'rwa_calculation'
            st.rerun()
    
    # Affichage de la base de données
    if st.session_state.get('show_data', False):
        st.markdown("### 📋 Base de Données")
        st.dataframe(df, use_container_width=True, height=400)
        
        # Statistiques générales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Lignes", len(df))
        with col2:
            st.metric("Total Exposition", f"{df['montant'].sum():,.0f} MAD")
        with col3:
            st.metric("Segments Uniques", df['segment'].nunique())
        with col4:
            st.metric("Contreparties", df['sous_segment'].nunique())
    
    # Statistiques descriptives
    if st.session_state.get('show_stats', False):
        display_descriptive_stats(df)

def display_descriptive_stats(df):
    """Afficher les statistiques descriptives"""
    st.markdown("### 📊 Statistiques Descriptives")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par type de contrepartie
        segment_counts = df['segment'].value_counts()
        fig_pie = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title="Répartition par Type de Contrepartie",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Histogramme des notes externes
        note_counts = df['note_externe'].value_counts().sort_index()
        fig_hist = px.bar(
            x=note_counts.index,
            y=note_counts.values,
            title="Distribution des Notes Externes",
            labels={'x': 'Note Externe', 'y': 'Nombre d\'Expositions'},
            color=note_counts.values,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Tableau de répartition
    st.markdown("### 📋 Répartition Détaillée")
    segment_analysis = df.groupby(['segment', 'sous_segment']).agg({
        'montant': ['count', 'sum'],
        'note_externe': lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A'
    }).round(2)
    
    segment_analysis.columns = ['Nombre', 'Montant Total (MAD)', 'Note Dominante']
    st.dataframe(segment_analysis, use_container_width=True)

def generate_stats_pdf(df):
    """Générer le PDF des statistiques"""
    try:
        pdf_gen = PDFGenerator()
        pdf_buffer = pdf_gen.generate_statistics_report(df)
        
        # Création du lien de téléchargement
        b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="statistiques_rwa.pdf">📄 Télécharger le rapport PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("✅ Rapport PDF généré avec succès!")
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la génération du PDF: {str(e)}")

def display_rwa_calculation():
    """Page de calcul RWA"""
    df = st.session_state['df']
    
    st.markdown('<div class="main-header"><h1>🧮 Calcul des Risk Weighted Assets</h1></div>', unsafe_allow_html=True)
    
    # Bouton retour
    if st.button("← Retour à l'Analyse", use_container_width=False):
        st.session_state['current_page'] = 'analysis'
        st.rerun()
    
    # Calculer RWA si pas encore fait
    if not st.session_state['rwa_calculated']:
        with st.spinner("Calcul des RWA en cours..."):
            calculator = RWACalculator()
            results = calculator.calculate_rwa(df)
            st.session_state['rwa_results'] = results
            st.session_state['rwa_calculated'] = True
    
    results = st.session_state['rwa_results']
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Expositions</h3>
            <h2>{:,.0f}</h2>
            <p>Nombre d'expositions</p>
        </div>
        """.format(len(df)), unsafe_allow_html=True)
    
    with col2:
        total_rwa = results['total_rwa']
        st.markdown("""
        <div class="metric-card">
            <h3>Total RWA</h3>
            <h2>{:,.2f} MAD</h2>
            <p>Risk Weighted Assets</p>
        </div>
        """.format(total_rwa), unsafe_allow_html=True)
    
    with col3:
        avg_weighting = results['average_weighting']
        st.markdown("""
        <div class="metric-card">
            <h3>Pondération Moyenne</h3>
            <h2>{:.1f}%</h2>
            <p>Pondération moyenne</p>
        </div>
        """.format(avg_weighting), unsafe_allow_html=True)
    
    with col4:
        unique_types = results['unique_counterparty_types']
        st.markdown("""
        <div class="metric-card">
            <h3>Types Uniques</h3>
            <h2>{}</h2>
            <p>Types de contreparties</p>
        </div>
        """.format(unique_types), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Analyse par type de contrepartie
    st.markdown("### 🏢 Analyse par Type de Contrepartie")
    
    counterparty_analysis = results['counterparty_analysis']
    
    # Affichage des cartes de contreparties
    for segment, data in counterparty_analysis.items():
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            if st.button(f"📊 {segment}", key=f"btn_{segment}", use_container_width=True):
                display_counterparty_detail(segment, data)
        
        with col2:
            st.metric("Nb", data['count'])
        with col3:
            st.metric("RWA", f"{data['total_rwa']:,.0f}")
        with col4:
            st.metric("Pond.", f"{data['avg_weighting']:.1f}%")

def display_counterparty_detail(segment, data):
    """Afficher les détails d'une contrepartie"""
    st.markdown(f"### 📋 Détail - {segment}")
    
    # Récupérer les données filtrées
    df = st.session_state['df']
    segment_data = df[df['segment'] == segment].copy()
    
    # Ajouter les calculs RWA
    calculator = RWACalculator()
    segment_results = calculator.calculate_rwa(segment_data)
    
    # Afficher le tableau détaillé
    st.dataframe(segment_data, use_container_width=True)
    
    # Statistiques du segment
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Exposition", f"{segment_data['montant'].sum():,.0f} MAD")
    with col2:
        st.metric("Total RWA", f"{segment_results['total_rwa']:,.0f} MAD")
    with col3:
        st.metric("Pondération Moyenne", f"{segment_results['average_weighting']:.1f}%")

def main():
    """Fonction principale"""
    initialize_session_state()
    
    # Navigation entre les pages
    if st.session_state['current_page'] == 'upload':
        display_upload_page()
    elif st.session_state['current_page'] == 'analysis':
        display_data_analysis()
    elif st.session_state['current_page'] == 'rwa_calculation':
        display_rwa_calculation()

if __name__ == "__main__":
    main()
