import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import random

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
    /* Sidebar background verde */
    [data-testid="stSidebar"] {
        background-color: #5EA529 !important;
    }
    
    /* Sidebar text bianco */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Pulsanti sidebar */
    [data-testid="stSidebar"] button {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    /* Hover pulsanti */
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255,255,255,0.2) !important;
    }
    
    /* Titolo sidebar */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# URL E CONFIGURAZIONI
# ============================================================================

# Logo da GitHub (root del repository)
LOGO_URL = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png"

# URL Google Apps Script
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbxt39icOxVevvtes1ne1tK2ZTrw-uXldRIppSDgJj8YPwb13hOMRN6tOT0KJjB9vYF6MQ/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycby1isMOz1fKTptR83six7_3OMaDgcx8_LRn3rLkD9_wCRHdxu1GCgQr3aR9FxaSr3Q-/exec"

# Password dashboard
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# URL condizioni
URL_CONDIZIONI = "https://www.proacier.sn/condizioni"

# ============================================================================
# TRADUZIONI
# ============================================================================

TRADUZIONI = {
    'fr': {
        'titolo': 'PROACIER - GESTION DES RESSOURCES HUMAINES',
        'sottotitolo': 'Système de Recrutement - Sénégal',
        'lingua': 'Langue',
        'benvenuto': 'Bienvenue',
        'home_desc_1': 'Transmission de données pour les nouveaux travailleurs et journaliers',
        'home_desc_2': 'Candidatures spontanées',
        'home_desc_3': 'Espace personnel travailleur',
        'home_desc_4': 'Paiement des journaliers',
        'home_titolo': 'Comment utiliser l\'application',
        'home_btn_1': 'Candidature Spontanée',
        'home_btn_2': 'Espace Travailleur',
        'home_btn_3': 'Tableau de Bord',
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
    },
    'it': {
        'titolo': 'PROACIER - GESTIONE RISORSE UMANE',
        'sottotitolo': 'Sistema di Reclutamento - Senegal',
        'lingua': 'Lingua',
        'benvenuto': 'Benvenuto',
        'home_desc_1': 'Trasmissione dati per nuovi lavoratori e giornalieri',
        'home_desc_2': 'Candidature spontanee',
        'home_desc_3': 'Spazio personale lavoratore',
        'home_desc_4': 'Pagamento giornalieri',
        'home_titolo': 'Come usare l\'applicazione',
        'home_btn_1': 'Candidatura Spontanea',
        'home_btn_2': 'Spazio Lavoratore',
        'home_btn_3': 'Dashboard',
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
    },
    'en': {
        'titolo': 'PROACIER - HUMAN RESOURCES',
        'sottotitolo': 'Recruitment System - Senegal',
        'lingua': 'Language',
        'benvenuto': 'Welcome',
        'home_desc_1': 'Data transmission for new workers and daily workers',
        'home_desc_2': 'Spontaneous applications',
        'home_desc_3': 'Personal worker space',
        'home_desc_4': 'Daily workers payment',
        'home_titolo': 'How to use the application',
        'home_btn_1': 'Spontaneous Application',
        'home_btn_2': 'Worker Space',
        'home_btn_3': 'Dashboard',
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

def genera_codice_operatore(cognome, nome, data_nascita):
    """Genera codice operatore: THS-AAAA-NNNN"""
    anno = datetime.now().year
    random_num = random.randint(1000, 9999)
    return f"THS-{anno}-{random_num}"

def genera_pin():
    """Genera PIN a 4 cifre"""
    return str(random.randint(1000, 9999))

def salva_su_google_sheets(script_url, dati, action="append"):
    """Invia dati a Google Apps Script"""
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
# PAGINA HOME - NUOVA STRUTTURA
# ============================================================================

def pagina_home():
    """Nuova homepage descrittiva"""
    st.title(get_testo('titolo', st.session_state.lingua))
    st.subheader(get_testo('sottotitolo', st.session_state.lingua))
    
    st.markdown("---")
    
    # Sezione: A cosa serve l'app
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
    
    # Sezione: Come usare l'app
    st.subheader(get_testo('home_titolo', st.session_state.lingua))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(get_testo('home_btn_1', st.session_state.lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'candidatura'
            st.rerun()
    
    with col2:
        if st.button(get_testo('home_btn_2', st.session_state.lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'espace_travailleur'
            st.rerun()
    
    with col3:
        if st.button(get_testo('home_btn_3', st.session_state.lingua), use_container_width=True):
            st.session_state.pagina = 'dashboard'
            st.rerun()

# ============================================================================
# PAGINA ESPACE TRAVAILLEUR - 2 PULSANTI
# ============================================================================

def pagina_espace_travailleur():
    """Pagina con 2 opzioni: Login spazio personale o Trasmissione dati"""
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
    """Login per accedere allo spazio personale"""
    st.title("Connexion à mon espace")
    
    with st.form("login_form"):
        codice = st.text_input("Code d'accès")
        pin = st.text_input("PIN personnel", type="password")
        submitted = st.form_submit_button("Se connecter", type="primary")
        
        if submitted:
            if codice and pin:
                # Verifica credenziali nel foglio Google
                try:
                    response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
                    if response.status_code == 200:
                        data = response.json()
                        df = pd.DataFrame(data[1:], columns=data[0])
                        
                        # Cerca lavoratore
                        mask = (df['Codice'] == codice) & (df['PIN'] == pin)
                        
                        if mask.any():
                            row = df[mask].iloc[0]
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
# PAGINA AREA LAVORATORE (DASHBOARD PERSONALE)
# ============================================================================

def pagina_area_lavoratore():
    """Dashboard personale lavoratore - visualizza e modifica dati"""
    
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'lavoratore':
        st.error(get_testo("accesso_negato", st.session_state.lingua))
        st.stop()
    
    codice_lavoratore = st.session_state.get('codice_operatore')
    pin_lavoratore = st.session_state.get('pin_operatore')
    
    st.title(get_testo("i_miei_dati", st.session_state.lingua))
    st.success(f"Bonjour - Code: {codice_lavoratore}")
    
    try:
        # Carica dati dal foglio
        response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data[1:], columns=data[0])
            
            # Cerca lavoratore
            mask = (df['Codice'] == codice_lavoratore) & (df['PIN'] == pin_lavoratore)
            
            if not mask.any():
                st.error("Travailleur non trouvé")
                st.stop()
            
            row = df[mask].iloc[0]
            idx = row.name
            
            # DATI NON MODIFICABILI (bloccati)
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
            
            # FORM MODIFICHE (dati variabili)
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
                st.subheader("💰 Informations Salariales")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nuovo_salario = st.text_input("Salaire (FCFA)", value=str(row.get('Salario', '')))
                    nuova_data_inizio = st.text_input("Date de début", value=row.get('Data_Inizio', ''))
                
                with col2:
                    # Paga individuale (solo visualizzazione per il lavoratore)
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
                        # Aggiorna dataframe
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
                        
                        # Invia a Google
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
    """Form per trasmissione dati giornalieri (più semplice del form completo)"""
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
        st.subheader(" Informations Professionnelles")
        
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
            
            # Genera codice e PIN
            codice = genera_codice_operatore(cognome, nome, data_nascita)
            pin = genera_pin()
            
            # Prepara dati
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
                'tipo': 'Giornaliero'  # Campo per distinguere
            }
            
            # Salva su Google
            if salva_su_google_sheets(GOOGLE_SCRIPT_URL_ASSUNZIONI, dati, action="append"):
                st.success("✅ Données transmises avec succès!")
                st.info(f"**Conservez ces identifiants:**\n\nCode d'accès: **{codice}**\nPIN: **{pin}**")
                st.ballo()
            else:
                st.error("Erreur lors de la transmission")

# ============================================================================
# PAGINA CANDIDATURE SPONTANEE (CON NUOVI CAMPI)
# ============================================================================

def pagina_candidatura():
    """Candidature spontanee con nuovi campi"""
    st.title(get_testo('candidatura_spontanea', st.session_state.lingua))
    
    st.info("ℹ️ Ceci n'est PAS un contrat, mais seulement l'envoi de votre candidature spontanée.")
    
    with st.form("form_candidatura"):
        st.subheader(" Informations Personnelles")
        
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
        st.subheader(" Formations et Compétences")
        
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
            
            # Prepara dati
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
            
            # Salva su Google
            if salva_su_google_sheets(GOOGLE_SCRIPT_URL_CANDIDATURE, dati, action="append"):
                st.success("✅ Candidature envoyée avec succès! Nous vous contacterons bientôt.")
                st.ballo()
            else:
                st.error("Erreur lors de l'envoi")

# ============================================================================
# PAGINA REGISTRAZIONE MULTI-STEP (ASSUNZIONI COMPLETE)
# ============================================================================

def pagina_registrazione_multi_step(lingua):
    """Form assunzioni completo a step (già esistente, non modificato)"""
    # ... (mantieni il codice esistente che già funziona)
    # Per brevità non lo riscrivo qui, ma mantieni tutto il codice che avevi
    pass

# ============================================================================
# PAGINA DASHBOARD ADMIN
# ============================================================================

def pagina_dashboard():
    """Dashboard amministrativa"""
    st.title(get_testo('dashboard', st.session_state.lingua))
    
    # Login admin
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
        
        # Carica dati
        try:
            response = requests.get(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data[1:], columns=data[0])
                
                st.write(f"Total travailleurs: {len(df)}")
                
                # Seleziona lavoratore per modificare paga
                lavoratore = st.selectbox("Sélectionner un travailleur", df['Cognome'] + ' ' + df['Nome'])
                
                if lavoratore:
                    row = df[df['Cognome'] + ' ' + df['Nome'] == lavoratore].iloc[0]
                    idx = row.name
                    
                    st.text_input("Code", value=row.get('Codice', ''), disabled=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        tipo_paga = st.selectbox("Type de paiement", ["Horaire", "Journalier", "Mensuel"], 
                                                   index=0 if row.get('Tipo_Paga') == 'Horaire' else (1 if row.get('Tipo_Paga') == 'Journalier' else 2))
                    
                    with col2:
                        valore_paga = st.text_input("Montant (FCFA)", value=str(row.get('Valore_Paga', '')))
                    
                    if st.button("💾 Enregistrer le salaire"):
                        df.loc[idx, 'Tipo_Paga'] = tipo_paga
                        df.loc[idx, 'Valore_Paga'] = valore_paga
                        
                        # Salva su Google
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
    st.title(get_testo('titolo', st.session_state.lingua))
    st.markdown(get_testo('sottotitolo', st.session_state.lingua))
    st.markdown("---")
    
    # Selezione lingua
    lingua_sel = st.selectbox(get_testo('lingua', st.session_state.lingua), 
                               ["Français", "Italiano", "English"],
                               index=0 if st.session_state.lingua == 'fr' else (1 if st.session_state.lingua == 'it' else 2))
    st.session_state.lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
    
    st.markdown("---")
    
    # Navigazione semplificata
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
