import pandas as pd
import numpy as np

class RWACalculator:
    """Calculateur RWA selon les règles Bank Al-Maghrib"""
    
    def __init__(self):
        self.weighting_rules = self._initialize_weighting_rules()
    
    def _initialize_weighting_rules(self):
        """Initialiser les règles de pondération"""
        return {
            # A) Créances sur les emprunteurs souverains
            'souverain': {
                'etat_marocain_bam': 0.0,  # 0% pour État marocain et BAM
                'autres_etats': self._get_sovereign_weighting,
                'default': 1.0
            },
            
            # B) Créances sur les organismes publics
            'organisme_public': {
                'default': 0.2,  # 20% pour collectivités locales
                'with_external_rating': self._get_public_org_weighting
            },
            
            # C) Créances sur les BMD
            'bmd': {
                'bank_al_maghrib_list': 0.0,  # 0% pour BMD listées par BAM
                'others': self._get_bmd_weighting
            },
            
            # D) Créances sur établissements de crédit
            'etablissement_credit': {
                'with_external_rating': self._get_credit_institution_weighting,
                'short_term': self._get_short_term_weighting
            },
            
            # E) Créances sur entités bancaires
            'entite_bancaire': {
                'morocco': self._get_credit_institution_weighting,
                'foreign': self._get_credit_institution_weighting
            },
            
            # F) Créances sur entreprises
            'entreprise': {
                'with_external_rating': self._get_enterprise_weighting,
                'unique_weighting': 1.0,  # 100% option unique
                'group_entity': 1.5  # 150% pour entités de groupe
            },
            
            # G) Créances sur TPE et particuliers
            'tpe_particulier': {
                'default': 0.75,  # 75%
                'over_1m_mad': 1.0  # 100% pour montants > 1M MAD
            },
            
            # H) Prêts immobiliers résidentiels
            'immobilier_residentiel': {
                'default': 0.35  # 35%
            },
            
            # I) Prêts immobiliers commerciaux
            'immobilier_commercial': {
                'guaranteed': 1.0,  # 100% pour garantis par hypothèque
                'lease_purchase': 0.5  # 50% pour crédit-bail/location
            }
        }
    
    def calculate_rwa(self, df):
        """Calculer les RWA pour l'ensemble du portefeuille"""
        results = []
        
        for idx, row in df.iterrows():
            weighting = self._calculate_individual_weighting(row)
            rwa = row['montant'] * weighting
            
            results.append({
                'index': idx,
                'segment': row['segment'],
                'sous_segment': row['sous_segment'],
                'montant': row['montant'],
                'ponderation': weighting,
                'rwa': rwa,
                'note_externe': row.get('note_externe', ''),
                'monnaie': row.get('monnaie', ''),
                'echeance': row.get('echeance', '')
            })
        
        results_df = pd.DataFrame(results)
        
        # Calculs agrégés
        total_rwa = results_df['rwa'].sum()
        total_exposure = results_df['montant'].sum()
        average_weighting = (total_rwa / total_exposure * 100) if total_exposure > 0 else 0
        
        # Analyse par contrepartie
        counterparty_analysis = {}
        for segment in results_df['segment'].unique():
            segment_data = results_df[results_df['segment'] == segment]
            counterparty_analysis[segment] = {
                'count': len(segment_data),
                'total_exposure': segment_data['montant'].sum(),
                'total_rwa': segment_data['rwa'].sum(),
                'avg_weighting': (segment_data['rwa'].sum() / segment_data['montant'].sum() * 100) if segment_data['montant'].sum() > 0 else 0
            }
        
        return {
            'results_df': results_df,
            'total_rwa': total_rwa,
            'total_exposure': total_exposure,
            'average_weighting': average_weighting,
            'unique_counterparty_types': len(df['segment'].unique()),
            'counterparty_analysis': counterparty_analysis
        }
    
    def _calculate_individual_weighting(self, row):
        """Calculer la pondération individuelle d'une exposition"""
        segment_raw = row.get('segment', '')
        segment = str(segment_raw).lower().replace(' ', '_') if pd.notna(segment_raw) else ''
        
        # Gestion des créances en souffrance
        if row.get('creance_souffrance', False):
            return self._apply_provision_weighting(row)
        
        # Application des règles par segment
        if segment == 'souverain':
            return self._calculate_sovereign_weighting(row)
        elif segment == 'organisme_public':
            return self._calculate_public_org_weighting(row)
        elif segment == 'bmd':
            return self._calculate_bmd_weighting(row)
        elif segment == 'etablissement_credit':
            return self._calculate_credit_institution_weighting(row)
        elif segment == 'entreprise':
            return self._calculate_enterprise_weighting(row)
        elif segment == 'tpe' or segment == 'particulier':
            return self._calculate_tpe_individual_weighting(row)
        elif segment == 'immobilier':
            return self._calculate_real_estate_weighting(row)
        else:
            return 1.0  # Pondération par défaut 100%
    
    def _calculate_sovereign_weighting(self, row):
        """Calcul pondération créances souveraines"""
        sous_segment_raw = row.get('sous_segment', '')
        sous_segment = str(sous_segment_raw).lower() if pd.notna(sous_segment_raw) else ''
        
        # État marocain et BAM = 0%
        if 'maroc' in sous_segment or 'bam' in sous_segment:
            return 0.0
        
        # Autres États selon notation externe
        note_externe_raw = row.get('note_externe', '')
        note_externe = str(note_externe_raw).upper() if pd.notna(note_externe_raw) else 'UNRATED'
        return self._get_rating_weighting(note_externe, 'sovereign')
    
    def _calculate_public_org_weighting(self, row):
        """Calcul pondération organismes publics"""
        # Si remboursement prévu au budget = 20%
        if row.get('remboursement_budget', False):
            return 0.2
        
        # Sinon selon notation externe
        note_externe_raw = row.get('note_externe', '')
        note_externe = str(note_externe_raw).upper() if pd.notna(note_externe_raw) else 'UNRATED'
        return self._get_rating_weighting(note_externe, 'public_org')
    
    def _calculate_bmd_weighting(self, row):
        """Calcul pondération BMD"""
        # BMD listées par BAM = 0%
        if row.get('accord_bank_maghrib', False):
            return 0.0
        
        # Autres BMD selon notation
        note_externe_raw = row.get('note_externe', '')
        note_externe = str(note_externe_raw).upper() if pd.notna(note_externe_raw) else 'UNRATED'
        return self._get_rating_weighting(note_externe, 'bmd')
    
    def _calculate_credit_institution_weighting(self, row):
        """Calcul pondération établissements de crédit"""
        note_externe_raw = row.get('note_externe', '')
        note_externe = str(note_externe_raw).upper() if pd.notna(note_externe_raw) else 'UNRATED'
        echeance = str(row.get('echeance', '')) if pd.notna(row.get('echeance', '')) else ''
        
        # Créances à court terme (≤ 3 mois)
        if echeance == 'inf_3mois':
            return self._get_short_term_rating_weighting(note_externe)
        
        # Créances normales selon notation
        return self._get_rating_weighting(note_externe, 'credit_institution')
    
    def _calculate_enterprise_weighting(self, row):
        """Calcul pondération entreprises"""
        # Entité de groupe = 150%
        if row.get('appart_grpe', False) and row.get('dette_banc', 0) >= 500000000:
            return 1.5
        
        # Option pondération unique = 100%
        if row.get('accord_bank_maghrib', False):
            return 1.0
        
        # Selon notation externe si échéance initiale < 1 an
        echeance_initiale = str(row.get('echeance_initiale', '')) if pd.notna(row.get('echeance_initiale', '')) else ''
        if echeance_initiale == 'inf_1_an':
            note_raw = row.get('note_inf_1_an', row.get('note_externe', ''))
            note = str(note_raw).upper() if pd.notna(note_raw) else 'UNRATED'
            return self._get_rating_weighting(note, 'enterprise_short')
        
        # Notation externe standard
        note_externe_raw = row.get('note_externe', '')
        note_externe = str(note_externe_raw).upper() if pd.notna(note_externe_raw) else 'UNRATED'
        return self._get_rating_weighting(note_externe, 'enterprise')
    
    def _calculate_tpe_individual_weighting(self, row):
        """Calcul pondération TPE et particuliers"""
        montant = row.get('montant', 0)
        
        # Particuliers avec prêt immobilier > 1M MAD = 100%
        if montant > 1000000 and row.get('garanti_hypotheque', False):
            return 1.0
        
        # Sinon 75%
        return 0.75
    
    def _calculate_real_estate_weighting(self, row):
        """Calcul pondération immobilier"""
        usage_raw = row.get('usage', '')
        usage = str(usage_raw).lower() if pd.notna(usage_raw) else ''
        
        # Immobilier résidentiel = 35%
        if 'residentiel' in usage or 'habitation' in usage:
            return 0.35
        
        # Immobilier commercial garanti par hypothèque = 100%
        if row.get('garanti_hypotheque', False):
            return 1.0
        
        # Crédit-bail immobilier commercial = 50%
        return 0.5
    
    def _get_rating_weighting(self, rating, category):
        """Obtenir la pondération selon la notation et la catégorie"""
        rating_weights = {
            'sovereign': {
                'AAA': 0.0, 'AA+': 0.0, 'AA': 0.0, 'AA-': 0.0,
                'A+': 0.2, 'A': 0.2, 'A-': 0.2,
                'BBB+': 0.5, 'BBB': 0.5, 'BBB-': 0.5,
                'BB+': 1.0, 'BB': 1.0, 'BB-': 1.0,
                'B+': 1.0, 'B': 1.0, 'B-': 1.0,
                'DEFAULT': 1.0, 'UNRATED': 1.0
            },
            'public_org': {
                'AAA': 0.2, 'AA+': 0.2, 'AA': 0.2, 'AA-': 0.2,
                'A+': 0.5, 'A': 0.5, 'A-': 0.5,
                'BBB+': 0.5, 'BBB': 0.5, 'BBB-': 0.5,
                'BB+': 1.0, 'BB': 1.0, 'BB-': 1.0,
                'B+': 1.0, 'B': 1.0, 'B-': 1.0,
                'DEFAULT': 1.5, 'UNRATED': 0.5
            },
            'bmd': {
                'AAA': 0.2, 'AA+': 0.2, 'AA': 0.2, 'AA-': 0.2,
                'A+': 0.5, 'A': 0.5, 'A-': 0.5,
                'BBB+': 0.5, 'BBB': 0.5, 'BBB-': 0.5,
                'BB+': 1.0, 'BB': 1.0, 'BB-': 1.0,
                'B+': 1.0, 'B': 1.0, 'B-': 1.0,
                'DEFAULT': 1.5, 'UNRATED': 0.5
            },
            'credit_institution': {
                'AAA': 0.2, 'AA+': 0.2, 'AA': 0.2, 'AA-': 0.2,
                'A+': 0.5, 'A': 0.5, 'A-': 0.5,
                'BBB+': 0.5, 'BBB': 0.5, 'BBB-': 0.5,
                'BB+': 1.0, 'BB': 1.0, 'BB-': 1.0,
                'B+': 1.0, 'B': 1.0, 'B-': 1.0,
                'DEFAULT': 1.5, 'UNRATED': 0.5
            },
            'enterprise': {
                'AAA': 0.2, 'AA+': 0.2, 'AA': 0.2, 'AA-': 0.2,
                'A+': 0.5, 'A': 0.5, 'A-': 0.5,
                'BBB+': 1.0, 'BBB': 1.0, 'BBB-': 1.0,
                'BB+': 1.0, 'BB': 1.0, 'BB-': 1.0,
                'B+': 1.5, 'B': 1.5, 'B-': 1.5,
                'DEFAULT': 1.5, 'UNRATED': 1.0
            },
            'enterprise_short': {
                'A-1': 0.2, 'A-2': 0.5, 'A-3': 1.0, 'DEFAULT': 1.5
            }
        }
        
        category_weights = rating_weights.get(category, rating_weights['enterprise'])
        return category_weights.get(rating, category_weights.get('UNRATED', 1.0))
    
    def _get_short_term_rating_weighting(self, rating):
        """Pondération pour créances à court terme"""
        short_term_weights = {
            'A-1': 0.2, 'A-2': 0.5, 'A-3': 1.0, 'DEFAULT': 1.5
        }
        rating_str = str(rating).upper() if pd.notna(rating) else 'DEFAULT'
        return short_term_weights.get(rating_str, 0.2)
    
    def _apply_provision_weighting(self, row):
        """Appliquer les pondérations pour créances en souffrance"""
        provision_rate = row.get('provision_constitue', 0) / row.get('valeur_encours_creance', 1)
        usage_raw = row.get('usage', '')
        usage = str(usage_raw).lower() if pd.notna(usage_raw) else ''
        
        # Prêts immobiliers résidentiels
        if 'residentiel' in usage or 'habitation' in usage:
            if provision_rate < 0.2:
                return 1.0  # 100%
            else:
                return 0.5  # 50%
        
        # Autres créances
        if provision_rate < 0.2:
            return 1.5  # 150%
        elif provision_rate <= 0.5:
            return 1.0  # 100%
        else:
            return 0.5  # 50%
    
    def _get_sovereign_weighting(self, row):
        """Pondération spécifique souverains"""
        note_raw = row.get('note_externe', '')
        note = str(note_raw).upper() if pd.notna(note_raw) else 'UNRATED'
        return self._get_rating_weighting(note, 'sovereign')
    
    def _get_public_org_weighting(self, row):
        """Pondération spécifique organismes publics"""
        note_raw = row.get('note_externe', '')
        note = str(note_raw).upper() if pd.notna(note_raw) else 'UNRATED'
        return self._get_rating_weighting(note, 'public_org')
    
    def _get_bmd_weighting(self, row):
        """Pondération spécifique BMD"""
        note_raw = row.get('note_externe', '')
        note = str(note_raw).upper() if pd.notna(note_raw) else 'UNRATED'
        return self._get_rating_weighting(note, 'bmd')
    
    def _get_credit_institution_weighting(self, row):
        """Pondération spécifique établissements de crédit"""
        note_raw = row.get('note_externe', '')
        note = str(note_raw).upper() if pd.notna(note_raw) else 'UNRATED'
        return self._get_rating_weighting(note, 'credit_institution')
    
    def _get_enterprise_weighting(self, row):
        """Pondération spécifique entreprises"""
        note_raw = row.get('note_externe', '')
        note = str(note_raw).upper() if pd.notna(note_raw) else 'UNRATED'
        return self._get_rating_weighting(note, 'enterprise')
    
    def _get_short_term_weighting(self, row):
        """Pondération spécifique court terme"""
        note_raw = row.get('note_externe', '')
        note = str(note_raw).upper() if pd.notna(note_raw) else 'UNRATED' 
        return self._get_short_term_rating_weighting(note)
