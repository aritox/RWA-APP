import pandas as pd
import numpy as np

class RWACalculator:
    """Calculateur RWA selon les règles exactes Bank Al-Maghrib"""
    
    def __init__(self):
        self.rating_weights = self._initialize_rating_weights()
        self.pmae_weights = self._initialize_pmae_weights()
        
    def _initialize_rating_weights(self):
        """Tables de pondération selon les notations externes"""
        return {
            # Table générale pour la plupart des segments
            'general': {
                'AAA à AA-': 0.20,
                'A+ à A-': 0.50,
                'BBB+ à BBB-': 0.50,
                'BB+ à BB-': 1.00,
                'B+ à B-': 1.00,
                'Inférieure à B-': 1.50,
                'Pas de notation': 0.50
            },
            
            # Table spécifique pour les établissements de crédit (échéance < 1 an)
            'credit_short_term': {
                'A-1': 0.20,
                'A-2': 0.50,
                'A-3': 1.00,
                'Inférieure à A-3': 1.50
            },
            
            # Table pour les entreprises (échéance < 1 an)
            'enterprise_short_term': {
                'A-1': 0.20,
                'A-2': 0.50,
                'A-3': 1.00,
                'Inférieure à A-3': 1.50
            }
        }
    
    def _initialize_pmae_weights(self):
        """Table de pondération PMAE (Primes Minimales d'Assurance à l'Exportation)"""
        return {
            '0': 0.00,  # 0-1 = 0%
            '1': 0.00,  # 0-1 = 0%
            '2': 0.20,  # 2 = 20%
            '3': 0.50,  # 3 = 50%
            '4': 1.00,  # 4 à 6 = 100%
            '5': 1.00,  # 4 à 6 = 100%
            '6': 1.00,  # 4 à 6 = 100%
            '7': 1.50   # 7 = 150%
        }
    
    def get_segment_variables(self, segment):
        """Retourner les variables nécessaires pour chaque segment"""
        segment_variables = {
            'souverain': ['sous_segment', 'monnaie', 'montant', 'note_externe', 'note_pmae'],
            'organisme_public': ['sous_segment', 'monnaie', 'montant', 'remboursement_prevu_budget', 'creance_souffrance', 'note_externe'],
            'bmd': ['sous_segment', 'montant', 'note_externe'],
            'etablissement_credit': ['sous_segment', 'monnaie', 'montant', 'echeance_initiale', 'note_externe', 'note_inf_1an', 'note_inf_3mois'],
            'entreprise': ['sous_segment', 'monnaie', 'montant', 'echeance', 'note_sup_1an', 'note_inf_1an', 'accord_bank_maghrib', 'appart_grpe', 'dette_banc'],
            'tpe': ['sous_segment', 'montant', 'monnaie'],
            'particulier': ['sous_segment', 'montant', 'monnaie', 'montant_creance', 'garanti_hypotheque'],
            'pret': ['sous_segment', 'montant', 'usage', 'convention_etat', 'valeur_bien_hypotheque'],
            'creance_souffrance': ['sous_segment', 'valeur_encours_creance', 'provision_constitue']
        }
        return segment_variables.get(segment.lower(), ['sous_segment', 'montant'])
    
    def calculate_rwa(self, df):
        """Calculer les RWA pour l'ensemble du portefeuille avec les nouvelles règles"""
        results = []
        
        for idx, row in df.iterrows():
            segment = str(row.get('segment', '')).lower()
            weighting = self._calculate_individual_weighting(row)
            montant = float(row.get('montant', 0))
            rwa = montant * weighting
            
            # Créer l'entrée de résultat avec toutes les variables du segment
            result = {
                'index': idx,
                'segment': row.get('segment', ''),
                'sous_segment': row.get('sous_segment', ''),
                'montant': montant,
                'ponderation': weighting,
                'rwa': rwa,
                'regle': self._get_rule_explanation(row, weighting)
            }
            
            # Ajouter les variables spécifiques selon le segment
            if segment == 'souverain':
                result.update({
                    'monnaie': row.get('monnaie', ''),
                    'note_externe': row.get('note_externe', ''),
                    'note_pmae': row.get('note_pmae', '')
                })
            elif segment == 'organisme_public':
                result.update({
                    'monnaie': row.get('monnaie', ''),
                    'remboursement_prevu_budget': row.get('remboursement_prevu_budget', ''),
                    'creance_souffrance': row.get('creance_souffrance', ''),
                    'note_externe': row.get('note_externe', '')
                })
            elif segment == 'bmd':
                result.update({
                    'note_externe': row.get('note_externe', '')
                })
            elif segment == 'etablissement_credit':
                result.update({
                    'monnaie': row.get('monnaie', ''),
                    'echeance_initiale': row.get('echeance_initiale', ''),
                    'note_externe': row.get('note_externe', ''),
                    'note_inf_1an': row.get('note_inf_1an', ''),
                    'note_inf_3mois': row.get('note_inf_3mois', '')
                })
            elif segment == 'entreprise':
                result.update({
                    'monnaie': row.get('monnaie', ''),
                    'echeance': row.get('echeance', ''),
                    'note_sup_1an': row.get('note_sup_1an', ''),
                    'note_inf_1an': row.get('note_inf_1an', ''),
                    'accord_bank_maghrib': row.get('accord_bank_maghrib', ''),
                    'appart_grpe': row.get('appart_grpe', ''),
                    'dette_banc': row.get('dette_banc', '')
                })
            elif segment == 'tpe':
                result.update({
                    'monnaie': row.get('monnaie', '')
                })
            elif segment == 'particulier':
                result.update({
                    'monnaie': row.get('monnaie', ''),
                    'montant_creance': row.get('montant_creance', ''),
                    'garanti_hypotheque': row.get('garanti_hypotheque', '')
                })
            elif segment == 'pret':
                result.update({
                    'usage': row.get('usage', ''),
                    'convention_etat': row.get('convention_etat', ''),
                    'valeur_bien_hypotheque': row.get('valeur_bien_hypotheque', '')
                })
            elif segment == 'creance_souffrance':
                result.update({
                    'valeur_encours_creance': row.get('valeur_encours_creance', ''),
                    'provision_constitue': row.get('provision_constitue', '')
                })
            
            results.append(result)
        
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
        """Calculer la pondération individuelle selon les règles exactes Bank Al-Maghrib"""
        segment = str(row.get('segment', '')).lower()
        
        # Gestion spéciale des créances en souffrance
        if segment == 'creance_souffrance':
            return self._calculate_distressed_debt_weighting(row)
        
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
        elif segment == 'tpe':
            return self._calculate_tpe_weighting(row)
        elif segment == 'particulier':
            return self._calculate_individual_weighting_method(row)
        elif segment == 'pret':
            return self._calculate_loan_weighting(row)
        else:
            return 1.0  # Pondération par défaut 100%

    def _get_rating_weighting(self, rating, category='general'):
        """Récupérer la pondération selon la notation et la catégorie"""
        rating = str(rating).upper().strip()
        
        # Mappings spéciaux pour certaines notations
        if category == 'credit_short_term' or category == 'enterprise_short_term':
            table = self.rating_weights.get(category, {})
        else:
            table = self.rating_weights.get('general', {})
        
        # Recherche exacte puis approximative
        for rating_range, weight in table.items():
            if rating in rating_range or rating == rating_range:
                return weight
        
        # Recherche par gamme pour les notations standards
        if 'AAA' in rating or 'AA' in rating:
            return 0.20
        elif 'A+' in rating or 'A' in rating or 'A-' in rating:
            return 0.50
        elif 'BBB' in rating:
            return 0.50
        elif 'BB' in rating:
            return 1.00
        elif 'B+' in rating or 'B' in rating or 'B-' in rating:
            return 1.00
        elif 'CCC' in rating or 'CC' in rating or 'C' in rating or 'D' in rating:
            return 1.50
        else:
            return 0.50  # Pas de notation = 50%

    def _calculate_sovereign_weighting(self, row):
        """A) Créances sur les emprunteurs souverains"""
        sous_segment = str(row.get('sous_segment', '')).lower()
        monnaie = str(row.get('monnaie', '')).upper()
        
        # 1) Pondération de 0% appliquée aux créances sur l'État marocain et Bank Al-Maghrib
        # libellées et financées en dirhams, ainsi qu'aux créances sur BIS, FMI, BCE, Commission Européenne
        if ('maroc' in sous_segment or 'bam' in sous_segment or 'bank al-maghrib' in sous_segment) and monnaie == 'MAD':
            return 0.0
        
        if any(org in sous_segment for org in ['bis', 'banque des règlements internationaux', 'fonds monétaire international', 'fmi', 'banque centrale européenne', 'bce', 'commission européenne']):
            return 0.0
        
        # 2) Table de pondération selon notation externe
        note_externe = str(row.get('note_externe', '')).upper().strip()
        
        if any(rating in note_externe for rating in ['AAA', 'AA+', 'AA', 'AA-']):
            return 0.0  # AAA à AA- = 0%
        elif any(rating in note_externe for rating in ['A+', 'A', 'A-']):
            return 0.20  # A+ à A- = 20%
        elif any(rating in note_externe for rating in ['BBB+', 'BBB', 'BBB-']):
            return 0.50  # BBB+ à BBB- = 50%
        elif any(rating in note_externe for rating in ['BB+', 'BB', 'BB-']):
            return 1.00  # BB+ à BB- = 100%
        elif any(rating in note_externe for rating in ['B+', 'B', 'B-']):
            return 1.00  # B+ à B- = 100%
        elif note_externe and any(rating in note_externe for rating in ['CCC', 'CC', 'C', 'D']):
            return 1.50  # Inférieure à B- = 150%
        
        # 3) Notation PMAE si pas de notation externe
        note_pmae = str(row.get('note_pmae', '')).strip()
        if note_pmae and note_pmae != '':
            return self.pmae_weights.get(note_pmae, 1.0)
        
        # 4) Pas de notation = 100%
        return 1.00

    def _calculate_public_org_weighting(self, row):
        """B) Créances sur les organismes publics"""
        # 1) Remboursement prévu au budget = 20%
        remboursement_budget = row.get('remboursement_prevu_budget', False)
        if remboursement_budget:
            return 0.20
        
        # 2) Selon notation externe
        note_externe = str(row.get('note_externe', ''))
        if note_externe and note_externe.strip():
            return self._get_rating_weighting(note_externe, 'general')
        
        # 3) Pas de notation = 50%
        return 0.50

    def _calculate_bmd_weighting(self, row):
        """C) Créances sur les BMD"""
        # BMD listés par Bank Al-Maghrib = 0%
        if row.get('accord_bank_maghrib', False):
            return 0.0
        
        # Autres BMD selon notation externe avec table spécifique
        note_externe = str(row.get('note_externe', '')).upper().strip()
        
        # Table de pondération spécifique pour BMD
        if any(rating in note_externe for rating in ['AAA', 'AA+']):
            return 0.20
        elif any(rating in note_externe for rating in ['AA', 'AA-']):
            return 0.20
        elif any(rating in note_externe for rating in ['A+', 'A', 'A-']):
            return 0.50
        elif any(rating in note_externe for rating in ['BBB+', 'BBB', 'BBB-']):
            return 0.50
        elif any(rating in note_externe for rating in ['BB+', 'BB', 'BB-']):
            return 1.00
        elif any(rating in note_externe for rating in ['B+', 'B', 'B-']):
            return 1.00
        elif 'B-' in note_externe or any(rating in note_externe for rating in ['CCC', 'CC', 'C', 'D']):
            return 1.50
        else:
            return 0.50  # Pas de notation = 50%

    def _calculate_credit_institution_weighting(self, row):
        """D) Créances sur établissements de crédit"""
        note_externe = str(row.get('note_externe', ''))
        echeance_initiale = str(row.get('echeance_initiale', '')).lower()
        
        # 1) Notation externe selon échéance initiale
        if echeance_initiale and ('< 1 an' in echeance_initiale or 'inf 1 an' in echeance_initiale):
            # Échéance initiale < 1 an
            note_inf_1an = str(row.get('note_inf_1an', ''))
            if note_inf_1an:
                return self._get_rating_weighting(note_inf_1an, 'credit_short_term')
        
        # 2) Échéance initiale ≥ 1 an OU pas d'échéance spécifiée
        if note_externe:
            return self._get_rating_weighting(note_externe, 'general')
        
        # 3) Créances non renouvelables, échéance ≤ 3 mois
        if '≤ 3 mois' in echeance_initiale or '< 3 mois' in echeance_initiale:
            monnaie = str(row.get('monnaie', '')).upper()
            if monnaie == 'MAD':  # Monnaie locale
                return 0.20
            else:
                return self._get_rating_weighting(note_externe, 'general')
        
        return 0.50  # Défaut

    def _calculate_enterprise_weighting(self, row):
        """F) Créances sur grandes entreprises"""
        # 1) Pondération selon notation externe
        note_externe = str(row.get('note_externe', ''))
        echeance = str(row.get('echeance', '')).lower()
        
        if echeance and ('< 1 an' in echeance or 'inf 1 an' in echeance):
            # Échéance < 1 an, utiliser notation courte
            note_inf_1an = str(row.get('note_inf_1an', ''))
            if note_inf_1an:
                return self._get_rating_weighting(note_inf_1an, 'enterprise_short_term')
        
        # 2) Pondération unique après accord Bank Al-Maghrib = 100%
        accord_bam = row.get('accord_bank_maghrib', False)
        if accord_bam:
            return 1.0
        
        # 3) Pondération d'entreprise relevant d'un groupe = 150%
        appart_groupe = row.get('appart_grpe', False)
        if appart_groupe:
            return 1.5
        
        # 4) Notation externe standard
        if note_externe:
            return self._get_rating_weighting(note_externe, 'general')
        
        return 1.0  # Défaut 100%

    def _calculate_tpe_weighting(self, row):
        """G) Créances sur TPE - Très Petite Entreprise"""
        return 0.75  # 75% FIXE selon règles Bank Al-Maghrib

    def _calculate_individual_weighting_method(self, row):
        """G) Créances sur particuliers"""
        montant = float(row.get('montant', 0))
        
        # > 1 million MAD = 100%
        if montant > 1000000:
            return 1.0
        
        # ≤ 1 million MAD = 75%
        return 0.75

    def _calculate_loan_weighting(self, row):
        """H & I) Prêts immobiliers"""
        usage = str(row.get('usage', '')).lower()
        convention_etat = row.get('convention_etat', False)
        
        # H) Prêts immobiliers résidentiels = 35%
        if 'residentiel' in usage or 'habitation' in usage:
            return 0.35
        
        # I) Prêts immobiliers commerciaux
        if 'commercial' in usage or 'professionnel' in usage:
            # 1) Garantis par hypothèque = 100%
            garanti_hypotheque = row.get('garanti_hypotheque', False)
            if garanti_hypotheque:
                return 1.0
            
            # 2) Crédit-bail/location avec option d'achat = 50%
            if 'bail' in usage or 'location' in usage:
                return 0.50
        
        # Convention avec État
        if convention_etat:
            valeur_bien = float(row.get('valeur_bien_hypotheque', 0))
            montant = float(row.get('montant', 0))
            
            if valeur_bien > 0 and montant > 0:
                ratio = montant / valeur_bien
                if ratio <= 0.80:  # ≤ 80% de la valeur
                    return 0.75
        
        return 0.35  # Défaut résidentiel

    def _calculate_distressed_debt_weighting(self, row):
        """J) Créances en souffrance"""
        valeur_encours = float(row.get('valeur_encours_creance', 0))
        provision = float(row.get('provision_constitue', 0))
        
        if valeur_encours == 0:
            return 1.50  # Défaut maximum
        
        ratio_provision = provision / valeur_encours
        
        # 1) Prêts immobiliers résidentiels
        usage = str(row.get('usage', '')).lower()
        if 'residentiel' in usage:
            if ratio_provision < 0.20:
                return 1.00  # 100%
            else:
                return 0.50  # 50%
        
        # 2) Autres créances
        if ratio_provision < 0.20:
            return 1.50  # 150%
        elif ratio_provision <= 0.50:
            return 1.00  # 100%
        else:
            return 0.50  # 50%

    def _get_rule_explanation(self, row, weighting):
        """Générer l'explication détaillée de la règle appliquée"""
        segment = str(row.get('segment', '')).lower()
        sous_segment = str(row.get('sous_segment', ''))
        note_externe = row.get('note_externe', 'Pas de notation')
        monnaie = row.get('monnaie', 'MAD')
        weighting_percent = int(weighting * 100)
        
        if segment == 'souverain':
            if ('maroc' in sous_segment.lower() or 'bam' in sous_segment.lower()) and str(monnaie).upper() == 'MAD':
                return f"État marocain/BAM en MAD - Pondération {weighting_percent}%"
            elif row.get('note_pmae'):
                return f"État étranger PMAE {row.get('note_pmae')} - Pondération {weighting_percent}%"
            else:
                return f"État étranger note {note_externe} - Pondération {weighting_percent}%"
                
        elif segment == 'organisme_public':
            if row.get('remboursement_prevu_budget'):
                return f"Organisme public (remboursement budget) - Pondération {weighting_percent}%"
            else:
                return f"Organisme public note {note_externe} - Pondération {weighting_percent}%"
                
        elif segment == 'bmd':
            if row.get('accord_bank_maghrib'):
                return f"BMD listée Bank Al-Maghrib - Pondération {weighting_percent}%"
            else:
                return f"BMD note {note_externe} - Pondération {weighting_percent}%"
                
        elif segment == 'etablissement_credit':
            echeance = row.get('echeance_initiale', '')
            if '< 1 an' in str(echeance) and row.get('note_inf_1an'):
                return f"Établissement crédit court terme {row.get('note_inf_1an')} - Pondération {weighting_percent}%"
            else:
                return f"Établissement crédit note {note_externe} - Pondération {weighting_percent}%"
                
        elif segment == 'entreprise':
            if row.get('appart_grpe'):
                return f"Entreprise de groupe - Pondération {weighting_percent}%"
            elif row.get('accord_bank_maghrib'):
                return f"Entreprise accord BAM - Pondération {weighting_percent}%"
            else:
                return f"Entreprise note {note_externe} - Pondération {weighting_percent}%"
                
        elif segment == 'tpe':
            return f"Très petite entreprise - Pondération {weighting_percent}%"
            
        elif segment == 'particulier':
            montant = float(row.get('montant', 0))
            if montant > 1000000:
                return f"Particulier > 1M MAD - Pondération {weighting_percent}%"
            else:
                return f"Particulier ≤ 1M MAD - Pondération {weighting_percent}%"
                
        elif segment == 'pret':
            usage = str(row.get('usage', '')).lower()
            if 'residentiel' in usage:
                return f"Prêt immobilier résidentiel - Pondération {weighting_percent}%"
            elif 'commercial' in usage and row.get('garanti_hypotheque'):
                return f"Prêt commercial garanti - Pondération {weighting_percent}%"
            else:
                return f"Prêt immobilier - Pondération {weighting_percent}%"
                
        elif segment == 'creance_souffrance':
            return f"Créance en souffrance - Pondération {weighting_percent}%"
            
        else:
            return f"Autre contrepartie - Pondération {weighting_percent}%"