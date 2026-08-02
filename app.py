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

# CSS per sidebar grigio chiaro
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #99A1AF;
}
</style>
""", unsafe_allow_html=True)

# URL del logo Proacier
LOGO_URL = "https://proacier.sn/wp-content/uploads/2025/03/logo-proacier1-1024x386.png"

# URL Google Apps Script 1: Assunzioni Complete
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec"

# URL Google Apps Script 2: Candidature Spontanee
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycbzlc2iOHSiNSWNvU21g4GqsGwMA4QQDJXTG_J3hkfe5Za8nyeTWb1amhuR2ULFI5b9k/exec"

PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# ============================================
# TRADUZIONI
# ============================================
TRADUZIONI = {
    "fr": {
        "titolo": "🏭 PROACIER - GESTION DES RESSOURCES HUMAINES",
        "sottotitolo": "Système de Recrutement - Sénégal",
        "lingua": "Langue",
        "nuova_assunzione": "➕ Nouvelle Embauche",
        "candidatura_spontanea": "📩 Candidature Spontanée",
        "area_lavoratore": "👤 Espace Travailleur",
        "dashboard": " Tableau de Bord",
        "accedi": "Connexion",
        "password": "Mot de passe",
        "indietro": " Retour",
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
        "i_miei_dati": "👤 Mes Données Personnelles"
    },
    "it": {
        "titolo": "🏭 PROACIER - GESTIONE RISORSE UMANE",
        "sottotitolo": "Sistema di Reclutamento - Senegal",
        "lingua": "Lingua",
        "nuova_assunzione": "➕ Nuova Assunzione",
        "candidatura_spontanea": "📩 Candidatura Spontanea",
        "area_lavoratore": "👤 Area Lavoratore",
        "dashboard": "📊 Dashboard",
        "accedi": "Accedi",
        "password": "Password",
        "indietro": "⬅ Indietro",
        "continua": "Continua ➡",
        "genera_pdf": "✅ Genera PDF",
        "pdf_generato": "Documento registrato con successo!",
        "conserva_credenziali": "⚠️ Conserva queste informazioni",
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
        "titolo_candidatura": " CANDIDATURA SPONTANEA",
        "sottotitolo_candidatura": "Trasmetti i tuoi dati per una futura assunzione",
        "invia_candidatura": "Invia candidatura",
        "i_miei_dati": "👤 I Miei Dati Personali"
    },
    "en": {
        "titolo": "🏭 PROACIER - HUMAN RESOURCES MANAGEMENT",
        "sottotitolo": "Recruitment System - Senegal",
        "lingua": "Language",
        "nuova_assunzione": "➕ New Hiring",
        "candidatura_spontanea": "📩 Spontaneous Application",
        "area_lavoratore": "👤 Worker Area",
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
        "i_miei_dati": "👤 My Personal Data"
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
# STEP DEL FORMULARIO
# ============================================
def step_1_personale_famiglia(lingua):
    st.subheader(get_testo("step_1", lingua))
    cognome = st.text_input("Nom de famille *", key="s1_cognome")
    nome = st.text_input("Prénom *", key="s1_nome")
    data_nascita = st.date_input("Date de naissance", key="s1_data")
    luogo_nascita = st.text_input("Lieu de naissance", key="s1_luogo")
    sesso = st.selectbox("Sexe", ["M", "F"], key="s1_sesso")
    stato_civile = st.selectbox("État civil", ["Célibataire", "Marié", "Divorcé", "Veuf"], key="s1_stato")
    num_figli = st.number_input("Nombre d'enfants", min_value=0, key="s1_figli")
    return {"cognome": cognome, "nome": nome, "data_nascita": data_nascita, "luogo_nascita": luogo_nascita, "sesso": sesso, "stato_civile": stato_civile, "num_figli": num_figli}

def step_2_residenza_documenti(lingua):
    st.subheader(get_testo("step_2", lingua))
    indirizzo = st.text_input("Adresse", key="s2_indirizzo")
    quartiere = st.text_input("Quartier", key="s2_quartiere")
    citta = st.text_input("Ville", value="Thiès", key="s2_citta")
    telefono_1 = st.text_input("Téléphone 1 *", key="s2_tel1")
    telefono_2 = st.text_input("Téléphone 2", key="s2_tel2")
    email = st.text_input("Email", key="s2_email")
    cni = st.text_input("Numéro CNI *", key="s2_cni")
    return {"indirizzo": indirizzo, "quartiere": quartiere, "citta": citta, "telefono_1": telefono_1, "telefono_2": telefono_2, "email": email, "cni": cni}

def step_3_esperienza(lingua):
    st.subheader(get_testo("step_3", lingua))
    mansione_1 = st.text_input("Poste précédent 1", key="s3_mansione1")
    azienda_1 = st.text_input("Entreprise 1", key="s3_azienda1")
    return {"mansione_1": mansione_1, "azienda_1": azienda_1}

def step_4_competenze_permesso(lingua):
    st.subheader(get_testo("step_4", lingua))
    patente = st.selectbox("Permis de conduire", ["Aucun", "A", "B", "C", "D"], key="s4_patente")
    return {"patente": patente}

def step_5_medico(lingua):
    st.subheader(get_testo("step_5", lingua))
    gruppo = st.selectbox("Groupe sanguin", ["A", "B", "AB", "O"], key="s5_gruppo")
    rh = st.selectbox("Rh", ["+", "-"], key="s5_rh")
    return {"gruppo_sanguigno": gruppo, "rh": rh}

def step_6_emergenza_validazione(lingua):
    st.subheader(get_testo("step_6", lingua))
    em_nome = st.text_input("Nom du contact", key="s6_nome")
    em_parentela = st.text_input("Relation", key="s6_parentela")
    em_telefono = st.text_input("Téléphone", key="s6_telefono")
    conferma = st.checkbox("Je confirme l'exactitude des informations *", key="s6_conferma")
    return {"emergenza_nome": em_nome, "emergenza_parentela": em_parentela, "emergenza_telefono": em_telefono, "conferma": conferma}

# ============================================
# PAGINA CANDIDATURA SPONTANEA
# ============================================
def pagina_candidatura_spontanea(lingua):
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.info("⚠️ Ceci n'est PAS un contrat d'embauche, mais une transmission de données pour une éventuelle future embauche et pour le paiement des salaires des journaliers.")
    st.markdown("---")
    
    with st.form("form_candidatura", clear_on_submit=True):
        cognome = st.text_input("Nom *")
        nome = st.text_input("Prénom *")
        telefono = st.text_input("Téléphone *")
        email = st.text_input("Email")
        cni = st.text_input("Numéro CNI *")
        mansione = st.text_input("Poste souhaité")
        
        submitted = st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True)
        
        if submitted:
            if cognome and nome and telefono and cni:
                dati = {
                    "id": genera_codice(),
                    "cognome": cognome,
                    "nome": nome,
                    "telefono": telefono,
                    "email": email,
                    "cni": cni,
                    "mansione": mansione,
                    "data_invio": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                if salva_su_google_sheet(dati, GOOGLE_SCRIPT_URL_CANDIDATURE, "append"):
                    st.success("✅ Candidature envoyée avec succès!")
                else:
                    st.error("Erreur de connexion")
            else:
                st.error("Veuillez remplir tous les champs obligatoires")

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
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'dati_form' not in st.session_state:
        st.session_state.dati_form = {}

    lingua = st.session_state.lingua

    with st.sidebar:
        st.image(LOGO_URL, use_column_width=True)
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
            if st.button("🚪 Déconnexion", key="btn_logout"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.pagina = 'home'
                st.rerun()
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

    # ROUTING PAGINE
    if st.session_state.pagina == 'home':
        st.title(" PROACIER SN")
        st.markdown("### Système de Gestion des Ressources Humaines")
        st.info("Utilisez le menu à gauche pour naviguer")

    elif st.session_state.pagina == 'registrazione':
        pagina_registrazione_multi_step(lingua)

    elif st.session_state.pagina == 'candidatura':
        pagina_candidatura_spontanea(lingua)

    elif st.session_state.pagina == 'login_lavoratore':
        st.title(get_testo("area_lavoratore", lingua))
        codice = st.text_input("Code d'accès", key="login_codice")
        pin = st.text_input("PIN", type="password", key="login_pin")
        if st.button("Connexion", type="primary"):
            st.warning("Fonctionnalité en cours de développement")

    elif st.session_state.pagina == 'area_lavoratore':
        st.title(get_testo("i_miei_dati", lingua))
        st.warning("Pour toute modification, contactez l'administration")

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

def pagina_registrazione_multi_step(lingua):
    step = st.session_state.step
    st.progress(step / 6)
    st.markdown(f"**Étape {step} sur 6**")
    st.markdown("---")

    if step == 1:
        dati_step = step_1_personale_famiglia(lingua)
    elif step == 2:
        dati_step = step_2_residenza_documenti(lingua)
    elif step == 3:
        dati_step = step_3_esperienza(lingua)
    elif step == 4:
        dati_step = step_4_competenze_permesso(lingua)
    elif step == 5:
        dati_step = step_5_medico(lingua)
    elif step == 6:
        dati_step = step_6_emergenza_validazione(lingua)

    st.session_state.dati_form.update(dati_step)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if step > 1 and st.button(get_testo("indietro", lingua), use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with col2:
        if step < 6:
            if st.button(get_testo("continua", lingua), type="primary", use_container_width=True):
                if step == 1 and (not dati_step.get('cognome') or not dati_step.get('nome')):
                    st.error(get_testo("errore_obbligatori", lingua))
                    return
                if step == 2 and (not dati_step.get('cni') or not dati_step.get('telefono_1')):
                    st.error(get_testo("errore_obbligatori", lingua))
                    return
                st.session_state.step += 1
                st.rerun()
        else:
            if dati_step.get('conferma'):
                if st.button(get_testo("genera_pdf", lingua), type="primary", use_container_width=True):
                    genera_e_salva_pdf(st.session_state.dati_form, lingua)
            else:
                st.warning("Veuillez cocher la case de confirmation")

def genera_e_salva_pdf(dati, lingua):
    codice = genera_codice()
    pin = genera_pin()
    dati_finali = {
        "id": codice,
        "codice": codice,
        "pin": pin,
        "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"),
        **dati,
        "stato_firma": "Da firmare"
    }

    if salva_su_google_sheet(dati_finali, GOOGLE_SCRIPT_URL_ASSUNZIONI, "append"):
        st.success(f"✅ {get_testo('pdf_generato', lingua)}")
        pdf_bytes = genera_pdf_lavoratore(dati_finali)
        st.warning(get_testo('conserva_credenziali', lingua))
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**{get_testo('codice_accesso', lingua)}:** {codice}")
        with c2:
            st.info(f"**{get_testo('pin_accesso', lingua)}:** {pin}")
        st.download_button(
            label=f"📥 {get_testo('scarica', lingua)} PDF",
            data=pdf_bytes,
            file_name=f"Proacier_{codice}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="btn_dl"
        )
        st.session_state.step = 1
        st.session_state.dati_form = {}
    else:
        st.error("Erreur de connexion à Google Sheets.")

if __name__ == "__main__":
    main()
