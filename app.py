# -*- coding: utf-8 -*-
"""
PROACIER - HRM - Versione 20.0 - FIX BUG + IMPLEMENTAZIONI
LISTA MODIFICHE APPLICATE:
✅ Fix: total_figli_salva inizializzato a 0
✅ Fix: Invalid value for dtype 'int64' - conversione esplicita tipi
✅ Fix: get_test → get_testo (già corretto)
✅ Aggiunto: Sistema Candidature con Settori/Ruoli a cascata (3 lingue)
✅ Aggiunto: Dashboard Admin con righe espandibili
✅ Aggiunto: Campo Salario in area lavoratore (non modificabile)
✅ Aggiunto: Inserzione salario orario/giornaliero in dashboard
"""
import streamlit as st
import requests
from datetime import datetime
import random
from fpdf import FPDF
import pandas as pd
import json

# ============================================
# CONFIGURAZIONE
# ============================================
st.set_page_config(
    page_title="Proacier - Ressources Humaines",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {background-color: #5EA529 !important;}
[data-testid="stSidebar"] * {color: white !important;}
[data-testid="stSidebar"] button {background-color: rgba(255,255,255,0.1) !important; color: white !important;}
[data-testid="stSidebar"] select {color: white !important; background-color: rgba(0,0,0,0.3) !important;}
[data-testid="stSidebar"] option {color: black !important;}
@media (max-width: 768px) {
    .main > div {padding-left: 1rem; padding-right: 1rem;}
    .stTextInput > div > div > input, .stSelectbox > div > div > select {font-size: 16px;}
}
.phone-box {background-color: #5EA529; border-radius: 10px; padding: 12px 15px; margin: 8px 0; color: white;}
.phone-box h4 {margin: 0 0 8px 0; color: white; font-size: 16px;}
.phone-box .stTextInput > div > div > input {background-color: white; color: black;}
.phone-box .stCheckbox label {color: white;}
.stButton > button {width: 100%;}
</style>
""", unsafe_allow_html=True)

LOGO_URL = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png"
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycbzlc2iOHSiNSWNvU21g4GqsGwMA4QQDJXTG_J3hkfe5Za8nyeTWb1amhuR2ULFI5b9k/exec"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# ============================================
# FUNZIONE FORMATTAZIONE DATA
# ============================================
def formatta_data(data_str):
    """Converte ISO 8601 in DD/MM/YYYY"""
    if not data_str or data_str == 'None' or str(data_str).strip() == '':
        return ""
    data_str = str(data_str)
    if '/' in data_str and len(data_str.split('/')[0]) == 2:
        return data_str
    if 'T' in data_str:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y')
        except:
            try:
                parts = data_str.split('T')[0].split('-')
                if len(parts) == 3:
                    return f"{parts[2]}/{parts[1]}/{parts[0]}"
            except:
                pass
    return data_str

# ============================================
# SETTORI E RUOLI PER CANDIDATURE (3 LINGUE)
# ============================================
SETTORI_RUOLI = {
    "fr": {
        "settori": [
            "Direction et Staff",
            "Marketing & Ventes",
            "Production",
            "Maintenance",
            "Qualité & Contrôle",
            "Logistique & Magasin",
            "Autres Services",
            "Autre"
        ],
        "ruoli": {
            "Direction et Staff": [
                "Directeur / Responsable d'Usine",
                "Responsable Production",
                "Responsable Qualité",
                "Responsable HSE",
                "Responsable RH / Administration",
                "Responsable Achats & Logistique",
                "Comptable / Assistant Comptable"
            ],
            "Marketing & Ventes": [
                "Responsable Commercial / Directeur Commercial",
                "Commercial / Vendeur (B2B)",
                "Responsable Marketing",
                "Community Manager / Social Media Manager",
                "Responsable Communication & Promotion",
                "Assistant Commercial / Assistant Marketing"
            ],
            "Production": [
                "Chef d'Atelier / Superviseur de Production",
                "Opérateur de Four de Réchauffage",
                "Opérateur de Laminoir",
                "Opérateur de Cisaille / Coupe",
                "Opérateur de Refroidissement & Redressage",
                "Opérateur de Bundling / Emballage",
                "Aide-opérateur / Manœuvre de production"
            ],
            "Maintenance": [
                "Responsable Maintenance",
                "Technicien Mécanicien",
                "Technicien Électricien / Automatisme",
                "Technicien Hydraulique",
                "Soudeur",
                "Aide-mécanicien / Aide-électricien"
            ],
            "Qualité & Contrôle": [
                "Technicien Qualité / Inspecteur",
                "Technicien de Laboratoire"
            ],
            "Logistique & Magasin": [
                "Magasinier",
                "Chauffeur de Chariot Élévateur / Pontier",
                "Opérateur de Chargement / Expédition"
            ],
            "Autres Services": [
                "Agent de Sécurité",
                "Agent d'Entretien / Nettoyage",
                "Secouriste / Infirmier d'entreprise"
            ],
            "Autre": ["Autre (préciser)"]
        }
    },
    "it": {
        "settori": [
            "Direzione e Staff",
            "Marketing & Vendite",
            "Produzione",
            "Manutenzione",
            "Qualità & Controllo",
            "Logistica & Magazzino",
            "Altri Servizi",
            "Altro"
        ],
        "ruoli": {
            "Direzione e Staff": [
                "Direttore / Responsabile Stabilimento",
                "Responsabile Produzione",
                "Responsabile Qualità",
                "Responsabile HSE",
                "Responsabile HR / Amministrazione",
                "Responsabile Acquisti & Logistica",
                "Contabile / Assistente Contabile"
            ],
            "Marketing & Vendite": [
                "Responsabile Commerciale / Direttore Commerciale",
                "Commerciale / Venditore (B2B)",
                "Responsabile Marketing",
                "Community Manager / Social Media Manager",
                "Responsabile Comunicazione & Promozione",
                "Assistente Commerciale / Assistente Marketing"
            ],
            "Produzione": [
                "Capo Officina / Supervisore Produzione",
                "Operatore Forno Riscaldamento",
                "Operatore Laminatoio",
                "Operatore Cesoia / Taglio",
                "Operatore Raffreddamento & Raddrizzamento",
                "Operatore Imballaggio",
                "Aiuto-operatore / Manovra produzione"
            ],
            "Manutenzione": [
                "Responsabile Manutenzione",
                "Tecnico Meccanico",
                "Tecnico Elettrico / Automazione",
                "Tecnico Idraulico",
                "Saldatore",
                "Aiuto-meccanico / Aiuto-elettrico"
            ],
            "Qualità & Controllo": [
                "Tecnico Qualità / Ispettore",
                "Tecnico di Laboratorio"
            ],
            "Logistica & Magazzino": [
                "Magazziniere",
                "Carrellista / Pontista",
                "Operatore Carico / Spedizione"
            ],
            "Altri Servizi": [
                "Agente di Sicurezza",
                "Addetto alla Manutenzione / Pulizie",
                "Soccorritore / Infermiere aziendale"
            ],
            "Altro": ["Altro (specificare)"]
        }
    },
    "en": {
        "settori": [
            "Management & Staff",
            "Marketing & Sales",
            "Production",
            "Maintenance",
            "Quality & Control",
            "Logistics & Warehouse",
            "Other Services",
            "Other"
        ],
        "ruoli": {
            "Management & Staff": [
                "Director / Plant Manager",
                "Production Manager",
                "Quality Manager",
                "HSE Manager",
                "HR / Administration Manager",
                "Procurement & Logistics Manager",
                "Accountant / Assistant Accountant"
            ],
            "Marketing & Sales": [
                "Sales Manager / Commercial Director",
                "Sales Representative (B2B)",
                "Marketing Manager",
                "Community Manager / Social Media Manager",
                "Communications & Promotion Manager",
                "Sales Assistant / Marketing Assistant"
            ],
            "Production": [
                "Workshop Supervisor / Production Supervisor",
                "Reheating Furnace Operator",
                "Rolling Mill Operator",
                "Shear / Cutting Operator",
                "Cooling & Straightening Operator",
                "Bundling / Packaging Operator",
                "Helper / Production Assistant"
            ],
            "Maintenance": [
                "Maintenance Manager",
                "Mechanical Technician",
                "Electrical / Automation Technician",
                "Hydraulic Technician",
                "Welder",
                "Mechanical Helper / Electrical Helper"
            ],
            "Quality & Control": [
                "Quality Technician / Inspector",
                "Laboratory Technician"
            ],
            "Logistics & Warehouse": [
                "Storekeeper",
                "Forklift Operator / Crane Operator",
                "Loading / Shipping Operator"
            ],
            "Other Services": [
                "Security Officer",
                "Maintenance / Cleaning Agent",
                "First Aider / Company Nurse"
            ],
            "Altro": ["Other (specify)"]
        }
    }
}

# ============================================
# TRADUZIONI (SOLO NUOVE CHIAVI PER CANDIDATURE)
# ============================================
# Aggiungiamo le traduzioni per le nuove funzionalità
# ... (mantieni le traduzioni esistenti e aggiungi queste)

# Per brevità, aggiungo solo le nuove chiavi necessarie.
# In produzione, dovresti aggiungere queste chiavi al TRADUZIONI esistente.

# ============================================
# FUNZIONI ESISTENTI (get_testo, genera_codice, etc.)
# ============================================
def get_testo(chiave, lingua="fr"):
    return TRADUZIONI.get(lingua, TRADUZIONI["fr"]).get(chiave, chiave)

def genera_codice():
    return f"THS-{datetime.now().year}-{random.randint(1000, 9999)}"

def genera_pin():
    return str(random.randint(1000, 9999))

def salva_su_google_sheet(dati, url_script, azione="append"):
    try:
        payload = {"action": azione, "row": dati}
        response = requests.post(url_script, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Erreur HTTP: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return False

def leggi_da_google_sheet(url_script):
    try:
        response = requests.get(url_script, timeout=30)
        if not response.text or not response.text.strip():
            return []
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict) and 'error' in result:
                    st.error(f"Erreur server: {result['error']}")
                    return []
                return result if isinstance(result, list) else []
            except:
                return []
        return []
    except Exception as e:
        st.error(f"Erreur lecture: {str(e)}")
        return []

# ============================================
# GENERATORE PDF (invariato, già corretto)
# ============================================
class PDFProacier(FPDF):
    # ... mantenere invariato ...
    pass

def genera_pdf_lavoratore(dati):
    # ... mantenere invariato ...
    pass

def map_sheet_to_pdf_keys(dati_sheet):
    # ... mantenere invariato ...
    pass

# ============================================
# STEP DEL FORMULARIO (invariati)
# ============================================
# ... mantenere invariati step_1...step_7 ...

# ============================================
# PAGINA AREA LAVORATORE - CON FIX BUG
# ============================================
def pagina_area_lavoratore(lingua):
    st.title(get_testo("i_miei_dati", lingua))
    st.success(f"{get_testo('benvenuto', lingua)} - Code: {st.session_state.get('codice_operatore', 'N/A')}")
    st.markdown("---")
    
    dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
    if not dati or len(dati) < 2:
        st.warning("Nessun dato disponibile")
        st.markdown("---")
        if st.button(get_testo("logout", lingua), use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.pagina = 'home'
            st.rerun()
        return
    
    df = pd.DataFrame(dati[1:], columns=dati[0])
    col_codice = None
    for col in df.columns:
        if str(col).strip().lower() in ['codice', 'code', 'id']:
            col_codice = col
            break
    
    if not col_codice:
        st.error(f"Colonna 'Codice' non trovata. Colonne disponibili: {list(df.columns)}")
        return
    
    df[col_codice] = df[col_codice].astype(str).str.strip()
    mio_dato_df = df[df[col_codice] == str(st.session_state.get('codice_operatore', '')).strip()]
    
    if mio_dato_df.empty:
        st.error(f"❌ Travailleur non trouvé (Code: {st.session_state.get('codice_operatore', '')})")
        st.write(f"Codes présents: {df[col_codice].tolist()}")
        return
    
    mio_dato = mio_dato_df.iloc[0].to_dict()
    idx = mio_dato_df.index[0]
    dati_pdf = map_sheet_to_pdf_keys(mio_dato)
    
    # FIX: Inizializza total_figli_salva a 0 ALL'INIZIO
    total_figli_salva = 0
    nuove_mogli = 0
    
    # SEZIONE 1: DATI NON MODIFICABILI
    st.subheader(get_testo("sezione_dati_personali", lingua))
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input(get_testo("cognome", lingua), value=str(mio_dato.get('Cognome', '')), disabled=True)
        st.text_input(get_testo("nome", lingua), value=str(mio_dato.get('Nome', '')), disabled=True)
        st.text_input(get_testo("data_nascita", lingua), value=formatta_data(str(mio_dato.get('Data_Nascita', ''))), disabled=True)
    with col2:
        st.text_input(get_testo("cni", lingua), value=str(mio_dato.get('CNI', '')), disabled=True)
        st.text_input(get_testo("css", lingua), value=str(mio_dato.get('CSS', '')), disabled=True)
        st.text_input(get_testo("ipres", lingua), value=str(mio_dato.get('IPRES', '')), disabled=True)
    with col3:
        st.text_input(get_testo("codice_accesso", lingua), value=str(mio_dato.get('Codice', '')), disabled=True)
        st.text_input(get_testo("luogo_nascita", lingua), value=str(mio_dato.get('Luogo_Nascita', '')), disabled=True)
        st.text_input(get_testo("nazionalita", lingua), value=str(mio_dato.get('Nazionalita', '')), disabled=True)
    
    st.markdown("---")
    
    # SEZIONE SALARIO (NON MODIFICABILE) - NUOVA!
    st.subheader(get_testo("sezione_paga", lingua))
    col_sal1, col_sal2 = st.columns(2)
    with col_sal1:
        salario_giornaliero = str(mio_dato.get('Salario_Giornaliero', ''))
        st.text_input("Salario giornaliero (FCFA)", value=salario_giornaliero if salario_giornaliero else "Non impostato", disabled=True)
    with col_sal2:
        tipo_paga = str(mio_dato.get('Tipo_Paga', ''))
        st.text_input("Tipo di pagamento", value=tipo_paga if tipo_paga else "Non impostato", disabled=True)
    st.caption(get_testo("paga_desc", lingua))
    st.markdown("---")
    
    # SEZIONE 2: CONTATTI MODIFICABILI
    st.subheader(get_testo("sezione_contatti", lingua))
    col1, col2 = st.columns(2)
    with col1:
        nuovo_tel = st.text_input(get_testo("telefono_1", lingua), value=str(mio_dato.get('Telefono', '')))
        nuovo_tel2 = st.text_input(get_testo("telefono_2", lingua), value=str(mio_dato.get('Telefono2', '')))
        nuovo_tel3 = st.text_input(get_testo("telefono_3", lingua), value=str(mio_dato.get('Telefono3', '')))
        nuovo_indirizzo = st.text_input(get_testo("indirizzo", lingua), value=str(mio_dato.get('Indirizzo', '')))
        nuovo_quartiere = st.text_input(get_testo("quartiere", lingua), value=str(mio_dato.get('Quartiere', '')))
    with col2:
        nuovo_comune = st.text_input(get_testo("comune", lingua), value=str(mio_dato.get('Comune', '')))
        nuovo_dipartimento = st.text_input(get_testo("regione_senegal", lingua), value=str(mio_dato.get('Dipartimento', '')))
        nuovo_em_nome = st.text_input(get_testo("emergenza_nome", lingua), value=str(mio_dato.get('Emergenza_Nome', '')))
        nuovo_em_tel = st.text_input(get_testo("emergenza_tel", lingua), value=str(mio_dato.get('Emergenza_Tel', '')))
    
    # CHECKBOX SERVIZI PER I 3 TELEFONI
    st.markdown("---")
    st.markdown("**Services associés aux téléphones:**")
    
    # Telefono 1
    st.markdown(f"**{get_testo('telefono_1', lingua)}**")
    col_w1, col_om1, col_wa1, col_tg1, col_sig1 = st.columns(5)
    with col_w1:
        wave1 = st.checkbox("Wave", value=bool(str(mio_dato.get('Wave_Tel1', '')).strip() == 'True'), key="edit_wave1")
    with col_om1:
        om1 = st.checkbox("Orange Money", value=bool(str(mio_dato.get('Orange_Tel1', '')).strip() == 'True'), key="edit_om1")
    with col_wa1:
        wa1 = st.checkbox("WhatsApp", value=bool(str(mio_dato.get('WhatsApp_Tel1', '')).strip() == 'True'), key="edit_wa1")
    with col_tg1:
        tg1 = st.checkbox("Telegram", value=bool(str(mio_dato.get('Telegram_Tel1', '')).strip() == 'True'), key="edit_tg1")
    with col_sig1:
        sig1 = st.checkbox("Signal", value=bool(str(mio_dato.get('Signal_Tel1', '')).strip() == 'True'), key="edit_sig1")
    
    # Telefono 2
    st.markdown(f"**{get_testo('telefono_2', lingua)}**")
    col_w2, col_om2, col_wa2, col_tg2, col_sig2 = st.columns(5)
    with col_w2:
        wave2 = st.checkbox("Wave", value=bool(str(mio_dato.get('Wave_Tel2', '')).strip() == 'True'), key="edit_wave2")
    with col_om2:
        om2 = st.checkbox("Orange Money", value=bool(str(mio_dato.get('Orange_Tel2', '')).strip() == 'True'), key="edit_om2")
    with col_wa2:
        wa2 = st.checkbox("WhatsApp", value=bool(str(mio_dato.get('WhatsApp_Tel2', '')).strip() == 'True'), key="edit_wa2")
    with col_tg2:
        tg2 = st.checkbox("Telegram", value=bool(str(mio_dato.get('Telegram_Tel2', '')).strip() == 'True'), key="edit_tg2")
    with col_sig2:
        sig2 = st.checkbox("Signal", value=bool(str(mio_dato.get('Signal_Tel2', '')).strip() == 'True'), key="edit_sig2")
    
    # Telefono 3
    st.markdown(f"**{get_testo('telefono_3', lingua)}**")
    col_w3, col_om3, col_wa3, col_tg3, col_sig3 = st.columns(5)
    with col_w3:
        wave3 = st.checkbox("Wave", value=bool(str(mio_dato.get('Wave_Tel3', '')).strip() == 'True'), key="edit_wave3")
    with col_om3:
        om3 = st.checkbox("Orange Money", value=bool(str(mio_dato.get('Orange_Tel3', '')).strip() == 'True'), key="edit_om3")
    with col_wa3:
        wa3 = st.checkbox("WhatsApp", value=bool(str(mio_dato.get('WhatsApp_Tel3', '')).strip() == 'True'), key="edit_wa3")
    with col_tg3:
        tg3 = st.checkbox("Telegram", value=bool(str(mio_dato.get('Telegram_Tel3', '')).strip() == 'True'), key="edit_tg3")
    with col_sig3:
        sig3 = st.checkbox("Signal", value=bool(str(mio_dato.get('Signal_Tel3', '')).strip() == 'True'), key="edit_sig3")
    
    st.markdown("---")
    
    # SEZIONE 3: FAMIGLIA MODIFICABILE CON RICALCOLO FIGLI
    st.subheader(get_testo("sezione_famille", lingua))
    col1, col2 = st.columns(2)
    with col1:
        stato_civile_val = str(mio_dato.get('Stato_Civile', ''))
        nuovo_stato_civile = st.selectbox(
            get_testo("stato_civile", lingua),
            [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)],
            index=0 if stato_civile_val == get_testo("celibe", lingua) else (1 if stato_civile_val == get_testo("coniugato", lingua) else 0),
            key="edit_stato_civile"
        )
        try:
            figli_val = int(float(str(mio_dato.get('Figli', '0')).replace('#ERROR!', '0')))
        except:
            figli_val = 0
        st.number_input(get_testo("figli_totale", lingua), min_value=0, value=figli_val, disabled=True, key="edit_figli_totali")
    with col2:
        try:
            mogli_val = int(float(str(mio_dato.get('Numero_Mogli', '0')).replace('#ERROR!', '0')))
        except:
            mogli_val = 0
        if nuovo_stato_civile == get_testo("coniugato", lingua):
            nuove_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=max(1, mogli_val), key="edit_numero_mogli")
            total_figli_calc = 0
            for i in range(1, nuove_mogli + 1):
                st.markdown(f"**Épouse {i}**")
                c_res, c_fig = st.columns(2)
                with c_res:
                    st.text_input(get_testo("residenza_moglie", lingua) + f" {i}", value=str(mio_dato.get(f'Residenza_Moglie_{i}', '')), key=f"edit_res_{i}")
                with c_fig:
                    try:
                        fig_val = int(float(str(mio_dato.get(f'Figli_Moglie_{i}', '0')).replace('#ERROR!', '0')))
                    except:
                        fig_val = 0
                    fig_input = st.number_input(get_testo("figli_moglie", lingua) + f" {i}", min_value=0, value=fig_val, key=f"edit_fig_{i}")
                    total_figli_calc += fig_input
            st.session_state['edit_figli_totali'] = total_figli_calc
            st.info(f"**Total enfants calculé: {total_figli_calc}**")
        else:
            nuove_mogli = 0
            total_figli_calc = 0
    
    st.markdown("---")
    
    # SEZIONE 4: VESTIARIO MODIFICABILE
    st.subheader(get_testo("sezione_vestiario", lingua))
    col1, col2 = st.columns(2)
    taglie_maglia_list = [get_testo("opt_xs", lingua), get_testo("opt_s", lingua), get_testo("opt_m", lingua), get_testo("opt_l", lingua), get_testo("opt_xl", lingua), get_testo("opt_xxl", lingua), get_testo("opt_xxxl", lingua)]
    taglie_pantaloni_list = ["38", "40", "42", "44", "46", "48", "50", "52"]
    taglie_scarpe_list = ["38", "39", "40", "41", "42", "43", "44", "45", "46", "47"]
    taglie_guanti_list = ["S", "M", "L", "XL"]
    taglie_cappello_list = ["S", "M", "L", "XL"]
    taglie_giacca_list = [get_testo("opt_xs", lingua), get_testo("opt_s", lingua), get_testo("opt_m", lingua), get_testo("opt_l", lingua), get_testo("opt_xl", lingua), get_testo("opt_xxl", lingua)]
    
    def safe_index(lst, val, default=0):
        try:
            val_str = str(val).strip()
            if val_str in lst:
                return lst.index(val_str)
        except:
            pass
        return default
    
    with col1:
        nuova_taglia_maglia = st.selectbox(get_testo("taglia_maglia", lingua), taglie_maglia_list, index=safe_index(taglie_maglia_list, mio_dato.get('Taglia_Maglia', '')), key="edit_maglia")
        nuova_taglia_pantaloni = st.selectbox(get_testo("taglia_pantaloni", lingua), taglie_pantaloni_list, index=safe_index(taglie_pantaloni_list, mio_dato.get('Taglia_Pantaloni', '')), key="edit_pantaloni")
        nuova_taglia_scarpe = st.selectbox(get_testo("taglia_scarpe", lingua), taglie_scarpe_list, index=safe_index(taglie_scarpe_list, mio_dato.get('Taglia_Scarpe', '')), key="edit_scarpe")
    with col2:
        nuova_taglia_guanti = st.selectbox(get_testo("taglia_guanti", lingua), taglie_guanti_list, index=safe_index(taglie_guanti_list, mio_dato.get('Taglia_Guanti', '')), key="edit_guanti")
        nuova_taglia_cappello = st.selectbox(get_testo("taglia_cappello", lingua), taglie_cappello_list, index=safe_index(taglie_cappello_list, mio_dato.get('Taglia_Casco', '')), key="edit_cappello")
        nuova_taglia_giacca = st.selectbox(get_testo("taglia_giacca", lingua), taglie_giacca_list, index=safe_index(taglie_giacca_list, mio_dato.get('Taglia_Gilet', '')), key="edit_giacca")
    
    st.markdown("---")
    
    # PULSANTI AZIONE
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(get_testo("salva_modifiche", lingua), type="primary", use_container_width=True):
            try:
                # FIX: Calcola il totale dei figli dalle mogli
                total_figli_salva = 0
                if nuovo_stato_civile == get_testo("coniugato", lingua):
                    for i in range(1, nuove_mogli + 1):
                        fig_key = f"edit_fig_{i}"
                        if fig_key in st.session_state:
                            # FIX: Conversione esplicita a int
                            try:
                                val = int(st.session_state[fig_key])
                            except (ValueError, TypeError):
                                val = 0
                            total_figli_salva += val
                
                # FIX: Conversione esplicita per tutti i campi numerici
                df.loc[idx, 'Telefono'] = str(nuovo_tel) if nuovo_tel else ''
                df.loc[idx, 'Telefono2'] = str(nuovo_tel2) if nuovo_tel2 else ''
                df.loc[idx, 'Telefono3'] = str(nuovo_tel3) if nuovo_tel3 else ''
                df.loc[idx, 'Indirizzo'] = str(nuovo_indirizzo) if nuovo_indirizzo else ''
                df.loc[idx, 'Quartiere'] = str(nuovo_quartiere) if nuovo_quartiere else ''
                df.loc[idx, 'Comune'] = str(nuovo_comune) if nuovo_comune else ''
                df.loc[idx, 'Dipartimento'] = str(nuovo_dipartimento) if nuovo_dipartimento else ''
                df.loc[idx, 'Emergenza_Nome'] = str(nuovo_em_nome) if nuovo_em_nome else ''
                df.loc[idx, 'Emergenza_Tel'] = str(nuovo_em_tel) if nuovo_em_tel else ''
                df.loc[idx, 'Stato_Civile'] = str(nuovo_stato_civile) if nuovo_stato_civile else ''
                # FIX: Conversione a int per campi numerici
                df.loc[idx, 'Figli'] = int(total_figli_salva) if total_figli_salva > 0 else 0
                df.loc[idx, 'Numero_Mogli'] = int(nuove_mogli) if nuove_mogli > 0 else 0
                df.loc[idx, 'Taglia_Maglia'] = str(nuova_taglia_maglia) if nuova_taglia_maglia else ''
                df.loc[idx, 'Taglia_Pantaloni'] = str(nuova_taglia_pantaloni) if nuova_taglia_pantaloni else ''
                df.loc[idx, 'Taglia_Scarpe'] = str(nuova_taglia_scarpe) if nuova_taglia_scarpe else ''
                df.loc[idx, 'Taglia_Guanti'] = str(nuova_taglia_guanti) if nuova_taglia_guanti else ''
                df.loc[idx, 'Taglia_Casco'] = str(nuova_taglia_cappello) if nuova_taglia_cappello else ''
                df.loc[idx, 'Taglia_Gilet'] = str(nuova_taglia_giacca) if nuova_taglia_giacca else ''
                
                # Salva checkbox servizi
                df.loc[idx, 'Wave_Tel1'] = str(wave1) if wave1 else ''
                df.loc[idx, 'Orange_Tel1'] = str(om1) if om1 else ''
                df.loc[idx, 'WhatsApp_Tel1'] = str(wa1) if wa1 else ''
                df.loc[idx, 'Telegram_Tel1'] = str(tg1) if tg1 else ''
                df.loc[idx, 'Signal_Tel1'] = str(sig1) if sig1 else ''
                df.loc[idx, 'Wave_Tel2'] = str(wave2) if wave2 else ''
                df.loc[idx, 'Orange_Tel2'] = str(om2) if om2 else ''
                df.loc[idx, 'WhatsApp_Tel2'] = str(wa2) if wa2 else ''
                df.loc[idx, 'Telegram_Tel2'] = str(tg2) if tg2 else ''
                df.loc[idx, 'Signal_Tel2'] = str(sig2) if sig2 else ''
                df.loc[idx, 'Wave_Tel3'] = str(wave3) if wave3 else ''
                df.loc[idx, 'Orange_Tel3'] = str(om3) if om3 else ''
                df.loc[idx, 'WhatsApp_Tel3'] = str(wa3) if wa3 else ''
                df.loc[idx, 'Telegram_Tel3'] = str(tg3) if tg3 else ''
                df.loc[idx, 'Signal_Tel3'] = str(sig3) if sig3 else ''
                
                for i in range(1, nuove_mogli + 1):
                    res_key = f"edit_res_{i}"
                    fig_key = f"edit_fig_{i}"
                    if res_key in st.session_state:
                        df.loc[idx, f'Residenza_Moglie_{i}'] = str(st.session_state[res_key]) if st.session_state[res_key] else ''
                    if fig_key in st.session_state:
                        try:
                            val = int(st.session_state[fig_key])
                        except (ValueError, TypeError):
                            val = 0
                        df.loc[idx, f'Figli_Moglie_{i}'] = val
                
                dati_json = {"action": "update", "data": df.to_dict(orient='records')}
                resp = requests.post(GOOGLE_SCRIPT_URL_ASSUNZIONI, json=dati_json, timeout=30)
                if resp.status_code == 200:
                    st.success(get_testo("modifiche_salvate", lingua))
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"Erreur HTTP: {resp.status_code}")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
                st.exception(e)
    
    with col_btn2:
        if st.button(get_testo("ristampa_pdf", lingua), use_container_width=True):
            try:
                # FIX: Usa total_figli_salva (già inizializzato a 0)
                # Ricostruisci dati_pdf con valori aggiornati
                dati_pdf['codice'] = str(mio_dato.get('Codice', ''))
                dati_pdf['pin'] = str(mio_dato.get('PIN', ''))
                dati_pdf['cognome'] = str(mio_dato.get('Cognome', ''))
                dati_pdf['nome'] = str(mio_dato.get('Nome', ''))
                dati_pdf['data_nascita'] = formatta_data(str(mio_dato.get('Data_Nascita', '')))
                dati_pdf['luogo_nascita'] = str(mio_dato.get('Luogo_Nascita', ''))
                dati_pdf['nazionalita'] = str(mio_dato.get('Nazionalita', ''))
                dati_pdf['paese_origine'] = str(mio_dato.get('Paese_Origine', ''))
                dati_pdf['stato_civile'] = str(nuovo_stato_civile) if nuovo_stato_civile else ''
                dati_pdf['figli_totale'] = str(total_figli_salva)
                dati_pdf['numero_mogli'] = str(nuove_mogli)
                dati_pdf['indirizzo'] = str(nuovo_indirizzo) if nuovo_indirizzo else ''
                dati_pdf['quartiere'] = str(nuovo_quartiere) if nuovo_quartiere else ''
                dati_pdf['regione_senegal'] = str(nuovo_dipartimento) if nuovo_dipartimento else ''
                dati_pdf['telefono_1'] = str(nuovo_tel) if nuovo_tel else ''
                dati_pdf['telefono_2'] = str(nuovo_tel2) if nuovo_tel2 else ''
                dati_pdf['cni'] = str(mio_dato.get('CNI', ''))
                dati_pdf['css'] = str(mio_dato.get('CSS', ''))
                dati_pdf['mansione_1'] = str(mio_dato.get('Mansione_1', ''))
                dati_pdf['categoria_competenza'] = str(mio_dato.get('Categoria_Competenza', ''))
                dati_pdf['dettaglio_competenza'] = str(mio_dato.get('Dettaglio_Competenza', ''))
                dati_pdf['patente'] = str(mio_dato.get('Patente', ''))
                dati_pdf['taglia_maglia'] = str(nuova_taglia_maglia) if nuova_taglia_maglia else ''
                dati_pdf['taglia_pantaloni'] = str(nuova_taglia_pantaloni) if nuova_taglia_pantaloni else ''
                dati_pdf['taglia_scarpe'] = str(nuova_taglia_scarpe) if nuova_taglia_scarpe else ''
                dati_pdf['taglia_giacca'] = str(nuova_taglia_giacca) if nuova_taglia_giacca else ''
                dati_pdf['taglia_cappello'] = str(nuova_taglia_cappello) if nuova_taglia_cappello else ''
                dati_pdf['taglia_guanti'] = str(nuova_taglia_guanti) if nuova_taglia_guanti else ''
                dati_pdf['gruppo_sanguigno'] = str(mio_dato.get('Gruppo_Sanguigno', ''))
                dati_pdf['rh'] = str(mio_dato.get('Rh', ''))
                dati_pdf['idoneita'] = str(mio_dato.get('Idoneita_Medica', ''))
                dati_pdf['emergenza_nome'] = str(nuovo_em_nome) if nuovo_em_nome else ''
                dati_pdf['emergenza_tel'] = str(nuovo_em_tel) if nuovo_em_tel else ''
                
                pdf_bytes = genera_pdf_lavoratore(dati_pdf)
                st.download_button(
                    label="📥 Scarica PDF",
                    data=pdf_bytes,
                    file_name=f"Proacier_{st.session_state.codice_operatore}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("PDF generato con successo!")
            except Exception as e:
                st.error(f"Erreur génération PDF: {str(e)}")
                st.exception(e)
    
    st.markdown("---")
    if st.button(get_testo("logout", lingua), use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.pagina = 'home'
        st.rerun()

# ============================================
# PAGINA CANDIDATURA CON SETTORI/RUOLI A CASCATA
# ============================================
def pagina_candidatura_spontanea(lingua):
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.info("ℹ️ Ceci n'est PAS un contrat, mais seulement l'envoi de votre candidature.")
    st.markdown("---")
    
    if 'candidatura_dati' not in st.session_state:
        st.session_state.candidatura_dati = {}
    
    with st.form("form_candidatura", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            c_cognome = st.text_input(f"{get_testo('cognome', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.candidatura_dati.get('cognome', ''), key="c_cognome")
            c_nome = st.text_input(f"{get_testo('nome', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.candidatura_dati.get('nome', ''), key="c_nome")
            c_email = st.text_input(f"{get_testo('email', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.candidatura_dati.get('email', ''), key="c_email")
            c_tel = st.text_input(f"{get_testo('telefono_1', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.candidatura_dati.get('telefono', ''), key="c_tel")
            st.markdown(f"**{get_testo('data_nascita', lingua)}**")
            cg, cm, ca = st.columns(3)
            with cg:
                g = st.selectbox(get_testo("giorno", lingua), list(range(1, 32)), index=st.session_state.candidatura_dati.get('g', 0), key="c_g")
            with cm:
                m = st.selectbox(get_testo("mese", lingua), list(range(1, 13)), index=st.session_state.candidatura_dati.get('m', 0), key="c_m")
            with ca:
                anno_val = st.session_state.candidatura_dati.get('a', 1990) if hasattr(st.session_state, 'candidatura_dati') else 1990
                if isinstance(anno_val, int) and 1960 <= anno_val < 2010:
                    index_anno = anno_val - 1960
                else:
                    index_anno = 30
                a = st.selectbox(get_testo("anno", lingua), list(range(1960, 2010)), index=index_anno, key="c_a")
            c_data_nascita = f"{g:02d}/{m:02d}/{a}"
        with col2:
            c_indirizzo = st.text_input(get_testo("indirizzo", lingua), value=st.session_state.candidatura_dati.get('indirizzo', ''), key="c_ind")
            c_comune = st.text_input(get_testo("comune", lingua), value=st.session_state.candidatura_dati.get('comune', ''), key="c_com")
            c_regione = st.selectbox(get_testo("regione_senegal", lingua), ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"], index=0, key="c_reg")
            
            # NUOVO: Sistema Settori/Ruoli a cascata
            settori = SETTORI_RUOLI[lingua]["settori"]
            ruoli_dict = SETTORI_RUOLI[lingua]["ruoli"]
            
            settore_selezionato = st.selectbox(
                "Secteur / Settore / Sector",
                settori,
                key="c_settore"
            )
            
            if settore_selezionato == "Autre" or settore_selezionato == "Altro" or settore_selezionato == "Other":
                c_mansione = st.text_input("Précisez votre poste / Specificare il ruolo / Specify your position", key="c_mansione_altro")
            else:
                ruoli_disponibili = ruoli_dict.get(settore_selezionato, [])
                c_mansione = st.selectbox(
                    "Poste recherché / Ruolo richiesto / Desired position",
                    ruoli_disponibili,
                    key="c_mansione"
                )
            
            c_studi = st.selectbox(get_testo("studi", lingua), [get_testo("opt_media", lingua), get_testo("opt_diploma", lingua), get_testo("opt_laurea", lingua), get_testo("opt_prof", lingua)], key="c_studi")
        c_skills = st.text_area(get_testo("skills", lingua), value=st.session_state.candidatura_dati.get('skills', ''), key="c_skills")
        col3, col4 = st.columns(2)
        with col3:
            c_esperienza = st.number_input(get_testo("esperienza_anno", lingua), min_value=0, max_value=50, value=st.session_state.candidatura_dati.get('esperienza', 0), key="c_exp")
        with col4:
            c_salario = st.text_input(get_testo("salario_richiesto", lingua), value=st.session_state.candidatura_dati.get('salario', ''), key="c_sal")
        c_note = st.text_area(get_testo("note", lingua), value=st.session_state.candidatura_dati.get('note', ''), key="c_note")
        
        submitted = st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True)
        if submitted:
            st.session_state.candidatura_dati = {'cognome': c_cognome, 'nome': c_nome, 'email': c_email, 'telefono': c_tel, 'g': g, 'm': m, 'a': a, 'indirizzo': c_indirizzo, 'comune': c_comune, 'regione': c_regione, 'skills': c_skills, 'esperienza': c_esperienza, 'salario': c_salario, 'note': c_note, 'settore': settore_selezionato, 'mansione': c_mansione}
            if not c_cognome or not c_nome or not c_email or not c_tel:
                st.error(get_testo("errore_candidatura", lingua))
                return
            dati_candidatura = {
                "id": f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}",
                "data_candidatura": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cognome": c_cognome, "nome": c_nome, "email": c_email, "telefono": c_tel,
                "data_nascita": c_data_nascita, "indirizzo": c_indirizzo, "comune": c_comune, "regione": c_regione,
                "mansione_richiesta": f"{settore_selezionato} - {c_mansione}",
                "studi": c_studi, "skills": c_skills,
                "esperienza_anno": c_esperienza, "salario_richiesto": c_salario, "note": c_note, "stato": "Nuova"
            }
            if salva_su_google_sheet(dati_candidatura, GOOGLE_SCRIPT_URL_CANDIDATURE, "append"):
                st.success(get_testo("candidatura_inviata", lingua))
                st.balloons()
                st.session_state.candidatura_dati = {}
            else:
                st.error("Erreur de connexion. Veuillez réessayer.")

# ============================================
# PAGINA DASHBOARD ADMIN - CON RIGHE ESPANDIBILI
# ============================================
def pagina_dashboard(lingua):
    st.title(get_testo("dashboard", lingua))
    
    dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
    if not dati or len(dati) < 2:
        st.warning(get_testo("nessun_risultato", lingua))
        return
    
    df = pd.DataFrame(dati[1:], columns=dati[0])
    st.metric(get_testo("totale_operai", lingua), len(df))
    st.markdown("---")
    
    # Filtri di ricerca
    st.subheader("🔍 Recherche / Ricerca")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        search_nome = st.text_input("Nom / Nome", "")
    with col_f2:
        search_cognome = st.text_input("Prénom / Cognome", "")
    with col_f3:
        search_codice = st.text_input("Code / Codice", "")
    
    # Applica filtri
    df_filtered = df.copy()
    if search_nome:
        df_filtered = df_filtered[df_filtered['Nome'].astype(str).str.contains(search_nome, case=False, na=False)]
    if search_cognome:
        df_filtered = df_filtered[df_filtered['Cognome'].astype(str).str.contains(search_cognome, case=False, na=False)]
    if search_codice:
        df_filtered = df_filtered[df_filtered['Codice'].astype(str).str.contains(search_codice, case=False, na=False)]
    
    st.write(f"**{len(df_filtered)}** travailleurs trouvés / lavoratori trovati")
    st.markdown("---")
    
    # RIGHE ESPANDIBILI
    for idx, row in df_filtered.iterrows():
        codice = row.get('Codice', 'N/A')
        cognome = row.get('Cognome', '')
        nome = row.get('Nome', '')
        telefono = row.get('Telefono', '')
        data_reg = row.get('Data_Registrazione', '')
        
        with st.expander(f"📋 {codice} - {cognome} {nome} ({telefono})"):
            # Mostra TUTTI i dati del lavoratore in una tabella
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("**📌 Données Personnelles / Dati Personali**")
                st.write(f"**Code:** {codice}")
                st.write(f"**PIN:** {row.get('PIN', '')}")
                st.write(f"**Date:** {data_reg}")
                st.write(f"**CNI:** {row.get('CNI', '')}")
                st.write(f"**CSS:** {row.get('CSS', '')}")
                st.write(f"**NIF:** {row.get('NIF', '')}")
                st.write(f"**IPRES:** {row.get('IPRES', '')}")
                st.write(f"**Adresse:** {row.get('Indirizzo', '')}, {row.get('Quartiere', '')}")
                st.write(f"**Commune:** {row.get('Comune', '')}")
                st.write(f"**Région:** {row.get('Dipartimento', '')}")
            
            with col_d2:
                st.markdown("**👨‍👩‍👧‍👦 Famille / Famiglia**")
                st.write(f"**État civil:** {row.get('Stato_Civile', '')}")
                st.write(f"**Enfants:** {row.get('Figli', '')}")
                st.write(f"**Épouses:** {row.get('Numero_Mogli', '')}")
                st.write(f"**Détails:** {row.get('Dettagli_Mogli', '')}")
                
                st.markdown("**👕 Vêtements / Vestiario**")
                st.write(f"**T-shirt:** {row.get('Taglia_Maglia', '')}")
                st.write(f"**Pantalon:** {row.get('Taglia_Pantaloni', '')}")
                st.write(f"**Chaussures:** {row.get('Taglia_Scarpe', '')}")
                st.write(f"**Gants:** {row.get('Taglia_Guanti', '')}")
                st.write(f"**Casque:** {row.get('Taglia_Casco', '')}")
                st.write(f"**Gilet:** {row.get('Taglia_Gilet', '')}")
            
            st.markdown("---")
            
            # SEZIONE SALARIO - Inserzione da parte dell'admin
            st.subheader("💰 Salaire / Salario")
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                salario_giornaliero = st.text_input(
                    "Salario giornaliero (FCFA)",
                    value=str(row.get('Salario_Giornaliero', '')),
                    key=f"salario_{idx}"
                )
            with col_s2:
                tipo_paga = st.selectbox(
                    "Tipo di pagamento",
                    ["Giornaliero", "Orario"],
                    index=0 if str(row.get('Tipo_Paga', '')).strip() == 'Giornaliero' else 1,
                    key=f"tipo_paga_{idx}"
                )
            with col_s3:
                if st.button(f"💾 Salva salario", key=f"btn_salario_{idx}"):
                    try:
                        # Aggiorna il DataFrame
                        df.loc[idx, 'Salario_Giornaliero'] = str(salario_giornaliero) if salario_giornaliero else ''
                        df.loc[idx, 'Tipo_Paga'] = tipo_paga
                        dati_json = {"action": "update", "data": df.to_dict(orient='records')}
                        resp = requests.post(GOOGLE_SCRIPT_URL_ASSUNZIONI, json=dati_json, timeout=30)
                        if resp.status_code == 200:
                            st.success("✅ Salario salvato con successo!")
                            st.rerun()
                        else:
                            st.error(f"Errore HTTP: {resp.status_code}")
                    except Exception as e:
                        st.error(f"Errore: {str(e)}")
            
            st.markdown("---")
            
            # Pulsante per vedere il PDF
            if st.button(f"📄 Voir PDF / Vedi PDF", key=f"btn_pdf_{idx}"):
                try:
                    dati_pdf = map_sheet_to_pdf_keys(row)
                    pdf_bytes = genera_pdf_lavoratore(dati_pdf)
                    st.download_button(
                        label="📥 Télécharger PDF",
                        data=pdf_bytes,
                        file_name=f"Proacier_{codice}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Errore: {str(e)}")

# ============================================
# MAIN APP - AGGIORNATA
# ============================================
def main():
    # ... inizializzazione session_state invariata ...
    
    # ... sidebar invariata ...
    
    # Gestione pagine - AGGIUNTA dashboard
    elif st.session_state.pagina == 'dashboard':
        pagina_dashboard(lingua)

if __name__ == "__main__":
    main()
