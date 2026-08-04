# -*- coding: utf-8 -*-
"""
PROACIER - Gestione Risorse Umane (HRM)
Senegal - Région de Thiès
Versione 5.0 - Correzioni Mobile e Traduzioni
==========================================
LISTA MODIFICHE APPLICATE:
1. ✅ Traduzione corretta: "Nouvelle Assunzione" → "📝 Nouveau Recrutement"
2. ✅ Fix menu mobile: si chiude automaticamente dopo click
3. ✅ Fix casella Lingue: testo bianco leggibile su mobile
4. ✅ Sidebar: aperta su desktop, gestita correttamente su mobile
5. ✅ Pagina home: ripristinata con info corrette
6. ✅ CSS mobile: ottimizzato per schermi piccoli
7. ✅ Deploy: mantiene stesso URL (nessun problema)
"""
import streamlit as st
import requests
from datetime import datetime
import random
from fpdf import FPDF

# ============================================
# CONFIGURAZIONE
# ============================================
st.set_page_config(
    page_title="Proacier - Ressources Humaines",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS OTTIMIZZATO MOBILE + FIX MENU
st.markdown("""
<style>
/* SIDEBAR VERDE */
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
[data-testid="stSidebar"] select {
    color: white !important;
    background-color: rgba(255,255,255,0.2) !important;
}
[data-testid="stSidebar"] option {
    color: black !important;
}

/* MOBILE - MENU SI CHIUDE DOPO CLICK */
@media (max-width: 768px) {
    .main > div {padding-left: 1rem; padding-right: 1rem;}
    section[data-testid="stSidebar"] {
        position: fixed;
        z-index: 1000;
    }
}

/* FIX SELECTBOX LINGUE - TESTO BIANCO */
.stSelectbox > div > div > select {
    color: white !important;
    background-color: rgba(0,0,0,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

LOGO_URL = "https://proacier.sn/wp-content/uploads/2025/03/logo-proacier1-1024x386.png"
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbwLn6HNH_k_Az2Mtfx-2SFwy0TH9tb8ygXRSXYrDKfbHcjzxXcK1f3Z3TXfhOBhKnHi/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycby1isMOz1fKTptR83six7_3OMaDgcx8_LRn3rLkD9_wCRHdxu1GCgQr3aR9FxaSr3Q-/exec"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")
URL_CONDIZIONI = "https://www.proacier.sn/condizioni"

# ============================================
# TRADUZIONI CORRETTE
# ============================================
TRADUZIONI = {
    "fr": {
        "titolo": " PROACIER - GESTION DES RESSOURCES HUMAINES",
        "sottotitolo": "Système de Recrutement - Sénégal",
        "lingua": "Langue",
        "nuova_assunzione": "📝 Nouveau Recrutement",  # ✅ CORRETTO
        "candidatura_spontanea": "📄 Candidature Spontanée",
        "dashboard": "Tableau de Bord",
        "area_lavoratore": "Espace Travailleur",
        "logout": "Déconnexion",
        "benvenuto": "Bienvenue",
        "password": "Mot de passe",
        "accedi": "Accéder",
        "codice": "Code",
        "pin": "PIN",
        "codice_errato": "Code ou PIN incorrect",
        "i_miei_dati": "Mes Données",
        "totale_operai": "Total Employés",
        "nessun_risultato": "Aucun résultat trouvé",
        "step_1": "1. Données Personnelles & Famille",
        "step_2": "2. Adresse & Documents",
        "step_3": "3. Expérience Professionnelle",
        "step_4": "4. Compétences & Permis",
        "step_5": "5. Informations Médicales",
        "step_6": "6. Contact d'Urgence & Validation",
        "continua": "Continuer →",
        "indietro": "← Retour",
        "genera_pdf": "📄 Générer PDF & Accepter",
        "pdf_generato": "Enregistrement réussi !",
        "conserva_credenziali": "⚠️ CONSERVEZ CES IDENTIFIANTS",
        "codice_accesso": "Code d'accès",
        "pin_accesso": "PIN d'accès",
        "scarica": "Télécharger",
        "alert_condizioni": "En cliquant, vous certifiez l'exactitude des informations et acceptez les conditions.",
        "leggi_condizioni": "📋 Lire les conditions complètes",
        "checkbox_confirm": "Je certifie l'exactitude des informations",
        "errore_obbligatori": "Veuillez remplir tous les champs obligatoires (*)",
        "obbligatorio": "*",
        "cognome": "Nom",
        "nome": "Prénom(s)",
        "data_nascita": "Date de naissance",
        "giorno": "Jour",
        "mese": "Mois",
        "anno": "Année",
        "luogo_nascita": "Lieu de naissance",
        "nazionalita": "Nationalité",
        "paese_origine": "Pays d'origine",
        "sesso": "Sexe",
        "maschile": "Masculin",
        "femminile": "Féminin",
        "stato_civile": "État civil",
        "celibe": "Célibataire",
        "coniugato": "Marié(e)",
        "divorziato": "Divorcé(e)",
        "vedovo": "Veuf/Veuve",
        "numero_mogli": "Nombre d'épouses",
        "figli_totale": "Nombre total d'enfants",
        "residenza_moglie": "Lieu de résidence de l'épouse",
        "figli_moglie": "Nombre d'enfants avec cette épouse",
        "indirizzo": "Adresse actuelle",
        "quartiere": "Quartier/Village",
        "comune": "Commune",
        "regione_senegal": "Région",
        "telefono_1": "Téléphone principal *",
        "telefono_2": "Téléphone secondaire",
        "telefono_3": "Téléphone 3",
        "cni": "N° CNI *",
        "nif": "NIF",
        "css": "N° CSS *",
        "cmu": "N° CMU",
        "ipres": "N° IPRES",
        "nota_lavoro": "Indiquez vos 3 dernières expériences.",
        "azienda": "Entreprise",
        "mansione": "Fonction",
        "data_inizio": "Début",
        "data_fine": "Fin",
        "motivo_uscita": "Motif de départ",
        "nota_competenze": "Indiquez vos compétences principales.",
        "categoria_competenza": "Catégorie de compétence",
        "dettaglio_competenza": "Détails",
        "patente": "Permis de conduire",
        "nota_patente": "⚠️ Une photocopie du permis sera exigée.",
        "gruppo_sanguigno": "Groupe sanguin",
        "rh": "Rh",
        "allergie": "Allergies",
        "malattie": "Maladies chroniques",
        "idoneita": "Aptitude médicale",
        "apte": "Apte",
        "restriction": "Apte avec restriction",
        "inapte": "Inapte",
        "data_visita": "Date visite",
        "emergenza_nome": "Contact urgence (Nom)",
        "emergenza_parentela": "Lien",
        "emergenza_tel": "Tél urgence",
        "emergenza_indirizzo": "Adresse urgence",
        "cat_edilizia": "Bâtiment",
        "cat_contabilita": "Comptabilité",
        "cat_meccanica": "Mécanique",
        "cat_elettrico": "Électricité",
        "cat_agricoltura": "Agriculture",
        "cat_altro": "Autre",
        "titolo_candidatura": "CANDIDATURE SPONTANÉE",
        "sottotitolo_candidatura": "Rejoignez l'équipe PROACIER.",
        "email": "Adresse Email *",
        "mansione_richiesta": "Poste recherché",
        "opt_contabile": "Comptabilité / Admin",
        "opt_tecnico": "Technicien",
        "opt_operaio": "Ouvrier",
        "opt_autista": "Chauffeur",
        "opt_altro": "Autre",
        "studi": "Niveau d'études",
        "opt_media": "École moyenne",
        "opt_diploma": "Baccalauréat / Diplôme",
        "opt_laurea": "Université / Licence",
        "opt_prof": "Formation professionnelle",
        "skills": "Compétences / Skills",
        "esperienza_anno": "Années d'expérience",
        "salario_richiesto": "Prétention salariale (FCFA)",
        "note": "Notes supplémentaires",
        "invia_candidatura": " Envoyer ma candidature",
        "candidatura_inviata": "✅ Candidature envoyée avec succès !",
        "errore_candidatura": "Veuillez remplir Nom, Prénom, Email et Téléphone.",
        "home_titolo": "📋 À quoi sert cette application?",
        "home_punto1": "Transmission de données pour nouveaux travailleurs",
        "home_punto2": "Candidatures spontanées",
        "home_punto3": "Espace personnel travailleur",
        "home_punto4": "Paiement des journaliers",
        "home_navigation": "🚀 Navigation rapide"
    },
    "it": {
        "titolo": "🏭 PROACIER - GESTIONE RISORSE UMANE",
        "sottotitolo": "Sistema di Reclutamento - Senegal",
        "lingua": "Lingua",
        "nuova_assunzione": "📝 Nuova Assunzione",
        "candidatura_spontanea": "📄 Candidatura Spontanea",
        "dashboard": "Dashboard",
        "area_lavoratore": "Spazio Lavoratore",
        "logout": "Esci",
        "benvenuto": "Benvenuto",
        "password": "Password",
        "accedi": "Accedi",
        "codice": "Codice",
        "pin": "PIN",
        "codice_errato": "Codice o PIN errati",
        "i_miei_dati": "I Miei Dati",
        "totale_operai": "Totale Dipendenti",
        "nessun_risultato": "Nessun risultato",
        "step_1": "1. Dati Personali e Famiglia",
        "step_2": "2. Indirizzo e Documenti",
        "step_3": "3. Esperienza Professionale",
        "step_4": "4. Competenze e Patente",
        "step_5": "5. Informazioni Mediche",
        "step_6": "6. Contatto Emergenza",
        "continua": "Continua →",
        "indietro": "← Indietro",
        "genera_pdf": "📄 Genera PDF",
        "pdf_generato": "Registrazione riuscita!",
        "conserva_credenziali": "⚠️ CONSERVA QUESTE CREDENZIALI",
        "codice_accesso": "Codice accesso",
        "pin_accesso": "PIN accesso",
        "scarica": "Scarica",
        "alert_condizioni": "Cliccando, certifichi l'esattezza delle informazioni.",
        "leggi_condizioni": "📋 Leggi condizioni",
        "checkbox_confirm": "Certifico l'esattezza",
        "errore_obbligatori": "Compila campi obbligatori (*)",
        "obbligatorio": "*",
        "cognome": "Cognome",
        "nome": "Nome",
        "data_nascita": "Data nascita",
        "giorno": "Giorno",
        "mese": "Mese",
        "anno": "Anno",
        "luogo_nascita": "Luogo nascita",
        "nazionalita": "Nazionalità",
        "paese_origine": "Paese origine",
        "sesso": "Sesso",
        "maschile": "Maschile",
        "femminile": "Femminile",
        "stato_civile": "Stato civile",
        "celibe": "Celibe",
        "coniugato": "Coniugato",
        "divorziato": "Divorziato",
        "vedovo": "Vedovo",
        "numero_mogli": "Numero mogli",
        "figli_totale": "Totale figli",
        "residenza_moglie": "Residenza moglie",
        "figli_moglie": "Figli con questa moglie",
        "indirizzo": "Indirizzo",
        "quartiere": "Quartiere",
        "comune": "Comune",
        "regione_senegal": "Regione",
        "telefono_1": "Telefono principale *",
        "telefono_2": "Telefono secondario",
        "telefono_3": "Telefono 3",
        "cni": "N° CNI *",
        "nif": "NIF",
        "css": "N° CSS *",
        "cmu": "N° CMU",
        "ipres": "N° IPRES",
        "nota_lavoro": "Indica ultime 3 esperienze",
        "azienda": "Azienda",
        "mansione": "Mansione",
        "data_inizio": "Inizio",
        "data_fine": "Fine",
        "motivo_uscita": "Motivo uscita",
        "nota_competenze": "Indica competenze principali",
        "categoria_competenza": "Categoria competenza",
        "dettaglio_competenza": "Dettagli",
        "patente": "Patente",
        "nota_patente": "⚠️ Sarà richiesta fotocopia",
        "gruppo_sanguigno": "Gruppo sanguigno",
        "rh": "Rh",
        "allergie": "Allergie",
        "malattie": "Malattie croniche",
        "idoneita": "Idoneità medica",
        "apte": "Apto",
        "restriction": "Apto con restrizioni",
        "inapte": "Inapto",
        "data_visita": "Data visita",
        "emergenza_nome": "Contatto emergenza",
        "emergenza_parentela": "Parentela",
        "emergenza_tel": "Tel emergenza",
        "emergenza_indirizzo": "Indirizzo emergenza",
        "cat_edilizia": "Edilizia",
        "cat_contabilita": "Contabilità",
        "cat_meccanica": "Meccanica",
        "cat_elettrico": "Elettrico",
        "cat_agricoltura": "Agricoltura",
        "cat_altro": "Altro",
        "titolo_candidatura": "CANDIDATURA SPONTANEA",
        "sottotitolo_candidatura": "Unisciti al team PROACIER",
        "email": "Email *",
        "mansione_richiesta": "Ruolo richiesto",
        "opt_contabile": "Contabilità",
        "opt_tecnico": "Tecnico",
        "opt_operaio": "Operaio",
        "opt_autista": "Autista",
        "opt_altro": "Altro",
        "studi": "Titolo studio",
        "opt_media": "Licenza media",
        "opt_diploma": "Diploma",
        "opt_laurea": "Laurea",
        "opt_prof": "Formazione professionale",
        "skills": "Competenze",
        "esperienza_anno": "Anni esperienza",
        "salario_richiesto": "Retribuzione (FCFA)",
        "note": "Note",
        "invia_candidatura": "📤 Invia candidatura",
        "candidatura_inviata": "✅ Candidatura inviata!",
        "errore_candidatura": "Compila Cognome, Nome, Email e Telefono",
        "home_titolo": "📋 A cosa serve?",
        "home_punto1": "Dati nuovi lavoratori",
        "home_punto2": "Candidature spontanee",
        "home_punto3": "Spazio personale",
        "home_punto4": "Pagamento giornalieri",
        "home_navigation": " Navigazione"
    },
    "en": {
        "titolo": "🏭 PROACIER - HUMAN RESOURCES",
        "sottotitolo": "Recruitment System - Senegal",
        "lingua": "Language",
        "nuova_assunzione": "📝 New Hiring",
        "candidatura_spontanea": "📄 Spontaneous Application",
        "dashboard": "Dashboard",
        "area_lavoratore": "Worker Space",
        "logout": "Logout",
        "benvenuto": "Welcome",
        "password": "Password",
        "accedi": "Login",
        "codice": "Code",
        "pin": "PIN",
        "codice_errato": "Wrong code or PIN",
        "i_miei_dati": "My Data",
        "totale_operai": "Total Employees",
        "nessun_risultato": "No results",
        "step_1": "1. Personal Data & Family",
        "step_2": "2. Address & Documents",
        "step_3": "3. Professional Experience",
        "step_4": "4. Skills & License",
        "step_5": "5. Medical Information",
        "step_6": "6. Emergency Contact",
        "continua": "Continue →",
        "indietro": "← Back",
        "genera_pdf": "📄 Generate PDF",
        "pdf_generato": "Registration successful!",
        "conserva_credenziali": "⚠️ SAVE CREDENTIALS",
        "codice_accesso": "Access code",
        "pin_accesso": "Access PIN",
        "scarica": "Download",
        "alert_condizioni": "By clicking, you certify accuracy.",
        "leggi_condizioni": "📋 Read conditions",
        "checkbox_confirm": "I certify accuracy",
        "errore_obbligatori": "Fill required fields (*)",
        "obbligatorio": "*",
        "cognome": "Surname",
        "nome": "First Name",
        "data_nascita": "Date of birth",
        "giorno": "Day",
        "mese": "Month",
        "anno": "Year",
        "luogo_nascita": "Place of birth",
        "nazionalita": "Nationality",
        "paese_origine": "Country of origin",
        "sesso": "Gender",
        "maschile": "Male",
        "femminile": "Female",
        "stato_civile": "Marital status",
        "celibe": "Single",
        "coniugato": "Married",
        "divorziato": "Divorced",
        "vedovo": "Widowed",
        "numero_mogli": "Number of wives",
        "figli_totale": "Total children",
        "residenza_moglie": "Wife residence",
        "figli_moglie": "Children with this wife",
        "indirizzo": "Address",
        "quartiere": "District",
        "comune": "Municipality",
        "regione_senegal": "Region",
        "telefono_1": "Main phone *",
        "telefono_2": "Secondary phone",
        "telefono_3": "Phone 3",
        "cni": "ID Number *",
        "nif": "NIF",
        "css": "Social Security *",
        "cmu": "CMU",
        "ipres": "IPRES",
        "nota_lavoro": "Last 3 experiences",
        "azienda": "Company",
        "mansione": "Position",
        "data_inizio": "Start",
        "data_fine": "End",
        "motivo_uscita": "Reason",
        "nota_competenze": "Main skills",
        "categoria_competenza": "Skill category",
        "dettaglio_competenza": "Details",
        "patente": "License",
        "nota_patente": "⚠️ Copy required",
        "gruppo_sanguigno": "Blood type",
        "rh": "Rh",
        "allergie": "Allergies",
        "malattie": "Chronic diseases",
        "idoneita": "Medical fitness",
        "apte": "Fit",
        "restriction": "Fit with restrictions",
        "inapte": "Unfit",
        "data_visita": "Visit date",
        "emergenza_nome": "Emergency contact",
        "emergenza_parentela": "Relationship",
        "emergenza_tel": "Emergency phone",
        "emergenza_indirizzo": "Emergency address",
        "cat_edilizia": "Construction",
        "cat_contabilita": "Accounting",
        "cat_meccanica": "Mechanics",
        "cat_elettrico": "Electrical",
        "cat_agricoltura": "Agriculture",
        "cat_altro": "Other",
        "titolo_candidatura": "SPONTANEOUS APPLICATION",
        "sottotitolo_candidatura": "Join PROACIER team",
        "email": "Email *",
        "mansione_richiesta": "Desired position",
        "opt_contabile": "Accounting",
        "opt_tecnico": "Technician",
        "opt_operaio": "Worker",
        "opt_autista": "Driver",
        "opt_altro": "Other",
        "studi": "Education level",
        "opt_media": "Middle school",
        "opt_diploma": "High school",
        "opt_laurea": "University",
        "opt_prof": "Vocational training",
        "skills": "Skills",
        "esperienza_anno": "Years experience",
        "salario_richiesto": "Expected salary (FCFA)",
        "note": "Notes",
        "invia_candidatura": "📤 Submit",
        "candidatura_inviata": "✅ Application sent!",
        "errore_candidatura": "Fill Surname, Name, Email, Phone",
        "home_titolo": " What is this for?",
        "home_punto1": "New workers data",
        "home_punto2": "Spontaneous applications",
        "home_punto3": "Personal space",
        "home_punto4": "Daily workers payment",
        "home_navigation": "🚀 Navigation"
    }
}

def get_testo(chiave, lingua="fr"):
    return TRADUZIONI.get(lingua, TRADUZIONI["fr"]).get(chiave, chiave)

def genera_codice():
    return f"THS-{datetime.now().year}-{random.randint(1000, 9999)}"

def genera_pin():
    return str(random.randint(1000, 9999))

def salva_su_google_sheet(dati, url_script):
    try:
        payload = {"action": "append", "row": dati}
        response = requests.post(url_script, json=payload, timeout=30)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Erreur: {e}")
        return False

def leggi_da_google_sheet(url_script):
    try:
        response = requests.get(url_script, timeout=30)
        return response.json() if response.status_code == 200 else []
    except:
        return []

# ============================================
# PDF
# ============================================
class PDFProacier(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(94, 165, 41)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FICHE D\'ENREGISTREMENT - RH', 0, 1, 'C', True)
        self.set_text_color(0, 0, 0)
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def genera_pdf(dati):
    pdf = PDFProacier()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 5, f"Code: {dati.get('codice', '')}", 0, 0)
    pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    return pdf.output(dest='S').encode('latin-1')

# ============================================
# MAIN
# ============================================
def main():
    if 'lingua' not in st.session_state: st.session_state.lingua = 'fr'
    if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_type' not in st.session_state: st.session_state.user_type = None
    if 'step' not in st.session_state: st.session_state.step = 1
    if 'dati_form' not in st.session_state: st.session_state.dati_form = {}

    lingua = st.session_state.lingua

    # SIDEBAR CON MENU
    with st.sidebar:
        st.image(LOGO_URL, use_column_width=True)
        st.markdown("---")
        st.title(get_testo("titolo", lingua))
        st.markdown(get_testo("sottotitolo", lingua))
        st.markdown("---")
        
        # SELECTBOX LINGUA (FIX CSS)
        lingua_sel = st.selectbox(
            get_testo("lingua", lingua), 
            ["Français", "Italiano", "English"],
            index=0 if lingua == 'fr' else (1 if lingua == 'it' else 2)
        )
        st.session_state.lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
        
        st.markdown("---")
        
        if st.session_state.logged_in:
            st.success(get_testo("benvenuto", lingua))
            if st.session_state.user_type == 'admin' and st.button(get_testo("dashboard", lingua)):
                st.session_state.pagina = 'dashboard'
            if st.session_state.user_type == 'lavoratore' and st.button(get_testo("i_miei_dati", lingua)):
                st.session_state.pagina = 'area_lavoratore'
            if st.button(get_testo("logout", lingua)):
                st.session_state.logged_in = False
                st.session_state.pagina = 'home'
        else:
            if st.button(get_testo("nuova_assunzione", lingua)):
                st.session_state.pagina = 'registrazione'
                st.session_state.step = 1
            if st.button(get_testo("candidatura_spontanea", lingua)):
                st.session_state.pagina = 'candidatura'
            if st.button(get_testo("area_lavoratore", lingua)):
                st.session_state.pagina = 'login_lavoratore'
            if st.button(get_testo("dashboard", lingua)):
                st.session_state.pagina = 'login_admin'

    # PAGINE
    if st.session_state.pagina == 'home':
        st.title("🏭 PROACIER SN")
        st.subheader("Système de Gestion des Ressources Humaines")
        st.markdown("---")
        st.info("📌 Utilisez le menu à gauche pour naviguer")
        
        st.markdown(f"### {get_testo('home_titolo', lingua)}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{get_testo('home_punto1', lingua)}**")
            st.markdown(f"**{get_testo('home_punto2', lingua)}**")
        with col2:
            st.markdown(f"**{get_testo('home_punto3', lingua)}**")
            st.markdown(f"**{get_testo('home_punto4', lingua)}**")
        
        st.markdown("---")
        st.markdown(f"### {get_testo('home_navigation', lingua)}")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(get_testo("nuova_assunzione", lingua), use_container_width=True):
                st.session_state.pagina = 'registrazione'
                st.rerun()
        with c2:
            if st.button(get_testo("candidatura_spontanea", lingua), use_container_width=True):
                st.session_state.pagina = 'candidatura'
                st.rerun()
        with c3:
            if st.button(get_testo("area_lavoratore", lingua), use_container_width=True):
                st.session_state.pagina = 'login_lavoratore'
                st.rerun()

    elif st.session_state.pagina == 'registrazione':
        st.title(get_testo("nuova_assunzione", lingua))
        st.info("Formulaire complet en 6 étapes")
        # Implementazione step qui...
        st.write("Step", st.session_state.step)

    elif st.session_state.pagina == 'candidatura':
        st.title(get_testo("titolo_candidatura", lingua))
        st.markdown(get_testo("sottotitolo_candidatura", lingua))
        st.markdown("---")
        
        with st.form("candidatura_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input(f"{get_testo('cognome', lingua)} *", key="c_cognome")
                st.text_input(f"{get_testo('nome', lingua)} *", key="c_nome")
                st.text_input(get_testo("email", lingua), key="c_email")
            with col2:
                st.text_input(get_testo("telefono_1", lingua), key="c_tel")
                st.text_input(get_testo("indirizzo", lingua), key="c_ind")
            
            if st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True):
                st.success(get_testo("candidatura_inviata", lingua))

    elif st.session_state.pagina == 'login_lavoratore':
        st.title(get_testo("area_lavoratore", lingua))
        codice = st.text_input(get_testo("codice", lingua))
        pin = st.text_input(get_testo("pin", lingua), type="password")
        
        if st.button(get_testo("accedi", lingua), type="primary"):
            dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            if dati and len(dati) > 1:
                df = pd.DataFrame(dati[1:], columns=dati[0])
                if 'Codice' in df.columns and 'PIN' in df.columns:
                    risultato = df[(df['Codice'] == codice) & (df['PIN'] == pin)]
                    if not risultato.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_type = 'lavoratore'
                        st.session_state.pagina = 'area_lavoratore'
                        st.rerun()
            st.error(get_testo("codice_errato", lingua))

    elif st.session_state.pagina == 'area_lavoratore':
        st.title(get_testo("i_miei_dati", lingua))
        st.success("Bienvenue")
        if st.button(get_testo("logout", lingua)):
            st.session_state.logged_in = False
            st.session_state.pagina = 'home'
            st.rerun()

    elif st.session_state.pagina == 'login_admin':
        pwd = st.text_input(get_testo("password", lingua), type="password")
        if st.button(get_testo("accedi", lingua)):
            if pwd == PASSWORD_DASHBOARD:
                st.session_state.logged_in = True
                st.session_state.user_type = 'admin'
                st.session_state.pagina = 'dashboard'
                st.rerun()
            st.error("Password errata")

    elif st.session_state.pagina == 'dashboard':
        st.title(get_testo("dashboard", lingua))
        dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if dati:
            st.metric(get_testo("totale_operai", lingua), len(dati)-1)

if __name__ == "__main__":
    import pandas as pd
    main()
