import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

class PDFGenerator:
    """Générateur de rapports PDF pour les analyses RWA"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurer les styles personnalisés"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=1  # Center
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12
        )
    
    def generate_statistics_report(self, df):
        """Générer le rapport statistiques en PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Construction du contenu
        story = []
        
        # Titre
        title = Paragraph("Rapport Statistique - Analyse RWA", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Date de génération
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        date_para = Paragraph(f"Généré le: {date_str}", self.normal_style)
        story.append(date_para)
        story.append(Spacer(1, 30))
        
        # Statistiques générales
        story.append(Paragraph("1. Statistiques Générales", self.subtitle_style))
        
        stats_data = [
            ['Métrique', 'Valeur'],
            ['Nombre total d\'expositions', f"{len(df):,}"],
            ['Exposition totale', f"{df['montant'].sum():,.0f} MAD"],
            ['Nombre de segments', f"{df['segment'].nunique()}"],
            ['Nombre de contreparties', f"{df['sous_segment'].nunique()}"]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 30))
        
        # Répartition par segment
        story.append(Paragraph("2. Répartition par Type de Contrepartie", self.subtitle_style))
        
        segment_counts = df['segment'].value_counts()
        segment_data = [['Segment', 'Nombre', 'Pourcentage']]
        
        for segment, count in segment_counts.items():
            percentage = (count / len(df) * 100)
            segment_data.append([segment, f"{count:,}", f"{percentage:.1f}%"])
        
        segment_table = Table(segment_data)
        segment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(segment_table)
        story.append(Spacer(1, 30))
        
        # Distribution des notes externes
        story.append(Paragraph("3. Distribution des Notes Externes", self.subtitle_style))
        
        note_counts = df['note_externe'].value_counts().sort_index()
        note_data = [['Note Externe', 'Nombre', 'Pourcentage']]
        
        for note, count in note_counts.items():
            percentage = (count / len(df) * 100)
            note_data.append([note, f"{count:,}", f"{percentage:.1f}%"])
        
        note_table = Table(note_data)
        note_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(note_table)
        story.append(Spacer(1, 30))
        
        # Analyse détaillée par segment
        story.append(Paragraph("4. Analyse Détaillée par Segment", self.subtitle_style))
        
        segment_analysis = df.groupby(['segment', 'sous_segment']).agg({
            'montant': ['count', 'sum'],
            'note_externe': lambda x: x.mode().iloc[0] if not x.mode().empty else 'N/A'
        }).round(2)
        
        detailed_data = [['Segment', 'Sous-Segment', 'Nombre', 'Montant (MAD)', 'Note Dominante']]
        
        for (segment, sous_segment), row in segment_analysis.iterrows():
            count = int(row[('montant', 'count')])
            amount = row[('montant', 'sum')]
            note = row[('note_externe', '<lambda>')]
            
            detailed_data.append([
                segment, 
                sous_segment, 
                f"{count:,}", 
                f"{amount:,.0f}", 
                note
            ])
        
        detailed_table = Table(detailed_data)
        detailed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        story.append(detailed_table)
        
        # Génération du PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_rwa_report(self, df, rwa_results):
        """Générer le rapport RWA complet"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Titre
        title = Paragraph("Rapport de Calcul RWA - Bank Al-Maghrib", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Date et résumé exécutif
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        story.append(Paragraph(f"Date de génération: {date_str}", self.normal_style))
        story.append(Spacer(1, 30))
        
        # Résumé exécutif
        story.append(Paragraph("Résumé Exécutif", self.subtitle_style))
        
        summary_data = [
            ['Métrique', 'Valeur'],
            ['Total Expositions', f"{len(df):,}"],
            ['Exposition Totale', f"{rwa_results['total_exposure']:,.0f} MAD"],
            ['Total RWA', f"{rwa_results['total_rwa']:,.0f} MAD"],
            ['Pondération Moyenne', f"{rwa_results['average_weighting']:.2f}%"],
            ['Types de Contreparties', f"{rwa_results['unique_counterparty_types']}"]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 30))
        
        # Analyse par contrepartie
        story.append(Paragraph("Analyse par Type de Contrepartie", self.subtitle_style))
        
        counterparty_data = [['Type', 'Nombre', 'Exposition (MAD)', 'RWA (MAD)', 'Pondération Moy.']]
        
        for segment, analysis in rwa_results['counterparty_analysis'].items():
            counterparty_data.append([
                segment,
                f"{analysis['count']:,}",
                f"{analysis['total_exposure']:,.0f}",
                f"{analysis['total_rwa']:,.0f}",
                f"{analysis['avg_weighting']:.2f}%"
            ])
        
        counterparty_table = Table(counterparty_data)
        counterparty_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        story.append(counterparty_table)
        
        # Génération du PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
