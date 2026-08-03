# -*- coding: utf-8 -*-
"""
PROACIER - Gestione Risorse Umane (HRM)
Versione COMPLETA con tutti gli step
"""
import streamlit as st
import requests
from datetime import datetime
import random
from fpdf import FPDF
import pandas as pd

# CONFIGURAZIONE
st.set_page_config(page_title="Proacier - RH", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

LOGO_URL = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png"
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbxt39icOxVevvtes1ne1tK2ZTrw-uXldRIppSDgJj8YPwb13hOMRN6tOT0KJjB9vYF6MQ/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycby1isMOz1fKTptR83six7_3OMaDgcx8_LRn3rLkD9_wCRHdxu1GCgQr3aR9FxaSr3Q-/exec"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")
URL_CONDIZIONI = "https://www.proacier.sn/condizioni"

# TRADUZIONI COMPLETE
TRADUZIONI = {
    'fr': {
        'titolo': ' PROACIER - GESTION DES RESSOURCES HUMAINES',
        'sottotitolo': 'Système de Recrutement - Sénégal',
        'lingua': 'Langue',
        'nuova_assunzione': '📝 Nouvelle Embauche (Complet)',
        'candidatura_spontanea': '📄 Candidature Spontanée',
        'dashboard': 'Tableau de Bord',
        'area_lavoratore': 'Espace Travailleur',
        'logout': 'Déconnexion',
        'benvenuto': 'Bienvenue',
        'step1': '1. IDENTITÉ & FAMILLE',
        'step2': '2. COORDONNÉES',
        'step3': '3. DOCUMENTS OFFICIELS',
        'step4': '4. EMPLOI & SALAIRE',
        'step5': '5. COMPÉTENCES & SANTÉ',
        'step6': '6. URGENCE & CONFIRMATION',
        'suivant': 'Suivant →',
        'precedent': '← Précédent',
        'generer_pdf': ' Générer PDF & Accepter',
        'enregistrement_reussi': 'Enregistrement réussi !',
        'conservez_identifiants': '⚠️ CONSERVEZ CES IDENTIFIANTS',
        'code_acces': 'Code d\'accès',
        'pin_acces': 'PIN d\'accès',
        'telecharger_pdf': 'Télécharger PDF',
        'retour': 'Retour',
        'cognome': 'Nom de famille *',
        'nome': 'Prénom(s) *',
        'data_nascita': 'Date de naissance',
        'giorno': 'Jour',
        'mese': 'Mois',
        'anno': 'Année',
        'luogo_nascita': 'Lieu de naissance *',
        'nazionalita': 'Nationalité *',
        'sesso': 'Sexe *',
        'maschile': 'Masculin',
        'femminile': 'Féminin',
        'stato_civile': 'État civil *',
        'celibe': 'Célibataire',
        'coniugato': 'Marié(e)',
        'divorziato': 'Divorcé(e)',
        'vedovo': 'Veuf(ve)',
        'numero_mogli': 'Nombre d\'épouses',
        'figli_totale': 'Nombre total d\'enfants',
        'residenza_moglie': 'Lieu de résidence de l\'épouse',
        'figli_moglie': 'Nombre d\'enfants avec cette épouse',
        'indirizzo': 'Adresse *',
        'quartiere': 'Quartier',
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
        'apte': 'Apte',
        'restriction': 'Apte avec restriction',
        'inapte': 'Inapte',
        'data_visita': 'Date visite médicale',
        'emergenza_nome': 'Nom contact urgence *',
        'emergenza_parentela': 'Lien de parenté *',
        'emergenza_tel': 'Téléphone urgence *',
        'emergenza_indirizzo': 'Adresse urgence',
        'certifico': 'Je certifie l\'exactitude des informations et accepte les conditions.',
        'leggi_condizioni': '📋 Lire les conditions complètes',
        'certifico_checkbox': 'Je certifie l\'exactitude des informations',
        'erreur_obbligatori': 'Veuillez remplir les champs obligatoires (*)',
        'obbligatorio': '*',
        'giornalieri_titolo': 'Déjà travailleur?',
        'giornalieri_desc': 'Accédez à votre espace personnel',
        'nuovo_giornaliero_titolo': 'Nouveau / Journalier?',
        'nuovo_giornaliero_desc': 'Transmettez vos données (pas un contrat)',
        'login_btn': 'Connexion à mon espace',
        'trasmissione_btn': 'Transmettre mes données',
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
        'cand_info': 'Ceci n\'est PAS un contrat, mais seulement l\'envoi de votre candidature.',
        'cand_invia': 'Envoyer ma candidature',
        'cand_successo': 'Candidature envoyée avec succès!',
        'cand_errore': 'Erreur lors de l\'envoi',
        'cat_edilizia': 'Bâtiment',
        'cat_contabilita': 'Comptabilité',
        'cat_meccanica': 'Mécanique',
        'cat_elettrico': 'Électricité',
        'cat_agricoltura': 'Agriculture',
        'cat_altro': 'Autre',
    },
    'it': {
        'titolo': '🏭 PROACIER - GESTIONE RISORSE UMANE',
        'sottotitolo': 'Sistema di Reclutamento - Senegal',
        'lingua': 'Lingua',
        'nuova_assunzione': '📝 Nuova Assunzione (Completo)',
        'candidatura_spontanea': '📄 Candidatura Spontanea',
        'dashboard': 'Dashboard',
        'area_lavoratore': 'Spazio Lavoratore',
        'logout': 'Logout',
        'benvenuto': 'Benvenuto',
        'step1': '1. IDENTITÀ & FAMIGLIA',
        'step2': '2. COORDINATE',
        'step3': '3. DOCUMENTI UFFICIALI',
        'step4': '4. IMPIEGO & SALARIO',
        'step5': '5. COMPETENZE & SALUTE',
        'step6': '6. EMERGENZA & CONFERMA',
        'suivant': 'Avanti →',
        'precedent': '← Indietro',
        'generer_pdf': '📄 Genera PDF & Accetta',
        'enregistrement_reussi': 'Registrazione riuscita!',
        'conservez_identifiants': '⚠️ CONSERVA QUESTI IDENTIFICATIVI',
        'code_acces': 'Codice accesso',
        'pin_acces': 'PIN accesso',
        'telecharger_pdf': 'Scarica PDF',
        'retour': 'Indietro',
        'cognome': 'Cognome *',
        'nome': 'Nome *',
        'data_nascita': 'Data di nascita',
        'giorno': 'Giorno',
        'mese': 'Mese',
        'anno': 'Anno',
        'luogo_nascita': 'Luogo di nascita *',
        'nazionalita': 'Nazionalità *',
        'sesso': 'Sesso *',
        'maschile': 'Maschile',
        'femminile': 'Femminile',
        'stato_civile': 'Stato civile *',
        'celibe': 'Celibe/Nubile',
        'coniugato': 'Coniugato/a',
        'divorziato': 'Divorziato/a',
        'vedovo': 'Vedovo/a',
        'numero_mogli': 'Numero mogli',
        'figli_totale': 'Numero totale figli',
        'residenza_moglie': 'Luogo residenza moglie',
        'figli_moglie': 'Figli con questa moglie',
        'indirizzo': 'Indirizzo *',
        'quartiere': 'Quartiere',
        'comune': 'Comune *',
        'dipartimento': 'Dipartimento / Regione *',
        'telefono_1': 'Telefono 1 *',
        'telefono_2': 'Telefono 2',
        'telefono_3': 'Telefono 3',
        'cni': 'CNI (Carta Identità) *',
        'nif': 'NIF',
        'css': 'CSS (Sicurezza Sociale)',
        'cmu': 'CMU',
        'ipres': 'IPRES',
        'mansione_1': 'Mansione / Funzione *',
        'luogo_lavoro': 'Luogo lavoro *',
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
        'patente': 'Patente guida',
        'gruppo_sanguigno': 'Gruppo sanguigno',
        'rh': 'Rh',
        'allergie': 'Allergie',
        'malattie': 'Malattie croniche',
        'idoneita': 'Idoneità medica',
        'apte': 'Apto',
        'restriction': 'Apto con restrizioni',
        'inapte': 'Inapto',
        'data_visita': 'Data visita medica',
        'emergenza_nome': 'Nome contatto emergenza *',
        'emergenza_parentela': 'Parentela *',
        'emergenza_tel': 'Telefono emergenza *',
        'emergenza_indirizzo': 'Indirizzo emergenza',
        'certifico': 'Certifico l\'esattezza delle informazioni e accetto le condizioni.',
        'leggi_condizioni': '📋 Leggi condizioni complete',
        'certifico_checkbox': 'Certifico l\'esattezza delle informazioni',
        'erreur_obbligatori': 'Compila campi obbligatori (*)',
        'obbligatorio': '*',
        'giornalieri_titolo': 'Già lavoratore?',
        'giornalieri_desc': 'Accedi al tuo spazio',
        'nuovo_giornaliero_titolo': 'Nuovo / Giornaliero?',
        'nuovo_giornaliero_desc': 'Trasmetti dati (non contratto)',
        'login_btn': 'Accedi al mio spazio',
        'trasmissione_btn': 'Trasmetti i miei dati',
        'connexion_mon_espace': 'Accedi al mio spazio',
        'code_access_input': 'Codice accesso',
        'pin_input': 'PIN personale',
        'se_connecter': 'Accedi',
        'mes_donnees_titolo': 'I Miei Dati',
        'donnees_non_modifiables': 'Dati Personali (non modificabili)',
        'donnees_modifiables': 'Dati Modificabili',
        'mettre_a_jour': 'Aggiorna',
        'salaire_titolo': 'Informazioni Salariali',
        'salaire_desc': 'Salario gestito da amministrazione',
        'cand_info': 'NON è un contratto, solo candidatura.',
        'cand_invia': 'Invia candidatura',
        'cand_successo': 'Candidatura inviata!',
        'cand_errore': 'Errore invio',
        'cat_edilizia': 'Edilizia',
        'cat_contabilita': 'Contabilità',
        'cat_meccanica': 'Meccanica',
        'cat_elettrico': 'Elettrico',
        'cat_agricoltura': 'Agricoltura',
        'cat_altro': 'Altro',
    },
    'en': {
        'titolo': '🏭 PROACIER - HUMAN RESOURCES',
        'sottotitolo': 'Recruitment System - Senegal',
        'lingua': 'Language',
        'nuova_assunzione': '📝 New Hiring (Complete)',
        'candidatura_spontanea': ' Spontaneous Application',
        'dashboard': 'Dashboard',
        'area_lavoratore': 'Worker Space',
        'logout': 'Logout',
        'benvenuto': 'Welcome',
        'step1': '1. IDENTITY & FAMILY',
        'step2': '2. CONTACT INFO',
        'step3': '3. OFFICIAL DOCUMENTS',
        'step4': '4. EMPLOYMENT & SALARY',
        'step5': '5. SKILLS & HEALTH',
        'step6': '6. EMERGENCY & CONFIRMATION',
        'suivant': 'Next →',
        'precedent': '← Back',
        'generer_pdf': '📄 Generate PDF & Accept',
        'enregistrement_reussi': 'Registration successful!',
        'conservez_identifiants': '️ SAVE THESE CREDENTIALS',
        'code_acces': 'Access code',
        'pin_acces': 'PIN access',
        'telecharger_pdf': 'Download PDF',
        'retour': 'Back',
        'cognome': 'Surname *',
        'nome': 'First name *',
        'data_nascita': 'Date of birth',
        'giorno': 'Day',
        'mese': 'Month',
        'anno': 'Year',
        'luogo_nascita': 'Place of birth *',
        'nazionalita': 'Nationality *',
        'sesso': 'Gender *',
        'maschile': 'Male',
        'femminile': 'Female',
        'stato_civile': 'Marital status *',
        'celibe': 'Single',
        'coniugato': 'Married',
        'divorziato': 'Divorced',
        'vedovo': 'Widowed',
        'numero_mogli': 'Number of wives',
        'figli_totale': 'Total children',
        'residenza_moglie': 'Wife residence',
        'figli_moglie': 'Children with this wife',
        'indirizzo': 'Address *',
        'quartiere': 'Neighborhood',
        'comune': 'Municipality *',
        'dipartimento': 'Department / Region *',
        'telefono_1': 'Phone 1 *',
        'telefono_2': 'Phone 2',
        'telefono_3': 'Phone 3',
        'cni': 'National ID Card *',
        'nif': 'NIF',
        'css': 'Social Security',
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
        'patente': 'Driver\'s license',
        'gruppo_sanguigno': 'Blood type',
        'rh': 'Rh',
        'allergie': 'Allergies',
        'malattie': 'Chronic diseases',
        'idoneita': 'Medical fitness',
        'apte': 'Fit',
        'restriction': 'Fit with restrictions',
        'inapte': 'Unfit',
        'data_visita': 'Medical visit date',
        'emergenza_nome': 'Emergency contact name *',
        'emergenza_parentela': 'Relationship *',
        'emergenza_tel': 'Emergency phone *',
        'emergenza_indirizzo': 'Emergency address',
        'certifico': 'I certify accuracy and accept conditions.',
        'leggi_condizioni': '📋 Read full conditions',
        'certifico_checkbox': 'I certify accuracy',
        'erreur_obbligatori': 'Please fill required fields (*)',
        'obbligatorio': '*',
        'giornalieri_titolo': 'Already a worker?',
        'giornalieri_desc': 'Access your space',
        'nuovo_giornaliero_titolo': 'New / Daily worker?',
        'nuovo_giornaliero_desc': 'Submit data (not contract)',
        'login_btn': 'Login to my space',
        'trasmissione_btn': 'Submit my data',
        'connexion_mon_espace': 'Login to my space',
        'code_access_input': 'Access code',
        'pin_input': 'Personal PIN',
        'se_connecter': 'Login',
        'mes_donnees_titolo': 'My Data',
        'donnees_non_modifiables': 'Personal Data (non-modifiable)',
        'donnees_modifiables': 'Modifiable Data',
        'mettre_a_jour': 'Update',
        'salaire_titolo': 'Salary Information',
        'salaire_desc': 'Salary managed by administration',
        'cand_info': 'NOT a contract, only application.',
        'cand_invia': 'Send application',
        'cand_successo': 'Application sent!',
        'cand_errore': 'Error sending',
        'cat_edilizia': 'Construction',
        'cat_contabilita': 'Accounting',
        'cat_meccanica': 'Mechanics',
        'cat_elettrico': 'Electrical',
        'cat_agricoltura': 'Agriculture',
        'cat_altro': 'Other',
    }
}

def get_testo(chiave):
    lingua = st.session_state.get('lingua', 'fr')
    return TRADUZIONI.get(lingua, TRADUZIONI['fr']).get(chiave, chiave)

# SESSION STATE
if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'lingua' not in st.session_state: st.session_state.lingua = 'fr'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'codice_operatore' not in st.session_state: st.session_state.codice_operatore = None
if 'pin_operatore' not in st.session_state: st.session_state.pin_operatore = None
if 'step' not in st.session_state: st.session_state.step = 1
if 'dati_form' not in st.session_state: st.session_state.dati_form = {}
if 'admin_logged' not in st.session_state: st.session_state.admin_logged = False

def genera_codice(): return f"THS-{datetime.now().year}-{random.randint(1000, 9999)}"
def genera_pin(): return str(random.randint(1000, 9999))

def salva_su_google_sheets(script_url, dati, action="append"):
    try:
        response = requests.post(script_url, json={"action": action, "row": dati}, headers={"Content-Type": "application/json"}, timeout=30)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Errore: {str(e)}")
        return False

# PDF
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
    pdf.multi_cell(0, 4, "Je certifie l'exactitude des informations et accepte les conditions.")
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
    pdf.cell(0, 8, 'IDENTIFIANTS - CONSERVEZ CE DOCUMENT', 0, 1, 'C', True)
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
    if isinstance(pdf_bytes, str): pdf_bytes = pdf_bytes.encode('latin-1', errors='ignore')
    return bytes(pdf_bytes)

# STEP 1: IDENTITÀ & FAMIGLIA
def step_1():
    st.subheader(get_testo('step1'))
    col1, col2 = st.columns(2)
    with col1:
        cognome = st.text_input(get_testo('cognome'), value=st.session_state.dati_form.get('cognome', ''), key='s1_cognome')
        nome = st.text_input(get_testo('nome'), value=st.session_state.dati_form.get('nome', ''), key='s1_nome')
        st.markdown(f"**{get_testo('data_nascita')}**")
        cg, cm, ca = st.columns(3)
        with cg: giorno = st.selectbox(get_testo('giorno'), range(1, 32), index=st.session_state.dati_form.get('giorno', 0), key='s1_g')
        with cm: mese = st.selectbox(get_testo('mese'), range(1, 13), index=st.session_state.dati_form.get('mese', 0), key='s1_m')
        with ca: anno = st.selectbox(get_testo('anno'), range(1950, 2010), index=st.session_state.dati_form.get('anno', 30), key='s1_a')
        data_nascita_str = f"{giorno:02d}/{mese:02d}/{anno}"
        luogo_nascita = st.text_input(get_testo('luogo_nascita'), value=st.session_state.dati_form.get('luogo_nascita', ''), key='s1_luogo')
        nazionalita = st.text_input(get_testo('nazionalita'), value=st.session_state.dati_form.get('nazionalita', 'Sénégalaise'), key='s1_naz')
    with col2:
        sesso = st.selectbox(get_testo('sesso'), [get_testo('maschile'), get_testo('femminile')], index=0 if st.session_state.dati_form.get('sesso') != get_testo('femminile') else 1, key='s1_sesso')
        stato_civile = st.selectbox(get_testo('stato_civile'), [get_testo('celibe'), get_testo('coniugato'), get_testo('divorziato'), get_testo('vedovo')], index=0 if st.session_state.dati_form.get('stato_civile') == get_testo('celibe') else 1, key='s1_stato')
        numero_mogli, dettagli_mogli = 0, ""
        if stato_civile == get_testo('coniugato'):
            numero_mogli = st.number_input(get_testo('numero_mogli'), min_value=1, max_value=4, value=st.session_state.dati_form.get('numero_mogli', 1), key='s1_mogli')
            dettagli = []
            for i in range(1, numero_mogli + 1):
                st.markdown(f"**Épouse {i}**")
                c_res, c_fig = st.columns(2)
                with c_res: res = st.text_input(f"{get_testo('residenza_moglie')} {i}", value=st.session_state.dati_form.get(f'res_moglie_{i}', ''), key=f's1_res_{i}')
                with c_fig: fig = st.number_input(f"{get_testo('figli_moglie')} {i}", min_value=0, value=st.session_state.dati_form.get(f'figli_moglie_{i}', 0), key=f's1_fig_{i}')
                dettagli.append(f"Épouse {i}: {res} ({fig} enfants)")
            dettagli_mogli = " | ".join(dettagli)
        figli_totale = st.number_input(get_testo('figli_totale'), min_value=0, value=st.session_state.dati_form.get('figli_totale', 0), key='s1_figli_tot')
    st.session_state.dati_form.update({'cognome': cognome, 'nome': nome, 'data_nascita': data_nascita_str, 'luogo_nascita': luogo_nascita,
        'nazionalita': nazionalita, 'sesso': sesso, 'stato_civile': stato_civile, 'numero_mogli': numero_mogli,
        'dettagli_mogli': dettagli_mogli, 'figli_totale': figli_totale, 'giorno': giorno, 'mese': mese, 'anno': anno})

# STEP 2: COORDINATE
def step_2():
    st.subheader(get_testo('step2'))
    col1, col2 = st.columns(2)
    with col1:
        indirizzo = st.text_input(get_testo('indirizzo'), value=st.session_state.dati_form.get('indirizzo', ''), key='s2_ind')
        quartiere = st.text_input(get_testo('quartiere'), value=st.session_state.dati_form.get('quartiere', ''), key='s2_quart')
        comune = st.text_input(get_testo('comune'), value=st.session_state.dati_form.get('comune', ''), key='s2_com')
    with col2:
        regione_senegal = st.text_input(get_testo('dipartimento'), value=st.session_state.dati_form.get('regione_senegal', ''), key='s2_reg')
        telefono_1 = st.text_input(get_testo('telefono_1'), value=st.session_state.dati_form.get('telefono_1', ''), key='s2_tel1')
        telefono_2 = st.text_input(get_testo('telefono_2'), value=st.session_state.dati_form.get('telefono_2', ''), key='s2_tel2')
        telefono_3 = st.text_input(get_testo('telefono_3'), value=st.session_state.dati_form.get('telefono_3', ''), key='s2_tel3')
    st.session_state.dati_form.update({'indirizzo': indirizzo, 'quartiere': quartiere, 'comune': comune,
        'regione_senegal': regione_senegal, 'telefono_1': telefono_1, 'telefono_2': telefono_2, 'telefono_3': telefono_3})

# STEP 3: DOCUMENTI
def step_3():
    st.subheader(get_testo('step3'))
    col1, col2 = st.columns(2)
    with col1:
        cni = st.text_input(get_testo('cni'), value=st.session_state.dati_form.get('cni', ''), key='s3_cni')
        nif = st.text_input(get_testo('nif'), value=st.session_state.dati_form.get('nif', ''), key='s3_nif')
        css = st.text_input(get_testo('css'), value=st.session_state.dati_form.get('css', ''), key='s3_css')
    with col2:
        cmu = st.text_input(get_testo('cmu'), value=st.session_state.dati_form.get('cmu', ''), key='s3_cmu')
        ipres = st.text_input(get_testo('ipres'), value=st.session_state.dati_form.get('ipres', ''), key='s3_ipres')
    st.session_state.dati_form.update({'cni': cni, 'nif': nif, 'css': css, 'cmu': cmu, 'ipres': ipres})

# STEP 4: IMPIEGO & SALARIO
def step_4():
    st.subheader(get_testo('step4'))
    col1, col2 = st.columns(2)
    with col1:
        mansione_1 = st.text_input(get_testo('mansione_1'), value=st.session_state.dati_form.get('mansione_1', ''), key='s4_man')
        luogo_lavoro = st.text_input(get_testo('luogo_lavoro'), value=st.session_state.dati_form.get('luogo_lavoro', ''), key='s4_luogo')
        reparto = st.text_input(get_testo('reparto'), value=st.session_state.dati_form.get('reparto', ''), key='s4_rep')
        supervisore = st.text_input(get_testo('supervisore'), value=st.session_state.dati_form.get('supervisore', ''), key='s4_sup')
    with col2:
        data_inizio_1 = st.text_input(get_testo('data_inizio_1'), value=st.session_state.dati_form.get('data_inizio_1', ''), key='s4_data')
        salario = st.text_input(get_testo('salario'), value=st.session_state.dati_form.get('salario', ''), key='s4_sal')
        ore_giorno = st.number_input(get_testo('ore_giorno'), min_value=0, max_value=24, value=st.session_state.dati_form.get('ore_giorno', 8), key='s4_ore')
        giorni_settimana = st.number_input(get_testo('giorni_settimana'), min_value=0, max_value=7, value=st.session_state.dati_form.get('giorni_settimana', 6), key='s4_giorni')
        pagamento = st.selectbox(get_testo('pagamento'), ["Horaire", "Journalier", "Mensuel", "Hebdomadaire"], key='s4_pag')
        wave_orange = st.text_input(get_testo('wave_orange'), value=st.session_state.dati_form.get('wave_orange', ''), key='s4_wave')
    st.session_state.dati_form.update({'mansione_1': mansione_1, 'luogo_lavoro': luogo_lavoro, 'reparto': reparto,
        'supervisore': supervisore, 'data_inizio_1': data_inizio_1, 'salario': salario, 'ore_giorno': ore_giorno,
        'giorni_settimana': giorni_settimana, 'pagamento': pagamento, 'wave_orange': wave_orange})

# STEP 5: COMPETENZE & SALUTE
def step_5():
    st.subheader(get_testo('step5'))
    col1, col2 = st.columns(2)
    with col1:
        categoria_competenza = st.selectbox(get_testo('categoria_competenza'), [get_testo('cat_edilizia'), get_testo('cat_contabilita'),
            get_testo('cat_meccanica'), get_testo('cat_elettrico'), get_testo('cat_agricoltura'), get_testo('cat_altro')], key='s5_cat')
        dettaglio_competenza = st.text_input(get_testo('dettaglio_competenza'), value=st.session_state.dati_form.get('dettaglio_competenza', ''), key='s5_det')
        patente = st.text_input(get_testo('patente'), value=st.session_state.dati_form.get('patente', ''), key='s5_pat')
    with col2:
        gruppo_sanguigno = st.selectbox(get_testo('gruppo_sanguigno'), ["A", "B", "AB", "O"], key='s5_gruppo')
        rh = st.selectbox(get_testo('rh'), ["+", "-"], key='s5_rh')
        allergie = st.text_input(get_testo('allergie'), value=st.session_state.dati_form.get('allergie', ''), key='s5_all')
        malattie = st.text_input(get_testo('malattie'), value=st.session_state.dati_form.get('malattie', ''), key='s5_mal')
        idoneita = st.selectbox(get_testo('idoneita'), [get_testo('apte'), get_testo('restriction'), get_testo('inapte')], key='s5_ido')
        data_visita = st.text_input(get_testo('data_visita'), value=st.session_state.dati_form.get('data_visita', ''), key='s5_data_visita')
    st.session_state.dati_form.update({'categoria_competenza': categoria_competenza, 'dettaglio_competenza': dettaglio_competenza,
        'patente': patente, 'gruppo_sanguigno': gruppo_sanguigno, 'rh': rh, 'allergie': allergie, 'malattie': malattie,
        'idoneita': idoneita, 'data_visita': data_visita})

# STEP 6: EMERGENZA & CONFERMA
def step_6():
    st.subheader(get_testo('step6'))
    col1, col2 = st.columns(2)
    with col1:
        emergenza_nome = st.text_input(get_testo('emergenza_nome'), value=st.session_state.dati_form.get('emergenza_nome', ''), key='s6_em_nome')
        emergenza_parentela = st.text_input(get_testo('emergenza_parentela'), value=st.session_state.dati_form.get('emergenza_parentela', ''), key='s6_em_par')
    with col2:
        emergenza_tel = st.text_input(get_testo('emergenza_tel'), value=st.session_state.dati_form.get('emergenza_tel', ''), key='s6_em_tel')
        emergenza_indirizzo = st.text_input(get_testo('emergenza_indirizzo'), value=st.session_state.dati_form.get('emergenza_indirizzo', ''), key='s6_em_ind')
    st.markdown("---")
    st.info(get_testo('certifico'))
    st.markdown(f"[{get_testo('leggi_condizioni')}]({URL_CONDIZIONI})")
    certifica = st.checkbox(get_testo('certifico_checkbox'), value=st.session_state.dati_form.get('certifica', False), key='s6_conf')
    st.session_state.dati_form.update({'emergenza_nome': emergenza_nome, 'emergenza_parentela': emergenza_parentela,
        'emergenza_tel': emergenza_tel, 'emergenza_indirizzo': emergenza_indirizzo, 'certifica': certifica})

# PAGINA REGISTRAZIONE MULTI-STEP
def pagina_registrazione_multi_step():
    step = st.session_state.step
    st.progress(step / 6)
    st.write(f"**Step {step} / 6**")
    st.markdown("---")
    
    if step == 1: step_1()
    elif step == 2: step_2()
    elif step == 3: step_3()
    elif step == 4: step_4()
    elif step == 5: step_5()
    elif step == 6: step_6()
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if step > 1 and st.button(get_testo('precedent'), use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with col2:
        if step < 6:
            if st.button(get_testo('suivant'), type="primary", use_container_width=True):
                if step == 1 and (not st.session_state.dati_form.get('cognome') or not st.session_state.dati_form.get('nome')):
                    st.error(get_testo('erreur_obbligatori')); return
                if step == 2 and (not st.session_state.dati_form.get('indirizzo') or not st.session_state.dati_form.get('comune')):
                    st.error(get_testo('erreur_obbligatori')); return
                st.session_state.step += 1
                st.rerun()
        else:
            if st.session_state.dati_form.get('certifica'):
                if st.button(get_testo('generer_pdf'), type="primary", use_container_width=True):
                    codice = genera_codice(); pin = genera_pin()
                    dati_finali = {"id": codice, "codice": codice, "pin": pin,
                        "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        **st.session_state.dati_form, "tipo": "Assunzione"}
                    if salva_su_google_sheets(GOOGLE_SCRIPT_URL_ASSUNZIONI, dati_finali, action="append"):
                        st.success(get_testo('enregistrement_reussi'))
                        pdf_bytes = genera_pdf_lavoratore(dati_finali)
                        st.warning(get_testo('conservez_identifiants'))
                        c1, c2 = st.columns(2)
                        with c1: st.info(f"**{get_testo('code_acces')}:** {codice}")
                        with c2: st.info(f"**{get_testo('pin_acces')}:** {pin}")
                        st.download_button(label=f"📥 {get_testo('telecharger_pdf')}", data=pdf_bytes,
                            file_name=f"Fiche_{st.session_state.dati_form.get('cognome', '')}.pdf", mime="application/pdf")
                        st.ballo()
                        st.session_state.dati_form = {}; st.session_state.step = 1
                        st.rerun()
                    else: st.error("Erreur enregistrement")
            else: st.warning("Veuillez cocher la case")

# ALTRE PAGINE (candidatura, espace travailleur, dashboard, ecc.) - le mantengo brevi per spazio
def pagina_candidatura():
    st.title(get_testo('candidatura_spontanea'))
    st.info(get_testo('cand_info'))
    with st.form("form_candidatura"):
        col1, col2 = st.columns(2)
        with col1:
            cognome = st.text_input(get_testo('cognome'), key='c_cognome')
            nome = st.text_input(get_testo('nome'), key='c_nome')
            telefono = st.text_input(get_testo('telefono_1'), key='c_tel')
        with col2:
            indirizzo = st.text_input(get_testo('indirizzo'), key='c_ind')
            comune = st.text_input(get_testo('comune'), key='c_com')
            mansione = st.text_input("Poste souhaité", key='c_man')
        submitted = st.form_submit_button(get_testo('cand_invia'), type="primary")
        if submitted:
            if cognome and nome and telefono:
                dati = {"id": f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}",
                    "cognome": cognome, "nome": nome, "telefono": telefono,
                    "indirizzo": indirizzo, "comune": comune, "mansione_richiesta": mansione}
                if salva_su_google_sheets(GOOGLE_SCRIPT_URL_CANDIDATURE, dati):
                    st.success(get_testo('cand_successo')); st.ballo()
            else: st.error("Champs obligatoires")

def pagina_espace_travailleur():
    st.title(get_testo('area_lavoratore'))
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 👤 {get_testo('giornalieri_titolo')}")
        st.info(get_testo('giornalieri_desc'))
        if st.button(get_testo('login_btn'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'login_lavoratore'; st.rerun()
    with col2:
        st.markdown(f"### 📝 {get_testo('nuovo_giornaliero_titolo')}")
        st.info(get_testo('nuovo_giornaliero_desc'))
        if st.button(get_testo('trasmissione_btn'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'trasmissione_dati'; st.rerun()

def pagina_login_lavoratore():
    st.title(get_testo('connexion_mon_espace'))
    with st.form("login_form"):
        codice = st.text_input(get_testo('code_access_input'))
        pin = st.text_input(get_testo('pin_input'), type="password")
        submitted = st.form_submit_button(get_testo('se_connecter'), type="primary")
        if submitted and codice and pin:
            st.session_state.logged_in = True; st.session_state.user_type = 'lavoratore'
            st.session_state.codice_operatore = codice; st.session_state.pin_operatore = pin
            st.session_state.pagina = 'area_lavoratore'; st.success("Connecté!"); st.rerun()
    if st.button(get_testo('retour')): st.session_state.pagina = 'espace_travailleur'; st.rerun()

def pagina_area_lavoratore():
    if not st.session_state.get('logged_in'): st.error("Accès refusé"); return
    st.title(get_testo('mes_donnees_titolo'))
    st.success(f"Code: {st.session_state.codice_operatore}")
    st.markdown("---")
    st.subheader(get_testo('donnees_non_modifiables'))
    st.write("CNI, Données personnelles: Contactez l'administration pour modifications")
    st.markdown("---")
    st.subheader(get_testo('donnees_modifiables'))
    st.info("Téléphone, Adresse, Enfants - Modifiables ici")
    if st.button(get_testo('logout')):
        st.session_state.logged_in = False; st.session_state.pagina = 'home'; st.rerun()

def pagina_dashboard():
    st.title(get_testo('dashboard'))
    if not st.session_state.get('admin_logged'):
        pwd = st.text_input("Password", type="password")
        if st.button("Connexion"):
            if pwd == PASSWORD_DASHBOARD:
                st.session_state.admin_logged = True; st.success("Connecté admin"); st.rerun()
    else:
        st.success("Administrateur")
        if st.button("Déconnexion"): st.session_state.admin_logged = False; st.rerun()
        st.markdown("---")
        st.write("Gestion salaires individuels - Sélectionner travailleur")

# SIDEBAR
with st.sidebar:
    st.image(LOGO_URL, use_column_width=True)
    st.markdown("---")
    st.title(get_testo('titolo'))
    st.markdown(get_testo('sottotitolo'))
    st.markdown("---")
    lingua_sel = st.selectbox("Langue", ["Français", "Italiano", "English"],
        index=0 if st.session_state.lingua == 'fr' else (1 if st.session_state.lingua == 'it' else 2), key="sel_lingua")
    st.session_state.lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
    st.markdown("---")
    if st.button(get_testo('nuova_assunzione'), use_container_width=True):
        st.session_state.pagina = 'registrazione'; st.session_state.step = 1; st.session_state.dati_form = {}; st.rerun()
    if st.button(get_testo('candidatura_spontanea'), use_container_width=True):
        st.session_state.pagina = 'candidatura'; st.rerun()
    if st.button(get_testo('area_lavoratore'), use_container_width=True):
        st.session_state.pagina = 'espace_travailleur'; st.rerun()
    if st.button(get_testo('dashboard'), use_container_width=True):
        st.session_state.pagina = 'dashboard'; st.rerun()

# ROUTING
if st.session_state.pagina == 'home':
    st.title("🏭 PROACIER SN"); st.markdown("### Système de Gestion RH"); st.info("Utilisez le menu à gauche")
elif st.session_state.pagina == 'registrazione':
    pagina_registrazione_multi_step()
elif st.session_state.pagina == 'candidatura':
    pagina_candidatura()
elif st.session_state.pagina == 'espace_travailleur':
    pagina_espace_travailleur()
elif st.session_state.pagina == 'login_lavoratore':
    pagina_login_lavoratore()
elif st.session_state.pagina == 'area_lavoratore':
    pagina_area_lavoratore()
elif st.session_state.pagina == 'dashboard':
    pagina_dashboard()
