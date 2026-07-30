# -*- coding: utf-8 -*-
"""
PROACIER - Sistema di Gestione Operai
Senegal - Regione di Thiès
Versione 2.0 - 2026
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
    page_title="Proacier - Gestione Operai",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/XXXXXXXXXX/exec"
EMAIL_NOTIFICA = "proacier.sn@gmail.com"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")
URL_CONDIZIONI = "https://www.proacier.sn/condizioni"  # Link pagina condizioni

# ============================================
# TRADUZIONI
# ============================================
TRADUZIONI = {
    "fr": {
        "titolo": "🏭 PROACIER - GESTION OUVRIERS",
        "sottotitolo": "Système d'enregistrement - Sénégal",
        "lingua": "Langue",
        "step_1": "1. Données Personnelles",
        "step_2": "2. Adresse au Sénégal",
        "step_3": "3. Informations Professionnelles",
        "step_4": "4. Équipements de Protection (EPI)",
        "step_5": "5. Informations Médicales",
        "step_6": "6. Contact d'Urgence & Validation",
        "continua": "Continuer →",
        "indietro": "← Retour",
        "genera_pdf": "📄 Générer PDF & Accepter",
        "pdf_generato": "PDF généré avec succès!",
        "conserva_credenziali": "⚠️ CONSERVEZ CES IDENTIFIANTS",
        "codice_accesso": "Code d'accès",
        "pin_accesso": "PIN d'accès",
        "scarica": "Télécharger",
        "firma": "Faire signer à l'ouvrier",
        "alert_condizioni": "En cliquant sur ce bouton, vous certifiez que toutes les informations fournies sont véridiques et vous acceptez les conditions générales.",
        "leggi_condizioni": "📋 Lire les conditions complètes",
        "checkbox_confirm": "Je certifie l'exactitude des informations et j'accepte les conditions",
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
        "paese_origine": "Pays d'origine",
        "regione_origine": "Région d'origine",
        "indirizzo": "Adresse",
        "quartiere": "Quartier/Village",
        "comune": "Commune/Arrondissement",
        "regione_senegal": "Région au Sénégal",
        "telefono_1": "Téléphone principal *",
        "telefono_2": "Téléphone secondaire",
        "telefono_3": "Téléphone supplémentaire",
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
        "dashboard": "Tableau de Bord",
        "area_lavoratore": "Espace Ouvrier",
        "registrazione": "Nouvelle Inscription",
        "logout": "Déconnexion",
        "benvenuto": "Bienvenue",
        "password": "Mot de passe",
        "accedi": "Accéder",
        "codice": "Code Ouvrier",
        "pin": "PIN",
        "codice_errato": "Code ou PIN incorrect",
        "i_miei_dati": "Mes Données",
        "totale_operai": "Total Ouvriers",
        "cerca": "Rechercher...",
        "lista_operai": "Liste Ouvriers",
        "nessun_risultato": "Aucun ouvrier trouvé"
    },
    "it": {
        "titolo": "🏭 PROACIER - GESTIONE OPERAI",
        "sottotitolo": "Sistema di registrazione - Senegal",
        "lingua": "Lingua",
        "step_1": "1. Dati Personali",
        "step_2": "2. Indirizzo in Senegal",
        "step_3": "3. Informazioni Professionali",
        "step_4": "4. Equipaggiamenti (EPI)",
        "step_5": "5. Informazioni Mediche",
        "step_6": "6. Contatto Emergenza & Validazione",
        "continua": "Continua →",
        "indietro": "← Indietro",
        "genera_pdf": "📄 Genera PDF & Accetta",
        "pdf_generato": "PDF generato con successo!",
        "conserva_credenziali": "⚠️ CONSERVA QUESTE CREDENZIALI",
        "codice_accesso": "Codice di accesso",
        "pin_accesso": "PIN di accesso",
        "scarica": "Scarica",
        "firma": "Far firmare al lavoratore",
        "alert_condizioni": "Cliccando questo pulsante, certifichi che tutte le informazioni fornite sono veritiere e accetti le condizioni generali.",
        "leggi_condizioni": "📋 Leggi le condizioni complete",
        "checkbox_confirm": "Certifico l'esattezza delle informazioni e accetto le condizioni",
        "errore_obbligatori": "Compila tutti i campi obbligatori (*)",
        "obbligatorio": "*",
        "cognome": "Cognome",
        "nome": "Nome",
        "data_nascita": "Data di nascita",
        "giorno": "Giorno",
        "mese": "Mese",
        "anno": "Anno",
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
        "paese_origine": "Paese di origine",
        "regione_origine": "Regione di origine",
        "indirizzo": "Indirizzo",
        "quartiere": "Quartiere/Villaggio",
        "comune": "Comune/Arrondissement",
        "regione_senegal": "Regione in Senegal",
        "telefono_1": "Telefono principale *",
        "telefono_2": "Telefono secondario",
        "telefono_3": "Telefono aggiuntivo",
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
        "dashboard": "Dashboard Azienda",
        "area_lavoratore": "Area Lavoratore",
        "registrazione": "Nuova Registrazione",
        "logout": "Esci",
        "benvenuto": "Benvenuto",
        "password": "Password",
        "accedi": "Accedi",
        "codice": "Codice Operatore",
        "pin": "PIN",
        "codice_errato": "Codice o PIN errati",
        "i_miei_dati": "I Miei Dati",
        "totale_operai": "Totale Operai",
        "cerca": "Cerca...",
        "lista_operai": "Lista Operai",
        "nessun_risultato": "Nessun operatore trovato"
    },
    "en": {
        "titolo": "🏭 PROACIER - WORKER MANAGEMENT",
        "sottotitolo": "Registration system - Senegal",
        "lingua": "Language",
        "step_1": "1. Personal Data",
        "step_2": "2. Address in Senegal",
        "step_3": "3. Professional Information",
        "step_4": "4. PPE Equipment",
        "step_5": "5. Medical Information",
        "step_6": "6. Emergency Contact & Validation",
        "continua": "Continue →",
        "indietro": "← Back",
        "genera_pdf": "📄 Generate PDF & Accept",
        "pdf_generato": "PDF generated successfully!",
        "conserva_credenziali": "⚠️ SAVE THESE CREDENTIALS",
        "codice_accesso": "Access code",
        "pin_accesso": "Access PIN",
        "scarica": "Download",
        "firma": "Have the worker sign",
        "alert_condizioni": "By clicking this button, you certify that all information provided is truthful and you accept the general conditions.",
        "leggi_condizioni": " Read full conditions",
        "checkbox_confirm": "I certify the accuracy of the information and accept the conditions",
        "errore_obbligatori": "Please fill in all required fields (*)",
        "obbligatorio": "*",
        "cognome": "Surname",
        "nome": "First Name",
        "data_nascita": "Date of birth",
        "giorno": "Day",
        "mese": "Month",
        "anno": "Year",
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
        "paese_origine": "Country of origin",
        "regione_origine": "Region of origin",
        "indirizzo": "Address",
        "quartiere": "District/Village",
        "comune": "Municipality",
        "regione_senegal": "Region in Senegal",
        "telefono_1": "Main phone *",
        "telefono_2": "Secondary phone",
        "telefono_3": "Additional phone",
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
        "dashboard": "Company Dashboard",
        "area_lavoratore": "Worker Area",
        "registrazione": "New Registration",
        "logout": "Logout",
        "benvenuto": "Welcome",
        "password": "Password",
        "accedi": "Login",
        "codice": "Worker Code",
        "pin": "PIN",
        "codice_errato": "Wrong code or PIN",
        "i_miei_dati": "My Data",
        "totale_operai": "Total Workers",
        "cerca": "Search...",
        "lista_operai": "Workers List",
        "nessun_risultato": "No worker found"
    }
}

# ============================================
# FUNZIONI
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
# PDF
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
    pdf.campo("Date naissance:", dati.get('data_nascita', ''))
    pdf.campo("Lieu:", dati.get('luogo_nascita', ''))
    pdf.campo_doppio("Nationalite:", dati.get('nazionalita', ''), "Sexe:", dati.get('sesso', ''))
    pdf.campo_doppio("Pays d'origine:", dati.get('paese_origine', ''), "Region:", dati.get('regione_origine', ''))
    pdf.campo_doppio("Etat civil:", dati.get('stato_civile', ''), "Enfants:", dati.get('figli', ''))
    if dati.get('numero_mogli', 0) > 0:
        pdf.campo("Nombre d'epouses:", dati.get('numero_mogli', ''))
    pdf.ln(3)
    
    pdf.sezione("SECTION 2 - ADRESSE AU SENEGAL")
    pdf.campo("Adresse:", f"{dati.get('indirizzo', '')} - {dati.get('quartiere', '')}")
    pdf.campo("Commune:", f"{dati.get('comune', '')} - Region: {dati.get('regione_senegal', '')}")
    pdf.campo_doppio("Telephone 1:", dati.get('telefono_1', ''), "Telephone 2:", dati.get('telefono_2', ''))
    if dati.get('telefono_3'):
        pdf.campo("Telephone 3:", dati.get('telefono_3', ''))
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
    pdf.multi_cell(0, 5, "Je soussigne(e), certifie l'exactitude des informations et accepte les conditions generales.")
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
    pdf.cell(0, 8, 'CONSENTEMENT EXPRESS', 0, 1, 'C', True)
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
# PAGINE MULTI-STEP
# ============================================

def step_1_dati_personali(lingua):
    """Step 1: Dati personali + paese di origine"""
    st.subheader(get_testo("step_1", lingua))
    
    col1, col2 = st.columns(2)
    
    with col1:
        cognome = st.text_input(f"{get_testo('cognome', lingua)} {get_testo('obbligatorio', lingua)}", key="s1_cognome")
        nome = st.text_input(f"{get_testo('nome', lingua)} {get_testo('obbligatorio', lingua)}", key="s1_nome")
        
        st.markdown(f"**{get_testo('data_nascita', lingua)}**")
        col_g, col_m, col_a = st.columns(3)
        with col_g:
            giorno = st.selectbox(get_testo("giorno", lingua), range(1, 32), index=0, key="s1_giorno")
        with col_m:
            mese = st.selectbox(get_testo("mese", lingua), range(1, 13), index=0, key="s1_mese")
        with col_a:
            anno = st.selectbox(get_testo("anno", lingua), range(1950, 2010), index=30, key="s1_anno")
        data_nascita_str = f"{giorno:02d}/{mese:02d}/{anno}"
        
        luogo_nascita = st.text_input(get_testo("luogo_nascita", lingua), key="s1_luogo")
        nazionalita = st.text_input(get_testo("nazionalita", lingua), value="Sénégalaise", key="s1_nazionalita")
    
    with col2:
        sesso = st.selectbox(get_testo("sesso", lingua), 
            [get_testo("maschile", lingua), get_testo("femminile", lingua)], 
            key="s1_sesso")
        
        stato_civile = st.selectbox(get_testo("stato_civile", lingua), [
            get_testo("celibe", lingua),
            get_testo("coniugato", lingua),
            get_testo("divorziato", lingua),
            get_testo("vedovo", lingua)
        ], key="s1_stato_civile")
        
        numero_mogli = 0
        if stato_civile == get_testo("coniugato", lingua):
            numero_mogli = st.number_input(get_testo("numero_mogli", lingua), 
                min_value=1, max_value=4, value=1, key="s1_mogli")
        
        figli = st.number_input(get_testo("figli", lingua), min_value=0, value=0, key="s1_figli")
        
        st.markdown("---")
        st.markdown("**Pays d'origine / Paese di origine**")
        paese_origine = st.selectbox(get_testo("paese_origine", lingua), 
            ["Sénégal", "Sierra Leone", "Guinea", "Mali", "Gambia", "Autre / Other"],
            index=0, key="s1_paese_origine")
        
        if paese_origine == "Sénégal":
            regione_origine = st.selectbox(get_testo("regione_origine", lingua), [
                "Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", 
                "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", 
                "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"
            ], key="s1_regione_origine")
        elif paese_origine == "Autre / Other":
            regione_origine = st.text_input("Nom du pays et région", key="s1_regione_altro")
        else:
            regione_origine_input = st.text_input(f"Région de {paese_origine}", key="s1_regione_straniera")
            regione_origine = f"{paese_origine} - {regione_origine_input}" if regione_origine_input else paese_origine
    
    return {
        "cognome": cognome,
        "nome": nome,
        "data_nascita": data_nascita_str,
        "luogo_nascita": luogo_nascita,
        "nazionalita": nazionalita,
        "sesso": sesso,
        "stato_civile": stato_civile,
        "numero_mogli": numero_mogli,
        "figli": figli,
        "paese_origine": paese_origine,
        "regione_origine": regione_origine
    }

def step_2_residenza_senegal(lingua):
    """Step 2: Residenza in Senegal + telefoni + documenti"""
    st.subheader(get_testo("step_2", lingua))
    
    col1, col2 = st.columns(2)
    
    with col1:
        indirizzo = st.text_input(f"{get_testo('indirizzo', lingua)} {get_testo('obbligatorio', lingua)}", key="s2_indirizzo")
        quartiere = st.text_input(get_testo("quartiere", lingua), key="s2_quartiere")
        comune = st.text_input(get_testo("comune", lingua), key="s2_comune")
        
        regione_senegal = st.selectbox(get_testo("regione_senegal", lingua), [
            "Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", 
            "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", 
            "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"
        ], key="s2_regione_senegal")
    
    with col2:
        telefono_1 = st.text_input(f"{get_testo('telefono_1', lingua)}", key="s2_tel1")
        telefono_2 = st.text_input(get_testo("telefono_2", lingua), key="s2_tel2")
        telefono_3 = st.text_input(get_testo("telefono_3", lingua), key="s2_tel3")
        
        cni = st.text_input(get_testo("cni", lingua), key="s2_cni")
        css = st.text_input(get_testo("css", lingua), key="s2_css")
        ipres = st.text_input(get_testo("ipres", lingua), key="s2_ipres")
    
    return {
        "indirizzo": indirizzo,
        "quartiere": quartiere,
        "comune": comune,
        "regione_senegal": regione_senegal,
        "telefono_1": telefono_1,
        "telefono_2": telefono_2,
        "telefono_3": telefono_3,
        "cni": cni,
        "css": css,
        "ipres": ipres
    }

def step_3_professionale(lingua):
    """Step 3: Informazioni professionali"""
    st.subheader(get_testo("step_3", lingua))
    
    col1, col2 = st.columns(2)
    
    with col1:
        mansione = st.text_input(get_testo("mansione", lingua), key="s3_mansione")
        luogo_lavoro = st.text_input(get_testo("luogo_lavoro", lingua), key="s3_luogo_lavoro")
        reparto = st.text_input(get_testo("reparto", lingua), key="s3_reparto")
        supervisore = st.text_input(get_testo("supervisore", lingua), key="s3_supervisore")
    
    with col2:
        st.markdown(f"**{get_testo('data_inizio', lingua)}**")
        col_g, col_m, col_a = st.columns(3)
        with col_g:
            giorno = st.selectbox(get_testo("giorno", lingua), range(1, 32), index=29, key="s3_giorno")
        with col_m:
            mese = st.selectbox(get_testo("mese", lingua), range(1, 13), index=6, key="s3_mese")
        with col_a:
            anno = st.selectbox(get_testo("anno", lingua), range(2020, 2035), index=6, key="s3_anno")
        data_inizio_str = f"{giorno:02d}/{mese:02d}/{anno}"
        
        salario = st.number_input(get_testo("salario", lingua), min_value=0, value=5000, key="s3_salario")
        ore_giorno = st.number_input(get_testo("ore_giorno", lingua), min_value=1, max_value=24, value=8, key="s3_ore")
        giorni_settimana = st.text_input(get_testo("giorni_settimana", lingua), value="Lun-Ven", key="s3_giorni")
        pagamento = st.selectbox(get_testo("pagamento", lingua), [
            get_testo("especes", lingua),
            get_testo("virement", lingua),
            get_testo("mobile", lingua)
        ], key="s3_pagamento")
    
    return {
        "mansione": mansione,
        "luogo_lavoro": luogo_lavoro,
        "reparto": reparto,
        "supervisore": supervisore,
        "data_inizio": data_inizio_str,
        "salario": salario,
        "ore_giorno": ore_giorno,
        "giorni_settimana": giorni_settimana,
        "pagamento": pagamento
    }

def step_4_epi(lingua):
    """Step 4: Taglie EPI"""
    st.subheader(get_testo("step_4", lingua))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        taglia_maglia = st.selectbox(get_testo("taglia_maglia", lingua), 
            ["XS", "S", "M", "L", "XL", "XXL", "3XL"], key="s4_maglia")
        taglia_pantaloni = st.selectbox(get_testo("taglia_pantaloni", lingua), 
            ["36", "38", "40", "42", "44", "46", "48", "50"], key="s4_pantaloni")
        taglia_scarpe = st.selectbox(get_testo("taglia_scarpe", lingua), 
            ["38", "39", "40", "41", "42", "43", "44", "45", "46"], key="s4_scarpe")
    
    with col2:
        taglia_guanti = st.selectbox(get_testo("taglia_guanti", lingua), 
            ["S", "M", "L", "XL"], key="s4_guanti")
        taglia_casco = st.selectbox(get_testo("taglia_casco", lingua), 
            ["Standard", "Ajustable"], key="s4_casco")
        taglia_gilet = st.selectbox(get_testo("taglia_gilet", lingua), 
            ["S", "M", "L", "XL", "XXL"], key="s4_gilet")
    
    return {
        "taglia_maglia": taglia_maglia,
        "taglia_pantaloni": taglia_pantaloni,
        "taglia_scarpe": taglia_scarpe,
        "taglia_guanti": taglia_guanti,
        "taglia_casco": taglia_casco,
        "taglia_gilet": taglia_gilet
    }

def step_5_medico(lingua):
    """Step 5: Informazioni mediche"""
    st.subheader(get_testo("step_5", lingua))
    
    col1, col2 = st.columns(2)
    
    with col1:
        gruppo_sanguigno = st.selectbox(get_testo("gruppo_sanguigno", lingua), 
            ["A", "B", "AB", "O"], key="s5_gruppo")
        rh = st.selectbox(get_testo("rh", lingua), ["+", "-"], key="s5_rh")
        allergie = st.text_area(get_testo("allergie", lingua), key="s5_allergie")
    
    with col2:
        malattie = st.text_area(get_testo("malattie", lingua), key="s5_malattie")
        idoneita = st.selectbox(get_testo("idoneita", lingua), [
            get_testo("apte", lingua),
            get_testo("restriction", lingua),
            get_testo("inapte", lingua)
        ], key="s5_idoneita")
        
        st.markdown(f"**{get_testo('data_visita', lingua)}**")
        col_g, col_m, col_a = st.columns(3)
        with col_g:
            giorno = st.selectbox(get_testo("giorno", lingua), range(1, 32), index=29, key="s5_giorno")
        with col_m:
            mese = st.selectbox(get_testo("mese", lingua), range(1, 13), index=6, key="s5_mese")
        with col_a:
            anno = st.selectbox(get_testo("anno", lingua), range(2020, 2035), index=6, key="s5_anno")
        data_visita_str = f"{giorno:02d}/{mese:02d}/{anno}"
    
    return {
        "gruppo_sanguigno": gruppo_sanguigno,
        "rh": rh,
        "allergie": allergie,
        "malattie": malattie,
        "idoneita": idoneita,
        "data_visita": data_visita_str
    }

def step_6_emergenza_validazione(lingua):
    """Step 6: Emergenza + accettazione condizioni"""
    st.subheader(get_testo("step_6", lingua))
    
    col1, col2 = st.columns(2)
    
    with col1:
        emergenza_nome = st.text_input(get_testo("emergenza_nome", lingua), key="s6_em_nome")
        emergenza_parentela = st.text_input(get_testo("emergenza_parentela", lingua), key="s6_em_parentela")
    
    with col2:
        emergenza_tel = st.text_input(get_testo("emergenza_tel", lingua), key="s6_em_tel")
        emergenza_indirizzo = st.text_input(get_testo("emergenza_indirizzo", lingua), key="s6_em_indirizzo")
    
    st.markdown("---")
    
    # Alert condizioni
    st.warning(get_testo("alert_condizioni", lingua))
    
    # Link alle condizioni complete
    st.markdown(f"📋 [{get_testo('leggi_condizioni', lingua)}]({URL_CONDIZIONI})")
    
    # Checkbox conferma
    conferma = st.checkbox(get_testo("checkbox_confirm", lingua), key="s6_conferma")
    
    return {
        "emergenza_nome": emergenza_nome,
        "emergenza_parentela": emergenza_parentela,
        "emergenza_tel": emergenza_tel,
        "emergenza_indirizzo": emergenza_indirizzo,
        "conferma": conferma
    }

# ============================================
# MAIN
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
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'dati_form' not in st.session_state:
        st.session_state.dati_form = {}
    
    lingua = st.session_state.lingua
    
    with st.sidebar:
        st.title(get_testo("titolo", lingua))
        st.markdown(get_testo("sottotitolo", lingua))
        st.markdown("---")
        
        lingua_sel = st.selectbox(
            get_testo("lingua", lingua),
            ["Français", "Italiano", "English"],
            index=0 if lingua == 'fr' else (1 if lingua == 'it' else 2),
            key="sel_lingua_sidebar"
        )
        st.session_state.lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
        lingua = st.session_state.lingua
        
        st.markdown("---")
        
        if st.session_state.logged_in:
            if st.session_state.user_type == 'admin':
                st.success(f"{get_testo('benvenuto', lingua)} Admin")
                if st.button(get_testo("dashboard", lingua), key="btn_dash"):
                    st.session_state.pagina = 'dashboard'
                if st.button(get_testo("logout", lingua), key="btn_logout"):
                    st.session_state.logged_in = False
                    st.session_state.pagina = 'home'
            elif st.session_state.user_type == 'lavoratore':
                st.success(f"{get_testo('benvenuto', lingua)}")
                if st.button(get_testo("i_miei_dati", lingua), key="btn_miei"):
                    st.session_state.pagina = 'area_lavoratore'
                if st.button(get_testo("logout", lingua), key="btn_logout_lav"):
                    st.session_state.logged_in = False
                    st.session_state.pagina = 'home'
        else:
            if st.button(get_testo("registrazione", lingua), key="btn_reg"):
                st.session_state.pagina = 'registrazione'
                st.session_state.step = 1
                st.session_state.dati_form = {}
            if st.button(get_testo("area_lavoratore", lingua), key="btn_area"):
                st.session_state.pagina = 'login_lavoratore'
            if st.button(get_testo("dashboard", lingua), key="btn_dash_login"):
                st.session_state.pagina = 'login_admin'
    
    # Routing
    if st.session_state.pagina == 'home':
        st.title("🏭 PROACIER SN")
        st.markdown("### Système de Gestion des Ouvriers")
        st.markdown("---")
        st.info("Utilisez le menu à gauche")
    
    elif st.session_state.pagina == 'registrazione':
        pagina_registrazione_multi_step(lingua)
    
    elif st.session_state.pagina == 'login_lavoratore':
        pagina_login_lavoratore(lingua)
    
    elif st.session_state.pagina == 'area_lavoratore':
        pagina_area_lavoratore(lingua)
    
    elif st.session_state.pagina == 'login_admin':
        pagina_login_admin(lingua)
    
    elif st.session_state.pagina == 'dashboard':
        pagina_dashboard(lingua)

def pagina_registrazione_multi_step(lingua):
    """Gestione multi-step della registrazione"""
    
    # Barra progresso
    step_corrente = st.session_state.step
    st.progress(step_corrente / 6)
    st.markdown(f"**Étape {step_corrente} sur 6**")
    st.markdown("---")
    
    # Mostra step corrente
    if step_corrente == 1:
        dati_step = step_1_dati_personali(lingua)
    elif step_corrente == 2:
        dati_step = step_2_residenza_senegal(lingua)
    elif step_corrente == 3:
        dati_step = step_3_professionale(lingua)
    elif step_corrente == 4:
        dati_step = step_4_epi(lingua)
    elif step_corrente == 5:
        dati_step = step_5_medico(lingua)
    elif step_corrente == 6:
        dati_step = step_6_emergenza_validazione(lingua)
    
    # Salva dati dello step
    st.session_state.dati_form.update(dati_step)
    
    st.markdown("---")
    
    # Pulsanti navigazione
    col1, col2 = st.columns(2)
    
    with col1:
        if step_corrente > 1:
            if st.button(get_testo("indietro", lingua), use_container_width=True):
                st.session_state.step -= 1
                st.rerun()
    
    with col2:
        if step_corrente < 6:
            if st.button(get_testo("continua", lingua), type="primary", use_container_width=True):
                # Validazione step 1
                if step_corrente == 1:
                    if not dati_step.get('cognome') or not dati_step.get('nome'):
                        st.error(get_testo("errore_obbligatori", lingua))
                        return
                # Validazione step 2
                if step_corrente == 2:
                    if not dati_step.get('indirizzo') or not dati_step.get('telefono_1'):
                        st.error(get_testo("errore_obbligatori", lingua))
                        return
                
                st.session_state.step += 1
                st.rerun()
        else:
            # Step finale - genera PDF
            if dati_step.get('conferma'):
                if st.button(get_testo("genera_pdf", lingua), type="primary", use_container_width=True):
                    genera_e_salva_pdf(st.session_state.dati_form, lingua)
            else:
                st.warning("Veuillez cocher la case de confirmation")

def genera_e_salva_pdf(dati, lingua):
    """Genera PDF e salva su Google Sheets"""
    codice = genera_codice()
    pin = genera_pin()
    
    dati_finali = {
        "id": codice,
        "codice": codice,
        "pin": pin,
        "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"),
        **dati,
        "stato_firma": "Da firmare",
        "ultimo_aggiornamento": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    if salva_su_google_sheet(dati_finali, "append"):
        st.success(f"✅ {get_testo('pdf_generato', lingua)}")
        
        pdf_bytes = genera_pdf_lavoratore(dati_finali)
        
        st.warning(get_testo('conserva_credenziali', lingua))
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**{get_testo('codice_accesso', lingua)}:** {codice}")
        with col2:
            st.info(f"**{get_testo('pin_accesso', lingua)}:** {pin}")
        
        st.download_button(
            label=f"📥 {get_testo('scarica', lingua)} PDF",
            data=pdf_bytes,
            file_name=f"Proacier_{codice}_{dati.get('cognome', '')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="btn_download_final"
        )
        
        st.success(f"ℹ️ {get_testo('firma', lingua)}")
        
        # Reset
        st.session_state.step = 1
        st.session_state.dati_form = {}
    else:
        st.error("Erreur lors de l'enregistrement.")

def pagina_login_lavoratore(lingua):
    st.title(get_testo("area_lavoratore", lingua))
    
    codice = st.text_input(get_testo("codice", lingua), key="login_codice")
    pin = st.text_input(get_testo("pin", lingua), type="password", key="login_pin")
    
    if st.button(get_testo("accedi", lingua), type="primary", key="btn_login_lav"):
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
            st.error(get_testo("codice_errato", lingua))

def pagina_area_lavoratore(lingua):
    st.title(get_testo("i_miei_dati", lingua))
    
    if not st.session_state.user_data:
        st.error("Non sei loggato")
        return
    
    st.info(f"{get_testo('benvenuto', lingua)} {st.session_state.user_data.get('nome', '')}")
    st.warning("Pour modifications, contactez l'administration")

def pagina_login_admin(lingua):
    st.title(get_testo("dashboard", lingua))
    
    password = st.text_input(get_testo("password", lingua), type="password", key="login_pwd")
    
    if st.button(get_testo("accedi", lingua), type="primary", key="btn_login_admin"):
        if password == PASSWORD_DASHBOARD:
            st.session_state.logged_in = True
            st.session_state.user_type = 'admin'
            st.session_state.pagina = 'dashboard'
            st.rerun()
        else:
            st.error("Password errata")

def pagina_dashboard(lingua):
    st.title(get_testo("dashboard", lingua))
    
    dati_lavoratori = leggi_da_google_sheet()
    
    if dati_lavoratori:
        totale = len(dati_lavoratori) - 1
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(get_testo("totale_operai", lingua), totale)
        col2.metric("Nouveaux", 0)
        col3.metric("À signer", 0)
        col4.metric("Modifications", 0)
        
        st.markdown("---")
        st.subheader(get_testo("lista_operai", lingua))
        
        import pandas as pd
        if len(dati_lavoratori) > 1:
            headers = dati_lavoratori[0]
            df = pd.DataFrame(dati_lavoratori[1:], columns=headers)
            
            cerca = st.text_input(get_testo("cerca", lingua), key="dash_cerca")
            if cerca:
                df = df[df['Cognome'].astype(str).str.contains(cerca, case=False, na=False)]
            
            colonne = ['ID', 'Cognome', 'Nome', 'Telefono_1', 'Mansione', 'Stato_Firma']
            colonne_esistenti = [c for c in colonne if c in df.columns]
            st.dataframe(df[colonne_esistenti], use_container_width=True)
        else:
            st.warning(get_testo("nessun_risultato", lingua))
    else:
        st.warning("Aucune donnée disponible")

if __name__ == "__main__":
    main()
