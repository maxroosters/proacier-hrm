import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import random
import base64
from io import BytesIO
from fpdf import FPDF

# ============================================================================
# CONFIGURAZIONE PAGINA E STILE
# ============================================================================

st.set_page_config(
    page_title="Proacier - RH",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per sidebar verde PROACIER
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
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# URL E CONFIGURAZIONI
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
        'benvenuto': 'Bienvenue',
        'candidature': 'Candidature Spontanée',
        'espace_travailleur': 'Espace Travailleur',
        'dashboard': 'Tableau de Bord',
        'logout': 'Déconnexion',
        'nuova_assunzione': 'Nouvelle Embauche (Complet)',
        'candidatura_spontanea': 'Candidature Spontanée',
        'area_lavoratore': 'Espace Travailleur',
        'i_miei_dati': 'Mes Données',
        'accesso_negato': 'Accès refusé',
        'dati_mancanti': 'Données manquantes',
        'giornalieri_titolo': 'Déjà travailleur?',
        'giornalieri_desc': 'Accédez à votre espace personnel',
        'nuovo_giornaliero_titolo': 'Nouveau / Journalier?',
        'nuovo_giornaliero_desc': 'Transmettez vos données (pas un contrat)',
        'login_spazio_personale': 'Connexion à mon espace',
        'trasmissione_dati': 'Transmettre mes données',
        'step1_identite': '1. IDENTITÉ & FAMILLE',
        'step2_coord': '2. COORDONNÉES',
        'step3_documents': '3. DOCUMENTS OFFICIELS',
        'step4_emploi': '4. EMPLOI & SALAIRE',
        'step5_competences': '5. COMPÉTENCES & SANTÉ',
        'step6_urgence': '6. URGENCE & CONFIRMATION',
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
    },
    'it': {
        'titolo': 'PROACIER - GESTIONE RISORSE UMANE',
        'sottotitolo': 'Sistema di Reclutamento - Senegal',
        'lingua': 'Lingua',
        'benvenuto': 'Benvenuto',
        'candidature': 'Candidatura Spontanea',
        'espace_travailleur': 'Spazio Lavoratore',
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'nuova_assunzione': 'Nuova Assunzione (Completo)',
        'candidatura_spontanea': 'Candidatura Spontanea',
        'area_lavoratore': 'Spazio Lavoratore',
        'i_miei_dati': 'I Miei Dati',
        'accesso_negato': 'Accesso negato',
        'dati_mancanti': 'Dati mancanti',
        'giornalieri_titolo': 'Già lavoratore?',
        'giornalieri_desc': 'Accedi al tuo spazio personale',
        'nuovo_giornaliero_titolo': 'Nuovo / Giornaliero?',
        'nuovo_giornaliero_desc': 'Trasmetti i tuoi dati (non è un contratto)',
        'login_spazio_personale': 'Accedi al mio spazio',
        'trasmissione_dati': 'Trasmetti i miei dati',
        'step1_identite': '1. IDENTITÀ & FAMIGLIA',
        'step2_coord': '2. COORDINATE',
        'step3_documents': '3. DOCUMENTI UFFICIALI',
        'step4_emploi': '4. IMPIEGO & SALARIO',
        'step5_competences': '5. COMPETENZE & SALUTE',
        'step6_urgence': '6. EMERGENZA & CONFERMA',
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
    },
    'en': {
        'titolo': 'PROACIER - HUMAN RESOURCES',
        'sottotitolo': 'Recruitment System - Senegal',
        'lingua': 'Language',
        'benvenuto': 'Welcome',
        'candidature': 'Spontaneous Application',
        'espace_travailleur': 'Worker Space',
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'nuova_assunzione': 'New Hiring (Complete)',
        'candidatura_spontanea': 'Spontaneous Application',
        'area_lavoratore': 'Worker Space',
        'i_miei_dati': 'My Data',
        'accesso_negato': 'Access denied',
        'dati_mancanti': 'Missing data',
        'giornalieri_titolo': 'Already a worker?',
        'giornalieri_desc': 'Access your personal space',
        'nuovo_giornaliero_titolo': 'New / Daily worker?',
        'nuovo_giornaliero_desc': 'Submit your data (not a contract)',
        'login_spazio_personale': 'Login to my space',
        'trasmissione_dati': 'Submit my data',
        'step1_identite': '1. IDENTITY & FAMILY',
        'step2_coord': '2. CONTACT INFO',
        'step3_documents': '3. OFFICIAL DOCUMENTS',
        'step4_emploi': '4. EMPLOYMENT & SALARY',
        'step5_competences': '5. SKILLS & HEALTH',
        'step6_urgence': '6. EMERGENCY & CONFIRMATION',
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
    }
}

def get_testo(chiave, lingua='fr'):
    return TRADUZIONI.get(lingua, TRADUZIONI['fr']).get(chiave, chiave)

# ============================================================================
# INIZIALIZZAZIONE SESSION STATE
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

# ============================================================================
# FUNZIONI DI SUPPORTO
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
# CLASSE PDF
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
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 6, f"N° fiche: {dati.get('codice', '')}", 0, 0)
    pdf.cell(95, 6, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.ln(2)
    
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
# PAGINA HOME
# ============================================================================

def pagina_home():
    st.title(get_testo('titolo', st.session_state.lingua))
    st.subheader(get_testo('sottotitolo', st.session_state.lingua))
    
    st.markdown("---")
    st.subheader("🎯 A cosa serve questa applicazione?")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📋 Trasmissione Dati**
        - Per nuovi lavoratori e giornalieri
        - Invio dati per futura assunzione
        - Pagamento salariali
        
        **📨 Candidature Spontanee**
        - Invio candidatura libera
        - Valutazione da parte HR
        """)
    
    with col2:
        st.markdown("""
        **👤 Spazio Personale**
        - Accesso con codice e PIN
        - Visualizza e modifica dati
        - Contatto amministrazione
        
        **💰 Pagamento Giornalieri**
        - Gestione lavoratori giornalieri
        - Tracciamento presenze
        - Calcolo compensi
        """)
    
    st.markdown("---")
    st.subheader("Come usare l'applicazione")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(get_testo('candidature', st.session_state.lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'candidatura'
            st.rerun()
    
    with col2:
        if st.button(get_testo('espace_travailleur', st.session_state.lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'espace_travailleur'
            st.rerun()
    
    with col3:
        if st.button(get_testo('dashboard', st.session_state.lingua), use_container_width=True):
            st.session_state.pagina = 'dashboard'
            st.rerun()

# ============================================================================
# PAGINA ESPACE TRAVAILLEUR
# ============================================================================

def pagina_espace_travailleur():
    st.title(get_testo('espace_travailleur', st.session_state.lingua))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 " + get_testo('giornalieri_titolo', st.session_state.lingua))
        st.info(get_testo('giornalieri_desc', st.session_state.lingua))
        if st.button(get_testo('login_spazio_personale', st.session_state.lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'login_lavoratore'
            st.rerun()
    
    with col2:
        st.markdown("### 📝 " + get_testo('nuovo_giornaliero_titolo', st.session_state.lingua))
        st.info(get_testo('nuovo_giornaliero_desc', st.session_state.lingua))
        if st.button(get_testo('trasmissione_dati', st.session_state.lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'trasmissione_dati_giornalieri'
            st.rerun()

# ============================================================================
# PAGINA LOGIN LAVORATORE
# ============================================================================

def pagina_login_lavoratore():
    st.title("Connexion à mon espace")
    
    with st.form("login_form"):
        codice = st.text_input("Code d'accès")
        pin = st.text_input("PIN personnel", type="password")
        submitted = st.form_submit_button("Se connecter", type="primary")
        
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
    
    if st.button("Retour"):
        st.session_state.pagina = 'espace_travailleur'
        st.rerun()

# ============================================================================
# PAGINA AREA LAVORATORE
# ============================================================================

def pagina_area_lavoratore():
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'lavoratore':
        st.error(get_testo("accesso_negato", st.session_state.lingua))
        st.stop()
    
    codice_lavoratore = st.session_state.get('codice_operatore')
    pin_lavoratore = st.session_state.get('pin_operatore')
    
    st.title(get_testo("i_miei_dati", st.session_state.lingua))
    st.success(f"Bonjour - Code: {codice_lavoratore}")
    
    try:
        response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            
            mask = (df['Codice'] == codice_lavoratore) & (df['PIN'] == pin_lavoratore)
            
            if not mask.any():
                st.error("Travailleur non trouvé")
                st.stop()
            
            row = df[mask].iloc[0]
            idx = row.name
            
            st.markdown("---")
            st.subheader("📋 Données Personnelles (non modifiables)")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.text_input("Cognome", value=row.get('Cognome', ''), disabled=True)
                st.text_input("Nome", value=row.get('Nome', ''), disabled=True)
                st.text_input("Data Nascita", value=row.get('Data_Nascita', ''), disabled=True)
            
            with col2:
                st.text_input("CNI", value=row.get('CNI', ''), disabled=True)
                st.text_input("CSS", value=row.get('CSS', ''), disabled=True)
                st.text_input("IPRES", value=row.get('IPRES', ''), disabled=True)
            
            with col3:
                st.text_input("Codice Operatore", value=row.get('Codice', ''), disabled=True)
                st.text_input("Luogo Nascita", value=row.get('Luogo_Nascita', ''), disabled=True)
                st.text_input("Nazionalità", value=row.get('Nazionalita', ''), disabled=True)
            
            st.markdown("---")
            st.subheader("✏️ Données Modifiables")
            
            with st.form("modifica_dati_lavoratore"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    nuovo_telefono = st.text_input("Téléphone *", value=row.get('Telefono', ''))
                    nuovo_indirizzo = st.text_input("Adresse *", value=row.get('Indirizzo', ''))
                    nuovo_quartiere = st.text_input("Quartier", value=row.get('Quartiere', ''))
                    nuovi_figli = st.number_input("Nombre d'enfants", min_value=0, value=int(row.get('Figli', 0) if pd.notna(row.get('Figli')) else 0))
                
                with col2:
                    nuovo_telefono2 = st.text_input("Téléphone 2", value=row.get('Telefono2', ''))
                    nuovo_comune = st.text_input("Commune", value=row.get('Comune', ''))
                    nuovo_dipartimento = st.text_input("Département/Région", value=row.get('Dipartimento', ''))
                    nuovo_stato_civile = st.selectbox("État Civil", ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"], 
                                                       index=0 if row.get('Stato_Civile') == "Célibataire" else 1)
                
                with col3:
                    nuova_mansione = st.text_input("Poste", value=row.get('Mansione', ''))
                    nuovo_reparto = st.text_input("Département", value=row.get('Reparto', ''))
                    nuovo_supervisore = st.text_input("Superviseur", value=row.get('Supervisore', ''))
                    nuovo_luogo_lavoro = st.text_input("Lieu de travail", value=row.get('Luogo_Lavoro', ''))
                
                st.markdown("---")
                st.subheader(" Informations Salariales")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nuovo_salario = st.text_input("Salaire (FCFA)", value=str(row.get('Salario', '')))
                    nuova_data_inizio = st.text_input("Date de début", value=row.get('Data_Inizio', ''))
                
                with col2:
                    tipo_paga = row.get('Tipo_Paga', '')
                    valore_paga = row.get('Valore_Paga', '')
                    st.text_input("Type de paiement", value=tipo_paga, disabled=True)
                    st.text_input("Montant", value=valore_paga, disabled=True)
                    st.info("Pour modifier le salaire, contactez l'administration")
                
                st.markdown("---")
                st.subheader("🚨 Contact d'Urgence")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    emergenza_nome = st.text_input("Nom Contact Urgence", value=row.get('Emergenza_Nome', ''))
                    emergenza_parentela = st.text_input("Relation", value=row.get('Emergenza_Parentela', ''))
                
                with col2:
                    emergenza_tel = st.text_input("Téléphone Urgence", value=row.get('Emergenza_Tel', ''))
                    emergenza_indirizzo = st.text_input("Adresse Urgence", value=row.get('Emergenza_Indirizzo', ''))
                
                submitted = st.form_submit_button("💾 Mettre à jour", type="primary")
                
                if submitted:
                    if not nuovo_telefono or not nuovo_indirizzo:
                        st.error("Téléphone et Adresse sont obligatoires!")
                        st.stop()
                    
                    try:
                        df.loc[idx, 'Telefono'] = nuovo_telefono
                        df.loc[idx, 'Telefono2'] = nuovo_telefono2
                        df.loc[idx, 'Indirizzo'] = nuovo_indirizzo
                        df.loc[idx, 'Quartiere'] = nuovo_quartiere
                        df.loc[idx, 'Comune'] = nuovo_comune
                        df.loc[idx, 'Dipartimento'] = nuovo_dipartimento
                        df.loc[idx, 'Figli'] = nuovi_figli
                        df.loc[idx, 'Stato_Civile'] = nuovo_stato_civile
                        df.loc[idx, 'Mansione'] = nuova_mansione
                        df.loc[idx, 'Reparto'] = nuovo_reparto
                        df.loc[idx, 'Supervisore'] = nuovo_supervisore
                        df.loc[idx, 'Luogo_Lavoro'] = nuovo_luogo_lavoro
                        df.loc[idx, 'Salario'] = nuovo_salario
                        df.loc[idx, 'Data_Inizio'] = nuova_data_inizio
                        df.loc[idx, 'Emergenza_Nome'] = emergenza_nome
                        df.loc[idx, 'Emergenza_Parentela'] = emergenza_parentela
                        df.loc[idx, 'Emergenza_Tel'] = emergenza_tel
                        df.loc[idx, 'Emergenza_Indirizzo'] = emergenza_indirizzo
                        
                        dati_json = {"action": "update", "data": df.to_dict(orient='records')}
                        resp = requests.post(GOOGLE_SCRIPT_URL_ASSUNZIONI, json=dati_json)
                        
                        if resp.status_code == 200:
                            st.success("✅ Données mises à jour avec succès!")
                            st.ballo()
                        else:
                            st.error("Erreur lors de la sauvegarde")
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
        
        else:
            st.error("Erreur de chargement des données")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
    
    if st.button(get_testo("logout", st.session_state.lingua)):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.codice_operatore = None
        st.session_state.pin_operatore = None
        st.session_state.pagina = 'home'
        st.rerun()

# ============================================================================
# PAGINA TRASMISSIONE DATI GIORNALIERI
# ============================================================================

def pagina_trasmissione_dati_giornalieri():
    st.title("Transmission de Données - Journaliers")
    
    st.warning("⚠️ Ceci n'est PAS un contrat d'embauche, mais seulement la transmission de vos données pour un futur emploi éventuel et le paiement des journaliers.")
    
    with st.form("form_giornalieri"):
        st.subheader("📋 Informations Personnelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cognome = st.text_input("Nom *", "")
            nome = st.text_input("Prénom *", "")
            data_nascita = st.text_input("Date de naissance (JJ/MM/AAAA)", "")
            luogo_nascita = st.text_input("Lieu de naissance", "")
            nazionalita = st.text_input("Nationalité", "Sénégalaise")
        
        with col2:
            sesso = st.selectbox("Sexe", ["Masculin", "Féminin"])
            stato_civile = st.selectbox("État civil", ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"])
            figli = st.number_input("Nombre d'enfants", min_value=0, value=0)
            cni = st.text_input("CNI (Carte Nationale d'Identité)", "")
            css = st.text_input("CSS (Sécurité Sociale)", "")
        
        st.markdown("---")
        st.subheader("📍 Coordonnées")
        
        col1, col2 = st.columns(2)
        
        with col1:
            telefono = st.text_input("Téléphone *", "")
            indirizzo = st.text_input("Adresse *", "")
            quartiere = st.text_input("Quartier", "")
        
        with col2:
            comune = st.text_input("Commune", "")
            dipartimento = st.text_input("Département/Région", "")
            email = st.text_input("Email", "")
        
        st.markdown("---")
        st.subheader("💼 Informations Professionnelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mansione = st.text_input("Poste souhaité", "")
            esperienza = st.number_input("Années d'expérience", min_value=0, max_value=50, value=0)
        
        with col2:
            disponibilita = st.selectbox("Disponibilité", ["Immédiate", "1 semaine", "2 semaines", "1 mois", "Autre"])
            studi = st.selectbox("Niveau d'études", ["Aucun", "Primaire", "Collège", "Lycée", "CAP", "BTS", "Licence", "Master", "Doctorat"])
        
        submitted = st.form_submit_button("📤 Transmettre mes données", type="primary")
        
        if submitted:
            if not cognome or not nome or not telefono or not indirizzo:
                st.error("Veuillez remplir les champs obligatoires (*)")
                st.stop()
            
            codice = genera_codice_operatore(cognome, nome)
            pin = genera_pin()
            
            dati = {
                'id': f"JOUR-{datetime.now().year}-{random.randint(1000, 9999)}",
                'codice': codice,
                'pin': pin,
                'data_registrazione': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'cognome': cognome,
                'nome': nome,
                'data_nascita': data_nascita,
                'luogo_nascita': luogo_nascita,
                'nazionalita': nazionalita,
                'sesso': sesso,
                'stato_civile': stato_civile,
                'figli_totale': figli,
                'cni': cni,
                'css': css,
                'telefono_1': telefono,
                'indirizzo': indirizzo,
                'quartiere': quartiere,
                'comune': comune,
                'regione_senegal': dipartimento,
                'mansione_1': mansione,
                'tipo': 'Giornaliero'
            }
            
            if salva_su_google_sheets(GOOGLE_SCRIPT_URL_ASSUNZIONI, dati, action="append"):
                st.success("✅ Données transmises avec succès!")
                st.info(f"**Conservez ces identifiants:**\n\nCode d'accès: **{codice}**\nPIN: **{pin}**")
                st.ballo()
            else:
                st.error("Erreur lors de la transmission")

# ============================================================================
# PAGINA CANDIDATURE SPONTANEE
# ============================================================================

def pagina_candidatura():
    st.title(get_testo('candidatura_spontanea', st.session_state.lingua))
    
    st.info("ℹ️ Ceci n'est PAS un contrat, mais seulement l'envoi de votre candidature spontanée.")
    
    with st.form("form_candidatura"):
        st.subheader("📋 Informations Personnelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cognome = st.text_input("Nom *", "")
            nome = st.text_input("Prénom *", "")
            data_nascita = st.text_input("Date de naissance (JJ/MM/AAAA)", "")
            luogo_nascita = st.text_input("Lieu de naissance", "")
        
        with col2:
            indirizzo = st.text_input("Adresse *", "")
            comune = st.text_input("Commune", "")
            regione = st.text_input("Région", "")
            telefono = st.text_input("Téléphone *", "")
        
        st.markdown("---")
        st.subheader("📧 Contact")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email", "")
        
        with col2:
            telefono2 = st.text_input("Téléphone 2", "")
        
        st.markdown("---")
        st.subheader("💼 Informations Professionnelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mansione_richiesta = st.text_input("Poste souhaité", "")
            studi = st.selectbox("Niveau d'études", ["Aucun", "Primaire", "Collège", "Lycée", "CAP", "BTS", "Licence", "Master", "Doctorat"])
            specialite = st.text_input("Spécialité / Filière", "")
        
        with col2:
            esperienze = st.number_input("Années d'expérience", min_value=0, max_value=50, value=0)
            poste_actuel = st.text_input("Poste actuel ou dernier poste occupé", "")
            entreprise_actuelle = st.text_input("Entreprise actuelle ou dernière entreprise", "")
        
        st.markdown("---")
        st.subheader("🎓 Formations et Compétences")
        
        formations = st.text_area("Cours, certifications ou formations complémentaires", height=100)
        competences = st.text_area("Vos compétences techniques", height=100)
        skills = st.text_area("Vos compétences / Skills", height=100)
        
        st.markdown("---")
        st.subheader("💡 Motivation")
        
        motivazione = st.text_area("Pourquoi souhaitez-vous travailler chez PROACIER?", height=150)
        disponibilite = st.selectbox("Disponibilité", ["Immédiate", "1 semaine", "2 semaines", "1 mois", "Autre"])
        
        submitted = st.form_submit_button(" Envoyer ma candidature", type="primary")
        
        if submitted:
            if not cognome or not nome or not telefono:
                st.error("Veuillez remplir les champs obligatoires (*)")
                st.stop()
            
            dati = {
                'id': f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}",
                'data_candidatura': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'cognome': cognome,
                'nome': nome,
                'email': email,
                'telefono': telefono,
                'telefono2': telefono2,
                'data_nascita': data_nascita,
                'indirizzo': indirizzo,
                'comune': comune,
                'regione': regione,
                'mansione_richiesta': mansione_richiesta,
                'studi': studi,
                'specialite': specialite,
                'esperienze': esperienze,
                'poste_actuel': poste_actuel,
                'entreprise_actuelle': entreprise_actuelle,
                'formations': formations,
                'competences': competences,
                'skills': skills,
                'motivazione': motivazione,
                'disponibilite': disponibilite
            }
            
            if salva_su_google_sheets(GOOGLE_SCRIPT_URL_CANDIDATURE, dati, action="append"):
                st.success("✅ Candidature envoyée avec succès! Nous vous contacterons bientôt.")
                st.ballo()
            else:
                st.error("Erreur lors de l'envoi")

# ============================================================================
# PAGINA REGISTRAZIONE MULTI-STEP (ASSUNZIONI COMPLETE)
# ============================================================================

def pagina_registrazione_multi_step(lingua):
    """Form assunzioni completo a 6 step"""
    
    st.title(get_testo('nuova_assunzione', lingua))
    
    # Barra di progresso
    progress = st.progress((st.session_state.step - 1) / 6)
    st.write(f"**Step {st.session_state.step} / 6**")
    
    dati = st.session_state.dati_form
    
    # STEP 1: IDENTITÀ & FAMIGLIA
    if st.session_state.step == 1:
        st.subheader(get_testo('step1_identite', lingua))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['cognome'] = st.text_input(get_testo('cognome', lingua), value=dati.get('cognome', ''))
            dati['nome'] = st.text_input(get_testo('nome', lingua), value=dati.get('nome', ''))
            dati['data_nascita'] = st.text_input(get_testo('data_nascita', lingua), value=dati.get('data_nascita', ''))
            dati['luogo_nascita'] = st.text_input(get_testo('luogo_nascita', lingua), value=dati.get('luogo_nascita', ''))
        
        with col2:
            dati['nazionalita'] = st.text_input(get_testo('nazionalita', lingua), value=dati.get('nazionalita', 'Sénégalaise'))
            dati['sesso'] = st.selectbox(get_testo('sesso', lingua), ["Masculin", "Féminin"], index=0 if dati.get('sesso') == 'Masculin' else 1)
            dati['stato_civile'] = st.selectbox(get_testo('stato_civile', lingua), ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf(ve)"], 
                                                 index=0 if dati.get('stato_civile') == 'Célibataire' else 1)
            dati['numero_mogli'] = st.number_input(get_testo('numero_mogli', lingua), min_value=0, max_value=10, value=int(dati.get('numero_mogli', 0)))
            dati['figli_totale'] = st.number_input(get_testo('figli_totale', lingua), min_value=0, max_value=50, value=int(dati.get('figli_totale', 0)))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            pass
        with col2:
            if st.button(get_testo('suivant', lingua), type="primary"):
                if dati.get('cognome') and dati.get('nome') and dati.get('luogo_nascita'):
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Veuillez remplir les champs obligatoires (*)")
    
    # STEP 2: COORDINATE
    elif st.session_state.step == 2:
        st.subheader(get_testo('step2_coord', lingua))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['indirizzo'] = st.text_input(get_testo('indirizzo', lingua), value=dati.get('indirizzo', ''))
            dati['quartiere'] = st.text_input(get_testo('quartiere', lingua), value=dati.get('quartiere', ''))
            dati['comune'] = st.text_input(get_testo('comune', lingua), value=dati.get('comune', ''))
        
        with col2:
            dati['regione_senegal'] = st.text_input(get_testo('dipartimento', lingua), value=dati.get('regione_senegal', ''))
            dati['telefono_1'] = st.text_input(get_testo('telefono_1', lingua), value=dati.get('telefono_1', ''))
            dati['telefono_2'] = st.text_input(get_testo('telefono_2', lingua), value=dati.get('telefono_2', ''))
            dati['telefono_3'] = st.text_input(get_testo('telefono_3', lingua), value=dati.get('telefono_3', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent', lingua)):
                st.session_state.step = 1
                st.rerun()
        with col2:
            if st.button(get_testo('suivant', lingua), type="primary"):
                if dati.get('indirizzo') and dati.get('quartiere') and dati.get('comune') and dati.get('telefono_1'):
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("Veuillez remplir les champs obligatoires (*)")
    
    # STEP 3: DOCUMENTI UFFICIALI
    elif st.session_state.step == 3:
        st.subheader(get_testo('step3_documents', lingua))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['cni'] = st.text_input(get_testo('cni', lingua), value=dati.get('cni', ''))
            dati['nif'] = st.text_input(get_testo('nif', lingua), value=dati.get('nif', ''))
            dati['css'] = st.text_input(get_testo('css', lingua), value=dati.get('css', ''))
        
        with col2:
            dati['cmu'] = st.text_input(get_testo('cmu', lingua), value=dati.get('cmu', ''))
            dati['ipres'] = st.text_input(get_testo('ipres', lingua), value=dati.get('ipres', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent', lingua)):
                st.session_state.step = 2
                st.rerun()
        with col2:
            if st.button(get_testo('suivant', lingua), type="primary"):
                if dati.get('cni'):
                    st.session_state.step = 4
                    st.rerun()
                else:
                    st.error("CNI obligatoire (*)")
    
    # STEP 4: IMPIEGO & SALARIO
    elif st.session_state.step == 4:
        st.subheader(get_testo('step4_emploi', lingua))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['mansione_1'] = st.text_input(get_testo('mansione_1', lingua), value=dati.get('mansione_1', ''))
            dati['luogo_lavoro'] = st.text_input(get_testo('luogo_lavoro', lingua), value=dati.get('luogo_lavoro', ''))
            dati['reparto'] = st.text_input(get_testo('reparto', lingua), value=dati.get('reparto', ''))
            dati['supervisore'] = st.text_input(get_testo('supervisore', lingua), value=dati.get('supervisore', ''))
        
        with col2:
            dati['data_inizio_1'] = st.text_input(get_testo('data_inizio_1', lingua), value=dati.get('data_inizio_1', ''))
            dati['salario'] = st.text_input(get_testo('salario', lingua), value=dati.get('salario', ''))
            dati['ore_giorno'] = st.number_input(get_testo('ore_giorno', lingua), min_value=0, max_value=24, value=int(dati.get('ore_giorno', 8)))
            dati['giorni_settimana'] = st.number_input(get_testo('giorni_settimana', lingua), min_value=0, max_value=7, value=int(dati.get('giorni_settimana', 6)))
            dati['pagamento'] = st.selectbox(get_testo('pagamento', lingua), ["Horaire", "Journalier", "Mensuel", "Hebdomadaire"], 
                                              index=0 if dati.get('pagamento') == 'Horaire' else 1)
            dati['wave_orange'] = st.text_input(get_testo('wave_orange', lingua), value=dati.get('wave_orange', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent', lingua)):
                st.session_state.step = 3
                st.rerun()
        with col2:
            if st.button(get_testo('suivant', lingua), type="primary"):
                if dati.get('mansione_1') and dati.get('luogo_lavoro') and dati.get('data_inizio_1') and dati.get('salario'):
                    st.session_state.step = 5
                    st.rerun()
                else:
                    st.error("Veuillez remplir les champs obligatoires (*)")
    
    # STEP 5: COMPETENZE & SALUTE
    elif st.session_state.step == 5:
        st.subheader(get_testo('step5_competences', lingua))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['categoria_competenza'] = st.text_input(get_testo('categoria_competenza', lingua), value=dati.get('categoria_competenza', ''))
            dati['dettaglio_competenza'] = st.text_input(get_testo('dettaglio_competenza', lingua), value=dati.get('dettaglio_competenza', ''))
            dati['patente'] = st.text_input(get_testo('patente', lingua), value=dati.get('patente', ''))
        
        with col2:
            dati['gruppo_sanguigno'] = st.selectbox(get_testo('gruppo_sanguigno', lingua), ["A", "B", "AB", "O", ""], index=4)
            dati['rh'] = st.selectbox(get_testo('rh', lingua), ["+", "-"], index=0)
            dati['allergie'] = st.text_input(get_testo('allergie', lingua), value=dati.get('allergie', ''))
            dati['malattie'] = st.text_input(get_testo('malattie', lingua), value=dati.get('malattie', ''))
            dati['idoneita'] = st.text_input(get_testo('idoneita', lingua), value=dati.get('idoneita', ''))
            dati['data_visita'] = st.text_input(get_testo('data_visita', lingua), value=dati.get('data_visita', ''))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent', lingua)):
                st.session_state.step = 4
                st.rerun()
        with col2:
            if st.button(get_testo('suivant', lingua), type="primary"):
                st.session_state.step = 6
                st.rerun()
    
    # STEP 6: EMERGENZA & CONFERMA
    elif st.session_state.step == 6:
        st.subheader(get_testo('step6_urgence', lingua))
        
        col1, col2 = st.columns(2)
        
        with col1:
            dati['emergenza_nome'] = st.text_input(get_testo('emergenza_nome', lingua), value=dati.get('emergenza_nome', ''))
            dati['emergenza_parentela'] = st.text_input(get_testo('emergenza_parentela', lingua), value=dati.get('emergenza_parentela', ''))
        
        with col2:
            dati['emergenza_tel'] = st.text_input(get_testo('emergenza_tel', lingua), value=dati.get('emergenza_tel', ''))
            dati['emergenza_indirizzo'] = st.text_input(get_testo('emergenza_indirizzo', lingua), value=dati.get('emergenza_indirizzo', ''))
        
        st.markdown("---")
        st.info(get_testo('certifico', lingua))
        st.markdown(f"[{get_testo('leggi_condizioni', lingua)}]({URL_CONDIZIONI})")
        
        certifica = st.checkbox(get_testo('certifico_checkbox', lingua))
        
        st.session_state.dati_form = dati
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_testo('precedent', lingua)):
                st.session_state.step = 5
                st.rerun()
        with col2:
            if st.button(get_testo('generer_pdf', lingua), type="primary"):
                if certifica and dati.get('emergenza_nome') and dati.get('emergenza_tel'):
                    # Genera codice e PIN
                    codice = genera_codice_operatore(dati.get('cognome', ''), dati.get('nome', ''))
                    pin = genera_pin()
                    
                    dati['codice'] = codice
                    dati['pin'] = pin
                    dati['data_registrazione'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    dati['id'] = f"EMP-{datetime.now().year}-{random.randint(1000, 9999)}"
                    dati['tipo'] = 'Assunzione'
                    
                    # Salva su Google
                    if salva_su_google_sheets(GOOGLE_SCRIPT_URL_ASSUNZIONI, dati, action="append"):
                        st.success(get_testo('enregistrement_reussi', lingua))
                        
                        # Genera PDF
                        pdf_bytes = genera_pdf_lavoratore(dati)
                        
                        st.markdown("---")
                        st.warning(f"⚠️ {get_testo('conservez_identifiants', lingua)}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.info(f"**{get_testo('code_acces', lingua)}:** {codice}")
                        with col2:
                            st.info(f"**{get_testo('pin_acces', lingua)}:** {pin}")
                        
                        st.download_button(
                            label=f"📥 {get_testo('telecharger_pdf', lingua)}",
                            data=pdf_bytes,
                            file_name=f"Fiche_{dati.get('cognome', '')}_{dati.get('nome', '')}.pdf",
                            mime="application/pdf"
                        )
                        
                        st.ballo()
                        
                        # Reset form
                        st.session_state.dati_form = {}
                        st.session_state.step = 1
                    else:
                        st.error("Erreur lors de l'enregistrement")
                else:
                    st.error("Veuillez certifier et remplir les champs urgence")
    
    progress.progress(st.session_state.step / 6)

# ============================================================================
# PAGINA DASHBOARD ADMIN
# ============================================================================

def pagina_dashboard():
    st.title(get_testo('dashboard', st.session_state.lingua))
    
    if not st.session_state.get('admin_logged'):
        password = st.text_input("Mot de passe administrateur", type="password")
        if st.button("Connexion"):
            if password == PASSWORD_DASHBOARD:
                st.session_state.admin_logged = True
                st.success("Connexion réussie")
                st.rerun()
            else:
                st.error("Mot de passe incorrect")
    else:
        st.success("Connecté en tant qu'administrateur")
        
        if st.button("Déconnexion"):
            st.session_state.admin_logged = False
            st.rerun()
        
        st.markdown("---")
        st.subheader("Gestion des salaires individuels")
        
        try:
            response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data[1:], columns=data[0])
                
                st.write(f"Total travailleurs: {len(df)}")
                
                lavoratore = st.selectbox("Sélectionner un travailleur", df['Cognome'] + ' ' + df['Nome'])
                
                if lavoratore:
                    row = df[df['Cognome'] + ' ' + df['Nome'] == lavoratore].iloc[0]
                    idx = row.name
                    
                    st.text_input("Code", value=row.get('Codice', ''), disabled=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        tipo_paga = st.selectbox("Type de paiement", ["Horaire", "Journalier", "Mensuel", "Hebdomadaire"], 
                                                   index=0 if row.get('Tipo_Paga') == 'Horaire' else (1 if row.get('Tipo_Paga') == 'Journalier' else (2 if row.get('Tipo_Paga') == 'Mensuel' else 3)))
                    
                    with col2:
                        valore_paga = st.text_input("Montant (FCFA)", value=str(row.get('Valore_Paga', '')))
                    
                    if st.button("💾 Enregistrer le salaire"):
                        df.loc[idx, 'Tipo_Paga'] = tipo_paga
                        df.loc[idx, 'Valore_Paga'] = valore_paga
                        
                        dati_json = {"action": "update", "data": df.to_dict(orient='records')}
                        resp = requests.post(GOOGLE_SCRIPT_URL_ASSUNZIONI, json=dati_json)
                        
                        if resp.status_code == 200:
                            st.success("✅ Salaire enregistré!")
                        else:
                            st.error("Erreur")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image(LOGO_URL, use_column_width=True)
    st.markdown("---")
    
    # Selezione lingua - FIX: usa key unica e rerun
    lingua_attuale = st.session_state.lingua
    index_lingua = 0 if lingua_attuale == 'fr' else (1 if lingua_attuale == 'it' else 2)
    
    lingua_sel = st.selectbox(
        get_testo('lingua', lingua_attuale), 
        ["Français", "Italiano", "English"],
        index=index_lingua,
        key="sel_lingua_sidebar"
    )
    
    nuova_lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
    
    if nuova_lingua != lingua_attuale:
        st.session_state.lingua = nuova_lingua
        st.rerun()
    
    st.markdown("---")
    
    # Navigazione
    if st.button(get_testo('candidature', st.session_state.lingua), use_container_width=True):
        st.session_state.pagina = 'candidatura'
        st.rerun()
    
    if st.button(get_testo('espace_travailleur', st.session_state.lingua), use_container_width=True):
        st.session_state.pagina = 'espace_travailleur'
        st.rerun()
    
    if st.button(get_testo('dashboard', st.session_state.lingua), use_container_width=True):
        st.session_state.pagina = 'dashboard'
        st.rerun()

# ============================================================================
# ROUTING PAGINE
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
