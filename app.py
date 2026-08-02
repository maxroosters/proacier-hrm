# -*- coding: utf-8 -*-
"""
PROACIER - Gestione Risorse Umane (HRM)
Senegal - Région de Thiès
Versione 4.0 - Definitiva con Candidature
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
    # Sidebar grigio chiaro
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #e8e8e8;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)page_title="Proacier - Ressources Humaines",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL del logo dal sito Proacier
st.sidebar.image("logo.png", use_container_width=True)

# URL Google Apps Script 1: Assunzioni Complete (Operai/Dipendenti)
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec"

# URL Google Apps Script 2: Candidature Spontanee (questo lascialo così com'è)
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycbzlc2iOHSiNSWNvU21g4GqsGwMA4QQDJXTG_J3hkfe5Za8nyeTWb1amhuR2ULFI5b9k/exec"

PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")
URL_CONDIZIONI = "https://www.proacier.sn/condizioni"

# ============================================
# TRADUZIONI
# ============================================
TRADUZIONI = {
    "fr": {
        "titolo": "🏭 PROACIER - GESTION DES RESSOURCES HUMAINES",
        "sottotitolo": "Système de Recrutement - Sénégal",
        "lingua": "Langue",
        "nuova_assunzione": "📝 Nouvelle Embauche (Complet)",
        "candidatura_spontanea": "📄 Candidature Spontanée",
        "dashboard": "Tableau de Bord",
        "area_lavoratore": "Espace Ouvrier",
        "logout": "Déconnexion",
        "benvenuto": "Bienvenue",
        "password": "Mot de passe",
        "accedi": "Accéder",
        "codice": "Code", "pin": "PIN", "codice_errato": "Code ou PIN incorrect",
        "i_miei_dati": "Mes Données", "totale_operai": "Total Employés", "cerca": "Rechercher...",
        "lista_operai": "Liste du Personnel", "nessun_risultato": "Aucun résultat trouvé",
        
        # Step Assunzione
        "step_1": "1. Données Personnelles & Famille", "step_2": "2. Adresse & Documents",
        "step_3": "3. Expérience Professionnelle", "step_4": "4. Compétences & Permis",
        "step_5": "5. Informations Médicales", "step_6": "6. Contact d'Urgence & Validation",
        "continua": "Continuer →", "indietro": "← Retour", "genera_pdf": "📄 Générer PDF & Accepter",
        "pdf_generato": "Enregistrement réussi !", "conserva_credenziali": "⚠️ CONSERVEZ CES IDENTIFIANTS",
        "codice_accesso": "Code d'accès", "pin_accesso": "PIN d'accès", "scarica": "Télécharger",
        "firma": "Faire signer au candidat", "alert_condizioni": "En cliquant, vous certifiez l'exactitude des informations et acceptez les conditions.",
        "leggi_condizioni": "📋 Lire les conditions complètes", "checkbox_confirm": "Je certifie l'exactitude des informations",
        "errore_obbligatori": "Veuillez remplir tous les champs obligatoires (*)", "obbligatorio": "*",
        "cognome": "Nom", "nome": "Prénom(s)", "data_nascita": "Date de naissance", "giorno": "Jour", "mese": "Mois", "anno": "Année",
        "luogo_nascita": "Lieu de naissance", "nazionalita": "Nationalité", "paese_origine": "Pays d'origine",
        "sesso": "Sexe", "maschile": "Masculin", "femminile": "Féminin", "stato_civile": "État civil",
        "celibe": "Célibataire", "coniugato": "Marié(e)", "divorziato": "Divorcé(e)", "vedovo": "Veuf/Veuve",
        "numero_mogli": "Nombre d'épouses", "figli_totale": "Nombre total d'enfants",
        "residenza_moglie": "Lieu de résidence de l'épouse", "figli_moglie": "Nombre d'enfants avec cette épouse",
        "indirizzo": "Adresse actuelle", "quartiere": "Quartier/Village", "comune": "Commune",
        "regione_senegal": "Région", "telefono_1": "Téléphone principal *", "telefono_2": "Téléphone secondaire", "telefono_3": "Téléphone 3",
        "cni": "N° CNI *", "nif": "NIF", "css": "N° CSS *", "cmu": "N° CMU", "ipres": "N° IPRES",
        "nota_lavoro": "Indiquez vos 3 dernières expériences.",
        "azienda": "Entreprise", "mansione": "Fonction", "data_inizio": "Début", "data_fine": "Fin", "motivo_uscita": "Motif de départ",
        "nota_competenze": "Indiquez vos compétences principales.",
        "categoria_competenza": "Catégorie de compétence", "dettaglio_competenza": "Détails / Nozioni acquisite",
        "patente": "Permis de conduire", "nota_patente": "⚠️ Une photocopie du permis sera exigée.",
        "gruppo_sanguigno": "Groupe sanguin", "rh": "Rh", "allergie": "Allergies", "malattie": "Maladies chroniques",
        "idoneita": "Aptitude médicale", "apte": "Apte", "restriction": "Apte avec restriction", "inapte": "Inapte", "data_visita": "Date visite",
        "emergenza_nome": "Contact urgence (Nom)", "emergenza_parentela": "Lien", "emergenza_tel": "Tél urgence", "emergenza_indirizzo": "Adresse urgence",
        "cat_edilizia": "Bâtiment", "cat_contabilita": "Comptabilité", "cat_meccanica": "Mécanique", "cat_elettrico": "Électricité", "cat_agricoltura": "Agriculture", "cat_altro": "Autre",

        # Candidatura Spontanea
        "titolo_candidatura": "CANDIDATURE SPONTANÉE",
        "sottotitolo_candidatura": "Rejoignez l'équipe PROACIER. Remplissez ce formulaire rapide.",
        "email": "Adresse Email *",
        "mansione_richiesta": "Poste recherché",
        "opt_contabile": "Comptabilité / Admin", "opt_tecnico": "Technicien", "opt_operaio": "Ouvrier", "opt_autista": "Chauffeur", "opt_altro": "Autre",
        "studi": "Niveau d'études",
        "opt_media": "École moyenne", "opt_diploma": "Baccalauréat / Diplôme", "opt_laurea": "Université / Licence", "opt_prof": "Formation professionnelle",
        "skills": "Compétences / Skills",
        "esperienza_anno": "Années d'expérience",
        "salario_richiesto": "Prétention salariale (FCFA)",
        "note": "Notes supplémentaires",
        "invia_candidatura": "📤 Envoyer ma candidature",
        "candidatura_inviata": "✅ Candidature envoyée avec succès ! Nous vous contacterons bientôt.",
        "errore_candidatura": "Veuillez remplir Nom, Prénom, Email et Téléphone."
    },
    "it": {
        "titolo": "🏭 PROACIER - GESTIONE RISORSE UMANE",
        "sottotitolo": "Sistema di Reclutamento - Senegal",
        "lingua": "Lingua",
        "nuova_assunzione": "📝 Nuova Assunzione (Completo)",
        "candidatura_spontanea": "📄 Candidatura Spontanea",
        "dashboard": "Dashboard Azienda",
        "area_lavoratore": "Area Lavoratore",
        "logout": "Esci",
        "benvenuto": "Benvenuto",
        "password": "Password",
        "accedi": "Accedi",
        "codice": "Codice", "pin": "PIN", "codice_errato": "Codice o PIN errati",
        "i_miei_dati": "I Miei Dati", "totale_operai": "Totale Dipendenti", "cerca": "Cerca...",
        "lista_operai": "Lista Personale", "nessun_risultato": "Nessun risultato trovato",
        
        "step_1": "1. Dati Personali e Famiglia", "step_2": "2. Indirizzo e Documenti",
        "step_3": "3. Esperienza Professionale", "step_4": "4. Competenze e Patente",
        "step_5": "5. Informazioni Mediche", "step_6": "6. Contatto Emergenza e Validazione",
        "continua": "Continua →", "indietro": "← Indietro", "genera_pdf": "📄 Genera PDF e Accetta",
        "pdf_generato": "Registrazione riuscita!", "conserva_credenziali": "⚠️ CONSERVA QUESTE CREDENZIALI",
        "codice_accesso": "Codice di accesso", "pin_accesso": "PIN di accesso", "scarica": "Scarica",
        "firma": "Far firmare al candidato", "alert_condizioni": "Cliccando, certifichi l'esattezza delle informazioni e accetti le condizioni.",
        "leggi_condizioni": "📋 Leggi le condizioni complete", "checkbox_confirm": "Certifico l'esattezza delle informazioni",
        "errore_obbligatori": "Compila tutti i campi obbligatori (*)", "obbligatorio": "*",
        "cognome": "Cognome", "nome": "Nome", "data_nascita": "Data di nascita", "giorno": "Giorno", "mese": "Mese", "anno": "Anno",
        "luogo_nascita": "Luogo di nascita", "nazionalita": "Nazionalità", "paese_origine": "Paese di origine",
        "sesso": "Sesso", "maschile": "Maschile", "femminile": "Femminile", "stato_civile": "Stato civile",
        "celibe": "Celibe/Nubile", "coniugato": "Coniugato/a", "divorziato": "Divorziato/a", "vedovo": "Vedovo/a",
        "numero_mogli": "Numero di mogli", "figli_totale": "Numero totale di figli",
        "residenza_moglie": "Luogo di residenza della moglie", "figli_moglie": "Numero di figli con questa moglie",
        "indirizzo": "Indirizzo attuale", "quartiere": "Quartiere/Villaggio", "comune": "Comune",
        "regione_senegal": "Regione", "telefono_1": "Telefono principale *", "telefono_2": "Telefono secondario", "telefono_3": "Telefono 3",
        "cni": "N° CNI *", "nif": "NIF", "css": "N° CSS *", "cmu": "N° CMU", "ipres": "N° IPRES",
        "nota_lavoro": "Indica le tue ultime 3 esperienze.",
        "azienda": "Azienda", "mansione": "Mansione", "data_inizio": "Inizio", "data_fine": "Fine", "motivo_uscita": "Motivo uscita",
        "nota_competenze": "Indica le tue competenze principali.",
        "categoria_competenza": "Categoria di competenza", "dettaglio_competenza": "Dettagli / Nozioni acquisite",
        "patente": "Patente di guida", "nota_patente": "⚠️ Sarà richiesta una fotocopia della patente.",
        "gruppo_sanguigno": "Gruppo sanguigno", "rh": "Rh", "allergie": "Allergie", "malattie": "Malattie croniche",
        "idoneita": "Idoneità medica", "apte": "Apto", "restriction": "Apto con restrizioni", "inapte": "Inapto", "data_visita": "Data visita",
        "emergenza_nome": "Contatto emergenza (Nome)", "emergenza_parentela": "Parentela", "emergenza_tel": "Tel emergenza", "emergenza_indirizzo": "Indirizzo emergenza",
        "cat_edilizia": "Edilizia", "cat_contabilita": "Contabilità", "cat_meccanica": "Meccanica", "cat_elettrico": "Elettrico", "cat_agricoltura": "Agricoltura", "cat_altro": "Altro",

        "titolo_candidatura": "CANDIDATURA SPONTANEA",
        "sottotitolo_candidatura": "Unisciti al team PROACIER. Compila questo modulo rapido.",
        "email": "Indirizzo Email *",
        "mansione_richiesta": "Ruolo richiesto",
        "opt_contabile": "Contabilità / Admin", "opt_tecnico": "Tecnico", "opt_operaio": "Operaio", "opt_autista": "Autista", "opt_altro": "Altro",
        "studi": "Titolo di studio",
        "opt_media": "Licenza media", "opt_diploma": "Diploma", "opt_laurea": "Laurea", "opt_prof": "Formazione professionale",
        "skills": "Competenze / Skills",
        "esperienza_anno": "Anni di esperienza",
        "salario_richiesto": "Retribuzione richiesta (FCFA)",
        "note": "Note aggiuntive",
        "invia_candidatura": "📤 Invia la mia candidatura",
        "candidatura_inviata": "✅ Candidatura inviata con successo! Ti contatteremo presto.",
        "errore_candidatura": "Compila Cognome, Nome, Email e Telefono."
    },
    "en": {
        "titolo": "🏭 PROACIER - HUMAN RESOURCES MANAGEMENT",
        "sottotitolo": "Recruitment System - Senegal",
        "lingua": "Language",
        "nuova_assunzione": "📝 New Hiring (Complete)",
        "candidatura_spontanea": "📄 Spontaneous Application",
        "dashboard": "Company Dashboard",
        "area_lavoratore": "Worker Area",
        "logout": "Logout",
        "benvenuto": "Welcome",
        "password": "Password",
        "accedi": "Login",
        "codice": "Code", "pin": "PIN", "codice_errato": "Wrong code or PIN",
        "i_miei_dati": "My Data", "totale_operai": "Total Employees", "cerca": "Search...",
        "lista_operai": "Staff List", "nessun_risultato": "No results found",
        
        "step_1": "1. Personal Data & Family", "step_2": "2. Address & Documents",
        "step_3": "3. Professional Experience", "step_4": "4. Skills & License",
        "step_5": "5. Medical Information", "step_6": "6. Emergency Contact & Validation",
        "continua": "Continue →", "indietro": "← Back", "genera_pdf": "📄 Generate PDF & Accept",
        "pdf_generato": "Registration successful!", "conserva_credenziali": "⚠️ SAVE THESE CREDENTIALS",
        "codice_accesso": "Access code", "pin_accesso": "Access PIN", "scarica": "Download",
        "firma": "Have the candidate sign", "alert_condizioni": "By clicking, you certify the accuracy of the information and accept the conditions.",
        "leggi_condizioni": "📋 Read full conditions", "checkbox_confirm": "I certify the accuracy of the information",
        "errore_obbligatori": "Please fill in all required fields (*)", "obbligatorio": "*",
        "cognome": "Surname", "nome": "First Name", "data_nascita": "Date of birth", "giorno": "Day", "mese": "Month", "anno": "Year",
        "luogo_nascita": "Place of birth", "nazionalita": "Nationality", "paese_origine": "Country of origin",
        "sesso": "Gender", "maschile": "Male", "femminile": "Female", "stato_civile": "Marital status",
        "celibe": "Single", "coniugato": "Married", "divorziato": "Divorced", "vedovo": "Widowed",
        "numero_mogli": "Number of wives", "figli_totale": "Total number of children",
        "residenza_moglie": "Wife's residence", "figli_moglie": "Children with this wife",
        "indirizzo": "Current address", "quartiere": "District/Village", "comune": "Municipality",
        "regione_senegal": "Region", "telefono_1": "Main phone *", "telefono_2": "Secondary phone", "telefono_3": "Phone 3",
        "cni": "ID Number (CNI) *", "nif": "NIF", "css": "Social Security (CSS) *", "cmu": "CMU", "ipres": "IPRES",
        "nota_lavoro": "Indicate your last 3 experiences.",
        "azienda": "Company", "mansione": "Position", "data_inizio": "Start", "data_fine": "End", "motivo_uscita": "Reason for leaving",
        "nota_competenze": "Indicate your main skills.",
        "categoria_competenza": "Skill category", "dettaglio_competenza": "Details / Acquired knowledge",
        "patente": "Driver's license", "nota_patente": "⚠️ A photocopy of the license will be required.",
        "gruppo_sanguigno": "Blood type", "rh": "Rh", "allergie": "Allergies", "malattie": "Chronic diseases",
        "idoneita": "Medical fitness", "apte": "Fit", "restriction": "Fit with restrictions", "inapte": "Unfit", "data_visita": "Visit date",
        "emergenza_nome": "Emergency contact (Name)", "emergenza_parentela": "Relationship", "emergenza_tel": "Emergency phone", "emergenza_indirizzo": "Emergency address",
        "cat_edilizia": "Construction", "cat_contabilita": "Accounting", "cat_meccanica": "Mechanics", "cat_elettrico": "Electrical", "cat_agricoltura": "Agriculture", "cat_altro": "Other",

        "titolo_candidatura": "SPONTANEOUS APPLICATION",
        "sottotitolo_candidatura": "Join the PROACIER team. Fill out this quick form.",
        "email": "Email Address *",
        "mansione_richiesta": "Desired position",
        "opt_contabile": "Accounting / Admin", "opt_tecnico": "Technician", "opt_operaio": "Worker", "opt_autista": "Driver", "opt_altro": "Other",
        "studi": "Education level",
        "opt_media": "Middle school", "opt_diploma": "High school / Diploma", "opt_laurea": "University / Degree", "opt_prof": "Vocational training",
        "skills": "Skills / Competencies",
        "esperienza_anno": "Years of experience",
        "salario_richiesto": "Expected salary (FCFA)",
        "note": "Additional notes",
        "invia_candidatura": "📤 Submit my application",
        "candidatura_inviata": "✅ Application submitted successfully! We will contact you soon.",
        "errore_candidatura": "Please fill in Surname, First Name, Email, and Phone."
    }
}

# ============================================
# FUNZIONI DI SUPPORTO
# ============================================
def get_testo(chiave, lingua="fr"):
    return TRADUZIONI.get(lingua, TRADUZIONI["fr"]).get(chiave, chiave)

def genera_codice():
    return f"THS-{datetime.now().year}-{random.randint(1000, 9999)}"

def genera_pin():
    return str(random.randint(1000, 9999))

def salva_su_google_sheet(dati, url_script, azione="append"):
    try:
        payload = {"row": dati} if azione == "append" else {"id": dati.get("id"), "updates": dati}
        response = requests.post(url_script, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Errore connessione: {e}")
        return False

def leggi_da_google_sheet(url_script):
    try:
        response = requests.get(f"{url_script}?action=read", timeout=30)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Errore lettura: {e}")
        return []

# ============================================
# GENERATORE PDF (Assunzioni)
# ============================================
class PDFProacier(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(68, 114, 196)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FICHE D\'ENREGISTREMENT - RESSOURCES HUMAINES', 0, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def sezione(self, titolo):
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(217, 225, 242)
        self.cell(0, 6, titolo, 0, 1, 'C', True)
        self.ln(1)

    def campo(self, etichetta, valore):
        self.set_font('Helvetica', 'B', 8)
        self.cell(60, 5, etichetta, 0, 0)
        self.set_font('Helvetica', '', 8)
        self.cell(0, 5, str(valore) if valore else "___________", 0, 1)

    def campo_doppio(self, et1, val1, et2, val2):
        self.set_font('Helvetica', 'B', 8)
        self.cell(50, 5, et1, 0, 0)
        self.set_font('Helvetica', '', 8)
        self.cell(45, 5, str(val1) if val1 else "______", 0, 0)
        self.set_font('Helvetica', 'B', 8)
        self.cell(50, 5, et2, 0, 0)
        self.set_font('Helvetica', '', 8)
        self.cell(0, 5, str(val2) if val2 else "______", 0, 1)

def genera_pdf_lavoratore(dati):
    pdf = PDFProacier()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 5, f"N° fiche: {dati.get('codice', '')}", 0, 0)
    pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.ln(2)
    
    pdf.sezione("1. IDENTITE & FAMILLE")
    pdf.campo_doppio("Nom:", dati.get('cognome', ''), "Prenom(s):", dati.get('nome', ''))
    pdf.campo_doppio("Ne(e) le:", dati.get('data_nascita', ''), "a:", dati.get('luogo_nascita', ''))
    pdf.campo_doppio("Nationalite:", dati.get('nazionalita', ''), "Pays d'origine:", dati.get('paese_origine', ''))
    pdf.campo_doppio("Etat civil:", dati.get('stato_civile', ''), "Enfants total:", dati.get('figli_totale', ''))
    if dati.get('numero_mogli', 0) > 0:
        pdf.campo("Epouses:", f"{dati.get('numero_mogli')} (Details: {dati.get('dettagli_mogli', '')})")
    pdf.ln(1)
    
    pdf.sezione("2. CONTACT & DOCUMENTS")
    pdf.campo("Adresse:", f"{dati.get('indirizzo', '')}, {dati.get('quartiere', '')}, {dati.get('regione_senegal', '')}")
    pdf.campo_doppio("Tel 1:", dati.get('telefono_1', ''), "Tel 2:", dati.get('telefono_2', ''))
    pdf.campo_doppio("CNI:", dati.get('cni', ''), "NIF:", dati.get('nif', ''))
    pdf.campo_doppio("CSS:", dati.get('css', ''), "CMU:", dati.get('cmu', ''))
    pdf.ln(1)

    pdf.sezione("3. EXPERIENCE & COMPETENCES")
    pdf.campo("Dernier emploi:", f"{dati.get('mansione_1', '')} chez {dati.get('azienda_1', '')}")
    pdf.campo("Competence:", f"{dati.get('categoria_competenza', '')} - {dati.get('dettaglio_competenza', '')}")
    pdf.campo("Permis:", dati.get('patente', ''))
    pdf.ln(1)

    pdf.sezione("4. MEDICAL & URGENCE")
    pdf.campo_doppio("Groupe:", f"{dati.get('gruppo_sanguigno', '')} {dati.get('rh', '')}", "Aptitude:", dati.get('idoneita', ''))
    pdf.campo_doppio("Contact:", dati.get('emergenza_nome', ''), "Tel:", dati.get('emergenza_tel', ''))
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.multi_cell(0, 4, "Je certifie l'exactitude des informations et accepte les conditions de recrutement.")
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 6, 'CANDIDAT', 1, 0, 'C')
    pdf.cell(95, 6, 'EMPLOYEUR', 1, 1, 'C')
    pdf.cell(95, 15, '', 1, 0)
    pdf.cell(95, 15, '', 1, 1)
        
    # CODICI DI ACCESSO
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
    
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'CONSENTEMENT DONNEES PERSONNELLES', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 9)
    pdf.multi_cell(0, 5, "Conformement a la Loi n° 2008-12 du 25 janvier 2008 (Senegal).")
    pdf.ln(10)
    pdf.cell(0, 6, 'Signature:', 0, 1)
    pdf.cell(0, 20, '', 1, 1)
    
    # Genera PDF in formato bytes
    pdf_bytes = pdf.output(dest='S')
    
    # Converti in bytes se è stringa
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1', errors='replace')
    
    # Se è già bytes, restituisci direttamente
    return bytes(pdf_bytes)

# ============================================
# STEP DEL FORMULARIO (ASSUNZIONI)
# ============================================
def step_1_personale_famiglia(lingua):
    st.subheader(get_testo("step_1", lingua))
    col1, col2 = st.columns(2)
    with col1:
        cognome = st.text_input(f"{get_testo('cognome', lingua)} {get_testo('obbligatorio', lingua)}", key="s1_cognome")
        nome = st.text_input(f"{get_testo('nome', lingua)} {get_testo('obbligatorio', lingua)}", key="s1_nome")
        st.markdown(f"**{get_testo('data_nascita', lingua)}**")
        cg, cm, ca = st.columns(3)
        with cg: giorno = st.selectbox(get_testo("giorno", lingua), range(1, 32), index=0, key="s1_g")
        with cm: mese = st.selectbox(get_testo("mese", lingua), range(1, 13), index=0, key="s1_m")
        with ca: anno = st.selectbox(get_testo("anno", lingua), range(1950, 2010), index=30, key="s1_a")
        data_nascita_str = f"{giorno:02d}/{mese:02d}/{anno}"
        luogo_nascita = st.text_input(get_testo("luogo_nascita", lingua), key="s1_luogo")
        nazionalita = st.text_input(get_testo("nazionalita", lingua), value="Sénégalaise", key="s1_naz")
        paese_origine = st.text_input(get_testo("paese_origine", lingua), value="Sénégal", key="s1_paese_origine")
    with col2:
        sesso = st.selectbox(get_testo("sesso", lingua), [get_testo("maschile", lingua), get_testo("femminile", lingua)], key="s1_sesso")
        stato_civile = st.selectbox(get_testo("stato_civile", lingua), [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)], key="s1_stato")
        numero_mogli, dettagli_mogli = 0, ""
        if stato_civile == get_testo("coniugato", lingua):
            numero_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=1, key="s1_mogli")
            dettagli = []
            for i in range(1, numero_mogli + 1):
                st.markdown(f"**Épouse {i}**")
                c_res, c_fig = st.columns(2)
                with c_res: res = st.text_input(get_testo("residenza_moglie", lingua) + f" {i}", key=f"s1_res_{i}")
                with c_fig: fig = st.number_input(get_testo("figli_moglie", lingua) + f" {i}", min_value=0, value=0, key=f"s1_fig_{i}")
                dettagli.append(f"Épouse {i}: {res} ({fig} enfants)")
            dettagli_mogli = " | ".join(dettagli)
        figli_totale = st.number_input(get_testo("figli_totale", lingua), min_value=0, value=0, key="s1_figli_tot")
    return {"cognome": cognome, "nome": nome, "data_nascita": data_nascita_str, "luogo_nascita": luogo_nascita, 
            "nazionalita": nazionalita, "paese_origine": paese_origine, "sesso": sesso, "stato_civile": stato_civile, 
            "numero_mogli": numero_mogli, "dettagli_mogli": dettagli_mogli, "figli_totale": figli_totale}

def step_2_residenza_documenti(lingua):
    st.subheader(get_testo("step_2", lingua))
    col1, col2 = st.columns(2)
    with col1:
        indirizzo = st.text_input(f"{get_testo('indirizzo', lingua)} {get_testo('obbligatorio', lingua)}", key="s2_ind")
        quartiere = st.text_input(get_testo("quartiere", lingua), key="s2_quart")
        comune = st.text_input(get_testo("comune", lingua), key="s2_com")
        regione_senegal = st.selectbox(get_testo("regione_senegal", lingua), ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"], key="s2_reg")
    with col2:
        tel1 = st.text_input(f"{get_testo('telefono_1', lingua)}", key="s2_tel1")
        tel2 = st.text_input(get_testo("telefono_2", lingua), key="s2_tel2")
        tel3 = st.text_input(get_testo("telefono_3", lingua), key="s2_tel3")
        cni = st.text_input(f"{get_testo('cni', lingua)}", key="s2_cni")
        nif = st.text_input(get_testo("nif", lingua), key="s2_nif")
        css = st.text_input(f"{get_testo('css', lingua)}", key="s2_css")
        cmu = st.text_input(get_testo("cmu", lingua), key="s2_cmu")
        ipres = st.text_input(get_testo("ipres", lingua), key="s2_ipres")
    return {"indirizzo": indirizzo, "quartiere": quartiere, "comune": comune, "regione_senegal": regione_senegal,
            "telefono_1": tel1, "telefono_2": tel2, "telefono_3": tel3, "cni": cni, "nif": nif, "css": css, "cmu": cmu, "ipres": ipres}

def step_3_esperienza(lingua):
    st.subheader(get_testo("step_3", lingua))
    st.info(get_testo("nota_lavoro", lingua))
    dati_lavori = {}
    for i in range(1, 4):
        st.markdown(f"**Emploi précédent {i}**")
        c1, c2 = st.columns(2)
        with c1:
            dati_lavori[f"azienda_{i}"] = st.text_input(get_testo("azienda", lingua), key=f"s3_az_{i}")
            dati_lavori[f"mansione_{i}"] = st.text_input(get_testo("mansione", lingua), key=f"s3_man_{i}")
        with c2:
            dati_lavori[f"data_inizio_{i}"] = st.text_input(get_testo("data_inizio", lingua) + " (MM/AAAA)", key=f"s3_di_{i}")
            dati_lavori[f"data_fine_{i}"] = st.text_input(get_testo("data_fine", lingua) + " (MM/AAAA)", key=f"s3_df_{i}")
        dati_lavori[f"motivo_uscita_{i}"] = st.text_input(get_testo("motivo_uscita", lingua), key=f"s3_mu_{i}")
        st.markdown("---")
    return dati_lavori

def step_4_competenze_permesso(lingua):
    st.subheader(get_testo("step_4", lingua))
    st.info(get_testo("nota_competenze", lingua))
    cat_options = [get_testo("cat_edilizia", lingua), get_testo("cat_contabilita", lingua), get_testo("cat_meccanica", lingua), get_testo("cat_elettrico", lingua), get_testo("cat_agricoltura", lingua), get_testo("cat_altro", lingua)]
    categoria = st.selectbox(get_testo("categoria_competenza", lingua), cat_options, key="s4_cat")
    dettaglio = st.text_area(get_testo("dettaglio_competenza", lingua), key="s4_det")
    st.markdown("---")
    patente = st.text_input(get_testo("patente", lingua), key="s4_pat")
    st.caption(get_testo("nota_patente", lingua))
    return {"categoria_competenza": categoria, "dettaglio_competenza": dettaglio, "patente": patente}

def step_5_medico(lingua):
    st.subheader(get_testo("step_5", lingua))
    col1, col2 = st.columns(2)
    with col1:
        gruppo = st.selectbox(get_testo("gruppo_sanguigno", lingua), ["A", "B", "AB", "O"], key="s5_gruppo")
        rh = st.selectbox(get_testo("rh", lingua), ["+", "-"], key="s5_rh")
        allergie = st.text_area(get_testo("allergie", lingua), key="s5_all")
    with col2:
        malattie = st.text_area(get_testo("malattie", lingua), key="s5_mal")
        idoneita = st.selectbox(get_testo("idoneita", lingua), [get_testo("apte", lingua), get_testo("restriction", lingua), get_testo("inapte", lingua)], key="s5_ido")
        data_visita = st.text_input(get_testo("data_visita", lingua) + " (GG/MM/AAAA)", key="s5_data")
    return {"gruppo_sanguigno": gruppo, "rh": rh, "allergie": allergie, "malattie": malattie, "idoneita": idoneita, "data_visita": data_visita}

def step_6_emergenza_validazione(lingua):
    st.subheader(get_testo("step_6", lingua))
    col1, col2 = st.columns(2)
    with col1:
        em_nome = st.text_input(get_testo("emergenza_nome", lingua), key="s6_em_nome")
        em_parentela = st.text_input(get_testo("emergenza_parentela", lingua), key="s6_em_par")
    with col2:
        em_tel = st.text_input(get_testo("emergenza_tel", lingua), key="s6_em_tel")
        em_ind = st.text_input(get_testo("emergenza_indirizzo", lingua), key="s6_em_ind")
    st.markdown("---")
    st.warning(get_testo("alert_condizioni", lingua))
    st.markdown(f"[{get_testo('leggi_condizioni', lingua)}]({URL_CONDIZIONI})")
    conferma = st.checkbox(get_testo("checkbox_confirm", lingua), key="s6_conf")
    return {"emergenza_nome": em_nome, "emergenza_parentela": em_parentela, "emergenza_tel": em_tel, "emergenza_indirizzo": em_ind, "conferma": conferma}

# ============================================
# PAGINA CANDIDATURA SPONTANEA
# ============================================
def pagina_candidatura_spontanea(lingua):
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.markdown("---")
    
    with st.form("form_candidatura", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            c_cognome = st.text_input(f"{get_testo('cognome', lingua)} {get_testo('obbligatorio', lingua)}", key="c_cognome")
            c_nome = st.text_input(f"{get_testo('nome', lingua)} {get_testo('obbligatorio', lingua)}", key="c_nome")
            c_email = st.text_input(f"{get_testo('email', lingua)}", key="c_email")
            c_tel = st.text_input(f"{get_testo('telefono_1', lingua)}", key="c_tel")
            
            st.markdown(f"**{get_testo('data_nascita', lingua)}**")
            cg, cm, ca = st.columns(3)
            with cg: g = st.selectbox(get_testo("giorno", lingua), range(1, 32), index=0, key="c_g")
            with cm: m = st.selectbox(get_testo("mese", lingua), range(1, 13), index=0, key="c_m")
            with ca: a = st.selectbox(get_testo("anno", lingua), range(1960, 2010), index=30, key="c_a")
            c_data_nascita = f"{g:02d}/{m:02d}/{a}"
            
        with col2:
            c_indirizzo = st.text_input(get_testo("indirizzo", lingua), key="c_ind")
            c_comune = st.text_input(get_testo("comune", lingua), key="c_com")
            c_regione = st.selectbox(get_testo("regione_senegal", lingua), ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"], key="c_reg")
            
            c_mansione = st.selectbox(get_testo("mansione_richiesta", lingua), [
                get_testo("opt_contabile", lingua), get_testo("opt_tecnico", lingua), 
                get_testo("opt_operaio", lingua), get_testo("opt_autista", lingua), get_testo("opt_altro", lingua)
            ], key="c_man")
            
            c_studi = st.selectbox(get_testo("studi", lingua), [
                get_testo("opt_media", lingua), get_testo("opt_diploma", lingua), 
                get_testo("opt_laurea", lingua), get_testo("opt_prof", lingua)
            ], key="c_studi")
            
        c_skills = st.text_area(get_testo("skills", lingua), key="c_skills")
        
        col3, col4 = st.columns(2)
        with col3:
            c_esperienza = st.number_input(get_testo("esperienza_anno", lingua), min_value=0, max_value=50, value=0, key="c_exp")
        with col4:
            c_salario = st.text_input(get_testo("salario_richiesto", lingua), key="c_sal")
            
        c_note = st.text_area(get_testo("note", lingua), key="c_note")
        
        submitted = st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True)
        
        if submitted:
            if not c_cognome or not c_nome or not c_email or not c_tel:
                st.error(get_testo("errore_candidatura", lingua))
                return
            
            dati_candidatura = {
                "id": f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}",
                "data_candidatura": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cognome": c_cognome, "nome": c_nome, "email": c_email, "telefono": c_tel,
                "data_nascita": c_data_nascita, "indirizzo": c_indirizzo, "comune": c_comune, "regione": c_regione,
                "mansione_richiesta": c_mansione, "studi": c_studi, "skills": c_skills,
                "esperienza_anno": c_esperienza, "salario_richiesto": c_salario, "note": c_note, "stato": "Nuova"
            }
            
            if salva_su_google_sheet(dati_candidatura, GOOGLE_SCRIPT_URL_CANDIDATURE, "append"):
                st.success(get_testo("candidatura_inviata", lingua))
            else:
                st.error("Erreur de connexion. Veuillez réessayer.")

# ============================================
# MAIN APP
# ============================================
def main():
    if 'lingua' not in st.session_state: st.session_state.lingua = 'fr'
    if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_type' not in st.session_state: st.session_state.user_type = None
    if 'step' not in st.session_state: st.session_state.step = 1
    if 'dati_form' not in st.session_state: st.session_state.dati_form = {}
    
    lingua = st.session_state.lingua
    
    with st.sidebar:
        # st.image(LOGO_URL, use_column_width=True)
        st.markdown("---")
        st.title(get_testo("titolo", lingua))
        st.markdown(get_testo("sottotitolo", lingua))
        st.markdown("---")
        
        lingua_sel = st.selectbox(get_testo("lingua", lingua), ["Français", "Italiano", "English"], index=0 if lingua == 'fr' else (1 if lingua == 'it' else 2), key="sel_lingua_sidebar")
        st.session_state.lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
        lingua = st.session_state.lingua
        st.markdown("---")
        
        if st.session_state.logged_in:
            st.success(f"{get_testo('benvenuto', lingua)}")
            if st.session_state.user_type == 'admin' and st.button(get_testo("dashboard", lingua), key="btn_dash"): 
                st.session_state.pagina = 'dashboard'
            if st.session_state.user_type == 'lavoratore' and st.button(get_testo("i_miei_dati", lingua), key="btn_miei"): 
                st.session_state.pagina = 'area_lavoratore'
            if st.button(get_testo("logout", lingua), key="btn_logout"): 
                st.session_state.logged_in = False
                st.session_state.pagina = 'home'
        else:
            if st.button(get_testo("nuova_assunzione", lingua), key="btn_reg"): 
                st.session_state.pagina = 'registrazione'
                st.session_state.step = 1
                st.session_state.dati_form = {}
            if st.button(get_testo("candidatura_spontanea", lingua), key="btn_cand"): 
                st.session_state.pagina = 'candidatura'
            if st.button(get_testo("area_lavoratore", lingua), key="btn_area"): 
                st.session_state.pagina = 'login_lavoratore'
            if st.button(get_testo("dashboard", lingua), key="btn_dash_login"): 
                st.session_state.pagina = 'login_admin'

    if st.session_state.pagina == 'home':
        st.title("🏭 PROACIER SN"); st.markdown("### Système de Gestion des Ressources Humaines"); st.info("Utilisez le menu à gauche")
    elif st.session_state.pagina == 'registrazione':
        pagina_registrazione_multi_step(lingua)
    elif st.session_state.pagina == 'candidatura':
        pagina_candidatura_spontanea(lingua)
    elif st.session_state.pagina == 'login_lavoratore':
        codice = st.text_input(get_testo("codice", lingua), key="login_codice")
        pin = st.text_input(get_testo("pin", lingua), type="password", key="login_pin")
        if st.button(get_testo("accedi", lingua), type="primary", key="btn_login_lav"):
            dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            trovato = any(len(row) >= 3 and str(row[1]) == codice and str(row[2]) == pin for row in dati[1:])
            if trovato:
                st.session_state.logged_in = True; st.session_state.user_type = 'lavoratore'; st.session_state.pagina = 'area_lavoratore'; st.rerun()
            else: st.error(get_testo("codice_errato", lingua))
    elif st.session_state.pagina == 'area_lavoratore':
        st.title(get_testo("i_miei_dati", lingua)); st.warning("Pour modifications, contactez l'administration")
    elif st.session_state.pagina == 'login_admin':
        pwd = st.text_input(get_testo("password", lingua), type="password", key="login_pwd")
        if st.button(get_testo("accedi", lingua), type="primary", key="btn_login_admin"):
            if pwd == PASSWORD_DASHBOARD: st.session_state.logged_in = True; st.session_state.user_type = 'admin'; st.session_state.pagina = 'dashboard'; st.rerun()
            else: st.error("Password errata")
    elif st.session_state.pagina == 'dashboard':
        st.title(get_testo("dashboard", lingua))
        dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if dati and len(dati) > 1:
            import pandas as pd
            df = pd.DataFrame(dati[1:], columns=dati[0])
            st.metric(get_testo("totale_operai", lingua), len(df))
            st.dataframe(df[['ID', 'Cognome', 'Nome', 'Telefono_1', 'Mansione_1', 'Stato_Firma']], use_container_width=True)
        else: st.warning(get_testo("nessun_risultato", lingua))

def pagina_registrazione_multi_step(lingua):
    step = st.session_state.step
    st.progress(step / 6)
    st.markdown(f"**Étape {step} sur 6**")
    st.markdown("---")
    
    if step == 1: dati_step = step_1_personale_famiglia(lingua)
    elif step == 2: dati_step = step_2_residenza_documenti(lingua)
    elif step == 3: dati_step = step_3_esperienza(lingua)
    elif step == 4: dati_step = step_4_competenze_permesso(lingua)
    elif step == 5: dati_step = step_5_medico(lingua)
    elif step == 6: dati_step = step_6_emergenza_validazione(lingua)
    
    st.session_state.dati_form.update(dati_step)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if step > 1 and st.button(get_testo("indietro", lingua), use_container_width=True):
            st.session_state.step -= 1; st.rerun()
    with col2:
        if step < 6:
            if st.button(get_testo("continua", lingua), type="primary", use_container_width=True):
                if step == 1 and (not dati_step.get('cognome') or not dati_step.get('nome')): st.error(get_testo("errore_obbligatori", lingua)); return
                if step == 2 and (not dati_step.get('cni') or not dati_step.get('telefono_1')): st.error(get_testo("errore_obbligatori", lingua)); return
                st.session_state.step += 1; st.rerun()
        else:
            if dati_step.get('conferma'):
                if st.button(get_testo("genera_pdf", lingua), type="primary", use_container_width=True):
                    genera_e_salva_pdf(st.session_state.dati_form, lingua)
            else: st.warning("Veuillez cocher la case de confirmation")

def genera_e_salva_pdf(dati, lingua):
    codice = genera_codice(); pin = genera_pin()
    dati_finali = {"id": codice, "codice": codice, "pin": pin, "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"), **dati, "stato_firma": "Da firmare"}
    
    if salva_su_google_sheet(dati_finali, GOOGLE_SCRIPT_URL_ASSUNZIONI, "append"):
        st.success(f"✅ {get_testo('pdf_generato', lingua)}")
        pdf_bytes = genera_pdf_lavoratore(dati_finali)
        st.warning(get_testo('conserva_credenziali', lingua))
        c1, c2 = st.columns(2)
        with c1: st.info(f"**{get_testo('codice_accesso', lingua)}:** {codice}")
        with c2: st.info(f"**{get_testo('pin_accesso', lingua)}:** {pin}")
        st.download_button(label=f"📥 {get_testo('scarica', lingua)} PDF", data=pdf_bytes, file_name=f"Proacier_{codice}.pdf", mime="application/pdf", use_container_width=True, key="btn_dl")
        st.session_state.step = 1; st.session_state.dati_form = {}
    else: st.error("Erreur de connexion à Google Sheets.")

if __name__ == "__main__":
    main()
