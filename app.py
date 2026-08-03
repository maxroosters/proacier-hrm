# -*- coding: utf-8 -*-
"""PROACIER - HRM - Versione FINALE"""
import streamlit as st
import requests
from datetime import datetime
import random
from fpdf import FPDF
import pandas as pd

# CONFIG
st.set_page_config(page_title="Proacier - RH", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")

# CSS SIDEBAR VERDE
st.markdown("""
<style>
[data-testid="stSidebar"] {background-color: #5EA529 !important;}
[data-testid="stSidebar"] * {color: white !important;}
[data-testid="stSidebar"] button {background-color: rgba(255,255,255,0.1) !important; color: white !important; border: 1px solid rgba(255,255,255,0.3) !important;}
[data-testid="stSidebar"] button:hover {background-color: rgba(255,255,255,0.2) !important;}
</style>
""", unsafe_allow_html=True)

LOGO_URL = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png"
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbxt39icOxVevvtes1ne1tK2ZTrw-uXldRIppSDgJj8YPwb13hOMRN6tOT0KJjB9vYF6MQ/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycby1isMOz1fKTptR83six7_3OMaDgcx8_LRn3rLkD9_wCRHdxu1GCgQr3aR9FxaSr3Q-/exec"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# TRADUZIONI
TRADUZIONI = {
    'fr': {
        'titolo': '🏭 PROACIER - GESTION DES RESSOURCES HUMAINES',
        'sottotitolo': 'Système de Recrutement - Sénégal',
        'home_punto1': ' Transmission de données pour nouveaux travailleurs',
        'home_punto2': '📨 Candidatures spontanées',
        'home_punto3': '👤 Espace personnel travailleur',
        'home_punto4': '💰 Paiement des journaliers',
        'btn_nouvelle_embauche': '📝 Nouvelle Embauche (Complet)',
        'btn_candidature': '📄 Candidature Spontanée',
        'btn_espace': ' Espace Travailleur',
        'btn_dashboard': '📊 Tableau de Bord',
        'giornalieri_titolo': 'Déjà travailleur?',
        'giornalieri_desc': 'Accédez à votre espace personnel',
        'nuovo_giornaliero_titolo': 'Nouveau / Journalier?',
        'nuovo_giornaliero_desc': 'Transmettez vos données (pas un contrat)',
        'login_btn': '🔐 Connexion à mon espace',
        'trasmissione_btn': ' Transmettre mes données',
        'lingua': 'Langue', 'logout': 'Déconnexion', 'benvenuto': 'Bienvenue',
        'cognome': 'Nom', 'nome': 'Prénom(s)', 'data_nascita': 'Date de naissance',
        'luogo_nascita': 'Lieu de naissance', 'nazionalita': 'Nationalité',
        'sesso': 'Sexe', 'maschile': 'Masculin', 'femminile': 'Féminin',
        'stato_civile': 'État civil', 'celibe': 'Célibataire', 'coniugato': 'Marié(e)',
        'numero_mogli': "Nombre d'épouses", 'figli_totale': "Nombre total d'enfants",
        'indirizzo': 'Adresse', 'quartiere': 'Quartier', 'comune': 'Commune',
        'regione_senegal': 'Région', 'telefono_1': 'Téléphone 1', 'cni': 'N° CNI',
        'css': 'N° CSS', 'mansione_1': 'Poste / Fonction', 'salario': 'Salaire (FCFA)',
        'wave_orange': 'N° Wave / Orange Money', 'patente': 'Permis de conduire',
        'gruppo_sanguigno': 'Groupe sanguin', 'rh': 'Rh', 'allergie': 'Allergies',
        'idoneita': 'Aptitude médicale', 'emergenza_nome': 'Contact urgence',
        'emergenza_tel': 'Tél urgence', 'certifico_checkbox': "Je certifie l'exactitude",
        'genera_pdf': '📄 Générer PDF & Accepter', 'pdf_generato': 'Enregistrement réussi!',
        'conserva_credenziali': '️ CONSERVEZ CES IDENTIFIANTS',
        'code_acces': "Code d'accès", 'pin_acces': "PIN d'accès",
        'cand_titolo': 'CANDIDATURE SPONTANÉE',
        'cand_sottotitolo': 'Rejoignez PROACIER. Remplissez ce formulaire.',
        'cand_info': "Ceci n'est PAS un contrat, seulement votre candidature.",
        'cand_email': 'Email', 'cand_mansione': 'Poste recherché',
        'cand_studi': 'Niveau études', 'cand_skills': 'Compétences / Skills',
        'cand_esperienze': 'Années expérience', 'cand_motivazione': 'Pourquoi PROACIER?',
        'cand_disponibilite': 'Disponibilité', 'cand_invia': '📤 Envoyer candidature',
        'opt_contabile': 'Comptabilité', 'opt_tecnico': 'Technicien',
        'opt_operaio': 'Ouvrier', 'opt_autista': 'Chauffeur', 'opt_altro': 'Autre',
        'opt_media': 'École moyenne', 'opt_diploma': 'Baccalauréat',
        'opt_laurea': 'Licence/Master', 'opt_prof': 'Formation pro',
    },
    'it': {
        'titolo': '🏭 PROACIER - GESTIONE RISORSE UMANE',
        'sottotitolo': 'Sistema di Reclutamento - Senegal',
        'home_punto1': '📋 Trasmissione dati nuovi lavoratori',
        'home_punto2': '📨 Candidature spontanee',
        'home_punto3': '👤 Spazio personale lavoratore',
        'home_punto4': '💰 Pagamento giornalieri',
        'btn_nouvelle_embauche': ' Nuova Assunzione (Completo)',
        'btn_candidature': '📄 Candidatura Spontanea',
        'btn_espace': ' Spazio Lavoratore',
        'btn_dashboard': '📊 Dashboard',
        'giornalieri_titolo': 'Già lavoratore?',
        'giornalieri_desc': 'Accedi al tuo spazio',
        'nuovo_giornaliero_titolo': 'Nuovo / Giornaliero?',
        'nuovo_giornaliero_desc': 'Trasmetti dati (non contratto)',
        'login_btn': '🔐 Accedi al mio spazio',
        'trasmissione_btn': '📝 Trasmetti i miei dati',
        'lingua': 'Lingua', 'logout': 'Logout', 'benvenuto': 'Benvenuto',
        'cognome': 'Cognome', 'nome': 'Nome', 'data_nascita': 'Data nascita',
        'luogo_nascita': 'Luogo nascita', 'nazionalita': 'Nazionalità',
        'sesso': 'Sesso', 'maschile': 'Maschile', 'femminile': 'Femminile',
        'stato_civile': 'Stato civile', 'celibe': 'Celibe', 'coniugato': 'Coniugato',
        'numero_mogli': 'Numero mogli', 'figli_totale': 'Totale figli',
        'indirizzo': 'Indirizzo', 'quartiere': 'Quartiere', 'comune': 'Comune',
        'regione_senegal': 'Regione', 'telefono_1': 'Telefono 1', 'cni': 'N° CNI',
        'css': 'N° CSS', 'mansione_1': 'Mansione', 'salario': 'Salario (FCFA)',
        'wave_orange': 'N° Wave / Orange Money', 'patente': 'Patente',
        'gruppo_sanguigno': 'Gruppo sanguigno', 'rh': 'Rh', 'allergie': 'Allergie',
        'idoneita': 'Idoneità medica', 'emergenza_nome': 'Contatto emergenza',
        'emergenza_tel': 'Tel emergenza', 'certifico_checkbox': 'Certifico esattezza',
        'genera_pdf': ' Genera PDF & Accetta', 'pdf_generato': 'Registrazione riuscita!',
        'conserva_credenziali': '⚠️ CONSERVA CREDENZIALI',
        'code_acces': 'Codice accesso', 'pin_acces': 'PIN accesso',
        'cand_titolo': 'CANDIDATURA SPONTANEA',
        'cand_sottotitolo': 'Unisciti a PROACIER. Compila il modulo.',
        'cand_info': 'NON è un contratto, solo candidatura.',
        'cand_email': 'Email', 'cand_mansione': 'Ruolo richiesto',
        'cand_studi': 'Titolo studi', 'cand_skills': 'Competenze / Skills',
        'cand_esperienze': 'Anni esperienza', 'cand_motivazione': 'Perché PROACIER?',
        'cand_disponibilite': 'Disponibilità', 'cand_invia': '📤 Invia candidatura',
        'opt_contabile': 'Contabilità', 'opt_tecnico': 'Tecnico',
        'opt_operaio': 'Operaio', 'opt_autista': 'Autista', 'opt_altro': 'Altro',
        'opt_media': 'Licenza media', 'opt_diploma': 'Diploma',
        'opt_laurea': 'Laurea', 'opt_prof': 'Formazione professionale',
    },
    'en': {
        'titolo': '🏭 PROACIER - HUMAN RESOURCES',
        'sottotitolo': 'Recruitment System - Senegal',
        'home_punto1': ' Data transmission new workers',
        'home_punto2': '📨 Spontaneous applications',
        'home_punto3': '👤 Personal worker space',
        'home_punto4': '💰 Daily workers payment',
        'btn_nouvelle_embauche': '📝 New Hiring (Complete)',
        'btn_candidature': ' Spontaneous Application',
        'btn_espace': '👤 Worker Space',
        'btn_dashboard': '📊 Dashboard',
        'giornalieri_titolo': 'Already a worker?',
        'giornalieri_desc': 'Access your space',
        'nuovo_giornaliero_titolo': 'New / Daily worker?',
        'nuovo_giornaliero_desc': 'Submit data (not contract)',
        'login_btn': '🔐 Login to my space',
        'trasmissione_btn': ' Submit my data',
        'lingua': 'Language', 'logout': 'Logout', 'benvenuto': 'Welcome',
        'cognome': 'Surname', 'nome': 'First Name', 'data_nascita': 'Date of birth',
        'luogo_nascita': 'Place of birth', 'nazionalita': 'Nationality',
        'sesso': 'Gender', 'maschile': 'Male', 'femminile': 'Female',
        'stato_civile': 'Marital status', 'celibe': 'Single', 'coniugato': 'Married',
        'numero_mogli': 'Number of wives', 'figli_totale': 'Total children',
        'indirizzo': 'Address', 'quartiere': 'District', 'comune': 'Municipality',
        'regione_senegal': 'Region', 'telefono_1': 'Phone 1', 'cni': 'ID Number',
        'css': 'Social Security', 'mansione_1': 'Position', 'salario': 'Salary (FCFA)',
        'wave_orange': 'Wave / Orange Money', 'patente': 'License',
        'gruppo_sanguigno': 'Blood type', 'rh': 'Rh', 'allergie': 'Allergies',
        'idoneita': 'Medical fitness', 'emergenza_nome': 'Emergency contact',
        'emergenza_tel': 'Emergency phone', 'certifico_checkbox': 'I certify accuracy',
        'genera_pdf': '📄 Generate PDF & Accept', 'pdf_generato': 'Registration successful!',
        'conserva_credenziali': '⚠️ SAVE CREDENTIALS',
        'code_acces': 'Access code', 'pin_acces': 'PIN access',
        'cand_titolo': 'SPONTANEOUS APPLICATION',
        'cand_sottotitolo': 'Join PROACIER. Fill the form.',
        'cand_info': 'NOT a contract, only application.',
        'cand_email': 'Email', 'cand_mansione': 'Desired position',
        'cand_studi': 'Education level', 'cand_skills': 'Skills',
        'cand_esperienze': 'Years experience', 'cand_motivazione': 'Why PROACIER?',
        'cand_disponibilite': 'Availability', 'cand_invia': '📤 Submit application',
        'opt_contabile': 'Accounting', 'opt_tecnico': 'Technician',
        'opt_operaio': 'Worker', 'opt_autista': 'Driver', 'opt_altro': 'Other',
        'opt_media': 'Middle school', 'opt_diploma': 'High school',
        'opt_laurea': 'Degree', 'opt_prof': 'Vocational training',
    }
}

def get_testo(chiave):
    return TRADUZIONI.get(st.session_state.lingua, TRADUZIONI['fr']).get(chiave, chiave)

# SESSION STATE
if 'pagina' not in st.session_state: st.session_state.pagina = 'home'
if 'lingua' not in st.session_state: st.session_state.lingua = 'fr'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'step' not in st.session_state: st.session_state.step = 1
if 'dati_form' not in st.session_state: st.session_state.dati_form = {}
if 'admin_logged' not in st.session_state: st.session_state.admin_logged = False

def genera_codice(): return f"THS-{datetime.now().year}-{random.randint(1000, 9999)}"
def genera_pin(): return str(random.randint(1000, 9999))

def salva_su_google_sheets(script_url, dati, action="append"):
    try:
        response = requests.post(script_url, json={"action": action, "row": dati}, headers={"Content-Type": "application/json"}, timeout=30)
        return response.status_code == 200
    except: return False

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
    pdf.campo_doppio("CNI:", dati.get('cni', ''), "CSS:", dati.get('css', ''),)
    pdf.ln(3)
    pdf.sezione("4. EMPLOI & SALAIRE")
    pdf.campo_doppio("Poste:", dati.get('mansione_1', ''), "Salaire:", f"{dati.get('salario', '')} FCFA")
    pdf.campo_doppio("Wave/OM:", dati.get('wave_orange', ''), "Permis:", dati.get('patente', ''))
    pdf.ln(3)
    pdf.sezione("5. MEDICAL & URGENCE")
    pdf.campo_doppio("Groupe:", f"{dati.get('gruppo_sanguigno', '')} {dati.get('rh', '')}", "Aptitude:", dati.get('idoneita', ''))
    pdf.campo_doppio("Contact:", dati.get('emergenza_nome', ''), "Tel:", dati.get('emergenza_tel', ''))
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

# STEP FORM ASSUNZIONE
def step_1():
    st.subheader("1. IDENTITÉ & FAMILLE")
    col1, col2 = st.columns(2)
    with col1:
        cognome = st.text_input(get_testo('cognome'), value=st.session_state.dati_form.get('cognome', ''), key='s1_cognome')
        nome = st.text_input(get_testo('nome'), value=st.session_state.dati_form.get('nome', ''), key='s1_nome')
        st.markdown(f"**{get_testo('data_nascita')}**")
        cg, cm, ca = st.columns(3)
        with cg: giorno = st.selectbox("Jour", range(1, 32), index=st.session_state.dati_form.get('giorno', 0), key='s1_g')
        with cm: mese = st.selectbox("Mois", range(1, 13), index=st.session_state.dati_form.get('mese', 0), key='s1_m')
        with ca: anno = st.selectbox("Année", range(1950, 2010), index=st.session_state.dati_form.get('anno', 30), key='s1_a')
        data_nascita_str = f"{giorno:02d}/{mese:02d}/{anno}"
        luogo_nascita = st.text_input(get_testo('luogo_nascita'), value=st.session_state.dati_form.get('luogo_nascita', ''), key='s1_luogo')
        nazionalita = st.text_input(get_testo('nazionalita'), value=st.session_state.dati_form.get('nazionalita', 'Sénégalaise'), key='s1_naz')
    with col2:
        sesso = st.selectbox(get_testo('sesso'), [get_testo('maschile'), get_testo('femminile')], index=0 if st.session_state.dati_form.get('sesso') != get_testo('femminile') else 1, key='s1_sesso')
        stato_civile = st.selectbox(get_testo('stato_civile'), [get_testo('celibe'), get_testo('coniugato'), "Divorcé(e)", "Veuf(ve)"], index=0 if st.session_state.dati_form.get('stato_civile') == get_testo('celibe') else 1, key='s1_stato')
        numero_mogli, dettagli_mogli = 0, ""
        if stato_civile == get_testo('coniugato'):
            numero_mogli = st.number_input(get_testo('numero_mogli'), min_value=1, max_value=4, value=st.session_state.dati_form.get('numero_mogli', 1), key='s1_mogli')
            dettagli = []
            for i in range(1, numero_mogli + 1):
                st.markdown(f"**Épouse {i}**")
                c_res, c_fig = st.columns(2)
                with c_res: res = st.text_input(f"Lieu résidence épouse {i}", value=st.session_state.dati_form.get(f'res_moglie_{i}', ''), key=f's1_res_{i}')
                with c_fig: fig = st.number_input(f"Nombre enfants épouse {i}", min_value=0, value=st.session_state.dati_form.get(f'figli_moglie_{i}', 0), key=f's1_fig_{i}')
                dettagli.append(f"Épouse {i}: {res} ({fig} enfants)")
            dettagli_mogli = " | ".join(dettagli)
        figli_totale = st.number_input(get_testo('figli_totale'), min_value=0, value=st.session_state.dati_form.get('figli_totale', 0), key='s1_figli_tot')
    st.session_state.dati_form.update({'cognome': cognome, 'nome': nome, 'data_nascita': data_nascita_str, 'luogo_nascita': luogo_nascita,
        'nazionalita': nazionalita, 'sesso': sesso, 'stato_civile': stato_civile, 'numero_mogli': numero_mogli,
        'dettagli_mogli': dettagli_mogli, 'figli_totale': figli_totale, 'giorno': giorno, 'mese': mese, 'anno': anno})

def step_2():
    st.subheader("2. COORDONNÉES")
    col1, col2 = st.columns(2)
    with col1:
        indirizzo = st.text_input(get_testo('indirizzo'), value=st.session_state.dati_form.get('indirizzo', ''), key='s2_ind')
        quartiere = st.text_input(get_testo('quartiere'), value=st.session_state.dati_form.get('quartiere', ''), key='s2_quart')
        comune = st.text_input(get_testo('comune'), value=st.session_state.dati_form.get('comune', ''), key='s2_com')
    with col2:
        regione_senegal = st.text_input(get_testo('regione_senegal'), value=st.session_state.dati_form.get('regione_senegal', ''), key='s2_reg')
        telefono_1 = st.text_input(get_testo('telefono_1'), value=st.session_state.dati_form.get('telefono_1', ''), key='s2_tel1')
        telefono_2 = st.text_input("Téléphone 2", value=st.session_state.dati_form.get('telefono_2', ''), key='s2_tel2')
        telefono_3 = st.text_input("Téléphone 3", value=st.session_state.dati_form.get('telefono_3', ''), key='s2_tel3')
    st.session_state.dati_form.update({'indirizzo': indirizzo, 'quartiere': quartiere, 'comune': comune,
        'regione_senegal': regione_senegal, 'telefono_1': telefono_1, 'telefono_2': telefono_2, 'telefono_3': telefono_3})

def step_3():
    st.subheader("3. DOCUMENTS OFFICIELS")
    col1, col2 = st.columns(2)
    with col1:
        cni = st.text_input(get_testo('cni'), value=st.session_state.dati_form.get('cni', ''), key='s3_cni')
        css = st.text_input(get_testo('css'), value=st.session_state.dati_form.get('css', ''), key='s3_css')
    with col2:
        nif = st.text_input("NIF", value=st.session_state.dati_form.get('nif', ''), key='s3_nif')
        ipres = st.text_input("IPRES", value=st.session_state.dati_form.get('ipres', ''), key='s3_ipres')
    st.session_state.dati_form.update({'cni': cni, 'css': css, 'nif': nif, 'ipres': ipres})

def step_4():
    st.subheader("4. EMPLOI & SALAIRE")
    col1, col2 = st.columns(2)
    with col1:
        mansione_1 = st.text_input(get_testo('mansione_1'), value=st.session_state.dati_form.get('mansione_1', ''), key='s4_man')
        luogo_lavoro = st.text_input("Lieu de travail", value=st.session_state.dati_form.get('luogo_lavoro', ''), key='s4_luogo')
        reparto = st.text_input("Département", value=st.session_state.dati_form.get('reparto', ''), key='s4_rep')
    with col2:
        data_inizio_1 = st.text_input("Date début", value=st.session_state.dati_form.get('data_inizio_1', ''), key='s4_data')
        salario = st.text_input(get_testo('salario'), value=st.session_state.dati_form.get('salario', ''), key='s4_sal')
        wave_orange = st.text_input(get_testo('wave_orange'), value=st.session_state.dati_form.get('wave_orange', ''), key='s4_wave')
        pagamento = st.selectbox("Type paiement", ["Horaire", "Journalier", "Mensuel"], key='s4_pag')
    st.session_state.dati_form.update({'mansione_1': mansione_1, 'luogo_lavoro': luogo_lavoro, 'reparto': reparto,
        'data_inizio_1': data_inizio_1, 'salario': salario, 'wave_orange': wave_orange, 'pagamento': pagamento})

def step_5():
    st.subheader("5. COMPÉTENCES & SANTÉ")
    col1, col2 = st.columns(2)
    with col1:
        categoria_competenza = st.text_input("Catégorie compétence", value=st.session_state.dati_form.get('categoria_competenza', ''), key='s5_cat')
        dettaglio_competenza = st.text_input("Détail compétence", value=st.session_state.dati_form.get('dettaglio_competenza', ''), key='s5_det')
        patente = st.text_input(get_testo('patente'), value=st.session_state.dati_form.get('patente', ''), key='s5_pat')
    with col2:
        gruppo_sanguigno = st.selectbox(get_testo('gruppo_sanguigno'), ["A", "B", "AB", "O"], key='s5_gruppo')
        rh = st.selectbox(get_testo('rh'), ["+", "-"], key='s5_rh')
        allergie = st.text_input(get_testo('allergie'), value=st.session_state.dati_form.get('allergie', ''), key='s5_all')
        idoneita = st.selectbox(get_testo('idoneita'), ["Apte", "Apte avec restriction", "Inapte"], key='s5_ido')
    st.session_state.dati_form.update({'categoria_competenza': categoria_competenza, 'dettaglio_competenza': dettaglio_competenza,
        'patente': patente, 'gruppo_sanguigno': gruppo_sanguigno, 'rh': rh, 'allergie': allergie, 'idoneita': idoneita})

def step_6():
    st.subheader("6. URGENCE & CONFIRMATION")
    col1, col2 = st.columns(2)
    with col1:
        emergenza_nome = st.text_input(get_testo('emergenza_nome'), value=st.session_state.dati_form.get('emergenza_nome', ''), key='s6_em_nome')
        emergenza_parentela = st.text_input("Lien parenté", value=st.session_state.dati_form.get('emergenza_parentela', ''), key='s6_em_par')
    with col2:
        emergenza_tel = st.text_input(get_testo('emergenza_tel'), value=st.session_state.dati_form.get('emergenza_tel', ''), key='s6_em_tel')
        emergenza_indirizzo = st.text_input("Adresse urgence", value=st.session_state.dati_form.get('emergenza_indirizzo', ''), key='s6_em_ind')
    st.markdown("---")
    st.info("Je certifie l'exactitude des informations et accepte les conditions.")
    certifica = st.checkbox(get_testo('certifico_checkbox'), value=st.session_state.dati_form.get('certifica', False), key='s6_conf')
    st.session_state.dati_form.update({'emergenza_nome': emergenza_nome, 'emergenza_parentela': emergenza_parentela,
        'emergenza_tel': emergenza_tel, 'emergenza_indirizzo': emergenza_indirizzo, 'certifica': certifica})

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
        if step > 1 and st.button("← Retour", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with col2:
        if step < 6:
            if st.button("Suivant →", type="primary", use_container_width=True):
                st.session_state.step += 1
                st.rerun()
        else:
            if st.session_state.dati_form.get('certifica'):
                if st.button(get_testo('genera_pdf'), type="primary", use_container_width=True):
                    codice = genera_codice(); pin = genera_pin()
                    dati_finali = {"id": codice, "codice": codice, "pin": pin,
                        "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        **st.session_state.dati_form, "tipo": "Assunzione"}
                    if salva_su_google_sheets(GOOGLE_SCRIPT_URL_ASSUNZIONI, dati_finali, action="append"):
                        st.success(get_testo('pdf_generato'))
                        pdf_bytes = genera_pdf_lavoratore(dati_finali)
                        st.warning(get_testo('conserva_credenziali'))
                        c1, c2 = st.columns(2)
                        with c1: st.info(f"**{get_testo('code_acces')}:** {codice}")
                        with c2: st.info(f"**{get_testo('pin_acces')}:** {pin}")
                        st.download_button(label=f"📥 Télécharger PDF", data=pdf_bytes,
                            file_name=f"Fiche_{st.session_state.dati_form.get('cognome', '')}.pdf", mime="application/pdf")
                        st.ballo()
                        st.session_state.dati_form = {}; st.session_state.step = 1
                        st.rerun()
            else: st.warning("Veuillez cocher la case")

def pagina_candidatura_spontanea():
    st.title(get_testo('cand_titolo'))
    st.markdown(get_testo('cand_sottotitolo'))
    st.info(get_testo('cand_info'))
    
    with st.form("form_candidatura", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            c_cognome = st.text_input(get_testo('cognome'), key='c_cognome')
            c_nome = st.text_input(get_testo('nome'), key='c_nome')
            c_email = st.text_input(get_testo('cand_email'), key='c_email')
            c_tel = st.text_input(get_testo('telefono_1'), key='c_tel')
        with col2:
            c_indirizzo = st.text_input(get_testo('indirizzo'), key='c_ind')
            c_comune = st.text_input(get_testo('comune'), key='c_com')
            c_regione = st.text_input(get_testo('regione_senegal'), key='c_reg')
            c_mansione = st.selectbox(get_testo('cand_mansione'), [
                get_testo('opt_contabile'), get_testo('opt_tecnico'),
                get_testo('opt_operaio'), get_testo('opt_autista'), get_testo('opt_altro')
            ], key='c_man')
        
        c_studi = st.selectbox(get_testo('cand_studi'), [
            get_testo('opt_media'), get_testo('opt_diploma'),
            get_testo('opt_laurea'), get_testo('opt_prof')
        ], key='c_studi')
        
        c_esperienze = st.number_input(get_testo('cand_esperienze'), min_value=0, max_value=50, value=0, key='c_exp')
        c_skills = st.text_area(get_testo('cand_skills'), key='c_skills')
        c_motivazione = st.text_area(get_testo('cand_motivazione'), key='c_mot')
        c_disponibilite = st.selectbox(get_testo('cand_disponibilite'), ["Immédiate", "1 semaine", "2 semaines", "1 mois", "Autre"], key='c_disp')
        
        submitted = st.form_submit_button(get_testo('cand_invia'), type="primary", use_container_width=True)
        if submitted:
            if c_cognome and c_nome and c_email and c_tel:
                dati = {"id": f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}",
                    "cognome": c_cognome, "nome": c_nome, "email": c_email, "telefono": c_tel,
                    "indirizzo": c_indirizzo, "comune": c_comune, "regione": c_regione,
                    "mansione_richiesta": c_mansione, "studi": c_studi,
                    "esperienza_anno": c_esperienze, "skills": c_skills,
                    "motivazione": c_motivazione, "disponibilite": c_disponibilite}
                if salva_su_google_sheets(GOOGLE_SCRIPT_URL_CANDIDATURE, dati):
                    st.success("✅ Candidature envoyée!")
                    st.ballo()
            else: st.error("Champs obligatoires")

def pagina_espace_travailleur():
    st.title(get_testo('btn_espace'))
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 👤 {get_testo('giornalieri_titolo')}")
        st.info(get_testo('giornalieri_desc'))
        if st.button(get_testo('login_btn'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'login_lavoratore'
            st.rerun()
    with col2:
        st.markdown(f"### 📝 {get_testo('nuovo_giornaliero_titolo')}")
        st.info(get_testo('nuovo_giornaliero_desc'))
        if st.button(get_testo('trasmissione_btn'), use_container_width=True, type="primary"):
            st.session_state.pagina = 'registrazione'
            st.session_state.step = 1
            st.session_state.dati_form = {}
            st.rerun()

def pagina_login_lavoratore():
    st.title("Connexion à mon espace")
    with st.form("login_form"):
        codice = st.text_input("Code d'accès")
        pin = st.text_input("PIN personnel", type="password")
        submitted = st.form_submit_button("Se connecter", type="primary")
        if submitted and codice and pin:
            st.session_state.logged_in = True
            st.session_state.user_type = 'lavoratore'
            st.session_state.codice_operatore = codice
            st.session_state.pin_operatore = pin
            st.session_state.pagina = 'area_lavoratore'
            st.success("Connecté!")
            st.rerun()
    if st.button("Retour"):
        st.session_state.pagina = 'espace_travailleur'
        st.rerun()

def pagina_area_lavoratore():
    if not st.session_state.get('logged_in'):
        st.error("Accès refusé")
        return
    st.title("Mes Données")
    st.success(f"Code: {st.session_state.codice_operatore}")
    st.warning("Pour modifications, contactez l'administration")
    if st.button(get_testo('logout')):
        st.session_state.logged_in = False
        st.session_state.pagina = 'home'
        st.rerun()

def pagina_dashboard():
    st.title(get_testo('btn_dashboard'))
    if not st.session_state.get('admin_logged'):
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            if pwd == PASSWORD_DASHBOARD:
                st.session_state.admin_logged = True
                st.success("Connecté admin")
                st.rerun()
    else:
        st.success("Administrateur")
        if st.button("Déconnexion"):
            st.session_state.admin_logged = False
            st.rerun()

# SIDEBAR
with st.sidebar:
    st.image(LOGO_URL, use_column_width=True)
    st.markdown("---")
    st.title(get_testo('titolo'))
    st.markdown(get_testo('sottotitolo'))
    st.markdown("---")
    
    lingua_sel = st.selectbox(get_testo('lingua'), ["Français", "Italiano", "English"],
        index=0 if st.session_state.lingua == 'fr' else (1 if st.session_state.lingua == 'it' else 2), key="sel_lingua")
    st.session_state.lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
    
    st.markdown("---")
    
    if st.button(get_testo('btn_nouvelle_embauche'), use_container_width=True):
        st.session_state.pagina = 'registrazione'
        st.session_state.step = 1
        st.session_state.dati_form = {}
        st.rerun()
    if st.button(get_testo('btn_candidature'), use_container_width=True):
        st.session_state.pagina = 'candidatura'
        st.rerun()
    if st.button(get_testo('btn_espace'), use_container_width=True):
        st.session_state.pagina = 'espace_travailleur'
        st.rerun()
    if st.button(get_testo('btn_dashboard'), use_container_width=True):
        st.session_state.pagina = 'dashboard'
        st.rerun()

# ROUTING
if st.session_state.pagina == 'home':
    st.title(" PROACIER SN")
    st.markdown("### Système de Gestion des Ressources Humaines")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{get_testo('home_punto1')}**\n\n**{get_testo('home_punto2')}**")
    with col2:
        st.markdown(f"**{get_testo('home_punto3')}**\n\n**{get_testo('home_punto4')}**")
elif st.session_state.pagina == 'registrazione':
    pagina_registrazione_multi_step()
elif st.session_state.pagina == 'candidatura':
    pagina_candidatura_spontanea()
elif st.session_state.pagina == 'espace_travailleur':
    pagina_espace_travailleur()
elif st.session_state.pagina == 'login_lavoratore':
    pagina_login_lavoratore()
elif st.session_state.pagina == 'area_lavoratore':
    pagina_area_lavoratore()
elif st.session_state.pagina == 'dashboard':
    pagina_dashboard()
