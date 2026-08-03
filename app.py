import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import random
from fpdf import FPDF

# ============================================================================
# CONFIGURAZIONE
# ============================================================================

st.set_page_config(
    page_title="Proacier - RH",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Sidebar verde
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #5EA529 !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] button {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255,255,255,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# URL
# ============================================================================

LOGO_URL = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png"
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbxt39icOxVevvtes1ne1tK2ZTrw-uXldRIppSDgJj8YPwb13hOMRN6tOT0KJjB9vYF6MQ/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycby1isMOz1fKTptR83six7_3OMaDgcx8_LRn3rLkD9_wCRHdxu1GCgQr3aR9FxaSr3Q-/exec"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")
URL_CONDIZIONI = "https://www.proacier.sn/condizioni"

# ============================================================================
# TRADUZIONI COMPLETE
# ============================================================================

TRADUZIONI = {
    'fr': {
        'titolo': 'PROACIER - GESTION DES RESSOURCES HUMAINES',
        'sottotitolo': 'Système de Recrutement - Sénégal',
        'lingua': 'Langue',
        'candidature': 'Candidature Spontanée',
        'espace_travailleur': 'Espace Travailleur',
        'dashboard': 'Tableau de Bord',
        'logout': 'Déconnexion',
        'nuova_assunzione': 'Nouvelle Embauche (Complet)',
        'home_desc_1': 'Transmission de données pour les nouveaux travailleurs et journaliers',
        'home_desc_2': 'Candidatures spontanées',
        'home_desc_3': 'Espace personnel travailleur',
        'home_desc_4': 'Paiement des journaliers',
        'home_titolo': 'Comment utiliser l\'application',
        'home_btn_1': 'Candidature Spontanée',
        'home_btn_2': 'Espace Travailleur',
        'home_btn_3': 'Tableau de Bord',
        'giornalieri_titolo': 'Déjà travailleur?',
        'giornalieri_desc': 'Accédez à votre espace personnel',
        'nuovo_giornaliero_titolo': 'Nouveau / Journalier?',
        'nuovo_giornaliero_desc': 'Transmettez vos données (pas un contrat)',
        'login_btn': 'Connexion à mon espace',
        'trasmissione_btn': 'Transmettre mes données',
        'i_miei_dati': 'Mes Données',
        'accesso_negato': 'Accès refusé',
        'step1': '1. IDENTITÉ & FAMILLE',
        'step2': '2. COORDONNÉES',
        'step3': '3. DOCUMENTS OFFICIELS',
        'step4': '4. EMPLOI & SALAIRE',
        'step5': '5. COMPÉTENCES & SANTÉ',
        'step6': '6. URGENCE & CONFIRMATION',
        'suivant': 'Suivant →',
        'precedent': '← Précédent',
        'generer_pdf': 'Générer PDF & Accepter',
        'enregistrement_reussi': 'Enregistrement réussi !',
        'conservez_identifiants': 'CONSERVEZ CES IDENTIFIANTS',
        'code_acces': 'Code d\'accès',
        'pin_acces': 'PIN d\'accès',
        'telecharger_pdf': 'Télécharger PDF',
        'retour': 'Retour',
        'cognome': 'Nom de famille *',
        'nome': 'Prénom(s) *',
        'data_nascita': 'Date de naissance',
        'luogo_nascita': 'Lieu de naissance *',
        'nazionalita': 'Nationalité *',
        'sesso': 'Sexe *',
        'stato_civile': 'État civil *',
        'numero_mogli': 'Nombre d\'épouses',
        'figli_totale': 'Nombre total d\'enfants',
        'indirizzo': 'Adresse *',
        'quartiere': 'Quartier *',
        'comune': 'Commune *',
        'dipartimento': 'Département / Région *',
        'telefono_1': 'Téléphone 1 *',
        'telefono_2': 'Téléphone 2',
        'telefono_3': 'Téléphone 3',
        'cni': 'CNI (Carte Nationale d\'Identité) *',
        'nif': 'NIF',
        'css': 'CSS (Sécurité Sociale)',
        'cmu': 'CMU',
        'ipres': 'IPRES',
        'mansione_1': 'Poste / Fonction *',
        'luogo_lavoro': 'Lieu de travail *',
        'reparto': 'Département / Service',
        'supervisore': 'Superviseur',
        'data_inizio_1': 'Date de début *',
        'salario': 'Salaire (FCFA) *',
        'ore_giorno': 'Heures par jour',
        'giorni_settimana': 'Jours par semaine',
        'pagamento': 'Type de paiement',
        'wave_orange': 'N° Wave / Orange Money',
        'categoria_competenza': 'Catégorie de compétence',
        'dettaglio_competenza': 'Détail compétence',
        'patente': 'Permis de conduire',
        'gruppo_sanguigno': 'Groupe sanguin',
        'rh': 'Rhésus',
        'allergie': 'Allergies',
        'malattie': 'Maladies chroniques',
        'idoneita': 'Aptitude médicale',
        'data_visita': 'Date visite médicale',
        'emergenza_nome': 'Nom contact urgence *',
        'emergenza_parentela': 'Lien de parenté *',
        'emergenza_tel': 'Téléphone urgence *',
        'emergenza_indirizzo': 'Adresse urgence',
        'certifico': 'Je certifie l\'exactitude des informations et accepte les conditions.',
        'leggi_condizioni': 'Lire les conditions complètes',
        'certifico_checkbox': 'Je certifie l\'exactitude des informations',
        'connexion_mon_espace': 'Connexion à mon espace',
        'code_access_input': 'Code d\'accès',
        'pin_input': 'PIN personnel',
        'se_connecter': 'Se connecter',
        'mes_donnees_titolo': 'Mes Données Personnelles',
        'donnees_non_modifiables': 'Données Personnelles (non modifiables)',
        'donnees_modifiables': 'Données Modifiables',
        'mettre_a_jour': 'Mettre à jour',
        'salaire_titolo': 'Informations Salariales',
        'salaire_desc': 'Votre salaire est géré par l\'administration',
        'cognome_label': 'Cognome',
        'nome_label': 'Nome',
        'data_nascita_label': 'Data Nascita',
        'luogo_nascita_label': 'Luogo Nascita',
        'cni_label': 'CNI',
        'css_label': 'CSS',
        'ipres_label': 'IPRES',
        'codice_label': 'Codice Operatore',
        'telefono_label': 'Téléphone *',
        'telefono2_label': 'Téléphone 2',
        'indirizzo_label': 'Adresse *',
        'quartiere_label': 'Quartier',
        'comune_label': 'Commune',
        'dipartimento_label': 'Département/Région',
        'figli_label': 'Nombre d\'enfants',
        'stato_civile_label': 'État Civil',
        'mansione_label': 'Poste',
        'reparto_label': 'Département',
        'supervisore_label': 'Superviseur',
        'luogo_lavoro_label': 'Lieu de travail',
        'salario_label': 'Salaire (FCFA)',
        'data_inizio_label': 'Date de début',
        'tipo_paga_label': 'Type de paiement',
        'montant_label': 'Montant',
        'emergenza_nome_label': 'Nom Contact Urgence',
        'emergenza_parentela_label': 'Relation',
        'emergenza_tel_label': 'Téléphone Urgence',
        'emergenza_indirizzo_label': 'Adresse Urgence',
        'candidatura_info': 'Ceci n\'est PAS un contrat, mais seulement l\'envoi de votre candidature.',
        'candidatura_titolo': 'Informations Personnelles',
        'candidatura_prof': 'Informations Professionnelles',
        'candidatura_skills': 'Vos compétences / Skills',
        'candidatura_motivazione': 'Pourquoi PROACIER?',
        'candidatura_disponibilite': 'Disponibilité',
        'candidatura_btn': 'Envoyer ma candidature',
        'candidatura_success': 'Candidature envoyée avec succès!',
        'candidatura_error': 'Champs obligatoires (*)',
        'giornalieri_titolo_page': 'Transmission de Données - Journaliers',
        'giornalieri_warning': 'Ceci n\'est PAS un contrat d\'embauche, mais seulement la transmission de vos données pour un futur emploi éventuel et le paiement des journaliers.',
        'giornalieri_personal': 'Informations Personnelles',
        'giornalieri_coord': 'Coordonnées',
        'giornalieri_prof': 'Informations Professionnelles',
        'giornalieri_btn': 'Transmettre mes données',
        'giornalieri_success': 'Données transmises avec succès!',
        'giornalieri_code': 'Code',
        'giornalieri_pin': 'PIN',
        'dashboard_admin': 'Mot de passe administrateur',
        'dashboard_connexion': 'Connexion',
        'dashboard_success': 'Connecté administrateur',
        'dashboard_deconnexion': 'Déconnexion',
        'dashboard_gestion': 'Gestion des salaires individuels',
        'dashboard_total': 'Total travailleurs',
        'dashboard_select': 'Sélectionner un travailleur',
        'dashboard_code': 'Code',
        'dashboard_tipo': 'Type de paiement',
        'dashboard_montant': 'Montant (FCFA)',
        'dashboard_save': 'Enregistrer le salaire',
        'dashboard_saved': 'Salaire enregistré!',
        'dashboard_error': 'Erreur',
        'home': 'Accueil',
        'new_hiring': 'Nouvelle Embauche',
        'spontaneous': 'Candidature Spontanée',
        'worker_space': 'Espace Travailleur',
        'admin_panel': 'Tableau de Bord',
    },
    'it': {
        'titolo': 'PROACIER - GESTIONE RISORSE UMANE',
        'sottotitolo': 'Sistema di Reclutamento - Senegal',
        'lingua': 'Lingua',
        'candidature': 'Candidatura Spontanea',
        'espace_travailleur': 'Spazio Lavoratore',
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'nuova_assunzione': 'Nuova Assunzione (Completo)',
        'home_desc_1': 'Trasmissione dati per nuovi lavoratori e giornalieri',
        'home_desc_2': 'Candidature spontanee',
        'home_desc_3': 'Spazio personale lavoratore',
        'home_desc_4': 'Pagamento giornalieri',
        'home_titolo': 'Come usare l\'applicazione',
        'home_btn_1': 'Candidatura Spontanea',
        'home_btn_2': 'Spazio Lavoratore',
        'home_btn_3': 'Dashboard',
        'giornalieri_titolo': 'Già lavoratore?',
        'giornalieri_desc': 'Accedi al tuo spazio personale',
        'nuovo_giornaliero_titolo': 'Nuovo / Giornaliero?',
        'nuovo_giornaliero_desc': 'Trasmetti i tuoi dati (non è un contratto)',
        'login_btn': 'Accedi al mio spazio',
        'trasmissione_btn': 'Trasmetti i miei dati',
        'i_miei_dati': 'I Miei Dati',
        'accesso_negato': 'Accesso negato',
        'step1': '1. IDENTITÀ & FAMIGLIA',
        'step2': '2. COORDINATE',
        'step3': '3. DOCUMENTI UFFICIALI',
        'step4': '4. IMPIEGO & SALARIO',
        'step5': '5. COMPETENZE & SALUTE',
        'step6': '6. EMERGENZA & CONFERMA',
        'suivant': 'Avanti →',
        'precedent': '← Indietro',
        'generer_pdf': 'Genera PDF & Accetta',
        'enregistrement_reussi': 'Registrazione riuscita!',
        'conservez_identifiants': 'CONSERVA QUESTI IDENTIFICATIVI',
        'code_acces': 'Codice accesso',
        'pin_acces': 'PIN accesso',
        'telecharger_pdf': 'Scarica PDF',
        'retour': 'Indietro',
        'cognome': 'Cognome *',
        'nome': 'Nome *',
        'data_nascita': 'Data di nascita',
        'luogo_nascita': 'Luogo di nascita *',
        'nazionalita': 'Nazionalità *',
        'sesso': 'Sesso *',
        'stato_civile': 'Stato civile *',
        'numero_mogli': 'Numero mogli',
        'figli_totale': 'Numero totale figli',
        'indirizzo': 'Indirizzo *',
        'quartiere': 'Quartiere *',
        'comune': 'Comune *',
        'dipartimento': 'Dipartimento / Regione *',
        'telefono_1': 'Telefono 1 *',
        'telefono_2': 'Telefono 2',
        'telefono_3': 'Telefono 3',
        'cni': 'CNI (Carta Nazionale Identità) *',
        'nif': 'NIF',
        'css': 'CSS (Sicurezza Sociale)',
        'cmu': 'CMU',
        'ipres': 'IPRES',
        'mansione_1': 'Mansione / Funzione *',
        'luogo_lavoro': 'Luogo di lavoro *',
        'reparto': 'Reparto / Servizio',
        'supervisore': 'Supervisore',
        'data_inizio_1': 'Data inizio *',
        'salario': 'Salario (FCFA) *',
        'ore_giorno': 'Ore al giorno',
        'giorni_settimana': 'Giorni a settimana',
        'pagamento': 'Tipo pagamento',
        'wave_orange': 'N° Wave / Orange Money',
        'categoria_competenza': 'Categoria competenza',
        'dettaglio_competenza': 'Dettaglio competenza',
        'patente': 'Patente di guida',
        'gruppo_sanguigno': 'Gruppo sanguigno',
        'rh': 'Rh',
        'allergie': 'Allergie',
        'malattie': 'Malattie croniche',
        'idoneita': 'Idoneità medica',
        'data_visita': 'Data visita medica',
        'emergenza_nome': 'Nome contatto emergenza *',
        'emergenza_parentela': 'Parentela *',
        'emergenza_tel': 'Telefono emergenza *',
        'emergenza_indirizzo': 'Indirizzo emergenza',
        'certifico': 'Certifico l\'esattezza delle informazioni e accetto le condizioni.',
        'leggi_condizioni': 'Leggi le condizioni complete',
        'certifico_checkbox': 'Certifico l\'esattezza delle informazioni',
        'connexion_mon_espace': 'Accedi al mio spazio',
        'code_access_input': 'Codice accesso',
        'pin_input': 'PIN personale',
        'se_connecter': 'Accedi',
        'mes_donnees_titolo': 'I Miei Dati Personali',
        'donnees_non_modifiables': 'Dati Personali (non modificabili)',
        'donnees_modifiables': 'Dati Modificabili',
        'mettre_a_jour': 'Aggiorna',
        'salaire_titolo': 'Informazioni Salariali',
        'salaire_desc': 'Il tuo salario è gestito dall\'amministrazione',
        'cognome_label': 'Cognome',
        'nome_label': 'Nome',
        'data_nascita_label': 'Data Nascita',
        'luogo_nascita_label': 'Luogo Nascita',
        'cni_label': 'CNI',
        'css_label': 'CSS',
        'ipres_label': 'IPRES',
        'codice_label': 'Codice Operatore',
        'telefono_label': 'Telefono *',
        'telefono2_label': 'Telefono 2',
        'indirizzo_label': 'Indirizzo *',
        'quartiere_label': 'Quartiere',
        'comune_label': 'Comune',
        'dipartimento_label': 'Dipartimento/Regione',
        'figli_label': 'Numero figli',
        'stato_civile_label': 'Stato Civile',
        'mansione_label': 'Mansione',
        'reparto_label': 'Reparto',
        'supervisore_label': 'Supervisore',
        'luogo_lavoro_label': 'Luogo di Lavoro',
        'salario_label': 'Salario (FCFA)',
        'data_inizio_label': 'Data Inizio',
        'tipo_paga_label': 'Tipo pagamento',
        'montant_label': 'Importo',
        'emergenza_nome_label': 'Nome Contatto Emergenza',
        'emergenza_parentela_label': 'Parentela',
        'emergenza_tel_label': 'Telefono Emergenza',
        'emergenza_indirizzo_label': 'Indirizzo Emergenza',
        'candidatura_info': 'Questo NON è un contratto, ma solo l\'invio della tua candidatura.',
        'candidatura_titolo': 'Informazioni Personali',
        'candidatura_prof': 'Informazioni Professionali',
        'candidatura_skills': 'Le tue competenze / Skills',
        'candidatura_motivazione': 'Perché PROACIER?',
        'candidatura_disponibilite': 'Disponibilità',
        'candidatura_btn': 'Invia candidatura',
        'candidatura_success': 'Candidatura inviata con successo!',
        'candidatura_error': 'Campi obbligatori (*)',
        'giornalieri_titolo_page': 'Trasmissione Dati - Giornalieri',
        'giornalieri_warning': 'Questo NON è un contratto di assunzione, ma solo la trasmissione dei tuoi dati per un futuro eventuale impiego e il pagamento dei giornalieri.',
        'giornalieri_personal': 'Informazioni Personali',
        'giornalieri_coord': 'Coordinate',
        'giornalieri_prof': 'Informazioni Professionali',
        'giornalieri_btn': 'Trasmetti i miei dati',
        'giornalieri_success': 'Dati trasmessi con successo!',
        'giornalieri_code': 'Codice',
        'giornalieri_pin': 'PIN',
        'dashboard_admin': 'Password amministratore',
        'dashboard_connexion': 'Accedi',
        'dashboard_success': 'Connesso come amministratore',
        'dashboard_deconnexion': 'Logout',
        'dashboard_gestion': 'Gestione salari individuali',
        'dashboard_total': 'Totale lavoratori',
        'dashboard_select': 'Seleziona lavoratore',
        'dashboard_code': 'Codice',
        'dashboard_tipo': 'Tipo pagamento',
        'dashboard_montant': 'Importo (FCFA)',
        'dashboard_save': 'Salva salario',
        'dashboard_saved': 'Salario salvato!',
        'dashboard_error': 'Errore',
        'home': 'Home',
        'new_hiring': 'Nuova Assunzione',
        'spontaneous': 'Candidatura Spontanea',
        'worker_space': 'Spazio Lavoratore',
        'admin_panel': 'Dashboard',
    },
    'en': {
        'titolo': 'PROACIER - HUMAN RESOURCES',
        'sottotitolo': 'Recruitment System - Senegal',
        'lingua': 'Language',
        'candidature': 'Spontaneous Application',
        'espace_travailleur': 'Worker Space',
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'nuova_assunzione': 'New Hiring (Complete)',
        'home_desc_1': 'Data transmission for new workers and daily workers',
        'home_desc_2': 'Spontaneous applications',
        'home_desc_3': 'Personal worker space',
        'home_desc_4': 'Daily workers payment',
        'home_titolo': 'How to use the application',
        'home_btn_1': 'Spontaneous Application',
        'home_btn_2': 'Worker Space',
        'home_btn_3': 'Dashboard',
        'giornalieri_titolo': 'Already a worker?',
        'giornalieri_desc': 'Access your personal space',
        'nuovo_giornaliero_titolo': 'New / Daily worker?',
        'nuovo_giornaliero_desc': 'Submit your data (not a contract)',
        'login_btn': 'Login to my space',
        'trasmissione_btn': 'Submit my data',
        'i_miei_dati': 'My Data',
        'accesso_negato': 'Access denied',
        'step1': '1. IDENTITY & FAMILY',
        'step2': '2. CONTACT INFO',
        'step3': '3. OFFICIAL DOCUMENTS',
        'step4': '4. EMPLOYMENT & SALARY',
        'step5': '5. SKILLS & HEALTH',
        'step6': '6. EMERGENCY & CONFIRMATION',
        'suivant': 'Next →',
        'precedent': '← Back',
        'generer_pdf': 'Generate PDF & Accept',
        'enregistrement_reussi': 'Registration successful!',
        'conservez_identifiants': 'SAVE THESE CREDENTIALS',
        'code_acces': 'Access code',
        'pin_acces': 'PIN access',
        'telecharger_pdf': 'Download PDF',
        'retour': 'Back',
        'cognome': 'Surname *',
        'nome': 'First name *',
        'data_nascita': 'Date of birth',
        'luogo_nascita': 'Place of birth *',
        'nazionalita': 'Nationality *',
        'sesso': 'Gender *',
        'stato_civile': 'Marital status *',
        'numero_mogli': 'Number of wives',
        'figli_totale': 'Total children',
        'indirizzo': 'Address *',
        'quartiere': 'Neighborhood *',
        'comune': 'Municipality *',
        'dipartimento': 'Department / Region *',
        'telefono_1': 'Phone 1 *',
        'telefono_2': 'Phone 2',
        'telefono_3': 'Phone 3',
        'cni': 'CNI (National ID Card) *',
        'nif': 'NIF',
        'css': 'CSS (Social Security)',
        'cmu': 'CMU',
        'ipres': 'IPRES',
        'mansione_1': 'Position / Function *',
        'luogo_lavoro': 'Workplace *',
        'reparto': 'Department / Service',
        'supervisore': 'Supervisor',
        'data_inizio_1': 'Start date *',
        'salario': 'Salary (FCFA) *',
        'ore_giorno': 'Hours per day',
        'giorni_settimana': 'Days per week',
        'pagamento': 'Payment type',
        'wave_orange': 'Wave / Orange Money Number',
        'categoria_competenza': 'Skill category',
        'dettaglio_competenza': 'Skill detail',
        'patente': 'Driving license',
        'gruppo_sanguigno': 'Blood type',
        'rh': 'Rh',
        'allergie': 'Allergies',
        'malattie': 'Chronic diseases',
        'idoneita': 'Medical fitness',
        'data_visita': 'Medical visit date',
        'emergenza_nome': 'Emergency contact name *',
        'emergenza_parentela': 'Relationship *',
        'emergenza_tel': 'Emergency phone *',
        'emergenza_indirizzo': 'Emergency address',
        'certifico': 'I certify the accuracy of the information and accept the conditions.',
        'leggi_condizioni': 'Read full conditions',
        'certifico_checkbox': 'I certify the accuracy of the information',
        'connexion_mon_espace': 'Login to my space',
        'code_access_input': 'Access code',
        'pin_input': 'Personal PIN',
        'se_connecter': 'Login',
        'mes_donnees_titolo': 'My Personal Data',
        'donnees_non_modifiables': 'Personal Data (non-modifiable)',
        'donnees_modifiables': 'Modifiable Data',
        'mettre_a_jour': 'Update',
        'salaire_titolo': 'Salary Information',
        'salaire_desc': 'Your salary is managed by administration',
        'cognome_label': 'Surname',
        'nome_label': 'First name',
        'data_nascita_label': 'Date of birth',
        'luogo_nascita_label': 'Place of birth',
        'cni_label': 'CNI',
        'css_label': 'CSS',
        'ipres_label': 'IPRES',
        'codice_label': 'Operator Code',
        'telefono_label': 'Phone *',
        'telefono2_label': 'Phone 2',
        'indirizzo_label': 'Address *',
        'quartiere_label': 'Neighborhood',
        'comune_label': 'Municipality',
        'dipartimento_label': 'Department/Region',
        'figli_label': 'Number of children',
        'stato_civile_label': 'Marital status',
        'mansione_label': 'Position',
        'reparto_label': 'Department',
        'supervisore_label': 'Supervisor',
        'luogo_lavoro_label': 'Workplace',
        'salario_label': 'Salary (FCFA)',
        'data_inizio_label': 'Start date',
        'tipo_paga_label': 'Payment type',
        'montant_label': 'Amount',
        'emergenza_nome_label': 'Emergency Contact Name',
        'emergenza_parentela_label': 'Relationship',
        'emergenza_tel_label': 'Emergency Phone',
        'emergenza_indirizzo_label': 'Emergency Address',
        'candidatura_info': 'This is NOT a contract, but only the submission of your application.',
        'candidatura_titolo': 'Personal Information',
        'candidatura_prof': 'Professional Information',
        'candidatura_skills': 'Your skills / Skills',
        'candidatura_motivazione': 'Why PROACIER?',
        'candidatura_disponibilite': 'Availability',
        'candidatura_btn': 'Send application',
        'candidatura_success': 'Application sent successfully!',
        'candidatura_error': 'Required fields (*)',
        'giornalieri_titolo_page': 'Data Transmission - Daily Workers',
        'giornalieri_warning': 'This is NOT an employment contract, but only the transmission of your data for a possible future employment and daily workers payment.',
        'giornalieri_personal': 'Personal Information',
        'giornalieri_coord': 'Contact Information',
        'giornalieri_prof': 'Professional Information',
        'giornalieri_btn': 'Submit my data',
        'giornalieri_success': 'Data transmitted successfully!',
        'giornalieri_code': 'Code',
        'giornalieri_pin': 'PIN',
        'dashboard_admin': 'Administrator password',
        'dashboard_connexion': 'Login',
        'dashboard_success': 'Connected as administrator',
        'dashboard_deconnexion': 'Logout',
        'dashboard_gestion': 'Individual salary management',
        'dashboard_total': 'Total workers',
        'dashboard_select': 'Select worker',
        'dashboard_code': 'Code',
        'dashboard_tipo': 'Payment type',
        'dashboard_montant': 'Amount (FCFA)',
        'dashboard_save': 'Save salary',
        'dashboard_saved': 'Salary saved!',
        'dashboard_error': 'Error',
        'home': 'Home',
        'new_hiring': 'New Hiring',
        'spontaneous': 'Spontaneous Application',
        'worker_space': 'Worker Space',
        'admin_panel': 'Dashboard',
    }
}

def get_testo(chiave):
    lingua = st.session_state.get('lingua', 'fr')
    return TRADUZIONI.get(lingua, TRADUZIONI['fr']).get(chiave, chiave)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'pagina' not in st.session_state:
    st.session_state.pagina = 'home'
if 'lingua' not in st.session_state:
    st.session_state.lingua = 'fr'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'codice_operatore' not in st.session_state:
    st.session_state.codice_operatore = None
if 'pin_operatore' not in st.session_state:
    st.session_state.pin_operatore = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'dati_form' not in st.session_state:
    st.session_state.dati_form = {}
if 'admin_logged' not in st.session_state:
    st.session_state.admin_logged = False

# ============================================================================
# FUNZIONI
# ============================================================================

def genera_codice_operatore(cognome, nome):
    anno = datetime.now().year
    random_num = random.randint(1000, 9999)
    return f"THS-{anno}-{random_num}"

def genera_pin():
    return str(random.randint(1000, 9999))

def salva_su_google_sheets(script_url, dati, action="append"):
    try:
        response = requests.post(
            script_url,
            json={"action": action, "row": dati},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"Errore salvataggio: {str(e)}")
        return False

# ============================================================================
# PDF
# ============================================================================

class PDFProacier(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'PROACIER - FICHE EMPLOYE', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def sezione(self, titolo):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(94, 165, 41)
        self.cell(0, 8, f'  {titolo}', 0, 1, 'L', True)
        self.ln(2)
    
    def campo_doppio(self, label1, val1, label2, val2):
        self.set_font('Helvetica', 'B', 9)
        self.cell(45, 6, label1, 0, 0)
        self.set_font('Helvetica', '', 9)
        self.cell(50, 6, str(val1), 0, 0)
        self.set_font('Helvetica', 'B', 9)
        self.cell(45, 6, label2, 0, 0)
        self.set_font('Helvetica', '', 9)
        self.cell(50, 6, str(val2), 0, 1)

def genera_pdf_lavoratore(dati):
    pdf = PDFProacier()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Helvetica', '', 9)
    
    pdf.sezione("1. IDENTITE & FAMILLE")
    pdf.campo_doppio("Nom:", dati.get('cognome', ''), "Prenom(s):", dati.get('nome', ''))
    pdf.campo_doppio("Ne(e) le:", dati.get('data_nascita', ''), "a:", dati.get('luogo_nascita', ''))
    pdf.campo_doppio("Nationalite:", dati.get('nazionalita', ''), "Sexe:", dati.get('sesso', ''))
    pdf.campo_doppio("Etat civil:", dati.get('stato_civile', ''), "Epouses:", dati.get('numero_mogli', ''))
    pdf.campo_doppio("Enfants:", dati.get('figli_totale', ''), "", "")
    pdf.ln(3)
    
    pdf.sezione("2. COORDONNEES")
    pdf.campo_doppio("Adresse:", dati.get('indirizzo', ''), "Quartier:", dati.get('quartiere', ''))
    pdf.campo_doppio("Commune:", dati.get('comune', ''), "Region:", dati.get('regione_senegal', ''))
    pdf.campo_doppio("Tel 1:", dati.get('telefono_1', ''), "Tel 2:", dati.get('telefono_2', ''))
    pdf.ln(3)
    
    pdf.sezione("3. DOCUMENTS OFFICIELS")
    pdf.campo_doppio("CNI:", dati.get('cni', ''), "NIF:", dati.get('nif', ''))
    pdf.campo_doppio("CSS:", dati.get('css', ''), "IPRES:", dati.get('ipres', ''))
    pdf.ln(3)
    
    pdf.sezione("4. EMPLOI & SALAIRE")
    pdf.campo_doppio("Poste:", dati.get('mansione_1', ''), "Lieu:", dati.get('luogo_lavoro', ''))
    pdf.campo_doppio("Service:", dati.get('reparto', ''), "Superviseur:", dati.get('supervisore', ''))
    pdf.campo_doppio("Debut:", dati.get('data_inizio_1', ''), "Salaire:", f"{dati.get('salario', '')} FCFA")
    pdf.campo_doppio("Wave/OM:", dati.get('wave_orange', ''), "Paiement:", dati.get('pagamento', ''))
    pdf.ln(3)
    
    pdf.sezione("5. COMPETENCES & SANTE")
    pdf.campo_doppio("Competence:", dati.get('categoria_competenza', ''), "Detail:", dati.get('dettaglio_competenza', ''))
    pdf.campo_doppio("Permis:", dati.get('patente', ''), "Sang:", f"{dati.get('gruppo_sanguigno', '')} {dati.get('rh', '')}")
    pdf.campo_doppio("Allergies:", dati.get('allergie', ''), "Maladies:", dati.get('malattie', ''))
    pdf.campo_doppio("Aptitude:", dati.get('idoneita', ''), "Date:", dati.get('data_visita', ''))
    pdf.ln(3)
    
    pdf.sezione("6. CONTACT URGENCE")
    pdf.campo_doppio("Nom:", dati.get('emergenza_nome', ''), "Lien:", dati.get('emergenza_parentela', ''))
    pdf.campo_doppio("Tel:", dati.get('emergenza_tel', ''), "Adresse:", dati.get('emergenza_indirizzo', ''))
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.multi_cell(0, 4, "Je certifie l'exactitude des informations et accepte les conditions de recrutement.")
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 6, 'CANDIDAT', 1, 0, 'C')
    pdf.cell(95, 6, 'EMPLOYEUR', 1, 1, 'C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(95, 15, '', 1, 0)
    pdf.cell(95, 15, '', 1, 1)
    
    pdf.ln(5)
    pdf.set_fill_color(255, 243, 205)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 8, 'IDENTIFIANTS DE CONNEXION - CONSERVEZ CE DOCUMENT', 0, 1, 'C', True)
    pdf.ln(2)
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, f"Code d'acces: {dati.get('codice', '___________')}", 0, 1)
    pdf.cell(0, 6, f"PIN: {dati.get('pin', '___________')}", 0, 1)
    pdf.ln(2)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 4, "Ces identifiants sont personnels et confidentiels.")
    pdf.set_text_color(0, 0, 0)
    
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1', errors='ignore')
    return bytes(pdf_bytes)

# ============================================================================
# PAGINE
# ============================================================================

def pagina_home():
    st.title(get_testo('titolo'))
    st.subheader(get_testo('sottotitolo'))
    
    st.markdown("---")
    st.subheader("🎯 A cosa serve questa applicazione?")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **📋 {get_testo('home_desc_1')}**
        
        **📨 {get_testo('home_desc_2')}**
        """)
    
    with col2:
        st.markdown(f"""
        **👤 {get_testo('home_desc_3')}**
        
        **💰 {get_testo('home_desc_4')}**
        """)
    
    st.markdown("---")
    st.subheader(get_testo('home_titolo'))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(get_testo('home_btn_1'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'candidatura'
            st.rerun()
    
    with col2:
        if st.button(get_testo('home_btn_2'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'espace_travailleur'
            st.rerun()
    
    with col3:
        if st.button(get_testo('home_btn_3'), use_container_width=True):
            st.session_state.pagina = 'dashboard'
            st.rerun()

def pagina_espace_travailleur():
    st.title(get_testo('espace_travailleur'))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 " + get_testo('giornalieri_titolo'))
        st.info(get_testo('giornalieri_desc'))
        if st.button(get_testo('login_btn'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'login_lavoratore'
            st.rerun()
    
    with col2:
        st.markdown("### 📝 " + get_testo('nuovo_giornaliero_titolo'))
        st.info(get_testo('nuovo_giornaliero_desc'))
        if st.button(get_testo('trasmissione_btn'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'trasmissione_dati_giornalieri'
            st.rerun()

def pagina_login_lavoratore():
    st.title(get_testo('connexion_mon_espace'))
    
    with st.form("login_form"):
        codice = st.text_input(get_testo('code_access_input'))
        pin = st.text_input(get_testo('pin_input'), type="password")
        submitted = st.form_submit_button(get_testo('se_connecter'), type="primary")
        
        if submitted:
            if codice and pin:
                try:
                    response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
                    if response.status_code == 200:
                        data = response.json()
                        df = pd.DataFrame(data[1:], columns=data[0])
                        
                        mask = (df['Codice'] == codice) & (df['PIN'] == pin)
                        
                        if mask.any():
                            st.session_state.logged_in = True
                            st.session_state.user_type = 'lavoratore'
                            st.session_state.codice_operatore = codice
                            st.session_state.pin_operatore = pin
                            st.success("Connexion réussie!")
                            st.session_state.pagina = 'area_lavoratore'
                            st.rerun()
                        else:
                            st.error("Code ou PIN incorrect")
                    else:
                        st.error("Erreur de connexion")
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
            else:
                st.error("Veuillez remplir tous les champs")
    
    if st.button(get_testo('retour')):
        st.session_state.pagina = 'espace_travailleur'
        st.rerun()

def pagina_area_lavoratore():
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'lavoratore':
        st.error(get_testo('accesso_negato'))
        st.stop()
    
    st.title(get_testo('mes_donnees_titolo'))
    st.success(f"Bonjour - Code: {st.session_state.codice_operatore}")
    
    try:
        response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            
            mask = (df['Codice'] == st.session_state.codice_operatore) & (df['PIN'] == st.session_state.pin_operatore)
            
            if not mask.any():
                st.error("Travailleur non trouvé")
                st.stop()
            
            row = df[mask].iloc[0]
            idx = row.name
            
            st.markdown("---")
            st.subheader(get_testo('donnees_non_modifiables'))
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.text_input(get_testo('cognome_label'), value=row.get('Cognome', ''), disabled=True)
                st.text_input(get_testo('nome_label'), value=row.get('Nome', ''), disabled=True)
                st.text_input(get_testo('data_nascita_label'), value=row.get('Data_Nascita', ''), disabled=True)
            
            with col2:
                st.text_input(get_testo('cni_label'), value=row.get('CNI', ''), disabled=True)
                st.text_input(get_testo('css_label'), value=row.get('CSS', ''), disabled=True)
                st.text_input(get_testo('ipres_label'), value=row.get('IPRES', ''), disabled=True)
            
            with col3:
                st.text_input(get_testo('codice_label'), value=row.get('Codice', ''), disabled=True)
                st.text_input(get_testo('luogo_nascita_label'), value=row.get('Luogo_Nascita', ''), disabled=True)
            
            st.markdown("---")
            st.subheader(get_testo('donnees_modifiables'))
            
            with st.form("modifica_dati"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    nuovo_tel = st.text_input(get_testo('telefono_label'), value=row.get('Telefono', ''))
                    nuovo_indirizzo = st.text_input(get_testo('indirizzo_label'), value=row.get('Indirizzo', ''))
                    nuovi_figli = st.number_input(get_testo('figli_label'), min_value=0, value=int(row.get('Figli', 0) if pd.notna(row.get('Figli')) else 0))
                
                with col2:
                    nuovo_tel2 = st.text_input(get_testo('telefono2_label'), value=row.get('Telefono2', ''))
                    nuovo_quartiere = st.text_input(get_testo('quartiere_label'), value=row.get('Quartiere', ''))
                    nuovo_comune = st.text_input(get_testo('comune_label'), value=row.get('Comune', ''))
                
                with col3:
                    nuovo_dipartimento = st.text_input(get_testo('dipartimento_label'), value=row.get('Dipartimento', ''))
                    nuovo_stato_civile = st.selectbox(get_testo('stato_civile_label'), ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"], 
                                                       index=0 if row.get('Stato_Civile') == "Célibataire" else 1)
                
                st.markdown("---")
                st.subheader(get_testo('salaire_titolo'))
                st.info(get_testo('salaire_desc'))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    tipo_paga = row.get('Tipo_Paga', 'Non défini')
                    st.text_input(get_testo('tipo_paga_label'), value=tipo_paga, disabled=True)
                
                with col2:
                    valore_paga = row.get('Valore_Paga', 'Non défini')
                    st.text_input(get_testo('montant_label'), value=valore_paga, disabled=True)
                
                st.markdown("---")
                st.subheader("🚨 Contact d'Urgence")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    emergenza_nome = st.text_input(get_testo('emergenza_nome_label'), value=row.get('Emergenza_Nome', ''))
                    emergenza_parentela = st.text_input(get_testo('emergenza_parentela_label'), value=row.get('Emergenza_Parentela', ''))
                
                with col2:
                    emergenza_tel = st.text_input(get_testo('emergenza_tel_label'), value=row.get('Emergenza_Tel', ''))
                    emergenza_indirizzo = st.text_input(get_testo('emergenza_indirizzo_label'), value=row.get('Emergenza_Indirizzo', ''))
                
                submitted = st.form_submit_button(get_testo('mettre_a_jour'), type="primary")
                
                if submitted:
                    if not nuovo_tel or not nuovo_indirizzo:
                        st.error("Téléphone et Adresse sont obligatoires!")
                        st.stop()
                    
                    try:
                        df.loc[idx, 'Telefono'] = nuovo_tel
                        df.loc[idx, 'Telefono2'] = nuovo_tel2
                        df.loc[idx, 'Indirizzo'] = nuovo_indirizzo
                        df.loc[idx, 'Figli'] = nuovi_figli
                        df.loc[idx, 'Stato_Civile'] = nuovo_stato_civile
                        df.loc[idx, 'Quartiere'] = nuovo_quartiere
                        df.loc[idx, 'Comune'] = nuovo_comune
                        df.loc[idx, 'Dipartimento'] = nuovo_dipartimento
                        df.loc[idx, 'Emergenza_Nome'] = emergenza_nome
                        df.loc[idx, 'Emergenza_Parentela'] = emergenza_parentela
                        df.loc[idx, 'Emergenza_Tel'] = emergenza_tel
                        df.loc[idx, 'Emergenza_Indirizzo'] = emergenza_indirizzo
                        
                        dati_json = {"action": "update", "data": df.to_dict(orient='records')}
                        resp = requests.post(GOOGLE_SCRIPT_URL_ASSUNZIONI, json=dati_json)
                        
                        if resp.status_code == 200:
                            st.success("✅ Données mises à jour!")
                            st.ballo()
                        else:
                            st.error("Erreur sauvegarde")
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
        
        else:
            st.error("Erreur chargement")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
    
    if st.button(get_testo('logout')):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.codice_operatore = None
        st.session_state.pin_operatore = None
        st.session_state.pagina = 'home'
        st.rerun()

def pagina_candidatura():
    st.title(get_testo('candidature'))
    st.info(get_testo('candidatura_info'))
    
    with st.form("form_candidatura"):
        st.subheader(get_testo('candidatura_titolo'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            cognome = st.text_input(get_testo('cognome'), "")
            nome = st.text_input(get_testo('nome'), "")
            data_nascita = st.text_input(get_testo('data_nascita'), "")
            luogo_nascita = st.text_input(get_testo('luogo_nascita'), "")
        
        with col2:
            indirizzo = st.text_input(get_testo('indirizzo'), "")
            comune = st.text_input(get_testo('comune'), "")
            regione = st.text_input(get_testo('dipartimento'), "")
            telefono = st.text_input(get_testo('telefono_1'), "")
        
        st.markdown("---")
        st.subheader(get_testo('candidatura_prof'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            mansione = st.text_input(get_testo('mansione_1'), "")
            studi = st.selectbox("Niveau d'études", ["Aucun", "Primaire", "Collège", "Lycée", "CAP", "BTS", "Licence", "Master", "Doctorat"])
            esperienze = st.number_input("Années d'expérience", min_value=0, max_value=50, value=0)
        
        with col2:
            poste_actuel = st.text_input("Poste actuel", "")
            entreprise_actuelle = st.text_input("Entreprise actuelle", "")
            specialite = st.text_input("Spécialité", "")
        
        st.markdown("---")
        skills = st.text_area(get_testo('candidatura_skills'), height=100)
        motivazione = st.text_area(get_testo('candidatura_motivazione'), height=150)
        disponibilite = st.selectbox(get_testo('candidatura_disponibilite'), ["Immédiate", "1 semaine", "2 semaines", "1 mois", "Autre"])
        
        submitted = st.form_submit_button(get_testo('candidatura_btn'), type="primary")
        
        if submitted:
            if not cognome or not nome or not telefono:
                st.error(get_testo('candidatura_error'))
                st.stop()
            
            dati = {
                'id': f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}",
                'data_candidatura': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'cognome': cognome, 'nome': nome, 'telefono': telefono,
                'indirizzo': indirizzo, 'comune': comune, 'regione': regione,
                'mansione_richiesta': mansione, 'studi': studi,
            }
            
            if salva_su_google_sheets(GOOGLE_SCRIPT_URL_CANDIDATURE, dati, action="append"):
                st.success(get_testo('candidatura_success'))
                st.ballo()
            else:
                st.error("Erreur envoi")

def pagina_trasmissione_dati_giornalieri():
    st.title(get_testo('giornalieri_titolo_page'))
    st.warning(get_testo('giornalieri_warning'))
    
    with st.form("form_giornalieri"):
        st.subheader(get_testo('giornalieri_personal'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            cognome = st.text_input(get_testo('cognome'), "")
            nome = st.text_input(get_testo('nome'), "")
            data_nascita = st.text_input(get_testo('data_nascita'), "")
            luogo_nascita = st.text_input(get_testo('luogo_nascita'), "")
            nazionalita = st.text_input(get_testo('nazionalita'), "Sénégalaise")
        
        with col2:
            sesso = st.selectbox(get_testo('sesso'), ["Masculin", "Féminin"])
            stato_civile = st.selectbox(get_testo('stato_civile'), ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"])
            figli = st.number_input(get_testo('figli_totale'), min_value=0, value=0)
            cni = st.text_input(get_testo('cni'), "")
            css = st.text_input(get_testo('css'), "")
        
        st.markdown("---")
        st.subheader(get_testo('giornalieri_coord'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            telefono = st.text_input(get_testo('telefono_1'), "")
            indirizzo = st.text_input(get_testo('indirizzo'), "")
            quartiere = st.text_input(get_testo('quartiere'), "")
        
        with col2:
            comune = st.text_input(get_testo('comune'), "")
            dipartimento = st.text_input(get_testo('dipartimento'), "")
        
        st.markdown("---")
        st.subheader(get_testo('giornalieri_prof'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            mansione = st.text_input(get_testo('mansione_1'), "")
        
        with col2:
            disponibilita = st.selectbox(get_testo('candidatura_disponibilite'), ["Immédiate", "1 semaine", "2 semaines", "1 mois", "Autre"])
        
        submitted = st.form_submit_button(get_testo('giornalieri_btn'), type="primary")
        
        if submitted:
            if not cognome or not nome or not telefono or not indirizzo:
                st.error(get_testo('candidatura_error'))
                st.stop()
            
            codice = genera_codice_operatore(cognome, nome)
            pin = genera_pin()
            
            dati = {
                'id': f"JOUR-{datetime.now().year}-{random.randint(1000, 9999)}",
                'codice': codice, 'pin': pin,
                'data_registrazione': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'cognome': cognome, 'nome': nome,
                'data_nascita': data_nascita, 'luogo_nascita': luogo_nascita,
                'nazionalita': nazionalita, 'sesso': sesso,
                'stato_civile': stato_civile, 'figli_totale': figli,
                'cni': cni, 'css': css,
                'telefono_1': telefono, 'indirizzo': indirizzo,
                'quartiere': quartiere, 'comune': comune,
                'regione_senegal': dipartimento,
                'mansione_1': mansione, 'tipo': 'Giornaliero'
            }
            
            if salva_su_google_sheets(GOOGLE_SCRIPT_URL_ASSUNZIONI, dati, action="append"):
                st.success(get_testo('giornalieri_success'))
                st.info(f"**{get_testo('giornalieri_code')}:** {codice}\n**{get_testo('giornalieri_pin')}:** {pin}")
                st.ballo()
            else:
                st.error("Erreur")

def pagina_registrazione_multi_step(lingua):
    st.title(get_testo('nuova_assunzione'))
    
    progress = st.progress((st.session_state.step - 1) / 6)
    st.write(f"**Step {st.session_state.step} / 6**")
    
    dati = st.session_state.dati_form
    
    # STEP 1
    if st.session_state.step == 1:
        st.subheader(get_testo('step1'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['cognome'] = st.text_input(get_testo('cognome'), value=dati.get('cognome', ''))
            dati['nome'] = st.text_input(get_testo('nome'), value=dati.get('nome', ''))
            dati['data_nascita'] = st.text_input(get_testo('data_nascita'), value=dati.get('data_nascita', ''))
            dati['luogo_nascita'] = st.text_input(get_testo('luogo_nascita'), value=dati.get('luogo_nascita', ''))
        
        with col2:
            dati['nazionalita'] = st.text_input(get_testo('nazionalita'), value=dati.get('nazionalita', 'Sénégalaise'))
            dati['sesso'] = st.selectbox(get_testo('sesso'), ["Masculin", "Féminin"])
            dati['stato_civile'] = st.selectbox(get_testo('stato_civile'), ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"])
            dati['numero_mogli'] = st.number_input(get_testo('numero_mogli'), min_value=0, max_value=10, value=int(dati.get('numero_mogli', 0)))
            dati['figli_totale'] = st.number_input(get_testo('figli_totale'), min_value=0, max_value=50, value=int(dati.get('figli_totale', 0)))
        
        st.session_state.dati_form = dati
        
        if st.button(get_testo('suivant'), type="primary"):
            if dati.get('cognome') and dati.get('nome') and dati.get('luogo_nascita'):
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Champs obligatoires (*)")
    
    # STEP 2
    elif st.session_state.step == 2:
        st.subheader(get_testo('step2'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['indirizzo'] = st.text_input(get_testo('indirizzo'), value=dati.get('indirizzo', ''))
            dati['quartiere'] = st.text_input(get_testo('quartiere'), value=dati.get('quartiere', ''))
            dati['comune'] = st.text_input(get_testo('comune'), value=dati.get('comune', ''))
        
        with col2:
            dati['regione_senegal'] = st.text_input(get_testo('dipartimento'), value=dati.get('regione_senegal', ''))
            dati['telefono_1'] = st.text_input(get_testo('telefono_1'), value=dati.get('telefono_1', ''))
            dati['telefono_2'] = st.text_input(get_testo('telefono_2'), value=dati.get('telefono_2', ''))
            dati['telefono_3'] = st.text_input(get_testo('telefono_3'), value=dati.get('telefono_3', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent')):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button(get_testo('suivant'), type="primary"):
                if dati.get('indirizzo') and dati.get('quartiere') and dati.get('telefono_1'):
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("Champs obligatoires (*)")
    
    # STEP 3
    elif st.session_state.step == 3:
        st.subheader(get_testo('step3'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['cni'] = st.text_input(get_testo('cni'), value=dati.get('cni', ''))
            dati['nif'] = st.text_input(get_testo('nif'), value=dati.get('nif', ''))
            dati['css'] = st.text_input(get_testo('css'), value=dati.get('css', ''))
        
        with col2:
            dati['cmu'] = st.text_input(get_testo('cmu'), value=dati.get('cmu', ''))
            dati['ipres'] = st.text_input(get_testo('ipres'), value=dati.get('ipres', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent')):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button(get_testo('suivant'), type="primary"):
                if dati.get('cni'):
                    st.session_state.step = 4
                    st.rerun()
                else:
                    st.error("CNI obligatoire (*)")
    
    # STEP 4
    elif st.session_state.step == 4:
        st.subheader(get_testo('step4'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['mansione_1'] = st.text_input(get_testo('mansione_1'), value=dati.get('mansione_1', ''))
            dati['luogo_lavoro'] = st.text_input(get_testo('luogo_lavoro'), value=dati.get('luogo_lavoro', ''))
            dati['reparto'] = st.text_input(get_testo('reparto'), value=dati.get('reparto', ''))
            dati['supervisore'] = st.text_input(get_testo('supervisore'), value=dati.get('supervisore', ''))
        
        with col2:
            dati['data_inizio_1'] = st.text_input(get_testo('data_inizio_1'), value=dati.get('data_inizio_1', ''))
            dati['salario'] = st.text_input(get_testo('salario'), value=dati.get('salario', ''))
            dati['ore_giorno'] = st.number_input(get_testo('ore_giorno'), min_value=0, max_value=24, value=int(dati.get('ore_giorno', 8)))
            dati['giorni_settimana'] = st.number_input(get_testo('giorni_settimana'), min_value=0, max_value=7, value=int(dati.get('giorni_settimana', 6)))
            dati['pagamento'] = st.selectbox(get_testo('pagamento'), ["Horaire", "Journalier", "Mensuel", "Hebdomadaire"])
            dati['wave_orange'] = st.text_input(get_testo('wave_orange'), value=dati.get('wave_orange', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent')):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button(get_testo('suivant'), type="primary"):
                if dati.get('mansione_1') and dati.get('luogo_lavoro') and dati.get('data_inizio_1') and dati.get('salario'):
                    st.session_state.step = 5
                    st.rerun()
                else:
                    st.error("Champs obligatoires (*)")
    
    # STEP 5
    elif st.session_state.step == 5:
        st.subheader(get_testo('step5'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['categoria_competenza'] = st.text_input(get_testo('categoria_competenza'), value=dati.get('categoria_competenza', ''))
            dati['dettaglio_competenza'] = st.text_input(get_testo('dettaglio_competenza'), value=dati.get('dettaglio_competenza', ''))
            dati['patente'] = st.text_input(get_testo('patente'), value=dati.get('patente', ''))
        
        with col2:
            dati['gruppo_sanguigno'] = st.selectbox(get_testo('gruppo_sanguigno'), ["A", "B", "AB", "O", ""])
            dati['rh'] = st.selectbox(get_testo('rh'), ["+", "-"])
            dati['allergie'] = st.text_input(get_testo('allergie'), value=dati.get('allergie', ''))
            dati['malattie'] = st.text_input(get_testo('malattie'), value=dati.get('malattie', ''))
            dati['idoneita'] = st.text_input(get_testo('idoneita'), value=dati.get('idoneita', ''))
            dati['data_visita'] = st.text_input(get_testo('data_visita'), value=dati.get('data_visita', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent')):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button(get_testo('suivant'), type="primary"):
                st.session_state.step = 6
                st.rerun()
    
    # STEP 6
    elif st.session_state.step == 6:
        st.subheader(get_testo('step6'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['emergenza_nome'] = st.text_input(get_testo('emergenza_nome'), value=dati.get('emergenza_nome', ''))
            dati['emergenza_parentela'] = st.text_input(get_testo('emergenza_parentela'), value=dati.get('emergenza_parentela', ''))
        
        with col2:
            dati['emergenza_tel'] = st.text_input(get_testo('emergenza_tel'), value=dati.get('emergenza_tel', ''))
            dati['emergenza_indirizzo'] = st.text_input(get_testo('emergenza_indirizzo'), value=dati.get('emergenza_indirizzo', ''))
        
        st.markdown("---")
        st.info(get_testo('certifico'))
        st.markdown(f"[{get_testo('leggi_condizioni')}]({URL_CONDIZIONI})")
        
        certifica = st.checkbox(get_testo('certifico_checkbox'))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent')):
                st.session_state.step = 5
                st.rerun()
        with col2:
            if st.button(get_testo('generer_pdf'), type="primary"):
                if certifica and dati.get('emergenza_nome') and dati.get('emergenza_tel'):
                    codice = genera_codice_operatore(dati.get('cognome', ''), dati.get('nome', ''))
                    pin = genera_pin()
                    
                    dati['codice'] = codice
                    dati['pin'] = pin
                    dati['data_registrazione'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    dati['id'] = f"EMP-{datetime.now().year}-{random.randint(1000, 9999)}"
                    dati['tipo'] = 'Assunzione'
                    
                    if salva_su_google_sheets(GOOGLE_SCRIPT_URL_ASSUNZIONI, dati, action="append"):
                        st.success(get_testo('enregistrement_reussi'))
                        
                        pdf_bytes = genera_pdf_lavoratore(dati)
                        
                        st.markdown("---")
                        st.warning(f"⚠️ {get_testo('conservez_identifiants')}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**{get_testo('code_acces')}:** {codice}")
                        with col2:
                            st.info(f"**{get_testo('pin_acces')}:** {pin}")
                        
                        st.download_button(
                            label=f"📥 {get_testo('telecharger_pdf')}",
                            data=pdf_bytes,
                            file_name=f"Fiche_{dati.get('cognome', '')}.pdf",
                            mime="application/pdf"
                        )
                        
                        st.ballo()
                        st.session_state.dati_form = {}
                        st.session_state.step = 1
                    else:
                        st.error("Erreur enregistrement")
                else:
                    st.error("Certifiez et remplissez les champs urgence")
    
    progress.progress(st.session_state.step / 6)

def pagina_dashboard():
    st.title(get_testo('dashboard'))
    
    if not st.session_state.get('admin_logged'):
        password = st.text_input(get_testo('dashboard_admin'), type="password")
        if st.button(get_testo('dashboard_connexion')):
            if password == PASSWORD_DASHBOARD:
                st.session_state.admin_logged = True
                st.success(get_testo('dashboard_success'))
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    else:
        st.success(get_testo('dashboard_success'))
        
        if st.button(get_testo('dashboard_deconnexion')):
            st.session_state.admin_logged = False
            st.rerun()
        
        st.markdown("---")
        st.subheader(get_testo('dashboard_gestion'))
        
        try:
            response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data[1:], columns=data[0])
                
                st.write(f"{get_testo('dashboard_total')}: {len(df)}")
                
                lavoratore = st.selectbox(get_testo('dashboard_select'), df['Cognome'] + ' ' + df['Nome'])
                
                if lavoratore:
                    row = df[df['Cognome'] + ' ' + df['Nome'] == lavoratore].iloc[0]
                    idx = row.name
                    
                    st.text_input(get_testo('dashboard_code'), value=row.get('Codice', ''), disabled=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        tipo_paga = st.selectbox(get_testo('dashboard_tipo'), ["Horaire", "Journalier", "Mensuel", "Hebdomadaire"])
                    
                    with col2:
                        valore_paga = st.text_input(get_testo('dashboard_montant'), value="")
                    
                    if st.button(get_testo('dashboard_save')):
                        df.loc[idx, 'Tipo_Paga'] = tipo_paga
                        df.loc[idx, 'Valore_Paga'] = valore_paga
                        
                        dati_json = {"action": "update", "data": df.to_dict(orient='records')}
                        resp = requests.post(GOOGLE_SCRIPT_URL_ASSUNZIONI, json=dati_json)
                        
                        if resp.status_code == 200:
                            st.success(get_testo('dashboard_saved'))
                        else:
                            st.error(get_testo('dashboard_error'))
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image(LOGO_URL, use_column_width=True)
    st.markdown("---")
    
    lingua_attuale = st.session_state.lingua
    index_lingua = 0 if lingua_attuale == 'fr' else (1 if lingua_attuale == 'it' else 2)
    
    lingua_sel = st.selectbox(
        "Langue", 
        ["Français", "Italiano", "English"],
        index=index_lingua,
        key="sel_lingua"
    )
    
    nuova_lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
    
    if nuova_lingua != lingua_attuale:
        st.session_state.lingua = nuova_lingua
        st.rerun()
    
    st.markdown("---")
    
    if st.button(get_testo('candidature'), use_container_width=True):
        st.session_state.pagina = 'candidatura'
        st.rerun()
    
    if st.button(get_testo('espace_travailleur'), use_container_width=True):
        st.session_state.pagina = 'espace_travailleur'
        st.rerun()
    
    if st.button(get_testo('dashboard'), use_container_width=True):
        st.session_state.pagina = 'dashboard'
        st.rerun()

# ============================================================================
# ROUTING
# ============================================================================

if st.session_state.pagina == 'home':
    pagina_home()
elif st.session_state.pagina == 'candidatura':
    pagina_candidatura()
elif st.session_state.pagina == 'espace_travailleur':
    pagina_espace_travailleur()
elif st.session_state.pagina == 'login_lavoratore':
    pagina_login_lavoratore()
elif st.session_state.pagina == 'area_lavoratore':
    pagina_area_lavoratore()
elif st.session_state.pagina == 'trasmissione_dati_giornalieri':
    pagina_trasmissione_dati_giornalieri()
elif st.session_state.pagina == 'dashboard':
    pagina_dashboard()
elif st.session_state.pagina == 'registrazione':
    pagina_registrazione_multi_step(st.session_state.lingua)
