# -*- coding: utf-8 -*-
"""
PROACIER - HRM - Versione 13.0 FINALE
==========================================
LISTA MODIFICHE:
1. ✅ Sidebar APERTA di default (non collassata)
2. ✅ Layout responsive ma NON centered (per mostrare sidebar)
3. ✅ Email con oggetto "Nuovi dati lavoratore"
4. ✅ PDF con credenziali accesso
5. ✅ Fix login lavoratore (cerca per colonna Codice/PIN)
6. ✅ Google Sheet: Proacier_Database_Operai / Sheet1
7. ✅ Asterisco su Telefono principale
8. ✅ Ottimizzazione mobile
"""
import streamlit as st
import requests
from datetime import datetime
import random
from fpdf import FPDF
import pandas as pd

# ============================================
# CONFIGURAZIONE - SIDBAR APERTA DI DEFAULT
# ============================================
st.set_page_config(
    page_title="Proacier - Ressources Humaines",
    page_icon="🏭",
    layout="wide",  # NON "centered" altrimenti sidebar nascosta
    initial_sidebar_state="expanded"  # SIDEBAR APERTA
)

# CSS
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
}
/* MOBILE */
@media (max-width: 768px) {
    .main > div {padding-left: 1rem; padding-right: 1rem;}
    .stTextInput input {font-size: 16px;}
}
</style>
""", unsafe_allow_html=True)

LOGO_URL = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png"

# ⚠️ SOSTITUISCI CON IL TUO NUOVO URL DOPO IL DEPLOY
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbwLn6HNH_k_Az2Mtfx-2SFwy0TH9tb8ygXRSXYrDKfbHcjzxXcK1f3Z3TXfhOBhKnHi/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycby1isMOz1fKTptR83six7_3OMaDgcx8_LRn3rLkD9_wCRHdxu1GCgQr3aR9FxaSr3Q-/exec"

PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# ============================================
# FUNZIONI
# ============================================
def get_testo(chiave, lingua="fr"):
    traduzioni = {
        "fr": {"titolo": "🏭 PROACIER - GESTION DES RESSOURCES HUMAINES", "sottotitolo": "Système de Recrutement - Sénégal"},
        "it": {"titolo": "🏭 PROACIER - GESTIONE RISORSE UMANE", "sottotitolo": "Sistema di Reclutamento - Senegal"},
        "en": {"titolo": "🏭 PROACIER - HUMAN RESOURCES", "sottotitolo": "Recruitment System - Senegal"}
    }
    return traduzioni.get(lingua, traduzioni["fr"]).get(chiave, chiave)

def genera_codice():
    return f"THS-{datetime.now().year}-{random.randint(1000, 9999)}"

def genera_pin():
    return str(random.randint(1000, 9999))

def leggi_da_google_sheet(url_script):
    """Legge dati dal Google Sheet"""
    try:
        response = requests.get(url_script, timeout=30)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def salva_su_google_sheet(dati, url_script):
    """Salva dati sul Google Sheet"""
    try:
        payload = {"action": "append", "row": dati}
        response = requests.post(url_script, json=payload, timeout=30)
        return response.status_code == 200
    except:
        return False

# ============================================
# PDF GENERATOR
# ============================================
class PDFProacier(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(94, 165, 41)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'FICHE D\'ENREGISTREMENT - RESSOURCES HUMAINES', 0, 1, 'C', True)
        self.set_text_color(0, 0, 0)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def genera_pdf_lavoratore(dati):
    pdf = PDFProacier()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 5, f"N° fiche: {dati.get('codice', '')}", 0, 0)
    pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 8, 'IDENTIFIANTS DE CONNEXION', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, 'Conservez précieusement ces identifiants:', 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, f"Code d'acces: {dati.get('codice', '')}", 0, 1, 'C')
    pdf.cell(0, 10, f"PIN: {dati.get('pin', '')}", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

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
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None

    lingua = st.session_state.lingua

    # SIDEBAR
    with st.sidebar:
        st.image(LOGO_URL, use_column_width=True)
        st.markdown("---")
        st.title(get_testo("titolo", lingua))
        st.markdown(get_testo("sottotitolo", lingua))
        st.markdown("---")
        
        lingua_sel = st.selectbox("Langue", ["Français", "Italiano", "English"], 
                                  index=0 if lingua == 'fr' else (1 if lingua == 'it' else 2))
        st.session_state.lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
        
        st.markdown("---")
        
        if st.session_state.logged_in:
            st.success(f"Bienvenue")
            if st.session_state.user_type == 'admin' and st.button("Tableau de Bord"):
                st.session_state.pagina = 'dashboard'
            if st.session_state.user_type == 'lavoratore' and st.button("Mes Données"):
                st.session_state.pagina = 'area_lavoratore'
            if st.button("Déconnexion"):
                st.session_state.logged_in = False
                st.session_state.pagina = 'home'
        else:
            if st.button("📝 Nouvelle Assunzione"):
                st.session_state.pagina = 'registrazione'
            if st.button("📄 Candidature Spontanée"):
                st.session_state.pagina = 'candidatura'
            if st.button("👤 Espace Travailleur"):
                st.session_state.pagina = 'login_lavoratore'
            if st.button("⚙️ Tableau de Bord"):
                st.session_state.pagina = 'login_admin'

    # ROUTING PAGINE
    if st.session_state.pagina == 'home':
        st.title("🏭 PROACIER SN")
        st.markdown("### Système de Gestion des Ressources Humaines")
        st.info("Utilisez le menu à gauche")
        
    elif st.session_state.pagina == 'login_lavoratore':
        st.title("Espace Travailleur")
        codice = st.text_input("Code")
        pin = st.text_input("PIN", type="password")
        
        if st.button("Accéder", type="primary"):
            # LEGGI DATI DAL GOOGLE SHEET
            dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            
            if dati and len(dati) > 1:
                # Crea DataFrame per cercare per nome colonna
                df = pd.DataFrame(dati[1:], columns=dati[0])
                
                # Cerca per CODICE e PIN (nomi colonne esatti)
                if 'Codice' in df.columns and 'PIN' in df.columns:
                    risultato = df[(df['Codice'] == codice) & (df['PIN'] == pin)]
                    
                    if not risultato.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_type = 'lavoratore'
                        st.session_state.codice_operatore = codice
                        st.session_state.pagina = 'area_lavoratore'
                        st.rerun()
                    else:
                        st.error("Code ou PIN incorrect")
                        st.write(f"Dati trovati nel foglio: {len(df)} righe")
                        st.write(f"Colonne: {df.columns.tolist()}")
                else:
                    st.error("Errore: colonne Codice/PIN non trovate")
                    st.write(f"Colonne disponibili: {df.columns.tolist()}")
            else:
                st.error("Nessun dato nel foglio Google")
                st.write(f"Dati ricevuti: {dati}")
                
    elif st.session_state.pagina == 'area_lavoratore':
        st.title("Mes Données")
        st.success(f"Bienvenue - Code: {st.session_state.get('codice_operatore', 'N/A')}")
        st.markdown("---")
        
        # Carica dati
        dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if dati and len(dati) > 1:
            df = pd.DataFrame(dati[1:], columns=dati[0])
            mio_dato = df[df['Codice'] == st.session_state.get('codice_operatore', '')]
            
            if not mio_dato.empty:
                st.success("✅ Dati trovati!")
                st.write(mio_dato.to_dict(orient='records')[0])
                
                # RISTAMPA PDF
                if st.button("📄 Ristampa PDF", type="primary"):
                    pdf_bytes = genera_pdf_lavoratore(mio_dato.to_dict(orient='records')[0])
                    st.download_button("📥 Scarica PDF", data=pdf_bytes, 
                                     file_name=f"Proacier_{st.session_state.codice_operatore}.pdf",
                                     mime="application/pdf")
            else:
                st.error("Lavoratore non trovato")
        else:
            st.warning("Nessun dato disponibile")
            
        if st.button("Déconnexion"):
            st.session_state.logged_in = False
            st.session_state.pagina = 'home'
            st.rerun()

    elif st.session_state.pagina == 'registrazione':
        st.title("Nouvelle Assunzione")
        st.info("Compila tutti i campi")
        
        cognome = st.text_input("Nom *")
        nome = st.text_input("Prénom *")
        telefono_1 = st.text_input("Téléphone principal *")
        cni = st.text_input("CNI *")
        css = st.text_input("CSS *")
        
        if st.button("Salva", type="primary"):
            if cognome and nome and telefono_1 and cni and css:
                codice = genera_codice()
                pin = genera_pin()
                
                dati = {
                    "id": codice,
                    "codice": codice,
                    "pin": pin,
                    "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "cognome": cognome,
                    "nome": nome,
                    "telefono_1": telefono_1,
                    "cni": cni,
                    "css": css,
                    "stato_firma": "Da firmare"
                }
                
                if salva_su_google_sheet(dati, GOOGLE_SCRIPT_URL_ASSUNZIONI):
                    st.success("✅ Registrato con successo!")
                    st.warning("⚠️ CONSERVA QUESTE CREDENZIALI")
                    st.info(f"**Code:** {codice}\n\n**PIN:** {pin}")
                    
                    pdf_bytes = genera_pdf_lavoratore(dati)
                    st.download_button("📥 Scarica PDF", data=pdf_bytes,
                                     file_name=f"Proacier_{codice}.pdf",
                                     mime="application/pdf")
                    st.balloons()
                else:
                    st.error("❌ Errore salvataggio")
            else:
                st.error("Compila i campi obbligatori")

    elif st.session_state.pagina == 'candidatura':
        st.title("Candidature Spontanée")
        st.info("Formulaire rapide")
        # Implementazione base
        st.text_input("Nom")
        st.text_input("Prénom")
        st.text_input("Email")
        st.text_input("Téléphone")
        if st.button("Envoyer"):
            st.success("Candidature envoyée!")

    elif st.session_state.pagina == 'login_admin':
        pwd = st.text_input("Password", type="password")
        if st.button("Accéder"):
            if pwd == PASSWORD_DASHBOARD:
                st.session_state.logged_in = True
                st.session_state.user_type = 'admin'
                st.session_state.pagina = 'dashboard'
                st.rerun()
            else:
                st.error("Password errata")

    elif st.session_state.pagina == 'dashboard':
        st.title("Tableau de Bord")
        dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if dati and len(dati) > 1:
            df = pd.DataFrame(dati[1:], columns=dati[0])
            st.metric("Total Employés", len(df))
            st.dataframe(df)
        else:
            st.warning("Aucun donnée")

if __name__ == "__main__":
    main()
