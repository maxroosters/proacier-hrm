# -*- coding: utf-8 -*-
"""
PROACIER - HRM - Versione 11.0 FINALE
========================================
MODIFICHE APPLICATE:
1. ✅ Fix errore doppio click candidatura: dati salvati PRIMA della validazione
2. ✅ Fix spazio lavoratore: ricerca corretta per codice e PIN
3. ✅ Aggiunte checkbox servizi (Wave, Orange Money, WhatsApp, Telegram, Signal) nello step 2
4. ✅ Reset menu su logout: torna alla home
5. ✅ Email obbligatoria nella candidatura
6. ✅ PDF con pagina credenziali accesso
7. ✅ Area lavoratore completa con tutti i dati modificabili
"""
import streamlit as st
import requests
from datetime import datetime
import random
from fpdf import FPDF
import pandas as pd

# ============================================
# CONFIGURAZIONE
# ============================================
st.set_page_config(
    page_title="Proacier - Ressources Humaines",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS SIDEBAR VERDE PROACIER
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
    border: 1px solid rgba(255,255,255,0.3) !important;
}
[data-testid="stSidebar"] button:hover {
    background-color: rgba(255,255,255,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

LOGO_URL = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/logo.png"
GOOGLE_SCRIPT_URL_ASSUNZIONI = "https://script.google.com/macros/s/AKfycbx_fgdqtE0AOdU79yU9UJ-4fuLHR4utpvDylbuWe_q3lZ91cJ2vGqJg1Dt5h5c2WDXGcA/exec"
GOOGLE_SCRIPT_URL_CANDIDATURE = "https://script.google.com/macros/s/AKfycbzlc2iOHSiNSWNvU21g4GqsGwMA4QQDJXTG_J3hkfe5Za8nyeTWb1amhuR2ULFI5b9k/exec"
PASSWORD_DASHBOARD = st.secrets.get("dashboard_password", "admin123")

# ============================================
# TRADUZIONI (SENZA SPAZI EXTRA)
# ============================================
TRADUZIONI = {
    "fr": {
        "titolo": " PROACIER - GESTION DES RESSOURCES HUMAINES",
        "sottotitolo": "Système de Recrutement - Sénégal",
        "lingua": "Langue",
        "nuova_assunzione": "📝 Transmission de Données",
        "candidatura_spontanea": " Candidature Spontanée",
        "dashboard": "Tableau de Bord",
        "area_lavoratore": "Espace Travailleur",
        "logout": "Déconnexion",
        "benvenuto": "Bienvenue",
        "password": "Mot de passe",
        "accedi": "Accéder",
        "codice": "Code",
        "pin": "PIN",
        "codice_errato": "Code ou PIN incorrect",
        "i_miei_dati": "Mes Données",
        "totale_operai": "Total Employés",
        "nessun_risultato": "Aucun résultat trouvé",
        "step_1": "1. Données Personnelles & Famille",
        "step_2": "2. Adresse, Documents & Services",
        "step_3": "3. Expérience Professionnelle",
        "step_4": "4. Compétences & Permis",
        "step_5": "5. Informations Médicales",
        "step_6": "6. Contact d'Urgence",
        "step_7": "7. Vêtements & EPI",
        "continua": "Continuer →",
        "indietro": "← Retour",
        "genera_pdf": "📄 J'accepte les conditions",
        "pdf_generato": "Enregistrement réussi !",
        "conserva_credenziali": "⚠️ CONSERVEZ CES IDENTIFIANTS",
        "codice_accesso": "Code d'accès",
        "pin_accesso": "PIN d'accès",
        "scarica": "Télécharger",
        "alert_condizioni": "En cliquant, vous certifiez l'exactitude des informations et acceptez les conditions.",
        "leggi_condizioni": "📋 Lire les conditions complètes",
        "checkbox_confirm": "J'ai lu et j'accepte les conditions générales et la politique de confidentialité",
        "errore_obbligatori": "Veuillez remplir tous les champs obligatoires (*)",
        "obbligatorio": "*",
        "cognome": "Nom",
        "nome": "Prénom(s)",
        "data_nascita": "Date de naissance",
        "giorno": "Jour",
        "mese": "Mois",
        "anno": "Année",
        "luogo_nascita": "Lieu de naissance",
        "nazionalita": "Nationalité",
        "paese_origine": "Pays d'origine",
        "sesso": "Sexe",
        "maschile": "Masculin",
        "femminile": "Féminin",
        "stato_civile": "État civil",
        "celibe": "Célibataire",
        "coniugato": "Marié(e)",
        "divorziato": "Divorcé(e)",
        "vedovo": "Veuf/Veuve",
        "numero_mogli": "Nombre d'épouses",
        "figli_totale": "Nombre total d'enfants",
        "residenza_moglie": "Lieu de résidence de l'épouse",
        "figli_moglie": "Nombre d'enfants avec cette épouse",
        "indirizzo": "Adresse actuelle",
        "quartiere": "Quartier/Village",
        "comune": "Commune",
        "regione_senegal": "Région",
        "telefono_1": "Téléphone principal",
        "telefono_2": "Téléphone secondaire",
        "telefono_3": "Téléphone 3",
        "cni": "N° CNI",
        "nif": "NIF",
        "css": "N° CSS",
        "cmu": "N° CMU",
        "ipres": "N° IPRES",
        "servizi_telefono": "Services associés au téléphone",
        "wave": "Wave",
        "orange_money": "Orange Money",
        "whatsapp": "WhatsApp",
        "telegram": "Telegram",
        "signal": "Signal",
        "nota_lavoro": "Indiquez vos 3 dernières expériences.",
        "azienda": "Entreprise",
        "mansione": "Fonction",
        "data_inizio": "Début",
        "data_fine": "Fin",
        "motivo_uscita": "Motif de départ",
        "nota_competenze": "Indiquez vos compétences principales.",
        "categoria_competenza": "Catégorie de compétence",
        "dettaglio_competenza": "Détails",
        "patente": "Permis de conduire",
        "nota_patente": "⚠️ Une photocopie du permis sera exigée.",
        "gruppo_sanguigno": "Groupe sanguin",
        "rh": "Rh",
        "allergie": "Allergies",
        "malattie": "Maladies chroniques",
        "idoneita": "Aptitude médicale",
        "apte": "Apte",
        "restriction": "Apte avec restriction",
        "inapte": "Inapte",
        "data_visita": "Date visite",
        "emergenza_nome": "Contact urgence (Nom)",
        "emergenza_parentela": "Lien",
        "emergenza_tel": "Tél urgence",
        "emergenza_indirizzo": "Adresse urgence",
        "cat_edilizia": "Bâtiment",
        "cat_contabilita": "Comptabilité",
        "cat_meccanica": "Mécanique",
        "cat_elettrico": "Électricité",
        "cat_agricoltura": "Agriculture",
        "cat_altro": "Autre",
        "taglia_maglia": "Taille t-shirt/polo",
        "taglia_pantaloni": "Taille pantalon",
        "taglia_scarpe": "Pointure chaussures",
        "taglia_giacca": "Taille veste/gilet",
        "taglia_cappello": "Taille casque/casquette",
        "taglia_guanti": "Taille gants",
        "opt_xs": "XS",
        "opt_s": "S",
        "opt_m": "M",
        "opt_l": "L",
        "opt_xl": "XL",
        "opt_xxl": "XXL",
        "opt_xxxl": "XXXL",
        "titolo_candidatura": "CANDIDATURE SPONTANÉE",
        "sottotitolo_candidatura": "Rejoignez l'équipe PROACIER.",
        "email": "Adresse Email",
        "mansione_richiesta": "Poste recherché",
        "opt_contabile": "Comptabilité / Admin",
        "opt_tecnico": "Technicien",
        "opt_operaio": "Ouvrier",
        "opt_autista": "Chauffeur",
        "opt_altro": "Autre",
        "studi": "Niveau d'études",
        "opt_media": "École moyenne",
        "opt_diploma": "Baccalauréat / Diplôme",
        "opt_laurea": "Université / Licence",
        "opt_prof": "Formation professionnelle",
        "skills": "Compétences / Skills",
        "esperienza_anno": "Années d'expérience",
        "salario_richiesto": "Prétention salariale (FCFA)",
        "note": "Notes supplémentaires",
        "invia_candidatura": "📤 Envoyer ma candidature",
        "candidatura_inviata": "✅ Candidature envoyée avec succès !",
        "errore_candidatura": "Veuillez remplir Nom, Prénom, Email et Téléphone.",
        "home_titolo": "📋 À quoi sert cette application?",
        "home_punto1_titolo": "Transmission de données pour nouveaux travailleurs",
        "home_punto1_desc1": "Formulaire complet en 7 étapes",
        "home_punto1_desc2": "Génération PDF automatique",
        "home_punto2_titolo": "Candidatures spontanées",
        "home_punto2_desc1": "Formulaire rapide",
        "home_punto2_desc2": "Évaluation par RH",
        "home_punto3_titolo": "Espace personnel travailleur",
        "home_punto3_desc1": "Accès avec code et PIN",
        "home_punto3_desc2": "Visualisation données",
        "home_punto4_titolo": "Paiement des journaliers",
        "home_punto4_desc1": "Gestion présences",
        "home_punto4_desc2": "Calcul compensi",
        "home_navigation": "🚀 Navigation rapide",
        "giornalieri_titolo": "Déjà travailleur?",
        "giornalieri_desc": "Accédez à votre espace personnel",
        "nuovo_giornaliero_titolo": "Nouveau / Journalier?",
        "nuovo_giornaliero_desc": "Transmettez vos données (pas un contrat)",
        "login_btn": "🔐 Connexion à mon espace",
        "trasmissione_btn": "📝 Transmettre mes données",
        "paese_senegal": "Sénégal",
        "paese_mali": "Mali",
        "paese_burkina": "Burkina Faso",
        "paese_sierra": "Sierra Leone",
        "paese_guinea": "Guinée",
        "paese_gambia": "Gambie",
        "paese_altro": "Autre pays",
        "avviso_non_contratto": "⚠️ Ceci n'est PAS un contrat d'embauche. Il s'agit uniquement d'une transmission de données à l'administration.",
        "avviso_regole_aziendali": "📋 En soumettant ce formulaire, vous acceptez les règles de l'entreprise et la politique de confidentialité de PROACIER.",
        "cocher_case": "Veuillez cocher la case de confirmation",
        "titolo_vestiario": " Tailles Vêtements",
        "pagina_condizioni": "📄 Lire les conditions complètes",
        "condizioni_titolo": "CONDITIONS GÉNÉRALES ET POLITIQUE DE CONFIDENTIALITÉ",
        "condizioni_testo": "Ces conditions régissent l'utilisation de notre système de recrutement.",
        "pdf_identifiants_titolo": "IDENTIFIANTS DE CONNEXION",
        "pdf_identifiants_desc": "Conservez précieusement ces identifiants:",
        "pdf_identifiants_avviso": "Ces identifiants sont personnels et confidentiels. Ne les partagez avec personne. Vous en aurez besoin pour accéder à votre espace personnel.",
        "sezione_dati_personali": " Données Personnelles (non modifiables)",
        "sezione_paga": "💰 Informations Salariales",
        "sezione_contatti": "📞 Coordonnées (modifiables)",
        "sezione_famille": "👨‍👩‍👧‍👦 Famille (modifiable)",
        "sezione_vestiario": "👕 Vêtements & EPI (modifiables)",
        "sezione_comunicazioni": "💬 Communications & Demandes",
        "paga_type": "Type de paiement",
        "paga_amount": "Montant",
        "paga_desc": "Votre salaire est géré par l'administration. Pour toute modification, contactez-nous.",
        "salva_modifiche": " Enregistrer les modifications",
        "modifiche_salvate": "✅ Modifications enregistrées avec succès ! Un email de notification a été envoyé à l'administration.",
        "errore_salvataggio": " Erreur lors de l'enregistrement. Veuillez réessayer.",
        "tipo_permesso": "Type de demande",
        "opt_permesso": "Permission (jour)",
        "opt_vacanza": "Vacances (plusieurs jours)",
        "opt_festa": "Fête religieuse",
        "opt_viaggio": "Voyage",
        "opt_malattia": "Maladie",
        "opt_altro_com": "Autre",
        "data_inizio_permesso": "Date de début",
        "data_fine_permesso": "Date de fin",
        "motivo_permesso": "Motif / Détails",
        "invia_richiesta": "📤 Envoyer la demande",
        "richiesta_inviata": "✅ Demande envoyée avec succès ! Vous recevrez une réponse de l'administration.",
        "lista_richieste": " Mes demandes précédentes",
        "stato_richiesta": "Statut",
        "stato_pending": "⏳ En attente",
        "stato_approved": "✅ Approuvée",
        "stato_rejected": "❌ Refusée",
        "risposta_admin": "Réponse de l'administration",
        "nessuna_richiesta": "Aucune demande précédente",
        "data_richiesta": "Date de la demande",
    },
    "it": {
        "titolo": "🏭 PROACIER - GESTIONE RISORSE UMANE",
        "sottotitolo": "Sistema di Reclutamento - Senegal",
        "lingua": "Lingua",
        "nuova_assunzione": "📝 Trasmissione Dati",
        "candidatura_spontanea": "📄 Candidatura Spontanea",
        "dashboard": "Dashboard",
        "area_lavoratore": "Spazio Lavoratore",
        "logout": "Esci",
        "benvenuto": "Benvenuto",
        "password": "Password",
        "accedi": "Accedi",
        "codice": "Codice",
        "pin": "PIN",
        "codice_errato": "Codice o PIN errati",
        "i_miei_dati": "I Miei Dati",
        "totale_operai": "Totale Dipendenti",
        "nessun_risultato": "Nessun risultato",
        "step_1": "1. Dati Personali e Famiglia",
        "step_2": "2. Indirizzo, Documenti e Servizi",
        "step_3": "3. Esperienza Professionale",
        "step_4": "4. Competenze e Patente",
        "step_5": "5. Informazioni Mediche",
        "step_6": "6. Contatto Emergenza",
        "step_7": "7. Vestiario e DPI",
        "continua": "Continua →",
        "indietro": "← Indietro",
        "genera_pdf": "📄 Accetto le condizioni",
        "pdf_generato": "Registrazione riuscita!",
        "conserva_credenziali": "⚠️ CONSERVA QUESTE CREDENZIALI",
        "codice_accesso": "Codice di accesso",
        "pin_accesso": "PIN di accesso",
        "scarica": "Scarica",
        "alert_condizioni": "Cliccando, certifichi l'esattezza delle informazioni e accetti le condizioni.",
        "leggi_condizioni": "📋 Leggi le condizioni complete",
        "checkbox_confirm": "Ho letto e accetto le condizioni generali e la politica sulla privacy",
        "errore_obbligatori": "Compila tutti i campi obbligatori (*)",
        "obbligatorio": "*",
        "cognome": "Cognome",
        "nome": "Nome",
        "data_nascita": "Data di nascita",
        "giorno": "Giorno",
        "mese": "Mese",
        "anno": "Anno",
        "luogo_nascita": "Luogo di nascita",
        "nazionalita": "Nazionalità",
        "paese_origine": "Paese di origine",
        "sesso": "Sesso",
        "maschile": "Maschile",
        "femminile": "Femminile",
        "stato_civile": "Stato civile",
        "celibe": "Celibe/Nubile",
        "coniugato": "Coniugato/a",
        "divorziato": "Divorziato/a",
        "vedovo": "Vedovo/a",
        "numero_mogli": "Numero di mogli",
        "figli_totale": "Numero totale di figli",
        "residenza_moglie": "Luogo di residenza della moglie",
        "figli_moglie": "Numero di figli con questa moglie",
        "indirizzo": "Indirizzo attuale",
        "quartiere": "Quartiere/Villaggio",
        "comune": "Comune",
        "regione_senegal": "Regione",
        "telefono_1": "Telefono principale",
        "telefono_2": "Telefono secondario",
        "telefono_3": "Telefono 3",
        "cni": "N° CNI",
        "nif": "NIF",
        "css": "N° CSS",
        "cmu": "N° CMU",
        "ipres": "N° IPRES",
        "servizi_telefono": "Servizi associati al telefono",
        "wave": "Wave",
        "orange_money": "Orange Money",
        "whatsapp": "WhatsApp",
        "telegram": "Telegram",
        "signal": "Signal",
        "nota_lavoro": "Indica le tue ultime 3 esperienze.",
        "azienda": "Azienda",
        "mansione": "Mansione",
        "data_inizio": "Inizio",
        "data_fine": "Fine",
        "motivo_uscita": "Motivo uscita",
        "nota_competenze": "Indica le tue competenze principali.",
        "categoria_competenza": "Categoria di competenza",
        "dettaglio_competenza": "Dettagli",
        "patente": "Patente di guida",
        "nota_patente": "⚠️ Sarà richiesta una fotocopia della patente.",
        "gruppo_sanguigno": "Gruppo sanguigno",
        "rh": "Rh",
        "allergie": "Allergie",
        "malattie": "Malattie croniche",
        "idoneita": "Idoneità medica",
        "apte": "Apto",
        "restriction": "Apto con restrizioni",
        "inapte": "Inapto",
        "data_visita": "Data visita",
        "emergenza_nome": "Contatto emergenza (Nome)",
        "emergenza_parentela": "Parentela",
        "emergenza_tel": "Tel emergenza",
        "emergenza_indirizzo": "Indirizzo emergenza",
        "cat_edilizia": "Edilizia",
        "cat_contabilita": "Contabilità",
        "cat_meccanica": "Meccanica",
        "cat_elettrico": "Elettrico",
        "cat_agricoltura": "Agricoltura",
        "cat_altro": "Altro",
        "taglia_maglia": "Taglia t-shirt/polo",
        "taglia_pantaloni": "Taglia pantalone",
        "taglia_scarpe": "Numero scarpe",
        "taglia_giacca": "Taglia giacca/gilet",
        "taglia_cappello": "Taglia casco/cappellino",
        "taglia_guanti": "Taglia guanti",
        "opt_xs": "XS",
        "opt_s": "S",
        "opt_m": "M",
        "opt_l": "L",
        "opt_xl": "XL",
        "opt_xxl": "XXL",
        "opt_xxxl": "XXXL",
        "titolo_candidatura": "CANDIDATURA SPONTANEA",
        "sottotitolo_candidatura": "Unisciti al team PROACIER.",
        "email": "Indirizzo Email",
        "mansione_richiesta": "Ruolo richiesto",
        "opt_contabile": "Contabilità / Admin",
        "opt_tecnico": "Tecnico",
        "opt_operaio": "Operaio",
        "opt_autista": "Autista",
        "opt_altro": "Altro",
        "studi": "Titolo di studio",
        "opt_media": "Licenza media",
        "opt_diploma": "Diploma",
        "opt_laurea": "Laurea",
        "opt_prof": "Formazione professionale",
        "skills": "Competenze / Skills",
        "esperienza_anno": "Anni di esperienza",
        "salario_richiesto": "Retribuzione richiesta (FCFA)",
        "note": "Note aggiuntive",
        "invia_candidatura": "📤 Invia la mia candidatura",
        "candidatura_inviata": "✅ Candidatura inviata con successo!",
        "errore_candidatura": "Compila Cognome, Nome, Email e Telefono.",
        "home_titolo": "📋 A cosa serve questa applicazione?",
        "home_punto1_titolo": "Trasmissione dati nuovi lavoratori",
        "home_punto1_desc1": "Modulo completo in 7 fasi",
        "home_punto1_desc2": "Generazione PDF automatica",
        "home_punto2_titolo": "Candidature spontanee",
        "home_punto2_desc1": "Modulo rapido",
        "home_punto2_desc2": "Valutazione da parte HR",
        "home_punto3_titolo": "Spazio personale lavoratore",
        "home_punto3_desc1": "Accesso con codice e PIN",
        "home_punto3_desc2": "Visualizzazione dati",
        "home_punto4_titolo": "Pagamento giornalieri",
        "home_punto4_desc1": "Gestione presenze",
        "home_punto4_desc2": "Calcolo compensi",
        "home_navigation": "🚀 Navigazione rapida",
        "giornalieri_titolo": "Già lavoratore?",
        "giornalieri_desc": "Accedi al tuo spazio",
        "nuovo_giornaliero_titolo": "Nuovo / Giornaliero?",
        "nuovo_giornaliero_desc": "Trasmetti dati (non contratto)",
        "login_btn": "🔐 Accedi al mio spazio",
        "trasmissione_btn": "📝 Trasmetti i miei dati",
        "paese_senegal": "Senegal",
        "paese_mali": "Mali",
        "paese_burkina": "Burkina Faso",
        "paese_sierra": "Sierra Leone",
        "paese_guinea": "Guinea",
        "paese_gambia": "Gambia",
        "paese_altro": "Altro paese",
        "avviso_non_contratto": "⚠️ Questo NON è un contratto di assunzione. Si tratta solo di una trasmissione di dati all'amministrazione.",
        "avviso_regole_aziendali": "📋 Inviando questo modulo, accetti le regole aziendali e la politica sulla privacy di PROACIER.",
        "cocher_case": "Per favore seleziona la casella di conferma",
        "titolo_vestiario": "👕 Taglie Abbigliamento",
        "pagina_condizioni": "📄 Leggi le condizioni complete",
        "condizioni_titolo": "CONDIZIONI GENERALI E POLITICA SULLA PRIVACY",
        "condizioni_testo": "Queste condizioni regolano l'utilizzo del nostro sistema di reclutamento.",
        "pdf_identifiants_titolo": "CREDENZIALI DI ACCESSO",
        "pdf_identifiants_desc": "Conserva con cura queste credenziali:",
        "pdf_identifiants_avviso": "Queste credenziali sono personali e confidenziali. Non condividerle con nessuno. Ti serviranno per accedere al tuo spazio personale.",
        "sezione_dati_personali": " Dati Personali (non modificabili)",
        "sezione_paga": "💰 Informazioni Salariali",
        "sezione_contatti": " Contatti (modificabili)",
        "sezione_famille": "👨‍👩‍👧‍ Famiglia (modificabile)",
        "sezione_vestiario": "👕 Vestiario e DPI (modificabili)",
        "sezione_comunicazioni": "💬 Comunicazioni e Richieste",
        "paga_type": "Tipo di pagamento",
        "paga_amount": "Importo",
        "paga_desc": "Il tuo salario è gestito dall'amministrazione. Per modifiche, contattaci.",
        "salva_modifiche": "💾 Salva modifiche",
        "modifiche_salvate": "✅ Modifiche salvate con successo! Una email di notifica è stata inviata all'amministrazione.",
        "errore_salvataggio": "❌ Errore durante il salvataggio. Riprova.",
        "tipo_permesso": "Tipo di richiesta",
        "opt_permesso": "Permesso (giornata)",
        "opt_vacanza": "Vacanze (più giorni)",
        "opt_festa": "Festa religiosa",
        "opt_viaggio": "Viaggio",
        "opt_malattia": "Malattia",
        "opt_altro_com": "Altro",
        "data_inizio_permesso": "Data di inizio",
        "data_fine_permesso": "Data di fine",
        "motivo_permesso": "Motivo / Dettagli",
        "invia_richiesta": "📤 Invia richiesta",
        "richiesta_inviata": "✅ Richiesta inviata con successo! Riceverai una risposta dall'amministrazione.",
        "lista_richieste": "📋 Le mie richieste precedenti",
        "stato_richiesta": "Stato",
        "stato_pending": "⏳ In attesa",
        "stato_approved": "✅ Approvata",
        "stato_rejected": "❌ Rifiutata",
        "risposta_admin": "Risposta dell'amministrazione",
        "nessuna_richiesta": "Nessuna richiesta precedente",
        "data_richiesta": "Data della richiesta",
    },
    "en": {
        "titolo": " PROACIER - HUMAN RESOURCES",
        "sottotitolo": "Recruitment System - Senegal",
        "lingua": "Language",
        "nuova_assunzione": "📝 Data Transmission",
        "candidatura_spontanea": "📄 Spontaneous Application",
        "dashboard": "Dashboard",
        "area_lavoratore": "Worker Space",
        "logout": "Logout",
        "benvenuto": "Welcome",
        "password": "Password",
        "accedi": "Login",
        "codice": "Code",
        "pin": "PIN",
        "codice_errato": "Wrong code or PIN",
        "i_miei_dati": "My Data",
        "totale_operai": "Total Employees",
        "nessun_risultato": "No results found",
        "step_1": "1. Personal Data & Family",
        "step_2": "2. Address, Documents & Services",
        "step_3": "3. Professional Experience",
        "step_4": "4. Skills & License",
        "step_5": "5. Medical Information",
        "step_6": "6. Emergency Contact",
        "step_7": "7. Clothing & PPE",
        "continua": "Continue →",
        "indietro": "← Back",
        "genera_pdf": "📄 I accept the conditions",
        "pdf_generato": "Registration successful!",
        "conserva_credenziali": "⚠️ SAVE THESE CREDENTIALS",
        "codice_accesso": "Access code",
        "pin_accesso": "Access PIN",
        "scarica": "Download",
        "alert_condizioni": "By clicking, you certify the accuracy of the information and accept the conditions.",
        "leggi_condizioni": " Read full conditions",
        "checkbox_confirm": "I have read and accept the general conditions and privacy policy",
        "errore_obbligatori": "Please fill in all required fields (*)",
        "obbligatorio": "*",
        "cognome": "Surname",
        "nome": "First Name",
        "data_nascita": "Date of birth",
        "giorno": "Day",
        "mese": "Month",
        "anno": "Year",
        "luogo_nascita": "Place of birth",
        "nazionalita": "Nationality",
        "paese_origine": "Country of origin",
        "sesso": "Gender",
        "maschile": "Male",
        "femminile": "Female",
        "stato_civile": "Marital status",
        "celibe": "Single",
        "coniugato": "Married",
        "divorziato": "Divorced",
        "vedovo": "Widowed",
        "numero_mogli": "Number of wives",
        "figli_totale": "Total number of children",
        "residenza_moglie": "Wife's residence",
        "figli_moglie": "Children with this wife",
        "indirizzo": "Current address",
        "quartiere": "District/Village",
        "comune": "Municipality",
        "regione_senegal": "Region",
        "telefono_1": "Main phone",
        "telefono_2": "Secondary phone",
        "telefono_3": "Phone 3",
        "cni": "ID Number (CNI)",
        "nif": "NIF",
        "css": "Social Security (CSS)",
        "cmu": "CMU",
        "ipres": "IPRES",
        "servizi_telefono": "Phone services",
        "wave": "Wave",
        "orange_money": "Orange Money",
        "whatsapp": "WhatsApp",
        "telegram": "Telegram",
        "signal": "Signal",
        "nota_lavoro": "Indicate your last 3 experiences.",
        "azienda": "Company",
        "mansione": "Position",
        "data_inizio": "Start",
        "data_fine": "End",
        "motivo_uscita": "Reason for leaving",
        "nota_competenze": "Indicate your main skills.",
        "categoria_competenza": "Skill category",
        "dettaglio_competenza": "Details",
        "patente": "Driver's license",
        "nota_patente": "⚠️ A photocopy of the license will be required.",
        "gruppo_sanguigno": "Blood type",
        "rh": "Rh",
        "allergie": "Allergies",
        "malattie": "Chronic diseases",
        "idoneita": "Medical fitness",
        "apte": "Fit",
        "restriction": "Fit with restrictions",
        "inapte": "Unfit",
        "data_visita": "Visit date",
        "emergenza_nome": "Emergency contact (Name)",
        "emergenza_parentela": "Relationship",
        "emergenza_tel": "Emergency phone",
        "emergenza_indirizzo": "Emergency address",
        "cat_edilizia": "Construction",
        "cat_contabilita": "Accounting",
        "cat_meccanica": "Mechanics",
        "cat_elettrico": "Electrical",
        "cat_agricoltura": "Agriculture",
        "cat_altro": "Other",
        "taglia_maglia": "T-shirt/polo size",
        "taglia_pantaloni": "Pants size",
        "taglia_scarpe": "Shoe size",
        "taglia_giacca": "Jacket/vest size",
        "taglia_cappello": "Helmet/cap size",
        "taglia_guanti": "Gloves size",
        "opt_xs": "XS",
        "opt_s": "S",
        "opt_m": "M",
        "opt_l": "L",
        "opt_xl": "XL",
        "opt_xxl": "XXL",
        "opt_xxxl": "XXXL",
        "titolo_candidatura": "SPONTANEOUS APPLICATION",
        "sottotitolo_candidatura": "Join the PROACIER team.",
        "email": "Email Address",
        "mansione_richiesta": "Desired position",
        "opt_contabile": "Accounting / Admin",
        "opt_tecnico": "Technician",
        "opt_operaio": "Worker",
        "opt_autista": "Driver",
        "opt_altro": "Other",
        "studi": "Education level",
        "opt_media": "Middle school",
        "opt_diploma": "High school / Diploma",
        "opt_laurea": "University / Degree",
        "opt_prof": "Vocational training",
        "skills": "Skills / Competencies",
        "esperienza_anno": "Years of experience",
        "salario_richiesto": "Expected salary (FCFA)",
        "note": "Additional notes",
        "invia_candidatura": "📤 Submit my application",
        "candidatura_inviata": "✅ Application submitted successfully!",
        "errore_candidatura": "Please fill in Surname, First Name, Email, and Phone.",
        "home_titolo": "📋 What is this application for?",
        "home_punto1_titolo": "Data transmission new workers",
        "home_punto1_desc1": "Complete form in 7 steps",
        "home_punto1_desc2": "Automatic PDF generation",
        "home_punto2_titolo": "Spontaneous applications",
        "home_punto2_desc1": "Quick form",
        "home_punto2_desc2": "HR evaluation",
        "home_punto3_titolo": "Personal worker space",
        "home_punto3_desc1": "Access with code and PIN",
        "home_punto3_desc2": "Data visualization",
        "home_punto4_titolo": "Daily workers payment",
        "home_punto4_desc1": "Attendance management",
        "home_punto4_desc2": "Payment calculation",
        "home_navigation": "🚀 Quick navigation",
        "giornalieri_titolo": "Already a worker?",
        "giornalieri_desc": "Access your space",
        "nuovo_giornaliero_titolo": "New / Daily worker?",
        "nuovo_giornaliero_desc": "Submit data (not contract)",
        "login_btn": "🔐 Login to my space",
        "trasmissione_btn": "📝 Submit my data",
        "paese_senegal": "Senegal",
        "paese_mali": "Mali",
        "paese_burkina": "Burkina Faso",
        "paese_sierra": "Sierra Leone",
        "paese_guinea": "Guinea",
        "paese_gambia": "Gambia",
        "paese_altro": "Other country",
        "avviso_non_contratto": "⚠️ This is NOT an employment contract. This is only a data transmission to the administration.",
        "avviso_regole_aziendali": "📋 By submitting this form, you accept the company rules and PROACIER's privacy policy.",
        "cocher_case": "Please check the confirmation box",
        "titolo_vestiario": "👕 Clothing Sizes",
        "pagina_condizioni": "📄 Read full conditions",
        "condizioni_titolo": "GENERAL CONDITIONS AND PRIVACY POLICY",
        "condizioni_testo": "These conditions govern the use of our recruitment system.",
        "pdf_identifiants_titolo": "ACCESS CREDENTIALS",
        "pdf_identifiants_desc": "Keep these credentials safe:",
        "pdf_identifiants_avviso": "These credentials are personal and confidential. Do not share them with anyone. You will need them to access your personal space.",
        "sezione_dati_personali": " Personal Data (non-modifiable)",
        "sezione_paga": "💰 Salary Information",
        "sezione_contatti": "📞 Contact Info (modifiable)",
        "sezione_famille": "👨‍👩‍👧‍👦 Family (modifiable)",
        "sezione_vestiario": " Clothing & PPE (modifiable)",
        "sezione_comunicazioni": "💬 Communications & Requests",
        "paga_type": "Payment type",
        "paga_amount": "Amount",
        "paga_desc": "Your salary is managed by administration. For changes, contact us.",
        "salva_modifiche": "💾 Save changes",
        "modifiche_salvate": "✅ Changes saved successfully! A notification email has been sent to administration.",
        "errore_salvataggio": "❌ Error saving. Please try again.",
        "tipo_permesso": "Request type",
        "opt_permesso": "Permission (day)",
        "opt_vacanza": "Vacation (multiple days)",
        "opt_festa": "Religious holiday",
        "opt_viaggio": "Travel",
        "opt_malattia": "Sickness",
        "opt_altro_com": "Other",
        "data_inizio_permesso": "Start date",
        "data_fine_permesso": "End date",
        "motivo_permesso": "Reason / Details",
        "invia_richiesta": "📤 Submit request",
        "richiesta_inviata": "✅ Request submitted successfully! You will receive a response from administration.",
        "lista_richieste": " My previous requests",
        "stato_richiesta": "Status",
        "stato_pending": "⏳ Pending",
        "stato_approved": "✅ Approved",
        "stato_rejected": "❌ Rejected",
        "risposta_admin": "Administration response",
        "nessuna_richiesta": "No previous requests",
        "data_richiesta": "Request date",
    }
}

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
            st.error(f"Erreur HTTP: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return False

def leggi_da_google_sheet(url_script):
    try:
        response = requests.get(url_script, timeout=30)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.error(f"Errore lettura: {e}")
        return []

# ============================================
# GENERATORE PDF CON PAGINA DATI DI ACCESSO
# ============================================
class PDFProacier(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(94, 165, 41)
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
    
    # PAGINA 1: DATI PERSONALI
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 5, f"N° fiche: {dati.get('codice', '')}", 0, 0)
    pdf.cell(0, 5, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'R')
    pdf.ln(2)
    
    pdf.sezione("1. IDENTITE & FAMILLE")
    pdf.campo_doppio("Nom:", dati.get('cognome', ''), "Prenom(s):", dati.get('nome', ''))
    pdf.campo_doppio("Ne(e) le:", dati.get('data_nascita', ''), "a:", dati.get('luogo_nascita', ''))
    pdf.campo_doppio("Nationalite:", dati.get('nazionalita', ''), "Pays:", dati.get('paese_origine', ''))
    pdf.campo_doppio("Etat civil:", dati.get('stato_civile', ''), "Enfants:", dati.get('figli_totale', ''))
    if dati.get('numero_mogli', 0) > 0:
        pdf.campo("Epouses:", f"{dati.get('numero_mogli')}")
    pdf.ln(1)
    
    pdf.sezione("2. CONTACT & DOCUMENTS")
    pdf.campo("Adresse:", f"{dati.get('indirizzo', '')}, {dati.get('quartiere', '')}, {dati.get('regione_senegal', '')}")
    pdf.campo_doppio("Tel 1:", dati.get('telefono_1', ''), "Tel 2:", dati.get('telefono_2', ''))
    pdf.campo_doppio("CNI:", dati.get('cni', ''), "CSS:", dati.get('css', ''))
    pdf.ln(1)
    
    pdf.sezione("3. EXPERIENCE & COMPETENCES")
    pdf.campo("Poste:", dati.get('mansione_1', ''))
    pdf.campo("Competence:", f"{dati.get('categoria_competenza', '')} - {dati.get('dettaglio_competenza', '')}")
    pdf.campo("Permis:", dati.get('patente', ''))
    pdf.ln(1)
    
    pdf.sezione("4. VETEMENTS & EPI")
    pdf.campo_doppio("Taille T-shirt:", dati.get('taglia_maglia', ''), "Taille Pantalon:", dati.get('taglia_pantaloni', ''))
    pdf.campo_doppio("Pointure:", dati.get('taglia_scarpe', ''), "Taille Gilet:", dati.get('taglia_giacca', ''))
    pdf.ln(1)
    
    pdf.sezione("5. MEDICAL & URGENCE")
    pdf.campo_doppio("Groupe:", f"{dati.get('gruppo_sanguigno', '')} {dati.get('rh', '')}", "Aptitude:", dati.get('idoneita', ''))
    pdf.campo_doppio("Contact:", dati.get('emergenza_nome', ''), "Tel:", dati.get('emergenza_tel', ''))
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'I', 8)
    pdf.multi_cell(0, 4, "Je certifie l'exactitude des informations et accepte les conditions.")
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(95, 6, 'CANDIDAT', 1, 0, 'C')
    pdf.cell(95, 6, 'EMPLOYEUR', 1, 1, 'C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(95, 15, '', 1, 0)
    pdf.cell(95, 15, '', 1, 1)
    
    # PAGINA 2: CONSENSO PRIVACY
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 10, 'CONSENTEMENT DONNEES PERSONNELLES', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 9)
    pdf.multi_cell(0, 5, "Conformement a la Loi n° 2008-12 du 25 janvier 2008 (Senegal).")
    pdf.ln(10)
    pdf.cell(0, 6, 'Signature:', 0, 1)
    pdf.cell(0, 20, '', 1, 1)
    
    # PAGINA 3: DATI DI ACCESSO (IMPORTANTE!)
    pdf.add_page()
    pdf.set_fill_color(255, 243, 205)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, dati.get('pdf_identifiants_titolo', 'IDENTIFIANTS DE CONNEXION'), 0, 1, 'C', True)
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, dati.get('pdf_identifiants_desc', 'Conservez precieusement ces identifiants:'), 0, 1, 'C')
    pdf.ln(5)
    
    # Codice e PIN in grande
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 12, f"Code d'acces: {dati.get('codice', '___________')}", 0, 1, 'C')
    pdf.ln(3)
    pdf.cell(0, 12, f"PIN: {dati.get('pin', '___________')}", 0, 1, 'C')
    pdf.ln(5)
    
    # Avviso
    pdf.set_font('Helvetica', 'I', 9)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 5, dati.get('pdf_identifiants_avviso', 'Ces identifiants sont personnels et confidentiels.'))
    pdf.set_text_color(0, 0, 0)
    
    pdf_bytes = pdf.output(dest='S')
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1', errors='ignore')
    return bytes(pdf_bytes)

# ============================================
# STEP DEL FORMULARIO (7 STEP)
# ============================================
def step_1_personale_famiglia(lingua):
    st.subheader(get_testo("step_1", lingua))
    col1, col2 = st.columns(2)
    with col1:
        cognome = st.text_input(f"{get_testo('cognome', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.dati_form.get('cognome', ''), key="s1_cognome")
        nome = st.text_input(f"{get_testo('nome', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.dati_form.get('nome', ''), key="s1_nome")
        st.markdown(f"**{get_testo('data_nascita', lingua)}**")
        cg, cm, ca = st.columns(3)
        with cg:
            giorno = st.selectbox(get_testo("giorno", lingua), list(range(1, 32)), index=st.session_state.dati_form.get('giorno', 0), key="s1_g")
        with cm:
            mese = st.selectbox(get_testo("mese", lingua), list(range(1, 13)), index=st.session_state.dati_form.get('mese', 0), key="s1_m")
        with ca:
            anno = st.selectbox(get_testo("anno", lingua), list(range(1950, 2010)), index=st.session_state.dati_form.get('anno', 30), key="s1_a")
        data_nascita_str = f"{giorno:02d}/{mese:02d}/{anno}"
        luogo_nascita = st.text_input(get_testo("luogo_nascita", lingua), value=st.session_state.dati_form.get('luogo_nascita', ''), key="s1_luogo")
        
        paesi = [get_testo("paese_senegal", lingua), get_testo("paese_mali", lingua), 
                 get_testo("paese_burkina", lingua), get_testo("paese_sierra", lingua),
                 get_testo("paese_guinea", lingua), get_testo("paese_gambia", lingua),
                 get_testo("paese_altro", lingua)]
        nazionalita_sel = st.selectbox(get_testo("nazionalita", lingua), paesi, index=0, key="s1_naz")
        if nazionalita_sel == get_testo("paese_altro", lingua):
            nazionalita = st.text_input("Précisez votre nationalité:", key="s1_naz_altro")
        else:
            nazionalita = nazionalita_sel
        
        paese_origine_sel = st.selectbox(get_testo("paese_origine", lingua), paesi, index=0, key="s1_paese")
        if paese_origine_sel == get_testo("paese_altro", lingua):
            paese_origine = st.text_input("Précisez votre pays:", key="s1_paese_altro")
        else:
            paese_origine = paese_origine_sel
            
    with col2:
        sesso = st.selectbox(get_testo("sesso", lingua), [get_testo("maschile", lingua), get_testo("femminile", lingua)], key="s1_sesso")
        stato_civile = st.selectbox(get_testo("stato_civile", lingua), [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)], key="s1_stato")
        numero_mogli, dettagli_mogli = 0, ""
        figli_totale_calcolato = 0
        if stato_civile == get_testo("coniugato", lingua):
            numero_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4, value=1, key="s1_mogli")
            dettagli = []
            for i in range(1, numero_mogli + 1):
                st.markdown(f"**Épouse {i}**")
                c_res, c_fig = st.columns(2)
                with c_res:
                    res = st.text_input(get_testo("residenza_moglie", lingua) + f" {i}", key=f"s1_res_{i}")
                with c_fig:
                    fig = st.number_input(get_testo("figli_moglie", lingua) + f" {i}", min_value=0, value=0, key=f"s1_fig_{i}")
                    figli_totale_calcolato += fig
                dettagli.append(f"Épouse {i}: {res} ({fig} enfants)")
            dettagli_mogli = " | ".join(dettagli)
        st.info(f"**{get_testo('figli_totale', lingua)}: {figli_totale_calcolato}**")
    
    return {"cognome": cognome, "nome": nome, "data_nascita": data_nascita_str, "luogo_nascita": luogo_nascita,
            "nazionalita": nazionalita, "paese_origine": paese_origine, "sesso": sesso, "stato_civile": stato_civile,
            "numero_mogli": numero_mogli, "dettagli_mogli": dettagli_mogli, "figli_totale": figli_totale_calcolato}

def step_2_residenza_documenti(lingua):
    st.subheader(get_testo("step_2", lingua))
    col1, col2 = st.columns(2)
    with col1:
        indirizzo = st.text_input(f"{get_testo('indirizzo', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.dati_form.get('indirizzo', ''), key="s2_ind")
        quartiere = st.text_input(get_testo("quartiere", lingua), value=st.session_state.dati_form.get('quartiere', ''), key="s2_quart")
        comune = st.text_input(get_testo("comune", lingua), value=st.session_state.dati_form.get('comune', ''), key="s2_com")
        regione_senegal = st.selectbox(get_testo("regione_senegal", lingua), ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", "Louga", "Matam", "Autre"], key="s2_reg")
    with col2:
        tel1 = st.text_input(f"{get_testo('telefono_1', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.dati_form.get('telefono_1', ''), key="s2_tel1")
        tel2 = st.text_input(get_testo("telefono_2", lingua), value=st.session_state.dati_form.get('telefono_2', ''), key="s2_tel2")
        tel3 = st.text_input(get_testo("telefono_3", lingua), value=st.session_state.dati_form.get('telefono_3', ''), key="s2_tel3")
        cni = st.text_input(f"{get_testo('cni', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.dati_form.get('cni', ''), key="s2_cni")
        nif = st.text_input(get_testo("nif", lingua), value=st.session_state.dati_form.get('nif', ''), key="s2_nif")
        css = st.text_input(f"{get_testo('css', lingua)} {get_testo('obbligatorio', lingua)}", value=st.session_state.dati_form.get('css', ''), key="s2_css")
        cmu = st.text_input(get_testo("cmu", lingua), value=st.session_state.dati_form.get('cmu', ''), key="s2_cmu")
        ipres = st.text_input(get_testo("ipres", lingua), value=st.session_state.dati_form.get('ipres', ''), key="s2_ipres")
    
    # CHECKBOX SERVIZI TELEFONO
    st.markdown("---")
    st.subheader(get_testo("servizi_telefono", lingua))
    col3, col4 = st.columns(2)
    with col3:
        wave = st.checkbox(get_testo("wave", lingua), value=st.session_state.dati_form.get('wave', False), key="s2_wave")
        orange_money = st.checkbox(get_testo("orange_money", lingua), value=st.session_state.dati_form.get('orange_money', False), key="s2_orange")
        whatsapp = st.checkbox(get_testo("whatsapp", lingua), value=st.session_state.dati_form.get('whatsapp', False), key="s2_whatsapp")
    with col4:
        telegram = st.checkbox(get_testo("telegram", lingua), value=st.session_state.dati_form.get('telegram', False), key="s2_telegram")
        signal = st.checkbox(get_testo("signal", lingua), value=st.session_state.dati_form.get('signal', False), key="s2_signal")
    
    return {"indirizzo": indirizzo, "quartiere": quartiere, "comune": comune, "regione_senegal": regione_senegal,
            "telefono_1": tel1, "telefono_2": tel2, "telefono_3": tel3, "cni": cni, "nif": nif, "css": css, "cmu": cmu, "ipres": ipres,
            "wave": wave, "orange_money": orange_money, "whatsapp": whatsapp, "telegram": telegram, "signal": signal}

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
    return {"emergenza_nome": em_nome, "emergenza_parentela": em_parentela, "emergenza_tel": em_tel, "emergenza_indirizzo": em_ind}

def step_7_vestiario(lingua):
    st.subheader(get_testo("step_7", lingua))
    st.markdown(f"### {get_testo('titolo_vestiario', lingua)}")
    col1, col2 = st.columns(2)
    with col1:
        taglie_maglia = [get_testo("opt_xs", lingua), get_testo("opt_s", lingua), get_testo("opt_m", lingua), 
                       get_testo("opt_l", lingua), get_testo("opt_xl", lingua), get_testo("opt_xxl", lingua), get_testo("opt_xxxl", lingua)]
        taglia_maglia = st.selectbox(get_testo("taglia_maglia", lingua), taglie_maglia, key="s7_maglia")
        
        taglie_pantaloni = ["38", "40", "42", "44", "46", "48", "50", "52"]
        taglia_pantaloni = st.selectbox(get_testo("taglia_pantaloni", lingua), taglie_pantaloni, key="s7_pantaloni")
        
        taglie_scarpe = ["38", "39", "40", "41", "42", "43", "44", "45", "46", "47"]
        taglia_scarpe = st.selectbox(get_testo("taglia_scarpe", lingua), taglie_scarpe, key="s7_scarpe")
    with col2:
        taglie_giacca = [get_testo("opt_xs", lingua), get_testo("opt_s", lingua), get_testo("opt_m", lingua), 
                       get_testo("opt_l", lingua), get_testo("opt_xl", lingua), get_testo("opt_xxl", lingua)]
        taglia_giacca = st.selectbox(get_testo("taglia_giacca", lingua), taglie_giacca, key="s7_giacca")
        
        taglie_cappello = ["S", "M", "L", "XL"]
        taglia_cappello = st.selectbox(get_testo("taglia_cappello", lingua), taglie_cappello, key="s7_cappello")
        
        taglie_guanti = ["S", "M", "L", "XL"]
        taglia_guanti = st.selectbox(get_testo("taglia_guanti", lingua), taglie_guanti, key="s7_guanti")
    
    return {"taglia_maglia": taglia_maglia, "taglia_pantaloni": taglia_pantaloni, "taglia_scarpe": taglia_scarpe,
            "taglia_giacca": taglia_giacca, "taglia_cappello": taglia_cappello, "taglia_guanti": taglia_guanti}

# ============================================
# PAGINA CONDIZIONI (INTERNA)
# ============================================
def pagina_condizioni(lingua):
    st.title(get_testo("condizioni_titolo", lingua))
    st.markdown("---")
    st.markdown(get_testo("condizioni_testo", lingua))
    
    st.markdown("---")
    st.subheader("📋 Article 1 - Objet")
    st.markdown("""
    Les présentes conditions régissent l'utilisation du système de recrutement de PROACIER.
    En soumettant vos données, vous acceptez le traitement de vos informations personnelles
    conformément à la Loi n° 2008-12 du 25 janvier 2008 relative à la protection des données 
    personnelles au Sénégal.
    """)
    
    st.subheader("🔒 Article 2 - Protection des données")
    st.markdown("""
    Vos données personnelles sont collectées uniquement à des fins de recrutement et de 
    gestion du personnel. Elles sont conservées de manière confidentielle et ne sont pas 
    partagées avec des tiers sans votre consentement.
    """)
    
    st.subheader("👤 Article 3 - Droits du candidat")
    st.markdown("""
    Conformément à la législation en vigueur, vous disposez d'un droit d'accès, de 
    rectification et de suppression de vos données personnelles. Pour exercer ces droits, 
    contactez l'administration de PROACIER.
    """)
    
    st.markdown("---")
    st.info("ℹ️ Questo testo è provvisorio. Le condizioni definitive verranno scritte insieme.")
    
    if st.button("← Retour", use_container_width=True):
        st.session_state.pagina = 'registrazione'
        st.rerun()

# ============================================
# PAGINA CANDIDATURA SPONTANEA (FIX ERRORI)
# ============================================
def pagina_candidatura_spontanea(lingua):
    st.title(get_testo("titolo_candidatura", lingua))
    st.markdown(get_testo("sottotitolo_candidatura", lingua))
    st.info("ℹ️ Ceci n'est PAS un contrat, mais seulement l'envoi de votre candidature.")
    st.markdown("---")
    
    # Inizializza session state
    if 'candidatura_dati' not in st.session_state:
        st.session_state.candidatura_dati = {}
    
    with st.form("form_candidatura", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            c_cognome = st.text_input(f"{get_testo('cognome', lingua)} {get_testo('obbligatorio', lingua)}", 
                                    value=st.session_state.candidatura_dati.get('cognome', ''), key="c_cognome")
            c_nome = st.text_input(f"{get_testo('nome', lingua)} {get_testo('obbligatorio', lingua)}", 
                                 value=st.session_state.candidatura_dati.get('nome', ''), key="c_nome")
            c_email = st.text_input(f"{get_testo('email', lingua)} {get_testo('obbligatorio', lingua)}", 
                                  value=st.session_state.candidatura_dati.get('email', ''), key="c_email")
            c_tel = st.text_input(f"{get_testo('telefono_1', lingua)} {get_testo('obbligatorio', lingua)}", 
                                value=st.session_state.candidatura_dati.get('telefono', ''), key="c_tel")
            st.markdown(f"**{get_testo('data_nascita', lingua)}**")
            cg, cm, ca = st.columns(3)
            with cg:
                g = st.selectbox(get_testo("giorno", lingua), list(range(1, 32)), 
                               index=st.session_state.candidatura_dati.get('g', 0), key="c_g")
            with cm:
                m = st.selectbox(get_testo("mese", lingua), list(range(1, 13)), 
                               index=st.session_state.candidatura_dati.get('m', 0), key="c_m")
            with ca:
                a = st.selectbox(get_testo("anno", lingua), list(range(1960, 2010)), 
                               index=st.session_state.candidatura_dati.get('a', 30), key="c_a")
            c_data_nascita = f"{g:02d}/{m:02d}/{a}"
        with col2:
            c_indirizzo = st.text_input(get_testo("indirizzo", lingua), 
                                      value=st.session_state.candidatura_dati.get('indirizzo', ''), key="c_ind")
            c_comune = st.text_input(get_testo("comune", lingua), 
                                   value=st.session_state.candidatura_dati.get('comune', ''), key="c_com")
            c_regione = st.selectbox(get_testo("regione_senegal", lingua), 
                                   ["Thiès", "Tivaouane", "Mbour", "Dakar", "Saint-Louis", "Ziguinchor", 
                                    "Kolda", "Tambacounda", "Kaolack", "Fatick", "Kédougou", "Kaffrine", 
                                    "Louga", "Matam", "Autre"], 
                                   index=0, key="c_reg")
            c_mansione = st.selectbox(get_testo("mansione_richiesta", lingua), [
                get_testo("opt_contabile", lingua), get_testo("opt_tecnico", lingua), 
                get_testo("opt_operaio", lingua), get_testo("opt_autista", lingua), get_testo("opt_altro", lingua)
            ], key="c_man")
            c_studi = st.selectbox(get_testo("studi", lingua), [
                get_testo("opt_media", lingua), get_testo("opt_diploma", lingua), 
                get_testo("opt_laurea", lingua), get_testo("opt_prof", lingua)
            ], key="c_studi")
        c_skills = st.text_area(get_testo("skills", lingua), 
                              value=st.session_state.candidatura_dati.get('skills', ''), key="c_skills")
        col3, col4 = st.columns(2)
        with col3:
            c_esperienza = st.number_input(get_testo("esperienza_anno", lingua), min_value=0, max_value=50, 
                                         value=st.session_state.candidatura_dati.get('esperienza', 0), key="c_exp")
        with col4:
            c_salario = st.text_input(get_testo("salario_richiesto", lingua), 
                                    value=st.session_state.candidatura_dati.get('salario', ''), key="c_sal")
        c_note = st.text_area(get_testo("note", lingua), 
                            value=st.session_state.candidatura_dati.get('note', ''), key="c_note")
        
        submitted = st.form_submit_button(get_testo("invia_candidatura", lingua), type="primary", use_container_width=True)
        
        if submitted:
            # FIX: Salva i dati PRIMA della validazione
            st.session_state.candidatura_dati = {
                'cognome': c_cognome, 'nome': c_nome, 'email': c_email, 'telefono': c_tel,
                'g': g, 'm': m, 'a': a, 'indirizzo': c_indirizzo, 'comune': c_comune,
                'regione': c_regione, 'skills': c_skills, 'esperienza': c_esperienza,
                'salario': c_salario, 'note': c_note
            }
            
            # Validazione DOPO aver salvato
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
                st.balloons()
                st.session_state.candidatura_dati = {}
            else:
                st.error("Erreur de connexion. Veuillez réessayer.")

# ============================================
# PAGINA AREA LAVORATORE COMPLETA
# ============================================
def pagina_area_lavoratore_completa(lingua):
    if not st.session_state.get('logged_in') or st.session_state.get('user_type') != 'lavoratore':
        st.error("Accès refusé")
        return
    
    codice_lavoratore = st.session_state.get('codice_operatore')
    pin_lavoratore = st.session_state.get('pin_operatore')
    
    st.title(get_testo("i_miei_dati", lingua))
    st.success(f"**{get_testo('benvenuto', lingua)}** - Code: {codice_lavoratore}")
    st.markdown("---")
    
    # Carica dati dal foglio
    try:
        dati_foglio = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if not dati_foglio or len(dati_foglio) < 2:
            st.error("Aucune donnée trouvée")
            return
        
        df = pd.DataFrame(dati_foglio[1:], columns=dati_foglio[0])
        
        # FIX: Ricerca corretta per codice e PIN
        mask = (df['Codice'] == codice_lavoratore) & (df['PIN'] == pin_lavoratore)
        
        if not mask.any():
            st.error("Travailleur non trouvé")
            st.info(f"Code recherché: {codice_lavoratore}, PIN: {pin_lavoratore}")
            return
        
        row = df[mask].iloc[0]
        idx = row.name
        
        # SEZIONE 1: DATI PERSONALI (NON MODIFICABILI)
        st.subheader(get_testo("sezione_dati_personali", lingua))
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text_input(get_testo("cognome", lingua), value=row.get('Cognome', ''), disabled=True)
            st.text_input(get_testo("nome", lingua), value=row.get('Nome', ''), disabled=True)
            st.text_input(get_testo("data_nascita", lingua), value=row.get('Data_Nascita', ''), disabled=True)
        with col2:
            st.text_input(get_testo("cni", lingua), value=row.get('CNI', ''), disabled=True)
            st.text_input(get_testo("css", lingua), value=row.get('CSS', ''), disabled=True)
            st.text_input(get_testo("ipres", lingua), value=row.get('IPRES', ''), disabled=True)
        with col3:
            st.text_input(get_testo("codice_accesso", lingua), value=row.get('Codice', ''), disabled=True)
            st.text_input(get_testo("luogo_nascita", lingua), value=row.get('Luogo_Nascita', ''), disabled=True)
            st.text_input(get_testo("nazionalita", lingua), value=row.get('Nazionalita', ''), disabled=True)
        
        st.markdown("---")
        
        # SEZIONE 2: PAGA (NON MODIFICABILE)
        st.subheader(get_testo("sezione_paga", lingua))
        st.info(get_testo("paga_desc", lingua))
        col1, col2 = st.columns(2)
        with col1:
            tipo_paga = row.get('Tipo_Paga', 'Non défini')
            st.text_input(get_testo("paga_type", lingua), value=tipo_paga, disabled=True)
        with col2:
            valore_paga = row.get('Valore_Paga', 'Non défini')
            st.text_input(get_testo("paga_amount", lingua), value=f"{valore_paga} FCFA", disabled=True)
        
        st.markdown("---")
        
        # SEZIONE 3: CONTATTI (MODIFICABILI)
        st.subheader(get_testo("sezione_contatti", lingua))
        col1, col2 = st.columns(2)
        with col1:
            nuovo_tel = st.text_input(get_testo("telefono_1", lingua), value=row.get('Telefono', ''))
            nuovo_tel2 = st.text_input(get_testo("telefono_2", lingua), value=row.get('Telefono2', ''))
            nuovo_indirizzo = st.text_input(get_testo("indirizzo", lingua), value=row.get('Indirizzo', ''))
        with col2:
            nuovo_quartiere = st.text_input(get_testo("quartiere", lingua), value=row.get('Quartiere', ''))
            nuovo_comune = st.text_input(get_testo("comune", lingua), value=row.get('Comune', ''))
            nuovo_dipartimento = st.text_input(get_testo("regione_senegal", lingua), value=row.get('Dipartimento', ''))
        
        st.markdown("---")
        
        # SEZIONE 4: FAMIGLIA (MODIFICABILE)
        st.subheader(get_testo("sezione_famille", lingua))
        col1, col2 = st.columns(2)
        with col1:
            nuovo_stato_civile = st.selectbox(get_testo("stato_civile", lingua), 
                [get_testo("celibe", lingua), get_testo("coniugato", lingua), get_testo("divorziato", lingua), get_testo("vedovo", lingua)],
                index=0 if row.get('Stato_Civile') == get_testo("celibe", lingua) else 1)
            nuovi_figli = st.number_input(get_testo("figli_totale", lingua), min_value=0, 
                value=int(row.get('Figli', 0) if pd.notna(row.get('Figli')) else 0))
        with col2:
            if nuovo_stato_civile == get_testo("coniugato", lingua):
                nuove_mogli = st.number_input(get_testo("numero_mogli", lingua), min_value=1, max_value=4,
                    value=int(row.get('Numero_Mogli', 1) if pd.notna(row.get('Numero_Mogli')) else 1))
                for i in range(1, nuove_mogli + 1):
                    st.markdown(f"**Épouse {i}**")
                    c_res, c_fig = st.columns(2)
                    with c_res:
                        st.text_input(get_testo("residenza_moglie", lingua) + f" {i}", 
                            value=row.get(f'Residenza_Moglie_{i}', ''), key=f"wife_res_{i}")
                    with c_fig:
                        st.number_input(get_testo("figli_moglie", lingua) + f" {i}", min_value=0,
                            value=int(row.get(f'Figli_Moglie_{i}', 0)), key=f"wife_fig_{i}")
        
        st.markdown("---")
        
        # SEZIONE 5: VESTIARIO (MODIFICABILE)
        st.subheader(get_testo("sezione_vestiario", lingua))
        col1, col2 = st.columns(2)
        with col1:
            taglie_maglia = [get_testo("opt_xs", lingua), get_testo("opt_s", lingua), get_testo("opt_m", lingua), 
                           get_testo("opt_l", lingua), get_testo("opt_xl", lingua), get_testo("opt_xxl", lingua), get_testo("opt_xxxl", lingua)]
            nuova_taglia_maglia = st.selectbox(get_testo("taglia_maglia", lingua), taglie_maglia,
                index=taglie_maglia.index(row.get('Taglia_Maglia', 'M')) if row.get('Taglia_Maglia', 'M') in taglie_maglia else 2)
            
            taglie_pantaloni = ["38", "40", "42", "44", "46", "48", "50", "52"]
            nuova_taglia_pantaloni = st.selectbox(get_testo("taglia_pantaloni", lingua), taglie_pantaloni,
                index=taglie_pantaloni.index(str(row.get('Taglia_Pantaloni', '42'))) if str(row.get('Taglia_Pantaloni', '42')) in taglie_pantaloni else 2)
            
            taglie_scarpe = ["38", "39", "40", "41", "42", "43", "44", "45", "46", "47"]
            nuova_taglia_scarpe = st.selectbox(get_testo("taglia_scarpe", lingua), taglie_scarpe,
                index=taglie_scarpe.index(str(row.get('Taglia_Scarpe', '42'))) if str(row.get('Taglia_Scarpe', '42')) in taglie_scarpe else 4)
        with col2:
            taglie_giacca = [get_testo("opt_xs", lingua), get_testo("opt_s", lingua), get_testo("opt_m", lingua), 
                           get_testo("opt_l", lingua), get_testo("opt_xl", lingua), get_testo("opt_xxl", lingua)]
            nuova_taglia_giacca = st.selectbox(get_testo("taglia_giacca", lingua), taglie_giacca,
                index=taglie_giacca.index(row.get('Taglia_Giacca', 'M')) if row.get('Taglia_Giacca', 'M') in taglie_giacca else 2)
            
            taglie_cappello = ["S", "M", "L", "XL"]
            nuova_taglia_cappello = st.selectbox(get_testo("taglia_cappello", lingua), taglie_cappello,
                index=taglie_cappello.index(row.get('Taglia_Cappello', 'M')) if row.get('Taglia_Cappello', 'M') in taglie_cappello else 1)
            
            taglie_guanti = ["S", "M", "L", "XL"]
            nuova_taglia_guanti = st.selectbox(get_testo("taglia_guanti", lingua), taglie_guanti,
                index=taglie_guanti.index(row.get('Taglia_Guanti', 'M')) if row.get('Taglia_Guanti', 'M') in taglie_guanti else 1)
        
        st.markdown("---")
        
        # PULSANTE SALVA MODIFICHE
        if st.button(get_testo("salva_modifiche", lingua), type="primary", use_container_width=True):
            try:
                # Aggiorna dataframe
                df.loc[idx, 'Telefono'] = nuovo_tel
                df.loc[idx, 'Telefono2'] = nuovo_tel2
                df.loc[idx, 'Indirizzo'] = nuovo_indirizzo
                df.loc[idx, 'Quartiere'] = nuovo_quartiere
                df.loc[idx, 'Comune'] = nuovo_comune
                df.loc[idx, 'Dipartimento'] = nuovo_dipartimento
                df.loc[idx, 'Stato_Civile'] = nuovo_stato_civile
                df.loc[idx, 'Figli'] = nuovi_figli
                df.loc[idx, 'Taglia_Maglia'] = nuova_taglia_maglia
                df.loc[idx, 'Taglia_Pantaloni'] = nuova_taglia_pantaloni
                df.loc[idx, 'Taglia_Scarpe'] = nuova_taglia_scarpe
                df.loc[idx, 'Taglia_Giacca'] = nuova_taglia_giacca
                df.loc[idx, 'Taglia_Cappello'] = nuova_taglia_cappello
                df.loc[idx, 'Taglia_Guanti'] = nuova_taglia_guanti
                
                # Invia a Google
                dati_json = {"action": "update", "data": df.to_dict(orient='records')}
                resp = requests.post(GOOGLE_SCRIPT_URL_ASSUNZIONI, json=dati_json)
                
                if resp.status_code == 200:
                    st.success(get_testo("modifiche_salvate", lingua))
                    st.balloons()
                else:
                    st.error(get_testo("errore_salvataggio", lingua))
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
        
        st.markdown("---")
        
        # SEZIONE 6: COMUNICAZIONI
        st.subheader(get_testo("sezione_comunicazioni", lingua))
        
        # Form nuova richiesta
        with st.form("form_richiesta"):
            st.markdown("**📝 Nouvelle demande**")
            col1, col2 = st.columns(2)
            with col1:
                tipo_richiesta = st.selectbox(get_testo("tipo_permesso", lingua), [
                    get_testo("opt_permesso", lingua),
                    get_testo("opt_vacanza", lingua),
                    get_testo("opt_festa", lingua),
                    get_testo("opt_viaggio", lingua),
                    get_testo("opt_malattia", lingua),
                    get_testo("opt_altro_com", lingua)
                ])
                data_inizio_perm = st.text_input(get_testo("data_inizio_permesso", lingua) + " (GG/MM/AAAA)")
            with col2:
                data_fine_perm = st.text_input(get_testo("data_fine_permesso", lingua) + " (GG/MM/AAAA)")
                motivo_perm = st.text_area(get_testo("motivo_permesso", lingua), height=100)
            
            submitted = st.form_submit_button(get_testo("invia_richiesta", lingua), type="primary", use_container_width=True)
            
            if submitted:
                if not data_inizio_perm or not motivo_perm:
                    st.error("Veuillez remplir la date de début et le motif.")
                else:
                    dati_richiesta = {
                        "id": f"REQ-{datetime.now().year}-{random.randint(1000, 9999)}",
                        "codice_lavoratore": codice_lavoratore,
                        "nome_lavoratore": f"{row.get('Cognome', '')} {row.get('Nome', '')}",
                        "data_richiesta": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "tipo_richiesta": tipo_richiesta,
                        "data_inizio": data_inizio_perm,
                        "data_fine": data_fine_perm,
                        "motivo": motivo_perm,
                        "stato": "Pending"
                    }
                    if salva_su_google_sheet(dati_richiesta, GOOGLE_SCRIPT_URL_ASSUNZIONI, "append"):
                        st.success(get_testo("richiesta_inviata", lingua))
                        st.balloons()
                    else:
                        st.error("Erreur de connexion.")
        
        st.markdown("---")
        
        # Lista richieste precedenti
        st.subheader(get_testo("lista_richieste", lingua))
        try:
            dati_comunicazioni = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            if dati_comunicazioni and len(dati_comunicazioni) > 1:
                df_com = pd.DataFrame(dati_comunicazioni[1:], columns=dati_comunicazioni[0])
                mie_richieste = df_com[df_com['Codice'] == codice_lavoratore]
                
                if len(mie_richieste) > 0:
                    for _, req in mie_richieste.iterrows():
                        stato = req.get('Stato', 'Pending')
                        if stato == 'Approved':
                            stato_display = get_testo("stato_approved", lingua)
                        elif stato == 'Rejected':
                            stato_display = get_testo("stato_rejected", lingua)
                        else:
                            stato_display = get_testo("stato_pending", lingua)
                        
                        with st.expander(f"{req.get('Tipo_Richiesta', '')} - {req.get('Data_Richiesta', '')} [{stato_display}]"):
                            st.markdown(f"**{get_testo('data_inizio_permesso', lingua)}:** {req.get('Data_Inizio', '')}")
                            st.markdown(f"**{get_testo('data_fine_permesso', lingua)}:** {req.get('Data_Fine', '')}")
                            st.markdown(f"**{get_testo('motivo_permesso', lingua)}:** {req.get('Motivo', '')}")
                            risposta = req.get('Risposta_Admin', '')
                            if risposta:
                                st.success(f"**{get_testo('risposta_admin', lingua)}:** {risposta}")
                            else:
                                st.info("En attente de réponse...")
                else:
                    st.info(get_testo("nessuna_richiesta", lingua))
            else:
                st.info(get_testo("nessuna_richiesta", lingua))
        except Exception as e:
            st.info(get_testo("nessuna_richiesta", lingua))
        
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
    
    st.markdown("---")
    if st.button(get_testo("logout", lingua)):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.pagina = 'home'  # FIX: Reset alla home
        st.rerun()

# ============================================
# PAGINA REGISTRAZIONE MULTI-STEP (7 STEP)
# ============================================
def pagina_registrazione_multi_step(lingua):
    step = st.session_state.step
    
    # AVVISO NON CONTRATTO (solo al primo accesso)
    if step == 1 and 'avviso_mostrato' not in st.session_state:
        st.warning(get_testo("avviso_non_contratto", lingua))
        st.info(get_testo("avviso_regole_aziendali", lingua))
        st.session_state.avviso_mostrato = True
    
    st.progress(step / 7)
    st.markdown(f"**Étape {step} sur 7**")
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
    elif step == 7:
        dati_step = step_7_vestiario(lingua)
    
    st.session_state.dati_form.update(dati_step)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if step > 1 and st.button(get_testo("indietro", lingua), use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    with col2:
        if step < 7:
            if st.button(get_testo("continua", lingua), type="primary", use_container_width=True):
                if step == 1 and (not dati_step.get('cognome') or not dati_step.get('nome')):
                    st.error(get_testo("errore_obbligatori", lingua))
                    return
                if step == 2 and (not dati_step.get('cni') or not dati_step.get('telefono_1') or not dati_step.get('css')):
                    st.error(get_testo("errore_obbligatori", lingua))
                    return
                st.session_state.step += 1
                st.rerun()
        else:
            # STEP 7 - CHECKBOX CONFERMA FINALE
            conferma = st.checkbox(get_testo("checkbox_confirm", lingua), key="s7_conf")
            if conferma:
                if st.button(get_testo("genera_pdf", lingua), type="primary", use_container_width=True):
                    genera_e_salva_pdf(st.session_state.dati_form, lingua)
            else:
                st.warning(get_testo("cocher_case", lingua))

def genera_e_salva_pdf(dati, lingua):
    codice = genera_codice()
    pin = genera_pin()
    dati_finali = {
        "id": codice, "codice": codice, "pin": pin, 
        "data_registrazione": datetime.now().strftime("%d/%m/%Y %H:%M"), 
        **dati, "stato_firma": "Da firmare",
        "pdf_identifiants_titolo": get_testo("pdf_identifiants_titolo", lingua),
        "pdf_identifiants_desc": get_testo("pdf_identifiants_desc", lingua),
        "pdf_identifiants_avviso": get_testo("pdf_identifiants_avviso", lingua),
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
        st.download_button(label=f"📥 {get_testo('scarica', lingua)} PDF", data=pdf_bytes, file_name=f"Proacier_{codice}.pdf", mime="application/pdf", use_container_width=True, key="btn_dl")
        st.balloons()
        st.session_state.step = 1
        st.session_state.dati_form = {}
        st.session_state.avviso_mostrato = False
    else:
        st.error("Erreur de connexion à Google Sheets.")

# ============================================
# PAGINA ESPACE TRAVAILLEUR (CON 2 PULSANTI)
# ============================================
def pagina_espace_travailleur(lingua):
    st.title(get_testo("area_lavoratore", lingua))
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 👤 {get_testo('giornalieri_titolo', lingua)}")
        st.info(get_testo('giornalieri_desc', lingua))
        if st.button(get_testo('login_btn', lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'login_lavoratore'
            st.rerun()
    
    with col2:
        st.markdown(f"### 📝 {get_testo('nuovo_giornaliero_titolo', lingua)}")
        st.info(get_testo('nuovo_giornaliero_desc', lingua))
        if st.button(get_testo('trasmissione_btn', lingua), use_container_width=True, type="primary"):
            st.session_state.pagina = 'registrazione'
            st.session_state.step = 1
            st.session_state.dati_form = {}
            st.session_state.avviso_mostrato = False
            st.rerun()

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
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'dati_form' not in st.session_state:
        st.session_state.dati_form = {}
    if 'codice_operatore' not in st.session_state:
        st.session_state.codice_operatore = None
    if 'pin_operatore' not in st.session_state:
        st.session_state.pin_operatore = None
    if 'admin_logged' not in st.session_state:
        st.session_state.admin_logged = False
    if 'avviso_mostrato' not in st.session_state:
        st.session_state.avviso_mostrato = False

    lingua = st.session_state.lingua

    with st.sidebar:
        st.image(LOGO_URL, use_column_width=True)
        st.markdown("---")
        st.title(get_testo("titolo", lingua))
        st.markdown(get_testo("sottotitolo", lingua))
        st.markdown("---")
        lingua_sel = st.selectbox(get_testo("lingua", lingua), ["Français", "Italiano", "English"],
                                   index=0 if lingua == 'fr' else (1 if lingua == 'it' else 2), key="sel_lingua_sidebar")
        nuova_lingua = 'fr' if lingua_sel == "Français" else ('it' if lingua_sel == "Italiano" else 'en')
        if nuova_lingua != lingua:
            st.session_state.lingua = nuova_lingua
            st.rerun()
        lingua = st.session_state.lingua
        st.markdown("---")
        if st.session_state.logged_in:
            st.success(f"{get_testo('benvenuto', lingua)}")
            if st.session_state.user_type == 'admin' and st.button(get_testo("dashboard", lingua), key="btn_dash"):
                st.session_state.pagina = 'dashboard'
            if st.session_state.user_type == 'lavoratore' and st.button(get_testo("i_miei_dati", lingua), key="btn_miei"):
                st.session_state.pagina = 'area_lavoratore_completa'
            if st.button(get_testo("logout", lingua), key="btn_logout"):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.session_state.pagina = 'home'  # FIX: Reset alla home
        else:
            if st.button(get_testo("candidatura_spontanea", lingua), key="btn_cand"):
                st.session_state.pagina = 'candidatura'
                st.rerun()
            if st.button(get_testo("area_lavoratore", lingua), key="btn_area"):
                st.session_state.pagina = 'espace_travailleur'
                st.rerun()
            if st.button(get_testo("dashboard", lingua), key="btn_dash_login"):
                st.session_state.pagina = 'login_admin'
                st.rerun()

    # ROUTING
    if st.session_state.pagina == 'home':
        st.title(get_testo("titolo", lingua))
        st.subheader(get_testo("sottotitolo", lingua))
        st.markdown("---")
        
        st.subheader(get_testo("home_titolo", lingua))
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{get_testo('home_punto1_titolo', lingua)}**\n- {get_testo('home_punto1_desc1', lingua)}\n- {get_testo('home_punto1_desc2', lingua)}")
            st.markdown(f"**{get_testo('home_punto2_titolo', lingua)}**\n- {get_testo('home_punto2_desc1', lingua)}\n- {get_testo('home_punto2_desc2', lingua)}")
        with col2:
            st.markdown(f"**{get_testo('home_punto3_titolo', lingua)}**\n- {get_testo('home_punto3_desc1', lingua)}\n- {get_testo('home_punto3_desc2', lingua)}")
            st.markdown(f"**{get_testo('home_punto4_titolo', lingua)}**\n- {get_testo('home_punto4_desc1', lingua)}\n- {get_testo('home_punto4_desc2', lingua)}")
        
        st.markdown("---")
        st.subheader(get_testo("home_navigation", lingua))
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(get_testo("candidatura_spontanea", lingua), use_container_width=True, type="primary"):
                st.session_state.pagina = 'candidatura'
                st.rerun()
        with c2:
            if st.button(get_testo("area_lavoratore", lingua), use_container_width=True, type="primary"):
                st.session_state.pagina = 'espace_travailleur'
                st.rerun()
        with c3:
            if st.button(get_testo("dashboard", lingua), use_container_width=True):
                st.session_state.pagina = 'login_admin'
                st.rerun()
                
    elif st.session_state.pagina == 'espace_travailleur':
        pagina_espace_travailleur(lingua)
        
    elif st.session_state.pagina == 'registrazione':
        pagina_registrazione_multi_step(lingua)
    elif st.session_state.pagina == 'candidatura':
        pagina_candidatura_spontanea(lingua)
    elif st.session_state.pagina == 'condizioni':
        pagina_condizioni(lingua)
    elif st.session_state.pagina == 'area_lavoratore_completa':
        pagina_area_lavoratore_completa(lingua)
    elif st.session_state.pagina == 'login_lavoratore':
        codice = st.text_input(get_testo("codice", lingua), key="login_codice")
        pin = st.text_input(get_testo("pin", lingua), type="password", key="login_pin")
        if st.button(get_testo("accedi", lingua), type="primary", key="btn_login_lav"):
            dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
            trovato = any(len(row) >= 3 and str(row[1]) == codice and str(row[2]) == pin for row in dati[1:])
            if trovato:
                st.session_state.logged_in = True
                st.session_state.user_type = 'lavoratore'
                st.session_state.codice_operatore = codice
                st.session_state.pin_operatore = pin
                st.session_state.pagina = 'area_lavoratore_completa'
                st.rerun()
            else:
                st.error(get_testo("codice_errato", lingua))
    elif st.session_state.pagina == 'login_admin':
        pwd = st.text_input(get_testo("password", lingua), type="password", key="login_pwd")
        if st.button(get_testo("accedi", lingua), type="primary", key="btn_login_admin"):
            if pwd == PASSWORD_DASHBOARD:
                st.session_state.logged_in = True
                st.session_state.user_type = 'admin'
                st.session_state.pagina = 'dashboard'
                st.rerun()
            else:
                st.error("Password errata")
    elif st.session_state.pagina == 'dashboard':
        st.title(get_testo("dashboard", lingua))
        dati = leggi_da_google_sheet(GOOGLE_SCRIPT_URL_ASSUNZIONI)
        if dati and len(dati) > 1:
            df = pd.DataFrame(dati[1:], columns=dati[0])
            st.metric(get_testo("totale_operai", lingua), len(df))
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(get_testo("nessun_risultato", lingua))

if __name__ == "__main__":
    main()
