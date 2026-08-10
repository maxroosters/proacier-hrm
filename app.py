# -*- coding: utf-8 -*-
"""
PROACIER HRM - v20.20 - FILE COMPLETO
✅ v20.20: layout compatto — bandierine grandi in alto, sidebar e area principale
   compattate via CSS (la home entra nello schermo, tasti non più fuori pagina)
✅ Include tutto v20.19: bandierine lingua, bottoni uniformi, salva-tutto admin,
   ambiente test/produzione, ricordami admin, bacheca AVVISI+Telegram, festività
Richiede: Apps Script v6.1 + fase6_paghe.py F6.7 + foglio AVVISI + chiavi CONFIG.
"""
import sys
import importlib
import streamlit as st
import requests
import random
import re
from datetime import datetime, timedelta, date
from fpdf import FPDF
import fase6_paghe
importlib.reload(fase6_paghe)  # codice FASE 6 sempre fresco

VERSIONE = "v20.20"

# ============================================================
# CONFIGURAZIONE CENTRALE
# ============================================================
CONFIG = {
    "url_api_produzione": "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec",
    "url_api_test": "https://script.google.com/macros/s/AKfycbyUwzt7l_b-K7xsGX2mz1E9lPMRUZ7XptpMU8Z_4c_X-AsHd4X8haEXqlYId0buIw/exec",
    "email_ouvriers": "ouvriers@proacier.sn",
    "email_candidature": "candidature@proacier.sn",
    "prefisso_codice": "THS",
    "user_admin": "admin",
    "password_admin": "admin123",
    "logo_url": "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png",
    "base_url": "https://hrm.proacier.sn",
}

st.set_page_config(page_title="Proacier - Ressources Humaines", page_icon="🏭",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
[data-testid="stSidebar"]{background-color:#5EA529 !important;}
[data-testid="stSidebar"] *{color:white !important;}
[data-testid="stSidebar"] button{background-color:rgba(255,255,255,0.1)!important;color:white!important;padding:0.35rem 0.5rem !important;min-height:2.1rem !important;}
[data-testid="stSidebar"] select{color:white!important;background-color:rgba(0,0,0,0.3)!important;}
[data-testid="stSidebar"] option{color:black!important;}
[data-testid="stSidebar"] .element-container{margin-bottom:0.25rem !important;}
[data-testid="stSidebar"] h1{font-size:1.25rem !important;margin:0.15rem 0 !important;}
[data-testid="stSidebar"] hr{margin:0.4rem 0 !important;}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type button{font-size:1.7rem !important;line-height:1.1 !important;padding:0.1rem 0 !important;min-height:2.6rem !important;}
[data-testid="stMainBlockContainer"]{padding-top:1.1rem !important;padding-bottom:0.5rem !important;}
[data-testid="stMain"] h1{font-size:1.9rem !important;margin:0.2rem 0 0.5rem 0 !important;}
[data-testid="stMain"] h2{font-size:1.35rem !important;margin:0.5rem 0 0.3rem 0 !important;}
[data-testid="stMain"] h3{font-size:1.05rem !important;margin:0.3rem 0 !important;}
[data-testid="stMain"] hr{margin:0.5rem 0 !important;}
[data-testid="stMain"] .stMarkdown p{margin-bottom:0.35rem !important;}
@media (max-width:768px){.stTextInput>div>div>input,.stSelectbox>div>div>select{font-size:16px;}}
.phone-box{background-color:#5EA529;border-radius:10px;padding:10px 14px;margin:8px 0;color:white;}
.phone-box h4{margin:0 0 6px 0;color:white;font-size:15px;}
.phone-box .stTextInput>div>div>input{background-color:white;color:black;}
.phone-box .stCheckbox label{color:white;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# TRADUZIONI (fr, it, en)
# ============================================================
LINGUE = {"fr": 0, "it": 1, "en": 2}
T = {
    "titolo": ("🏭 PROACIER - GESTION DES RESSOURCES HUMAINES", "🏭 PROACIER - GESTIONE RISORSE UMANE", "🏭 PROACIER - HUMAN RESOURCES"),
    "sottotitolo": ("Système de Recrutement - Sénégal", "Sistema di Reclutamento - Senegal", "Recruitment System - Senegal"),
    "lingua": ("Langue", "Lingua", "Language"),
    "home": ("🏠 Accueil", "🏠 Home", "🏠 Home"),
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
    "fest_box_titolo": ("🗓️ Prochains jours fériés", "🗓️ Prossime festività", "🗓️ Upcoming public holidays"),
    "fest_tra": ("dans {n} jours", "tra {n} giorni", "in {n} days"),
    "fest_oggi": ("aujourd'hui", "oggi", "today"),
    "fest_stop": ("🏭 Prévoir l'arrêt des lignes ou l'organisation du travail.", "🏭 Prevedere la fermata delle linee o l'organizzazione del lavoro.", "🏭 Plan line stoppage or work organization."),
    "amb_title": ("🧪 Environnement de travail", "🧪 Ambiente di lavoro", "🧪 Work environment"),
    "amb_hint": ("« test » écrit UNIQUEMENT dans Proacier_SANDBOX_HRM. Par défaut: production.",
                 "« test » scrive SOLO su Proacier_SANDBOX_HRM. Default: produzione.",
                 "« test » writes ONLY to Proacier_SANDBOX_HRM. Default: production."),
    "admin_user": ("Nom d'utilisateur", "Nome utente", "Username"),
    "bacheca_title": ("📢 Tableau d'affichage de la direction", "📢 Bacheca della direzione", "📢 Management notice board"),
    "avviso_new": ("📢 Nouveau avis", "📢 Nuovo avviso", "📢 New notice"),
    "avviso_titolo": ("Titre (facultatif)", "Titolo (facoltativo)", "Title (optional)"),
    "avviso_testo": ("Texte de l'avis", "Testo dell'avviso", "Notice text"),
    "avviso_urgente": ("⚠️ Urgent (mis en évidence)", "⚠️ Urgente (evidenziato)", "⚠️ Urgent (highlighted)"),
    "avviso_pubblica": ("Publier l'avis", "Pubblica avviso", "Publish notice"),
    "avviso_ok": ("✅ Avis publié", "✅ Avviso pubblicato", "✅ Notice published"),
    "avviso_tel_ok": ("+ envoyé sur Telegram ✅", "+ inviato su Telegram ✅", "+ sent to Telegram ✅"),
    "avviso_tel_no": ("(Telegram non configuré: clés CONFIG manquantes)", "(Telegram non configurato: chiavi CONFIG mancanti)", "(Telegram not configured: missing CONFIG keys)"),
    "avviso_vuoto": ("⚠️ Écris au moins le texte de l'avis", "⚠️ Scrivi almeno il testo dell'avviso", "⚠️ Write at least the notice text"),
    "avvisi_ultimi": ("Derniers avis", "Ultimi avvisi", "Latest notices"),
    "tg_obbligo": ("📲 Telegram est OBLIGATOIRE pour recevoir les avis de la direction.",
                   "📲 Telegram è OBBLIGATORIO per ricevere gli avvisi della direzione.",
                   "📲 Telegram is MANDATORY to receive management notices."),
    "tg_install": ("1️⃣ Installer Telegram", "1️⃣ Installa Telegram", "1️⃣ Install Telegram"),
    "tg_join": ("2️⃣ Entrer dans le canal de l'entreprise", "2️⃣ Entra nel canale aziendale", "2️⃣ Join the company channel"),
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
    "ricordami": ("🔖 Mémoriser mon accès dans le lien de la page", "🔖 Salva il mio accesso nel link della pagina", "🔖 Save my access in the page link"),
    "link_hint": ("🔖 L'adresse de cette page contient maintenant ton accès: mets-la en favori ou garde-la (ex. WhatsApp). En la rouvrant, tu entreras directement.",
                  "🔖 L'indirizzo di questa pagina ora contiene il tuo accesso: salvalo nei preferiti o conservalo (es. WhatsApp). Riaprendolo, entrerai direttamente.",
                  "🔖 This page's address now contains your access: bookmark it or keep it (e.g. WhatsApp). Reopening it, you will enter directly."),
    "copia_link_help": ("Copie ce lien et garde-le précieusement :", "Copia questo link e conservalo con cura:", "Copy this link and keep it safe:"),
    "salva_link": ("🔖 Lien personnel", "🔖 Link personale", "🔖 Personal link"),
    "salva_tutto": ("💾 Enregistrer toutes les modifications", "💾 Salva tutte le modifiche", "💾 Save all changes"),
    "salvate_n": ("ligne(s) mise(s) à jour :", "riga/e aggiornata/e:", "row(s) updated:"),
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
    "checkbox_confirm": ("J'ai lu et j'accepte les conditions générales et la politique de confidentialité",
                         "Ho letto e accetto le condizioni generali e la politica sulla privacy",
                         "I have read and accept the general conditions and privacy policy"),
    "cocher_case": ("Veuillez cocher la case de confirmation", "Seleziona la casella di conferma", "Please check the confirmation box"),
    "errore_obbligatori": ("Veuillez remplir tous les champs obligatoires (*)", "Compila tutti i campi obbligatori (*)", "Please fill in all required fields (*)"),
    "avviso_non_contratto": ("⚠️ Ceci n'est PAS un contrat d'embauche. Uniquement une transmission de données à l'administration.",
                             "⚠️ Questo NON è un contratto di assunzione. Solo una trasmissione di dati all'amministrazione.",
                             "⚠️ This is NOT an employment contract. Only a data transmission to the administration."),
    "avviso_regole_aziendali": ("📋 En soumettant ce formulaire, vous acceptez les règles de l'entreprise et la politique de confidentialité de PROACIER.",
                                "📋 Inviando questo modulo, accetti le regole aziendali e la politica sulla privacy di PROACIER.",
                                "📋 By submitting this form, you accept the company rules and PROACIER's privacy policy."),
    "nuova_registrazione": ("🆕 Nouvelle inscription", "🆕 Nuova registrazione", "🆕 New registration"),
    "nouvelle_candidature": ("🆕 Nouvelle candidature", "🆕 Nuova candidatura", "🆕 New application"),
    "candidatura_gia_inviata": ("ℹ️ Candidature déjà envoyée avec ces coordonnées.", "ℹ️ Candidatura già inviata con questi dati.", "ℹ️ Application already submitted with these details."),
    "reg_gia": ("ℹ️ Travailleur déjà enregistré aujourd'hui avec ces données. Voici ses identifiants.",
                "ℹ️ Lavoratore già registrato oggi con questi dati. Ecco le sue credenziali.",
                "ℹ️ Worker already registered today with these details. Here are the credentials."),
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
    "stato_civile": ("État civil", "Stato civile", "Marital status"),
    "numero_mogli": ("Nombre d'épouses", "Numero di mogli", "Number of wives"),
    "figli_totale": ("Nombre total d'enfants", "Numero totale di figli", "Total number of children"),
    "somma_mogli": ("Somme des enfants des épouses", "Somma figli dichiarati per moglie", "Sum of children declared per wife"),
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
    "data_visita": ("Date visite", "Data visita", "Visit date"),
    "emergenza_nome": ("Contact urgence (Nom)", "Contatto emergenza (Nome)", "Emergency contact (Name)"),
    "emergenza_parentela": ("Lien", "Parentela", "Relationship"),
    "emergenza_tel": ("Tél urgence", "Tel emergenza", "Emergency phone"),
    "emergenza_indirizzo": ("Adresse urgence", "Indirizzo emergenza", "Emergency address"),
    "titolo_vestiario": ("Tailles Vêtements & EPI", "Taglie Abbigliamento e DPI", "Clothing & PPE Sizes"),
    "taglia_maglia": ("Taille t-shirt/polo", "Taglia t-shirt/polo", "T-shirt/polo size"),
    "taglia_pantaloni": ("Taille pantalon", "Taglia pantalone", "Pants size"),
    "taglia_scarpe": ("Pointure chaussures", "Numero scarpe", "Shoe size"),
    "taglia_giacca": ("Taille veste/gilet", "Taglia giacca/gilet", "Jacket/vest size"),
    "taglia_cappello": ("Taille casque/casquette", "Taglia casco/cappellino", "Helmet/cap size"),
    "taglia_guanti": ("Taille gants", "Taglia guanti", "Gloves size"),
    "titolo_candidatura": ("CANDIDATURE SPONTANÉE", "CANDIDATURA SPONTANEA", "SPONTANEOUS APPLICATION"),
    "sottotitolo_candidatura": ("Rejoignez l'équipe PROACIER.", "Unisciti al team PROACIER.", "Join the PROACIER team."),
    "email": ("Adresse Email", "Indirizzo Email", "Email Address"),
    "settore_richiesto": ("Secteur d'intérêt", "Settore di interesse", "Area of interest"),
    "mansione_richiesta": ("Poste recherché", "Ruolo richiesto", "Desired position"),
    "altro_specifica": ("Précisez le rôle souhaité", "Specifica il ruolo desiderato", "Specify the desired role"),
    "studi": ("Niveau d'études", "Titolo di studio", "Education level"),
    "hint_prof": ("💡 Précisez votre formation (métier appris, certificat...) dans les notes supplémentaires.",
                  "💡 Specifica la tua formazione (mestiere imparato, certificato...) nelle note aggiuntive.",
                  "💡 Please specify your training (trade learned, certificate...) in the additional notes."),
    "skills": ("Compétences / Skills", "Competenze / Skills", "Skills / Competencies"),
    "esperienza_anno": ("Années d'expérience", "Anni di esperienza", "Years of experience"),
    "salario_richiesto": ("Prétention salariale (FCFA)", "Retribuzione richiesta (FCFA)", "Expected salary (FCFA)"),
    "note": ("Notes supplémentaires", "Note aggiuntive", "Additional notes"),
    "invia_candidatura": ("📤 Envoyer ma candidature", "📤 Invia la mia candidatura", "📤 Submit my application"),
    "candidatura_inviata": ("✅ Candidature envoyée avec succès!", "✅ Candidatura inviata con successo!", "✅ Application submitted successfully!"),
    "errore_candidatura": ("Veuillez remplir Nom, Prénom, Email et Téléphone.", "Compila Cognome, Nome, Email e Telefono.", "Please fill in Surname, First Name, Email, and Phone."),
    "sezione_dati_personali": ("📋 Données Personnelles (non modifiables)", "📋 Dati Personali (non modificabili)", "📋 Personal Data (non-modifiable)"),
    "sezione_medica": ("Informations Médicales (non modifiables)", "Informazioni Mediche (non modificabili)", "Medical Information (non-modifiable)"),
    "sezione_paga": ("💰 Informations Salariales", "💰 Informazioni Salariali", "💰 Salary Information"),
    "sezione_contatti": ("📞 Coordonnées (modifiables)", "📞 Contatti (modificabili)", "📞 Contact Info (modifiable)"),
    "sezione_famille": ("👨‍‍👦 Famille (modifiable)", "👨‍‍👧‍ Famiglia (modificabile)", "👨‍‍👦 Family (modifiable)"),
    "sezione_vestiario": ("👕 Vêtements & EPI (modifiables)", "👕 Vestiario e DPI (modificabili)", "👕 Clothing & PPE (modifiable)"),
    "sezione_comunicazioni": ("💬 Communications & Demandes (bientôt disponible)", "💬 Comunicazioni e Richieste (prossimamente)", "💬 Communications & Requests (coming soon)"),
    "paga_desc": ("Votre salaire est géré par l'administration.", "Il tuo salario è gestito dall'amministrazione.", "Your salary is managed by administration."),
    "paga_type": ("Type de paiement", "Tipo di pagamento", "Payment type"),
    "paga_amount": ("Montant", "Importo", "Amount"),
    "salva_modifiche": ("💾 Enregistrer les modifications", "💾 Salva modifiche", "💾 Save changes"),
    "modifiche_salvate": ("✅ Modifications enregistrées avec succès!", "✅ Modifiche salvate con successo!", "✅ Changes saved successfully!"),
    "errore_salvataggio": ("❌ Erreur lors de l'enregistrement.", "❌ Errore durante il salvataggio.", "❌ Error saving."),
    "saving": ("Enregistrement en cours...", "Salvataggio in corso...", "Saving..."),
    "cerca_dip": ("🔍 Rechercher (code, nom, prénom)", "🔍 Cerca (codice, cognome, nome)", "🔍 Search (code, surname, name)"),
    "turno": ("Turno", "Turno", "Shift"),
    "globale": ("Global (switch CONFIG)", "Globale (switch CONFIG)", "Global (CONFIG switch)"),
    "turni_assegnati": ("Postes attribués", "Turni assegnati", "Assigned shifts"),
    "salari_attivi": ("Salaires actifs", "Salari attivi", "Active salaries"),
    "dash_p1": ("1 - Employés & Salaires", "1 - Dipendenti & Salari", "1 - Employees & Salaries"),
    "dash_p2": ("2 - Présences & Paies", "2 - Presenze & Paghe", "2 - Attendance & Payroll"),
    "sez_admin": ("🛠️ Gestion administrative", "🛠️ Gestione amministrativa", "🛠️ Administrative management"),
    "storico_visite": ("Historique des visites médicales", "Storico visite mediche", "Medical visit history"),
    "nuova_visita": ("Nouvelle visite médicale", "Nuova visita medica", "New medical visit"),
    "tipo_visita": ("Type de visite", "Tipo di visita", "Visit type"),
    "esito": ("Résultat médical", "Esito medico", "Medical outcome"),
    "restrizioni": ("Restrictions", "Restrizioni", "Restrictions"),
    "prossimo_controllo": ("Prochain contrôle", "Prossimo controllo", "Next check"),
    "nessuna_visita": ("Aucune visite enregistrée", "Nessuna visita registrata", "No visits recorded"),
    "visite_scadute": ("Visites médicales à renouveler (≤30 jours ou scadute)", "Visite mediche da rinnovare (≤30 giorni o scadute)", "Medical visits to renew (≤30 days or expired)"),
    "idoneita_parziale": ("Aptitude avec restriction / inaptitude", "Idoneità con restrizione o inidoneità", "Restricted fitness / unfitness"),
    "promemoria_visita": ("⚠️ Prochain contrôle médical le ", "⚠️ Prossimo controllo medico il ", "⚠️ Next medical check on "),
    "form_hint": ("ℹ️ Modifiez ce que vous voulez, puis cliquez UNE fois sur « Enregistrer toutes les modifications » en bas de liste.",
                  "ℹ️ Modifica ciò che vuoi, poi clicca UNA volta su « Salva tutte le modifiche » in fondo alla lista.",
                  "ℹ️ Edit what you need, then click “Save all changes” once at the bottom of the list."),
    "mogli_hint": ("Après modification du nombre d'épouses, enregistrez pour afficher les champs des nouvelles épouses.",
                   "Dopo aver cambiato il numero di mogli, salva per visualizzare i campi delle nuove mogli.",
                   "After changing the number of wives, save to display the fields of the new wives."),
    "mostra_altri": ("➕ Afficher 15 de plus", "➕ Mostrane altri 15", "➕ Show 15 more"),
    "pdf_titolo": ("FICHE D'ENREGISTREMENT - RESSOURCES HUMAINES", "SCHEDA DI REGISTRAZIONE - RISORSE UMANE", "REGISTRATION FORM - HUMAN RESOURCES"),
    "pdf_nfiche": ("N° fiche: ", "N° scheda: ", "File No.: "),
    "pdf_data": ("Date: ", "Data: ", "Date: "),
    "pdf_sez1": ("1. IDENTITE & FAMILLE", "1. IDENTITA' E FAMIGLIA", "1. IDENTITY & FAMILY"),
    "pdf_nom": ("Nom: ", "Cognome: ", "Surname: "),
    "pdf_prenoms": ("Prenom(s): ", "Nome: ", "First name(s): "),
    "pdf_ne_le": ("Ne(e) le: ", "Nato/a il: ", "Born on: "),
    "pdf_a": ("a: ", "a: ", "at: "),
    "pdf_nationalite": ("Nationalite: ", "Nazionalita': ", "Nationality: "),
    "pdf_pays": ("Pays: ", "Paese: ", "Country: "),
    "pdf_etat_civil": ("Etat civil: ", "Stato civile: ", "Marital status: "),
    "pdf_enfants": ("Enfants: ", "Figli: ", "Children: "),
    "pdf_epouses": ("Epouses: ", "Mogli: ", "Wives: "),
    "pdf_sez2": ("2. CONTACT & DOCUMENTS", "2. CONTATTI E DOCUMENTI", "2. CONTACT & DOCUMENTS"),
    "pdf_adresse": ("Adresse: ", "Indirizzo: ", "Address: "),
    "pdf_tel1": ("Tel 1: ", "Tel 1: ", "Phone 1: "),
    "pdf_tel2": ("Tel 2: ", "Tel 2: ", "Phone 2: "),
    "pdf_sez3": ("3. EXPERIENCE & COMPETENCES", "3. ESPERIENZA E COMPETENZE", "3. EXPERIENCE & SKILLS"),
    "pdf_poste": ("Poste: ", "Mansione: ", "Position: "),
    "pdf_competence": ("Competence: ", "Competenza: ", "Skill: "),
    "pdf_permis": ("Permis: ", "Patente: ", "License: "),
    "pdf_sez4": ("4. VETEMENTS & EPI", "4. ABBIGLIAMENTO E DPI", "4. CLOTHING & PPE"),
    "pdf_tshirt": ("T-shirt: ", "T-shirt: ", "T-shirt: "),
    "pdf_pantalon": ("Pantalon: ", "Pantalone: ", "Pants: "),
    "pdf_pointure": ("Pointure: ", "Numero scarpe: ", "Shoe size: "),
    "pdf_gilet": ("Gilet: ", "Gilet: ", "Vest: "),
    "pdf_casque": ("Casque: ", "Casco: ", "Helmet: "),
    "pdf_gants": ("Gants: ", "Guanti: ", "Gloves: "),
    "pdf_sez5": ("5. MEDICAL & URGENCE", "5. MEDICO E EMERGENZA", "5. MEDICAL & EMERGENCY"),
    "pdf_groupe": ("Groupe: ", "Gruppo: ", "Blood type: "),
    "pdf_aptitude": ("Aptitude: ", "Idoneita': ", "Fitness: "),
    "pdf_urgence": ("Urgence: ", "Emergenza: ", "Emergency: "),
    "pdf_tel": ("Tel: ", "Tel: ", "Phone: "),
    "pdf_certifie": ("Je certifie l'exactitude des informations et accepte les conditions.",
                     "Certifico l'esattezza delle informazioni e accetto le condizioni.",
                     "I certify the accuracy of the information and accept the conditions."),
    "pdf_candidat": ("CANDIDAT", "CANDIDATO", "CANDIDATE"),
    "pdf_employeur": ("EMPLOYEUR", "DATORE DI LAVORO", "EMPLOYER"),
    "pdf_consent_titolo": ("CONSENTEMENT DONNEES PERSONNELLES", "CONSENSO DATI PERSONALI", "PERSONAL DATA CONSENT"),
    "pdf_consent_testo": ("Conformement a la Loi n° 2008-12 du 25 janvier 2008 (Senegal).",
                          "Conforme alla Legge n° 2008-12 del 25 gennaio 2008 (Senegal).",
                          "In accordance with Law No. 2008-12 of 25 January 2008 (Senegal)."),
    "pdf_signature": ("Signature: ", "Firma: ", "Signature: "),
    "pdf_id_titolo": ("IDENTIFIANTS DE CONNEXION", "CREDENZIALI DI ACCESSO", "LOGIN CREDENTIALS"),
    "pdf_id_desc": ("Conservez precieusement ces identifiants: ", "Conserva con cura queste credenziali: ", "Keep these credentials safe: "),
    "pdf_id_code": ("Code d'acces: ", "Codice di accesso: ", "Access code: "),
    "pdf_id_avviso": ("Ces identifiants sont personnels et confidentiels. Ne les partagez avec personne.",
                      "Queste credenziali sono personali e riservate. Non condividerle con nessuno.",
                      "These credentials are personal and confidential. Do not share them with anyone."),
}


def get_testo(chiave, lingua="fr"):
    t = T.get(chiave)
    if not t:
        return chiave
    return t[LINGUE.get(lingua, 0)]


# ============================================================
# OPZIONI CANONICHE
# ============================================================
OPZ = {
    "sesso": [("M", "Masculin", "Maschile", "Male"), ("F", "Féminin", "Femminile", "Female")],
    "stato_civile": [("celibe", "Célibataire", "Celibe/Nubile", "Single"), ("coniugato", "Marié(e)", "Coniugato/a", "Married"),
                     ("divorziato", "Divorcé(e)", "Divorziato/a", "Divorced"), ("vedovo", "Veuf/Veuve", "Vedovo/a", "Widowed")],
    "idoneita": [("apte", "Apte", "Apto", "Fit"), ("restriction", "Apte avec restriction", "Apto con restrizioni", "Fit with restrictions"),
                 ("inapte", "Inapte", "Inapto", "Unfit")],
    "categoria": [("edilizia", "Bâtiment", "Edilizia", "Construction"), ("contabilita", "Comptabilité", "Contabilità", "Accounting"),
                  ("meccanica", "Mécanique", "Meccanica", "Mechanics"), ("elettrico", "Électricité", "Elettrico", "Electrical"),
                  ("agricoltura", "Agriculture", "Agricoltura", "Agriculture"), ("altro_cat", "Autre", "Altro", "Other")],
    "studi": [("media", "École moyenne", "Licenza media", "Middle school"), ("diploma", "Baccalauréat / Diplôme", "Diploma", "High school / Diploma"),
              ("laurea", "Université / Licence", "Laurea", "University / Degree"), ("prof", "Formation professionnelle", "Formazione professionale", "Vocational training")],
    "paesi": [("SN", "Sénégal", "Senegal", "Senegal"), ("ML", "Mali", "Mali", "Mali"), ("BF", "Burkina Faso", "Burkina Faso", "Burkina Faso"),
              ("SL", "Sierra Leone", "Sierra Leone", "Sierra Leone"), ("GN", "Guinée", "Guinea", "Guinea"),
              ("GM", "Gambie", "Gambia", "Gambia"), ("AUTRE", "Autre pays", "Altro paese", "Other country")],
    "tipo_visita": [("assunzione", "Visite d'embauche", "Visita di assunzione", "Hiring visit"),
                    ("periodica", "Visite périodique", "Visita periodica", "Periodic visit"),
                    ("straordinaria", "Visite extraordinaire", "Visita straordinaria", "Extraordinary visit")],
    "tipo_paga": [("giornaliero", "Journalier", "Giornaliero", "Daily"), ("orario", "Horaire", "Orario", "Hourly"),
                  ("mensile", "Mensuel", "Mensile", "Monthly")],
}


def etichetta(tipo, valore, lingua="fr"):
    v = s_str(valore)
    if not v:
        return ""
    for o in OPZ.get(tipo, []):
        if v in o:
            return o[LINGUE.get(lingua, 0) + 1]
    return v


def select_canonico(tipo, lingua, label, key, saved=None):
    codes = [o[0] for o in OPZ[tipo]]
    idx = 0
    sv = s_str(saved)
    if sv:
        if sv in codes:
            idx = codes.index(sv)
        else:
            for o in OPZ[tipo]:
                if sv in o[1:]:
                    idx = codes.index(o[0])
                    break
    return st.selectbox(label, codes, index=idx, format_func=lambda c: etichetta(tipo, c, lingua), key=key)


def norm_idoneita(v):
    v = s_str(v)
    if v in ("apte", "Apte", "Apto", "Fit"):
        return "apte"
    if v in ("restriction", "Apte avec restriction", "Apto con restrizioni", "Fit with restrictions"):
        return "restriction"
    if v in ("inapte", "Inapte", "Inapto", "Unfit"):
        return "inapte"
    return v


def data_ord(s):
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s_str(s))
    if not m:
        return None
    d, mo, y = map(int, m.groups())
    return (y, mo, d)


# ============================================================
# AREE AZIENDALI
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
# HELPERS DATI
# ============================================================
def genera_credenziali():
    anno = datetime.now().year
    prefisso = CONFIG["prefisso_codice"]
    _, recs = leggi_foglio("DIPENDENTI", force=True)
    pattern = re.compile(r"^" + re.escape(prefisso) + r"-\d{4}-(\d+)$", re.I)
    max_seq = 0
    codici_esistenti = set()
    pins_esistenti = set()
    for r in recs:
        cod = s_str(r.get("codice")).upper()
        if cod:
            codici_esistenti.add(cod)
            m = pattern.match(cod)
            if m:
                max_seq = max(max_seq, int(m.group(1)))
        p = s_str(r.get("pin"))
        if p:
            pins_esistenti.add(p)
    seq = max_seq + 1
    codice = f"{prefisso}-{anno}-{seq:04d}"
    while codice.upper() in codici_esistenti:
        seq += 1
        codice = f"{prefisso}-{anno}-{seq:04d}"
    pin = str(random.randint(1000, 9999))
    while pin in pins_esistenti:
        pin = str(random.randint(1000, 9999))
    return codice, pin


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


def parse_mogli(s):
    out = []
    s = s_str(s)
    if not s:
        return out
    chunks = [c.strip() for c in s.split("|") if c.strip()]
    for c in chunks:
        m = re.search(r"(\d+)\s*enfants?", c)
        fig = int(m.group(1)) if m else 0
        res = re.sub(r"^Épouse\s*\d+\s*:\s*", "", c)
        res = re.sub(r"\s*\(\d+\s*enfants?\)\s*$", "", res).strip()
        out.append({"res": res, "fig": fig})
    return out


# ============================================================
# RETE: POST unificato + CACHE
# ============================================================
def _post_json(payload):
    try:
        r = requests.post(CONFIG["url_api"], json=payload, timeout=90)
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


def _svuota_cache(nome_foglio=None):
    cache = st.session_state.get("_cache", {})
    if nome_foglio:
        cache.pop(nome_foglio, None)
    cache.pop("_admin", None)
    st.session_state["_cache"] = cache


def leggi_foglio(nome_foglio, force=False):
    cache = st.session_state.get("_cache", {})
    if not force and nome_foglio in cache:
        ts, h, recs = cache[nome_foglio]
        if (datetime.now() - ts).total_seconds() < 30:
            return h, recs
    data = None
    try:
        r = requests.post(CONFIG["url_api"], json={"sheet": nome_foglio, "action": "read"}, timeout=60)
        if r.status_code == 200:
            try:
                j = r.json()
                if isinstance(j, list) and j:
                    data = j
            except Exception:
                data = None
    except Exception:
        data = None
    if data is None:
        try:
            r2 = requests.get(CONFIG["url_api"], params={"sheet": nome_foglio}, timeout=60)
            j2 = r2.json()
            if isinstance(j2, list) and j2:
                data = j2
        except Exception as e:
            st.error(f"Erreur de connexion: {e}")
            return [], []
    if not data:
        return [], []
    headers = [str(h).strip() for h in data[0]]
    records = [dict(zip(headers, row)) for row in data[1:]]
    cache[nome_foglio] = (datetime.now(), headers, records)
    st.session_state["_cache"] = cache
    return headers, records


def leggi_admin(force=False):
    cache = st.session_state.get("_cache", {})
    if not force and "_admin" in cache:
        ts, bundle = cache["_admin"]
        if (datetime.now() - ts).total_seconds() < 120:
            return bundle
    bundle = None
    try:
        r = requests.post(CONFIG["url_api"], json={"action": "read_all",
                                                   "sheets": ["DIPENDENTI", "SALARI", "TURNI", "VISITE_MEDICHE"]}, timeout=90)
        if r.status_code == 200:
            j = r.json()
            if isinstance(j, dict) and "DIPENDENTI" in j:
                bundle = {}
                for name, rows in j.items():
                    if isinstance(rows, list) and rows:
                        headers = [str(h).strip() for h in rows[0]]
                        bundle[name] = [dict(zip(headers, row)) for row in rows[1:]]
                    else:
                        bundle[name] = []
    except Exception:
        bundle = None
    if bundle is None:
        bundle = {}
        for name in ("DIPENDENTI", "SALARI", "TURNI", "VISITE_MEDICHE"):
            _, recs = leggi_foglio(name, force=force)
            bundle[name] = recs
    cache["_admin"] = (datetime.now(), bundle)
    st.session_state["_cache"] = cache
    return bundle


def salva_append(nome_foglio, row, chiave_id=None, valore_id=None):
    ok, msg = _post_json({"sheet": nome_foglio, "action": "append", "row": row})
    if ok:
        _svuota_cache(nome_foglio)
        return True, "ok"
    if chiave_id:
        try:
            _, recs = leggi_foglio(nome_foglio, force=True)
            if any(s_str(r.get(chiave_id)) == s_str(valore_id) for r in recs):
                _svuota_cache(nome_foglio)
                return True, "ok (verificato sul foglio)"
        except Exception:
            pass
    return ok, msg


def salva_append_many(nome_foglio, rows):
    if not rows:
        return True, "ok"
    ok, msg = _post_json({"sheet": nome_foglio, "action": "append", "rows": rows})
    if ok:
        _svuota_cache(nome_foglio)
    return ok, msg


def salva_update(nome_foglio, row_index, row):
    ok, msg = _post_json({"sheet": nome_foglio, "action": "update", "rowIndex": row_index, "row": row})
    if ok:
        _svuota_cache(nome_foglio)
    return ok, msg


def trova_duplicato_reg(dati):
    oggi = datetime.now().strftime("%d/%m/%Y")
    _, recs = leggi_foglio("DIPENDENTI", force=True)
    for r in recs:
        if (s_str(r.get("cognome")).lower() == s_str(dati.get("cognome")).lower()
                and s_str(r.get("nome")).lower() == s_str(dati.get("nome")).lower()
                and s_str(r.get("telefono_1")) == s_str(dati.get("telefono_1"))
                and s_str(r.get("data_registrazione")).startswith(oggi)):
            return r
    return None


def trova_duplicato_cand(cognome, nome, email, tel):
    oggi = datetime.now().strftime("%d/%m/%Y")
    _, recs = leggi_foglio("CANDIDATURE", force=True)
    for r in recs:
        if (s_str(r.get("cognome")).lower() == s_str(cognome).lower()
                and s_str(r.get("nome")).lower() == s_str(nome).lower()
                and s_str(r.get("email")).lower() == s_str(email).lower()
                and s_str(r.get("telefono")) == s_str(tel)
                and s_str(r.get("data_candidatura")).startswith(oggi)):
            return r
    return None


# ============================================================
# GENERATORE PDF
# ============================================================
class PDFProacier(FPDF):
    titolo = "FICHE D'ENREGISTREMENT - RESSOURCES HUMAINES"

    def header(self):
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(94, 165, 41)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, self.titolo, 0, 1, "C", True)
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
        self.cell(0, 5, s_str(val) or "___", 0, 1)

    def campo_doppio(self, e1, v1, e2, v2):
        self.set_font("Helvetica", "B", 8)
        self.cell(50, 5, e1, 0, 0)
        self.set_font("Helvetica", "", 8)
        self.cell(45, 5, s_str(v1) or "", 0, 0)
        self.set_font("Helvetica", "B", 8)
        self.cell(50, 5, e2, 0, 0)
        self.set_font("Helvetica", "", 8)
        self.cell(0, 5, s_str(v2) or "", 0, 1)


def genera_pdf_lavoratore(d, lingua="fr"):
    pdf = PDFProacier()
    pdf.titolo = get_testo("pdf_titolo", lingua)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 5, f"{get_testo('pdf_nfiche', lingua)} {s_str(d.get('codice'))}", 0, 0)
    pdf.cell(0, 5, f"{get_testo('pdf_data', lingua)} {datetime.now().strftime('%d/%m/%Y')}", 0, 1, "R")
    pdf.ln(2)
    pdf.sezione(get_testo("pdf_sez1", lingua))
    pdf.campo_doppio(get_testo("pdf_nom", lingua), d.get("cognome"), get_testo("pdf_prenoms", lingua), d.get("nome"))
    pdf.campo_doppio(get_testo("pdf_ne_le", lingua), formatta_data(d.get("data_nascita")), get_testo("pdf_a", lingua), d.get("luogo_nascita"))
    pdf.campo_doppio(get_testo("pdf_nationalite", lingua), etichetta("paesi", d.get("nazionalita"), lingua), get_testo("pdf_pays", lingua), etichetta("paesi", d.get("paese_origine"), lingua))
    pdf.campo_doppio(get_testo("pdf_etat_civil", lingua), etichetta("stato_civile", d.get("stato_civile"), lingua), get_testo("pdf_enfants", lingua), d.get("figli_totale"))
    if s_int(d.get("numero_mogli")) > 0:
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(60, 5, get_testo("pdf_epouses", lingua), 0, 0)
        pdf.set_font("Helvetica", "", 8)
        pdf.multi_cell(0, 4, s_str(d.get("dettagli_mogli")))
        pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez2", lingua))
    pdf.campo(get_testo("pdf_adresse", lingua), f"{s_str(d.get('indirizzo'))}, {s_str(d.get('quartiere'))}, {s_str(d.get('regione_senegal'))}")
    pdf.campo_doppio(get_testo("pdf_tel1", lingua), d.get("telefono_1"), get_testo("pdf_tel2", lingua), d.get("telefono_2"))
    pdf.campo_doppio("CNI: ", d.get("cni"), "CSS: ", d.get("css"))
    pdf.campo_doppio("NIF: ", d.get("nif"), "IPRES: ", d.get("ipres"))
    pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez3", lingua))
    pdf.campo(get_testo("pdf_poste", lingua), d.get("mansione_1"))
    pdf.campo(get_testo("pdf_competence", lingua), f"{etichetta('categoria', d.get('categoria_competenza'), lingua)} - {s_str(d.get('dettaglio_competenza'))}")
    pdf.campo(get_testo("pdf_permis", lingua), d.get("patente"))
    pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez4", lingua))
    pdf.campo_doppio(get_testo("pdf_tshirt", lingua), d.get("taglia_maglia"), get_testo("pdf_pantalon", lingua), d.get("taglia_pantaloni"))
    pdf.campo_doppio(get_testo("pdf_pointure", lingua), d.get("taglia_scarpe"), get_testo("pdf_gilet", lingua), d.get("taglia_giacca"))
    pdf.campo_doppio(get_testo("pdf_casque", lingua), d.get("taglia_cappello"), get_testo("pdf_gants", lingua), d.get("taglia_guanti"))
    pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez5", lingua))
    pdf.campo_doppio(get_testo("pdf_groupe", lingua), f"{s_str(d.get('gruppo_sanguigno'))} {s_str(d.get('rh'))}", get_testo("pdf_aptitude", lingua), etichetta("idoneita", d.get("idoneita"), lingua))
    pdf.campo_doppio(get_testo("pdf_urgence", lingua), d.get("emergenza_nome"), get_testo("pdf_tel", lingua), d.get("emergenza_tel"))
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, get_testo("pdf_certifie", lingua))
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 6, get_testo("pdf_candidat", lingua), 1, 0, "C")
    pdf.cell(95, 6, get_testo("pdf_employeur", lingua), 1, 1, "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(95, 15, "", 1, 0)
    pdf.cell(95, 15, "", 1, 1)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, get_testo("pdf_consent_titolo", lingua), 0, 1, "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, get_testo("pdf_consent_testo", lingua))
    pdf.ln(10)
    pdf.cell(0, 6, get_testo("pdf_signature", lingua), 0, 1)
    pdf.cell(0, 20, "", 1, 1)
    pdf.add_page()
    pdf.set_fill_color(255, 243, 205)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, get_testo("pdf_id_titolo", lingua), 0, 1, "C", True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, get_testo("pdf_id_desc", lingua), 0, 1, "C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, f"{get_testo('pdf_id_code', lingua)} {s_str(d.get('codice')) or '_________'}", 0, 1, "C")
    pdf.ln(3)
    pdf.cell(0, 12, f"PIN: {s_str(d.get('pin')) or '_________'}", 0, 1, "C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 5, get_testo("pdf_id_avviso", lingua))
    pdf.set_text_color(0, 0, 0)
    out = pdf.output(dest="S")
    if isinstance(out, str):
        out = out.encode("latin-1", errors="ignore")
    return bytes(out)


# ============================================================
# STEP DEL FORMULARIO
# ============================================================
def box_telefono(lingua, n, obbligatorio=False):
    st.markdown(f'<div class="phone-box"><h4>{get_testo("telefono_" + str(n), lingua)}{" *" if obbligatorio else ""}</h4></div>', unsafe_allow_html=True)
    tel = st.text_input(f"Numero {n}", value=st.session_state.dati_form.get(f"telefono_{n}", ""), key=f"s2_tel{n}", label_visibility="collapsed")
    servizi_attivi = s_str(st.session_state.dati_form.get(f"servizi_tel{n}", "")).split(", ")
    cb = st.columns(5)
    sel = {}
    for i, sv in enumerate(("Wave", "Orange Money", "WhatsApp", "Telegram", "Signal")):
        sel[sv] = cb[i].checkbox(sv, value=sv in servizi_attivi, key=f"s2_sv{n}_{i}")
    servizi = ", ".join([k for k, v in sel.items() if v])
    return tel, servizi


def step_1(lingua):
    st.subheader(get_testo("step_1", lingua))
    c1, c2 = st.columns(2)
    with c1:
        cognome = st.text_input(f'{get_testo("cognome", lingua)} *', value=st.session_state.dati_form.get("cognome", ""), key="s1_cog")
        nome = st.text_input(f'{get_testo("nome", lingua)} *', value=st.session_state.dati_form.get("nome", ""), key="s1_nom")
        st.markdown(f'{get_testo("data_nascita", lingua)}')
        g, m, a = st.columns(3)
        giorno = g.selectbox(get_testo("giorno", lingua), list(range(1, 32)), key="s1_g")
        mese = m.selectbox(get_testo("mese", lingua), list(range(1, 13)), key="s1_m")
        anno = a.selectbox(get_testo("anno", lingua), list(range(1950, 2010)), index=30, key="s1_a")
        luogo = st.text_input(get_testo("luogo_nascita", lingua), value=st.session_state.dati_form.get("luogo_nascita", ""), key="s1_luo")
        naz = select_canonico("paesi", lingua, get_testo("nazionalita", lingua), "s1_naz", saved=st.session_state.dati_form.get("nazionalita"))
        if naz == "AUTRE":
            naz = st.text_input("Précisez:", key="s1_naz_a")
        por = select_canonico("paesi", lingua, get_testo("paese_origine", lingua), "s1_pae", saved=st.session_state.dati_form.get("paese_origine"))
        if por == "AUTRE":
            por = st.text_input("Précisez:", key="s1_pae_a")
    with c2:
        sesso = select_canonico("sesso", lingua, get_testo("sesso", lingua), "s1_ses", saved=st.session_state.dati_form.get("sesso"))
        stato_civile = select_canonico("stato_civile", lingua, get_testo("stato_civile", lingua), "s1_sta", saved=st.session_state.dati_form.get("stato_civile"))
        numero_mogli, dettagli_mogli, figli_tot = 0, "", 0
        if stato_civile == "coniugato":
            numero_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=1, key="s1_mog")
            det = []
            for i in range(1, numero_mogli + 1):
                st.markdown(f"Épouse {i}")
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
        st.markdown(f"Emploi {i}")
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
    categoria = select_canonico("categoria", lingua, get_testo("categoria_competenza", lingua), "s4_cat", saved=st.session_state.dati_form.get("categoria_competenza"))
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
        idoneita = select_canonico("idoneita", lingua, get_testo("idoneita", lingua), "s5_ido", saved=st.session_state.dati_form.get("idoneita"))
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
# PAGINA REGISTRAZIONE
# ============================================================
def pannello_successo(lingua):
    u = st.session_state.ultimo_salvataggio
    if u.get("dup"):
        st.info(get_testo("reg_gia", lingua))
    else:
        st.success(f'✅ {get_testo("pdf_generato", lingua)}')
    st.warning(get_testo("conserva_credenziali", lingua))
    c1, c2 = st.columns(2)
    c1.info(f'{get_testo("codice_accesso", lingua)}: {u["codice"]}')
    c2.info(f'{get_testo("pin_accesso", lingua)}: {u["pin"]}')
    st.download_button(label=f'📥 {get_testo("scarica", lingua)} PDF', data=u["pdf"],
                       file_name=f'Proacier_{u["codice"]}.pdf', mime="application/pdf",
                       use_container_width=True, key="btn_dl_ok")
    st.markdown("---")
    blocco_telegram(lingua)
    st.markdown("---")
    if st.button(get_testo("nuova_registrazione", lingua), use_container_width=True):
        st.session_state.ultimo_salvataggio = None
        st.session_state.reg_fp = None
        st.session_state.dati_form = {}
        st.session_state.step = 1
        st.session_state.avviso_mostrato = False
        st.rerun()


def pagina_registrazione(lingua):
    if st.session_state.get("ultimo_salvataggio"):
        pannello_successo(lingua)
        return
    step = st.session_state.step
    if step == 1 and not st.session_state.avviso_mostrato:
        st.warning(get_testo("avviso_non_contratto", lingua))
        st.info(get_testo("avviso_regole_aziendali", lingua))
        st.session_state.avviso_mostrato = True
    st.progress(step / 7)
    st.markdown(f"Étape {step}/7")
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
    if not dati.get("cognome") or not dati.get("nome"):
        st.warning(get_testo("errore_obbligatori", lingua))
        return
    fp = "|".join([s_str(dati.get("cognome")).lower(), s_str(dati.get("nome")).lower(), s_str(dati.get("telefono_1"))])
    if st.session_state.get("reg_fp") == fp:
        st.info(get_testo("reg_gia", lingua))
        return
    with st.spinner(get_testo("saving", lingua)):
        dup = trova_duplicato_reg(dati)
        if dup:
            st.session_state.reg_fp = fp
            st.session_state.ultimo_salvataggio = {"codice": s_str(dup.get("codice")), "pin": s_str(dup.get("pin")),
                                                   "pdf": genera_pdf_lavoratore(dup, lingua), "dup": True}
            st.session_state.dati_form = {}
            st.rerun()
            return
        codice, pin = genera_credenziali()
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        row = dict(dati)
        row.update({"id": codice, "codice": codice, "pin": pin, "data_registrazione": now,
                    "stato_firma": "Da firmare", "timestamp": now, "turno": ""})
        ok, msg = salva_append("DIPENDENTI", row, "codice", codice)
        if ok:
            st.session_state.reg_fp = fp
            st.session_state.ultimo_salvataggio = {"codice": codice, "pin": pin,
                                                   "pdf": genera_pdf_lavoratore(row, lingua)}
            st.session_state.dati_form = {}
            st.rerun()
        else:
            st.error(f"Erreur: {msg}")


# ============================================================
# PAGINA CANDIDATURA
# ============================================================
def pagina_candidatura(lingua):
    idx = LINGUE.get(lingua, 0)
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        c_cognome = st.text_input(f'{get_testo("cognome", lingua)} *', key="c_cognome")
        c_nome = st.text_input(f'{get_testo("nome", lingua)} *', key="c_nome")
        c_email = st.text_input(f'{get_testo("email", lingua)} *', key="c_email")
        c_tel = st.text_input(f'{get_testo("telefono_1", lingua)} *', key="c_tel")
        st.markdown(f'{get_testo("data_nascita", lingua)}')
        g, m, a = st.columns(3)
        cg = g.selectbox(get_testo("giorno", lingua), list(range(1, 32)), key="c_g")
        cm = m.selectbox(get_testo("mese", lingua), list(range(1, 13)), key="c_m")
        ca = a.selectbox(get_testo("anno", lingua), list(range(1960, 2010)), index=30, key="c_a")
    with c2:
        c_ind = st.text_input(get_testo("indirizzo", lingua), key="c_ind")
        c_com = st.text_input(get_testo("comune", lingua), key="c_com")
        c_reg = st.selectbox(get_testo("regione_senegal", lingua), ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"], key="c_reg")
        labels = [ar["label"][idx] for ar in AREE_AZIENDALI]
        settore = st.selectbox(get_testo("settore_richiesto", lingua), labels, key="c_settore")
        area_idx = labels.index(settore)
        area = AREE_AZIENDALI[area_idx]
        if area["ruoli"]:
            mansione = st.selectbox(get_testo("mansione_richiesta", lingua), area["ruoli"], key=f"c_man_{area_idx}")
        else:
            mansione = st.text_input(get_testo("altro_specifica", lingua), key=f"c_man_libera_{area_idx}")
        c_studi = select_canonico("studi", lingua, get_testo("studi", lingua), "c_studi")
        if c_studi == "prof":
            st.caption(get_testo("hint_prof", lingua))
        c_skills = st.text_area(get_testo("skills", lingua), key="c_skills")
        c3, c4 = st.columns(2)
        c_exp = c3.number_input(get_testo("esperienza_anno", lingua), min_value=0, max_value=50, value=0, key="c_exp")
        c_sal = c4.text_input(get_testo("salario_richiesto", lingua), key="c_sal")
        c_note = st.text_area(get_testo("note", lingua), key="c_note")
    st.markdown("---")
    if st.button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True, key="btn_cand_invia"):
        if not c_cognome or not c_nome or not c_email or not c_tel:
            st.error(get_testo("errore_candidatura", lingua))
        else:
            fp = "|".join([c_cognome.strip().lower(), c_nome.strip().lower(), c_email.strip().lower(), c_tel.strip()])
            if st.session_state.get("cand_fp") == fp:
                st.info(get_testo("candidatura_gia_inviata", lingua))
            else:
                with st.spinner(get_testo("saving", lingua)):
                    dup = trova_duplicato_cand(c_cognome, c_nome, c_email, c_tel)
                    if dup:
                        st.session_state.cand_fp = fp
                        st.info(get_testo("candidatura_gia_inviata", lingua))
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
                            st.session_state.cand_fp = fp
                            st.success(get_testo("candidatura_inviata", lingua))
                            st.balloons()
                        else:
                            st.error(f"Erreur: {msg}")
    if st.session_state.get("cand_fp") and st.button(get_testo("nouvelle_candidature", lingua), use_container_width=True, key="btn_cand_new"):
        for k in ("c_cognome", "c_nome", "c_email", "c_tel", "c_ind", "c_com", "c_skills", "c_sal", "c_note", "c_studi"):
            st.session_state.pop(k, None)
        for k in list(st.session_state.keys()):
            if k.startswith("c_man_"):
                st.session_state.pop(k, None)
        st.session_state.cand_fp = None
        st.rerun()


# ============================================================
# TELEGRAM HELPERS
# ============================================================
def telegram_cfg():
    out = {}
    try:
        _, recs = leggi_foglio("CONFIG")
    except Exception:
        return out
    for r in recs:
        k = s_str(r.get("chiave")).lower().replace(" ", "_")
        if k in ("telegram_bot_token", "telegram_chat_id", "telegram_link_canale"):
            out[k] = s_str(r.get("valore"))
    return out


def invia_avviso_telegram(titolo, testo, urgente):
    tc = telegram_cfg()
    tok, chat = tc.get("telegram_bot_token"), tc.get("telegram_chat_id")
    if not tok or not chat:
        return False
    msg = ("🚨 URGENT\n" if urgente else "📢 PROACIER\n") + f"*{titolo}*\n\n{testo}"
    try:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                          json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"}, timeout=30)
        return r.status_code == 200
    except Exception:
        return False


def blocco_telegram(lingua):
    tc = telegram_cfg()
    link_canale = tc.get("telegram_link_canale")
    st.caption(get_testo("tg_obbligo", lingua))
    c1, c2 = st.columns(2)
    c1.link_button(get_testo("tg_install", lingua), "https://telegram.org/download", use_container_width=True)
    if link_canale:
        c2.link_button(get_testo("tg_join", lingua), link_canale, use_container_width=True)


def bacheca_avvisi(lingua):
    try:
        _, recs = leggi_foglio("AVVISI")
    except Exception:
        return
    recs = [r for r in recs if s_str(r.get("titolo"))]
    if not recs:
        return
    recs = list(reversed(recs))[:5]
    st.markdown("**" + get_testo("bacheca_title", lingua) + "**")
    for r in recs:
        urg = s_str(r.get("urgente")).upper() in ("SI", "SÌ", "YES", "TRUE", "1")
        box = st.error if urg else st.info
        box(f"**{s_str(r.get('titolo'))}** — {s_str(r.get('data_avviso'))}\n\n{s_str(r.get('testo'))}")


# ============================================================
# PROMEMORIA FESTIVITÀ
# ============================================================
def promemoria_festivita(lingua, consiglio=False):
    try:
        _, recs = leggi_foglio("CONFIG")
    except Exception:
        return
    giorni_limite = 10
    fest = []
    for r in recs:
        k = s_str(r.get("chiave")).lower().replace(" ", "_")
        v = s_str(r.get("valore"))
        if k == "promemoria_festivita_giorni_prima":
            try:
                f = int(float(v))
                if f > 0:
                    giorni_limite = f
            except Exception:
                pass
        elif k.startswith("festivo_"):
            ds = k.replace("festivo_", "", 1)
            try:
                y, m, g = ds.split("-")
                fest.append((date(int(y), int(m), int(g)), v or "Férié"))
            except Exception:
                pass
    oggi = date.today()
    imminenti = sorted([(d, n) for (d, n) in fest if 0 <= (d - oggi).days <= giorni_limite])
    if not imminenti:
        return
    righe = []
    for d, n in imminenti:
        delta = (d - oggi).days
        quando = get_testo("fest_oggi", lingua) if delta == 0 else get_testo("fest_tra", lingua).format(n=delta)
        righe.append(f"- **{n}** — {d.strftime('%d/%m/%Y')} ({quando})")
    msg = "**" + get_testo("fest_box_titolo", lingua) + "**\n\n" + "\n".join(righe)
    if consiglio:
        msg += "\n\n" + get_testo("fest_stop", lingua)
    st.info(msg)


# ============================================================
# AREA LAVORATORE
# ============================================================
def pagina_area_lavoratore(lingua):
    st.title(get_testo("i_miei_dati", lingua))
    st.success(f'{get_testo("benvenuto", lingua)} - {st.session_state.codice_operatore}')
    promemoria_festivita(lingua)
    bacheca_avvisi(lingua)
    blocco_telegram(lingua)
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
    c3.text_input(get_testo("nazionalita", lingua), value=etichetta("paesi", mio.get("nazionalita"), lingua), disabled=True)
    st.markdown("---")
    st.subheader("🩺 " + get_testo("sezione_medica", lingua))
    _, recs_vis_me = leggi_foglio("VISITE_MEDICHE")
    mie_vis = [v for v in recs_vis_me if s_str(v.get("codice_lavoratore")).upper() == str(st.session_state.codice_operatore).strip().upper()]
    mie_vis.sort(key=lambda v: data_ord(v.get("data_visita")) or (0, 0, 0), reverse=True)
    if mie_vis:
        ultima = mie_vis[0]
        pc = data_ord(ultima.get("prossimo_controllo"))
        if pc:
            lim = datetime.now() + timedelta(days=30)
            if pc <= (lim.year, lim.month, lim.day):
                st.warning(f'{get_testo("promemoria_visita", lingua)} {s_str(ultima.get("prossimo_controllo"))}')
        if norm_idoneita(ultima.get("idoneita")) in ("restriction", "inapte") and s_str(ultima.get("restrizioni")):
            st.info("🩺 " + s_str(ultima.get("restrizioni")))
    c1, c2, c3 = st.columns(3)
    c1.text_input(get_testo("gruppo_sanguigno", lingua), value=s_str(mio.get("gruppo_sanguigno")), disabled=True)
    c1.text_input(get_testo("rh", lingua), value=s_str(mio.get("rh")), disabled=True)
    c2.text_input(get_testo("idoneita", lingua), value=etichetta("idoneita", mio.get("idoneita"), lingua), disabled=True)
    c2.text_input(get_testo("data_visita", lingua), value=formatta_data(mio.get("data_visita")), disabled=True)
    c3.text_input(get_testo("allergie", lingua), value=s_str(mio.get("allergie")), disabled=True)
    c3.text_input(get_testo("malattie", lingua), value=s_str(mio.get("malattie")), disabled=True)
    if mie_vis:
        with st.expander("🩺 " + get_testo("storico_visite", lingua)):
            for v in mie_vis:
                riga = (f"- {s_str(v.get('data_visita'))} ({etichetta('tipo_visita', v.get('tipo_visita'), lingua)}) "
                        f"— {etichetta('idoneita', v.get('idoneita'), lingua)}")
                if s_str(v.get("esito")):
                    riga += f" — {s_str(v.get('esito'))}"
                if s_str(v.get("restrizioni")):
                    riga += f" — ⛔ {s_str(v.get('restrizioni'))}"
                st.markdown(riga)
    else:
        st.caption(get_testo("nessuna_visita", lingua))
    st.markdown("---")
    st.subheader(get_testo("sezione_paga", lingua))
    _, sal_records = leggi_foglio("SALARI")
    mia_paga = [s for s in sal_records if s_str(s.get("codice_lavoratore")).upper() == str(st.session_state.codice_operatore).strip().upper()]
    if mia_paga:
        c1, c2 = st.columns(2)
        c1.text_input(get_testo("paga_type", lingua), value=etichetta("tipo_paga", mia_paga[0].get("tipo_paga"), lingua) or s_str(mia_paga[0].get("tipo_paga")), disabled=True)
        c2.text_input(get_testo("paga_amount", lingua), value=s_str(mia_paga[0].get("importo_base")) + " FCFA", disabled=True)
    else:
        st.info(get_testo("paga_desc", lingua))
    st.markdown("---")
    st.caption(get_testo("form_hint", lingua))
    with st.form("area_lav_form"):
        st.subheader(get_testo("sezione_contatti", lingua))
        c1, c2 = st.columns(2)
        with c1:
            n_tel1 = st.text_input(get_testo("telefono_1", lingua), value=s_str(mio.get("telefono_1")), key="ar_tel1")
            n_tel2 = st.text_input(get_testo("telefono_2", lingua), value=s_str(mio.get("telefono_2")), key="ar_tel2")
            n_tel3 = st.text_input(get_testo("telefono_3", lingua), value=s_str(mio.get("telefono_3")), key="ar_tel3")
            n_ind = st.text_input(get_testo("indirizzo", lingua), value=s_str(mio.get("indirizzo")), key="ar_ind")
        with c2:
            n_qua = st.text_input(get_testo("quartiere", lingua), value=s_str(mio.get("quartiere")), key="ar_qua")
            n_com = st.text_input(get_testo("comune", lingua), value=s_str(mio.get("comune")), key="ar_com")
            n_reg = st.text_input(get_testo("regione_senegal", lingua), value=s_str(mio.get("regione_senegal")), key="ar_reg")
            n_em_nome = st.text_input(get_testo("emergenza_nome", lingua), value=s_str(mio.get("emergenza_nome")), key="ar_emn")
            n_em_tel = st.text_input(get_testo("emergenza_tel", lingua), value=s_str(mio.get("emergenza_tel")), key="ar_emt")
        st.markdown("---")
        st.subheader(get_testo("sezione_famille", lingua))
        n_stato = select_canonico("stato_civile", lingua, get_testo("stato_civile", lingua), "ar_stato", saved=mio.get("stato_civile"))
        c1, c2 = st.columns(2)
        with c2:
            n_mogli = 0
            if n_stato == "coniugato":
                n_mogli = int(st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=max(1, s_int(mio.get("numero_mogli"))), key="ar_mogli"))
            esistenti = parse_mogli(mio.get("dettagli_mogli"))
            dettagli = ""
            if n_stato == "coniugato":
                st.caption(get_testo("mogli_hint", lingua))
                det, somma_mogli = [], 0
                for i in range(1, n_mogli + 1):
                    st.markdown(f"Épouse {i}")
                    cr, cf = st.columns(2)
                    old = esistenti[i - 1] if len(esistenti) >= i else {"res": "", "fig": 0}
                    res = cr.text_input(f'{get_testo("residenza_moglie", lingua)} {i}', value=old["res"], key=f"ar_res{i}")
                    fig = int(cf.number_input(f'{get_testo("figli_moglie", lingua)} {i}', min_value=0, value=old["fig"], key=f"ar_fig{i}"))
                    somma_mogli += fig
                    det.append(f"Épouse {i}: {res} ({fig} enfants)")
                dettagli = " | ".join(det)
                st.info(f'ℹ️ {get_testo("somma_mogli", lingua)}: {somma_mogli}')
            n_figli = int(st.number_input(get_testo("figli_totale", lingua), min_value=0,
                                          value=s_int(mio.get("figli_totale")), key="ar_fig_tot"))
        st.markdown("---")
        st.subheader(get_testo("sezione_vestiario", lingua))
        xs = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]

        def safe_idx(lst, v):
            v = s_str(v)
            return lst.index(v) if v in lst else 0
        c1, c2 = st.columns(2)
        with c1:
            n_tm = st.selectbox(get_testo("taglia_maglia", lingua), xs, index=safe_idx(xs, mio.get("taglia_maglia")), key="ar_tm")
            n_tp = st.selectbox(get_testo("taglia_pantaloni", lingua), ["38", "40", "42", "44", "46", "48", "50", "52"], index=safe_idx(["38", "40", "42", "44", "46", "48", "50", "52"], mio.get("taglia_pantaloni")), key="ar_tp")
            n_ts = st.selectbox(get_testo("taglia_scarpe", lingua), [str(x) for x in range(38, 48)], index=safe_idx([str(x) for x in range(38, 48)], mio.get("taglia_scarpe")), key="ar_ts")
        with c2:
            n_tg = st.selectbox(get_testo("taglia_giacca", lingua), xs[:-1], index=safe_idx(xs[:-1], mio.get("taglia_giacca")), key="ar_tg")
            n_tc = st.selectbox(get_testo("taglia_cappello", lingua), ["S", "M", "L", "XL"], index=safe_idx(["S", "M", "L", "XL"], mio.get("taglia_cappello")), key="ar_tc")
            n_tgu = st.selectbox(get_testo("taglia_guanti", lingua), ["S", "M", "L", "XL"], index=safe_idx(["S", "M", "L", "XL"], mio.get("taglia_guanti")), key="ar_tgu")
        st.markdown("---")
        sub = st.form_submit_button(get_testo("salva_modifiche", lingua), type="primary")
        if sub:
            upd = {"telefono_1": n_tel1, "telefono_2": n_tel2, "telefono_3": n_tel3,
                   "indirizzo": n_ind, "quartiere": n_qua, "comune": n_com, "regione_senegal": n_reg,
                   "emergenza_nome": n_em_nome, "emergenza_tel": n_em_tel, "stato_civile": n_stato,
                   "figli_totale": n_figli, "numero_mogli": n_mogli, "dettagli_mogli": dettagli,
                   "taglia_maglia": n_tm, "taglia_pantaloni": n_tp, "taglia_scarpe": n_ts,
                   "taglia_giacca": n_tg, "taglia_cappello": n_tc, "taglia_guanti": n_tgu}
            with st.spinner(get_testo("saving", lingua)):
                ok, msg = salva_update("DIPENDENTI", mio_idx, upd)
                if ok:
                    st.success(get_testo("modifiche_salvate", lingua))
                    st.rerun()
                else:
                    st.error(f"{get_testo('errore_salvataggio', lingua)} ({msg})")
    st.info(get_testo("sezione_comunicazioni", lingua))
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(get_testo("salva_link", lingua), use_container_width=True):
            _code = s_str(mio.get("codice"))
            _pin = s_str(mio.get("pin"))
            st.query_params.update({"code": _code, "pin": _pin})
            st.session_state.link_personale = f"{CONFIG['base_url']}/?code={_code}&pin={_pin}"
            st.info(get_testo("link_hint", lingua))
        if st.session_state.get("link_personale"):
            st.caption(get_testo("copia_link_help", lingua))
            st.code(st.session_state.link_personale, language=None)
    with c2:
        pdf_bytes = genera_pdf_lavoratore(dict(mio), lingua)
        st.download_button(label=get_testo("ristampa_pdf", lingua), data=pdf_bytes,
                           file_name=f"Proacier_{mio.get('codice')}.pdf", mime="application/pdf",
                           use_container_width=True)
    st.markdown("---")
    if st.button(get_testo("logout", lingua), use_container_width=True):
        _do_logout()
        st.rerun()


# ============================================================
# DASHBOARD ADMIN (salva-tutto)
# ============================================================
def pagina_dashboard(lingua):
    st.title(get_testo("dashboard", lingua))
    env = st.session_state.get("ambiente", "produzione")
    with st.expander("🧪 " + get_testo("amb_title", lingua), expanded=(env == "test")):
        sel_env = st.radio("Ambiente", ["produzione", "test"],
                           index=0 if env == "produzione" else 1,
                           horizontal=True, key="amb_sel", label_visibility="collapsed")
        st.caption(get_testo("amb_hint", lingua))
        if sel_env != env:
            st.session_state["ambiente"] = sel_env
            _svuota_cache()
            st.rerun()
    promemoria_festivita(lingua, consiglio=True)
    pag = st.radio("Pagina", [get_testo("dash_p1", lingua), get_testo("dash_p2", lingua)],
                   horizontal=True, label_visibility="collapsed")
    if pag == get_testo("dash_p2", lingua):
        fase6_paghe.pagina_fase6(lingua, sys.modules[__name__])
        return
    b = leggi_admin()
    recs_dip = b.get("DIPENDENTI", [])
    recs_sal = b.get("SALARI", [])
    recs_turni = b.get("TURNI", [])
    recs_vis = b.get("VISITE_MEDICHE", [])
    turni_codes = [s_str(r.get("codice_turno")) for r in recs_turni
                   if s_str(r.get("codice_turno")) and s_str(r.get("ora_inizio"))]
    if not turni_codes:
        turni_codes = ["T1", "T2", "T3", "EQUIPE"]
    c1, c2, c3 = st.columns(3)
    c1.metric(get_testo("totale_operai", lingua), len(recs_dip))
    c2.metric(get_testo("turni_assegnati", lingua), sum(1 for r in recs_dip if s_str(r.get("turno"))))
    c3.metric(get_testo("salari_attivi", lingua), sum(1 for r in recs_sal
                                                      if s_str(r.get("codice_lavoratore")) and not s_str(r.get("data_fine_validita"))))
    ultime = {}
    for v in recs_vis:
        cod = s_str(v.get("codice_lavoratore"))
        if not cod:
            continue
        o = data_ord(v.get("data_visita"))
        if cod not in ultime or (o and (ultime[cod][0] is None or o > ultime[cod][0])):
            ultime[cod] = (o, v)
    lim = datetime.now() + timedelta(days=30)
    lim_t = (lim.year, lim.month, lim.day)
    scaduti, restritti = [], []
    for r in recs_dip:
        cod = s_str(r.get("codice"))
        nome = f"{s_str(r.get('cognome'))} {s_str(r.get('nome'))}"
        u = ultime.get(cod)
        if u:
            pc = data_ord(u[1].get("prossimo_controllo"))
            if pc and pc <= lim_t:
                scaduti.append(f"{nome} ({cod}) → {s_str(u[1].get('prossimo_controllo'))}")
        if norm_idoneita(r.get("idoneita")) in ("restriction", "inapte"):
            restritti.append(f"{nome} ({cod})")
    if scaduti:
        st.warning("⚠️ " + get_testo("visite_scadute", lingua) + ": " + "; ".join(scaduti))
    if restritti:
        st.error("🩺 " + get_testo("idoneita_parziale", lingua) + ": " + "; ".join(restritti))
    st.markdown("---")
    cerca = st.text_input(get_testo("cerca_dip", lingua), key="adm_cerca")
    mostrati = []
    for i, r in enumerate(recs_dip):
        blob = (s_str(r.get("codice")) + " " + s_str(r.get("cognome")) + " " + s_str(r.get("nome"))).lower()
        if not cerca or cerca.lower() in blob:
            mostrati.append((i, r))
    if not mostrati:
        st.warning(get_testo("nessun_risultato", lingua))
        return
    limite = st.session_state.get("adm_limit", 15)
    vista = mostrati if cerca else mostrati[:limite]
    st.caption(get_testo("form_hint", lingua))
    for i, r in vista:
        cod = s_str(r.get("codice"))
        with st.expander(f"{cod} — {s_str(r.get('cognome'))} {s_str(r.get('nome'))} | {get_testo('turno', lingua)}: {s_str(r.get('turno')) or '—'}"):
            st.markdown(
                f'{get_testo("data_nascita", lingua)}: {formatta_data(r.get("data_nascita"))} '
                f'— {get_testo("telefono_1", lingua)}: {s_str(r.get("telefono_1"))} '
                f'— {get_testo("regione_senegal", lingua)}: {s_str(r.get("regione_senegal"))}\n'
                f'{get_testo("stato_civile", lingua)}: {etichetta("stato_civile", r.get("stato_civile"), lingua)} '
                f'— {get_testo("figli_totale", lingua)}: {s_str(r.get("figli_totale"))} '
                f'— {get_testo("idoneita", lingua)}: {etichetta("idoneita", r.get("idoneita"), lingua)} '
                f'({formatta_data(r.get("data_visita"))})')
            st.markdown(f'### {get_testo("sez_admin", lingua)}')
            ca, cb = st.columns(2)
            with ca:
                t_val = s_str(r.get("turno"))
                t_idx = turni_codes.index(t_val) if t_val in turni_codes else 0
                n_turno = st.selectbox(get_testo("turno", lingua), turni_codes, index=t_idx, key=f"adm_turno_{cod}")
                ido_codes = [o[0] for o in OPZ["idoneita"]]
                ido_val = s_str(r.get("idoneita"))
                i_idx = ido_codes.index(ido_val) if ido_val in ido_codes else 0
                n_ido = st.selectbox(get_testo("idoneita", lingua), ido_codes, index=i_idx,
                                     format_func=lambda c: etichetta("idoneita", c, lingua), key=f"adm_ido_{cod}")
                n_vis = st.text_input(get_testo("data_visita", lingua), value=s_str(r.get("data_visita")), key=f"adm_vis_{cod}")
            with cb:
                attiva = None
                for s in recs_sal:
                    if s_str(s.get("codice_lavoratore")) == cod and not s_str(s.get("data_fine_validita")):
                        attiva = s
                        break
                tp_val = s_str(attiva.get("tipo_paga")) if attiva else ""
                tp_opts = ["", "giornaliero", "orario", "mensile"]
                tp_idx = tp_opts.index(tp_val) if tp_val in tp_opts else 0
                n_tp = st.selectbox(get_testo("paga_type", lingua), tp_opts, index=tp_idx,
                                    format_func=lambda x: get_testo("globale", lingua) if x == "" else etichetta("tipo_paga", x, lingua), key=f"adm_tp_{cod}")
                n_imp = st.number_input(get_testo("paga_amount", lingua) + " (FCFA)", min_value=0,
                                        value=s_int(attiva.get("importo_base")) if attiva else 0,
                                        step=500, key=f"adm_imp_{cod}")
            st.markdown("### 🩺 " + get_testo("storico_visite", lingua))
            mie_vis = [v for v in recs_vis if s_str(v.get("codice_lavoratore")) == cod]
            mie_vis.sort(key=lambda v: data_ord(v.get("data_visita")) or (0, 0, 0), reverse=True)
            if mie_vis:
                for v in mie_vis:
                    riga = (f"- {s_str(v.get('data_visita'))} ({etichetta('tipo_visita', v.get('tipo_visita'), lingua)}) "
                            f"— {etichetta('idoneita', v.get('idoneita'), lingua)} — {s_str(v.get('esito'))}")
                    if s_str(v.get("restrizioni")):
                        riga += f" — ⛔ {s_str(v.get('restrizioni'))}"
                    if s_str(v.get("prossimo_controllo")):
                        riga += f" — ➡️ {s_str(v.get('prossimo_controllo'))}"
                    st.markdown(riga)
            else:
                st.caption(get_testo("nessuna_visita", lingua))
            with st.form(f"adm_vis_form_{cod}"):
                v1, v2 = st.columns(2)
                with v1:
                    n_data_vis = st.text_input(get_testo("data_visita", lingua),
                                               value=datetime.now().strftime("%d/%m/%Y"), key=f"adm_visdata_{cod}")
                    n_tipo = st.selectbox(get_testo("tipo_visita", lingua), [o[0] for o in OPZ["tipo_visita"]],
                                          format_func=lambda c: etichetta("tipo_visita", c, lingua), key=f"adm_vistipo_{cod}")
                    n_ido2 = st.selectbox(get_testo("idoneita", lingua), [o[0] for o in OPZ["idoneita"]],
                                          format_func=lambda c: etichetta("idoneita", c, lingua), key=f"adm_visido_{cod}")
                with v2:
                    n_restr = st.text_input(get_testo("restrizioni", lingua), key=f"adm_visrestr_{cod}")
                    n_pross = st.text_input(get_testo("prossimo_controllo", lingua) + " (GG/MM/AAAA)", key=f"adm_vispros_{cod}")
                    n_esito = st.text_area(get_testo("esito", lingua), key=f"adm_visesito_{cod}")
                sub_vis = st.form_submit_button(get_testo("salva_modifiche", lingua))
                if sub_vis:
                    okv, mv = salva_append("VISITE_MEDICHE", {
                        "codice_lavoratore": cod, "data_visita": n_data_vis, "tipo_visita": n_tipo,
                        "idoneita": n_ido2, "restrizioni": n_restr, "esito": n_esito,
                        "prossimo_controllo": n_pross, "registrato_da": "admin",
                        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    okd, md = salva_update("DIPENDENTI", i, {"idoneita": n_ido2, "data_visita": n_data_vis})
                    if okv and okd:
                        st.success(get_testo("modifiche_salvate", lingua))
                        st.rerun()
                    else:
                        st.error(f"{get_testo('errore_salvataggio', lingua)} ({mv} {md})")
            st.download_button(get_testo("ristampa_pdf", lingua), data=genera_pdf_lavoratore(r, lingua),
                               file_name=f"Proacier_{cod}.pdf", mime="application/pdf",
                               use_container_width=True, key=f"adm_pdf_{cod}")
    # ---- SALVA-TUTTO (un solo click, solo righe cambiate) ----
    if st.button(get_testo("salva_tutto", lingua), type="primary", use_container_width=True):
        cambi = 0
        for i, r in vista:
            cod = s_str(r.get("codice"))
            upd = {}
            orig_turno = s_str(r.get("turno"))
            n_turno = st.session_state.get(f"adm_turno_{cod}", orig_turno)
            if n_turno != orig_turno:
                upd["turno"] = n_turno
            orig_ido = s_str(r.get("idoneita"))
            n_ido = st.session_state.get(f"adm_ido_{cod}", orig_ido)
            if n_ido != orig_ido:
                upd["idoneita"] = n_ido
            orig_vis = s_str(r.get("data_visita"))
            n_vis = st.session_state.get(f"adm_vis_{cod}", orig_vis)
            if n_vis != orig_vis:
                upd["data_visita"] = n_vis
            if upd:
                ok, _ = salva_update("DIPENDENTI", i, upd)
                if ok:
                    cambi += 1
            attiva = None
            for s in recs_sal:
                if s_str(s.get("codice_lavoratore")) == cod and not s_str(s.get("data_fine_validita")):
                    attiva = s
                    break
            orig_tp = s_str(attiva.get("tipo_paga")) if attiva else ""
            orig_imp = s_int(attiva.get("importo_base")) if attiva else 0
            n_tp = st.session_state.get(f"adm_tp_{cod}", orig_tp)
            n_imp = int(st.session_state.get(f"adm_imp_{cod}", orig_imp))
            if (n_tp != orig_tp) or (n_imp != orig_imp):
                if attiva:
                    ok2, _2 = salva_update("SALARI", recs_sal.index(attiva),
                                           {"tipo_paga": n_tp, "importo_base": n_imp})
                elif n_imp > 0 or n_tp:
                    ok2, _2 = salva_append("SALARI", {"codice_lavoratore": cod, "tipo_paga": n_tp,
                                                      "importo_base": n_imp,
                                                      "data_inizio_validita": datetime.now().strftime("%d/%m/%Y"),
                                                      "data_fine_validita": "", "note": ""})
                else:
                    ok2 = True
                if ok2:
                    cambi += 1
        st.success(f"✅ {cambi} {get_testo('salvate_n', lingua)}")
        st.rerun()
    if not cerca and len(mostrati) > limite:
        if st.button(get_testo("mostra_altri", lingua), key="adm_more"):
            st.session_state.adm_limit = limite + 15
            st.rerun()


# ============================================================
# LOGOUT CENTRALE
# ============================================================
def _do_logout():
    st.session_state.logged_in = False
    st.session_state.user_type = None
    st.session_state.codice_operatore = None
    st.session_state.pagina = "home"
    st.session_state.link_personale = None
    try:
        st.query_params.clear()
    except Exception:
        pass


# ============================================================
# MAIN (bandierine grandi in alto + sidebar compatta)
# ============================================================
def main():
    for k, v in {"lingua": "fr", "pagina": "home", "logged_in": False, "user_type": None,
                 "step": 1, "dati_form": {}, "codice_operatore": None, "avviso_mostrato": False,
                 "ultimo_salvataggio": None, "cand_fp": None, "reg_fp": None, "_cache": {},
                 "adm_limit": 15, "link_personale": None, "ambiente": "produzione"}.items():
        if k not in st.session_state:
            st.session_state[k] = v
    CONFIG["url_api"] = CONFIG["url_api_produzione"] if st.session_state.get("ambiente") == "produzione" else CONFIG["url_api_test"]
    if not st.session_state.logged_in:
        try:
            qp = st.query_params
            qc, qpin = qp.get("code"), qp.get("pin")
            au, ap = qp.get("adm_u"), qp.get("adm_p")
        except Exception:
            qc, qpin, au, ap = None, None, None, None
        if au and ap and au == CONFIG["user_admin"] and ap == CONFIG["password_admin"]:
            st.session_state.logged_in = True
            st.session_state.user_type = "admin"
        elif qc and qpin:
            _, recs = leggi_foglio("DIPENDENTI")
            for r in recs:
                if s_str(r.get("codice")).upper() == str(qc).strip().upper() and s_str(r.get("pin")) == str(qpin).strip():
                    st.session_state.logged_in = True
                    st.session_state.user_type = "lavoratore"
                    st.session_state.codice_operatore = str(qc).strip()
                    break
    lingua = st.session_state.lingua
    with st.sidebar:
        f1, f2, f3 = st.columns(3)
        if f1.button("🇫", key="flag_fr", use_container_width=True):
            st.session_state.lingua = "fr"
            st.rerun()
        if f2.button("🇮🇹", key="flag_it", use_container_width=True):
            st.session_state.lingua = "it"
            st.rerun()
        if f3.button("🇬🇧", key="flag_en", use_container_width=True):
            st.session_state.lingua = "en"
            st.rerun()
        st.image(CONFIG["logo_url"], use_container_width=True)
        if st.button(get_testo("home", lingua), use_container_width=True, key="sb_home"):
            _do_logout()
            st.rerun()
        if st.session_state.logged_in:
            st.success(f'{get_testo("benvenuto", lingua)}')
            if st.session_state.user_type == "admin":
                if st.button(get_testo("dashboard", lingua), use_container_width=True, key="sb_dash"):
                    st.session_state.pagina = "dashboard"
                    st.rerun()
            if st.session_state.user_type == "lavoratore":
                if st.button(get_testo("i_miei_dati", lingua), use_container_width=True, key="sb_miei"):
                    st.session_state.pagina = "area_lavoratore"
                    st.rerun()
            if st.button(get_testo("logout", lingua), use_container_width=True, key="sb_out"):
                _do_logout()
                st.rerun()
        else:
            if st.button(get_testo("candidatura_spontanea", lingua), use_container_width=True, key="sb_cand"):
                st.session_state.pagina = "candidatura"
                st.rerun()
            if st.button(get_testo("area_lavoratore", lingua), use_container_width=True, key="sb_area"):
                st.session_state.pagina = "espace"
                st.rerun()
            if st.button(get_testo("dashboard", lingua), use_container_width=True, key="sb_admin"):
                st.session_state.pagina = "login_admin"
                st.rerun()
        st.markdown("---")
        st.title(get_testo("titolo", lingua))
        st.markdown(get_testo("sottotitolo", lingua))
        st.caption(VERSIONE + (" — 🧪 SANDBOX" if st.session_state.get("ambiente") == "test" else ""))
    if st.session_state.pagina == "home":
        st.title(get_testo("titolo", lingua))
        st.subheader(get_testo("sottotitolo", lingua))
        promemoria_festivita(lingua)
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
            st.session_state.ultimo_salvataggio = None
            st.session_state.reg_fp = None
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
        ricordami = st.checkbox(get_testo("ricordami", lingua), key="lg_ric")
        if st.button(get_testo("accedi", lingua), type="primary", key="lg_btn"):
            _, records = leggi_foglio("DIPENDENTI")
            ok = any(s_str(r.get("codice")).upper() == codice.strip().upper() and s_str(r.get("pin")) == pin.strip() for r in records)
            if ok:
                st.session_state.logged_in = True
                st.session_state.user_type = "lavoratore"
                st.session_state.codice_operatore = codice.strip()
                if ricordami:
                    st.query_params.update({"code": codice.strip(), "pin": pin.strip()})
                    st.info(get_testo("link_hint", lingua))
                st.session_state.pagina = "area_lavoratore"
                st.rerun()
            else:
                st.error(get_testo("codice_errato", lingua))
    elif st.session_state.pagina == "login_admin":
        usr = st.text_input(get_testo("admin_user", lingua), key="lg_usr")
        pwd = st.text_input(get_testo("password", lingua), type="password", key="lg_pwd")
        ricordami = st.checkbox(get_testo("ricordami", lingua), key="lg_ric_adm")
        if st.button(get_testo("accedi", lingua), type="primary", key="lg_adm"):
            if usr.strip() == CONFIG["user_admin"] and pwd == CONFIG["password_admin"]:
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                if ricordami:
                    st.query_params.update({"adm_u": usr.strip(), "adm_p": pwd})
                    st.session_state.link_admin = f"{CONFIG['base_url']}/?adm_u={usr.strip()}&adm_p={pwd}"
                st.session_state.pagina = "dashboard"
                st.rerun()
            else:
                st.error(get_testo("codice_errato", lingua))
        if st.session_state.get("link_admin"):
            st.caption(get_testo("copia_link_help", lingua))
            st.code(st.session_state.link_admin, language=None)
    elif st.session_state.pagina == "dashboard":
        pagina_dashboard(lingua)


if __name__ == "__main__":
    main()