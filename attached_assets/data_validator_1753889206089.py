import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

class DataValidator:
    """Validateur de données pour le calcul RWA"""
    
    def __init__(self):
        self.required_columns = [
            'segment', 'sous_segment', 'monnaie', 'note_externe', 'note_pmae',
            'remboursement_budget', 'creance_souffrance', 'echeance_initiale',
            'echeance', 'note_inf_1_an', 'note_sup_1_an', 'accord_bank_maghrib',
            'appart_grpe', 'dette_banc', 'montant', 'garanti_hypotheque',
            'usage', 'convention_etat', 'valeur_bien_hypoteq', 
            'valeur_encours_creance', 'provision_constitue'
        ]
        
        self.valid_segments = [
            'souverain', 'organisme_public', 'bmd', 'etablissement_credit',
            'entreprise', 'tpe', 'particulier', 'immobilier'
        ]
        
        self.valid_ratings = [
            'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-',
            'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-',
            'B+', 'B', 'B-', 'A-1', 'A-2', 'A-3', 'UNRATED'
        ]
        
        self.valid_currencies = ['MAD', 'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD']
        
        self.valid_maturities = ['inf_3mois', 'inf_1_an', 'sup_1_an']
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Valider l'ensemble du DataFrame"""
        validation_results = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Vérification des colonnes requises
        missing_columns = self._check_required_columns(df)
        if missing_columns:
            validation_results['errors'].extend([
                f"Colonne manquante: {col}" for col in missing_columns
            ])
            return validation_results
        
        # Validation des données
        validation_results['errors'].extend(self._validate_data_types(df))
        validation_results['warnings'].extend(self._validate_data_values(df))
        validation_results['info'].extend(self._generate_data_summary(df))
        
        return validation_results
    
    def _check_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Vérifier la présence des colonnes requises"""
        return [col for col in self.required_columns if col not in df.columns]
    
    def _validate_data_types(self, df: pd.DataFrame) -> List[str]:
        """Valider les types de données"""
        errors = []
        
        # Colonnes numériques
        numeric_columns = ['montant', 'dette_banc', 'valeur_bien_hypoteq', 
                          'valeur_encours_creance', 'provision_constitue']
        
        for col in numeric_columns:
            if col in df.columns:
                non_numeric = df[~pd.to_numeric(df[col], errors='coerce').notna()]
                if not non_numeric.empty:
                    errors.append(f"Valeurs non numériques dans {col}: {len(non_numeric)} lignes")
        
        # Colonnes booléennes
        boolean_columns = ['remboursement_budget', 'creance_souffrance', 
                          'accord_bank_maghrib', 'appart_grpe', 
                          'garanti_hypotheque', 'convention_etat']
        
        for col in boolean_columns:
            if col in df.columns:
                valid_bool_values = [True, False, 1, 0, 'True', 'False', 'true', 'false', 'oui', 'non']
                invalid_bool = df[~df[col].isin(valid_bool_values)]
                if not invalid_bool.empty:
                    errors.append(f"Valeurs booléennes invalides dans {col}: {len(invalid_bool)} lignes")
        
        return errors
    
    def _validate_data_values(self, df: pd.DataFrame) -> List[str]:
        """Valider les valeurs des données"""
        warnings = []
        
        # Validation des segments
        if 'segment' in df.columns:
            invalid_segments = df[~df['segment'].str.lower().isin(self.valid_segments)]
            if not invalid_segments.empty:
                unique_invalid = invalid_segments['segment'].unique()
                warnings.append(f"Segments non reconnus: {', '.join(unique_invalid)}")
        
        # Validation des notations
        rating_columns = ['note_externe', 'note_pmae', 'note_inf_1_an', 'note_sup_1_an']
        for col in rating_columns:
            if col in df.columns:
                invalid_ratings = df[
                    ~df[col].str.upper().isin(self.valid_ratings) & 
                    df[col].notna() & 
                    (df[col] != '')
                ]
                if not invalid_ratings.empty:
                    unique_invalid = invalid_ratings[col].unique()
                    warnings.append(f"Notations non reconnues dans {col}: {', '.join(unique_invalid)}")
        
        # Validation des devises
        if 'monnaie' in df.columns:
            invalid_currencies = df[~df['monnaie'].str.upper().isin(self.valid_currencies)]
            if not invalid_currencies.empty:
                unique_invalid = invalid_currencies['monnaie'].unique()
                warnings.append(f"Devises non reconnues: {', '.join(unique_invalid)}")
        
        # Validation des échéances
        maturity_columns = ['echeance_initiale', 'echeance']
        for col in maturity_columns:
            if col in df.columns:
                invalid_maturities = df[~df[col].isin(self.valid_maturities)]
                if not invalid_maturities.empty:
                    warnings.append(f"Échéances non reconnues dans {col}: {len(invalid_maturities)} lignes")
        
        # Validation des montants
        if 'montant' in df.columns:
            negative_amounts = df[df['montant'] < 0]
            if not negative_amounts.empty:
                warnings.append(f"Montants négatifs détectés: {len(negative_amounts)} lignes")
            
            zero_amounts = df[df['montant'] == 0]
            if not zero_amounts.empty:
                warnings.append(f"Montants nuls détectés: {len(zero_amounts)} lignes")
        
        # Cohérence des garanties hypothécaires
        if all(col in df.columns for col in ['garanti_hypotheque', 'valeur_bien_hypoteq']):
            guaranteed_without_value = df[
                (df['garanti_hypotheque'] == True) & 
                (df['valeur_bien_hypoteq'].isna() | (df['valeur_bien_hypoteq'] == 0))
            ]
            if not guaranteed_without_value.empty:
                warnings.append(f"Garanties hypothécaires sans valeur: {len(guaranteed_without_value)} lignes")
        
        return warnings
    
    def _generate_data_summary(self, df: pd.DataFrame) -> List[str]:
        """Générer un résumé des données"""
        info = []
        
        info.append(f"Nombre total de lignes: {len(df):,}")
        info.append(f"Nombre total de colonnes: {len(df.columns)}")
        
        if 'segment' in df.columns:
            info.append(f"Segments uniques: {df['segment'].nunique()}")
            segment_distribution = df['segment'].value_counts()
            for segment, count in segment_distribution.head(5).items():
                info.append(f"  - {segment}: {count:,} lignes")
        
        if 'montant' in df.columns:
            total_exposure = df['montant'].sum()
            info.append(f"Exposition totale: {total_exposure:,.0f}")
            info.append(f"Exposition moyenne: {df['montant'].mean():,.0f}")
            info.append(f"Exposition médiane: {df['montant'].median():,.0f}")
        
        if 'note_externe' in df.columns:
            info.append(f"Notations externes uniques: {df['note_externe'].nunique()}")
            rating_distribution = df['note_externe'].value_counts()
            for rating, count in rating_distribution.head(3).items():
                info.append(f"  - {rating}: {count:,} lignes")
        
        return info
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoyer et standardiser le DataFrame"""
        df_clean = df.copy()
        
        # Standardisation des segments
        if 'segment' in df_clean.columns:
            df_clean['segment'] = df_clean['segment'].str.lower().str.strip()
        
        # Standardisation des notations
        rating_columns = ['note_externe', 'note_pmae', 'note_inf_1_an', 'note_sup_1_an']
        for col in rating_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].str.upper().str.strip()
                df_clean[col] = df_clean[col].replace('', 'UNRATED')
                df_clean[col] = df_clean[col].fillna('UNRATED')
        
        # Standardisation des devises
        if 'monnaie' in df_clean.columns:
            df_clean['monnaie'] = df_clean['monnaie'].str.upper().str.strip()
        
        # Conversion des valeurs booléennes
        boolean_columns = ['remboursement_budget', 'creance_souffrance', 
                          'accord_bank_maghrib', 'appart_grpe', 
                          'garanti_hypotheque', 'convention_etat']
        
        for col in boolean_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].map({
                    True: True, False: False, 1: True, 0: False,
                    'True': True, 'False': False, 'true': True, 'false': False,
                    'oui': True, 'non': False, 'Oui': True, 'Non': False
                }).fillna(False)
        
        # Nettoyage des valeurs numériques
        numeric_columns = ['montant', 'dette_banc', 'valeur_bien_hypoteq', 
                          'valeur_encours_creance', 'provision_constitue']
        
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
        
        return df_clean
    
    def generate_validation_report(self, validation_results: Dict[str, List[str]]) -> str:
        """Générer un rapport de validation formaté"""
        report = []
        report.append("=== RAPPORT DE VALIDATION DES DONNÉES ===\n")
        
        if validation_results['errors']:
            report.append("🔴 ERREURS CRITIQUES:")
            for error in validation_results['errors']:
                report.append(f"  - {error}")
            report.append("")
        
        if validation_results['warnings']:
            report.append("🟡 AVERTISSEMENTS:")
            for warning in validation_results['warnings']:
                report.append(f"  - {warning}")
            report.append("")
        
        if validation_results['info']:
            report.append("ℹ️ INFORMATIONS:")
            for info in validation_results['info']:
                report.append(f"  - {info}")
            report.append("")
        
        if not validation_results['errors'] and not validation_results['warnings']:
            report.append("✅ Aucun problème détecté. Les données sont prêtes pour le calcul RWA.")
        
        return "\n".join(report)
