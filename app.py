# -*- coding: utf-8 -*-
"""PROACIER HRM - v21.3 - PARTE 1/2
✅ v21.3: logo in cache (_logo_bytes) → dashboard veloce, niente download ripetuti
✅ v21.3: icone singole, CSS compatto, traduzioni complete (dipartimento, data_sanzione)
✅ Include tutto v21.2: manuale trilingua, certificato, stati lavorativi, paga_fissa,
   trattenute legali via paghe, avvisi+Telegram, sandbox, 7 step, candidature
Richiede: Apps Script v6.1 + paghe.py v08.02+ + fpdf2 + streamlit-js-eval
"""
import sys, importlib, random, re, unicodedata
import streamlit as st
import requests
from datetime import datetime, timedelta, date
from fpdf import FPDF
try:
    import paghe as modulo_paghe
except ImportError:
    import fase6_paghe as modulo_paghe
importlib.reload(modulo_paghe)
VERSIONE = "v21.3"
LOGO_BASE = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/"
CONFIG = {"url_api_produzione": "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec",
          "url_api_test": "https://script.google.com/macros/s/AKfycbyUwzt7l_b-K7xsGX2mz1E9lPMRUZ7XptpMU8Z_4c_X-AsHd4X8haEXqlYId0buIw/exec",
          "email_ouvriers": "ouvriers@proacier.sn", "email_candidature": "candidatures@proacier.sn",
          "prefisso_codice": "THS", "user_admin": "admin", "password_admin": "admin123",
          "base_url": "https://hrm.proacier.sn"}
REG_FALLBACK = """RÈGLEMENT INTÉRIEUR - AD TRADING SA / PROACIER (synthèse)
Art.1 Horaires/pointage: postes 08h00-16h00 / 16h00-00h00; pointage obligatoire; tolérance 15 min, au-delà retenue par tranches de 30 min; absence non justifiée sous 24h = retenue + sanction.
Art.2 Sécurité/EPI: port des EPI obligatoire dans les ateliers; procédure LOTO (cadenas personnel) avant toute intervention; interdit de nettoyer/débloquer une machine en marche; accident = alerter superviseur + HSE.
Art.3 Discipline: tolérance zéro alcool, drogue, vol, violence; téléphones interdits sur les lignes; sanctions graduelles après explication du travailleur.
Art.4 Règles de vie: fumer aux zones prévues; déchets triés (DND/DIB/DIM); propreté du poste; visiteurs interdits sans autorisation.
Art.5 Paie: quinzaine avec retenues légales (CSS, IPRES, IPM, IR); avances exceptionnelles remboursées selon échéancier.
Art.6 Statut: période d'essai jusqu'à confirmation écrite; ce formulaire n'est PAS un contrat. Le certificat numéroté vaut preuve d'acceptation."""
PRIV_FALLBACK = """CONSENTEMENT AU TRAITEMENT DES DONNÉES PERSONNELLES
(Loi n° 2008-12 du 25 janvier 2008 - CDP)
Le travailleur autorise AD Trading SA / PROACIER à collecter et traiter ses données (identité, famille, contacts, numéros administratifs, aptitude médicale, données professionnelles et de paie) pour: gestion RH et paie, déclarations sociales (IPRES/CSS/IPM), sécurité, communication interne.
Destinataires: RH, Direction, organismes sociaux selon la loi. Durée: relation de travail + archivages légaux. Sécurité: accès code/PIN, sauvegardes.
Droits: accès, rectification, suppression (demande écrite au RH); saisine de la CDP. Sans consentement, enregistrement et paie impossibles.
L'acceptation électronique génère un certificat numéroté (code, date, heure, lieu, IP) valant signature."""
st.set_page_config(page_title="Proacier - Ressources Humaines", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
[data-testid="stSidebar"]{background-color:#5EA529 !important;}
[data-testid="stSidebar"] *{color:white !important;}
[data-testid="stSidebar"] button{background-color:rgba(0,0,0,0.18)!important;color:white!important;padding:0.3rem 0.5rem !important;min-height:2rem !important;}
[data-testid="stSidebar"] select{color:white!important;background-color:rgba(0,0,0,0.3)!important;}
[data-testid="stSidebar"] option{color:black!important;}
[data-testid="stSidebar"] .element-container{margin-bottom:0.2rem !important;}
[data-testid="stSidebar"] .block-container{padding-top:1rem !important;padding-bottom:0 !important;}
[data-testid="stSidebar"] img{max-height:105px !important;object-fit:contain !important;}
[data-testid="stSidebar"] hr{margin:0.35rem 0 !important;}
section.main{background-color:#0e1117 !important;min-height:100vh !important;}
[data-testid="stMainBlockContainer"]{padding-top:0.9rem !important;padding-bottom:2.5rem !important;}
[data-testid="stMain"] h1{font-size:1.8rem !important;margin:0.15rem 0 0.4rem 0 !important;}
[data-testid="stMain"] h2{font-size:1.3rem !important;margin:0.4rem 0 0.25rem 0 !important;}
[data-testid="stMain"] h3{font-size:1.02rem !important;margin:0.25rem 0 !important;}
[data-testid="stMain"] hr{margin:0.45rem 0 !important;}
[data-testid="stDownloadButton"] button{background-color:#2b4a6b !important;color:#fff !important;}
footer, #footer, [data-testid="stFooter"], .stFooter{display:none !important;}
#MainMenu{visibility:hidden !important;}
header, [data-testid="stToolbar"], div[role="toolbar"]{visibility:hidden !important;height:0 !important;}
@media (max-width:768px){.stTextInput >div >div >input,.stSelectbox >div >div >select{font-size:16px;}}
.phone-box{background-color:#5EA529;border-radius:10px;padding:10px 14px;margin:8px 0;color:white;}
.phone-box h4{margin:0 0 6px 0;color:white;font-size:15px;}
.phone-box .stTextInput >div >div >input{background-color:white;color:black;}
.phone-box .stCheckbox label{color:white;}
.tg-banner{background:#8b0000;color:#fff;border-radius:8px;padding:12px 16px;margin:10px 0;font-size:1.05rem;line-height:1.5;}
.docbtn{flex:1;text-align:center;padding:11px 0;border-radius:8px;text-decoration:none;font-size:1rem;color:#fff;display:block;}
</style>
""", unsafe_allow_html=True)
LINGUE = {"fr": 0, "it": 1, "en": 2}
T = {
 "titolo": ("🏭 PROACIER - GESTION DES RESSOURCES HUMAINES", "🏭 PROACIER - GESTIONE RISORSE UMANE", "🏭 PROACIER - HUMAN RESOURCES"),
 "titolo_sidebar": ("Gestion <br>Ressources <br>Humaines", "Gestione <br>Risorse <br>Umane", "Human <br>Resources <br>Management"),
 "sottotitolo": ("Système de Recrutement - Sénégal", "Sistema di Reclutamento - Senegal", "Recruitment System - Senegal"),
 "home": ("🏠 Accueil", "🏠 Home", "🏠 Home"), "candidatura_spontanea": ("📄 Candidature Spontanée", "📄 Candidatura Spontanea", "📄 Spontaneous Application"),
 "dashboard": ("Tableau de Bord", "Dashboard", "Dashboard"), "area_lavoratore": ("Espace Travailleur", "Spazio Lavoratore", "Worker Space"),
 "logout": ("Déconnexion", "Esci", "Logout"), "benvenuto": ("Bienvenue", "Benvenuto", "Welcome"),
 "password": ("Mot de passe", "Password", "Password"), "accedi": ("Accéder", "Accedi", "Login"),
 "codice": ("Code", "Codice", "Code"), "pin": ("PIN", "PIN", "PIN"), "codice_errato": ("Code ou PIN incorrect", "Codice o PIN errati", "Wrong code or PIN"),
 "i_miei_dati": ("Mes Données", "I Miei Dati", "My Data"), "totale_operai": ("Total Employés", "Totale Dipendenti", "Total Employees"),
 "nessun_risultato": ("Aucun résultat trouvé", "Nessun risultato", "No results found"),
 "bacheca_title": ("📢 Tableau d'affichage de la direction", "📢 Bacheca della direzione", "📢 Management notice board"),
 "fest_box_titolo": ("🗓️ Prochains jours fériés", "🗓️ Prossime festività", "🗓️ Upcoming public holidays"),
 "fest_tra": ("dans {n} jours", "tra {n} giorni", "in {n} days"), "fest_oggi": ("aujourd'hui", "oggi", "today"),
 "fest_stop": ("🏭 Prévoir l'arrêt des lignes ou l'organisation du travail.", "🏭 Prevedere la fermata delle linee o l'organizzazione del lavoro.", "🏭 Plan line stoppage or work organization."),
 "amb_title": ("🧪 Environnement de travail", "🧪 Ambiente di lavoro", "🧪 Work environment"),
 "amb_hint": ("« test » écrit UNIQUEMENT dans Proacier_SANDBOX_HRM. Par défaut: production.", "« test » scrive SOLO su Proacier_SANDBOX_HRM. Default: produzione.", "« test » writes ONLY to Proacier_SANDBOX_HRM. Default: production."),
 "admin_user": ("Nom d'utilisateur", "Nome utente", "Username"),
 "tg_obbligo": ("📲 Telegram OBLIGATOIRE pour recevoir les avis de la direction.", "📲 Telegram OBBLIGATORIO per ricevere gli avvisi della direzione.", "📲 Telegram MANDATORY to receive management notices."),
 "tg_install": ("Installer Telegram", "Installa Telegram", "Install Telegram"), "tg_join": ("Entrer dans le canal", "Entra nel canale", "Join the channel"),
 "doc_regolamento": ("Règlement intérieur", "Regolamento interno", "Internal rules"), "doc_privacy": ("Politique de confidentialité", "Privacy", "Privacy policy"),
 "mie_buste": ("🖨️ Mes fiches de paie", "🖨️ Le mie buste paga", "🖨️ My pay slips"), "gen_mia_busta": ("🖨️ Générer ma fiche", "🖨️ Genera la mia busta", "🖨️ Generate my slip"),
 "no_buste": ("ℹ️ Aucune paie enregistrée.", "ℹ️ Nessuna paga registrata.", "ℹ️ No payroll recorded."),
 "buste_period": ("Période (quinzaine)", "Periodo (quindicina)", "Period (fortnight)"),
 "home_titolo": ("📋 À quoi sert cette application?", "📋 A cosa serve questa applicazione?", "📋 What is this application for?"),
 "home_p1_t": ("Transmission de données nouveaux travailleurs", "Trasmissione dati nuovi lavoratori", "Data transmission new workers"),
 "home_p1_d": ("Formulaire en 7 étapes + PDF automatique", "Modulo in 7 fasi + PDF automatico", "7-step form + automatic PDF"),
 "home_p2_t": ("Candidatures spontanées", "Candidature spontanee", "Spontaneous applications"), "home_p2_d": ("Formulaire rapide, évaluation RH", "Modulo rapido, valutazione HR", "Quick form, HR evaluation"),
 "home_p3_t": ("Espace personnel travailleur", "Spazio personale lavoratore", "Personal worker space"), "home_p3_d": ("Accès avec code et PIN", "Accesso con codice e PIN", "Access with code and PIN"),
 "home_p4_t": ("Paiement des journaliers", "Pagamento giornalieri", "Daily workers payment"), "home_p4_d": ("Gestion présences et calcul compensi", "Gestione presenze e calcolo compensi", "Attendance and payment calculation"),
 "home_navigation": ("🚀 Navigation rapide", "🚀 Navigazione rapida", "🚀 Quick navigation"),
 "giornalieri_titolo": ("Déjà travailleur?", "Già lavoratore?", "Already a worker?"), "giornalieri_desc": ("Accédez à votre espace personnel", "Accedi al tuo spazio", "Access your space"),
 "nuovo_giornaliero_titolo": ("Nouveau / Journalier?", "Nuovo / Giornaliero?", "New / Daily worker?"),
 "nuovo_giornaliero_desc": ("Transmettez vos données (pas un contrat)", "Trasmetti i tuoi dati (non un contratto)", "Submit your data (not a contract)"),
 "login_btn": ("🔐 Connexion à mon espace", "🔐 Accedi al mio spazio", "🔐 Login to my space"), "trasmissione_btn": ("📝 Transmettre mes données", "📝 Trasmetti i miei dati", "📝 Submit my data"),
 "salva_link": ("🔖 Mes identifiants", "🔖 Le mie credenziali", "🔖 My credentials"),
 "link_hint": ("🔖 L'adresse de cette page contient maintenant ton accès: mets-la en favori.", "🔖 L'indirizzo di questa pagina ora contiene il tuo accesso: salvalo.", "🔖 This page's address now contains your access: bookmark it."),
 "copia_link_help": ("Copie ce lien et garde-le précieusement :", "Copia questo link e conservalo con cura:", "Copy this link and keep it safe:"),
 "step_1": ("1. Données Personnelles & Famille", "1. Dati Personali e Famiglia", "1. Personal Data & Family"),
 "step_2": ("2. Adresse, Documents & Services", "2. Indirizzo, Documenti e Servizi", "2. Address, Documents & Services"),
 "step_3": ("3. Expérience Professionnelle", "3. Esperienza Professionale", "3. Professional Experience"),
 "step_4": ("4. Compétences & Permis", "4. Competenze e Patente", "4. Skills & License"),
 "step_5": ("5. Informations Médicales", "5. Informazioni Mediche", "5. Medical Information"),
 "step_6": ("6. Contact d'Urgence", "6. Contatto Emergenza", "6. Emergency Contact"),
 "step_7": ("7. Vêtements & EPI", "7. Vestiario e DPI", "7. Clothing & PPE"),
 "continua": ("Continuer →", "Continua →", "Continue →"), "indietro": ("← Retour", "← Indietro", "← Back"),
 "genera_pdf": ("📄 J'accepte les conditions", "📄 Accetto le condizioni", "📄 I accept the conditions"),
 "pdf_generato": ("Enregistrement réussi!", "Registrazione riuscita!", "Registration successful!"),
 "conserva_credenziali": ("⚠️ CONSERVEZ CES IDENTIFIANTS", "⚠️ CONSERVA QUESTE CREDENZIALI", "⚠️ SAVE THESE CREDENTIALS"),
 "codice_accesso": ("Code d'accès", "Codice di accesso", "Access code"), "pin_accesso": ("PIN d'accès", "PIN di accesso", "Access PIN"),
 "scarica": ("Télécharger", "Scarica", "Download"), "ristampa_pdf": ("📄 Réimprimer PDF identifiants", "📄 Ristampa PDF credenziali", "📄 Reprint PDF credentials"),
 "checkbox_confirm": ("J'ai lu et j'accepte les conditions générales et la politique de confidentialité", "Ho letto e accetto le condizioni generali e la politica sulla privacy", "I have read and accept the general conditions and privacy policy"),
 "cocher_case": ("Veuillez cocher les cases de confirmation", "Seleziona le caselle di conferma", "Please check the confirmation boxes"),
 "errore_obbligatori": ("Veuillez remplir tous les champs obligatoires (*)", "Compila tutti i campi obbligatori (*)", "Please fill in all required fields (*)"),
 "avviso_non_contratto": ("⚠️ Ceci n'est PAS un contrat d'embauche. Uniquement une transmission de données à l'administration.", "⚠️ Questo NON è un contratto di assunzione. Solo una trasmissione di dati all'amministrazione.", "⚠️ This is NOT an employment contract. Only a data transmission to the administration."),
 "avviso_regole_aziendali": ("📋 En soumettant ce formulaire, vous acceptez les règles de l'entreprise et la politique de confidentialité de PROACIER.", "📋 Inviando questo modulo, accetti le regole aziendali e la politica sulla privacy di PROACIER.", "📋 By submitting this form, you accept the company rules and PROACIER's privacy policy."),
 "nuova_registrazione": ("🆕 Nouvelle inscription", "🆕 Nuova iscrizione", "🆕 New registration"),
 "nouvelle_candidature": ("🆕 Nouvelle candidature", "🆕 Nuova candidatura", "🆕 New application"),
 "candidatura_gia_inviata": ("ℹ️ Candidature déjà envoyée avec ces coordonnées.", "ℹ️ Candidatura già inviata con questi dati.", "ℹ️ Application already submitted with these details."),
 "cognome": ("Nom", "Cognome", "Surname"), "nome": ("Prénom(s)", "Nome", "First Name"), "data_nascita": ("Date de naissance", "Data di nascita", "Date of birth"),
 "giorno": ("Jour", "Giorno", "Day"), "mese": ("Mois", "Mese", "Month"), "anno": ("Année", "Anno", "Year"),
 "luogo_nascita": ("Lieu de naissance", "Luogo di nascita", "Place of birth"), "nazionalita": ("Nationalité", "Nazionalità", "Nationality"),
 "paese_origine": ("Pays d'origine", "Paese di origine", "Country of origin"), "sesso": ("Sexe", "Sesso", "Gender"),
 "stato_civile": ("État civil", "Stato civile", "Marital status"), "numero_mogli": ("Nombre d'épouses", "Numero mogli", "Number of wives"),
 "figli_totale": ("Nombre total d'enfants", "Numero totale figli", "Total number of children"),
 "somma_mogli": ("Somme des enfants des épouses", "Somma figli dichiarati per moglie", "Sum of children declared per wife"),
 "residenza_moglie": ("Lieu de résidence de l'épouse", "Residenza della moglie", "Wife's residence"),
 "figli_moglie": ("Enfants avec cette épouse", "Figli con questa épouse", "Children with this wife"),
 "indirizzo": ("Adresse actuelle", "Indirizzo attuale", "Current address"), "quartiere": ("Quartier/Village", "Quartiere/Villaggio", "District/Village"),
 "comune": ("Commune", "Comune", "Municipality"), "regione_senegal": ("Région", "Regione", "Region"),
 "telefono_1": ("Téléphone principal", "Telefono principale", "Main phone"), "telefono_2": ("Téléphone secondaire", "Telefono secondario", "Secondary phone"),
 "telefono_3": ("Téléphone 3", "Telefono 3", "Phone 3"), "servizi_telefono": ("Services associés", "Servizi associati", "Phone services"),
 "cni": ("N° CNI", "N° CNI", "ID Number (CNI)"), "nif": ("NIF", "NIF", "NIF"), "css": ("N° CSS", "N° CSS", "Social Security (CSS)"),
 "cmu": ("N° CMU", "N° CMU", "CMU"), "ipres": ("N° IPRES", "N° IPRES", "IPRES"),
 "nota_lavoro": ("Indiquez vos 3 dernières expériences.", "Indica le tue ultime 3 esperienze.", "Indicate your last 3 experiences."),
 "azienda": ("Entreprise", "Azienda", "Company"), "mansione": ("Fonction", "Mansione", "Position"),
 "data_inizio": ("Début", "Inizio", "Start"), "data_fine": ("Fin", "Fine", "End"), "motivo_uscita": ("Motif de départ", "Motivo uscita", "Reason for leaving"),
 "nota_competenze": ("Indiquez vos compétences principales.", "Indica le tue competenze principali.", "Indicate your main skills."),
 "categoria_competenza": ("Catégorie de compétence", "Categoria di competenza", "Skill category"), "dettaglio_competenza": ("Détails", "Dettagli", "Details"),
 "patente": ("Permis de conduire", "Patente di guida", "Driver's license"), "nota_patente": ("⚠️ Une photocopie du permis sera exigée.", "⚠️ Sarà richiesta una fotocopia della patente.", "⚠️ A photocopy of the license will be required."),
 "gruppo_sanguigno": ("Groupe sanguin", "Gruppo sanguigno", "Blood type"), "rh": ("Rh", "Rh", "Rh"),
 "allergie": ("Allergies", "Allergie", "Allergies"), "malattie": ("Maladies chroniques", "Malattie croniche", "Chronic diseases"),
 "idoneita": ("Aptitude médicale", "Idoneità medica", "Medical fitness"), "data_visita": ("Date visite", "Data visita", "Visit date"),
 "emergenza_nome": ("Contact urgence (Nom)", "Contatto emergenza (Nome)", "Emergency contact (Name)"), "emergenza_parentela": ("Lien", "Parentela", "Relationship"),
 "emergenza_tel": ("Tél urgence", "Tel emergenza", "Emergency phone"), "emergenza_indirizzo": ("Adresse urgence", "Indirizzo emergenza", "Emergency address"),
 "titolo_vestiario": ("Tailles Vêtements & EPI", "Taglie Abbigliamento e DPI", "Clothing & PPE Sizes"),
 "taglia_maglia": ("Taille t-shirt/polo", "Taglia t-shirt/polo", "T-shirt/polo size"), "taglia_pantaloni": ("Taille pantalon", "Taglia pantalone", "Pants size"),
 "taglia_scarpe": ("Pointure chaussures", "Numero scarpe", "Shoe size"), "taglia_giacca": ("Taille veste/gilet", "Taglia giacca/gilet", "Jacket/vest size"),
 "taglia_cappello": ("Taille casque/casquette", "Taglia casco/cappellino", "Helmet/cap size"), "taglia_guanti": ("Taille gants", "Taglia guanti", "Gloves size"),
 "titolo_candidatura": ("CANDIDATURE SPONTANÉE", "CANDIDATURA SPONTANEA", "SPONTANEOUS APPLICATION"),
 "sottotitolo_candidatura": ("Rejoignez l'équipe PROACIER.", "Unisciti al team PROACIER.", "Join the PROACIER team."),
 "email": ("Adresse Email", "Indirizzo Email", "Email Address"), "settore_richiesto": ("Secteur d'intérêt", "Settore di interesse", "Area of interest"),
 "mansione_richiesta": ("Poste recherché", "Ruolo richiesto", "Desired position"), "altro_specifica": ("Précisez le rôle souhaité", "Specifica il ruolo desiderato", "Specify the desired role"),
 "studi": ("Niveau d'études", "Titolo di studio", "Education level"),
 "hint_prof": ("💡 Précisez votre formation dans les notes.", "💡 Specifica la tua formazione nelle note.", "💡 Please specify your training in the notes."),
 "skills": ("Compétences / Skills", "Competenze / Skills", "Skills / Competencies"), "esperienza_anno": ("Années d'expérience", "Anni di esperienza", "Years of experience"),
 "salario_richiesto": ("Prétention salariale (FCFA)", "Retribuzione richiesta (FCFA)", "Expected salary (FCFA)"), "note": ("Notes supplémentaires", "Note aggiuntive", "Additional notes"),
 "invia_candidatura": ("📤 Envoyer ma candidature", "📤 Invia la mia candidatura", "📤 Submit my application"),
 "candidatura_inviata": ("✅ Candidature envoyée avec succès!", "✅ Candidatura inviata con successo!", "✅ Application submitted successfully!"),
 "errore_candidatura": ("Veuillez remplir Nom, Prénom, Email et Téléphone.", "Compila Cognome, Nome, Email e Telefono.", "Please fill in Surname, First Name, Email, and Phone."),
 "sezione_dati_personali": ("📋 Données Personnelles (non modifiables)", "📋 Dati Personali (non modificabili)", "📋 Personal Data (non-modifiable)"),
 "sezione_medica": ("Informations Médicales (non modifiables)", "Informazioni Mediche (non modificabili)", "Medical Information (non-modifiable)"),
 "sezione_paga": ("💰 Informations Salariales", "💰 Informazioni Salariali", "💰 Salary Information"),
 "sezione_contatti": ("📞 Coordonnées (modifiables)", "📞 Contatti (modificabili)", "📞 Contact Info (modifiable)"),
 "sezione_famille": ("👨‍👩‍ Famille (modifiable)", "👨‍👩‍ Famiglia (modificabile)", "👨‍👩‍ Family (modifiable)"),
 "sezione_vestiario": ("👕 Vêtements & EPI (modifiables)", "👕 Vestiario e DPI (modificabili)", "👕 Clothing & PPE (modifiable)"),
 "sezione_comunicazioni": ("💬 Communications & Demandes (bientôt disponible)", "💬 Comunicazioni e Richieste (prossimamente)", "💬 Communications & Requests (coming soon)"),
 "sezione_mansione": ("💼 Ma fonction", "💼 La mia mansione", "💼 My position"),
 "sezione_storico_mansioni": ("📜 Historique des fonctions", "📜 Storico mansioni", "📜 Position history"),
 "sezione_storico_paghe": ("Historique des salaires", "Storico salari", "Salary history"),
 "sezione_performance": ("Mes évaluations de performance", "Le mie valutazioni", "My performance reviews"),
 "sezione_sanzioni": ("Sanctions / Rappels", "Sanzioni / Richiami", "Sanctions / Warnings"),
 "paga_desc": ("Votre salaire est géré par l'administration.", "Il tuo salario è gestito dall'amministrazione.", "Your salary is managed by administration."),
 "paga_type": ("Type de paiement", "Tipo di pagamento", "Payment type"), "paga_amount": ("Montant", "Importo", "Amount"),
 "salva_modifiche": ("💾 Enregistrer les modifications", "💾 Salva modifiche", "💾 Save changes"),
 "modifiche_salvate": ("✅ Modifications enregistrées avec succès!", "✅ Modifiche salvate con successo!", "✅ Changes saved successfully!"),
 "errore_salvataggio": ("❌ Erreur lors de l'enregistrement.", "❌ Errore durante il salvataggio.", "❌ Error saving."),
 "saving": ("Enregistrement en cours...", "Salvataggio in corso...", "Saving..."),
 "cerca_dip": ("🔍 Rechercher (code, nom, prénom)", "🔍 Cerca (codice, cognome, nome)", "🔍 Search (code, surname, name)"),
 "turno": ("Turno", "Turno", "Shift"), "globale": ("Global (switch CONFIG)", "Globale (switch CONFIG)", "Global (CONFIG switch)"),
 "turni_assegnati": ("Postes attribués", "Turni assegnati", "Assigned shifts"), "salari_attivi": ("Salaires actifs", "Salari attivi", "Active salaries"),
 "dash_p1": ("1 - Employés & Salaires", "1 - Dipendenti & Salari", "1 - Employees & Salaries"),
 "dash_p2": ("2 - Présences & Paies", "2 - Presenze & Paghe", "2 - Attendance & Payroll"),
 "sez_admin": ("🛠️ Gestion administrative", "🛠️ Gestione amministrativa", "🛠️ Administrative management"),
 "sez_mansioni": ("Gestion des fonctions", "Gestione mansioni", "Position management"),
 "sez_sanzioni": ("Sanctions et rappels", "Sanzioni e richiami", "Sanctions and warnings"),
 "sez_performance": ("Performance Review", "Valutazioni", "Performance Reviews"),
 "storico_visite": ("Historique des visites médicales", "Storico visite mediche", "Medical visit history"),
 "nuova_visita": ("Nouvelle visite médicale", "Nuova visita medica", "New medical visit"),
 "tipo_visita": ("Type de visite", "Tipo di visita", "Visit type"), "esito": ("Résultat médical", "Esito medico", "Medical outcome"),
 "restrizioni": ("Restrictions", "Restrizioni", "Restrictions"), "prossimo_controllo": ("Prochain contrôle", "Prossimo controllo", "Next check"),
 "nessuna_visita": ("Aucune visite enregistrée", "Nessuna visita registrata", "No visits recorded"),
 "visite_scadute": ("Visites médicales à renouveler (≤30 jours ou scadute)", "Visite mediche da rinnovare (≤30 giorni o scadute)", "Medical visits to renew (≤30 days or expired)"),
 "idoneita_parziale": ("Aptitude avec restriction / inaptitude", "Idoneità con restrizione o inidoneità", "Restricted fitness / unfitness"),
 "promemoria_visita": ("⚠️ Prochain contrôle médical le ", "⚠️ Prossimo controllo medico il ", "⚠️ Next medical check on "),
 "form_hint": ("ℹ️ Remplissez tout, puis cliquez UNE fois sur « Enregistrer toutes les modifications » en bas.", "ℹ️ Compila tutto, poi clicca UNA volta su « Salva tutte le modifiche » in fondo.", "ℹ️ Fill everything, then click “Save all changes” once at the bottom."),
 "mogli_hint": ("Le total se met à jour automatiquement; ajustez manuellement seulement pour adoption/décès.", "Il totale si aggiorna da solo; ajusta manualmente solo per adozione/decesso.", "The total auto-updates; adjust manually only for adoption/death."),
 "mostra_altri": ("➕ Afficher 15 de plus", "➕ Mostrane altri 15", "➕ Show 15 more"),
 "pdf_titolo": ("FICHE D'ENREGISTREMENT - RESSOURCES HUMAINES", "SCHEDA DI REGISTRAZIONE - RISORSE UMANE", "REGISTRATION FORM - HUMAN RESOURCES"),
 "pdf_nfiche": ("N° fiche: ", "N° scheda: ", "File No.: "), "pdf_data": ("Date: ", "Data: ", "Date: "),
 "pdf_sez1": ("1. IDENTITE & FAMILLE", "1. IDENTITA' E FAMIGLIA", "1. IDENTITY & FAMILY"),
 "pdf_nom": ("Nom: ", "Cognome: ", "Surname: "), "pdf_prenoms": ("Prenom(s): ", "Nome: ", "First name(s): "),
 "pdf_ne_le": ("Ne(e) le: ", "Nato/a il: ", "Born on: "), "pdf_a": ("a: ", "a: ", "at: "),
 "pdf_nationalite": ("Nationalite: ", "Nazionalita': ", "Nationality: "), "pdf_pays": ("Pays: ", "Paese: ", "Country: "),
 "pdf_etat_civil": ("Etat civil: ", "Stato civile: ", "Marital status: "), "pdf_enfants": ("Enfants: ", "Figli: ", "Children: "),
 "pdf_epouses": ("Epouses: ", "Mogli: ", "Wives: "),
 "pdf_sez2": ("2. CONTACT & DOCUMENTS", "2. CONTATTI E DOCUMENTI", "2. CONTACT & DOCUMENTS"),
 "pdf_adresse": ("Adresse: ", "Indirizzo: ", "Address: "), "pdf_tel1": ("Tel 1: ", "Tel 1: ", "Phone 1: "), "pdf_tel2": ("Tel 2: ", "Tel 2: ", "Phone 2: "),
 "pdf_sez3": ("3. EXPERIENCE & COMPETENCES", "3. ESPERIENZA E COMPETENZE", "3. EXPERIENCE & SKILLS"),
 "pdf_poste": ("Poste: ", "Mansione: ", "Position: "), "pdf_competence": ("Competence: ", "Competenza: ", "Skill: "), "pdf_permis": ("Permis: ", "Patente: ", "License: "),
 "pdf_sez4": ("4. VETEMENTS & EPI", "4. ABBIGLIAMENTO E DPI", "4. CLOTHING & PPE"),
 "pdf_tshirt": ("T-shirt: ", "T-shirt: ", "T-shirt: "), "pdf_pantalon": ("Pantalon: ", "Pantalone: ", "Pants: "),
 "pdf_pointure": ("Pointure: ", "Numero scarpe: ", "Shoe size: "), "pdf_gilet": ("Gilet: ", "Gilet: ", "Vest: "),
 "pdf_casque": ("Casque: ", "Casco: ", "Helmet: "), "pdf_gants": ("Gants: ", "Guanti: ", "Gloves: "),
 "pdf_sez5": ("5. MEDICAL & URGENCE", "5. MEDICO E EMERGENZA", "5. MEDICAL & EMERGENCY"),
 "pdf_groupe": ("Groupe: ", "Gruppo: ", "Blood type: "), "pdf_aptitude": ("Aptitude: ", "Idoneita': ", "Fitness: "),
 "pdf_urgence": ("Urgence: ", "Emergenza: ", "Emergency: "), "pdf_tel": ("Tel: ", "Tel: ", "Phone: "),
 "pdf_certifie": ("Je certifie l'exactitude des informations et accepte les conditions.", "Certifico l'esattezza delle informazioni e accetto le condizioni.", "I certify the accuracy of the information and accept the conditions."),
 "pdf_candidat": ("CANDIDAT", "CANDIDATO", "CANDIDATE"), "pdf_employeur": ("EMPLOYEUR", "DATORE DI LAVORO", "EMPLOYER"),
 "pdf_id_titolo": ("IDENTIFIANTS DE CONNEXION", "CREDENZIALI DI ACCESSO", "LOGIN CREDENTIALS"),
 "pdf_id_desc": ("Conservez precieusement ces identifiants:", "Conserva con cura queste credenziali:", "Keep these credentials safe:"),
 "pdf_id_code": ("Code d'acces: ", "Codice di accesso: ", "Access code: "),
 "pdf_id_avviso": ("Ces identifiants sont personnels et confidentiels. Ne les partagez avec personne.", "Queste credenziali sono personali e riservate. Non condividerle.", "These credentials are personal and confidential. Do not share them."),
 "salva_tutto": ("💾 Enregistrer toutes les modifications", "💾 Salva tutte le modifiche", "💾 Save all changes"),
 "salvate_n": ("modifications enregistrées", "modifiche salvate", "changes saved"),
 "no_mansione": ("ℹ️ Aucune fonction enregistrée.", "ℹ️ Nessuna mansione registrata.", "ℹ️ No position recorded."),
 "no_storico_paghe": ("ℹ️ Aucun historique salarial.", "ℹ️ Nessuno storico salari.", "ℹ️ No salary history."),
 "no_storico_mansioni": ("ℹ️ Aucun historique des fonctions.", "ℹ️ Nessuno storico mansioni.", "ℹ️ No position history."),
 "no_performance": ("ℹ️ Aucune évaluation.", "ℹ️ Nessuna valutazione.", "ℹ️ No reviews."),
 "no_sanzioni": ("Aucune sanction", "Nessuna sanzione", "No sanctions"),
 "upgrade": ("Promotion", "Promozione", "Promotion"), "descrizione": ("Description", "Descrizione", "Description"),
 "critere": ("Critère", "Criterio", "Criterion"), "nota_1_5": ("Note (1-5)", "Voto (1-5)", "Score (1-5)"),
 "comportamento_osservato": ("Comportement observé", "Comportamento osservato", "Observed behaviour"),
 "evaluateur": ("Évaluateur", "Valutatore", "Evaluator"), "contesto": ("Contexte", "Contesto", "Context"),
 "frequenza": ("Fréquence", "Frequenza", "Frequency"), "azione_proposta": ("Action proposée", "Azione proposta", "Proposed action"),
 "regola_oro": ("Règle d'or : on n'analyse pas qui est la personne, mais comment elle se comporte dans le contexte de travail.", "Regola d'oro: non si analizza chi è, ma come si comporta in relazione al contesto lavorativo.", "Golden rule: we analyse behaviour in the work context, not the person."),
 "stato_lav": ("Statut travailleur", "Stato lavoratore", "Worker status"),
 "soc_formale": ("Société formelle (employeur)", "Società formale (datore)", "Formal employer"),
 "fine_prova": ("Fin période d'essai (GG/MM/AAAA)", "Fine prova (GG/MM/AAAA)", "End of probation (DD/MM/YYYY)"),
 "paga_fissa_lbl": ("Paie fixe mensuelle (sans pointage)", "Paga fissa mensile (senza punatura)", "Fixed monthly pay (no punching)"),
 "dash_attivi": ("Actifs", "Attivi", "Active"), "dash_archiviati": ("Archivés", "Archiviati", "Archived"),
 "prova_scad": ("Périodes d'essai à confirmer", "Prove da confermare", "Probations to confirm"),
 "avv_title": ("📢 Publier un avis (bacheca + Telegram)", "📢 Pubblica avviso (bacheca + Telegram)", "📢 Publish notice (board + Telegram)"),
 "avv_titolo": ("Titre (facultatif)", "Titolo (facoltativo)", "Title (optional)"), "avv_testo": ("Texte de l'avis", "Testo dell'avviso", "Notice text"),
 "avv_urgente": ("Urgent (rouge + Telegram)", "Urgente (rosso + Telegram)", "Urgent (red + Telegram)"),
 "avv_pub": ("📤 Publier", "📤 Pubblica", "📤 Publish"), "avv_done": ("✅ Avis publié", "✅ Avviso pubblicato", "✅ Notice published"),
 "avv_err": ("Texte requis", "Testo obbligatorio", "Text required"),
 "man_title": ("📘 Manuel des procédures", "📘 Manuale delle procedure", "📘 Procedures manual"),
 "man_search": ("🔍 Recherche (titre + texte)", "🔍 Ricerca (titolo + testo)", "🔍 Search (title + text)"),
 "man_section": ("Section", "Sezione", "Section"), "man_all": ("Toutes", "Tutte", "All"),
 "man_download": ("📥 Télécharger le manuel (PDF)", "📥 Scarica manuale (PDF)", "📥 Download manual (PDF)"),
 "man_reload": ("🔄 Recharger le manuel", "🔄 Ricarica manuale", "🔄 Reload manual"),
 "man_accept_box": ("J'ai lu et j'accepte le Manuel des procédures", "Ho letto e accetto il Manuale delle procedure", "I have read and accept the Procedures Manual"),
 "man_updated": ("📘 Manuel mis à jour : veuillez le relire et l'accepter pour continuer.", "📘 Manuale aggiornato: rileggilo e accettalo per continuare.", "📘 Manual updated: please re-read and accept to continue."),
 "man_vuoto": ("⚠️ Manuel introuvable ou vide. Vérifiez les onglets MANUAL_FR/EN/IT et MANUAL_CONFIG (noms exacts, sans « Copy of »).", "⚠️ Manuale non trovato o vuoto. Verifica i tab MANUAL_FR/EN/IT e MANUAL_CONFIG (nomi esatti, senza « Copy of »).", "⚠️ Manual not found or empty. Check tabs MANUAL_FR/EN/IT and MANUAL_CONFIG (exact names, no « Copy of »)."),
 "man_sommaire": ("SOMMAIRE", "SOMMARIO", "CONTENTS"),
 "man_index": ("Cliquez sur un chapitre pour le filtrer", "Clicca su un capitolo per filtrarlo", "Click a chapter to filter it"),
 "man_apri": ("📘 Ouvrir le manuel", "📘 Apri il manuale", "📘 Open the manual"),
 "man_remis": ("Le Manuel des procédures m'a été remis et expliqué par l'administration avant l'inscription.", "Il Manuale delle procedure mi è stato consegnato e spiegato dall'amministrazione prima dell'iscrizione.", "The Procedures Manual was given and explained to me by the administration before registration."),
 "motivo_cambio": ("Motif", "Motivo", "Reason"), "tipo_sanzione": ("Type de sanction", "Tipo sanzione", "Sanction type"),
 "gravita": ("Gravité", "Gravità", "Severity"), "dipartimento": ("Département", "Dipartimento", "Department"),
 "data_sanzione": ("Date de la sanction", "Data sanzione", "Sanction date"),
 "reg_officiali": ("Enregistrements officiels (marque temporelle fixée)", "Registrazioni ufficiali (marca temporale fissa)", "Official registrations (fixed timestamp)"),
 "cert_titolo": ("CERTIFICAT D'ENREGISTREMENT", "CERTIFICATO DI REGISTRAZIONE", "REGISTRATION CERTIFICATE"),
 "cert_ufficiale": ("DOCUMENT OFFICIEL", "DOCUMENTO UFFICIALE", "OFFICIAL DOCUMENT"),
 "cert_copia": ("COPIE DE TRAVAIL - NON OFFICIELLE", "COPIA DI LAVORO - NON UFFICIALE", "WORKING COPY - NOT OFFICIAL"),
}
def get_testo(chiave, lingua="fr"):
    t = T.get(chiave)
    return chiave if not t else t[LINGUE.get(lingua, 0)]
OPZ = {
 "sesso": [("M", "Masculin", "Maschile", "Male"), ("F", "Féminin", "Femminile", "Female")],
 "stato_civile": [("celibe", "Célibataire", "Celibe/Nubile", "Single"), ("coniugato", "Marié(e)", "Coniugato/a", "Married"), ("divorziato", "Divorcé(e)", "Divorziato/a", "Divorced"), ("vedovo", "Veuf/Veuve", "Vedovo/a", "Widowed")],
 "idoneita": [("apte", "Apte", "Apto", "Fit"), ("restriction", "Apte avec restriction", "Apto con restrizioni", "Fit with restrictions"), ("inapte", "Inapte", "Inapto", "Unfit")],
 "categoria": [("edilizia", "Bâtiment", "Edilizia", "Construction"), ("contabilita", "Comptabilité", "Contabilità", "Accounting"), ("meccanica", "Mécanique", "Meccanica", "Mechanics"), ("elettrico", "Électricité", "Elettrico", "Electrical"), ("agricoltura", "Agriculture", "Agricoltura", "Agriculture"), ("altro_cat", "Autre", "Altro", "Other")],
 "studi": [("media", "École moyenne", "Licenza media", "Middle school"), ("diploma", "Baccalauréat / Diplôme", "Diploma", "High school / Diploma"), ("laurea", "Université / Licence", "Laurea", "University / Degree"), ("prof", "Formation professionnelle", "Formazione professionale", "Vocational training")],
 "paesi": [("SN", "Sénégal", "Senegal", "Senegal"), ("ML", "Mali", "Mali", "Mali"), ("BF", "Burkina Faso", "Burkina Faso", "Burkina Faso"), ("SL", "Sierra Leone", "Sierra Leone", "Sierra Leone"), ("GN", "Guinée", "Guinea", "Guinea"), ("GM", "Gambie", "Gambia", "Gambia"), ("AUTRE", "Autre pays", "Altro paese", "Other country")],
 "tipo_visita": [("assunzione", "Visite d'embauche", "Visita di assunzione", "Hiring visit"), ("periodica", "Visite périodique", "Visita periodica", "Periodic visit"), ("straordinaria", "Visite extraordinaire", "Visita straordinaria", "Extraordinary visit")],
 "tipo_paga": [("giornaliero", "Journalier", "Giornaliero", "Daily"), ("orario", "Horaire", "Orario", "Hourly"), ("mensile", "Mensuel", "Mensile", "Monthly")],
 "tipo_sanzione": [("richiamo_verbale", "Rappel verbal", "Richiamo verbale", "Verbal warning"), ("richiamo_scritto", "Rappel écrit", "Richiamo scritto", "Written warning"), ("sospensione", "Suspension", "Sospensione", "Suspension"), ("altro", "Autre", "Altro", "Other")],
 "gravita": [("lieve", "Légère", "Lieve", "Minor"), ("media", "Moyenne", "Media", "Moderate"), ("grave", "Grave", "Grave", "Severe")],
 "motivo_cambio": [("assunzione", "Embauche", "Assunzione", "Hiring"), ("promozione", "Promotion", "Promozione", "Promotion"), ("trasferimento", "Transfert", "Trasferimento", "Transfer"), ("reintegro", "Réintégration", "Reintegro", "Reinstatement"), ("altro", "Autre", "Altro", "Other")],
 "criteri_perf": [("puntualita", "Ponctualité", "Puntualità", "Punctuality"), ("qualita", "Qualité du travail", "Qualità del lavoro", "Work quality"), ("collaborazione", "Collaboration", "Collaborazione", "Collaboration"), ("sicurezza", "Sécurité", "Sicurezza", "Safety"), ("produttivita", "Productivité", "Produttività", "Productivity"), ("leadership", "Leadership", "Leadership", "Leadership"), ("affidabilita", "Fiabilité", "Affidabilità", "Reliability"), ("iniziativa", "Initiative", "Iniziativa", "Initiative")],
 "stato_lavorativo": [("prova", "Période d'essai", "Prova", "Probation"), ("assunto", "Embauché", "Assunto", "Hired"), ("esterno", "Journalier externe", "Esterno", "External"), ("dimissionario", "Démissionnaire", "Dimissionario", "Resigned"), ("licenziato", "Licencié", "Licenziato", "Dismissed")],
}
def etichetta(tipo, valore, lingua="fr"):
    v = s_str(valore)
    if not v: return ""
    for o in OPZ.get(tipo, []):
        if v in o: return o[LINGUE.get(lingua, 0) + 1]
    return v
def select_canonico(tipo, lingua, label, key, saved=None):
    codes = [o[0] for o in OPZ[tipo]]
    idx = 0
    sv = s_str(saved)
    if sv:
        if sv in codes: idx = codes.index(sv)
        else:
            for o in OPZ[tipo]:
                if sv in o[1:]: idx = codes.index(o[0]); break
    return st.selectbox(label, codes, index=idx, format_func=lambda c: etichetta(tipo, c, lingua), key=key)
def norm_idoneita(v):
    v = s_str(v)
    if v in ("apte", "Apte", "Apto", "Fit"): return "apte"
    if v in ("restriction", "Apte avec restriction", "Apto con restrizioni", "Fit with restrictions"): return "restriction"
    if v in ("inapte", "Inapte", "Inapto", "Unfit"): return "inapte"
    return v
def data_ord(s):
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s_str(s))
    if not m: return None
    d, mo, y = map(int, m.groups())
    return (y, mo, d)
def _norm_acc(s):
    return unicodedata.normalize("NFD", str(s or "").lower()).encode("ascii", "ignore").decode()
_PDF_MAP = {"→": "->", "–": "-", "—": "-", "•": "-", "…": "...", "’": "'", "‘": "'", "“": '"', "”": '"', "≤": "<=", "≥": ">=", "€": "EUR", "Œ": "OE", "œ": "oe", "⚠": "!", "✅": "[OK]", "⭐": "*", "📈": "^", "⛔": "X", "➡": "->", "\xa0": " ", "★": "*", "☆": "*"}
def _pdf_safe(s):
    out = []
    for ch in str(s or ""):
        if ch in _PDF_MAP: out.append(_PDF_MAP[ch]); continue
        try:
            ch.encode("latin-1"); out.append(ch)
        except Exception: out.append("?")
    return "".join(out)
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
def s_str(v):
    if v is None: return ""
    s = str(v)
    return "" if s in ("nan", "None", "#ERROR!") else s.strip()
def s_int(v):
    try: return int(float(s_str(v) or 0))
    except Exception: return 0
def formatta_data(v):
    s = s_str(v)
    if not s: return ""
    if "T" in s: s = s.split("T")[0]
    p = s.split("-")
    if len(p) == 3: return f"{p[2]}/{p[1]}/{p[0]}"
    return s
def parse_mogli(s):
    out = []
    s = s_str(s)
    if not s: return out
    for c in [c.strip() for c in s.split("|") if c.strip()]:
        m = re.search(r"(\d+)\s*enfants?", c)
        fig = int(m.group(1)) if m else 0
        res = re.sub(r"^Épouse\s*\d+\s*:\s*", "", c)
        res = re.sub(r"\s*(\d+\s*enfants?)\s*$", "", res).strip()
        out.append({"res": res, "fig": fig})
    return out
def servizi_di(r):
    parti = []
    for n in (1, 2, 3):
        tel = s_str(r.get(f"telefono_{n}"))
        sv = s_str(r.get(f"servizi_tel{n}"))
        if tel: parti.append(f"{tel}" + (f" ({sv})" if sv else ""))
    return " / ".join(parti)
def _logo_url(chiave, default):
    f = cfg_get(chiave, default)
    return f if f.startswith("http") else LOGO_BASE + f
_LOGO_CACHE = {}
def _logo_bytes(chiave, default):
    url = _logo_url(chiave, default)
    if url not in _LOGO_CACHE:
        try:
            r = requests.get(url, timeout=30)
            _LOGO_CACHE[url] = r.content if (r.status_code == 200 and r.content) else b""
        except Exception:
            _LOGO_CACHE[url] = b""
    return _LOGO_CACHE[url]
def genera_credenziali():
    anno = datetime.now().year
    prefisso = CONFIG["prefisso_codice"]
    _, recs = leggi_foglio("DIPENDENTI", force=True)
    pattern = re.compile(r"^" + re.escape(prefisso) + r"-\d{4}-(\d+)$", re.I)
    max_seq = 0
    codici, pins = set(), set()
    for r in recs:
        cod = s_str(r.get("codice")).upper()
        if cod:
            codici.add(cod)
            m = pattern.match(cod)
            if m: max_seq = max(max_seq, int(m.group(1)))
        p = s_str(r.get("pin"))
        if p: pins.add(p)
    seq = max_seq + 1
    codice = f"{prefisso}-{anno}-{seq:04d}"
    while codice.upper() in codici:
        seq += 1
        codice = f"{prefisso}-{anno}-{seq:04d}"
    pin = str(random.randint(1000, 9999))
    while pin in pins: pin = str(random.randint(1000, 9999))
    return codice, pin
def _post_json(payload):
    try:
        r = requests.post(CONFIG["url_api"], json=payload, timeout=90)
        if r.status_code == 200:
            try:
                j = r.json()
                if isinstance(j, dict):
                    if j.get("status") == "success": return True, "ok"
                    return False, j.get("message", "Erreur serveur")
                return False, "Réponse inattendue"
            except Exception: return False, "Réponse non JSON"
        return False, f"HTTP {r.status_code}"
    except Exception as e: return False, str(e)
def _svuota_cache(nome_foglio=None):
    cache = st.session_state.get("_cache", {})
    if nome_foglio: cache.pop(nome_foglio, None)
    cache.pop("_admin", None)
    st.session_state["_cache"] = cache
def leggi_foglio(nome_foglio, force=False):
    cache = st.session_state.get("_cache", {})
    if not force and nome_foglio in cache:
        ts, h, recs = cache[nome_foglio]
        if (datetime.now() - ts).total_seconds() < 120: return h, recs
    data = None
    try:
        r = requests.post(CONFIG["url_api"], json={"sheet": nome_foglio, "action": "read"}, timeout=60)
        if r.status_code == 200:
            j = r.json()
            if isinstance(j, list) and j: data = j
    except Exception: data = None
    if data is None:
        try:
            r2 = requests.get(CONFIG["url_api"], params={"sheet": nome_foglio}, timeout=60)
            j2 = r2.json()
            if isinstance(j2, list) and j2: data = j2
        except Exception as e:
            st.error(f"Erreur de connexion: {e}")
            return [], []
    if not data: return [], []
    headers = [str(h).strip() for h in data[0]]
    records = [dict(zip(headers, row)) for row in data[1:]]
    cache[nome_foglio] = (datetime.now(), headers, records)
    st.session_state["_cache"] = cache
    return headers, records
def leggi_admin(force=False):
    cache = st.session_state.get("_cache", {})
    if not force and "_admin" in cache:
        ts, bundle = cache["_admin"]
        if (datetime.now() - ts).total_seconds() < 120: return bundle
    bundle = None
    try:
        r = requests.post(CONFIG["url_api"], json={"action": "read_all",
            "sheets": ["DIPENDENTI", "SALARI", "TURNI", "VISITE_MEDICHE", "STORICO_MANSIONI", "STORICO_SANZIONI", "PERFORMANCE_REVIEW"]}, timeout=90)
        if r.status_code == 200:
            j = r.json()
            if isinstance(j, dict) and "DIPENDENTI" in j:
                bundle = {}
                for name, rows in j.items():
                    if isinstance(rows, list) and rows:
                        headers = [str(h).strip() for h in rows[0]]
                        bundle[name] = [dict(zip(headers, row)) for row in rows[1:]]
                    else: bundle[name] = []
    except Exception: bundle = None
    if bundle is None:
        bundle = {}
        for name in ("DIPENDENTI", "SALARI", "TURNI", "VISITE_MEDICHE", "STORICO_MANSIONI", "STORICO_SANZIONI", "PERFORMANCE_REVIEW"):
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
                return True, "ok (vérifié)"
        except Exception: pass
    return ok, msg
def salva_append_many(nome_foglio, rows):
    if not rows: return True, "ok"
    ok, msg = _post_json({"sheet": nome_foglio, "action": "append", "rows": rows})
    if ok: _svuota_cache(nome_foglio)
    return ok, msg
def salva_update(nome_foglio, row_index, row):
    ok, msg = _post_json({"sheet": nome_foglio, "action": "update", "rowIndex": row_index, "row": row})
    if ok: _svuota_cache(nome_foglio)
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
        if (s_str(r.get("cognome")).lower() == s_str(cognome).lower() and s_str(r.get("nome")).lower() == s_str(nome).lower()
            and s_str(r.get("email")).lower() == s_str(email).lower() and s_str(r.get("telefono")) == s_str(tel)
            and s_str(r.get("data_candidatura")).startswith(oggi)):
            return r
    return None
def cfg_get(key, default=""):
    try: _, recs = leggi_foglio("CONFIG")
    except Exception: return default
    for r in recs:
        if s_str(r.get("chiave")).strip().lower() == key.lower():
            return s_str(r.get("valore")) or default
    return default
def cfg_set(key, value):
    _, recs = leggi_foglio("CONFIG", force=True)
    for i, r in enumerate(recs):
        if s_str(r.get("chiave")).lower() == key.lower():
            return salva_update("CONFIG", i, {"valore": value})
    return salva_append("CONFIG", {"chiave": key, "valore": value, "note": ""})
def testo_legale(chiave, default):
    try: _, recs = leggi_foglio("TESTI_LEGALI")
    except Exception: return default
    parti = [s_str(r.get("testo")) for r in recs if s_str(r.get("chiave")).lower() == chiave.lower() and s_str(r.get("testo"))]
    return "\n".join(parti) if parti else default
def azienda_info():
    cache = st.session_state.get("_azienda")
    if cache: return cache
    out = {"nome": "AD Trading S.A.", "indirizzo": "Cité Asecna Ouakam N° A72 - 12300 DAKAR (SÉNÉGAL)",
           "tel": "+221 33 9133312", "email": "info@adtrading.sn",
           "fisc": "NINEA: 004250180 2Y3 - RCCM: SN.DKR.2007-B-5254 - Shared Capital: 100.000.000 FCFA"}
    for k in ("azienda_nome", "azienda_indirizzo", "azienda_tel", "azienda_email"):
        v = cfg_get(k)
        if v: out[k.split("_", 1)[1]] = v
    st.session_state["_azienda"] = out
    return out
def footer():
    anno = datetime.now().year
    st.markdown("---")
    st.markdown(f'<div style="text-align:center;padding:2rem 0 1rem 0;color:#9aa0a6;font-size:0.8rem;">'
                f'Proacier - tel. +221 33 913 33 12 - <span>info@proacier.sn</span><br><br><br><br><br><br>'
                f'- powered by Lehev Ltd - © Copyright for Lehev Ltd. {anno} - All rights reserved -</div>', unsafe_allow_html=True)
def promemoria_festivita(lingua, consiglio=False):
    try: _, recs = leggi_foglio("CONFIG")
    except Exception: return
    giorni_limite = 10
    fest = []
    for r in recs:
        k = s_str(r.get("chiave")).lower().replace(" ", "_")
        v = s_str(r.get("valore"))
        if k == "promemoria_festivita_giorni_prima":
            try:
                f = int(float(v))
                if f > 0: giorni_limite = f
            except Exception: pass
        elif k.startswith("festivo_"):
            try:
                y, m, g = k[8:].split("-")
                fest.append((date(int(y), int(m), int(g)), v or "Férié"))
            except Exception: pass
    oggi = date.today()
    imminenti = sorted([(d, n) for (d, n) in fest if 0 <= (d - oggi).days <= giorni_limite])
    if not imminenti: return
    righe = []
    for d, n in imminenti:
        delta = (d - oggi).days
        quando = get_testo("fest_oggi", lingua) if delta == 0 else get_testo("fest_tra", lingua).format(n=delta)
        righe.append(f"- {n} — {d.strftime('%d/%m/%Y')} ({quando})")
    msg = get_testo("fest_box_titolo", lingua) + "\n\n" + "\n".join(righe)
    if consiglio: msg += "\n\n" + get_testo("fest_stop", lingua)
    st.info(msg)
def invia_telegram(testo):
    tok = cfg_get("telegram_bot_token")
    chat = cfg_get("telegram_chat_id")
    if not tok or not chat: return False
    try:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendMessage", json={"chat_id": chat, "text": testo}, timeout=20)
        return r.status_code == 200
    except Exception: return False
def rileva_ip_luogo():
    ip, luogo = "", ""
    try:
        from streamlit_js_eval import streamlit_js_eval, get_geolocation
        try:
            r = streamlit_js_eval(js_expr="(async()=>{try{const j=await (await fetch('https://api.ipify.org?format=json')).json();return j.ip}catch(e){return ''}})()")
            if isinstance(r, str): ip = r
            elif isinstance(r, dict): ip = r.get("ip", "")
        except Exception: pass
        try:
            g = get_geolocation()
            if g and g.get("latitude") is not None:
                luogo = f"{float(g['latitude']):.3f}, {float(g['longitude']):.3f}"
        except Exception: pass
    except Exception: pass
    return ip, luogo
def genera_cert_codice(codice):
    seq = s_int(cfg_get("cert_seq", "0")) + 1
    cfg_set("cert_seq", str(seq))
    rnd = random.randint(100, 999)
    return f"CERT-{codice}-{datetime.now().strftime('%Y%m%d')}-{seq:04d}-{rnd}", seq
	# ------------------------- MANUALE OPERATIVO -------------------------
def leggi_manual_config(force=False):
    key = "_manconf"
    if not force and key in st.session_state: return st.session_state[key]
    out = {"params": {}, "machines": []}
    try: _, recs = leggi_foglio("MANUAL_CONFIG", force=force)
    except Exception: recs = []
    for r in recs:
        t = s_str(r.get("type")).upper(); code = s_str(r.get("code"))
        if not code: continue
        if t == "PARAM" and s_str(r.get("statut")).lower() == "actif":
            out["params"][code] = s_str(r.get("quantite"))
        elif t == "MACHINE" and not code.upper().startswith("NEW"):
            out["machines"].append(r)
    st.session_state[key] = out
    return out
def _parc_machines(lingua, conf):
    col = {"fr": "fr", "it": "it", "en": "en"}.get(lingua, "fr")
    return "\n".join([f"- {s_str(m.get('code'))} x{s_str(m.get('quantite'))} ({s_str(m.get('statut'))}) : {s_str(m.get(col))}" for m in conf["machines"]])
def _apply_placeholders(texto, lingua, conf):
    texto = texto.replace("{{PARC_MACHINES}}", _parc_machines(lingua, conf))
    for code, val in conf["params"].items():
        texto = texto.replace("{{%s}}" % code, val)
    return texto
def _meta_get(meta, keys):
    for k in keys:
        for mk, mv in meta.items():
            if k in mk: return mv
    return ""
def leggi_manuale(lingua, force=False):
    sheet = {"fr": "MANUAL_FR", "en": "MANUAL_EN", "it": "MANUAL_IT"}.get(lingua, "MANUAL_FR")
    ck = "_manual_" + lingua
    if not force and ck in st.session_state: return st.session_state[ck]
    conf = leggi_manual_config(force=force)
    meta, sections, order = {}, {}, []
    try: _, recs = leggi_foglio(sheet, force=force)
    except Exception: recs = []
    for r in recs:
        sez, tit, tex = s_str(r.get("sezione")), s_str(r.get("titolo")), s_str(r.get("testo"))
        if not sez: continue
        pref = sez.split(".")[0].strip()
        if pref == "00":
            meta[_norm_acc(tit)] = tex; continue
        if sez not in sections:
            sections[sez] = {"id": sez, "pref": int(pref) if pref.isdigit() else 99, "paras": []}
            order.append(sez)
        sections[sez]["paras"].append({"title": tit, "text": _apply_placeholders(tex, lingua, conf)})
    secs = sorted([sections[s] for s in order], key=lambda x: x["pref"])
    out = {"meta": meta, "sections": secs}
    if secs: st.session_state[ck] = out
    return out
def manuale_versione():
    man = leggi_manuale("fr")
    return cfg_get("manuale_versione") or _meta_get(man["meta"], ["version du manuel", "manual version", "versione del manuale"]) or "1"
def genera_pdf_manuale(lingua):
    man = leggi_manuale(lingua)
    if not man["sections"]: raise ValueError("Manuale vuoto")
    az = azienda_info()
    pdf = FPDF(); pdf.set_auto_page_break(True, 15); pdf.set_margins(10, 10)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12); pdf.set_x(10); pdf.cell(0, 8, _pdf_safe(az.get("nome", "")), 0, 1, "C")
    titolo = _meta_get(man["meta"], ["titre du manuel", "title of the manual", "titolo del manuale"]) or "Manuel des Procédures"
    pdf.set_font("Helvetica", "B", 14); pdf.set_x(10); pdf.multi_cell(0, 7, _pdf_safe(titolo), align="C")
    pdf.set_font("Helvetica", "", 9); dat = _meta_get(man["meta"], ["date de la version", "version date", "data della versione"])
    pdf.set_x(10); pdf.cell(0, 6, _pdf_safe(f"Version {manuale_versione()} - {dat}"), 0, 1, "C"); pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10); pdf.set_x(10); pdf.cell(0, 7, _pdf_safe(get_testo("man_sommaire", lingua)), 0, 1, "L")
    pdf.set_font("Helvetica", "", 9)
    for s in man["sections"]:
        if s["pref"] <= 2: continue
        pdf.set_x(10); pdf.cell(0, 6, _pdf_safe("- " + s["id"]), 0, 1, "L")
    for s in man["sections"]:
        if s["pref"] == 0: continue
        pdf.add_page(); pdf.set_font("Helvetica", "B", 11); pdf.set_x(10); pdf.cell(0, 7, _pdf_safe(s["id"]), 0, 1, "L")
        for p in s["paras"]:
            try:
                pdf.set_font("Helvetica", "B", 9); pdf.set_x(10); pdf.multi_cell(0, 5, _pdf_safe(p["title"]))
                pdf.set_font("Helvetica", "", 9); pdf.set_x(10); pdf.multi_cell(0, 5, _pdf_safe(p["text"])); pdf.ln(2)
            except Exception: continue
    out = pdf.output(dest="S")
    return out.encode("latin-1", "ignore") if isinstance(out, str) else bytes(out)
def pagina_manuale(lingua):
    st.title(get_testo("man_title", lingua))
    man = leggi_manuale(lingua)
    if not man["sections"]:
        st.error(get_testo("man_vuoto", lingua)); return
    st.caption(f"v{manuale_versione()} — {_meta_get(man['meta'], ['date de la version', 'version date', 'data della versione'])}")
    q = st.text_input(get_testo("man_search", lingua), key="pgman_q")
    secs = [s for s in man["sections"] if s["pref"] >= 3]
    opts = ["*"] + [s["id"] for s in secs]
    if st.session_state.get("pgman_sel") not in opts: st.session_state["pgman_sel"] = "*"
    b1, b2, b3 = st.columns([2, 1, 1])
    if b1.button(get_testo("man_download", lingua), type="primary", key="pgman_pdf"):
        try:
            st.session_state["pgman_bytes"] = genera_pdf_manuale(lingua); st.session_state["pgman_lang"] = lingua
        except Exception as e: st.error(f"PDF: {e}")
    if b2.button(get_testo("man_reload", lingua), key="pgman_rl"):
        for k in list(st.session_state.keys()):
            if k.startswith("_manual_") or k == "_manconf": st.session_state.pop(k, None)
        st.rerun()
    if b3.button(get_testo("man_all", lingua), key="pgman_all"): st.session_state["pgman_sel"] = "*"
    if st.session_state.get("pgman_bytes"):
        st.download_button("📥 PDF", data=st.session_state["pgman_bytes"], file_name=f"Manuel_Proacier_{st.session_state.get('pgman_lang', lingua)}.pdf", mime="application/pdf", key="pgman_dl", use_container_width=True)
    st.caption(get_testo("man_index", lingua))
    ic = st.columns(3)
    for n, s in enumerate(secs):
        if ic[n % 3].button(s["id"], key=f"pgman_toc_{n}", use_container_width=True):
            st.session_state["pgman_sel"] = s["id"]
    sel = st.session_state["pgman_sel"]; st.markdown("---")
    nq = _norm_acc(q)
    for s in man["sections"]:
        if s["pref"] == 0: continue
        if sel != "*" and s["id"] != sel: continue
        paras = [p for p in s["paras"] if not nq or nq in _norm_acc(p["title"] + " " + p["text"])]
        if nq and not paras: continue
        with st.expander(s["id"], expanded=(sel != "*" or bool(nq))):
            for p in paras:
                st.markdown(f"**{p['title']}**"); st.write(p["text"])
def pagina_documento(doc, lingua):
    st.title("AD Trading SA / Proacier")
    if doc == "reglement":
        st.subheader("RÈGLEMENT INTÉRIEUR & RÈGLES GÉNÉRALES DE L'USINE")
        st.markdown(_pdf_safe(testo_legale("reglement_interieur", REG_FALLBACK)).replace("\n", "\n\n"))
    else:
        st.subheader("POLITIQUE DE CONFIDENTIALITÉ / CONSENTEMENT")
        st.markdown(_pdf_safe(testo_legale("consentement_privacy", PRIV_FALLBACK)).replace("\n", "\n\n"))
# ------------------------- PDF LAVORATORE + CERTIFICATO -------------------------
class PDFProacier(FPDF):
    titolo = "FICHE D'ENREGISTREMENT - RESSOURCES HUMAINES"
    azienda = {}
    cert_code = ""
    def header(self):
        if self.page_no() == 1: return
        self.set_font("Helvetica", "B", 11); self.cell(0, 8, self.titolo, 0, 1, "C"); self.ln(2)
    def footer(self):
        az = self.azienda or {}
        self.set_y(-18); self.set_font("Helvetica", "", 7)
        self.cell(0, 4, f"{az.get('nome','AD Trading S.A.')} - {az.get('indirizzo','')}", 0, 1, "L")
        self.cell(90, 4, self.cert_code or "", 0, 0, "L")
        self.cell(60, 4, f"tel. {az.get('tel','')} - {az.get('email','')}", 0, 0, "L")
        self.cell(0, 4, f"Pag. {self.page_no()}", 0, 1, "R")
    def sezione(self, titolo):
        self.set_font("Helvetica", "B", 10); self.set_fill_color(217, 225, 242); self.cell(0, 6, titolo, 0, 1, "C", True); self.ln(1)
    def campo(self, et, val):
        self.set_font("Helvetica", "B", 8); self.cell(60, 5, et, 0, 0)
        self.set_font("Helvetica", "", 8); self.cell(0, 5, _pdf_safe(s_str(val) or "___"), 0, 1)
    def campo_doppio(self, e1, v1, e2, v2):
        self.set_font("Helvetica", "B", 8); self.cell(50, 5, e1, 0, 0)
        self.set_font("Helvetica", "", 8); self.cell(45, 5, _pdf_safe(s_str(v1) or ""), 0, 0)
        self.set_font("Helvetica", "B", 8); self.cell(50, 5, e2, 0, 0)
        self.set_font("Helvetica", "", 8); self.cell(0, 5, _pdf_safe(s_str(v2) or ""), 0, 1)
def genera_pdf_lavoratore(d, lingua="fr"):
    az = azienda_info()
    pdf = PDFProacier(); pdf.azienda = az; pdf.titolo = get_testo("pdf_titolo", lingua)
    pdf.cert_code = s_str(d.get("cert_codice"))
    doc_ts = s_str(d.get("doc_timestamp")) or datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.add_page()
    lb = _logo_bytes("logo_azienda", "adtrading.png")
    if lb: pdf.image(lb, x=10, y=8, w=30)
    pdf.set_xy(110, 34); pdf.set_font("Helvetica", "B", 9); pdf.cell(0, 5, s_str(d.get("codice")), 0, 1, "R")
    pref = "M. " if s_str(d.get("sesso")) == "M" else ("Mme " if s_str(d.get("sesso")) == "F" else "")
    pdf.cell(0, 5, _pdf_safe(f"{pref}{s_str(d.get('nome'))} {s_str(d.get('cognome'))}".strip()), 0, 1, "R")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 4, _pdf_safe(s_str(d.get("indirizzo"))), 0, 1, "R")
    pdf.cell(0, 4, _pdf_safe(f"{s_str(d.get('comune'))} {s_str(d.get('quartiere'))}".strip()), 0, 1, "R")
    pdf.set_xy(10, 62); pdf.set_font("Helvetica", "B", 12); pdf.cell(0, 8, get_testo("pdf_titolo", lingua), 0, 1, "C")
    pdf.set_xy(10, 72); pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 5, f"{get_testo('pdf_nfiche', lingua)} {s_str(d.get('codice'))}", 0, 0)
    pdf.cell(0, 5, f"{get_testo('pdf_data', lingua)} {doc_ts}", 0, 1, "R"); pdf.ln(2)
    pdf.sezione(get_testo("pdf_sez1", lingua))
    pdf.campo_doppio(get_testo("pdf_nom", lingua), d.get("cognome"), get_testo("pdf_prenoms", lingua), d.get("nome"))
    pdf.campo_doppio(get_testo("pdf_ne_le", lingua), formatta_data(d.get("data_nascita")), get_testo("pdf_a", lingua), d.get("luogo_nascita"))
    pdf.campo_doppio(get_testo("pdf_nationalite", lingua), etichetta("paesi", d.get("nazionalita"), lingua), get_testo("pdf_pays", lingua), etichetta("paesi", d.get("paese_origine"), lingua))
    pdf.campo_doppio(get_testo("pdf_etat_civil", lingua), etichetta("stato_civile", d.get("stato_civile"), lingua), get_testo("pdf_enfants", lingua), d.get("figli_totale"))
    pdf.campo_doppio(get_testo("pdf_epouses", lingua), d.get("numero_mogli"), get_testo("pdf_enfants", lingua), d.get("figli_totale"))
    if s_int(d.get("numero_mogli")) > 0:
        pdf.set_font("Helvetica", "B", 8); pdf.cell(60, 5, get_testo("pdf_epouses", lingua), 0, 0)
        pdf.set_font("Helvetica", "", 8); pdf.set_x(10); pdf.multi_cell(0, 4, _pdf_safe(s_str(d.get("dettagli_mogli")))); pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez2", lingua))
    pdf.campo(get_testo("pdf_adresse", lingua), f"{s_str(d.get('indirizzo'))}, {s_str(d.get('quartiere'))}, {s_str(d.get('regione_senegal'))}")
    pdf.campo_doppio(get_testo("pdf_tel1", lingua), d.get("telefono_1"), get_testo("pdf_tel2", lingua), d.get("telefono_2"))
    pdf.campo(get_testo("servizi_telefono", lingua), servizi_di(d))
    pdf.campo_doppio("CNI: ", d.get("cni"), "CSS: ", d.get("css"))
    pdf.campo_doppio("NIF: ", d.get("nif"), "IPRES: ", d.get("ipres")); pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez3", lingua))
    pdf.campo(get_testo("pdf_poste", lingua), d.get("mansione_1"))
    pdf.campo(get_testo("pdf_competence", lingua), f"{etichetta('categoria', d.get('categoria_competenza'), lingua)} - {s_str(d.get('dettaglio_competenza'))}")
    pdf.campo(get_testo("pdf_permis", lingua), d.get("patente")); pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez4", lingua))
    pdf.campo_doppio(get_testo("pdf_tshirt", lingua), d.get("taglia_maglia"), get_testo("pdf_pantalon", lingua), d.get("taglia_pantaloni"))
    pdf.campo_doppio(get_testo("pdf_pointure", lingua), d.get("taglia_scarpe"), get_testo("pdf_gilet", lingua), d.get("taglia_giacca"))
    pdf.campo_doppio(get_testo("pdf_casque", lingua), d.get("taglia_cappello"), get_testo("pdf_gants", lingua), d.get("taglia_guanti")); pdf.ln(1)
    pdf.sezione(get_testo("pdf_sez5", lingua))
    pdf.campo_doppio(get_testo("pdf_groupe", lingua), f"{s_str(d.get('gruppo_sanguigno'))} {s_str(d.get('rh'))}", get_testo("pdf_aptitude", lingua), etichetta("idoneita", d.get("idoneita"), lingua))
    pdf.campo_doppio(get_testo("pdf_urgence", lingua), d.get("emergenza_nome"), get_testo("pdf_tel", lingua), d.get("emergenza_tel")); pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8); pdf.set_x(10); pdf.multi_cell(0, 4, get_testo("pdf_certifie", lingua))
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12); pdf.cell(0, 8, "CONSENTEMENT AU TRAITEMENT DES DONNEES PERSONNELLES", 0, 1, "C")
    pdf.set_font("Helvetica", "", 8)
    for ln_ in testo_legale("consentement_privacy", PRIV_FALLBACK).split("\n"):
        pdf.set_x(10); pdf.multi_cell(0, 4.5, _pdf_safe(ln_))
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12); pdf.cell(0, 8, "REGLEMENT INTERIEUR & REGLES GENERALES DE L'USINE", 0, 1, "C")
    pdf.set_font("Helvetica", "", 8)
    for ln_ in testo_legale("reglement_interieur", REG_FALLBACK).split("\n"):
        pdf.set_x(10); pdf.multi_cell(0, 4.5, _pdf_safe(ln_))
    pdf.add_page()
    pdf.set_fill_color(255, 243, 205); pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, get_testo("pdf_id_titolo", lingua), 0, 1, "C", True); pdf.ln(5)
    pdf.set_font("Helvetica", "", 11); pdf.cell(0, 8, get_testo("pdf_id_desc", lingua), 0, 1, "C"); pdf.ln(5)
    pdf.set_font("Helvetica", "B", 16); pdf.cell(0, 12, f"{get_testo('pdf_id_code', lingua)} {s_str(d.get('codice')) or '____'}", 0, 1, "C"); pdf.ln(3)
    pdf.cell(0, 12, f"PIN: {s_str(d.get('pin')) or '_____'}", 0, 1, "C"); pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9); pdf.set_text_color(150, 0, 0); pdf.set_x(10); pdf.multi_cell(0, 5, get_testo("pdf_id_avviso", lingua)); pdf.set_text_color(0, 0, 0)
    pdf.add_page()
    pdf.set_fill_color(240, 248, 240); pdf.rect(0, 0, 210, 297, "F")
    pdf.set_draw_color(0, 110, 60); pdf.set_line_width(1.2); pdf.rect(7, 7, 196, 283)
    pdf.set_draw_color(0, 90, 160); pdf.set_line_width(0.4); pdf.rect(10, 10, 190, 277)
    pdf.set_draw_color(120, 180, 140); pdf.set_line_width(0.15)
    for i in range(10): pdf.ellipse(105, 150, 95 - i * 4, 60 - i * 2)
    if lb: pdf.image(lb, x=88, y=18, w=34)
    pdf.set_xy(15, 56); pdf.set_font("Helvetica", "B", 14); pdf.cell(0, 8, _pdf_safe(az.get("nome", "")), 0, 1, "C")
    pdf.set_font("Helvetica", "B", 12); pdf.cell(0, 7, get_testo("cert_titolo", lingua), 0, 1, "C")
    ufficiale = str(cfg_get("registrazioni_ufficiali", "NO")).upper() == "SI"
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, get_testo("cert_ufficiale", lingua) if ufficiale else get_testo("cert_copia", lingua), 0, 1, "C"); pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _pdf_safe(f"{get_testo('pdf_nom', lingua)} {s_str(d.get('cognome'))}   {get_testo('pdf_prenoms', lingua)} {s_str(d.get('nome'))}"), 0, 1, "C")
    pdf.cell(0, 6, _pdf_safe(f"CNI: {s_str(d.get('cni')) or '---'}   {get_testo('codice_accesso', lingua)}: {s_str(d.get('codice'))}"), 0, 1, "C"); pdf.ln(2)
    cert = s_str(d.get("cert_codice")) or genera_cert_codice(s_str(d.get("codice")))[0]
    pdf.set_font("Helvetica", "B", 10); pdf.cell(0, 6, _pdf_safe(f"N° {cert}"), 0, 1, "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _pdf_safe(f"{get_testo('pdf_data', lingua)} {doc_ts}"), 0, 1, "C")
    pdf.cell(0, 6, _pdf_safe(f"IP: {s_str(d.get('cert_ip')) or 'n/d'}   Lieu: {s_str(d.get('cert_lieu')) or 'Kiniambour (Sindia)'}"), 0, 1, "C")
    pdf.cell(0, 6, _pdf_safe(f"Manuel v{manuale_versione()} - Reglement + Consentement acceptes"), 0, 1, "C"); pdf.ln(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(90, 6, get_testo("pdf_candidat", lingua), 1, 0, "C"); pdf.cell(20, 6, "", 0, 0); pdf.cell(90, 6, get_testo("pdf_employeur", lingua), 1, 1, "C")
    pdf.ln(28); pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Signature: ______________________", 0, 1, "L"); pdf.ln(8)
    pdf.cell(0, 6, _pdf_safe(f"Data / Date: {doc_ts}"), 0, 1, "L")
    out = pdf.output(dest="S")
    return out.encode("latin-1", "ignore") if isinstance(out, str) else bytes(out)
# ------------------------- REGISTRAZIONE -------------------------
def box_telefono(lingua, n, obbligatorio=False):
    st.markdown(f'<div class="phone-box"><h4>{get_testo("telefono_" + str(n), lingua)}{" *" if obbligatorio else ""}</h4></div>', unsafe_allow_html=True)
    tel = st.text_input(f"Numero {n}", value=st.session_state.dati_form.get(f"telefono_{n}", ""), key=f"s2_tel{n}", label_visibility="collapsed")
    servizi_attivi = s_str(st.session_state.dati_form.get(f"servizi_tel{n}", "")).split(",")
    cb = st.columns(5); sel = {}
    for i, sv in enumerate(("Wave", "Orange Money", "WhatsApp", "Telegram", "Signal")):
        sel[sv] = cb[i].checkbox(sv, value=sv in servizi_attivi, key=f"s2_sv{n}_{i}")
    return tel, ",".join([k for k, v in sel.items() if v])
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
        if naz == "AUTRE": naz = st.text_input("Précisez: ", key="s1_naz_a")
        por = select_canonico("paesi", lingua, get_testo("paese_origine", lingua), "s1_pae", saved=st.session_state.dati_form.get("paese_origine"))
        if por == "AUTRE": por = st.text_input("Précisez: ", key="s1_pae_a")
    with c2:
        sesso = select_canonico("sesso", lingua, get_testo("sesso", lingua), "s1_ses", saved=st.session_state.dati_form.get("sesso"))
        stato_civile = select_canonico("stato_civile", lingua, get_testo("stato_civile", lingua), "s1_sta", saved=st.session_state.dati_form.get("stato_civile"))
        numero_mogli, dettagli_mogli, figli_tot = 0, "", 0
        if stato_civile == "coniugato":
            numero_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=1, key="s1_mog")
            det, somma = [], 0
            for i in range(1, numero_mogli + 1):
                st.markdown(f"Épouse {i}")
                cr, cf = st.columns(2)
                res = cr.text_input(f'{get_testo("residenza_moglie", lingua)} {i}', key=f"s1_res{i}")
                fig = cf.number_input(f'{get_testo("figli_moglie", lingua)} {i}', min_value=0, value=0, key=f"s1_fig{i}")
                somma += fig; det.append(f"Épouse {i}: {res} ({fig} enfants)")
            dettagli_mogli = " | ".join(det); figli_tot = somma
            st.info(f'ℹ️ {get_testo("somma_mogli", lingua)}: {somma}')
    return {"cognome": cognome, "nome": nome, "data_nascita": f"{giorno:02d}/{mese:02d}/{anno}", "luogo_nascita": luogo, "nazionalita": naz, "paese_origine": por, "sesso": sesso, "stato_civile": stato_civile, "numero_mogli": numero_mogli, "dettagli_mogli": dettagli_mogli, "figli_totale": figli_tot}
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
        tel1, sv1 = box_telefono(lingua, 1, True); tel2, sv2 = box_telefono(lingua, 2); tel3, sv3 = box_telefono(lingua, 3)
    return {"indirizzo": indirizzo, "quartiere": quartiere, "comune": comune, "regione_senegal": regione, "cni": cni, "nif": nif, "css": css, "cmu": cmu, "ipres": ipres, "telefono_1": tel1, "servizi_tel1": sv1, "telefono_2": tel2, "servizi_tel2": sv2, "telefono_3": tel3, "servizi_tel3": sv3}
def step_3(lingua):
    st.subheader(get_testo("step_3", lingua)); st.info(get_testo("nota_lavoro", lingua))
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
    st.subheader(get_testo("step_4", lingua)); st.info(get_testo("nota_competenze", lingua))
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
    return {"gruppo_sanguigno": gruppo, "rh": rh, "allergie": allergie, "malattie": malattie, "idoneita": idoneita, "data_visita": data_visita}
def step_6(lingua):
    st.subheader(get_testo("step_6", lingua))
    c1, c2 = st.columns(2)
    with c1:
        em_nome = st.text_input(get_testo("emergenza_nome", lingua), key="s6_no")
        em_par = st.text_input(get_testo("emergenza_parentela", lingua), key="s6_pa")
    with c2:
        em_tel = st.text_input(get_testo("emergenza_tel", lingua), key="s6_te")
        em_ind = st.text_input(get_testo("emergenza_indirizzo", lingua), key="s6_in")
    return {"emergenza_nome": em_nome, "emergenza_parentela": em_par, "emergenza_tel": em_tel, "emergenza_indirizzo": em_ind}
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
    return {"taglia_maglia": tm, "taglia_pantaloni": tp, "taglia_scarpe": ts, "taglia_giacca": tg, "taglia_cappello": tc, "taglia_guanti": tgu}
def blocco_telegram(lingua):
    link_canale = cfg_get("telegram_link_canale") or CONFIG["base_url"]
    st.markdown(f'<div class="tg-banner">📲 <b>{get_testo("tg_obbligo", lingua)}</b></div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="display:flex;gap:10px;">
<a class="docbtn" style="background:#a03030;" href="https://telegram.org/download" target="_blank">1️⃣ {get_testo("tg_install", lingua)}</a>
<a class="docbtn" style="background:#a03030;" href="{link_canale}" target="_blank">2️⃣ {get_testo("tg_join", lingua)}</a></div>
<div style="display:flex;gap:10px;margin-top:10px;">
<a class="docbtn" style="background:#2b4a6b;" href="{CONFIG['base_url']}/?doc=reglement" target="_blank">📄 {get_testo("doc_regolamento", lingua)}</a>
<a class="docbtn" style="background:#2b4a6b;" href="{CONFIG['base_url']}/?doc=privacy" target="_blank">🔒 {get_testo("doc_privacy", lingua)}</a></div>''', unsafe_allow_html=True)
def pannello_successo(lingua):
    u = st.session_state.ultimo_salvataggio
    st.success(f'✅ {get_testo("pdf_generato", lingua)}')
    st.info(get_testo("conserva_credenziali", lingua))
    c1, c2 = st.columns(2)
    c1.info(f'{get_testo("codice_accesso", lingua)}: {u["codice"]}')
    c2.info(f'{get_testo("pin_accesso", lingua)}: {u["pin"]}')
    st.download_button(label=f'📥 {get_testo("scarica", lingua)} PDF', data=u["pdf"], file_name=f'Proacier_{u["codice"]}.pdf', mime="application/pdf", use_container_width=True, key="btn_dl_ok")
    st.markdown("<br><br>", unsafe_allow_html=True)
    try:
        st.download_button(get_testo("man_download", lingua), data=genera_pdf_manuale(lingua), file_name=f"Manuel_Proacier_{lingua}.pdf", mime="application/pdf", use_container_width=True, key="btn_dl_man")
    except Exception: pass
    st.markdown("<br>", unsafe_allow_html=True)
    blocco_telegram(lingua)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(get_testo("nuova_registrazione", lingua), use_container_width=True):
        st.session_state.ultimo_salvataggio = None; st.session_state.reg_fp = None
        st.session_state.dati_form = {}; st.session_state.step = 1; st.session_state.avviso_mostrato = False
        st.rerun()
def pagina_registrazione(lingua):
    if st.session_state.get("ultimo_salvataggio"):
        pannello_successo(lingua); return
    step = st.session_state.step
    if step == 1 and not st.session_state.avviso_mostrato:
        st.warning(get_testo("avviso_non_contratto", lingua)); st.info(get_testo("avviso_regole_aziendali", lingua)); st.session_state.avviso_mostrato = True
    st.progress(step / 7); st.markdown(f"Étape {step}/7"); st.markdown("---")
    fn = {1: step_1, 2: step_2, 3: step_3, 4: step_4, 5: step_5, 6: step_6, 7: step_7}[step]
    dati_step = fn(lingua); st.session_state.dati_form.update(dati_step); st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if step > 1 and st.button(get_testo("indietro", lingua), use_container_width=True):
            st.session_state.step -= 1; st.rerun()
    with c2:
        if step < 7:
            if st.button(get_testo("continua", lingua), type="primary", use_container_width=True):
                if step == 1 and (not dati_step.get("cognome") or not dati_step.get("nome")): st.error(get_testo("errore_obbligatori", lingua))
                elif step == 2 and not dati_step.get("telefono_1"): st.error(get_testo("errore_obbligatori", lingua))
                else: st.session_state.step += 1; st.rerun()
        else:
            st.caption(get_testo("man_remis", lingua))
            conferma = st.checkbox(get_testo("checkbox_confirm", lingua), key="s7_conf")
            acc_man = st.checkbox(get_testo("man_accept_box", lingua), key="s7_man")
            if conferma and acc_man:
                if st.button(get_testo("genera_pdf", lingua), type="primary", use_container_width=True):
                    genera_e_salva(st.session_state.dati_form, lingua)
            else: st.warning(get_testo("cocher_case", lingua))
def genera_e_salva(dati, lingua):
    if not dati.get("cognome") or not dati.get("nome"):
        st.warning(get_testo("errore_obbligatori", lingua)); return
    fp = "|".join([s_str(dati.get("cognome")).lower(), s_str(dati.get("nome")).lower(), s_str(dati.get("telefono_1"))])
    if st.session_state.get("reg_fp") == fp:
        st.info(get_testo("candidatura_gia_inviata", lingua)); return
    with st.spinner(get_testo("saving", lingua)):
        dup = trova_duplicato_reg(dati)
        if dup:
            st.session_state.reg_fp = fp
            st.session_state.ultimo_salvataggio = {"codice": s_str(dup.get("codice")), "pin": s_str(dup.get("pin")), "pdf": genera_pdf_lavoratore(dup, lingua)}
            st.session_state.dati_form = {}; st.rerun(); return
        codice, pin = genera_credenziali()
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        ip, luogo = rileva_ip_luogo()
        cert, _sq = genera_cert_codice(codice)
        row = dict(dati)
        row.update({"id": codice, "codice": codice, "pin": pin, "data_registrazione": now, "stato_firma": "Da firmare", "timestamp": now, "turno": "",
                    "doc_timestamp": now, "cert_codice": cert, "cert_ip": ip, "cert_lieu": luogo,
                    "accetta_manuale": "SI", "accetta_manuale_versione": manuale_versione(), "accetta_manuale_data": datetime.now().strftime("%d/%m/%Y")})
        ok, msg = salva_append("DIPENDENTI", row, "codice", codice)
        if ok:
            st.session_state.reg_fp = fp
            st.session_state.ultimo_salvataggio = {"codice": codice, "pin": pin, "pdf": genera_pdf_lavoratore(row, lingua)}
            st.session_state.dati_form = {}; st.rerun()
        else: st.error(f"Erreur: {msg}")
def pagina_candidatura(lingua):
    idx = LINGUE.get(lingua, 0)
    st.title(get_testo("titolo_candidatura", lingua)); st.markdown(get_testo("sottotitolo_candidatura", lingua)); st.markdown("---")
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
        area = AREE_AZIENDALI[labels.index(settore)]
        if area["ruoli"]: mansione = st.selectbox(get_testo("mansione_richiesta", lingua), area["ruoli"], key=f"c_man_{labels.index(settore)}")
        else: mansione = st.text_input(get_testo("altro_specifica", lingua), key=f"c_man_libera_{labels.index(settore)}")
        c_studi = select_canonico("studi", lingua, get_testo("studi", lingua), "c_studi")
        if c_studi == "prof": st.caption(get_testo("hint_prof", lingua))
        c_skills = st.text_area(get_testo("skills", lingua), key="c_skills")
    c3, c4 = st.columns(2)
    c_exp = c3.number_input(get_testo("esperienza_anno", lingua), min_value=0, max_value=50, value=0, key="c_exp")
    c_sal = c4.text_input(get_testo("salario_richiesto", lingua), key="c_sal")
    c_note = st.text_area(get_testo("note", lingua), key="c_note")
    st.markdown("---")
    if st.button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True, key="btn_cand_invia"):
        if not c_cognome or not c_nome or not c_email or not c_tel: st.error(get_testo("errore_candidatura", lingua))
        else:
            fp = "|".join([c_cognome.strip().lower(), c_nome.strip().lower(), c_email.strip().lower(), c_tel.strip()])
            if st.session_state.get("cand_fp") == fp: st.info(get_testo("candidatura_gia_inviata", lingua))
            else:
                with st.spinner(get_testo("saving", lingua)):
                    dup = trova_duplicato_cand(c_cognome, c_nome, c_email, c_tel)
                    if dup:
                        st.session_state.cand_fp = fp; st.info(get_testo("candidatura_gia_inviata", lingua))
                    else:
                        row = {"id": f"CAND-{datetime.now().year}-{random.randint(1000, 9999)}", "data_candidatura": datetime.now().strftime("%d/%m/%Y %H:%M"),
                               "cognome": c_cognome, "nome": c_nome, "email": c_email, "telefono": c_tel, "data_nascita": f"{cg:02d}/{cm:02d}/{ca}",
                               "indirizzo": c_ind, "comune": c_com, "regione": c_reg, "settore_richiesto": settore, "mansione_richiesta": mansione,
                               "studi": c_studi, "skills": c_skills, "esperienza_anno": int(c_exp), "salario_richiesto": c_sal, "note": c_note, "stato": "Nuova"}
                        ok, msg = salva_append("CANDIDATURE", row, "id", row["id"])
                        if ok:
                            st.session_state.cand_fp = fp; st.success(get_testo("candidatura_inviata", lingua)); st.balloons()
                        else: st.error(f"Erreur: {msg}")
    if st.session_state.get("cand_fp") and st.button(get_testo("nouvelle_candidature", lingua), use_container_width=True, key="btn_cand_new"):
        for k in ("c_cognome", "c_nome", "c_email", "c_tel", "c_ind", "c_com", "c_skills", "c_sal", "c_note", "c_studi"): st.session_state.pop(k, None)
        for k in list(st.session_state.keys()):
            if k.startswith("c_man_"): st.session_state.pop(k, None)
        st.session_state.cand_fp = None; st.rerun()
def mostra_storico_mansioni(codice, lingua):
    _, recs = leggi_foglio("STORICO_MANSIONI")
    miei = [r for r in recs if s_str(r.get("code_travailleur")).upper() == codice.upper()]
    miei.sort(key=lambda r: data_ord(r.get("date_debut")) or (0, 0, 0), reverse=True)
    return miei
def mostra_storico_paghe(codice, lingua):
    _, recs = leggi_foglio("SALARI")
    miei = [r for r in recs if s_str(r.get("codice_lavoratore")).upper() == codice.upper()]
    miei.sort(key=lambda r: data_ord(r.get("data_inizio_validita")) or (0, 0, 0), reverse=True)
    return miei
def mostra_sanzioni(codice, lingua):
    _, recs = leggi_foglio("STORICO_SANZIONI")
    miei = [r for r in recs if s_str(r.get("code_travailleur")).upper() == codice.upper()]
    miei.sort(key=lambda r: data_ord(r.get("date")) or (0, 0, 0), reverse=True)
    return miei
def mostra_performance(codice, lingua):
    _, recs = leggi_foglio("PERFORMANCE_REVIEW")
    miei = [r for r in recs if s_str(r.get("code_travailleur")).upper() == codice.upper()]
    miei.sort(key=lambda r: data_ord(r.get("date_review")) or (0, 0, 0), reverse=True)
    return miei
def bacheca_avvisi(lingua):
    try: _, recs = leggi_foglio("AVVISI")
    except Exception: return
    recs = [r for r in recs if s_str(r.get("titolo")) or s_str(r.get("testo"))]
    if not recs: return
    st.markdown(get_testo("bacheca_title", lingua))
    for r in list(reversed(recs))[:5]:
        urg = s_str(r.get("urgente")).upper() == "SI"
        if urg: st.error(f"⚠️ URGENTE — {s_str(r.get('titolo'))} — {s_str(r.get('data_avviso'))}\n\n{s_str(r.get('testo'))}")
        else: st.info(f"📌 {s_str(r.get('titolo'))} — {s_str(r.get('data_avviso'))}\n\n{s_str(r.get('testo'))}")
def pagina_area_lavoratore(lingua):
    st.title(get_testo("i_miei_dati", lingua))
    st.success(f'{get_testo("benvenuto", lingua)} - {st.session_state.codice_operatore}')
    headers, records = leggi_foglio("DIPENDENTI")
    mio, mio_idx = None, -1
    for i, r in enumerate(records):
        if s_str(r.get("codice")).upper() == str(st.session_state.codice_operatore).strip().upper():
            mio, mio_idx = r, i; break
    if mio is None:
        st.error(get_testo("nessun_risultato", lingua)); return
    codice_mio = s_str(mio.get("codice"))
    man_ver = manuale_versione()
    if s_str(mio.get("accetta_manuale")) != "SI" or s_str(mio.get("accetta_manuale_versione")) != man_ver:
        st.warning(get_testo("man_updated", lingua))
        if st.button(get_testo("man_apri", lingua), key="wl_open_man"):
            st.session_state.pagina = "manuale"; st.rerun()
        if st.checkbox(get_testo("man_accept_box", lingua), key="wl_acc_chk"):
            if st.button("✅ OK", type="primary", key="wl_acc_btn"):
                ok, _ = salva_update("DIPENDENTI", mio_idx, {"accetta_manuale": "SI", "accetta_manuale_versione": man_ver, "accetta_manuale_data": datetime.now().strftime("%d/%m/%Y")})
                if ok: st.rerun()
        st.stop()
    promemoria_festivita(lingua); bacheca_avvisi(lingua); blocco_telegram(lingua); st.markdown("---")
    st.subheader(get_testo("sezione_mansione", lingua))
    mansioni = mostra_storico_mansioni(codice_mio, lingua)
    attuale = next((m for m in mansioni if not s_str(m.get("date_fin"))), None)
    if attuale: st.info(f"💼 {s_str(attuale.get('poste'))} — {s_str(attuale.get('departement'))}\n\n{get_testo('data_inizio', lingua)}: {s_str(attuale.get('date_debut'))}")
    else: st.info(get_testo("no_mansione", lingua))
    st.markdown("---")
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
    mie_vis = [v for v in recs_vis_me if s_str(v.get("codice_lavoratore")).upper() == codice_mio.upper()]
    mie_vis.sort(key=lambda v: data_ord(v.get("data_visita")) or (0, 0, 0), reverse=True)
    if mie_vis:
        ultima = mie_vis[0]
        pc = data_ord(ultima.get("prossimo_controllo"))
        if pc:
            lim = datetime.now() + timedelta(days=30)
            if pc <= (lim.year, lim.month, lim.day): st.warning(f'{get_testo("promemoria_visita", lingua)} {s_str(ultima.get("prossimo_controllo"))}')
        if norm_idoneita(ultima.get("idoneita")) in ("restriction", "inapte") and s_str(ultima.get("restrizioni")): st.info("🩺 " + s_str(ultima.get("restrizioni")))
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
                riga = f"- {s_str(v.get('data_visita'))} ({etichetta('tipo_visita', v.get('tipo_visita'), lingua)}) — {etichetta('idoneita', v.get('idoneita'), lingua)}"
                if s_str(v.get("esito")): riga += f" — {s_str(v.get('esito'))}"
                if s_str(v.get("restrizioni")): riga += f" — ⛔ {s_str(v.get('restrizioni'))}"
                st.markdown(riga)
    else: st.caption(get_testo("nessuna_visita", lingua))
    st.markdown("---")
    st.subheader(get_testo("sezione_paga", lingua))
    _, sal_records = leggi_foglio("SALARI")
    mia_paga = [s for s in sal_records if s_str(s.get("codice_lavoratore")).upper() == codice_mio.upper() and not s_str(s.get("data_fine_validita"))]
    if mia_paga:
        c1, c2 = st.columns(2)
        c1.text_input(get_testo("paga_type", lingua), value=etichetta("tipo_paga", mia_paga[0].get("tipo_paga"), lingua) or s_str(mia_paga[0].get("tipo_paga")), disabled=True)
        c2.text_input(get_testo("paga_amount", lingua), value=s_str(mia_paga[0].get("importo_base")) + " FCFA", disabled=True)
    else: st.info(get_testo("paga_desc", lingua))
    with st.expander(get_testo("sezione_storico_paghe", lingua)):
        storico_paghe = mostra_storico_paghe(codice_mio, lingua)
        if storico_paghe:
            for p in storico_paghe:
                riga = f"- {s_str(p.get('data_inizio_validita'))} → {etichetta('tipo_paga', p.get('tipo_paga'), lingua)} {s_str(p.get('importo_base'))} FCFA"
                if s_str(p.get("data_fine_validita")): riga += f" → {s_str(p.get('data_fine_validita'))}"
                if s_str(p.get("note")): riga += f" • {s_str(p.get('note'))}"
                st.markdown(riga)
        else: st.caption(get_testo("no_storico_paghe", lingua))
    st.markdown("---")
    st.subheader(get_testo("sezione_storico_mansioni", lingua))
    if mansioni:
        for m in mansioni:
            riga = f"- {s_str(m.get('date_debut'))} → {s_str(m.get('poste'))} ({s_str(m.get('departement'))})"
            riga += f" → {s_str(m.get('date_fin'))}" if s_str(m.get("date_fin")) else " (actuel)"
            if s_str(m.get("upgrade")) == "SI": riga += f" • 📈 {etichetta('motivo_cambio', m.get('motif'), lingua)}"
            st.markdown(riga)
    else: st.caption(get_testo("no_storico_mansioni", lingua))
    st.markdown("---")
    st.subheader("⭐ " + get_testo("sezione_performance", lingua))
    st.info("💡 " + get_testo("regola_oro", lingua))
    performance = mostra_performance(codice_mio, lingua)
    if performance:
        for p in performance:
            voto = s_int(p.get("note_1_5")); stelle = "⭐" * voto + "☆" * (5 - voto)
            st.markdown(f"### {s_str(p.get('date_review'))} — {etichetta('criteri_perf', p.get('critere'), lingua)} ({stelle})\n{get_testo('comportamento_osservato', lingua)}: {s_str(p.get('comportement_observé'))}\n\n{get_testo('evaluateur', lingua)}: {s_str(p.get('evaluateur'))}")
    else: st.caption(get_testo("no_performance", lingua))
    st.markdown("---")
    st.subheader("⚠️ " + get_testo("sezione_sanzioni", lingua))
    sanzioni = mostra_sanzioni(codice_mio, lingua)
    if sanzioni:
        for s in sanzioni:
            st.markdown(f"- {s_str(s.get('date'))} — {etichetta('tipo_sanzione', s.get('type'), lingua)} ({etichetta('gravita', s.get('gravite'), lingua)}): {s_str(s.get('description'))}")
    else: st.success("✅ " + get_testo("no_sanzioni", lingua))
    st.markdown("---")
    st.subheader(get_testo("mie_buste", lingua))
    _, pays_all = leggi_foglio("PAGAMENTI")
    miei_pays = [p for p in pays_all if s_str(p.get("codice_lavoratore")).upper() == codice_mio.upper()]
    miei_pays.sort(key=lambda p: data_ord(p.get("periodo_da")) or (0, 0, 0), reverse=True)
    if miei_pays:
        opts = [f"{s_str(p.get('periodo_da'))} → {s_str(p.get('periodo_a'))}" for p in miei_pays]
        sel = st.selectbox(get_testo("buste_period", lingua), opts, key="wl_busta_period")
        pago = miei_pays[opts.index(sel)]
        if st.button(get_testo("gen_mia_busta", lingua), type="primary", use_container_width=True, key="wl_busta_btn"):
            A = sys.modules[__name__]; det = None
            m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s_str(pago.get("periodo_da")))
            if m:
                dd, mm, yy = map(int, m.groups())
                try:
                    ant = modulo_paghe.calcola_anteprima(A, lingua, yy, mm, 1 if dd == 1 else 2)
                    det = next((x for x in ant["dets"] if x["code"].upper() == codice_mio.upper()), None)
                except Exception: det = None
            _, accs = leggi_foglio("ACCONTI")
            acconti = [a for a in accs if s_str(a.get("codice_lavoratore")).upper() == codice_mio.upper() and s_str(a.get("stato")).lower() not in ("annullato",)]
            st.download_button("📥 PDF", data=modulo_paghe.genera_busta_paga(A, lingua, mio, det, pago, miei_pays, acconti), file_name=f"Busta_{codice_mio}_{s_str(pago.get('periodo_da'))}.pdf", mime="application/pdf", use_container_width=True)
    else: st.info(get_testo("no_buste", lingua))
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
        n_mogli = 0
        if n_stato == "coniugato":
            n_mogli = int(st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=max(1, s_int(mio.get("numero_mogli"))), key="ar_mogli"))
            esistenti = parse_mogli(mio.get("dettagli_mogli")); st.caption(get_testo("mogli_hint", lingua))
            somma_mogli = 0
            for i in range(1, n_mogli + 1):
                st.markdown(f"Épouse {i}")
                cr, cf = st.columns(2)
                old = esistenti[i - 1] if len(esistenti) >= i else {"res": "", "fig": 0}
                res = cr.text_input(f'{get_testo("residenza_moglie", lingua)} {i}', value=old["res"], key=f"ar_res{i}")
                fig = int(cf.number_input(f'{get_testo("figli_moglie", lingua)} {i}', min_value=0, value=old["fig"], key=f"ar_fig{i}"))
                somma_mogli += fig
            prev = st.session_state.get("prev_somma_mogli")
            if prev is None:
                if "ar_fig_tot" not in st.session_state: st.session_state["ar_fig_tot"] = s_int(mio.get("figli_totale"))
            elif somma_mogli != prev: st.session_state["ar_fig_tot"] = somma_mogli
            st.session_state["prev_somma_mogli"] = somma_mogli
            st.info(f'ℹ️ {get_testo("somma_mogli", lingua)}: {somma_mogli}')
        n_figli = int(st.number_input(get_testo("figli_totale", lingua), min_value=0, key="ar_fig_tot"))
        st.markdown("---")
        st.subheader(get_testo("sezione_vestiario", lingua))
        xs = ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
        def safe_idx(lst, v):
            v = s_str(v); return lst.index(v) if v in lst else 0
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
            upd = {"telefono_1": n_tel1, "telefono_2": n_tel2, "telefono_3": n_tel3, "indirizzo": n_ind, "quartiere": n_qua, "comune": n_com, "regione_senegal": n_reg,
                   "emergenza_nome": n_em_nome, "emergenza_tel": n_em_tel, "stato_civile": n_stato,
                   "figli_totale": n_figli if n_stato == "coniugato" else s_int(mio.get("figli_totale")), "numero_mogli": n_mogli,
                   "dettagli_mogli": " | ".join([f"Épouse {i}: {st.session_state.get(f'ar_res{i}','')} ({st.session_state.get(f'ar_fig{i}',0)} enfants)" for i in range(1, n_mogli + 1)]) if n_stato == "coniugato" else "",
                   "taglia_maglia": n_tm, "taglia_pantaloni": n_tp, "taglia_scarpe": n_ts, "taglia_giacca": n_tg, "taglia_cappello": n_tc, "taglia_guanti": n_tgu}
            with st.spinner(get_testo("saving", lingua)):
                ok, msg = salva_update("DIPENDENTI", mio_idx, upd)
                if ok: st.success(get_testo("modifiche_salvate", lingua)); st.rerun()
                else: st.error(f"{get_testo('errore_salvataggio', lingua)} ({msg})")
    st.info(get_testo("sezione_comunicazioni", lingua))
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(get_testo("salva_link", lingua), use_container_width=True):
            _code, _pin = s_str(mio.get("codice")), s_str(mio.get("pin"))
            st.query_params.update({"code": _code, "pin": _pin})
            st.session_state.link_personale = f"{CONFIG['base_url']}/?code={_code}&pin={_pin}"
            st.info(get_testo("link_hint", lingua))
        if st.session_state.get("link_personale"):
            st.caption(get_testo("copia_link_help", lingua)); st.code(st.session_state.link_personale, language=None)
    with c2:
        st.download_button(label=get_testo("ristampa_pdf", lingua), data=genera_pdf_lavoratore(dict(mio), lingua), file_name=f"Proacier_{codice_mio}.pdf", mime="application/pdf", use_container_width=True)
    st.markdown("---")
    if st.button(get_testo("logout", lingua), use_container_width=True):
        _do_logout(); st.rerun()
def sezione_avvisi_admin(lingua):
    st.markdown("### " + get_testo("avv_title", lingua))
    with st.form("avv_form"):
        tit = st.text_input(get_testo("avv_titolo", lingua))
        tex = st.text_area(get_testo("avv_testo", lingua))
        urg = st.checkbox(get_testo("avv_urgente", lingua))
        if st.form_submit_button(get_testo("avv_pub", lingua), type="primary"):
            if not tex.strip(): st.error(get_testo("avv_err", lingua))
            else:
                tg_ok = invia_telegram(("🚨 URGENT — " if urg else "📢 ") + (tit + "\n" if tit else "") + tex)
                row = {"id_avviso": f"AVV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10,99)}", "data_avviso": datetime.now().strftime("%d/%m/%Y"),
                       "titolo": tit, "testo": tex, "urgente": "SI" if urg else "NO", "autore": "admin",
                       "inviato_telegram": "SI" if tg_ok else "NO", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
                ok, _ = salva_append("AVVISI", row)
                if ok: st.success(get_testo("avv_done", lingua) + (" — Telegram ✅" if tg_ok else " — Telegram ❌"))
                else: st.error("Erreur AVVISI")
def pagina_dashboard(lingua):
    st.title(get_testo("dashboard", lingua))
    env = st.session_state.get("ambiente", "produzione")
    with st.expander(get_testo("amb_title", lingua), expanded=(env == "test")):
        sel_env = st.radio("Ambiente", ["produzione", "test"], index=0 if env == "produzione" else 1, horizontal=True, key="amb_sel", label_visibility="collapsed")
        st.caption(get_testo("amb_hint", lingua))
        uff = str(cfg_get("registrazioni_ufficiali", "NO")).upper() == "SI"
        n_uff = st.checkbox(get_testo("reg_officiali", lingua), value=uff, key="amb_uff")
        if n_uff != uff:
            cfg_set("registrazioni_ufficiali", "SI" if n_uff else "NO"); st.rerun()
        if sel_env != env:
            st.session_state["ambiente"] = sel_env; _svuota_cache(); st.rerun()
    promemoria_festivita(lingua, consiglio=True)
    pag = st.radio("Pagina", [get_testo("dash_p1", lingua), get_testo("dash_p2", lingua)], horizontal=True, label_visibility="collapsed")
    if pag == get_testo("dash_p2", lingua):
        modulo_paghe.pagina_fase7(lingua, sys.modules[__name__]); return
    b = leggi_admin()
    recs_dip, recs_sal = b.get("DIPENDENTI", []), b.get("SALARI", [])
    recs_turni, recs_vis = b.get("TURNI", []), b.get("VISITE_MEDICHE", [])
    recs_man, recs_sanz, recs_perf = b.get("STORICO_MANSIONI", []), b.get("STORICO_SANZIONI", []), b.get("PERFORMANCE_REVIEW", [])
    turni_codes = [s_str(r.get("codice_turno")) for r in recs_turni if s_str(r.get("codice_turno")) and s_str(r.get("ora_inizio"))]
    if not turni_codes: turni_codes = ["T1", "T2", "T3", "EQUIPE"]
    attivi = sum(1 for r in recs_dip if (s_str(r.get("stato_lavorativo")).lower() or "prova") in ("prova", "assunto", "esterno"))
    archiviati = sum(1 for r in recs_dip if s_str(r.get("stato_lavorativo")).lower() in ("dimissionario", "licenziato"))
    cfg_prova_gg = s_int(cfg_get("promemoria_prova_giorni_prima", "7")) or 7
    oggi = date.today(); prove_scad = []
    for r in recs_dip:
        fp = data_ord(r.get("data_fine_prova"))
        if fp and (s_str(r.get("stato_lavorativo")).lower() or "prova") == "prova":
            d = date(*fp)
            if (d - oggi).days <= cfg_prova_gg: prove_scad.append(f"{s_str(r.get('cognome'))} {s_str(r.get('nome'))} ({s_str(r.get('codice'))}) → {d.strftime('%d/%m/%Y')}")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(get_testo("totale_operai", lingua), len(recs_dip))
    c2.metric(get_testo("dash_attivi", lingua), attivi)
    c3.metric(get_testo("dash_archiviati", lingua), archiviati)
    c4.metric(get_testo("turni_assegnati", lingua), sum(1 for r in recs_dip if s_str(r.get("turno"))))
    c5.metric(get_testo("salari_attivi", lingua), sum(1 for r in recs_sal if s_str(r.get("codice_lavoratore")) and not s_str(r.get("data_fine_validita"))))
    if prove_scad: st.warning("⚠️ " + get_testo("prova_scad", lingua) + ": " + "; ".join(prove_scad))
    ultime = {}
    for v in recs_vis:
        cod = s_str(v.get("codice_lavoratore"))
        if not cod: continue
        o = data_ord(v.get("data_visita"))
        if cod not in ultime or (o and (ultime[cod][0] is None or o > ultime[cod][0])): ultime[cod] = (o, v)
    lim = datetime.now() + timedelta(days=30); lim_t = (lim.year, lim.month, lim.day)
    scaduti, restritti = [], []
    for r in recs_dip:
        cod, nome = s_str(r.get("codice")), f"{s_str(r.get('cognome'))} {s_str(r.get('nome'))}"
        u = ultime.get(cod)
        if u:
            pc = data_ord(u[1].get("prossimo_controllo"))
            if pc and pc <= lim_t: scaduti.append(f"{nome} ({cod}) → {s_str(u[1].get('prossimo_controllo'))}")
        if norm_idoneita(r.get("idoneita")) in ("restriction", "inapte"): restritti.append(f"{nome} ({cod})")
    if scaduti: st.warning("⚠️ " + get_testo("visite_scadute", lingua) + ": " + "; ".join(scaduti))
    if restritti: st.error("🩺 " + get_testo("idoneita_parziale", lingua) + ": " + "; ".join(restritti))
    st.markdown("---")
    sezione_avvisi_admin(lingua)
    st.markdown("---")
    cerca = st.text_input(get_testo("cerca_dip", lingua), key="adm_cerca")
    mostrati = []
    for i, r in enumerate(recs_dip):
        blob = (s_str(r.get("codice")) + " " + s_str(r.get("cognome")) + " " + s_str(r.get("nome"))).lower()
        if not cerca or cerca.lower() in blob: mostrati.append((i, r))
    if not mostrati:
        st.warning(get_testo("nessun_risultato", lingua)); return
    limite = st.session_state.get("adm_limit", 15)
    vista = mostrati if cerca else mostrati[:limite]
    st.caption(get_testo("form_hint", lingua))
    for i, r in vista:
        cod = s_str(r.get("codice")) or f"(senza codice riga {i})"
        nome_completo = f"{s_str(r.get('nome'))} {s_str(r.get('cognome'))}"
        stato_lbl = etichetta("stato_lavorativo", s_str(r.get("stato_lavorativo")) or "prova", lingua)
        with st.expander(f"{cod} — {nome_completo} | {get_testo('turno', lingua)}: {s_str(r.get('turno')) or '—'} | {stato_lbl}"):
            st.markdown(f"👤 {nome_completo} — {s_str(r.get('indirizzo'))}, {s_str(r.get('comune'))} {s_str(r.get('quartiere'))}\n\n🎂 {formatta_data(r.get('data_nascita'))} — {s_str(r.get('luogo_nascita'))}\n\n📞 {servizi_di(r)}\n\n🚨 {get_testo('emergenza_nome', lingua)}: {s_str(r.get('emergenza_nome'))} — {s_str(r.get('emergenza_tel'))}\n\n👥 {get_testo('numero_mogli', lingua)}: {s_int(r.get('numero_mogli'))} — {get_testo('figli_totale', lingua)}: {s_int(r.get('figli_totale'))}")
            st.markdown(f'### {get_testo("sez_admin", lingua)}')
            ca, cb = st.columns(2)
            with ca:
                t_val = s_str(r.get("turno"))
                n_turno = st.selectbox(get_testo("turno", lingua), turni_codes, index=turni_codes.index(t_val) if t_val in turni_codes else 0, key=f"adm_turno_{i}")
                ido_codes = [o[0] for o in OPZ["idoneita"]]; ido_val = s_str(r.get("idoneita"))
                n_ido = st.selectbox(get_testo("idoneita", lingua), ido_codes, index=ido_codes.index(ido_val) if ido_val in ido_codes else 0, format_func=lambda c: etichetta("idoneita", c, lingua), key=f"adm_ido_{i}")
                n_vis = st.text_input(get_testo("data_visita", lingua), value=s_str(r.get("data_visita")), key=f"adm_vis_{i}")
                n_stato = select_canonico("stato_lavorativo", lingua, get_testo("stato_lav", lingua), f"adm_stato_{i}", saved=r.get("stato_lavorativo") or "prova")
                n_fissa = st.checkbox(get_testo("paga_fissa_lbl", lingua), value=s_str(r.get("paga_fissa")).upper() == "SI", key=f"adm_fissa_{i}")
            with cb:
                attiva = next((s for s in recs_sal if s_str(s.get("codice_lavoratore")) == s_str(r.get("codice")) and not s_str(s.get("data_fine_validita"))), None)
                tp_val = s_str(attiva.get("tipo_paga")) if attiva else ""
                tp_opts = ["", "giornaliero", "orario", "mensile"]
                n_tp = st.selectbox(get_testo("paga_type", lingua), tp_opts, index=tp_opts.index(tp_val) if tp_val in tp_opts else 0, format_func=lambda x: get_testo("globale", lingua) if x == "" else etichetta("tipo_paga", x, lingua), key=f"adm_tp_{i}")
                n_imp = st.number_input(get_testo("paga_amount", lingua) + " (FCFA)", min_value=0, value=s_int(attiva.get("importo_base")) if attiva else 0, step=500, key=f"adm_imp_{i}")
                n_soc = st.text_input(get_testo("soc_formale", lingua), value=s_str(r.get("societa_formale")), key=f"adm_soc_{i}")
                n_fp = st.text_input(get_testo("fine_prova", lingua), value=s_str(r.get("data_fine_prova")), key=f"adm_fp_{i}")
            st.markdown("### " + get_testo("sez_mansioni", lingua))
            mie_man = [m for m in recs_man if s_str(m.get("code_travailleur")).upper() == s_str(r.get("codice")).upper()]
            mie_man.sort(key=lambda x: data_ord(x.get("date_debut")) or (0, 0, 0), reverse=True)
            if mie_man:
                for m in mie_man:
                    riga = f"- {s_str(m.get('date_debut'))} → {s_str(m.get('poste'))} ({s_str(m.get('departement'))})"
                    riga += f" → {s_str(m.get('date_fin'))}" if s_str(m.get("date_fin")) else " (actuel)"
                    st.markdown(riga)
            else: st.caption(get_testo("no_storico_mansioni", lingua))
            mc1, mc2, mc3 = st.columns(3)
            mc1.text_input(get_testo("mansione", lingua), key=f"new_poste_{i}")
            mc2.text_input(get_testo("dipartimento", lingua), key=f"new_dept_{i}")
            mc3.text_input(get_testo("data_inizio", lingua) + " (GG/MM/AAAA)", value=datetime.now().strftime("%d/%m/%Y"), key=f"new_mdata_{i}")
            select_canonico("motivo_cambio", lingua, get_testo("motivo_cambio", lingua), f"new_motivo_{i}")
            st.checkbox(get_testo("upgrade", lingua), key=f"new_upgrade_{i}")
            st.markdown("### " + get_testo("sez_sanzioni", lingua))
            mie_sanz = [s for s in recs_sanz if s_str(s.get("code_travailleur")).upper() == s_str(r.get("codice")).upper()]
            mie_sanz.sort(key=lambda x: data_ord(x.get("date")) or (0, 0, 0), reverse=True)
            if mie_sanz:
                for s in mie_sanz:
                    st.markdown(f"- {s_str(s.get('date'))} — {etichetta('tipo_sanzione', s.get('type'), lingua)} ({etichetta('gravita', s.get('gravite'), lingua)}): {s_str(s.get('description'))}")
            else: st.success("✅ " + get_testo("no_sanzioni", lingua))
            sc1, sc2 = st.columns(2)
            select_canonico("tipo_sanzione", lingua, get_testo("tipo_sanzione", lingua), f"new_tipo_s_{i}")
            select_canonico("gravita", lingua, get_testo("gravita", lingua), f"new_grav_{i}")
            sc1.text_input(get_testo("data_sanzione", lingua), value=datetime.now().strftime("%d/%m/%Y"), key=f"new_sdata_{i}")
            st.text_area(get_testo("descrizione", lingua), key=f"new_desc_{i}")
            st.text_input(get_testo("note", lingua), key=f"new_note_{i}")
            st.markdown("### " + get_testo("sez_performance", lingua))
            st.info("💡 " + get_testo("regola_oro", lingua))
            mie_perf = [p for p in recs_perf if s_str(p.get("code_travailleur")).upper() == s_str(r.get("codice")).upper()]
            mie_perf.sort(key=lambda x: data_ord(x.get("date_review")) or (0, 0, 0), reverse=True)
            if mie_perf:
                for p in mie_perf:
                    voto = s_int(p.get("note_1_5")); stelle = "⭐" * voto + "☆" * (5 - voto)
                    st.markdown(f"- {s_str(p.get('date_review'))} — {etichetta('criteri_perf', p.get('critere'), lingua)} ({stelle})\n   {s_str(p.get('comportement_observé'))}")
            else: st.caption(get_testo("no_performance", lingua))
            pc1, pc2 = st.columns(2)
            select_canonico("criteri_perf", lingua, get_testo("critere", lingua), f"new_crit_{i}")
            pc1.slider(get_testo("nota_1_5", lingua), 1, 5, 3, key=f"new_voto_{i}")
            pc2.text_input(get_testo("data_visita", lingua), value=datetime.now().strftime("%d/%m/%Y"), key=f"new_pdata_{i}")
            st.text_area(get_testo("comportamento_osservato", lingua), key=f"new_comp_{i}")
            st.text_input(get_testo("contesto", lingua), key=f"new_cont_{i}")
            st.text_input(get_testo("frequenza", lingua), key=f"new_freq_{i}")
            st.text_input(get_testo("azione_proposta", lingua), key=f"new_az_{i}")
            st.text_input(get_testo("evaluateur", lingua), value="admin", key=f"new_eval_{i}")
            st.markdown("### 🩺 " + get_testo("storico_visite", lingua))
            mie_vis = [v for v in recs_vis if s_str(v.get("codice_lavoratore")) == s_str(r.get("codice"))]
            mie_vis.sort(key=lambda v: data_ord(v.get("data_visita")) or (0, 0, 0), reverse=True)
            if mie_vis:
                for v in mie_vis:
                    riga = f"- {s_str(v.get('data_visita'))} ({etichetta('tipo_visita', v.get('tipo_visita'), lingua)}) — {etichetta('idoneita', v.get('idoneita'), lingua)} — {s_str(v.get('esito'))}"
                    if s_str(v.get("restrizioni")): riga += f" — ⛔ {s_str(v.get('restrizioni'))}"
                    if s_str(v.get("prossimo_controllo")): riga += f" — ➡️ {s_str(v.get('prossimo_controllo'))}"
                    st.markdown(riga)
            else: st.caption(get_testo("nessuna_visita", lingua))
            with st.form(f"adm_vis_form_{i}"):
                v1, v2 = st.columns(2)
                with v1:
                    n_data_vis = st.text_input(get_testo("data_visita", lingua), value=datetime.now().strftime("%d/%m/%Y"), key=f"adm_visdata_{i}")
                    n_tipo = st.selectbox(get_testo("tipo_visita", lingua), [o[0] for o in OPZ["tipo_visita"]], format_func=lambda c: etichetta("tipo_visita", c, lingua), key=f"adm_vistipo_{i}")
                    n_ido2 = st.selectbox(get_testo("idoneita", lingua), [o[0] for o in OPZ["idoneita"]], format_func=lambda c: etichetta("idoneita", c, lingua), key=f"adm_visido_{i}")
                with v2:
                    n_restr = st.text_input(get_testo("restrizioni", lingua), key=f"adm_visrestr_{i}")
                    n_pross = st.text_input(get_testo("prossimo_controllo", lingua) + " (GG/MM/AAAA)", key=f"adm_vispros_{i}")
                    n_esito = st.text_area(get_testo("esito", lingua), key=f"adm_visesito_{i}")
                sub_vis = st.form_submit_button(get_testo("salva_modifiche", lingua))
                if sub_vis:
                    okv, mv = salva_append("VISITE_MEDICHE", {"codice_lavoratore": s_str(r.get("codice")), "data_visita": n_data_vis, "tipo_visita": n_tipo, "idoneita": n_ido2, "restrizioni": n_restr, "esito": n_esito, "prossimo_controllo": n_pross, "registrato_da": "admin", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")})
                    okd, md = salva_update("DIPENDENTI", i, {"idoneita": n_ido2, "data_visita": n_data_vis})
                    if okv and okd: st.success(get_testo("modifiche_salvate", lingua)); st.rerun()
                    else: st.error(f"{get_testo('errore_salvataggio', lingua)} ({mv} {md})")
            st.download_button(get_testo("ristampa_pdf", lingua), data=genera_pdf_lavoratore(r, lingua), file_name=f"Proacier_{s_str(r.get('codice')) or i}.pdf", mime="application/pdf", use_container_width=True, key=f"adm_pdf_{i}")
    if st.button(get_testo("salva_tutto", lingua), type="primary", use_container_width=True):
        cambi = 0
        _, fresh_man = leggi_foglio("STORICO_MANSIONI", force=True)
        for i, r in vista:
            cod = s_str(r.get("codice")); nome_completo = f"{s_str(r.get('nome'))} {s_str(r.get('cognome'))}"
            upd = {}
            for campo, key, orig in (("turno", f"adm_turno_{i}", s_str(r.get("turno"))), ("idoneita", f"adm_ido_{i}", s_str(r.get("idoneita"))),
                                     ("data_visita", f"adm_vis_{i}", s_str(r.get("data_visita"))), ("stato_lavorativo", f"adm_stato_{i}", s_str(r.get("stato_lavorativo")) or "prova"),
                                     ("societa_formale", f"adm_soc_{i}", s_str(r.get("societa_formale"))), ("data_fine_prova", f"adm_fp_{i}", s_str(r.get("data_fine_prova")))):
                nv = st.session_state.get(key, orig)
                if nv != orig: upd[campo] = nv
            fissa_v = "SI" if st.session_state.get(f"adm_fissa_{i}") else "NO"
            if fissa_v != (s_str(r.get("paga_fissa")) or "NO"): upd["paga_fissa"] = fissa_v
            if upd and cod:
                ok, _ = salva_update("DIPENDENTI", i, upd)
                if ok: cambi += 1
            attiva = next((s for s in recs_sal if s_str(s.get("codice_lavoratore")) == cod and not s_str(s.get("data_fine_validita"))), None)
            orig_tp = s_str(attiva.get("tipo_paga")) if attiva else ""
            orig_imp = s_int(attiva.get("importo_base")) if attiva else 0
            n_tp = st.session_state.get(f"adm_tp_{i}", orig_tp); n_imp = int(st.session_state.get(f"adm_imp_{i}", orig_imp))
            if (n_tp != orig_tp) or (n_imp != orig_imp):
                if attiva:
                    ok2, _2 = salva_update("SALARI", recs_sal.index(attiva), {"tipo_paga": n_tp, "importo_base": n_imp})
                    if ok2: cambi += 1
                elif n_imp > 0 or n_tp:
                    ok2, _2 = salva_append("SALARI", {"codice_lavoratore": cod, "tipo_paga": n_tp, "importo_base": n_imp, "data_inizio_validita": datetime.now().strftime("%d/%m/%Y"), "data_fine_validita": "", "note": ""})
                    if ok2: cambi += 1
            new_poste = s_str(st.session_state.get(f"new_poste_{i}"))
            if new_poste and cod:
                for idx_r, rr in enumerate(fresh_man):
                    if s_str(rr.get("code_travailleur")).upper() == cod.upper() and not s_str(rr.get("date_fin")):
                        salva_update("STORICO_MANSIONI", idx_r, {"date_fin": datetime.now().strftime("%d/%m/%Y")})
                ok, _ = salva_append("STORICO_MANSIONI", {"code_travailleur": cod, "nom_prenom": nome_completo, "date_debut": s_str(st.session_state.get(f"new_mdata_{i}")) or datetime.now().strftime("%d/%m/%Y"), "date_fin": "", "poste": new_poste, "departement": s_str(st.session_state.get(f"new_dept_{i}")), "motif": s_str(st.session_state.get(f"new_motivo_{i}")), "upgrade": "SI" if st.session_state.get(f"new_upgrade_{i}") else "NO"})
                if ok: cambi += 1
            new_desc = s_str(st.session_state.get(f"new_desc_{i}"))
            if new_desc and cod:
                ok, _ = salva_append("STORICO_SANZIONI", {"code_travailleur": cod, "nom_prenom": nome_completo, "date": s_str(st.session_state.get(f"new_sdata_{i}")) or datetime.now().strftime("%d/%m/%Y"), "type": s_str(st.session_state.get(f"new_tipo_s_{i}")), "description": new_desc, "gravite": s_str(st.session_state.get(f"new_grav_{i}")), "sanctionneur": "admin", "note": s_str(st.session_state.get(f"new_note_{i}"))})
                if ok: cambi += 1
            new_comp = s_str(st.session_state.get(f"new_comp_{i}"))
            if new_comp and cod:
                ok, _ = salva_append("PERFORMANCE_REVIEW", {"code_travailleur": cod, "nom_prenom": nome_completo, "date_review": s_str(st.session_state.get(f"new_pdata_{i}")) or datetime.now().strftime("%d/%m/%Y"), "evaluateur": s_str(st.session_state.get(f"new_eval_{i}")) or "admin", "critere": s_str(st.session_state.get(f"new_crit_{i}")), "comportement_observé": new_comp, "contexte": s_str(st.session_state.get(f"new_cont_{i}")), "frequence": s_str(st.session_state.get(f"new_freq_{i}")), "note_1_5": st.session_state.get(f"new_voto_{i}", 3), "action_proposee": s_str(st.session_state.get(f"new_az_{i}"))})
                if ok: cambi += 1
        st.success(f"✅ {cambi} {get_testo('salvate_n', lingua)}")
        st.rerun()
    if not cerca and len(mostrati) > limite:
        if st.button(get_testo("mostra_altri", lingua), key="adm_more"):
            st.session_state.adm_limit = limite + 15; st.rerun()
def _do_logout():
    st.session_state.logged_in = False; st.session_state.user_type = None
    st.session_state.codice_operatore = None; st.session_state.pagina = "home"; st.session_state.link_personale = None
    try: st.query_params.clear()
    except Exception: pass
def main():
    for k, v in {"lingua": "fr", "pagina": "home", "logged_in": False, "user_type": None, "step": 1, "dati_form": {}, "codice_operatore": None,
                 "avviso_mostrato": False, "ultimo_salvataggio": None, "cand_fp": None, "reg_fp": None, "_cache": {}, "adm_limit": 15,
                 "link_personale": None, "ambiente": "produzione"}.items():
        if k not in st.session_state: st.session_state[k] = v
    try:
        ql = st.query_params.get("lang")
        if ql in ("fr", "it", "en"): st.session_state.lingua = ql
    except Exception: pass
    lingua = st.session_state.lingua
    CONFIG["url_api"] = CONFIG["url_api_produzione"] if st.session_state.get("ambiente") == "produzione" else CONFIG["url_api_test"]
    try: qdoc = st.query_params.get("doc")
    except Exception: qdoc = None
    if qdoc in ("reglement", "privacy") and not st.session_state.logged_in:
        pagina_documento(qdoc, lingua); footer(); return
    if not st.session_state.logged_in:
        try:
            qp = st.query_params; qc, qpin = qp.get("code"), qp.get("pin"); au, ap = qp.get("adm_u"), qp.get("adm_p")
        except Exception: qc, qpin, au, ap = None, None, None, None
        if au and ap and au == CONFIG["user_admin"] and ap == CONFIG["password_admin"]:
            st.session_state.logged_in = True; st.session_state.user_type = "admin"; st.session_state.pagina = "dashboard"
        elif qc and qpin:
            _, recs = leggi_foglio("DIPENDENTI")
            for r in recs:
                if s_str(r.get("codice")).upper() == str(qc).strip().upper() and s_str(r.get("pin")) == str(qpin).strip():
                    st.session_state.logged_in = True; st.session_state.user_type = "lavoratore"
                    st.session_state.codice_operatore = str(qc).strip(); st.session_state.pagina = "area_lavoratore"; break
    with st.sidebar:
        lf1, lf2, lf3 = st.columns(3)
        if lf1.button("FRA", use_container_width=True, key="lang_fr"): st.session_state.lingua = "fr"; st.rerun()
        if lf2.button("ENG", use_container_width=True, key="lang_en"): st.session_state.lingua = "en"; st.rerun()
        if lf3.button("ITA", use_container_width=True, key="lang_it"): st.session_state.lingua = "it"; st.rerun()
        st.image(_logo_url("logo_brand", "proacier.png"), use_container_width=True)
        if st.button(get_testo("home", lingua), use_container_width=True, key="sb_home"):
            _do_logout(); st.rerun()
        if st.session_state.logged_in:
            st.success(f'{get_testo("benvenuto", lingua)}')
            if st.session_state.user_type == "admin":
                if st.button(get_testo("dashboard", lingua), use_container_width=True, key="sb_dash"): st.session_state.pagina = "dashboard"; st.rerun()
            if st.session_state.user_type == "lavoratore":
                if st.button(get_testo("i_miei_dati", lingua), use_container_width=True, key="sb_miei"): st.session_state.pagina = "area_lavoratore"; st.rerun()
            if st.button(get_testo("man_title", lingua), use_container_width=True, key="sb_man"): st.session_state.pagina = "manuale"; st.rerun()
            if st.button(get_testo("logout", lingua), use_container_width=True, key="sb_out"): _do_logout(); st.rerun()
        else:
            if st.button(get_testo("candidatura_spontanea", lingua), use_container_width=True, key="sb_cand"): st.session_state.pagina = "candidatura"; st.rerun()
            if st.button(get_testo("area_lavoratore", lingua), use_container_width=True, key="sb_area"): st.session_state.pagina = "espace"; st.rerun()
            if st.button(get_testo("dashboard", lingua), use_container_width=True, key="sb_admin"): st.session_state.pagina = "login_admin"; st.rerun()
        st.markdown("---")
        st.markdown(f'### {get_testo("titolo_sidebar", lingua)}', unsafe_allow_html=True)
        st.markdown(get_testo("sottotitolo", lingua))
        st.caption(VERSIONE + (" — 🧪 SANDBOX" if st.session_state.get("ambiente") == "test" else ""))
    if st.session_state.pagina == "home":
        st.title(get_testo("titolo", lingua)); st.subheader(get_testo("sottotitolo", lingua)); st.markdown("---")
        st.subheader(get_testo("home_titolo", lingua))
        c1, c2 = st.columns(2)
        c1.markdown(f'📌 {get_testo("home_p1_t", lingua)}\n- {get_testo("home_p1_d", lingua)}')
        c1.markdown(f'📌 {get_testo("home_p2_t", lingua)}\n- {get_testo("home_p2_d", lingua)}')
        c2.markdown(f'📌 {get_testo("home_p3_t", lingua)}\n- {get_testo("home_p3_d", lingua)}')
        c2.markdown(f'📌 {get_testo("home_p4_t", lingua)}\n- {get_testo("home_p4_d", lingua)}')
        st.markdown("---"); st.subheader(get_testo("home_navigation", lingua))
        c1, c2, c3 = st.columns(3)
        if c1.button(get_testo("candidatura_spontanea", lingua), use_container_width=True, type="primary"): st.session_state.pagina = "candidatura"; st.rerun()
        if c2.button(get_testo("area_lavoratore", lingua), use_container_width=True, type="primary"): st.session_state.pagina = "espace"; st.rerun()
        if c3.button(get_testo("dashboard", lingua), use_container_width=True): st.session_state.pagina = "login_admin"; st.rerun()
    elif st.session_state.pagina == "espace":
        st.title(get_testo("area_lavoratore", lingua)); st.markdown("---")
        c1, c2 = st.columns(2)
        c1.markdown(f'### 👤 {get_testo("giornalieri_titolo", lingua)}'); c1.info(get_testo("giornalieri_desc", lingua))
        if c1.button(get_testo("login_btn", lingua), use_container_width=True, type="primary"): st.session_state.pagina = "login_lavoratore"; st.rerun()
        c2.markdown(f'### 📝 {get_testo("nuovo_giornaliero_titolo", lingua)}'); c2.info(get_testo("nuovo_giornaliero_desc", lingua))
        if c2.button(get_testo("trasmissione_btn", lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = "registrazione"; st.session_state.step = 1; st.session_state.dati_form = {}
            st.session_state.avviso_mostrato = False; st.session_state.ultimo_salvataggio = None; st.session_state.reg_fp = None; st.rerun()
    elif st.session_state.pagina == "registrazione": pagina_registrazione(lingua)
    elif st.session_state.pagina == "candidatura": pagina_candidatura(lingua)
    elif st.session_state.pagina == "area_lavoratore": pagina_area_lavoratore(lingua)
    elif st.session_state.pagina == "manuale":
        if st.session_state.logged_in: pagina_manuale(lingua)
        else: st.session_state.pagina = "home"
    elif st.session_state.pagina == "login_lavoratore":
        codice = st.text_input(get_testo("codice", lingua), key="lg_cod")
        pin = st.text_input(get_testo("pin", lingua), type="password", key="lg_pin")
        if st.button(get_testo("accedi", lingua), type="primary", key="lg_btn"):
            _, records = leggi_foglio("DIPENDENTI")
            ok = any(s_str(r.get("codice")).upper() == codice.strip().upper() and s_str(r.get("pin")) == pin.strip() for r in records)
            if ok:
                st.session_state.logged_in = True; st.session_state.user_type = "lavoratore"
                st.session_state.codice_operatore = codice.strip(); st.session_state.pagina = "area_lavoratore"; st.rerun()
            else: st.error(get_testo("codice_errato", lingua))
    elif st.session_state.pagina == "login_admin":
        usr = st.text_input(get_testo("admin_user", lingua), key="lg_usr")
        pwd = st.text_input(get_testo("password", lingua), type="password", key="lg_pwd")
        if st.button(get_testo("accedi", lingua), type="primary", key="lg_adm"):
            if usr.strip() == CONFIG["user_admin"] and pwd == CONFIG["password_admin"]:
                st.session_state.logged_in = True; st.session_state.user_type = "admin"; st.session_state.pagina = "dashboard"; st.rerun()
            else: st.error(get_testo("codice_errato", lingua))
    elif st.session_state.pagina == "dashboard": pagina_dashboard(lingua)
    footer()
if __name__ == "__main__":
    main()