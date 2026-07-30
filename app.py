# -*- coding: utf-8 -*-
"""
PROACIER - Sistema di Gestione Operai
Senegal - Regione di Thiès
Versione 1.2 - 2026
"""

import streamlit as st
import requests
from datetime import datetime
import random
from fpdf import FPDF

# ============================================
# CONFIGURAZIONE PAGINA
# ============================================
st.set_page_config(
    page_title="Proacier - Gestione Operai",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CONFIGURAZIONE SICURA
# ============================================
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwLn6HNH_k_Az2Mtfx-2SFwy0TH9tb8ygXRSXYrDKfbHcjzxXcK1f3Z3TXfhOBhKnHi/exec"
EMAIL_NOTIFICA = "m.galli@proacier.sn"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# ============================================
# TRADUZIONI COMPLETE
# ============================================
TRADUZIONI = {
    "it": {
        "titolo": "🏭 PROACIER - GESTIONE OPERAI",
        "sottotitolo": "Sistema di registrazione operai - Senegal",
        "menu": "Menu",
        "registrazione": "📝 Nuova Registrazione",
        "area_lavoratore": "👤 Area Lavoratore",
        "dashboard": "🏢 Dashboard Azienda",
        "lingua": "🌐 Lingua",
        "benvenuto": "Benvenuto",
        "logout": "Esci",
        "codice": "Codice Operatore",
        "pin": "PIN",
        "accedi": "Accedi",
        "password": "Password",
        "dashboard_titolo": "DASHBOARD AZIENDA",
        "totale_operai": "Totale Operai",
        "cerca": "Cerca operatore...",
        "scarica_pdf": "Scarica PDF",
        "nessun_risultato": "Nessun operatore trovato",
        "codice_errato": "Codice o PIN errati",
        "benvenuto_lavoratore": "Benvenuto",
        "i_miei_dati": "I Miei Dati",
        "salva": "Salva",
        "indietro": "Indietro",
        "registra": "REGISTRAZIONE OPERAIO",
        "dati_anagrafici": "Dati Anagrafici",
        "documenti": "Documenti",
        "lavoro": "Informazioni Professionali",
        "epi": "Taglie EPI",
        "medico": "Informazioni Mediche",
        "emergenza": "Contatto Emergenza",
        "cognome": "Cognome",
        "nome": "Nome",
        "data_nascita": "Data di nascita",
        "luogo_nascita": "Luogo di nascita",
        "nazionalita": "Nazionalità",
        "sesso": "Sesso",
        "maschile": "Maschile",
        "femminile": "Femminile",
        "stato_civile": "Stato civile",
        "celibe": "Celibe/Nubile",
        "coniugato": "Coniugato/a",
        "divorziato": "Divorziato/a",
        "vedovo": "Vedovo/a",
        "numero_mogli": "Numero di mogli",
        "figli": "Figli a carico",
        "indirizzo": "Indirizzo",
        "quartiere": "Quartiere/Villaggio",
        "comune": "Comune/Arrondissement",
        "paese": "Paese",
        "dipartimento": "Dipartimento/Regione",
        "thies": "Thiès",
        "tivaouane": "Tivaouane",
        "mbour": "Mbour",
        "altro": "Altro / Other",
        "telefono": "Telefono",
        "telefono2": "Telefono secondario",
        "cni": "Numero CNI",
        "css": "Numero CSS",
        "ipres": "Numero IPRES",
        "mansione": "Mansione",
        "luogo_lavoro": "Luogo di lavoro",
        "reparto": "Reparto",
        "supervisore": "Supervisore",
        "data_inizio": "Data inizio",
        "salario": "Salario giornaliero (FCFA)",
        "ore_giorno": "Ore/giorno",
        "giorni_settimana": "Giorni/settimana",
        "pagamento": "Modalità pagamento",
        "especes": "Contanti",
        "virement": "Bonifico",
        "mobile": "Mobile Money",
        "taglia_maglia": "Taglia maglia",
        "taglia_pantaloni": "Taglia pantaloni",
        "taglia_scarpe": "Taglia scarpe",
        "taglia_guanti": "Taglia guanti",
        "taglia_casco": "Taglia casco",
        "taglia_gilet": "Taglia gilet",
        "gruppo_sanguigno": "Gruppo sanguigno",
        "rh": "Rh",
        "allergie": "Allergie",
        "malattie": "Malattie croniche",
        "idoneita": "Idoneità medica",
        "apte": "Apto",
        "restriction": "Apto con restrizioni",
        "inapte": "Inapto",
        "data_visita": "Data visita medica",
        "emergenza_nome": "Nome contatto emergenza",
        "emergenza_parentela": "Parentela",
        "emergenza_tel": "Telefono emergenza",
        "emergenza_indirizzo": "Indirizzo emergenza",
        "genera_pdf": "📄 Genera PDF e Registra",
        "pdf_generato": "PDF generato con successo!",
        "conserva_credenziali": "️ CONSERVA QUESTE CREDENZIALI",
        "codice_accesso": "Codice di accesso",
        "pin_accesso": "PIN di accesso",
        "scarica": "Scarica",
        "firma": "Far firmare al lavoratore",
        "paese_altro": "Inserisci nome Paese",
        "regione": "Regione/Dipartimento",
        "lista_operai": "Lista Operai",
        "cognome_nome": "Cognome e Nome",
        "telefono_col": "Telefono",
        "mansione_col": "Mansione",
        "stato_firma": "Stato Firma"
    },
    "fr": {
        "titolo": "🏭 PROACIER - GESTION OUVRIERS",
        "sottotitolo": "Système d'enregistrement - Sénégal",
        "menu": "Menu",
        "registrazione": "📝 Nouvelle Inscription",
        "area_lavoratore": "👤 Espace Ouvrier",
        "dashboard": " Tableau de Bord",
        "lingua": "🌐 Langue",
        "benvenuto": "Bienvenue",
        "logout": "Déconnexion",
        "codice": "Code Ouvrier",
        "pin": "PIN",
        "accedi": "Accéder",
        "password": "Mot de passe",
        "dashboard_titolo": "TABLEAU DE BORD",
        "totale_operai": "Total Ouvriers",
        "cerca": "Rechercher...",
        "scarica_pdf": "Télécharger PDF",
        "nessun_risultato": "Aucun ouvrier trouvé",
        "codice_errato": "Code ou PIN incorrect",
        "benvenuto_lavoratore": "Bienvenue",
        "i_miei_dati": "Mes Données",
        "salva": "Enregistrer",
        "indietro": "Retour",
        "registra": "ENREGISTREMENT OUVRIER",
        "dati_anagrafici": "Données Personnelles",
        "documenti": "Documents",
        "lavoro": "Informations Professionnelles",
        "epi": "Tailles EPI",
        "medico": "Informations Médicales",
        "emergenza": "Contact Urgence",
        "cognome": "Nom",
        "nome": "Prénom(s)",
        "data_nascita": "Date de naissance",
        "luogo_nascita": "Lieu de naissance",
        "nazionalita": "Nationalité",
        "sesso": "Sexe",
        "maschile": "Masculin",
        "femminile": "Féminin",
        "stato_civile": "État civil",
        "celibe": "Célibataire",
        "coniugato": "Marié(e)",
        "divorziato": "Divorcé(e)",
        "vedovo": "Veuf/Veuve",
        "numero_mogli": "Nombre d'épouses",
        "figli": "Enfants à charge",
        "indirizzo": "Adresse",
        "quartiere": "Quartier/Village",
        "comune": "Commune/Arrondissement",
        "paese": "Pays",
        "dipartimento": "Département/Région",
        "thies": "Thiès",
        "tivaouane": "Tivaouane",
        "mbour": "Mbour",
        "altro": "Autre / Other",
        "telefono": "Téléphone",
        "telefono2": "Téléphone secondaire",
        "cni": "N° CNI",
        "css": "N° Sécurité Sociale",
        "ipres": "N° IPRES",
        "mansione": "Fonction",
        "luogo_lavoro": "Lieu de travail",
        "reparto": "Service",
        "supervisore": "Superviseur",
        "data_inizio": "Date de début",
        "salario": "Salaire journalier (FCFA)",
        "ore_giorno": "Heures/jour",
        "giorni_settimana": "Jours/semaine",
        "pagamento": "Mode de paiement",
        "especes": "Espèces",
        "virement": "Virement",
        "mobile": "Mobile Money",
        "taglia_maglia": "Taille haut",
        "taglia_pantaloni": "Taille pantalon",
        "taglia_scarpe": "Taille chaussures",
        "taglia_guanti": "Taille gants",
        "taglia_casco": "Taille casque",
        "taglia_gilet": "Taille gilet",
        "gruppo_sanguigno": "Groupe sanguin",
        "rh": "Rh",
        "allergie": "Allergies",
        "malattie": "Maladies chroniques",
        "idoneita": "Aptitude médicale",
        "apte": "Apte",
        "restriction": "Apte avec restriction",
        "inapte": "Inapte",
        "data_visita": "Date visite médicale",
        "emergenza_nome": "Nom contact urgence",
        "emergenza_parentela": "Lien de parenté",
        "emergenza_tel": "Téléphone urgence",
        "emergenza_indirizzo": "Adresse urgence",
        "genera_pdf": "📄 Générer PDF et Enregistrer",
        "pdf_generato": "PDF généré avec succès!",
        "conserva_credenziali": "⚠️ CONSERVEZ CES IDENTIFIANTS",
        "codice_accesso": "Code d'accès",
        "pin_accesso": "PIN d'accès",
        "scarica": "Télécharger",
        "firma": "Faire signer à l'ouvrier",
        "paese_altro": "Entrez le nom du pays",
        "regione": "Région/Département",
        "lista_operai": "Liste Ouvriers",
        "cognome_nome": "Nom et Prénom",
        "telefono_col": "Téléphone",
        "mansione_col": "Fonction",
        "stato_firma": "État Signature"
    },
    "en": {
        "titolo": "🏭 PROACIER - WORKER MANAGEMENT",
        "sottotitolo": "Worker registration system - Senegal",
        "menu": "Menu",
        "registrazione": " New Registration",
        "area_lavoratore": "👤 Worker Area",
        "dashboard": "🏢 Company Dashboard",
        "lingua": "🌐 Language",
        "benvenuto": "Welcome",
        "logout": "Logout",
        "codice": "Worker Code",
        "pin": "PIN",
        "accedi": "Login",
        "password": "Password",
        "dashboard_titolo": "COMPANY DASHBOARD",
        "totale_operai": "Total Workers",
        "cerca": "Search worker...",
        "scarica_pdf": "Download PDF",
        "nessun_risultato": "No worker found",
        "codice_errato": "Wrong code or PIN",
        "benvenuto_lavoratore": "Welcome",
        "i_miei_dati": "My Data",
        "salva": "Save",
        "indietro": "Back",
        "registra": "WORKER REGISTRATION",
        "dati_anagrafici": "Personal Data",
        "documenti": "Documents",
        "lavoro": "Professional Information",
        "epi": "PPE Sizes",
        "medico": "Medical Information",
        "emergenza": "Emergency Contact",
        "cognome": "Surname",
        "nome": "First Name",
        "data_nascita": "Date of birth",
        "luogo_nascita": "Place of birth",
        "nazionalita": "Nationality",
        "sesso": "Gender",
        "maschile": "Male",
        "femminile": "Female",
        "stato_civile": "Marital status",
        "celibe": "Single",
        "coniugato": "Married",
        "divorziato": "Divorced",
        "vedovo": "Widowed",
        "numero_mogli": "Number of wives",
        "figli": "Dependent children",
        "indirizzo": "Address",
        "quartiere": "District/Village",
        "comune": "Municipality",
        "paese": "Country",
        "dipartimento": "Department/Region",
        "thies": "Thiès",
        "tivaouane": "Tivaouane",
        "mbour": "Mbour",
        "altro": "Other / Altro",
        "telefono": "Phone",
        "telefono2": "Secondary phone",
        "cni": "ID Number",
        "css": "Social Security Number",
        "ipres": "Pension Number",
        "mansione": "Position",
        "luogo_lavoro": "Work location",
        "reparto": "Department",
        "supervisore": "Supervisor",
        "data_inizio": "Start date",
        "salario": "Daily salary (FCFA)",
        "ore_giorno": "Hours/day",
        "giorni_settimana": "Days/week",
        "pagamento": "Payment method",
        "especes": "Cash",
        "virement": "Bank transfer",
        "mobile": "Mobile Money",
        "taglia_maglia": "Shirt size",
        "taglia_pantaloni": "Pants size",
        "taglia_scarpe": "Shoe size",
        "taglia_guanti": "Gloves size",
        "taglia_casco": "Helmet size",
        "taglia_gilet": "Vest size",
        "gruppo_sanguigno": "Blood type",
        "rh": "Rh",
        "allergie": "Allergies",
        "malattie": "Chronic diseases",
        "idoneita": "Medical fitness",
        "apte": "Fit",
        "restriction": "Fit with restrictions",
        "inapte": "Unfit",
        "data_visita": "Medical visit date",
        "emergenza_nome": "Emergency contact name",
        "emergenza_parentela": "Relationship",
        "emergenza_tel": "Emergency phone",
        "emergenza_indirizzo": "Emergency address",
        "genera_pdf": "📄 Generate PDF and Register",
        "pdf_generato": "PDF generated successfully!",
        "conserva_credenziali": "⚠️ SAVE THESE CREDENTIALS",
        "codice_accesso": "Access code",
        "pin_accesso": "Access PIN",
        "scarica": "Download",
        "firma": "Have the worker sign",
        "paese_altro": "Enter country name",
        "regione": "Region/Department",
        "lista_operai": "Workers List",
        "cognome_nome": "Full Name",
        "telefono_col": "Phone",
        "mansione_col": "Position",
        "stato_firma": "Signature Status"
    }
}

# ============================================
# FUNZIONI DI SUPPORTO
# ============================================

def get_testo(chiave, lingua="fr"):
    return TRADUZIONI.get(lingua, TRADUZIONI["fr"]).get(chiave, chiave)

def genera_codice():
    anno = datetime.now().year
    numero = random.randint(1000, 9999)
    return f"THS-{anno}-{numero}"

def genera_pin():
    return str(random.randint(1000, 9999))

def salva_su_google_sheet(dati, azione="append"):
    try:
        if azione == "append":
            payload = {"row": dati}
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, headers={"Content-Type": "application/json"})
        return response.status_code == 200
    except Exception as e:
        st.error(f"Errore Google Sheets: {e}")
        return False

def leggi_da_google_sheet():
    try:
        response = requests.get(f"{GOOGLE_SCRIPT_URL}?action=read")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Errore lettura: {e}")
        return []

# ============================================
# GENERATORE PDF
# ============================================

class PDFProacier(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(68, 114, 196)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FICHE D\'ENREGISTREMENT - OUVRIER', 0, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.ln(3)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
    
    def sezione(self, titolo):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(217, 225, 242)
        self.cell(0, 8, titolo, 0, 1, 'C', True)
        self.ln(2)
    
    def campo(self, etichetta, valore):
        self.set_font('Helvetica', 'B', 9)
        self.cell(60, 7, etichetta, 0, 0)
        self.set_font('Helvetica', '', 9)
        self.cell(0, 7, str(valore) if valore else "___________", 0, 1)
    
    def campo_doppio(self, et1, val1, et2, val2):
        self.set_font('Helvetica', 'B', 9)
        self.cell(50, 7, et1, 0, 0)
        self.set_font('Helvetica', '', 9)
        self.cell(45, 7, str(val1) if val1 else "______", 0, 0)
        self.set_font('Helvetica', 'B', 9)
        self.cell(50, 7, et2, 0, 0)
        self.set_font('Helvetica', '', 9)
        self.cell(0, 7, str(val2) if val2 else "______", 0, 1)

def genera_pdf_lavoratore(dati):
    pdf = PDFProacier()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(95, 7, f"N° fiche: {dati.get('codice', '')}", 0, 0)
    pdf.cell(0, 7, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.ln(3)
    
    pdf.sezione("SECTION 1 - IDENTITE DU TRAVAILLEUR")
    pdf.campo_doppio("Nom:", dati.get('cognome', ''), "Prenom(s):", dati.get('nome', ''))
    pdf.campo_doppio("Date naissance:", dati.get('data_nascita', ''), "Lieu:", dati.get('luogo_nascita', ''))
    pdf.campo_doppio("Nationalite:", dati.get('nazionalita', ''), "Sexe:", dati.get('sesso', ''))
    pdf.campo_doppio("Etat civil:", dati.get('stato_civile', ''), "Enfants:", dati.get('figli', ''))
    if dati.get('numero_mogli', 0) > 0:
        pdf.campo("Nombre d'epouses:", dati.get('numero_mogli', ''))
    pdf.campo("Adresse:", f"{dati.get('indirizzo', '')} - {dati.get('quartiere', '')}")
    pdf.campo("Pays:", dati.get('dipartimento', ''))
    pdf.campo_doppio("Telephone:", dati.get('telefono', ''), "Tel 2:", dati.get('telefono2', ''))
    pdf.ln(3)
    
    pdf.sezione("SECTION 2 - DOCUMENTS")
    pdf.campo("CNI N°:", dati.get('cni', ''))
    pdf.campo("N° Securite Sociale (CSS):", dati.get('css', ''))
    pdf.campo("N° IPRES:", dati.get('ipres', ''))
    pdf.ln(3)
    
    pdf.sezione("SECTION 3 - INFORMATIONS PROFESSIONNELLES")
    pdf.campo_doppio("Fonction:", dati.get('mansione', ''), "Chantier:", dati.get('luogo_lavoro', ''))
    pdf.campo_doppio("Service:", dati.get('reparto', ''), "Superviseur:", dati.get('supervisore', ''))
    pdf.campo_doppio("Date debut:", dati.get('data_inizio', ''), "Salaire:", f"{dati.get('salario', '')} FCFA")
    pdf.campo_doppio("Heures/jour:", dati.get('ore_giorno', ''), "Jours/sem:", dati.get('giorni_settimana', ''))
    pdf.campo("Paiement:", dati.get('pagamento', ''))
    pdf.ln(3)
    
    pdf.sezione("SECTION 4 - TAILLES EPI")
    pdf.campo_doppio("Haut:", dati.get('taglia_maglia', ''), "Pantalon:", dati.get('taglia_pantaloni', ''))
    pdf.campo_doppio("Chaussures:", dati.get('taglia_scarpe', ''), "Gants:", dati.get('taglia_guanti', ''))
    pdf.campo_doppio("Casque:", dati.get('taglia_casco', ''), "Gilet:", dati.get('taglia_gilet', ''))
    pdf.ln(3)
    
    pdf.sezione("SECTION 5 - INFORMATIONS MEDICALES")
    pdf.campo_doppio("Groupe sanguin:", dati.get('gruppo_sanguigno', ''), "Rh:", dati.get('rh', ''))
    pdf.campo("Allergies:", dati.get('allergie', ''))
    pdf.campo("Maladies chroniques:", dati.get('malattie', ''))
    pdf.campo_doppio("Aptitude:", dati.get('idoneita', ''), "Date visite:", dati.get('data_visita', ''))
    pdf.ln(3)
    
    pdf.sezione("SECTION 6 - CONTACT URGENCE")
    pdf.campo_doppio("Nom:", dati.get('emergenza_nome', ''), "Lien:", dati.get('emergenza_parentela', ''))
    pdf.campo_doppio("Telephone:", dati.get('emergenza_tel', ''), "Adresse:", dati.get('emergenza_indirizzo', ''))
    pdf.ln(5)
    
    pdf.sezione("SECTION 7 - SIGNATURES")
    pdf.set_font('Helvetica', 'I', 9)
    pdf.multi_cell(0, 5, "Je soussigne(e), reconnais avoir pris connaissance des conditions de travail.")
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(95, 7, 'TRAVAILLEUR', 1, 0, 'C')
    pdf.cell(95, 7, 'EMPLOYEUR', 1, 1, 'C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(95, 20, '', 1, 0)
    pdf.cell(95, 20, '', 1, 1)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 7, 'Nom:', 0, 0)
    pdf.cell(95, 7, 'Nom:', 0, 1)
    pdf.cell(95, 7, 'Signature:', 0, 0)
    pdf.cell(95, 7, 'Signature:', 0, 1)
    pdf.cell(95, 7, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 0)
    pdf.cell(95, 7, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 1)
    
    # Pagina 2 - Privacy
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_fill_color(68, 114, 196)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, 'CONSENTEMENT DONNEES PERSONNELLES', 0, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'I', 9)
    pdf.multi_cell(0, 5, "Conformement a la Loi n° 2008-12 du 25 janvier 2008 (Senegal)")
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'INFORMATIONS:', 0, 1)
    pdf.set_font('Helvetica', '', 9)
    
    info = [
        "1. COLLECTE: Vos donnees sont collectees pour la gestion administrative.",
        "2. FINALITES: Paie, securite au travail, contacts d'urgence.",
        "3. DUREE: Conservation 5 ans apres fin contrat.",
        "4. DROITS: Droit d'acces, rectification, suppression.",
        "5. AUTORITE: CDP - www.cdp.sn"
    ]
    
    for riga in info:
        pdf.multi_cell(0, 5, riga)
    
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_fill_color(255, 192, 0)
    pdf.cell(0, 8, 'CONSENTEMENT EXRES', 0, 1, 'C', True)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    nome_completo = f"{dati.get('cognome', '')} {dati.get('nome', '')}"
    pdf.multi_cell(0, 6, f"Je soussigne(e), {nome_completo}, donne mon consentement expres.")
    pdf.ln(8)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 7, 'Signature:', 0, 1)
    pdf.ln(2)
    pdf.cell(0, 30, '', 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# ============================================
# INTERFACCIA UTENTE
# ============================================

def main():
    if 'lingua' not in st.session_state:
        st.session_state.lingua = 'fr'
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'home'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    with st.sidebar:
        st.title(get_testo("titolo", st.session_state.lingua))
        st.markdown(get_testo("sottotitolo", st.session_state.lingua))
        st.markdown("---")
        
        lingua_sel = st.selectbox(
            get_testo("lingua", st.session_state.lingua),
            ["English", "Français", "Italiano"],
            index=0 if st.session_state.lingua == 'en' else (1 if st.session_state.lingua == 'fr' else 2),
            key="sel_lingua"
        )
        st.session_state.lingua = 'en' if lingua_sel == "English" else ('fr' if lingua_sel == "Français" else 'it')
        
        st.markdown("---")
        
        if st.session_state.logged_in:
            if st.session_state.user_type == 'admin':
                st.success(f"{get_testo('benvenuto', st.session_state.lingua)} Admin")
                if st.button(get_testo("dashboard", st.session_state.lingua), key="btn_dash"):
                    st.session_state.pagina = 'dashboard'
                if st.button(get_testo("logout", st.session_state.lingua), key="btn_logout"):
                    st.session_state.logged_in = False
                    st.session_state.pagina = 'home'
            elif st.session_state.user_type == 'lavoratore':
                st.success(f"{get_testo('benvenuto_lavoratore', st.session_state.lingua)}")
                if st.button(get_testo("i_miei_dati", st.session_state.lingua), key="btn_miei"):
                    st.session_state.pagina = 'area_lavoratore'
                if st.button(get_testo("logout", st.session_state.lingua), key="btn_logout_lav"):
                    st.session_state.logged_in = False
                    st.session_state.pagina = 'home'
        else:
            if st.button(get_testo("registrazione", st.session_state.lingua), key="btn_reg"):
                st.session_state.pagina = 'registrazione'
            if st.button(get_testo("area_lavoratore", st.session_state.lingua), key="btn_area"):
                st.session_state.pagina = 'login_lavoratore'
            if st.button(get_testo("dashboard", st.session_state.lingua), key="btn_dash_login"):
                st.session_state.pagina = 'login_admin'
    
    if st.session_state.pagina == 'home':
        st.title(" PROACIER SN")
        st.markdown("### Système de Gestion des Ouvriers")
        st.markdown("---")
        st.info(" Utilisez le menu à gauche")
    
    elif st.session_state.pagina == 'registrazione':
        pagina_registrazione()
    
    elif st.session_state.pagina == 'login_lavoratore':
        pagina_login_lavoratore()
    
    elif st.session_state.pagina == 'area_lavoratore':
        pagina_area_lavoratore()
    
    elif st.session_state.pagina == 'login_admin':
        pagina_login_admin()
    
    elif st.session_state.pagina == 'dashboard':
        pagina_dashboard()

def pagina_registrazione():
    st.title(get_testo("registra", st.session_state.lingua))
    
    with st.form("form_registrazione", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(get_testo("dati_anagrafici", st.session_state.lingua))
            cognome = st.text_input(get_testo("cognome", st.session_state.lingua), key="f_cognome")
            nome = st.text_input(get_testo("nome", st.session_state.lingua), key="f_nome")
            
            # Data di nascita con 3 selectbox (GG/MM/AAAA)
            st.markdown(f"**{get_testo('data_nascita', st.session_state.lingua)}**")
            col_g, col_m, col_a = st.columns(3)
            with col_g:
                giorno_n = st.selectbox("Jour", range(1, 32), index=0, key="f_giorno_n")
            with col_m:
                mese_n = st.selectbox("Mois", range(1, 13), index=0, key="f_mese_n")
            with col_a:
                anno_n = st.selectbox("Année", range(1950, 2010), index=30, key="f_anno_n")
            data_nascita_str = f"{giorno_n:02d}/{mese_n:02d}/{anno_n}"
            
            luogo_nascita = st.text_input(get_testo("luogo_nascita", st.session_state.lingua), key="f_luogo_nascita")
            nazionalita = st.text_input(get_testo("nazionalita", st.session_state.lingua), value="Sénégalaise", key="f_nazionalita")
            sesso = st.selectbox(get_testo("sesso", st.session_state.lingua), 
                [get_testo("maschile", st.session_state.lingua), get_testo("femminile", st.session_state.lingua)], 
                key="f_sesso")
            stato_civile = st.selectbox(get_testo("stato_civile", st.session_state.lingua), [
                get_testo("celibe", st.session_state.lingua),
                get_testo("coniugato", st.session_state.lingua),
                get_testo("divorziato", st.session_state.lingua),
                get_testo("vedovo", st.session_state.lingua)
            ], key="f_stato_civile")
            
            numero_mogli = 0
            if stato_civile == get_testo("coniugato", st.session_state.lingua):
                numero_mogli = st.number_input(get_testo("numero_mogli", st.session_state.lingua), 
                    min_value=1, max_value=4, value=1, key="f_numero_mogli")
            
            figli = st.number_input(get_testo("figli", st.session_state.lingua), min_value=0, value=0, key="f_figli")
        
        with col2:
            st.subheader(get_testo("documenti", st.session_state.lingua))
            indirizzo = st.text_input(get_testo("indirizzo", st.session_state.lingua), key="f_indirizzo")
            quartiere = st.text_input(get_testo("quartiere", st.session_state.lingua), key="f_quartiere")
            comune = st.text_input(get_testo("comune", st.session_state.lingua), key="f_comune")
            
            # PAESE DI RESIDENZA (indipendente dalla nazionalità)
            paese_residenza = st.selectbox(get_testo("paese", st.session_state.lingua), 
                ["Sénégal", "Sierra Leone", "Guinea", "Mali", "Gambia", "Autre / Other"],
                index=0, key="f_paese_residenza")
            
            # Regioni basate sul PAESE DI RESIDENZA
            if paese_residenza == "Sénégal":
                dipartimento = st.selectbox(get_testo("dipartimento", st.session_state.lingua), [
                    "Thiès", "Tivaouane", "Mbour",
                    "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda",
                    "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam",
                    "Autre région"
                ], key="f_dipartimento_senegal")
            elif paese_residenza == "Autre / Other":
                paese_altro = st.text_input("Nom du pays / Country name", key="f_paese_altro_residenza")
                regione_altro = st.text_input("Région / Region", key="f_regione_altro_residenza")
                dipartimento = f"{paese_altro} - {regione_altro}" if paese_altro and regione_altro else (paese_altro if paese_altro else "Autre")
            else:
                regione_straniera = st.text_input(f"Région de {paese_residenza} / Region of {paese_residenza}", 
                    key=f"f_regione_{paese_residenza.lower().replace(' ', '_')}")
                dipartimento = f"{paese_residenza} - {regione_straniera}" if regione_straniera else paese_residenza
            
            telefono = st.text_input(get_testo("telefono", st.session_state.lingua), key="f_telefono")
            telefono2 = st.text_input(get_testo("telefono2", st.session_state.lingua), key="f_telefono2")
            cni = st.text_input(get_testo("cni", st.session_state.lingua), key="f_cni")
            css = st.text_input(get_testo("css", st.session_state.lingua), key="f_css")
            ipres = st.text_input(get_testo("ipres", st.session_state.lingua), key="f_ipres")
        
        st.subheader(get_testo("lavoro", st.session_state.lingua))
        col1, col2 = st.columns(2)
        with col1:
            mansione = st.text_input(get_testo("mansione", st.session_state.lingua), key="f_mansione")
            luogo_lavoro = st.text_input(get_testo("luogo_lavoro", st.session_state.lingua), key="f_luogo_lavoro")
            reparto = st.text_input(get_testo("reparto", st.session_state.lingua), key="f_reparto")
            supervisore = st.text_input(get_testo("supervisore", st.session_state.lingua), key="f_supervisore")
        with col2:
            # Data inizio lavoro con 3 selectbox
            st.markdown(f"**{get_testo('data_inizio', st.session_state.lingua)}**")
            col_g2, col_m2, col_a2 = st.columns(3)
            with col_g2:
                giorno_i = st.selectbox("Jour", range(1, 32), index=29, key="f_giorno_i")
            with col_m2:
                mese_i = st.selectbox("Mois", range(1, 13), index=6, key="f_mese_i")
            with col_a2:
                anno_i = st.selectbox("Année", range(2020, 2035), index=6, key="f_anno_i")
            data_inizio_str = f"{giorno_i:02d}/{mese_i:02d}/{anno_i}"
            
            salario = st.number_input(get_testo("salario", st.session_state.lingua), min_value=0, value=5000, key="f_salario")
            ore_giorno = st.number_input(get_testo("ore_giorno", st.session_state.lingua), min_value=1, max_value=24, value=8, key="f_ore_giorno")
            giorni_settimana = st.text_input(get_testo("giorni_settimana", st.session_state.lingua), value="Lun-Ven", key="f_giorni_settimana")
            pagamento = st.selectbox(get_testo("pagamento", st.session_state.lingua), [
                get_testo("especes", st.session_state.lingua),
                get_testo("virement", st.session_state.lingua),
                get_testo("mobile", st.session_state.lingua)
            ], key="f_pagamento")
        
        st.subheader(get_testo("epi", st.session_state.lingua))
        col1, col2, col3 = st.columns(3)
        with col1:
            taglia_maglia = st.selectbox(get_testo("taglia_maglia", st.session_state.lingua), 
                ["XS", "S", "M", "L", "XL", "XXL", "3XL"], key="f_taglia_maglia")
            taglia_pantaloni = st.selectbox(get_testo("taglia_pantaloni", st.session_state.lingua), 
                ["36", "38", "40", "42", "44", "46", "48", "50"], key="f_taglia_pantaloni")
            taglia_scarpe = st.selectbox(get_testo("taglia_scarpe", st.session_state.lingua), 
                ["38", "39", "40", "41", "42", "43", "44", "45", "46"], key="f_taglia_scarpe")
        with col2:
            taglia_guanti = st.selectbox(get_testo("taglia_guanti", st.session_state.lingua), 
                ["S", "M", "L", "XL"], key="f_taglia_guanti")
            taglia_casco = st.selectbox(get_testo("taglia_casco", st.session_state.lingua), 
                ["Standard", "Ajustable"], key="f_taglia_casco")
            taglia_gilet = st.selectbox(get_testo("taglia_gilet", st.session_state.lingua), 
                ["S", "M", "L", "XL", "XXL"], key="f_taglia_gilet")
        
        st.subheader(get_testo("medico", st.session_state.lingua))
        col1, col2 = st.columns(2)
        with col1:
            gruppo_sanguigno = st.selectbox(get_testo("gruppo_sanguigno", st.session_state.lingua), 
                ["A", "B", "AB", "O"], key="f_gruppo_sanguigno")
            rh = st.selectbox(get_testo("rh", st.session_state.lingua), 
                ["+", "-"], key="f_rh")
            allergie = st.text_area(get_testo("allergie", st.session_state.lingua), key="f_allergie")
        with col2:
            malattie = st.text_area(get_testo("malattie", st.session_state.lingua), key="f_malattie")
            idoneita = st.selectbox(get_testo("idoneita", st.session_state.lingua), [
                get_testo("apte", st.session_state.lingua),
                get_testo("restriction", st.session_state.lingua),
                get_testo("inapte", st.session_state.lingua)
            ], key="f_idoneita")
            
            # Data visita medica con 3 selectbox
            st.markdown(f"**{get_testo('data_visita', st.session_state.lingua)}**")
            col_g3, col_m3, col_a3 = st.columns(3)
            with col_g3:
                giorno_v = st.selectbox("Jour", range(1, 32), index=29, key="f_giorno_v")
            with col_m3:
                mese_v = st.selectbox("Mois", range(1, 13), index=6, key="f_mese_v")
            with col_a3:
                anno_v = st.selectbox("Année", range(2020, 2035), index=6, key="f_anno_v")
            data_visita_str = f"{giorno_v:02d}/{mese_v:02d}/{anno_v}"
        
        st.subheader(get_testo("emergenza", st.session_state.lingua))
        col1, col2 = st.columns(2)
        with col1:
            emergenza_nome = st.text_input(get_testo("emergenza_nome", st.session_state.lingua), key="f_emergenza_nome")
            emergenza_parentela = st.text_input(get_testo("emergenza_parentela", st.session_state.lingua), key="f_emergenza_parentela")
        with col2:
            emergenza_tel = st.text_input(get_testo("emergenza_tel", st.session_state.lingua), key="f_emergenza_tel")
            emergenza_indirizzo = st.text_input(get_testo("emergenza_indirizzo", st.session_state.lingua), key="f_emergenza_indirizzo")
        
        submitted = st.form_submit_button(get_testo("genera_pdf", st.session_state.lingua), type="primary", use_container_width=True)
        
        if submitted:
            if not cognome or not nome:
                st.error("Veuillez remplir au moins Nom et Prénom!")
                return
            
            codice = genera_codice()
            pin = genera_pin()
            
            dati = {
                "id": codice,
                "codice": codice,
                "pin": pin,
                "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cognome": cognome,
                "nome": nome,
                "data_nascita": data_nascita_str,
                "luogo_nascita": luogo_nascita,
                "nazionalita": nazionalita,
                "sesso": sesso,
                "stato_civile": stato_civile,
                "numero_mogli": numero_mogli,
                "figli": figli,
                "indirizzo": indirizzo,
                "quartiere": quartiere,
                "comune": comune,
                "dipartimento": dipartimento,
                "telefono": telefono,
                "telefono2": telefono2,
                "cni": cni,
                "css": css,
                "ipres": ipres,
                "mansione": mansione,
                "luogo_lavoro": luogo_lavoro,
                "reparto": reparto,
                "supervisore": supervisore,
                "data_inizio": data_inizio_str,
                "salario": salario,
                "ore_giorno": ore_giorno,
                "giorni_settimana": giorni_settimana,
                "pagamento": pagamento,
                "taglia_maglia": taglia_maglia,
                "taglia_pantaloni": taglia_pantaloni,
                "taglia_scarpe": taglia_scarpe,
                "taglia_guanti": taglia_guanti,
                "taglia_casco": taglia_casco,
                "taglia_gilet": taglia_gilet,
                "gruppo_sanguigno": gruppo_sanguigno,
                "rh": rh,
                "allergie": allergie,
                "malattie": malattie,
                "idoneita": idoneita,
                "data_visita": data_visita_str,
                "emergenza_nome": emergenza_nome,
                "emergenza_parentela": emergenza_parentela,
                "emergenza_tel": emergenza_tel,
                "emergenza_indirizzo": emergenza_indirizzo,
                "stato_firma": "Da firmare",
                "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            
            if salva_su_google_sheet(dati, "append"):
                st.success(f"✅ {get_testo('pdf_generato', st.session_state.lingua)}")
                
                pdf_bytes = genera_pdf_lavoratore(dati)
                
                st.warning(get_testo('conserva_credenziali', st.session_state.lingua))
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**{get_testo('codice_accesso', st.session_state.lingua)}:** {codice}")
                with col2:
                    st.info(f"**{get_testo('pin_accesso', st.session_state.lingua)}:** {pin}")
                
                st.download_button(
                    label=f"📥 {get_testo('scarica', st.session_state.lingua)} PDF",
                    data=pdf_bytes,
                    file_name=f"Proacier_{codice}_{cognome}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="btn_download"
                )
                
                st.success(f"ℹ️ {get_testo('firma', st.session_state.lingua)}")
            else:
                st.error("Erreur lors de l'enregistrement.")

def pagina_login_lavoratore():
    st.title(get_testo("area_lavoratore", st.session_state.lingua))
    
    codice = st.text_input(get_testo("codice", st.session_state.lingua), key="login_codice")
    pin = st.text_input(get_testo("pin", st.session_state.lingua), type="password", key="login_pin")
    
    if st.button(get_testo("accedi", st.session_state.lingua), type="primary", key="btn_login_lav"):
        dati_lavoratori = leggi_da_google_sheet()
        
        trovato = False
        for row in dati_lavoratori[1:]:
            if len(row) >= 3 and str(row[1]) == codice and str(row[2]) == pin:
                trovato = True
                st.session_state.logged_in = True
                st.session_state.user_type = 'lavoratore'
                st.session_state.user_data = {
                    'codice': row[1],
                    'nome': row[4] if len(row) > 4 else '',
                    'cognome': row[3] if len(row) > 3 else ''
                }
                st.session_state.pagina = 'area_lavoratore'
                st.rerun()
                break
        
        if not trovato:
            st.error(get_testo("codice_errato", st.session_state.lingua))

def pagina_area_lavoratore():
    st.title(get_testo("i_miei_dati", st.session_state.lingua))
    
    if not st.session_state.user_data:
        st.error("Non sei loggato")
        return
    
    st.info(f"{get_testo('benvenuto_lavoratore', st.session_state.lingua)} {st.session_state.user_data.get('nome', '')}")
    st.warning("Per modifiche, contattare l'amministrazione")

def pagina_login_admin():
    st.title(get_testo("dashboard", st.session_state.lingua))
    
    password = st.text_input(get_testo("password", st.session_state.lingua), type="password", key="login_pwd")
    
    if st.button(get_testo("accedi", st.session_state.lingua), type="primary", key="btn_login_admin"):
        if password == PASSWORD_DASHBOARD:
            st.session_state.logged_in = True
            st.session_state.user_type = 'admin'
            st.session_state.pagina = 'dashboard'
            st.rerun()
        else:
            st.error("Password errata")

def pagina_dashboard():
    st.title(get_testo("dashboard_titolo", st.session_state.lingua))
    
    dati_lavoratori = leggi_da_google_sheet()
    
    if dati_lavoratori:
        totale = len(dati_lavoratori) - 1
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(get_testo("totale_operai", st.session_state.lingua), totale)
        col2.metric("Nuovi oggi", 0)
        col3.metric("Da firmare", 0)
        col4.metric("Modifiche", 0)
        
        st.markdown("---")
        st.subheader(get_testo("lista_operai", st.session_state.lingua))
        
        import pandas as pd
        if len(dati_lavoratori) > 1:
            headers = dati_lavoratori[0]
            df = pd.DataFrame(dati_lavoratori[1:], columns=headers)
            
            cerca = st.text_input(get_testo("cerca", st.session_state.lingua), key="dash_cerca")
            if cerca:
                df = df[df['Cognome'].astype(str).str.contains(cerca, case=False, na=False)]
            
            colonne = ['ID', 'Cognome', 'Nome', 'Telefono', 'Mansione', 'Stato_Firma']
            colonne_esistenti = [c for c in colonne if c in df.columns]
            st.dataframe(df[colonne_esistenti], use_container_width=True)
        else:
            st.warning(get_testo("nessun_risultato", st.session_state.lingua))
    else:
        st.warning("Nessun dato disponibile")

if __name__ == "__main__":
    main()
