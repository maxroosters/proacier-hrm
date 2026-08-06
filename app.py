# -*- coding: utf-8 -*-
"""
PROACIER HRM - v20.0 - RICOSTRUZIONE PULITA
✅ Zero spazi extra / ✅ Sintassi verificata / ✅ Sheet DIPENDENTI-CANDIDATURE-SALARI
✅ Candidatura con 2 tendine (7 aree) / ✅ PDF sicuro / ✅ Senza pandas
"""
import streamlit as st
import requests
import random
from datetime import datetime
from fpdf import FPDF

# ============================================================
# CONFIGURAZIONE CENTRALE
# ============================================================
CONFIG = {
    "url_api": "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec",  # <-- URL del deploy Apps Script v2
    "email_ouvriers": "ouvriers@proacier.sn",
    "email_candidature": "candidature@proacier.sn",
    "prefisso_codice": "THS",
    "password_admin": "admin123",
    "logo_url": "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png",
}

st.set_page_config(page_title="Proacier - Ressources Humaines", page_icon="🏭",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
[data-testid="stSidebar"]{background-color:#5EA529 !important;}
[data-testid="stSidebar"] *{color:white !important;}
[data-testid="stSidebar"] button{background-color:rgba(255,255,255,0.1)!important;color:white!important;}
[data-testid="stSidebar"] select{color:white!important;background-color:rgba(0,0,0,0.3)!important;}
[data-testid="stSidebar"] option{color:black!important;}
@media (max-width:768px){.stTextInput>div>div>input,.stSelectbox>div>div>select{font-size:16px;}}
.phone-box{background-color:#5EA529;border-radius:10px;padding:10px 14px;margin:8px 0;color:white;}
.phone-box h4{margin:0 0 6px 0;color:white;font-size:15px;}
.phone-box .stTextInput>div>div>input{background-color:white;color:black;}
.phone-box .stCheckbox label{color:white;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# TRADUZIONI (fr, it, en) - formato compatto a tupla
# ============================================================
LINGUE = {"fr": 0, "it": 1, "en": 2}
T = {
"titolo": ("🏭 PROACIER - GESTION DES RESSOURCES HUMAINES", "🏭 PROACIER - GESTIONE RISORSE UMANE", "🏭 PROACIER - HUMAN RESOURCES"),
"sottotitolo": ("Système de Recrutement - Sénégal", "Sistema di Reclutamento - Senegal", "Recruitment System - Senegal"),
"lingua": ("Langue", "Lingua", "Language"),
"candidatura_spontanea": ("📄 Candidature Spontanée", "📄 Candidatura Spontanea", "📄 Spontaneous Application"),
"dashboard": ("Tableau de Bord", "Dashboard", "Dashboard"),
"area_lavoratore": ("Espace Travailleur", "Spazio Lavoratore", "Worker Space"),
"logout": ("Déconnexion", "Esci", "Logout"),
"benvenuto": ("Bienvenue", "Benvenuto", "Welcome"),
"password": ("Mot de passe", "Password", "Password"),
"accedi": ("Accéder", "Accedi", "Login"),
"codice": ("Code", "Codice", "Code"),
"pin": ("PIN", "PIN", "PIN"),
"codice_errato": ("Code ou PIN incorrect", "Codice o PIN errati", "Wrong code or PIN"),
"i_miei_dati": ("Mes Données", "I Miei Dati", "My Data"),
"totale_operai": ("Total Employés", "Totale Dipendenti", "Total Employees"),
"nessun_risultato": ("Aucun résultat trouvé", "Nessun risultato", "No results found"),
"home_titolo": ("📋 À quoi sert cette application?", "📋 A cosa serve questa applicazione?", "📋 What is this application for?"),
"home_p1_t": ("Transmission de données nouveaux travailleurs", "Trasmissione dati nuovi lavoratori", "Data transmission new workers"),
"home_p1_d": ("Formulaire en 7 étapes + PDF automatique", "Modulo in 7 fasi + PDF automatico", "7-step form + automatic PDF"),
"home_p2_t": ("Candidatures spontanées", "Candidature spontanee", "Spontaneous applications"),
"home_p2_d": ("Formulaire rapide, évaluation RH", "Modulo rapido, valutazione HR", "Quick form, HR evaluation"),
"home_p3_t": ("Espace personnel travailleur", "Spazio personale lavoratore", "Personal worker space"),
"home_p3_d": ("Accès avec code et PIN", "Accesso con codice e PIN", "Access with code and PIN"),
"home_p4_t": ("Paiement des journaliers", "Pagamento giornalieri", "Daily workers payment"),
"home_p4_d": ("Gestion présences et calcul compensi", "Gestione presenze e calcolo compensi", "Attendance and payment calculation"),
"home_navigation": ("🚀 Navigation rapide", "🚀 Navigazione rapida", "🚀 Quick navigation"),
"giornalieri_titolo": ("Déjà travailleur?", "Già lavoratore?", "Already a worker?"),
"giornalieri_desc": ("Accédez à votre espace personnel", "Accedi al tuo spazio", "Access your space"),
"nuovo_giornaliero_titolo": ("Nouveau / Journalier?", "Nuovo / Giornaliero?", "New / Daily worker?"),
"nuovo_giornaliero_desc": ("Transmettez vos données (pas un contrat)", "Trasmetti i tuoi dati (non un contratto)", "Submit your data (not a contract)"),
"login_btn": ("🔐 Connexion à mon espace", "🔐 Accedi al mio spazio", "🔐 Login to my space"),
"trasmissione_btn": ("📝 Transmettre mes données", "📝 Trasmetti i miei dati", "📝 Submit my data"),
"step_1": ("1. Données Personnelles & Famille", "1. Dati Personali e Famiglia", "1. Personal Data & Family"),
"step_2": ("2. Adresse, Documents & Services", "2. Indirizzo, Documenti e Servizi", "2. Address, Documents & Services"),
"step_3": ("3. Expérience Professionnelle", "3. Esperienza Professionale", "3. Professional Experience"),
"step_4": ("4. Compétences & Permis", "4. Competenze e Patente", "4. Skills & License"),
"step_5": ("5. Informations Médicales", "5. Informazioni Mediche", "5. Medical Information"),
"step_6": ("6. Contact d'Urgence", "6. Contatto Emergenza", "6. Emergency Contact"),
"step_7": ("7. Vêtements & EPI", "7. Vestiario e DPI", "7. Clothing & PPE"),
"continua": ("Continuer →", "Continua →", "Continue →"),
"indietro": ("← Retour", "← Indietro", "← Back"),
"genera_pdf": ("📄 J'accepte les conditions", "📄 Accetto le condizioni", "📄 I accept the conditions"),
"pdf_generato": ("Enregistrement réussi!", "Registrazione riuscita!", "Registration successful!"),
"conserva_credenziali": ("⚠️ CONSERVEZ CES IDENTIFIANTS", "⚠️ CONSERVA QUESTE CREDENZIALI", "⚠️ SAVE THESE CREDENTIALS"),
"codice_accesso": ("Code d'accès", "Codice di accesso", "Access code"),
"pin_accesso": ("PIN d'accès", "PIN di accesso", "Access PIN"),
"scarica": ("Télécharger", "Scarica", "Download"),
"ristampa_pdf": ("📄 Réimprimer PDF identifiants", "📄 Ristampa PDF credenziali", "📄 Reprint PDF credentials"),
"checkbox_confirm": ("J'ai lu et j'accepte les conditions générales et la politique de confidentialité", "Ho letto e accetto le condizioni generali e la politica sulla privacy", "I have read and accept the general conditions and privacy policy"),
"cocher_case": ("Veuillez cocher la case de confirmation", "Seleziona la casella di conferma", "Please check the confirmation box"),
"errore_obbligatori": ("Veuillez remplir tous les champs obligatoires (*)", "Compila tutti i campi obbligatori (*)", "Please fill in all required fields (*)"),
"avviso_non_contratto": ("⚠️ Ceci n'est PAS un contrat d'embauche. Uniquement une transmission de données à l'administration.", "⚠️ Questo NON è un contratto di assunzione. Solo una trasmissione di dati all'amministrazione.", "⚠️ This is NOT an employment contract. Only a data transmission to the administration."),
"avviso_regole_aziendali": ("📋 En soumettant ce formulaire, vous acceptez les règles de l'entreprise et la politique de confidentialité de PROACIER.", "📋 Inviando questo modulo, accetti le regole aziendali e la politica sulla privacy di PROACIER.", "📋 By submitting this form, you accept the company rules and PROACIER's privacy policy."),
"cognome": ("Nom", "Cognome", "Surname"),
"nome": ("Prénom(s)", "Nome", "First Name"),
"data_nascita": ("Date de naissance", "Data di nascita", "Date of birth"),
"giorno": ("Jour", "Giorno", "Day"),
"mese": ("Mois", "Mese", "Month"),
"anno": ("Année", "Anno", "Year"),
"luogo_nascita": ("Lieu de naissance", "Luogo di nascita", "Place of birth"),
"nazionalita": ("Nationalité", "Nazionalità", "Nationality"),
"paese_origine": ("Pays d'origine", "Paese di origine", "Country of origin"),
"sesso": ("Sexe", "Sesso", "Gender"),
"maschile": ("Masculin", "Maschile", "Male"),
"femminile": ("Féminin", "Femminile", "Female"),
"stato_civile": ("État civil", "Stato civile", "Marital status"),
"celibe": ("Célibataire", "Celibe/Nubile", "Single"),
"coniugato": ("Marié(e)", "Coniugato/a", "Married"),
"divorziato": ("Divorcé(e)", "Divorziato/a", "Divorced"),
"vedovo": ("Veuf/Veuve", "Vedovo/a", "Widowed"),
"numero_mogli": ("Nombre d'épouses", "Numero di mogli", "Number of wives"),
"figli_totale": ("Nombre total d'enfants", "Numero totale di figli", "Total number of children"),
"residenza_moglie": ("Lieu de résidence de l'épouse", "Residenza della moglie", "Wife's residence"),
"figli_moglie": ("Enfants avec cette épouse", "Figli con questa moglie", "Children with this wife"),
"indirizzo": ("Adresse actuelle", "Indirizzo attuale", "Current address"),
"quartiere": ("Quartier/Village", "Quartiere/Villaggio", "District/Village"),
"comune": ("Commune", "Comune", "Municipality"),
"regione_senegal": ("Région", "Regione", "Region"),
"telefono_1": ("Téléphone principal", "Telefono principale", "Main phone"),
"telefono_2": ("Téléphone secondaire", "Telefono secondario", "Secondary phone"),
"telefono_3": ("Téléphone 3", "Telefono 3", "Phone 3"),
"servizi_telefono": ("Services associés", "Servizi associati", "Phone services"),
"cni": ("N° CNI", "N° CNI", "ID Number (CNI)"),
"nif": ("NIF", "NIF", "NIF"),
"css": ("N° CSS", "N° CSS", "Social Security (CSS)"),
"cmu": ("N° CMU", "N° CMU", "CMU"),
"ipres": ("N° IPRES", "N° IPRES", "IPRES"),
"nota_lavoro": ("Indiquez vos 3 dernières expériences.", "Indica le tue ultime 3 esperienze.", "Indicate your last 3 experiences."),
"azienda": ("Entreprise", "Azienda", "Company"),
"mansione": ("Fonction", "Mansione", "Position"),
"data_inizio": ("Début", "Inizio", "Start"),
"data_fine": ("Fin", "Fine", "End"),
"motivo_uscita": ("Motif de départ", "Motivo uscita", "Reason for leaving"),
"nota_competenze": ("Indiquez vos compétences principales.", "Indica le tue competenze principali.", "Indicate your main skills."),
"categoria_competenza": ("Catégorie de compétence", "Categoria di competenza", "Skill category"),
"dettaglio_competenza": ("Détails", "Dettagli", "Details"),
"patente": ("Permis de conduire", "Patente di guida", "Driver's license"),
"nota_patente": ("⚠️ Une photocopie du permis sera exigée.", "⚠️ Sarà richiesta una fotocopia della patente.", "⚠️ A photocopy of the license will be required."),
"gruppo_sanguigno": ("Groupe sanguin", "Gruppo sanguigno", "Blood type"),
"rh": ("Rh", "Rh", "Rh"),
"allergie": ("Allergies", "Allergie", "Allergies"),
"malattie": ("Maladies chroniques", "Malattie croniche", "Chronic diseases"),
"idoneita": ("Aptitude médicale", "Idoneità medica", "Medical fitness"),
"apte": ("Apte", "Apto", "Fit"),
"restriction": ("Apte avec restriction", "Apto con restrizioni", "Fit with restrictions"),
"inapte": ("Inapte", "Inapto", "Unfit"),
"data_visita": ("Date visite", "Data visita", "Visit date"),
"emergenza_nome": ("Contact urgence (Nom)", "Contatto emergenza (Nome)", "Emergency contact (Name)"),
"emergenza_parentela": ("Lien", "Parentela", "Relationship"),
"emergenza_tel": ("Tél urgence", "Tel emergenza", "Emergency phone"),
"emergenza_indirizzo": ("Adresse urgence", "Indirizzo emergenza", "Emergency address"),
"cat_edilizia": ("Bâtiment", "Edilizia", "Construction"),
"cat_contabilita": ("Comptabilité", "Contabilità", "Accounting"),
"cat_meccanica": ("Mécanique", "Meccanica", "Mechanics"),
"cat_elettrico": ("Électricité", "Elettrico", "Electrical"),
"cat_agricoltura": ("Agriculture", "Agricoltura", "Agriculture"),
"cat_altro": ("Autre", "Altro", "Other"),
"titolo_vestiario": ("Tailles Vêtements & EPI", "Taglie Abbigliamento e DPI", "Clothing & PPE Sizes"),
"taglia_maglia": ("Taille t-shirt/polo", "Taglia t-shirt/polo", "T-shirt/polo size"),
"taglia_pantaloni": ("Taille pantalon", "Taglia pantalone", "Pants size"),
"taglia_scarpe": ("Pointure chaussures", "Numero scarpe", "Shoe size"),
"taglia_giacca": ("Taille veste/gilet", "Taglia giacca/gilet", "Jacket/vest size"),
"taglia_cappello": ("Taille casque/casquette", "Taglia casco/cappellino", "Helmet/cap size"),
"taglia_guanti": ("Taille gants", "Taglia guanti", "Gloves size"),
"paese_senegal": ("Sénégal", "Senegal", "Senegal"),
"paese_mali": ("Mali", "Mali", "Mali"),
"paese_burkina": ("Burkina Faso", "Burkina Faso", "Burkina Faso"),
"paese_sierra": ("Sierra Leone", "Sierra Leone", "Sierra Leone"),
"paese_guinea": ("Guinée", "Guinea", "Guinea"),
"paese_gambia": ("Gambie", "Gambia", "Gambia"),
"paese_altro": ("Autre pays", "Altro paese", "Other country"),
"titolo_candidatura": ("CANDIDATURE SPONTANÉE", "CANDIDATURA SPONTANEA", "SPONTANEOUS APPLICATION"),
"sottotitolo_candidatura": ("Rejoignez l'équipe PROACIER.", "Unisciti al team PROACIER.", "Join the PROACIER team."),
"email": ("Adresse Email", "Indirizzo Email", "Email Address"),
"settore_richiesto": ("Secteur d'intérêt", "Settore di interesse", "Area of interest"),
"mansione_richiesta": ("Poste recherché", "Ruolo richiesto", "Desired position"),
"altro_specifica": ("Précisez le rôle souhaité", "Specifica il ruolo desiderato", "Specify the desired role"),
"studi": ("Niveau d'études", "Titolo di studio", "Education level"),
"opt_media": ("École moyenne", "Licenza media", "Middle school"),
"opt_diploma": ("Baccalauréat / Diplôme", "Diploma", "High school / Diploma"),
"opt_laurea": ("Université / Licence", "Laurea", "University / Degree"),
"opt_prof": ("Formation professionnelle", "Formazione professionale", "Vocational training"),
"skills": ("Compétences / Skills", "Competenze / Skills", "Skills / Competencies"),
"esperienza_anno": ("Années d'expérience", "Anni di esperienza", "Years of experience"),
"salario_richiesto": ("Prétention salariale (FCFA)", "Retribuzione richiesta (FCFA)", "Expected salary (FCFA)"),
"note": ("Notes supplémentaires", "Note aggiuntive", "Additional notes"),
"invia_candidatura": ("📤 Envoyer ma candidature", "📤 Invia la mia candidatura", "📤 Submit my application"),
"candidatura_inviata": ("✅ Candidature envoyée avec succès!", "✅ Candidatura inviata con successo!", "✅ Application submitted successfully!"),
"errore_candidatura": ("Veuillez remplir Nom, Prénom, Email et Téléphone.", "Compila Cognome, Nome, Email e Telefono.", "Please fill in Surname, First Name, Email, and Phone."),
"sezione_dati_personali": ("📋 Données Personnelles (non modifiables)", "📋 Dati Personali (non modificabili)", "📋 Personal Data (non-modifiable)"),
"sezione_paga": ("💰 Informations Salariales", "💰 Informazioni Salariali", "💰 Salary Information"),
"sezione_contatti": ("📞 Coordonnées (modifiables)", "📞 Contatti (modificabili)", "📞 Contact Info (modifiable)"),
"sezione_famille": ("👨‍👩‍👧‍ Famille (modifiable)", "👨‍👩‍👧‍ Famiglia (modificabile)", "👨‍‍👧👦 Family (modifiable)"),
"sezione_vestiario": ("👕 Vêtements & EPI (modifiables)", "👕 Vestiario e DPI (modificabili)", "👕 Clothing & PPE (modifiable)"),
"sezione_comunicazioni": ("💬 Communications & Demandes (bientôt disponible)", "💬 Comunicazioni e Richieste (prossimamente)", "💬 Communications & Requests (coming soon)"),
"paga_desc": ("Votre salaire est géré par l'administration.", "Il tuo salario è gestito dall'amministrazione.", "Your salary is managed by administration."),
"paga_type": ("Type de paiement", "Tipo di pagamento", "Payment type"),
"paga_amount": ("Montant", "Importo", "Amount"),
"salva_modifiche": ("💾 Enregistrer les modifications", "💾 Salva modifiche", "💾 Save changes"),
"modifiche_salvate": ("✅ Modifications enregistrées avec succès!", "✅ Modifiche salvate con successo!", "✅ Changes saved successfully!"),
"errore_salvataggio": ("❌ Erreur lors de l'enregistrement.", "❌ Errore durante il salvataggio.", "❌ Error saving."),
}

def get_testo(chiave, lingua="fr"):
    t = T.get(chiave)
    if not t:
        return chiave
    return t[LINGUE.get(lingua, 0)]

# ============================================================
# AREE AZIENDALI (candidatura a 2 tendine)
# ============================================================
AREE_AZIENDALI = [
{"label": ("Direction & Staff", "Direzione e Staff", "Management & Staff"), "ruoli": ["Directeur / Responsable d'Usine", "Responsable Production", "Responsable Qualité", "Responsable HSE", "Responsable RH / Administration", "Responsable Achats & Logistique", "Comptable / Assistant Comptable"]},
{"label": ("Marketing & Ventes", "Marketing e Vendite", "Marketing & Sales"), "ruoli": ["Responsable Commercial / Directeur Commercial", "Commercial / Vendeur (B2B)", "Responsable Marketing", "Community Manager / Social Media Manager", "Responsable Communication & Promotion", "Assistant Commercial / Assistant Marketing"]},
{"label": ("Production", "Produzione", "Production"), "ruoli": ["Chef d'Atelier / Superviseur de Production", "Opérateur de Four de Réchauffage", "Opérateur de Laminoir", "Opérateur de Cisaille / Coupe", "Opérateur de Refroidissement & Redressage", "Opérateur de Bundling / Emballage", "Aide-opérateur / Manœuvre de production"]},
{"label": ("Maintenance", "Manutenzione", "Maintenance"), "ruoli": ["Responsable Maintenance", "Technicien Mécanicien", "Technicien Électricien / Automatisme", "Technicien Hydraulique", "Soudeur", "Aide-mécanicien / Aide-électricien"]},
{"label": ("Qualité & Contrôle", "Qualità e Controllo", "Quality & Control"), "ruoli": ["Technicien Qualité / Inspecteur", "Technicien de Laboratoire"]},
{"label": ("Logistique & Magasin", "Logistica e Magazzino", "Logistics & Warehouse"), "ruoli": ["Magasinier", "Chauffeur de Chariot Élévateur / Pontier", "Opérateur de Chargement / Expédition"]},
{"label": ("Autres Services", "Altri Servizi", "Other Services"), "ruoli": ["Agent de Sécurité", "Agent d'Entretien / Nettoyage", "Secouriste / Infirmier d'entreprise"]},
{"label": ("Autre", "Altro", "Other"), "ruoli": []},
]

# ============================================================
# HELPERS
# ============================================================
def genera_codice():
    return f"{CONFIG['prefisso_codice']}-{datetime.now().year}-{random.randint(1000, 9999)}"

def genera_pin():
    return str(random.randint(1000, 9999))

def leggi_foglio(nome_foglio):
    """Ritorna (headers, records) oppure ([], [])"""
    try:
        r = requests.get(CONFIG["url_api"], params={"sheet": nome_foglio}, timeout=30)
        data = r.json()
        if isinstance(data, dict) or not data:
            return [], []
        headers = [str(h).strip() for h in data[0]]
        records = [dict(zip(headers, row)) for row in data[1:]]
        return headers, records
    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
        return [], []

def _post_json(payload):
    try:
        r = requests.post(CONFIG["url_api"], json=payload, timeout=60)
        if r.status_code == 200:
            try:
                j = r.json()
                if isinstance(j, dict):
                    if j.get("status") == "success":
                        return True, "ok"
                    return False, j.get("message", "Errore server")
                return False, "Risposta inattesa"
            except Exception:
                return False, "Risposta non JSON"
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)

def salva_append(nome_foglio, row, chiave_id=None, valore_id=None):
    ok, msg = _post_json({"sheet": nome_foglio, "action": "append", "row": row})
    if not ok and chiave_id:
        try:
            _, recs = leggi_foglio(nome_foglio)
            if any(s_str(r.get(chiave_id)) == s_str(valore_id) for r in recs):
                return True, "ok (verificato sul foglio)"
        except Exception:
            pass
    return ok, msg

def salva_update(nome_foglio, row_index, row):
    return _post_json({"sheet": nome_foglio, "action": "update", "rowIndex": row_index, "row": row})

def s_str(v):
    if v is None:
        return ""
    s = str(v)
    if s in ("nan", "None", "#ERROR!"):
        return ""
    return s.strip()

def s_int(v):
    try:
        return int(float(s_str(v) or 0))
    except Exception:
        return 0

def formatta_data(v):
    s = s_str(v)
    if not s:
        return ""
    if "T" in s:
        s = s.split("T")[0]
        p = s.split("-")
        if len(p) == 3:
            return f"{p[2]}/{p[1]}/{p[0]}"
    return s

# ============================================================
# GENERATORE PDF (tutti valori come stringa = zero TypeError)
# ============================================================
class PDFProacier(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(94, 165, 41)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "FICHE D'ENREGISTREMENT - RESSOURCES HUMAINES", 0, 1, "C", True)
        self.set_text_color(0, 0, 0)
        self.ln(2)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")
    def sezione(self, titolo):
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(217, 225, 242)
        self.cell(0, 6, titolo, 0, 1, "C", True)
        self.ln(1)
    def campo(self, et, val):
        self.set_font("Helvetica", "B", 8)
        self.cell(60, 5, et, 0, 0)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 5, s_str(val) or "___________", 0, 1)
    def campo_doppio(self, e1, v1, e2, v2):
        self.set_font("Helvetica", "B", 8)
        self.cell(50, 5, e1, 0, 0)
        self.set_font("Helvetica", "", 8)
        self.cell(45, 5, s_str(v1) or "______", 0, 0)
        self.set_font("Helvetica", "B", 8)
        self.cell(50, 5, e2, 0, 0)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 5, s_str(v2) or "______", 0, 1)

def genera_pdf_lavoratore(d):
    pdf = PDFProacier()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 5, f"N° fiche: {s_str(d.get('codice'))}", 0, 0)
    pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, "R")
    pdf.ln(2)
    pdf.sezione("1. IDENTITE & FAMILLE")
    pdf.campo_doppio("Nom:", d.get("cognome"), "Prenom(s):", d.get("nome"))
    pdf.campo_doppio("Ne(e) le:", formatta_data(d.get("data_nascita")), "a:", d.get("luogo_nascita"))
    pdf.campo_doppio("Nationalite:", d.get("nazionalita"), "Pays:", d.get("paese_origine"))
    pdf.campo_doppio("Etat civil:", d.get("stato_civile"), "Enfants:", d.get("figli_totale"))
    if s_int(d.get("numero_mogli")) > 0:
        pdf.campo("Epouses:", s_str(d.get("dettagli_mogli")))
    pdf.ln(1)
    pdf.sezione("2. CONTACT & DOCUMENTS")
    pdf.campo("Adresse:", f"{s_str(d.get('indirizzo'))}, {s_str(d.get('quartiere'))}, {s_str(d.get('regione_senegal'))}")
    pdf.campo_doppio("Tel 1:", d.get("telefono_1"), "Tel 2:", d.get("telefono_2"))
    pdf.campo_doppio("CNI:", d.get("cni"), "CSS:", d.get("css"))
    pdf.campo_doppio("NIF:", d.get("nif"), "IPRES:", d.get("ipres"))
    pdf.ln(1)
    pdf.sezione("3. EXPERIENCE & COMPETENCES")
    pdf.campo("Poste:", d.get("mansione_1"))
    pdf.campo("Competence:", f"{s_str(d.get('categoria_competenza'))} - {s_str(d.get('dettaglio_competenza'))}")
    pdf.campo("Permis:", d.get("patente"))
    pdf.ln(1)
    pdf.sezione("4. VETEMENTS & EPI")
    pdf.campo_doppio("T-shirt:", d.get("taglia_maglia"), "Pantalon:", d.get("taglia_pantaloni"))
    pdf.campo_doppio("Pointure:", d.get("taglia_scarpe"), "Gilet:", d.get("taglia_giacca"))
    pdf.campo_doppio("Casque:", d.get("taglia_cappello"), "Gants:", d.get("taglia_guanti"))
    pdf.ln(1)
    pdf.sezione("5. MEDICAL & URGENCE")
    pdf.campo_doppio("Groupe:", f"{s_str(d.get('gruppo_sanguigno'))} {s_str(d.get('rh'))}", "Aptitude:", d.get("idoneita"))
    pdf.campo_doppio("Urgence:", d.get("emergenza_nome"), "Tel:", d.get("emergenza_tel"))
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, "Je certifie l'exactitude des informations et accepte les conditions.")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 6, "CANDIDAT", 1, 0, "C")
    pdf.cell(95, 6, "EMPLOYEUR", 1, 1, "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(95, 15, "", 1, 0)
    pdf.cell(95, 15, "", 1, 1)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "CONSENTEMENT DONNEES PERSONNELLES", 0, 1, "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, "Conformement a la Loi n° 2008-12 du 25 janvier 2008 (Senegal).")
    pdf.ln(10)
    pdf.cell(0, 6, "Signature:", 0, 1)
    pdf.cell(0, 20, "", 1, 1)
    pdf.add_page()
    pdf.set_fill_color(255, 243, 205)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "IDENTIFIANTS DE CONNEXION", 0, 1, "C", True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Conservez precieusement ces identifiants:", 0, 1, "C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, f"Code d'acces: {s_str(d.get('codice')) or '___________'}", 0, 1, "C")
    pdf.ln(3)
    pdf.cell(0, 12, f"PIN: {s_str(d.get('pin')) or '___________'}", 0, 1, "C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 5, "Ces identifiants sont personnels et confidentiels. Ne les partagez avec personne.")
    pdf.set_text_color(0, 0, 0)
    out = pdf.output(dest="S")
    if isinstance(out, str):
        out = out.encode("latin-1", errors="ignore")
    return bytes(out)

# ============================================================
# STEP DEL FORMULARIO
# ============================================================
def lista_paesi(lingua):
    return [get_testo(k, lingua) for k in ("paese_senegal", "paese_mali", "paese_burkina", "paese_sierra", "paese_guinea", "paese_gambia", "paese_altro")]

def box_telefono(lingua, n, obbligatorio=False):
    st.markdown(f'<div class="phone-box"><h4>{get_testo("telefono_" + str(n), lingua)}{" *" if obbligatorio else ""}</h4></div>', unsafe_allow_html=True)
    tel = st.text_input(f"Numero {n}", value=st.session_state.dati_form.get(f"telefono_{n}", ""), key=f"s2_tel{n}", label_visibility="collapsed")
    servizi_attivi = s_str(st.session_state.dati_form.get(f"servizi_tel{n}", "")).split(",")
    cb = st.columns(5)
    sel = {}
    for i, sv in enumerate(("Wave", "Orange Money", "WhatsApp", "Telegram", "Signal")):
        sel[sv] = cb[i].checkbox(sv, value=sv in servizi_attivi, key=f"s2_sv{n}_{i}")
    servizi = ",".join([k for k, v in sel.items() if v])
    return tel, servizi

def step_1(lingua):
    st.subheader(get_testo("step_1", lingua))
    c1, c2 = st.columns(2)
    with c1:
        cognome = st.text_input(f'{get_testo("cognome", lingua)} *', value=st.session_state.dati_form.get("cognome", ""), key="s1_cog")
        nome = st.text_input(f'{get_testo("nome", lingua)} *', value=st.session_state.dati_form.get("nome", ""), key="s1_nom")
        st.markdown(f'**{get_testo("data_nascita", lingua)}**')
        g, m, a = st.columns(3)
        giorno = g.selectbox(get_testo("giorno", lingua), list(range(1, 32)), key="s1_g")
        mese = m.selectbox(get_testo("mese", lingua), list(range(1, 13)), key="s1_m")
        anno = a.selectbox(get_testo("anno", lingua), list(range(1950, 2010)), index=30, key="s1_a")
        luogo = st.text_input(get_testo("luogo_nascita", lingua), value=st.session_state.dati_form.get("luogo_nascita", ""), key="s1_luo")
        paesi = lista_paesi(lingua)
        naz_sel = st.selectbox(get_testo("nazionalita", lingua), paesi, key="s1_naz")
        naz = st.text_input("Précisez:", key="s1_naz_a") if naz_sel == get_testo("paese_altro", lingua) else naz_sel
        por_sel = st.selectbox(get_testo("paese_origine", lingua), paesi, key="s1_pae")
        por = st.text_input("Précisez:", key="s1_pae_a") if por_sel == get_testo("paese_altro", lingua) else por_sel
    with c2:
        sesso = st.selectbox(get_testo("sesso", lingua), [get_testo("maschile", lingua), get_testo("femminile", lingua)], key="s1_ses")
        stato_civile = st.selectbox(get_testo("stato_civile", lingua), [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)], key="s1_sta")
        numero_mogli, dettagli_mogli, figli_tot = 0, "", 0
        if stato_civile == get_testo("coniugato", lingua):
            numero_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=1, key="s1_mog")
            det = []
            for i in range(1, numero_mogli + 1):
                st.markdown(f"**Épouse {i}**")
                cr, cf = st.columns(2)
                res = cr.text_input(f'{get_testo("residenza_moglie", lingua)} {i}', key=f"s1_res{i}")
                fig = cf.number_input(f'{get_testo("figli_moglie", lingua)} {i}', min_value=0, value=0, key=f"s1_fig{i}")
                figli_tot += fig
                det.append(f"Épouse {i}: {res} ({fig} enfants)")
            dettagli_mogli = " | ".join(det)
            st.info(f'ℹ️ {get_testo("figli_totale", lingua)}: {figli_tot}')
    return {"cognome": cognome, "nome": nome, "data_nascita": f"{giorno:02d}/{mese:02d}/{anno}",
            "luogo_nascita": luogo, "nazionalita": naz, "paese_origine": por, "sesso": sesso,
            "stato_civile": stato_civile, "numero_mogli": numero_mogli, "dettagli_mogli": dettagli_mogli,
            "figli_totale": figli_tot}

def step_2(lingua):
    st.subheader(get_testo("step_2", lingua))
    c1, c2 = st.columns(2)
    with c1:
        indirizzo = st.text_input(f'{get_testo("indirizzo", lingua)} *', value=st.session_state.dati_form.get("indirizzo", ""), key="s2_ind")
        quartiere = st.text_input(get_testo("quartiere", lingua), value=st.session_state.dati_form.get("quartiere", ""), key="s2_qua")
        comune = st.text_input(get_testo("comune", lingua), value=st.session_state.dati_form.get("comune", ""), key="s2_com")
        regione = st.selectbox(get_testo("regione_senegal", lingua), ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"], key="s2_reg")
        st.markdown("---")
        cni = st.text_input(get_testo("cni", lingua), value=st.session_state.dati_form.get("cni", ""), key="s2_cni")
        nif = st.text_input(get_testo("nif", lingua), value=st.session_state.dati_form.get("nif", ""), key="s2_nif")
        css = st.text_input(get_testo("css", lingua), value=st.session_state.dati_form.get("css", ""), key="s2_css")
        cmu = st.text_input(get_testo("cmu", lingua), value=st.session_state.dati_form.get("cmu", ""), key="s2_cmu")
        ipres = st.text_input(get_testo("ipres", lingua), value=st.session_state.dati_form.get("ipres", ""), key="s2_ipr")
    with c2:
        tel1, sv1 = box_telefono(lingua, 1, True)
        tel2, sv2 = box_telefono(lingua, 2)
        tel3, sv3 = box_telefono(lingua, 3)
    return {"indirizzo": indirizzo, "quartiere": quartiere, "comune": comune, "regione_senegal": regione,
            "cni": cni, "nif": nif, "css": css, "cmu": cmu, "ipres": ipres,
            "telefono_1": tel1, "servizi_tel1": sv1, "telefono_2": tel2, "servizi_tel2": sv2,
            "telefono_3": tel3, "servizi_tel3": sv3}

def step_3(lingua):
    st.subheader(get_testo("step_3", lingua))
    st.info(get_testo("nota_lavoro", lingua))
    out = {}
    for i in range(1, 4):
        st.markdown(f"**Emploi {i}**")
        c1, c2 = st.columns(2)
        with c1:
            out[f"azienda_{i}"] = st.text_input(get_testo("azienda", lingua), key=f"s3_az{i}")
            out[f"mansione_{i}"] = st.text_input(get_testo("mansione", lingua), key=f"s3_ma{i}")
        with c2:
            out[f"data_inizio_{i}"] = st.text_input(f'{get_testo("data_inizio", lingua)} (MM/AAAA)', key=f"s3_di{i}")
            out[f"data_fine_{i}"] = st.text_input(f'{get_testo("data_fine", lingua)} (MM/AAAA)', key=f"s3_df{i}")
            out[f"motivo_uscita_{i}"] = st.text_input(get_testo("motivo_uscita", lingua), key=f"s3_mu{i}")
        st.markdown("---")
    return out

def step_4(lingua):
    st.subheader(get_testo("step_4", lingua))
    st.info(get_testo("nota_competenze", lingua))
    cats = [get_testo(k, lingua) for k in ("cat_edilizia", "cat_contabilita", "cat_meccanica", "cat_elettrico", "cat_agricoltura", "cat_altro")]
    categoria = st.selectbox(get_testo("categoria_competenza", lingua), cats, key="s4_cat")
    dettaglio = st.text_area(get_testo("dettaglio_competenza", lingua), key="s4_det")
    patente = st.text_input(get_testo("patente", lingua), key="s4_pat")
    st.caption(get_testo("nota_patente", lingua))
    return {"categoria_competenza": categoria, "dettaglio_competenza": dettaglio, "patente": patente}

def step_5(lingua):
    st.subheader(get_testo("step_5", lingua))
    c1, c2 = st.columns(2)
    with c1:
        gruppo = st.selectbox(get_testo("gruppo_sanguigno", lingua), ["A", "B", "AB", "O"], key="s5_gru")
        rh = st.selectbox(get_testo("rh", lingua), ["+", "-"], key="s5_rh")
        allergie = st.text_area(get_testo("allergie", lingua), key="s5_all")
    with c2:
        malattie = st.text_area(get_testo("malattie", lingua), key="s5_mal")
        idoneita = st.selectbox(get_testo("idoneita", lingua), [get_testo("apte", lingua), get_testo("restriction", lingua), get_testo("inapte", lingua)], key="s5_ido")
        data_visita = st.text_input(f'{get_testo("data_visita", lingua)} (GG/MM/AAAA)', key="s5_dat")
    return {"gruppo_sanguigno": gruppo, "rh": rh, "allergie": allergie, "malattie": malattie,
            "idoneita": idoneita, "data_visita": data_visita}

def step_6(lingua):
    st.subheader(get_testo("step_6", lingua))
    c1, c2 = st.columns(2)
    with c1:
        em_nome = st.text_input(get_testo("emergenza_nome", lingua), key="s6_no")
        em_par = st.text_input(get_testo("emergenza_parentela", lingua), key="s6_pa")
    with c2:
        em_tel = st.text_input(get_testo("emergenza_tel", lingua), key="s6_te")
        em_ind = st.text_input(get_testo("emergenza_indirizzo", lingua), key="s6_in")
    return {"emergenza_nome": em_nome, "emergenza_parentela": em_par, "emergenza_tel": em_tel,
            "emergenza_indirizzo": em_ind}

def step_7(lingua):
    st.subheader(get_testo("step_7", lingua))
    st.markdown(f'### {get_testo("titolo_vestiario", lingua)}')
    c1, c2 = st.columns(2)
    xs = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
    with c1:
        tm = st.selectbox(get_testo("taglia_maglia", lingua), xs, key="s7_ma")
        tp = st.selectbox(get_testo("taglia_pantaloni", lingua), ["38", "40", "42", "44", "46", "48", "50", "52"], key="s7_pa")
        ts = st.selectbox(get_testo("taglia_scarpe", lingua), [str(x) for x in range(38, 48)], key="s7_sc")
    with c2:
        tg = st.selectbox(get_testo("taglia_giacca", lingua), xs[:-1], key="s7_gi")
        tc = st.selectbox(get_testo("taglia_cappello", lingua), ["S", "M", "L", "XL"], key="s7_ca")
        tgu = st.selectbox(get_testo("taglia_guanti", lingua), ["S", "M", "L", "XL"], key="s7_gu")
    return {"taglia_maglia": tm, "taglia_pantaloni": tp, "taglia_scarpe": ts,
            "taglia_giacca": tg, "taglia_cappello": tc, "taglia_guanti": tgu}

# ============================================================
# PAGINA REGISTRAZIONE MULTI-STEP
# ============================================================
def pagina_registrazione(lingua):
    step = st.session_state.step
    if step == 1 and not st.session_state.avviso_mostrato:
        st.warning(get_testo("avviso_non_contratto", lingua))
        st.info(get_testo("avviso_regole_aziendali", lingua))
        st.session_state.avviso_mostrato = True
    st.progress(step / 7)
    st.markdown(f"**Étape {step} / 7**")
    st.markdown("---")
    fn = {1: step_1, 2: step_2, 3: step_3, 4: step_4, 5: step_5, 6: step_6, 7: step_7}[step]
    dati_step = fn(lingua)
    st.session_state.dati_form.update(dati_step)
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if step > 1 and st.button(get_testo("indietro", lingua), use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with c2:
        if step < 7:
            if st.button(get_testo("continua", lingua), type="primary", use_container_width=True):
                if step == 1 and (not dati_step.get("cognome") or not dati_step.get("nome")):
                    st.error(get_testo("errore_obbligatori", lingua))
                elif step == 2 and not dati_step.get("telefono_1"):
                    st.error(get_testo("errore_obbligatori", lingua))
                else:
                    st.session_state.step += 1
                    st.rerun()
        else:
            conferma = st.checkbox(get_testo("checkbox_confirm", lingua), key="s7_conf")
            if conferma:
                if st.button(get_testo("genera_pdf", lingua), type="primary", use_container_width=True):
                    genera_e_salva(st.session_state.dati_form, lingua)
            else:
                st.warning(get_testo("cocher_case", lingua))

def genera_e_salva(dati, lingua):
    codice = genera_codice()
    pin = genera_pin()
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    row = dict(dati)
    row.update({"id": codice, "codice": codice, "pin": pin, "data_registrazione": now,
                "stato_firma": "Da firmare", "timestamp": now, "turno": ""})
    ok, msg = salva_append("DIPENDENTI", row, "codice", codice)
    if ok:
        st.success(f'✅ {get_testo("pdf_generato", lingua)}')
        pdf_bytes = genera_pdf_lavoratore(row)
        st.warning(get_testo("conserva_credenziali", lingua))
        c1, c2 = st.columns(2)
        c1.info(f'**{get_testo("codice_accesso", lingua)}:** {codice}')
        c2.info(f'**{get_testo("pin_accesso", lingua)}:** {pin}')
        st.download_button(label=f'📥 {get_testo("scarica", lingua)} PDF', data=pdf_bytes,
                           file_name=f"Proacier_{codice}.pdf", mime="application/pdf",
                           use_container_width=True, key="btn_dl")
        st.balloons()
        st.session_state.step = 1
        st.session_state.dati_form = {}
        st.session_state.avviso_mostrato = False
    else:
        st.error(f"Erreur: {msg}")

# ============================================================
# PAGINA CANDIDATURA (2 tendine: settore -> ruolo)
# ============================================================
def pagina_candidatura(lingua):
    idx = LINGUE.get(lingua, 0)
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.markdown("---")
    with st.form("form_candidatura"):
        c1, c2 = st.columns(2)
        with c1:
            c_cognome = st.text_input(f'{get_testo("cognome", lingua)} *')
            c_nome = st.text_input(f'{get_testo("nome", lingua)} *')
            c_email = st.text_input(f'{get_testo("email", lingua)} *')
            c_tel = st.text_input(f'{get_testo("telefono_1", lingua)} *')
            st.markdown(f'**{get_testo("data_nascita", lingua)}**')
            g, m, a = st.columns(3)
            cg = g.selectbox(get_testo("giorno", lingua), list(range(1, 32)))
            cm = m.selectbox(get_testo("mese", lingua), list(range(1, 13)))
            ca = a.selectbox(get_testo("anno", lingua), list(range(1960, 2010)), index=30)
        with c2:
            c_ind = st.text_input(get_testo("indirizzo", lingua))
            c_com = st.text_input(get_testo("comune", lingua))
            c_reg = st.selectbox(get_testo("regione_senegal", lingua), ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"])
            labels = [ar["label"][idx] for ar in AREE_AZIENDALI]
            settore = st.selectbox(get_testo("settore_richiesto", lingua), labels)
            area = AREE_AZIENDALI[labels.index(settore)]
            if area["ruoli"]:
                mansione = st.selectbox(get_testo("mansione_richiesta", lingua), area["ruoli"])
            else:
                mansione = st.text_input(get_testo("altro_specifica", lingua))
            c_studi = st.selectbox(get_testo("studi", lingua), [get_testo("opt_media", lingua), get_testo("opt_diploma", lingua), get_testo("opt_laurea", lingua), get_testo("opt_prof", lingua)])
        c_skills = st.text_area(get_testo("skills", lingua))
        c3, c4 = st.columns(2)
        c_exp = c3.number_input(get_testo("esperienza_anno", lingua), min_value=0, max_value=50, value=0)
        c_sal = c4.text_input(get_testo("salario_richiesto", lingua))
        c_note = st.text_area(get_testo("note", lingua))
        submitted = st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True)
        if submitted:
            if not c_cognome or not c_nome or not c_email or not c_tel:
                st.error(get_testo("errore_candidatura", lingua))
            else:
                row = {"id": f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}",
                       "data_candidatura": datetime.now().strftime("%d/%m/%Y %H:%M"),
                       "cognome": c_cognome, "nome": c_nome, "email": c_email, "telefono": c_tel,
                       "data_nascita": f"{cg:02d}/{cm:02d}/{ca}", "indirizzo": c_ind, "comune": c_com,
                       "regione": c_reg, "settore_richiesto": settore, "mansione_richiesta": mansione,
                       "studi": c_studi, "skills": c_skills, "esperienza_anno": int(c_exp),
                       "salario_richiesto": c_sal, "note": c_note, "stato": "Nuova"}
                ok, msg = salva_append("CANDIDATURE", row, "id", row["id"])
                if ok:
                    st.success(get_testo("candidatura_inviata", lingua))
                    st.balloons()
                else:
                    st.error(f"Erreur: {msg}")

# ============================================================
# AREA LAVORATORE
# ============================================================
def pagina_area_lavoratore(lingua):
    st.title(get_testo("i_miei_dati", lingua))
    st.success(f'{get_testo("benvenuto", lingua)} - {st.session_state.codice_operatore}')
    st.markdown("---")
    headers, records = leggi_foglio("DIPENDENTI")
    mio, mio_idx = None, -1
    for i, r in enumerate(records):
        if s_str(r.get("codice")).upper() == str(st.session_state.codice_operatore).strip().upper():
            mio, mio_idx = r, i
            break
    if mio is None:
        st.error(get_testo("nessun_risultato", lingua))
        return
    st.subheader(get_testo("sezione_dati_personali", lingua))
    c1, c2, c3 = st.columns(3)
    c1.text_input(get_testo("cognome", lingua), value=s_str(mio.get("cognome")), disabled=True)
    c1.text_input(get_testo("nome", lingua), value=s_str(mio.get("nome")), disabled=True)
    c1.text_input(get_testo("data_nascita", lingua), value=formatta_data(mio.get("data_nascita")), disabled=True)
    c2.text_input(get_testo("cni", lingua), value=s_str(mio.get("cni")), disabled=True)
    c2.text_input(get_testo("css", lingua), value=s_str(mio.get("css")), disabled=True)
    c2.text_input(get_testo("ipres", lingua), value=s_str(mio.get("ipres")), disabled=True)
    c3.text_input(get_testo("codice_accesso", lingua), value=s_str(mio.get("codice")), disabled=True)
    c3.text_input(get_testo("luogo_nascita", lingua), value=s_str(mio.get("luogo_nascita")), disabled=True)
    c3.text_input(get_testo("nazionalita", lingua), value=s_str(mio.get("nazionalita")), disabled=True)
    st.markdown("---")
    st.subheader(get_testo("sezione_paga", lingua))
    _, sal_records = leggi_foglio("SALARI")
    mia_paga = [s for s in sal_records if s_str(s.get("codice_lavoratore")).upper() == str(st.session_state.codice_operatore).strip().upper()]
    if mia_paga:
        c1, c2 = st.columns(2)
        c1.text_input(get_testo("paga_type", lingua), value=s_str(mia_paga[0].get("tipo_paga")), disabled=True)
        c2.text_input(get_testo("paga_amount", lingua), value=s_str(mia_paga[0].get("importo_base")) + " FCFA", disabled=True)
    else:
        st.info(get_testo("paga_desc", lingua))
    st.markdown("---")
    st.subheader(get_testo("sezione_contatti", lingua))
    c1, c2 = st.columns(2)
    with c1:
        n_tel1 = st.text_input(get_testo("telefono_1", lingua), value=s_str(mio.get("telefono_1")))
        n_tel2 = st.text_input(get_testo("telefono_2", lingua), value=s_str(mio.get("telefono_2")))
        n_tel3 = st.text_input(get_testo("telefono_3", lingua), value=s_str(mio.get("telefono_3")))
        n_ind = st.text_input(get_testo("indirizzo", lingua), value=s_str(mio.get("indirizzo")))
    with c2:
        n_qua = st.text_input(get_testo("quartiere", lingua), value=s_str(mio.get("quartiere")))
        n_com = st.text_input(get_testo("comune", lingua), value=s_str(mio.get("comune")))
        n_reg = st.text_input(get_testo("regione_senegal", lingua), value=s_str(mio.get("regione_senegal")))
        n_em_nome = st.text_input(get_testo("emergenza_nome", lingua), value=s_str(mio.get("emergenza_nome")))
        n_em_tel = st.text_input(get_testo("emergenza_tel", lingua), value=s_str(mio.get("emergenza_tel")))
    st.markdown("---")
    st.subheader(get_testo("sezione_famille", lingua))
    c1, c2 = st.columns(2)
    with c1:
        n_stato = st.selectbox(get_testo("stato_civile", lingua), [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)], index=max(0, [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)].index(s_str(mio.get("stato_civile"))) if s_str(mio.get("stato_civile")) in [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)] else 0))
        n_figli = st.number_input(get_testo("figli_totale", lingua), min_value=0, value=s_int(mio.get("figli_totale")))
    with c2:
        n_mogli = 0
        if n_stato == get_testo("coniugato", lingua):
            n_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=max(1, s_int(mio.get("numero_mogli"))))
    st.markdown("---")
    st.subheader(get_testo("sezione_vestiario", lingua))
    xs = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
    def safe_idx(lst, v):
        v = s_str(v)
        return lst.index(v) if v in lst else 0
    c1, c2 = st.columns(2)
    with c1:
        n_tm = st.selectbox(get_testo("taglia_maglia", lingua), xs, index=safe_idx(xs, mio.get("taglia_maglia")))
        n_tp = st.selectbox(get_testo("taglia_pantaloni", lingua), ["38", "40", "42", "44", "46", "48", "50", "52"], index=safe_idx(["38", "40", "42", "44", "46", "48", "50", "52"], mio.get("taglia_pantaloni")))
        n_ts = st.selectbox(get_testo("taglia_scarpe", lingua), [str(x) for x in range(38, 48)], index=safe_idx([str(x) for x in range(38, 48)], mio.get("taglia_scarpe")))
    with c2:
        n_tg = st.selectbox(get_testo("taglia_giacca", lingua), xs[:-1], index=safe_idx(xs[:-1], mio.get("taglia_giacca")))
        n_tc = st.selectbox(get_testo("taglia_cappello", lingua), ["S", "M", "L", "XL"], index=safe_idx(["S", "M", "L", "XL"], mio.get("taglia_cappello")))
        n_tgu = st.selectbox(get_testo("taglia_guanti", lingua), ["S", "M", "L", "XL"], index=safe_idx(["S", "M", "L", "XL"], mio.get("taglia_guanti")))
    st.markdown("---")
    st.info(get_testo("sezione_comunicazioni", lingua))
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(get_testo("salva_modifiche", lingua), type="primary", use_container_width=True):
            upd = {"telefono_1": n_tel1, "telefono_2": n_tel2, "telefono_3": n_tel3,
                   "indirizzo": n_ind, "quartiere": n_qua, "comune": n_com, "regione_senegal": n_reg,
                   "emergenza_nome": n_em_nome, "emergenza_tel": n_em_tel, "stato_civile": n_stato,
                   "figli_totale": int(n_figli), "numero_mogli": int(n_mogli),
                   "taglia_maglia": n_tm, "taglia_pantaloni": n_tp, "taglia_scarpe": n_ts,
                   "taglia_giacca": n_tg, "taglia_cappello": n_tc, "taglia_guanti": n_tgu}
            ok, msg = salva_update("DIPENDENTI", mio_idx, upd)
            if ok:
                st.success(get_testo("modifiche_salvate", lingua))
                st.rerun()
            else:
                st.error(f"{get_testo('errore_salvataggio', lingua)} ({msg})")
    with c2:
        pdf_bytes = genera_pdf_lavoratore(mio)
        st.download_button(label=get_testo("ristampa_pdf", lingua), data=pdf_bytes,
                           file_name=f"Proacier_{mio.get('codice')}.pdf", mime="application/pdf",
                           use_container_width=True)
    st.markdown("---")
    if st.button(get_testo("logout", lingua), use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.pagina = "home"
        st.rerun()

# ============================================================
# MAIN
# ============================================================
def main():
    for k, v in {"lingua": "fr", "pagina": "home", "logged_in": False, "user_type": None,
                 "step": 1, "dati_form": {}, "codice_operatore": None, "avviso_mostrato": False}.items():
        if k not in st.session_state:
            st.session_state[k] = v
    lingua = st.session_state.lingua
    with st.sidebar:
        st.image(CONFIG["logo_url"], use_container_width=True)
        st.markdown("---")
        st.title(get_testo("titolo", lingua))
        st.markdown(get_testo("sottotitolo", lingua))
        st.markdown("---")
        sel = st.selectbox(get_testo("lingua", lingua), ["Français", "Italiano", "English"],
                           index={"fr": 0, "it": 1, "en": 2}[lingua])
        nuova = {"Français": "fr", "Italiano": "it", "English": "en"}[sel]
        if nuova != lingua:
            st.session_state.lingua = nuova
            st.rerun()
        lingua = st.session_state.lingua
        st.markdown("---")
        if st.session_state.logged_in:
            st.success(f'{get_testo("benvenuto", lingua)}')
            if st.session_state.user_type == "admin" and st.button(get_testo("dashboard", lingua), key="sb_dash"):
                st.session_state.pagina = "dashboard"
            if st.session_state.user_type == "lavoratore" and st.button(get_testo("i_miei_dati", lingua), key="sb_miei"):
                st.session_state.pagina = "area_lavoratore"
            if st.button(get_testo("logout", lingua), key="sb_out"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.pagina = "home"
                st.rerun()
        else:
            if st.button(get_testo("candidatura_spontanea", lingua), key="sb_cand"):
                st.session_state.pagina = "candidatura"
                st.rerun()
            if st.button(get_testo("area_lavoratore", lingua), key="sb_area"):
                st.session_state.pagina = "espace"
                st.rerun()
            if st.button(get_testo("dashboard", lingua), key="sb_admin"):
                st.session_state.pagina = "login_admin"
                st.rerun()

    if st.session_state.pagina == "home":
        st.title(get_testo("titolo", lingua))
        st.subheader(get_testo("sottotitolo", lingua))
        st.markdown("---")
        st.subheader(get_testo("home_titolo", lingua))
        c1, c2 = st.columns(2)
        c1.markdown(f'**{get_testo("home_p1_t", lingua)}**\n- {get_testo("home_p1_d", lingua)}')
        c1.markdown(f'**{get_testo("home_p2_t", lingua)}**\n- {get_testo("home_p2_d", lingua)}')
        c2.markdown(f'**{get_testo("home_p3_t", lingua)}**\n- {get_testo("home_p3_d", lingua)}')
        c2.markdown(f'**{get_testo("home_p4_t", lingua)}**\n- {get_testo("home_p4_d", lingua)}')
        st.markdown("---")
        st.subheader(get_testo("home_navigation", lingua))
        c1, c2, c3 = st.columns(3)
        if c1.button(get_testo("candidatura_spontanea", lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = "candidatura"
            st.rerun()
        if c2.button(get_testo("area_lavoratore", lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = "espace"
            st.rerun()
        if c3.button(get_testo("dashboard", lingua), use_container_width=True):
            st.session_state.pagina = "login_admin"
            st.rerun()

    elif st.session_state.pagina == "espace":
        st.title(get_testo("area_lavoratore", lingua))
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.markdown(f'### 👤 {get_testo("giornalieri_titolo", lingua)}')
        c1.info(get_testo("giornalieri_desc", lingua))
        if c1.button(get_testo("login_btn", lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = "login_lavoratore"
            st.rerun()
        c2.markdown(f'### 📝 {get_testo("nuovo_giornaliero_titolo", lingua)}')
        c2.info(get_testo("nuovo_giornaliero_desc", lingua))
        if c2.button(get_testo("trasmissione_btn", lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = "registrazione"
            st.session_state.step = 1
            st.session_state.dati_form = {}
            st.session_state.avviso_mostrato = False
            st.rerun()

    elif st.session_state.pagina == "registrazione":
        pagina_registrazione(lingua)
    elif st.session_state.pagina == "candidatura":
        pagina_candidatura(lingua)
    elif st.session_state.pagina == "area_lavoratore":
        pagina_area_lavoratore(lingua)

    elif st.session_state.pagina == "login_lavoratore":
        codice = st.text_input(get_testo("codice", lingua), key="lg_cod")
        pin = st.text_input(get_testo("pin", lingua), type="password", key="lg_pin")
        if st.button(get_testo("accedi", lingua), type="primary", key="lg_btn"):
            _, records = leggi_foglio("DIPENDENTI")
            ok = any(s_str(r.get("codice")).upper() == codice.strip().upper() and s_str(r.get("pin")) == pin.strip() for r in records)
            if ok:
                st.session_state.logged_in = True
                st.session_state.user_type = "lavoratore"
                st.session_state.codice_operatore = codice.strip()
                st.session_state.pagina = "area_lavoratore"
                st.rerun()
            else:
                st.error(get_testo("codice_errato", lingua))

    elif st.session_state.pagina == "login_admin":
        pwd = st.text_input(get_testo("password", lingua), type="password", key="lg_pwd")
        if st.button(get_testo("accedi", lingua), type="primary", key="lg_adm"):
            if pwd == CONFIG["password_admin"]:
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                st.session_state.pagina = "dashboard"
                st.rerun()
            else:
                st.error(get_testo("codice_errato", lingua))

    elif st.session_state.pagina == "dashboard":
        st.title(get_testo("dashboard", lingua))
        _, records = leggi_foglio("DIPENDENTI")
        if records:
            st.metric(get_testo("totale_operai", lingua), len(records))
            st.dataframe([{get_testo("codice", lingua): r.get("codice"), get_testo("cognome", lingua): r.get("cognome"), get_testo("nome", lingua): r.get("nome"), "Turno": r.get("turno")} for r in records], use_container_width=True)
            st.info("🚧 Pagina 1 (dettagli + salari) e Pagina 2 (presenze + paghe) in arrivo: FASI 5-6")
        else:
            st.warning(get_testo("nessun_risultato", lingua))

if __name__ == "__main__":
    main()
