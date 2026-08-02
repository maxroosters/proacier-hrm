import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF
import random
import pandas as pd

# ============================================
# CONFIGURAZIONE
# ============================================
st.set_page_config(
    page_title="Proacier - Ressources Humaines",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per sidebar verde Proacier
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #5EA529;
}
[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] div {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# URL del logo Proacier
LOGO_URL = "https://proacier.sn/wp-content/uploads/2025/03/logo-proacier1-1024x386.png"

# URL Google Apps Script
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycbzlc2iOHSiNSWNvU21g4GqsGwMA4QQDJXTG_J3hkfe5Za8nyeTWb1amhuR2ULFI5b9k/exec"

PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# ============================================
# TRADUZIONI
# ============================================
TRADUZIONI = {
    "fr": {
        "titolo": " PROACIER - GESTION RH",
        "sottotitolo": "Système de Recrutement - Sénégal",
        "lingua": "Langue",
        "candidatura_spontanea": "📩 Candidature Spontanée",
        "area_lavoratore": "👷 Espace Travailleur",
        "dashboard": "📊 Tableau de Bord",
        "accedi": "Connexion",
        "password": "Mot de passe",
        "indietro": "⬅ Retour",
        "continua": "Continuer ➡",
        "genera_pdf": "✅ Générer le PDF",
        "pdf_generato": "Document enregistré avec succès!",
        "conserva_credenziali": "⚠️ Conservez précieusement ces informations",
        "codice_accesso": "Code d'accès",
        "pin_accesso": "PIN personnel",
        "scarica": "Télécharger le",
        "totale_operai": "Total Ouvriers",
        "nessun_risultato": "Aucun résultat disponible",
        "step_1": "Étape 1: Informations Personnelles et Familiales",
        "step_2": "Étape 2: Résidence et Documents",
        "step_3": "Étape 3: Expérience Professionnelle",
        "step_4": "Étape 4: Compétences et Permis",
        "step_5": "Étape 5: Informations Médicales",
        "step_6": "Étape 6: Contact d'Urgence et Validation",
        "errore_obbligatori": "Veuillez remplir tous les champs obligatoires",
        "titolo_candidatura": " CANDIDATURE SPONTANÉE",
        "sottotitolo_candidatura": "Transmettez vos données pour une future embauche",
        "invia_candidatura": "Envoyer ma candidature",
        "i_miei_dati": "👤 Mes Données Personnelles",
        "spazio_lavoratore_titolo": "👷 Espace Travailleur",
        "spazio_lavoratore_sottotitolo": "Choisissez une option:",
        "gia_assunto": "Déjà embauché?",
        "gia_assunto_desc": "Accédez à votre espace personnel pour consulter vos données, vos fiches de paie et modifier vos informations familiales.",
        "btn_login_operaio": "🔓 Connexion à mon espace",
        "nuovo_giornaliero": "Nouveau / Journalier?",
        "nuovo_giornaliero_desc": "Transmettez vos données personnelles à l'administration pour une éventuelle future embauche.",
        "btn_trasmetti_operaio": "📤 Transmettre mes données",
        "login_operaio_titolo": "🔐 Connexion à mon espace personnel",
        "login_operaio_codice": "Code d'accès (ex: THS-2026-XXXX)",
        "login_operaio_pin": "PIN personnel",
        "btn_connetti": "Se connecter",
        "dashboard_operaio_titolo": "👤 Mon Espace Personnel",
        "dashboard_operaio_sottotitolo": "Bienvenue dans votre espace personnel PROACIER",
        "dati_personali": "📋 Mes Informations Personnelles",
        "dati_familiari": "👨‍👩‍👧‍ Ma Famille",
        "dati_lavoro": "💼 Mes Informations de Travail",
        "aggiorna": "💾 Mettre à jour",
        "aggiornato": "✅ Données mises à jour avec succès!",
        "errore_aggiornamento": "❌ Erreur lors de la mise à jour",
        "dati_bloccati": "🔒 Ces informations ne peuvent pas être modifiées",
        "dati_modificabili": "️ Ces informations peuvent être modifiées",
        "disclaimer_trasmetti": "⚠️ **IMPORTANT:** Ceci n'est PAS un contrat de travail, ni un document d'embauche. Il s'agit uniquement de la transmission de vos données à l'administration de PROACIER pour une éventuelle future embauche.",
        "trasmetti_titolo": "📝 Transmission de données personnelles",
        "btn_envia_trasmetti": "📤 Envoyer mes données",
        "trasmetti_successo": "✅ Données transmises avec succès à l'administration PROACIER!",
        "trasmetti_contatto": "Vous serez contacté en cas de besoin.",
        "logout": "🚪 Déconnexion",
        "benv": "Bienvenue",
        "home_titolo": "🏭 Bienvenue sur la plateforme PROACIER",
        "home_sottotitolo": "Système de Gestion des Ressources Humaines - Thiès, Sénégal",
        "home_descrizione": "Cette application permet de:",
        "home_punto_1": "📝 **Transmettre vos données personnelles** à l'administration PROACIER pour une éventuelle future embauche",
        "home_punto_2": "📩 **Envoyer une candidature spontanée** si vous êtes intéressé par un poste dans notre entreprise",
        "home_punto_3": "👷 **Accéder à votre espace personnel** si vous êtes déjà embauché, pour consulter vos données et modifier vos informations familiales",
        "home_punto_4": "💰 **Permettre le paiement des salaires** des journaliers grâce à la transmission sécurisée de vos informations",
        "home_come_faire": "📌 Comment utiliser cette application?",
        "home_btn_1": " **Espace Travailleur** (menu à gauche): Pour les employés déjà embauchés ou les nouveaux travailleurs qui souhaitent transmettre leurs données",
        "home_btn_2": "📩 **Candidature Spontanée** (menu à gauche): Pour envoyer votre candidature à PROACIER",
        "home_btn_3": "📊 **Tableau de Bord** (menu à gauche): Accès réservé à l'administration",
        "home_lingua": " Choisissez votre langue dans le menu à gauche",
        "home_contatto": "📍 PROACIER - Thiès, Sénégal",
        "home_footer": "© 2026 PROACIER - Tous droits réservés"
    },
    "it": {
        "titolo": "🏭 PROACIER - GESTIONE RH",
        "sottotitolo": "Sistema di Reclutamento - Senegal",
        "lingua": "Lingua",
        "candidatura_spontanea": "📩 Candidatura Spontanea",
        "area_lavoratore": "👷 Spazio Lavoratore",
        "dashboard": " Dashboard",
        "accedi": "Accedi",
        "password": "Password",
        "indietro": "⬅ Indietro",
        "continua": "Continua ➡",
        "genera_pdf": "✅ Genera PDF",
        "pdf_generato": "Documento registrato con successo!",
        "conserva_credenziali": "️ Conserva queste informazioni",
        "codice_accesso": "Codice di accesso",
        "pin_accesso": "PIN personale",
        "scarica": "Scarica il",
        "totale_operai": "Totale Operai",
        "nessun_risultato": "Nessun risultato disponibile",
        "step_1": "Passaggio 1: Informazioni Personali e Familiari",
        "step_2": "Passaggio 2: Residenza e Documenti",
        "step_3": "Passaggio 3: Esperienza Professionale",
        "step_4": "Passaggio 4: Competenze e Patente",
        "step_5": "Passaggio 5: Informazioni Mediche",
        "step_6": "Passaggio 6: Contatto di Emergenza e Validazione",
        "errore_obbligatori": "Compila tutti i campi obbligatori",
        "titolo_candidatura": "📩 CANDIDATURA SPONTANEA",
        "sottotitolo_candidatura": "Trasmetti i tuoi dati per una futura assunzione",
        "invia_candidatura": "Invia candidatura",
        "i_miei_dati": "👤 I Miei Dati Personali",
        "spazio_lavoratore_titolo": "👷 Spazio Lavoratore",
        "spazio_lavoratore_sottotitolo": "Scegli un'opzione:",
        "gia_assunto": "Già assunto?",
        "gia_assunto_desc": "Accedi al tuo spazio personale per consultare i tuoi dati, le buste paga e modificare le informazioni familiari.",
        "btn_login_operaio": " Accedi al mio spazio",
        "nuovo_giornaliero": "Nuovo / Giornaliero?",
        "nuovo_giornaliero_desc": "Trasmetti i tuoi dati personali all'amministrazione per una possibile futura assunzione.",
        "btn_trasmetti_operaio": " Trasmetti i miei dati",
        "login_operaio_titolo": " Accesso al mio spazio personale",
        "login_operaio_codice": "Codice di accesso (es: THS-2026-XXXX)",
        "login_operaio_pin": "PIN personale",
        "btn_connetti": "Accedi",
        "dashboard_operaio_titolo": "👤 Il Mio Spazio Personale",
        "dashboard_operaio_sottotitolo": "Benvenuto nel tuo spazio personale PROACIER",
        "dati_personali": "📋 Le Mie Informazioni Personali",
        "dati_familiari": "👨‍👩‍👧‍👦 La Mia Famiglia",
        "dati_lavoro": " Le Mie Informazioni di Lavoro",
        "aggiorna": "💾 Aggiorna",
        "aggiornato": "✅ Dati aggiornati con successo!",
        "errore_aggiornamento": "❌ Errore durante l'aggiornamento",
        "dati_bloccati": "🔒 Queste informazioni non possono essere modificate",
        "dati_modificabili": "✏️ Queste informazioni possono essere modificate",
        "disclaimer_trasmetti": "⚠️ **IMPORTANTE:** Questo NON è un contratto di lavoro, né un documento di assunzione. Si tratta solo della trasmissione dei tuoi dati all'amministrazione PROACIER per una possibile futura assunzione.",
        "trasmetti_titolo": "📝 Trasmissione dati personali",
        "btn_envia_trasmetti": "📤 Invia i miei dati",
        "trasmetti_successo": "✅ Dati trasmessi con successo all'amministrazione PROACIER!",
        "trasmetti_contatto": "Sarai contattato in caso di necessità.",
        "logout": "🚪 Esci",
        "benv": "Benvenuto",
        "home_titolo": "🏭 Benvenuto sulla piattaforma PROACIER",
        "home_sottotitolo": "Sistema di Gestione Risorse Umane - Thiès, Senegal",
        "home_descrizione": "Questa applicazione permette di:",
        "home_punto_1": "📝 **Trasmettere i tuoi dati personali** all'amministrazione PROACIER per una possibile futura assunzione",
        "home_punto_2": "📩 **Inviare una candidatura spontanea** se sei interessato a un posto nella nostra azienda",
        "home_punto_3": " **Accedere al tuo spazio personale** se sei già assunto, per consultare i tuoi dati e modificare le informazioni familiari",
        "home_punto_4": "💰 **Permettere il pagamento dei salari** dei giornalieri grazie alla trasmissione sicura delle tue informazioni",
        "home_come_faire": "📌 Come usare questa applicazione?",
        "home_btn_1": "👷 **Spazio Lavoratore** (menu a sinistra): Per i dipendenti già assunti o i nuovi lavoratori che vogliono trasmettere i propri dati",
        "home_btn_2": "📩 **Candidatura Spontanea** (menu a sinistra): Per inviare la tua candidatura a PROACIER",
        "home_btn_3": "📊 **Dashboard** (menu a sinistra): Accesso riservato all'amministrazione",
        "home_lingua": "🌍 Scegli la tua lingua nel menu a sinistra",
        "home_contatto": "📍 PROACIER - Thiès, Senegal",
        "home_footer": "© 2026 PROACIER - Tutti i diritti riservati"
    },
    "en": {
        "titolo": "🏭 PROACIER - HR MANAGEMENT",
        "sottotitolo": "Recruitment System - Senegal",
        "lingua": "Language",
        "candidatura_spontanea": "📩 Spontaneous Application",
        "area_lavoratore": "👷 Worker Area",
        "dashboard": "📊 Dashboard",
        "accedi": "Login",
        "password": "Password",
        "indietro": "⬅ Back",
        "continua": "Continue ➡",
        "genera_pdf": "✅ Generate PDF",
        "pdf_generato": "Document saved successfully!",
        "conserva_credenziali": "⚠️ Keep this information safe",
        "codice_accesso": "Access code",
        "pin_accesso": "Personal PIN",
        "scarica": "Download",
        "totale_operai": "Total Workers",
        "nessun_risultato": "No results available",
        "step_1": "Step 1: Personal and Family Information",
        "step_2": "Step 2: Residence and Documents",
        "step_3": "Step 3: Work Experience",
        "step_4": "Step 4: Skills and License",
        "step_5": "Step 5: Medical Information",
        "step_6": "Step 6: Emergency Contact and Validation",
        "errore_obbligatori": "Please fill in all required fields",
        "titolo_candidatura": "📩 SPONTANEOUS APPLICATION",
        "sottotitolo_candidatura": "Submit your data for future hiring",
        "invia_candidatura": "Submit application",
        "i_miei_dati": "👤 My Personal Data",
        "spazio_lavoratore_titolo": "👷 Worker Area",
        "spazio_lavoratore_sottotitolo": "Choose an option:",
        "gia_assunto": "Already hired?",
        "gia_assunto_desc": "Access your personal space to view your data, pay slips and modify family information.",
        "btn_login_operaio": "🔓 Login to my space",
        "nuovo_giornaliero": "New / Day worker?",
        "nuovo_giornaliero_desc": "Submit your personal data to the administration for a possible future hiring.",
        "btn_trasmetti_operaio": "📤 Submit my data",
        "login_operaio_titolo": "🔐 Login to my personal space",
        "login_operaio_codice": "Access code (ex: THS-2026-XXXX)",
        "login_operaio_pin": "Personal PIN",
        "btn_connetti": "Login",
        "dashboard_operaio_titolo": "👤 My Personal Space",
        "dashboard_operaio_sottotitolo": "Welcome to your PROACIER personal space",
        "dati_personali": " My Personal Information",
        "dati_familiari": "👨‍👩‍👧‍👦 My Family",
        "dati_lavoro": " My Work Information",
        "aggiorna": "💾 Update",
        "aggiornato": "✅ Data updated successfully!",
        "errore_aggiornamento": "❌ Error during update",
        "dati_bloccati": "🔒 This information cannot be modified",
        "dati_modificabili": "✏️ This information can be modified",
        "disclaimer_trasmetti": "️ **IMPORTANT:** This is NOT an employment contract, nor a hiring document. It is only the transmission of your data to PROACIER administration for a possible future hiring.",
        "trasmetti_titolo": "📝 Personal data transmission",
        "btn_envia_trasmetti": "📤 Submit my data",
        "trasmetti_successo": "✅ Data successfully transmitted to PROACIER administration!",
        "trasmetti_contatto": "You will be contacted if needed.",
        "logout": "🚪 Logout",
        "benv": "Welcome",
        "home_titolo": "🏭 Welcome to the PROACIER platform",
        "home_sottotitolo": "Human Resources Management System - Thiès, Senegal",
        "home_descrizione": "This application allows you to:",
        "home_punto_1": "📝 **Submit your personal data** to PROACIER administration for a possible future hiring",
        "home_punto_2": " **Send a spontaneous application** if you are interested in a position in our company",
        "home_punto_3": "👷 **Access your personal space** if you are already hired, to view your data and modify family information",
        "home_punto_4": "💰 **Enable salary payments** for day workers through secure transmission of your information",
        "home_come_faire": "📌 How to use this application?",
        "home_btn_1": "👷 **Worker Area** (left menu): For already hired employees or new workers who want to submit their data",
        "home_btn_2": " **Spontaneous Application** (left menu): To send your application to PROACIER",
        "home_btn_3": "📊 **Dashboard** (left menu): Access reserved for administration",
        "home_lingua": "🌍 Choose your language in the left menu",
        "home_contatto": "📍 PROACIER - Thiès, Senegal",
        "home_footer": "© 2026 PROACIER - All rights reserved"
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
# GENERATORE PDF
# ============================================
class PDFProacier(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(68, 114, 196)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "FICHE D'ENREGISTREMENT - RESSOURCES HUMAINES", 0, 1, 'C', True)
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

def genera_pdf_lavoratore(dati):
    pdf = PDFProacier()
    pdf.add_page()
    pdf.sezione("INFORMATIONS PERSONNELLES")
    pdf.campo("Nom", dati.get('cognome', ''))
    pdf.campo("Prénom", dati.get('nome', ''))
    pdf.campo("Date de naissance", dati.get('data_nascita', ''))
    pdf.campo("Lieu de naissance", dati.get('luogo_nascita', ''))
    return pdf.output(dest='S').encode('latin-1')

# ============================================
# PAGINA CANDIDATURA SPONTANEA (COMPLETA)
# ============================================
def pagina_candidatura_spontanea(lingua):
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.info("️ Ceci n'est PAS un contrat d'embauche, mais une transmission de données pour une éventuelle future embauche.")
    st.markdown("---")
    
    with st.form("form_candidatura", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            cognome = st.text_input("Nom *")
            nome = st.text_input("Prénom *")
            telefono = st.text_input("Téléphone *")
            cni = st.text_input("Numéro CNI *")
        with col2:
            email = st.text_input("Email")
            data_nascita = st.date_input("Date de naissance")
            indirizzo = st.text_input("Adresse / Quartier")
            citta = st.text_input("Ville", value="Thiès")
        
        st.markdown("---")
        st.subheader("💼 Expérience Professionnelle")
        lavoro_attuale = st.text_input("Poste actuel ou dernier poste occupé")
        azienda_attuale = st.text_input("Entreprise actuelle ou dernière entreprise")
        anni_esperienza = st.number_input("Années d'expérience", min_value=0, max_value=50, value=0)
        
        st.markdown("---")
        st.subheader("🎓 Formation et Études")
        livello_studio = st.selectbox("Niveau d'études", [
            "Aucun", "Primaire", "Collège", "Lycée", 
            "CAP/BTSA", "BTS", "Licence", "Master", "Doctorat"
        ])
        specializzazione = st.text_input("Spécialité / Filière")
        corsi_certificazioni = st.text_area("Cours, certifications ou formations complémentaires", 
                                           placeholder="Décrivez brièvement les cours ou certifications obtenus...")
        
        st.markdown("---")
        st.subheader("🛠️ Compétences et Motivations")
        skills = st.text_area("Vos compétences techniques", 
                             placeholder="Ex: Soudure, mécanique, électricité, maçonnerie, conduite d'engins...")
        motivazione = st.text_area("Pourquoi souhaitez-vous travailler chez PROACIER?", 
                                  placeholder="Expliquez votre motivation...")
        disponibilita = st.selectbox("Disponibilité", [
            "Immédiate", "1 semaine", "2 semaines", "1 mois", "Autre"
        ])
        
        st.markdown("---")
        conferma = st.checkbox("Je confirme l'exactitude des informations *")
        
        submitted = st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True)
        
        if submitted:
            if cognome and nome and telefono and cni and conferma:
                dati = {
                    "id": genera_codice(),
                    "cognome": cognome,
                    "nome": nome,
                    "telefono": telefono,
                    "email": email,
                    "cni": cni,
                    "data_nascita": str(data_nascita),
                    "indirizzo": indirizzo,
                    "citta": citta,
                    "lavoro_attuale": lavoro_attuale,
                    "azienda_attuale": azienda_attuale,
                    "anni_esperienza": anni_esperienza,
                    "livello_studio": livello_studio,
                    "specializzazione": specializzazione,
                    "corsi_certificazioni": corsi_certificazioni,
                    "skills": skills,
                    "motivazione": motivazione,
                    "disponibilita": disponibilita,
                    "data_invio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "tipo": "candidatura_spontanea"
                }
                if salva_su_google_sheet(dati, GOOGLE_SCRIPT_URL_CANDIDATURE, "append"):
                    st.success("✅ Candidature envoyée avec succès!")
                    st.info("Nous vous contacterons en cas de besoin.")
                else:
                    st.error("Erreur de connexion")
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*)")

# ============================================
# PAGINA SPAZIO LAVORATORE (2 PULSANTI)
# ============================================
def pagina_spazio_lavoratore(lingua):
    st.title(get_testo("spazio_lavoratore_titolo", lingua))
    st.markdown("---")
    st.markdown(f"### {get_testo('spazio_lavoratore_sottotitolo', lingua)}")
    st.markdown("---")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown(f"#### 🔐 {get_testo('gia_assunto', lingua)}")
        st.markdown(get_testo('gia_assunto_desc', lingua))
        st.markdown("---")
        if st.button(get_testo("btn_login_operaio", lingua), type="primary", use_container_width=True, key="btn_login_operaio_main"):
            st.session_state.pagina = 'login_operaio'
            st.rerun()
    
    with col2:
        st.markdown(f"####  {get_testo('nuovo_giornaliero', lingua)}")
        st.markdown(get_testo('nuovo_giornaliero_desc', lingua))
        st.markdown("---")
        if st.button(get_testo("btn_trasmetti_operaio", lingua), type="primary", use_container_width=True, key="btn_trasmetti_operaio_main"):
            st.session_state.pagina = 'trasmetti_dati'
            st.rerun()

# ============================================
# PAGINA LOGIN OPERAIO
# ============================================
def pagina_login_operaio(lingua):
    st.title(get_testo("login_operaio_titolo", lingua))
    st.markdown("---")
    
    codice = st.text_input(get_testo("login_operaio_codice", lingua), key="login_op_codice")
    pin = st.text_input(get_testo("login_operaio_pin", lingua), type="password", key="login_op_pin")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(get_testo("btn_connetti", lingua), type="primary", use_container_width=True):
            if codice and pin:
                st.session_state.logged_in_operaio = True
                st.session_state.codice_operaio = codice
                st.session_state.pagina = 'dashboard_operaio'
                st.rerun()
            else:
                st.error("Veuillez remplir tous les champs")
    with col2:
        if st.button(get_testo("indietro", lingua), use_container_width=True):
            st.session_state.pagina = 'login_lavoratore'
            st.rerun()

# ============================================
# PAGINA DASHBOARD OPERAIO
# ============================================
def pagina_dashboard_operaio(lingua):
    st.title(get_testo("dashboard_operaio_titolo", lingua))
    st.markdown(f"**{get_testo('benv', lingua)}** {st.session_state.get('codice_operaio', '')}")
    st.markdown("---")
    
    dati_operaio = {
        "cognome": "DIALLO",
        "nome": "Mamadou",
        "data_nascita": "15/03/1990",
        "luogo_nascita": "Thiès",
        "cni": "1234567890123",
        "telefono_1": "+221 77 123 45 67",
        "email": "mamadou.diallo@email.com",
        "stato_civile": "Marié",
        "num_figli": 3,
        "nome_coniuge": "Fatima DIALLO",
        "patente": "B",
        "mansione": "Soudeur",
        "data_assunzione": "01/01/2024"
    }
    
    st.subheader(get_testo("dati_personali", lingua))
    st.info(get_testo("dati_bloccati", lingua))
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nom de famille", value=dati_operaio["cognome"], disabled=True, key="op_cognome")
        st.text_input("Prénom", value=dati_operaio["nome"], disabled=True, key="op_nome")
        st.text_input("Date de naissance", value=dati_operaio["data_nascita"], disabled=True, key="op_data")
    with col2:
        st.text_input("Lieu de naissance", value=dati_operaio["luogo_nascita"], disabled=True, key="op_luogo")
        st.text_input("Numéro CNI ", value=dati_operaio["cni"], disabled=True, key="op_cni")
        st.text_input("Téléphone", value=dati_operaio["telefono_1"], disabled=False, key="op_tel")
    
    st.markdown("---")
    
    st.subheader(get_testo("dati_familiari", lingua))
    st.success(get_testo("dati_modificabili", lingua))
    
    col1, col2 = st.columns(2)
    with col1:
        stato_civile = st.selectbox("État civil", ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve"], 
                                    index=["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve"].index(dati_operaio["stato_civile"]) if dati_operaio["stato_civile"] in ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve"] else 0, 
                                    key="op_stato")
        num_figli = st.number_input("Nombre d'enfants", min_value=0, value=dati_operaio["num_figli"], key="op_figli")
    with col2:
        nome_coniuge = st.text_input("Nom du conjoint", value=dati_operaio["nome_coniuge"], key="op_coniuge")
    
    st.markdown("---")
    
    st.subheader(get_testo("dati_lavoro", lingua))
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Poste", value=dati_operaio["mansione"], disabled=True, key="op_mansione")
        st.text_input("Date d'embauche", value=dati_operaio["data_assunzione"], disabled=True, key="op_data_ass")
    with col2:
        st.text_input("Permis de conduire", value=dati_operaio["patente"], disabled=True, key="op_patente")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(get_testo("aggiorna", lingua), type="primary", use_container_width=True):
            st.success(get_testo("aggiornato", lingua))
    with col2:
        if st.button(get_testo("logout", lingua), use_container_width=True):
            st.session_state.logged_in_operaio = False
            st.session_state.codice_operaio = None
            st.session_state.pagina = 'login_lavoratore'
            st.rerun()

# ============================================
# PAGINA TRASMETTI DATI (COMPLETA)
# ============================================
def pagina_trasmetti_dati(lingua):
    st.title(get_testo("trasmetti_titolo", lingua))
    st.markdown("---")
    st.warning(get_testo("disclaimer_trasmetti", lingua))
    st.markdown("---")
    
    with st.form("form_trasmetti_completo", clear_on_submit=True):
        # STEP 1: Informazioni Personali
        st.subheader("📋 Informations Personnelles")
        col1, col2 = st.columns(2)
        with col1:
            cognome = st.text_input("Nom de famille *")
            nome = st.text_input("Prénom *")
            data_nascita = st.date_input("Date de naissance *")
            luogo_nascita = st.text_input("Lieu de naissance *")
            sesso = st.selectbox("Sexe", ["M", "F"])
        with col2:
            cni = st.text_input("Numéro CNI *")
            telefono = st.text_input("Téléphone *")
            email = st.text_input("Email")
            indirizzo = st.text_input("Adresse complète")
            quartiere = st.text_input("Quartier")
            citta = st.text_input("Ville", value="Thiès")
        
        st.markdown("---")
        
        # STEP 2: Stato Civile e Famiglia
        st.subheader("‍👩‍👧‍👦 Situation Familiale")
        col1, col2 = st.columns(2)
        with col1:
            stato_civile = st.selectbox("État civil", 
                ["Célibataire", "Marié(e)", "Divorcé(e)", "Veuf/Veuve", "Union libre"])
            num_figli = st.number_input("Nombre d'enfants", min_value=0, value=0)
        with col2:
            nome_coniuge = st.text_input("Nom du conjoint(e) (si applicable)")
            data_matrimonio = st.date_input("Date de mariage (si applicable)")
        
        # Dettagli figli
        figli_dati = []
        if num_figli > 0:
            st.markdown("---")
            st.info(" Informations sur les enfants (pour couverture sociale)")
            for i in range(num_figli):
                col1, col2, col3 = st.columns(3)
                with col1:
                    nome_figlio = st.text_input(f"Nom enfant {i+1}", key=f"figlio_nome_{i}")
                with col2:
                    data_figlio = st.date_input(f"Date naissance enfant {i+1}", key=f"figlio_data_{i}")
                with col3:
                    sesso_figlio = st.selectbox(f"Sexe enfant {i+1}", ["M", "F"], key=f"figlio_sesso_{i}")
                figli_dati.append({
                    "nome": nome_figlio,
                    "data_nascita": str(data_figlio),
                    "sesso": sesso_figlio
                })
        
        st.markdown("---")
        
        # STEP 3: Taglie per Uniformi
        st.subheader("👕 Tailles (pour équipements/uniformes)")
        col1, col2, col3 = st.columns(3)
        with col1:
            taglia_maglia = st.selectbox("Taille t-shirt/chemise", 
                ["XS", "S", "M", "L", "XL", "XXL", "XXXL"])
        with col2:
            taglia_pantaloni = st.selectbox("Taille pantalon", 
                ["28", "30", "32", "34", "36", "38", "40", "42", "44", "46"])
        with col3:
            taglia_scarpe = st.selectbox("Pointure chaussures", 
                ["38", "39", "40", "41", "42", "43", "44", "45", "46"])
        
        st.markdown("---")
        
        # STEP 4: Formazione
        st.subheader("🎓 Formation et Études")
        col1, col2 = st.columns(2)
        with col1:
            livello_studio = st.selectbox("Niveau d'études", [
                "Aucun", "Primaire", "Collège", "Lycée", 
                "CAP/BTSA", "BTS", "Licence", "Master"
            ])
            specializzazione = st.text_input("Spécialité / Filière")
        with col2:
            patente = st.selectbox("Permis de conduire", 
                ["Aucun", "A", "B", "C", "D", "E"])
            data_patente = st.date_input("Date d'obtention permis")
        
        corsi = st.text_area("Cours, certifications ou formations complémentaires",
                            placeholder="Décrivez les formations suivies...")
        
        st.markdown("---")
        
        # STEP 5: Esperienza Lavorativa
        st.subheader(" Expérience Professionnelle")
        mansione_precedente = st.text_input("Poste précédent ou actuel")
        azienda_precedente = st.text_input("Entreprise précédente ou actuelle")
        anni_esperienza = st.number_input("Années d'expérience", min_value=0, max_value=50, value=0)
        skills = st.text_area("Compétences techniques",
                             placeholder="Ex: Soudure, mécanique, électricité, maçonnerie...")
        
        st.markdown("---")
        
        # STEP 6: Informazioni Mediche
        st.subheader("🏥 Informations Médicales")
        col1, col2 = st.columns(2)
        with col1:
            gruppo_sanguigno = st.selectbox("Groupe sanguin", ["A", "B", "AB", "O", "Je ne sais pas"])
            rh = st.selectbox("Rhésus", ["+", "-", "Je ne sais pas"])
        with col2:
            allergie = st.text_area("Allergies connues")
            patologie = st.text_area("Pathologies chroniques (si applicable)")
        
        st.markdown("---")
        
        # STEP 7: Contatto Emergenza
        st.subheader("🚨 Contact d'Urgence")
        col1, col2 = st.columns(2)
        with col1:
            emergenza_nome = st.text_input("Nom du contact d'urgence *")
            emergenza_parentela = st.selectbox("Relation", 
                ["Conjoint(e)", "Père", "Mère", "Frère/Soeur", "Autre"])
        with col2:
            emergenza_telefono = st.text_input("Téléphone contact d'urgence *")
            emergenza_indirizzo = st.text_input("Adresse du contact")
        
        st.markdown("---")
        
        # Validazione
        conferma = st.checkbox("Je confirme que toutes les informations fournies sont exactes et complètes *")
        
        submitted = st.form_submit_button(get_testo("btn_envia_trasmetti", lingua), 
                                         type="primary", use_container_width=True)
        
        if submitted:
            if cognome and nome and cni and telefono and emergenza_nome and emergenza_telefono and conferma:
                # Costruisci dati completi
                dati = {
                    "id": genera_codice(),
                    "cognome": cognome,
                    "nome": nome,
                    "data_nascita": str(data_nascita),
                    "luogo_nascita": luogo_nascita,
                    "sesso": sesso,
                    "cni": cni,
                    "telefono": telefono,
                    "email": email,
                    "indirizzo": indirizzo,
                    "quartiere": quartiere,
                    "citta": citta,
                    "stato_civile": stato_civile,
                    "num_figli": num_figli,
                    "nome_coniuge": nome_coniuge,
                    "data_matrimonio": str(data_matrimonio),
                    "figli_dati": str(figli_dati) if num_figli > 0 else "",
                    "taglia_maglia": taglia_maglia,
                    "taglia_pantaloni": taglia_pantaloni,
                    "taglia_scarpe": taglia_scarpe,
                    "livello_studio": livello_studio,
                    "specializzazione": specializzazione,
                    "patente": patente,
                    "data_patente": str(data_patente),
                    "corsi": corsi,
                    "mansione_precedente": mansione_precedente,
                    "azienda_precedente": azienda_precedente,
                    "anni_esperienza": anni_esperienza,
                    "skills": skills,
                    "gruppo_sanguigno": gruppo_sanguigno,
                    "rh": rh,
                    "allergie": allergie,
                    "patologie": patologie,
                    "emergenza_nome": emergenza_nome,
                    "emergenza_parentela": emergenza_parentela,
                    "emergenza_telefono": emergenza_telefono,
                    "emergenza_indirizzo": emergenza_indirizzo,
                    "data_invio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "tipo": "trasmissione_dati_completa"
                }
                
                if salva_su_google_sheet(dati, GOOGLE_SCRIPT_URL_CANDIDATURE, "append"):
                    st.success(get_testo("trasmetti_successo", lingua))
                    st.info(get_testo("trasmetti_contatto", lingua))
                    st.balloons()
                else:
                    st.error("❌ Erreur de connexion. Réessayez.")
            else:
                st.error("Veuillez remplir tous les champs obligatoires (*) et confirmer.")
    
    if st.button(get_testo("indietro", lingua), use_container_width=True):
        st.session_state.pagina = 'login_lavoratore'
        st.rerun()

# ============================================
# PAGINA HOME
# ============================================
def pagina_home(lingua):
    st.title(get_testo("home_titolo", lingua))
    st.markdown(f"### {get_testo('home_sottotitolo', lingua)}")
    st.markdown("---")
    
    st.markdown(f"### {get_testo('home_descrizione', lingua)}")
    st.markdown(f"- {get_testo('home_punto_1', lingua)}")
    st.markdown(f"- {get_testo('home_punto_2', lingua)}")
    st.markdown(f"- {get_testo('home_punto_3', lingua)}")
    st.markdown(f"- {get_testo('home_punto_4', lingua)}")
    st.markdown("---")
    
    st.markdown(f"### {get_testo('home_come_faire', lingua)}")
    st.markdown(f"1. {get_testo('home_lingua', lingua)}")
    st.markdown(f"2. {get_testo('home_btn_1', lingua)}")
    st.markdown(f"3. {get_testo('home_btn_2', lingua)}")
    st.markdown(f"4. {get_testo('home_btn_3', lingua)}")
    st.markdown("---")
    
    st.info(get_testo("home_contatto", lingua))
    st.markdown(f"*{get_testo('home_footer', lingua)}*")

# ============================================
# MAIN APP
# ============================================
def main():
    if 'lingua' not in st.session_state:
        st.session_state.lingua = 'fr'
    if 'pagina' not in st.session_state:
        st.session_state.pagina = 'home'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'logged_in_operaio' not in st.session_state:
        st.session_state.logged_in_operaio = False
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'dati_form' not in st.session_state:
        st.session_state.dati_form = {}

    lingua = st.session_state.lingua

    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.markdown("---")
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
            if st.button("📊 Dashboard", key="btn_dash"):
                st.session_state.pagina = 'dashboard'
            if st.button(get_testo("logout", lingua), key="btn_logout"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.pagina = 'home'
                st.rerun()
        else:
            if st.button(get_testo("candidatura_spontanea", lingua), key="btn_cand"):
                st.session_state.pagina = 'candidatura'
            if st.button(get_testo("area_lavoratore", lingua), key="btn_area"):
                st.session_state.pagina = 'login_lavoratore'
            if st.button(get_testo("dashboard", lingua), key="btn_dash_login"):
                st.session_state.pagina = 'login_admin'

    # ROUTING PAGINE
    if st.session_state.pagina == 'home':
        pagina_home(lingua)

    elif st.session_state.pagina == 'candidatura':
        pagina_candidatura_spontanea(lingua)

    elif st.session_state.pagina == 'login_lavoratore':
        pagina_spazio_lavoratore(lingua)

    elif st.session_state.pagina == 'login_operaio':
        pagina_login_operaio(lingua)

    elif st.session_state.pagina == 'dashboard_operaio':
        pagina_dashboard_operaio(lingua)

    elif st.session_state.pagina == 'trasmetti_dati':
        pagina_trasmetti_dati(lingua)

    elif st.session_state.pagina == 'login_admin':
        pwd = st.text_input(get_testo("password", lingua), type="password", key="login_pwd")
        if st.button(get_testo("accedi", lingua), type="primary", key="btn_login_admin"):
            if pwd == PASSWORD_DASHBOARD:
                st.session_state.logged_in = True
                st.session_state.user_type = 'admin'
                st.session_state.pagina = 'dashboard'
                st.rerun()
            else:
                st.error("Mot de passe incorrect")

    elif st.session_state.pagina == 'dashboard':
        st.title(get_testo("dashboard", lingua))
        dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if dati and len(dati) > 1:
            df = pd.DataFrame(dati[1:], columns=dati[0])
            st.metric(get_testo("totale_operai", lingua), len(df))
            st.dataframe(df[['ID', 'Cognome', 'Nome', 'Telefono_1', 'Mansione_1', 'Stato_Firma']], use_container_width=True)
        else:
            st.warning(get_testo("nessun_risultato", lingua))

if __name__ == "__main__":
    main()
