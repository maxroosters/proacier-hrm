# -*- coding: utf-8 -*-
"""PROACIER HRM – FASE 7 (Pagina 2): Présences & Paies [v08.03]
✅ v08.03: _pdf_safe su tutti i testi PDF (fix FPDFUnicodeEncodingException)
✅ v08.03: sezione_buste legge PAGAMENTI via leggi_foglio (fix "Aucune paie")
✅ v08.03: icone tab singole (niente doppie)
✅ v08.02: stato lavorativo, solde de tout compte, relevé externes
✅ v08.01: paga fissa mensile senza punatura
✅ v08.00: trattenute legali Sénégal da CONFIG
Richiede: Apps Script v6.1 + fpdf2 + xlrd
"""
import re, math, random, calendar, csv, io
import requests
from datetime import datetime, date
from fpdf import FPDF
import streamlit as st
VERSIONE_PAGHE = "08.03"
LOGO_BASE = "https://raw.githubusercontent.com/maxroosters/proacier-hrm/main/"
LINGUE = {"fr": 0, "it": 1, "en": 2}
MESI = {"fr": ["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"],
 "it": ["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"],
 "en": ["January","February","March","April","May","June","July","August","September","October","November","December"]}
GIORNI_SETTIMANA = ["lunedi","martedi","mercoledi","giovedi","venerdi","sabato","domenica"]
T6 = {
 "titolo": ("🕒 Présences & Paies", "🕒 Presenze e Paghe", "🕒 Attendance & Payroll"),
 "import_title": ("Importation des pointages", "Importazione presenze", "Attendance import"),
 "import_hint": ("Collez le contenu « List of Logs » OU chargez le .XLS puis « Analyser le fichier chargé ».", "Incolla il « List of Logs » OPPURE carica il .XLS e usa « Analizza il file caricato ».", "Paste the “List of Logs” OR load the .XLS then “Analyse the loaded file”."),
 "import_da_testo": ("Contenu du fichier", "Contenuto del file", "File content"),
 "import_up_label": ("Fichier .XLS à analyser", "File .XLS da analizzare", ".XLS file to analyse"),
 "import_mem_btn": ("Analyser le fichier chargé", "Analizza il file caricato", "Analyse the loaded file"),
 "import_parse_btn": ("Analyser le fichier", "Analizza il file", "Parse file"),
 "import_write_btn": ("Enregistrer dans PRESENZE", "Scrivi in PRESENZE", "Write to PRESENZE"),
 "import_empty": ("Collez d'abord le contenu du fichier", "Prima incolla il contenuto", "Paste the file content first"),
 "parsed_none": ("❌ Impossible de lire le fichier.", "❌ Impossibile leggere il file.", "❌ Cannot read the file."),
 "parsed_ok": ("✅ Fichier analysé", "✅ File analizzato", "✅ File parsed"),
 "import_period": ("Période", "Periodo", "Period"),
 "import_workers": ("travailleurs détectés", "lavoratori rilevati", "workers detected"),
 "import_written": ("présences écrites", "presenze scritte", "attendances written"),
 "import_dup": ("déjà présentes (ignorées)", "già presenti (ignorate)", "already present (skipped)"),
 "import_unmapped": ("⚠️ Non mappati (MAPPING_PRESENZE): ", "⚠️ Non mappati (MAPPING_PRESENZE): ", "️ Unmapped (MAPPING_PRESENZE): "),
 "import_go_anomalies": ("Corrigez les DA_RIVEDERE dans « Anomalies ».", "Correggi i DA_RIVEDERE in « Anomalie ».", "Fix DA_RIVEDERE in “Anomalies”."),
 "anom_title": ("Anomalies & absences", "Anomalie e assenze", "Anomalies & absences"),
 "anom_none": ("✅ Aucune anomalie.", "✅ Nessuna anomalia.", "✅ No anomalies."),
 "anom_hint": ("DA_RIVEDERE = pointage incomplet. Modifiez puis « Enregistrer tout ».", "DA_RIVEDERE = timbratura incompleta. Modifica poi « Salva tutto ».", "DA_RIVEDERE = incomplete punch. Edit then “Save all”."),
 "anom_uscita": ("Heure de sortie (HH:MM)", "Ora uscita (HH:MM)", "Clock-out (HH:MM)"),
 "anom_stato": ("Statut", "Stato", "Status"),
 "anom_note": ("Note", "Nota", "Note"),
 "anom_save_all": ("💾 Enregistrer toutes les corrections", "💾 Salva tutte le correzioni", "💾 Save all corrections"),
 "anom_fixed_n": ("corrections enregistrées", "correzioni salvate", "corrections saved"),
 "anom_need_out": ("Pour OK il faut une heure de sortie valide", "Per OK serve un'ora di uscita valida", "For OK a valid clock-out is needed"),
 "paghe_title": ("Calcul des paies (quinzaine)", "Calcolo paghe (quindicina)", "Payroll (fortnight)"),
 "paghe_anno": ("Année", "Anno", "Year"), "paghe_mese": ("Mois", "Mese", "Month"),
 "paghe_quindicina": ("Quinzaine", "Quindicina", "Fortnight"),
 "paghe_q1": ("1 → 15", "1 → 15", "1 → 15"), "paghe_q2": ("16 → fin du mois", "16 → fine mese", "16 → end of month"),
 "paghe_calc_btn": ("Calculer", "Calcola", "Calculate"),
 "paghe_periodo": ("Période de paie", "Periodo paga", "Pay period"),
 "paghe_nulla": ("ℹ️ Aucune activité ni salaire.", "ℹ️ Nessuna attività né salario.", "ℹ️ No activity or salary."),
 "paghe_no_salario": ("pas de salaire actif (ignoré)", "nessun salario attivo (ignorato)", "no active salary (skipped)"),
 "paghe_gia": ("déjà payé (ignoré)", "già pagato (ignorato)", "already paid (skipped)"),
 "paghe_confirm_btn": ("Confirmer et écrire dans PAGAMENTI", "Conferma e scrivi in PAGAMENTI", "Confirm and write to PAGAMENTI"),
 "paghe_done": ("✅ Paies confirmées : ", "✅ Paghe confermate: ", "✅ Payrolls confirmed: "),
 "dar_warn": ("ligne(s) DA_RIVEDERE exclue(s) — corrigez puis recalculez", "riga/e DA_RIVEDERE escluse — correggi poi ricalcola", "DA_RIVEDERE row(s) excluded — fix then recalc"),
 "premi_title": ("Prix de production (FCFA)", "Premi produzione (FCFA)", "Production bonuses (FCFA)"),
 "tot_lordo": ("Total brut", "Totale lordo", "Total gross"),
 "tot_acc": ("Total avances déduites", "Totale acconti dedotti", "Total advances deducted"),
 "tot_netto": ("Total net (sans prix)", "Totale netto (senza premi)", "Total net (without bonuses)"),
 "netto_hint": ("Le net final tient compte des prix saisis ci-dessus.", "Il netto finale tiene conto dei premi inseriti.", "Final net includes the bonuses entered."),
 "col_codice": ("Code", "Codice", "Code"), "col_nome": ("Nom", "Nome", "Name"),
 "col_tipo": ("Type", "Tipo", "Type"), "col_base": ("Tarif", "Tariffa", "Rate"),
 "col_giorni": ("Jours", "Giorni", "Days"), "col_ore": ("Heures", "Ore", "Hours"),
 "col_stra": ("H. supp.", "Straord.", "OT hrs"), "col_rit": ("Retards (½h)", "Ritardi (½h)", "Delays (½h)"),
 "col_abs": ("Abs.", "Ass.", "Abs."), "col_lordo": ("Brut (FCFA)", "Lordo (FCFA)", "Gross (FCFA)"),
 "col_acc": ("Avances (FCFA)", "Acconti (FCFA)", "Advances (FCFA)"), "col_tratt": ("Retenues (FCFA)", "Trattenute (FCFA)", "Deductions (FCFA)"),
 "tot_tratt": ("Total retenues légales", "Totale trattenute legali", "Total statutory deductions"),
 "acc_title": ("Avances", "Acconti", "Advances"), "acc_new": ("Nouvelle avance", "Nuovo acconto", "New advance"),
 "acc_codice": ("Travailleur", "Lavoratore", "Worker"), "acc_tipo": ("Type d'avance", "Tipo acconto", "Advance type"),
 "acc_generico": ("Générique", "Generico", "Generic"), "acc_tabasky": ("Tabaski", "Tabaski", "Tabaski"),
 "acc_scuola": ("École", "Scuola", "School"), "acc_karem": ("Karêm", "Karem", "Karem"),
 "acc_importo": ("Montant (FCFA)", "Importo (FCFA)", "Amount (FCFA)"),
 "acc_modalita": ("Remboursement", "Rimborso", "Repayment"),
 "acc_unica": ("Une seule fois", "Unica soluzione", "One-off"), "acc_rate": ("Par versements", "A rate", "Installments"),
 "acc_num_rate": ("Nombre de versements", "Numero rate", "Number of installments"),
 "acc_data_rich": ("Date demande (JJ/MM/AAAA)", "Data richiesta (GG/MM/AAAA)", "Request date (DD/MM/YYYY)"),
 "acc_data_ero": ("Date paiement (JJ/MM/AAAA)", "Data erogazione (GG/MM/AAAA)", "Payment date (DD/MM/YYYY)"),
 "acc_crea_btn": ("Créer l'avance", "Crea acconto", "Create advance"),
 "acc_created": ("✅ Avance enregistrée", "✅ Acconto registrato", "✅ Advance saved"),
 "acc_open_title": ("Avances ouvertes", "Acconti aperti", "Open advances"),
 "acc_none": ("ℹ️ Aucune avance ouverte.", "ℹ️ Nessun acconto aperto.", "ℹ️ No open advances."),
 "acc_err": ("Sélectionnez un travailleur et un montant > 0", "Seleziona lavoratore e importo > 0", "Select a worker and amount > 0"),
 "acc_dedotto": ("sera déduit à la prochaine paie", "sarà dedotto alla prossima paga", "will be deducted at next payroll"),
 "buste_title": ("🖨️ Fiche de paie", "🖨️ Busta paga", "🖨️ Pay slip"),
 "buste_worker": ("Travailleur", "Lavoratore", "Worker"),
 "buste_period": ("Période (quinzaine)", "Periodo (quindicina)", "Period (fortnight)"),
 "buste_gen": ("🖨️ Générer / imprimer la fiche", "🖨️ Genera / stampa busta", "🖨️ Generate / print slip"),
 "buste_none": ("ℹ️ Aucune paie enregistrée.", "ℹ️ Nessuna paga registrata.", "ℹ️ No payroll recorded."),
 "buste_hist": ("Historique des paies (ristampabile)", "Storico buste (ristampabile)", "Pay history (reprintable)"),
 "buste_avances": ("Avances & remboursements", "Acconti e rimborsi", "Advances & repayments"),
 "tratt_title": ("RETENUES LÉGALES (SÉNÉGAL)", "TRATTENUTE LEGALI (SENEGAL)", "STATUTORY DEDUCTIONS (SENEGAL)"),
 "tratt_css": ("CSS – prévoyance (salarié)", "CSS – previdenza (lavoratore)", "CSS – pension (employee)"),
 "tratt_ipres": ("IPRES – retraite (salarié)", "IPRES – pensione (lavoratore)", "IPRES – pension (employee)"),
 "tratt_ipm": ("IPM – maladie (salarié)", "IPM – malattia (lavoratore)", "IPM – health (employee)"),
 "tratt_ir": ("IR / ITS – impôt sur le revenu", "IR / ITS – imposta sul reddito", "IR / ITS – income tax"),
 "tratt_tot": ("Total retenues légales", "Totale trattenute legali", "Total statutory deductions"),
 "tratt_off": ("Retenues légales désactivées (CONFIG).", "Trattenute legali disattivate (CONFIG).", "Statutory deductions disabled (CONFIG)."),
 "tratt_note": ("Taux & plafonds selon CONFIG – à faire valider par l'Inspection du Travail de Thiès.", "Aliquote e plafond da CONFIG – da far validare dall'Ispettorato di Thiès.", "Rates & ceilings from CONFIG – validate with Thiès Labour Inspection."),
 "dat_title": ("CHARGES PATRONALES (information)", "CONTRIBUTI DATORIALI (informativo)", "EMPLOYER CONTRIBUTIONS (info)"),
 "dat_css_af": ("CSS – allocations familiales", "CSS – assegni familiari", "CSS – family allowances"),
 "dat_css_at": ("CSS – accidents / maladies prof.", "CSS – infortuni / malattie prof.", "CSS – occupational accidents"),
 "dat_ipres": ("IPRES (part patronale)", "IPRES (quota datore)", "IPRES (employer share)"),
 "dat_ipm": ("IPM (part patronale)", "IPM (quota datore)", "IPM (employer share)"),
 "dat_fnp": ("FNP – formation professionnelle", "FNP – formazione professionale", "FNP – vocational training"),
 "fissa_badge": ("Mensuel fixe (sans pointage)", "Mensile fisso (senza punatura)", "Fixed monthly (no time clock)"),
 "esterno_badge": ("Journalier externe", "Giornaliero esterno", "External daily worker"),
 "esterno_skip": ("externe — exclus (CONFIG paghe_esterni_attive=NO)", "esterno — escluso (CONFIG paghe_esterni_attive=NO)", "external — excluded (CONFIG paghe_esterni_attive=NO)"),
 "cessato_skip": ("travailleur cessé (ignoré)", "lavoratore cessato (ignorato)", "terminated worker (skipped)"),
 "solde_title": ("📤 Solde de tout compte", "📤 Saldo finale", "📤 Final settlement"),
 "solde_hint": ("Préavis, congés non pris, indemnité de licenciement; archive sans supprimer l'historique.", "Préavis, ferie non godute, indennità licenziamento; archivia senza eliminare lo storico.", "Notice, untaken leave, severance; archives without deleting history."),
 "solde_worker": ("Travailleur à clôturer", "Lavoratore da chiudere", "Worker to close"),
 "solde_motivo": ("Motif de départ", "Motivo uscita", "Reason for leaving"),
 "solde_dimissioni": ("Démission", "Dimissioni", "Resignation"),
 "solde_licenziamento": ("Licenciement", "Licenziamento", "Dismissal"),
 "solde_fine_prova": ("Fin de période d'essai", "Fine periodo di prova", "End of probation"),
 "solde_altro": ("Autre", "Altro", "Other"),
 "solde_data_fine": ("Date de fin (JJ/MM/AAAA)", "Data fine (GG/MM/AAAA)", "End date (DD/MM/YYYY)"),
 "solde_preavviso_lav": ("Préavis travaillé", "Preavviso lavorato", "Notice worked"),
 "solde_preavviso_ind": ("Indemnité de préavis (FCFA)", "Indennità preavviso (FCFA)", "Notice allowance (FCFA)"),
 "solde_congedi_gg": ("Jours de congé non pris", "Giorni ferie non godute", "Untaken leave days"),
 "solde_congedi_fcfa": ("Indemnité congés (FCFA)", "Indennità ferie (FCFA)", "Leave allowance (FCFA)"),
 "solde_indennita_fcfa": ("Indemnité de licenciement (FCFA)", "Indennità licenziamento (FCFA)", "Severance (FCFA)"),
 "solde_totale": ("TOTAL SOLDE (FCFA)", "TOTALE SALDO (FCFA)", "TOTAL SETTLEMENT (FCFA)"),
 "solde_calc_btn": ("Calculer le solde", "Calcola il saldo", "Calculate settlement"),
 "solde_confirm_btn": ("Confirmer et archiver", "Conferma e archivia", "Confirm and archive"),
 "solde_archived": ("✅ Archivé. Salaire clôturé. Historique préservé.", "✅ Archiviato. Salario chiuso. Storico preservato.", "✅ Archived. Salary closed. History preserved."),
 "solde_no_worker": ("Sélectionnez un travailleur actif.", "Seleziona un lavoratore attivo.", "Select an active worker."),
 "releve_title": ("📤 Relevé d'heures (externes)", "📤 Riepilogo ore (esterni)", "📤 Hours summary (externals)"),
 "releve_hint": ("Heures des travailleurs externes pour facturation à la société tierce.", "Ore dei lavoratori esterni per fatturazione alla società terza.", "Hours of external workers for third-party billing."),
 "releve_gen_btn": ("Générer le relevé", "Genera il riepilogo", "Generate summary"),
 "releve_no_ext": ("ℹ️ Aucun travailleur externe.", "ℹ️ Nessun lavoratore esterno.", "ℹ️ No external workers."),
 "releve_soc": ("Société tierce", "Società terza", "Third company"),
 "releve_csv_btn": ("📥 Télécharger CSV", "📥 Scarica CSV", "📥 Download CSV"),
}
def t6(k, lingua="fr"):
    v = T6.get(k)
    return k if not v else v[LINGUE.get(lingua, 0)]
def s_str(v):
    if v is None: return ""
    s = str(v)
    return "" if s in ("nan", "None", "#ERROR!") else s.strip()
def to_min(t):
    try:
        p = str(t).strip().split(":"); return int(p[0]) * 60 + int(p[1])
    except Exception: return None
def to_float(s):
    try: return float(str(s).replace(",", ".").strip())
    except Exception: return 0.0
def to_float_or_none(s):
    try: return float(str(s).replace(",", ".").strip())
    except Exception: return None
def parse_data(s):
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s_str(s))
    if not m: return None
    d, mo, y = map(int, m.groups())
    try: return date(y, mo, d)
    except Exception: return None
def data_ord(s):
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", s_str(s))
    if not m: return None
    d, mo, y = map(int, m.groups())
    return (y, mo, d)
def timbro_notte(t):
    m = to_min(t)
    return m is not None and (m < 260 or m >= 2360)
_PDF_MAP = {"→": "->", "–": "-", "—": "-", "•": "-", "…": "...", "’": "'", "‘": "'", "“": '"', "”": '"', "≤": "<=", "≥": ">=", "€": "EUR", "Œ": "OE", "œ": "oe", "⚠": "!", "✅": "[OK]", "⭐": "*", "📈": "^", "⛔": "X", "➡": "->", "\xa0": " ", "★": "*", "☆": "*", "½": "1/2", "🖨": "", "📤": "", "📥": "", "🔍": "", "💰": "", "💸": "", "🧮": "", "🏆": "", "➕": "+", "🔎": "", "💾": "", "⚙": "", "🕒": "", "ℹ": "i", "": ""}
def _pdf_safe(s):
    out = []
    for ch in str(s or ""):
        if ch in _PDF_MAP: out.append(_PDF_MAP[ch]); continue
        try:
            ch.encode("latin-1"); out.append(ch)
        except Exception: out.append("?")
    return "".join(out)
OPZ = {
 "tipo_visita": [("assunzione","Visite d'embauche","Visita di assunzione","Hiring visit"),("periodica","Visite périodique","Visita periodica","Periodic visit"),("straordinaria","Visite extraordinaire","Visita straordinaria","Extraordinary visit")],
 "idoneita": [("apte","Apte","Apto","Fit"),("restriction","Apte avec restriction","Apto con restrizioni","Fit with restrictions"),("inapte","Inapte","Inapto","Unfit")],
 "tipo_paga": [("giornaliero","Journalier","Giornaliero","Daily"),("orario","Horaire","Orario","Hourly"),("mensile","Mensuel","Mensile","Monthly")],
 "stato_lavorativo": [("prova","Période d'essai","Periodo di prova","Probation"),("assunto","Embauché","Assunto","Hired"),("esterno","Journalier externe","Giornaliero esterno","External daily"),("dimissionario","Démissionnaire","Dimissionario","Resigned"),("licenziato","Licencié","Licenziato","Dismissed")],
}
def etichetta(tipo, valore, lingua="fr"):
    v = s_str(valore)
    if not v: return ""
    for o in OPZ.get(tipo, []):
        if v in o: return o[LINGUE.get(lingua, 0) + 1]
    return v
DEFAULT_CONFIG = {
 "straordinario_1_percent": 25.0, "straordinario_2_percent": 50.0,
 "ore_normali_giorno": 8.0, "modalita_paga": "giornaliero",
 "ritardo_tolleranza_min": 15.0, "ritardo_metodo": "mezzora", "assenza_penale_percent": 0.0,
 "trattenute_legali_attive": "si",
 "css_lavoratore_percent": 5.6, "css_plafond_mensile": 285000.0,
 "ipres_t1_lav_percent": 2.8, "ipres_t1_plafond": 291600.0,
 "ipres_t2_lav_percent": 6.1, "ipres_t2_plafond": 583200.0,
 "ipres_t3_lav_percent": 10.2, "ipres_t3_plafond": 874800.0,
 "ipm_lavoratore_percent": 2.5, "ipm_plafond_mensile": 285000.0,
 "ir_frais_prof_percent": 20.0, "ir_frais_prof_plafond_mensile": 125000.0,
 "ir_bareme_mensile": "35000|0;66333|12.1;133333|20.4;216666|25.3;333333|30.3;566666|38.1;1000000000|42.7",
 "css_af_dat_percent": 5.0, "css_at_mp_dat_percent": 3.0, "fnp_dat_percent": 1.5,
 "paghe_esterni_attive": "no", "promemoria_prova_giorni_prima": 7,
 "indennita_licenziamento_mesi_per_anno": 0.0, "preavviso_mesi": 1.0,
}
FLOAT_KEYS = ("straordinario_1_percent","straordinario_2_percent","ore_normali_giorno","ritardo_tolleranza_min","assenza_penale_percent","css_lavoratore_percent","css_plafond_mensile","ipres_t1_lav_percent","ipres_t1_plafond","ipres_t2_lav_percent","ipres_t2_plafond","ipres_t3_lav_percent","ipres_t3_plafond","ipm_lavoratore_percent","ipm_plafond_mensile","ir_frais_prof_percent","ir_frais_prof_plafond_mensile","css_af_dat_percent","css_at_mp_dat_percent","fnp_dat_percent","indennita_licenziamento_mesi_per_anno","preavviso_mesi")
def leggi_config(A):
    cfg = dict(DEFAULT_CONFIG); festivi = {}
    riposo = {"sabato", "domenica"}; flottanti = set(); soglia_notte = 180
    try: _, recs = A.leggi_foglio("CONFIG")
    except Exception: recs = []
    for r in recs:
        k = A.s_str(r.get("chiave")).strip().lower().replace(" ", "_")
        v = A.s_str(r.get("valore")).strip()
        if not k: continue
        if k.startswith("festivo"):
            try:
                y, m, g = k[8:].split("-"); festivi[f"{int(g):02d}/{int(m):02d}/{y}"] = v or "Férié"
            except Exception: pass
        elif k == "riposo_settimanale" and v: riposo = {x.strip().lower() for x in v.split(",") if x.strip()}
        elif k == "turni_flottanti" and v: flottanti = {x.strip().upper() for x in v.split(",") if x.strip()}
        elif k == "soglia_uscita_notturna":
            m2 = to_min(v)
            if m2 is not None: soglia_notte = m2
        elif k in ("modalita_paga", "ritardo_metodo", "trattenute_legali_attive", "paghe_esterni_attive") and v: cfg[k] = v.lower()
        elif k == "ir_bareme_mensile" and v: cfg[k] = v
        elif k == "promemoria_prova_giorni_prima":
            try: cfg[k] = int(float(v))
            except Exception: pass
        elif k in FLOAT_KEYS:
            f = to_float_or_none(v)
            if f is not None: cfg[k] = f
    cfg["_riposo"], cfg["_flottanti"], cfg["_soglia_notte"] = riposo, flottanti, soglia_notte
    if not festivi: cfg["_festivi_default"] = True
    return cfg, festivi
def _parse_bareme(s):
    out = []
    for tok in str(s).split(";"):
        if "|" in tok:
            a, b = tok.split("|", 1); out.append((to_float(a), to_float(b)))
    out.sort(key=lambda x: x[0]); return out
def _ir_mensile(imp, bareme):
    if imp <= 0 or not bareme: return 0.0
    prev = 0.0; ir = 0.0
    for lim, rate in bareme:
        if imp <= prev: break
        base = min(imp, lim) - prev
        if base > 0: ir += base * rate / 100.0
        prev = lim
    return ir
def _ipres_scaglioni(base, cfg, suff="lav"):
    t1 = cfg.get("ipres_t1_plafond", 291600.0)/2.0; t2 = cfg.get("ipres_t2_plafond", 583200.0)/2.0; t3 = cfg.get("ipres_t3_plafond", 874800.0)/2.0
    r1 = cfg.get(f"ipres_t1_{suff}_percent", 2.8); r2 = cfg.get(f"ipres_t2_{suff}_percent", 6.1); r3 = cfg.get(f"ipres_t3_{suff}_percent", 10.2)
    if base <= 0: return 0.0
    tot = min(base, t1) * r1 / 100.0
    if base > t1: tot += (min(base, t2) - t1) * r2 / 100.0
    if base > t2: tot += (min(base, t3) - t2) * r3 / 100.0
    return tot
def trattenute_attive(cfg): return str(cfg.get("trattenute_legali_attive", "si")).lower() in ("si", "sì", "oui", "yes", "1", "true")
def paghe_esterni_attive(cfg): return str(cfg.get("paghe_esterni_attive", "no")).lower() in ("si", "sì", "oui", "yes", "1", "true")
def calcola_trattenute_senegal(lordo, cfg):
    zero = {k: 0.0 for k in ("css", "ipres", "ipm", "ir", "totale", "dat_css_af", "dat_css_at", "dat_ipres", "dat_ipm", "dat_fnp")}
    if not trattenute_attive(cfg) or lordo <= 0: return zero
    L = float(lordo)
    css = min(L, cfg.get("css_plafond_mensile", 285000.0)/2.0) * cfg.get("css_lavoratore_percent", 5.6)/100.0
    ipres = _ipres_scaglioni(L, cfg, "lav")
    ipm = min(L, cfg.get("ipm_plafond_mensile", 285000.0)/2.0) * cfg.get("ipm_lavoratore_percent", 2.5)/100.0
    imp_ir = max(0.0, L - (css+ipres+ipm))
    frais = min(imp_ir * cfg.get("ir_frais_prof_percent", 20.0)/100.0, cfg.get("ir_frais_prof_plafond_mensile", 125000.0)/2.0)
    ir = _ir_mensile(max(0.0, imp_ir-frais) * 2.0, _parse_bareme(cfg.get("ir_bareme_mensile", DEFAULT_CONFIG["ir_bareme_mensile"]))) / 2.0
    return {"css": round(css), "ipres": round(ipres), "ipm": round(ipm), "ir": round(ir),
            "totale": round(css+ipres+ipm+ir),
            "dat_css_af": round(L * cfg.get("css_af_dat_percent", 5.0)/100.0),
            "dat_css_at": round(L * cfg.get("css_at_mp_dat_percent", 3.0)/100.0),
            "dat_ipres": round(_ipres_scaglioni(L, cfg, "dat")),
            "dat_ipm": round(min(L, cfg.get("ipm_plafond_mensile", 285000.0)/2.0) * cfg.get("ipm_lavoratore_percent", 2.5)/100.0),
            "dat_fnp": round(L * cfg.get("fnp_dat_percent", 1.5)/100.0)}
def _stato_lav(dip): return s_str(dip.get("stato_lavorativo")).lower() or "prova"
def _stato_attivo(dip, cfg=None):
    if _stato_lav(dip) in ("dimissionario", "licenziato"): return False
    df = parse_data(dip.get("data_fine_rapporto"))
    return not (df and df <= date.today())
def _flag_fissa(dip): return s_str(dip.get("paga_fissa")).upper() in ("SI", "SÌ", "OUI", "YES", "1", "TRUE", "VRAI")
def _is_esterno(dip): return _stato_lav(dip) == "esterno"
def mappa_turni(A, recs_turni):
    info = {}
    for r in recs_turni:
        ct = A.s_str(r.get("codice_turno")).strip().upper()
        if not ct or ct == "REGOLE": continue
        attr = A.s_str(r.get("attraversa_mezzanotte")).strip().lower() in ("si", "sì", "oui", "yes", "true", "1", "vrai")
        oi = A.s_str(r.get("ora_inizio")).strip()
        start = to_min(oi) if re.match(r"^\d{1,2}:\d{2}", oi) else None
        if start is None and not oi: continue
        info[ct] = {"attr": attr, "start": start}
    info.setdefault("T1", {"attr": False, "start": 480}); info.setdefault("T2", {"attr": True, "start": 960})
    info.setdefault("T3", {"attr": False, "start": 0}); info.setdefault("EQUIPE", {"attr": False, "start": 240})
    return info
TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")
def _extract_day_map(celle):
    nums = [(ci, int(cv.strip().strip('"'))) for ci, cv in enumerate(celle) if cv.strip().strip('"').isdigit() and 1 <= int(cv.strip().strip('"')) <= 31]
    return {ci: dv for ci, dv in nums} if len(nums) >= 15 else None
def _cell_times(cv):
    return [f"{int(mt.group(1)):02d}:{mt.group(2)}" for tok in re.split(r'[\s,;/]+', str(cv).strip())
            if (mt := TIME_RE.match(tok)) and int(mt.group(1)) < 24]
def _is_header(r):
    j = "\t".join(r)
    return re.search(r"No\s*:", j, re.I) and re.search(r"Name\s*:", j, re.I)
def _build_blocchi(rows, get_name):
    anno = mese = g1 = g2 = None
    for r in rows:
        m = re.search(r"Period\s*:\s*(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})\s*~\s*(\d{1,2})(?:[/\-.](\d{1,2}))?", "\t".join(r), re.I)
        if m:
            anno, mese, g1 = int(m.group(1)), int(m.group(2)), int(m.group(3))
            g2 = int(m.group(5)) if m.group(5) else int(m.group(4)); break
    if g2 is not None and g2 < (g1 or 1): g2 = g1
    blocchi = []; i, n = 0, len(rows)
    while i < n:
        if _is_header(rows[i]):
            nome = get_name(rows[i]); day_map = {}
            for j in list(range(max(0, i-3), i)) + list(range(i+1, min(n, i+4))):
                dm = _extract_day_map(rows[j])
                if dm: day_map = dm; break
            per_giorno = {}; j = i+1
            while j < n and not _is_header(rows[j]):
                if not _extract_day_map(rows[j]):
                    for ci, cv in enumerate(rows[j]):
                        for t in _cell_times(cv):
                            g = day_map.get(ci) or (ci+1 if 1 <= ci+1 <= 31 else None)
                            if g: per_giorno.setdefault(int(g), []).append(t)
                j += 1
            blocchi.append({"nome": nome, "per_giorno": per_giorno}); i = j
        else: i += 1
    return {"anno": anno, "mese": mese, "g1": g1 or 1, "g2": g2 or 31, "blocchi": blocchi}
def parse_list_of_logs(testo):
    rows = list(csv.reader(io.StringIO(testo.replace("\r", "")), delimiter="\t"))
    def get_name(r):
        m = re.search(r"Name\s*:\s*([^|\t]+)", "\t".join(r), re.I)
        if m:
            rest = m.group(1).strip().strip('"')
            if rest: return rest
        for ci, cv in enumerate(r):
            m2 = re.search(r"Name\s*:\s*(.*)", str(cv), re.I)
            if m2:
                rest = m2.group(1).strip().strip('"')
                if rest: return rest
            if ci+1 < len(r): return str(r[ci+1]).strip()
        return ""
    return _build_blocchi(rows, get_name)
def parse_matrix(rows):
    def get_name(r):
        for ci, cv in enumerate(r):
            m2 = re.search(r"Name\s*:\s*(.*)", str(cv), re.I)
            if m2:
                rest = m2.group(1).strip().strip('"')
                if rest: return rest
            for k in range(ci+1, min(len(r), ci+4)):
                if str(r[k]).strip(): return str(r[k]).strip()
        return ""
    return _build_blocchi(rows, get_name)
def _norm_nome(s):
    s = re.sub(r"\s+", " ", str(s or "")).strip().upper()
    return re.split(r"\bDEPT\b", s)[0].strip()
def resolve_code(nome, mapping, codici_dip, A):
    n = _norm_nome(nome)
    if not n: return None, ""
    if n in codici_dip: return n, ""
    for m in mapping:
        nm, nmach = _norm_nome(m.get("nome_macchina")), A.s_str(m.get("n_macchina")).strip().upper()
        if n and n in (nm, nmach):
            cod = A.s_str(m.get("codice_lavoratore")).strip().upper()
            if cod: return cod, A.s_str(nome)
    for c in codici_dip:
        if c and c in n: return c, A.s_str(nome)
    return None, A.s_str(nome)
def coppie_giorno(per_giorno, attr, notte_ok, soglia_notte):
    esiti = []; pending = None
    for g in sorted(per_giorno.keys()):
        times = sorted(set(per_giorno.get(g, [])), key=to_min)
        if not times: continue
        i = 0
        if pending is not None:
            if to_min(times[0]) is not None and to_min(times[0]) <= soglia_notte:
                esiti.append((pending[0], pending[1], times[0], "OK", "uscita dopo mezzanotte (turno doppio)")); i = 1
            else:
                esiti.append((pending[0], pending[1], "", "DA_RIVEDERE", "uscita mancante")); pending = None
        rest = times[i:]
        if rest and not attr and not notte_ok and pending is None and timbro_notte(rest[0]):
            esiti.append((g, rest[0], "", "DA_RIVEDERE", "timbratura in fascia notturna - verificare")); rest = rest[1:]
        if attr and pending is None:
            entrate = [t for t in rest if to_min(t) >= 720]
            uscite_next = sorted({t for t in per_giorno.get(g+1, []) if to_min(t) < 720}, key=to_min)
            for k, e in enumerate(entrate):
                if k < len(uscite_next): esiti.append((g, e, uscite_next[k], "OK", "uscita dopo mezzanotte"))
                else: pending = (g, e)
            continue
        for k in range(0, len(rest)-1, 2): esiti.append((g, rest[k], rest[k+1], "OK", ""))
        if len(rest) % 2 == 1: pending = (g, rest[-1])
    if pending is not None: esiti.append((pending[0], pending[1], "", "DA_RIVEDERE", "uscita mancante"))
    return esiti
def tipo_giorno(anno, mese, g, festivi):
    try: d = date(anno, mese, g)
    except ValueError: return "feriale"
    if d.strftime("%d/%m/%Y") in festivi: return "festivo"
    if d.weekday() == 6: return "domenica"
    return "feriale"
def genera_righe_lavoratore(code, nome_macchina, per_giorno, anno, mese, g1, g2, tinfo, festivi, riposo, flottante, soglia_notte):
    rows = []; attr = tinfo.get("attr", False); start = tinfo.get("start")
    notte_ok = (start is not None and start < 120) or flottante
    for (g, ingr, usc, stato, nota) in coppie_giorno(per_giorno, attr, notte_ok, soglia_notte):
        if g < g1 or g > g2: continue
        ore = 0.0
        if ingr and usc:
            diff = to_min(usc) - to_min(ingr)
            if diff < 0: diff += 1440
            ore = round(diff/60.0, 2)
        rows.append({"codice_lavoratore": code, "nome_macchina": nome_macchina or code, "data": f"{g:02d}/{mese:02d}/{anno}",
                     "ora_ingresso": ingr or "", "ora_uscita": usc or "", "ore_lavorate": f"{ore:.2f}",
                     "tipo_giorno": tipo_giorno(anno, mese, g, festivi), "stato": stato, "note": nota})
    timbrati = set(per_giorno.keys())
    if not flottante:
        for g in range(g1, g2+1):
            if g in timbrati: continue
            tg = tipo_giorno(anno, mese, g, festivi)
            if tg != "feriale": continue
            try: wd = GIORNI_SETTIMANA[date(anno, mese, g).weekday()]
            except ValueError: continue
            if wd in riposo: continue
            rows.append({"codice_lavoratore": code, "nome_macchina": nome_macchina or code, "data": f"{g:02d}/{mese:02d}/{anno}",
                         "ora_ingresso": "", "ora_uscita": "", "ore_lavorate": "0.00", "tipo_giorno": tg, "stato": "ASSENTE", "note": ""})
    return rows
def scrivi_presenze(A, parsed):
    _, mapping = A.leggi_foglio("MAPPING_PRESENZE")
    b = A.leggi_admin()
    dips = b.get("DIPENDENTI", [])
    codici_dip = {A.s_str(d.get("codice")).upper() for d in dips if A.s_str(d.get("codice"))}
    turni_dip = {A.s_str(d.get("codice")).upper(): A.s_str(d.get("turno")).upper() for d in dips}
    turni = mappa_turni(A, b.get("TURNI", []))
    cfg, festivi = leggi_config(A)
    _, pres_old = A.leggi_foglio("PRESENZE", force=True)
    esistenti = {(A.s_str(p.get("codice_lavoratore")).upper(), A.s_str(p.get("data"))) for p in pres_old}
    rows, unmapped, dup = [], set(), 0
    anno, mese, g1, g2 = parsed["anno"], parsed["mese"], parsed["g1"], parsed["g2"]
    for blk in parsed["blocchi"]:
        code, nome_macchina = resolve_code(blk["nome"], mapping, codici_dip, A)
        if not code: unmapped.add(_norm_nome(blk["nome"])); continue
        tc = turni_dip.get(code, "")
        tinfo = turni.get(tc, {"attr": False, "start": None})
        for r in genera_righe_lavoratore(code, nome_macchina, blk["per_giorno"], anno, mese, g1, g2, tinfo, festivi, cfg.get("_riposo", {"sabato","domenica"}), tc in cfg.get("_flottanti", set()), cfg.get("_soglia_notte", 180)):
            key = (r["codice_lavoratore"], r["data"])
            if key in esistenti: dup += 1; continue
            esistenti.add(key); rows.append(r)
    if rows:
        if hasattr(A, "salva_append_many"): ok, msg = A.salva_append_many("PRESENZE", rows)
        else:
            ok, msg = True, "ok"
            for rr in rows:
                ok, msg = A.salva_append("PRESENZE", rr)
                if not ok: break
        if not ok: return {"ok": False, "msg": msg}
    return {"ok": True, "scritte": len(rows), "okn": sum(1 for r in rows if r["stato"]=="OK"),
            "dar": sum(1 for r in rows if r["stato"]=="DA_RIVEDERE"), "abs": sum(1 for r in rows if r["stato"]=="ASSENTE"),
            "dup": dup, "unmapped": sorted(x for x in unmapped if x)}
def xls_matrix(data):
    import xlrd
    wb = xlrd.open_workbook(file_contents=data)
    sh = next((s for s in wb.sheets() if "log" in s.name.lower()), None) or wb.sheet_by_index(0)
    rows = []
    for ri in range(sh.nrows):
        cells = []
        for ci in range(sh.ncols):
            v = sh.cell_value(ri, ci)
            if isinstance(v, float) and 0 < v < 1:
                hh, mm, ss = xlrd.xldate_as_tuple(v, wb.datemode)[3:6] if hasattr(xlrd, "xldate_as_tuple") else (0,0,0)
                cells.append(f"{hh:02d}:{mm:02d}")
            elif isinstance(v, float) and v == int(v): cells.append(str(int(v)))
            else: cells.append("" if v is None else str(v))
        rows.append(cells)
    return rows
def calcola_busta(pp_list, tipo_paga, base, cfg, turno_start):
    ore_norm = cfg.get("ore_normali_giorno", 8) or 8
    s1, s2 = cfg.get("straordinario_1_percent", 25), cfg.get("straordinario_2_percent", 50)
    toll, pen = cfg.get("ritardo_tolleranza_min", 15), cfg.get("assenza_penale_percent", 0)
    v_or = base if tipo_paga == "orario" else (base/26.0/ore_norm if tipo_paga == "mensile" else base/ore_norm)
    n_giorni = n_assenze = n_dar = mezzore = 0
    ore_tot = ore_stra = comp_base = comp_stra = 0.0
    for p in pp_list:
        st = p["_stato"]
        if st in ("ANNULLATA", "RIPOSO", "MALATTIA", "GIUSTIFICATA"): continue
        if st == "ASSENTE": n_assenze += 1; continue
        if st == "DA_RIVEDERE": n_dar += 1; continue
        if st != "OK": continue
        n_giorni += 1; ore = p["_ore"]; ore_tot += ore
        extra = max(0.0, ore - ore_norm); ore_stra += extra
        mult = (1+s2/100.0) if p.get("tipo_giorno") in ("domenica", "festivo") else (1+s1/100.0)
        if tipo_paga == "giornaliero": comp_base += base
        elif tipo_paga == "orario": comp_base += min(ore, ore_norm) * v_or
        comp_stra += extra * v_or * mult
        ingr = str(p.get("ora_ingresso") or "").strip()
        if ingr and turno_start is not None and to_min(ingr) is not None:
            diff = to_min(ingr) - (turno_start + toll)
            if diff > 0: mezzore += math.ceil(diff/30.0)
    trat = mezzore * (v_or/2.0)
    if tipo_paga == "mensile": comp_base = base/2.0 - n_assenze * (base/26.0) * (1+pen/100.0)
    elif pen > 0 and n_assenze > 0: comp_base -= n_assenze * (base if tipo_paga=="giornaliero" else v_or*ore_norm) * (pen/100.0)
    return {"n_giorni": n_giorni, "n_assenze": n_assenze, "n_dar": n_dar, "ore_tot": round(ore_tot,2),
            "ore_stra": round(ore_stra,2), "mezzore": mezzore, "comp_base": comp_base, "comp_stra": comp_stra,
            "trat_rit": trat, "lordo": comp_base + comp_stra - trat}
def pianifica_acconti(code, accs, A):
    ded, piani = 0.0, []
    for idx, a in enumerate(accs):
        if A.s_str(a.get("codice_lavoratore")).upper() != code: continue
        if A.s_str(a.get("stato")).lower() in ("chiuso", "annullato"): continue
        imp = to_float(A.s_str(a.get("importo")))
        if imp <= 0: continue
        if "rate" in A.s_str(a.get("modalita_rimborso")).lower():
            nr = max(1, int(to_float(A.s_str(a.get("numero_rate"))) or 1))
            rata = to_float(A.s_str(a.get("importo_rata"))) or (imp/nr)
            rp = int(to_float(A.s_str(a.get("rate_pagate"))))
            if rp >= nr: piani.append((idx, {"stato": "chiuso"}, 0.0, a)); continue
            ded += rata; rp2 = rp+1
            piani.append((idx, {"rate_pagate": str(rp2), "stato": "chiuso" if rp2 >= nr else "in_corso"}, rata, a))
        else:
            ded += imp; piani.append((idx, {"stato": "chiuso"}, imp, a))
    return ded, piani
def calcola_anteprima(A, lingua, anno, mese, quindicina):
    cfg, festivi = leggi_config(A)
    b = A.leggi_admin(force=True)
    dips, sals = b.get("DIPENDENTI", []), b.get("SALARI", [])
    turni = mappa_turni(A, b.get("TURNI", []))
    _, pres = A.leggi_foglio("PRESENZE", force=True)
    _, accs = A.leggi_foglio("ACCONTI", force=True)
    _, pays = A.leggi_foglio("PAGAMENTI", force=True)
    g_in = 1 if quindicina == 1 else 16
    g_fine = 15 if quindicina == 1 else calendar.monthrange(anno, mese)[1]
    da, a = date(anno, mese, g_in), date(anno, mese, g_fine)
    pda, paa = da.strftime("%d/%m/%Y"), a.strftime("%d/%m/%Y")
    pres_per, dar_count = {}, 0
    for i, p in enumerate(pres):
        d = parse_data(A.s_str(p.get("data")))
        if not d or not (da <= d <= a): continue
        cod = A.s_str(p.get("codice_lavoratore")).upper()
        if not cod: continue
        pp = dict(p); pp["_idx"] = i; pp["_ore"] = to_float(A.s_str(p.get("ore_lavorate")))
        pp["_stato"] = A.s_str(p.get("stato")).upper()
        if pp["_stato"] == "DA_RIVEDERE": dar_count += 1
        pres_per.setdefault(cod, []).append(pp)
    dip_map = {A.s_str(d.get("codice")).upper(): d for d in dips}
    sal_map = {}
    for s in sals:
        cod = A.s_str(s.get("codice_lavoratore")).upper()
        if not cod or A.s_str(s.get("data_fine_validita")): continue
        cur = sal_map.get(cod)
        if cur is None: sal_map[cod] = s
        else:
            d1 = parse_data(A.s_str(s.get("data_inizio_validita"))) or date(1900,1,1)
            d0 = parse_data(A.s_str(cur.get("data_inizio_validita"))) or date(1900,1,1)
            if d1 > d0: sal_map[cod] = s
    giapagati = {A.s_str(py.get("codice_lavoratore")).upper() for py in pays
                 if A.s_str(py.get("periodo_da")) == pda and A.s_str(py.get("periodo_a")) == paa}
    dets, avvisi = [], []
    ext_on = paghe_esterni_attive(cfg)
    for code in sorted(set(list(pres_per.keys()) + list(sal_map.keys()))):
        dip = dip_map.get(code, {})
        nome = f"{A.s_str(dip.get('cognome'))} {A.s_str(dip.get('nome'))}".strip() or code
        if not _stato_attivo(dip): avvisi.append(f"{code} {nome}: {t6('cessato_skip', lingua)}"); continue
        if _is_esterno(dip) and not ext_on: avvisi.append(f"{code} {nome}: {t6('esterno_skip', lingua)}"); continue
        if code in giapagati: avvisi.append(f"{code} {nome}: {t6('paghe_gia', lingua)}"); continue
        sal = sal_map.get(code)
        if not sal: avvisi.append(f"{code} {nome}: {t6('paghe_no_salario', lingua)}"); continue
        tipo_paga = A.s_str(sal.get("tipo_paga")).lower() or cfg.get("modalita_paga", "giornaliero")
        base = to_float(A.s_str(sal.get("importo_base")))
        tinfo = turni.get(A.s_str(dip.get("turno")).upper(), {"attr": False, "start": None})
        busta = calcola_busta(pres_per.get(code, []), tipo_paga, base, cfg, tinfo.get("start"))
        ded, piani = pianifica_acconti(code, accs, A)
        fissa = _flag_fissa(dip)
        if not fissa and busta["n_giorni"] == 0 and busta["n_assenze"] == 0 and ded == 0: continue
        tratt = calcola_trattenute_senegal(max(0.0, busta["lordo"]), cfg)
        d = {"code": code, "nome": nome, "tipo_paga": tipo_paga, "base": base,
             "turno": A.s_str(dip.get("turno")), "ded": ded, "piani": piani,
             "tratt": tratt, "tratt_tot": tratt["totale"], "fissa": fissa, "esterno": _is_esterno(dip)}
        d.update(busta); dets.append(d)
    return {"pda": pda, "paa": paa, "dets": dets, "avvisi": avvisi, "dar_count": dar_count,
            "festivi_default": cfg.get("_festivi_default", False), "trattenute_attive": trattenute_attive(cfg)}
def conferma_paghe(A, ant):
    rows, piani_totali = [], []
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    for det in ant["dets"]:
        premio = to_float(st.session_state.get(f"f6_premio_{det['code']}", 0))
        lordo, ded = round(det["lordo"]), round(det["ded"])
        tratt = det.get("tratt", {}); tratt_tot = round(det.get("tratt_tot", 0))
        rows.append({"id_pagamento": f"PAG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{det['code']}",
                     "codice_lavoratore": det["code"], "periodo_da": ant["pda"], "periodo_a": ant["paa"],
                     "tipo_pagamento": det["tipo_paga"], "importo_lordo": str(lordo), "acconti_dedotti": str(ded),
                     "premi_produzione": str(round(premio)), "importo_netto": str(lordo - ded - tratt_tot + round(premio)),
                     "trattenute_css": str(tratt.get("css",0)), "trattenute_ipres": str(tratt.get("ipres",0)),
                     "trattenute_ipm": str(tratt.get("ipm",0)), "trattenute_ir": str(tratt.get("ir",0)),
                     "trattenute_totale": str(tratt_tot),
                     "data_pagamento": datetime.now().strftime("%d/%m/%Y"), "stato": "confermato", "timestamp": ts})
        for idx, upd, imp, _s in det["piani"]:
            if imp > 0: piani_totali.append((idx, upd))
    if rows:
        if hasattr(A, "salva_append_many"): ok, msg = A.salva_append_many("PAGAMENTI", rows)
        else:
            ok, msg = True, "ok"
            for rr in rows:
                ok, msg = A.salva_append("PAGAMENTI", rr)
                if not ok: break
        if not ok: return False, msg, 0
    for idx, upd in piani_totali: A.salva_update("ACCONTI", idx, upd)
    return True, "ok", len(rows)
def calcola_solde_de_tout_compte(A, code, dip, sal, cfg, motivo, data_fine_str, preavviso_lavorato, giorni_congedo):
    data_fine = parse_data(data_fine_str) or date.today()
    data_inizio = parse_data(sal.get("data_inizio_validita")) or parse_data(dip.get("data_registrazione")) or data_fine
    anz = max(0.0, (data_fine - data_inizio).days / 365.0)
    tipo_paga = A.s_str(sal.get("tipo_paga")).lower() or "giornaliero"
    base = to_float(sal.get("importo_base"))
    ore_norm = cfg.get("ore_normali_giorno", 8) or 8
    if tipo_paga == "mensile": base_mese, base_giorno = base, base/26.0
    elif tipo_paga == "orario": base_giorno, base_mese = base*ore_norm, base*ore_norm*26.0
    else: base_giorno, base_mese = base, base*26.0
    ind_preav = 0.0 if preavviso_lavorato else base_mese * cfg.get("preavviso_mesi", 1.0)
    ind_cong = giorni_congedo * base_giorno
    ind_lic = anz * base_mese * cfg.get("indennita_licenziamento_mesi_per_anno", 0.0) if motivo == "licenziamento" else 0.0
    return {"code": code, "motivo": motivo, "data_fine": data_fine_str, "anzianita_anni": anz,
            "ind_preavviso": round(ind_preav), "ind_congedo": round(ind_cong), "ind_licenziamento": round(ind_lic),
            "totale": round(ind_preav + ind_cong + ind_lic)}
def conferma_solde(A, code, stato_fin, data_fine_str):
    _, dips = A.leggi_foglio("DIPENDENTI", force=True)
    idx = next((i for i, r in enumerate(dips) if A.s_str(r.get("codice")).upper() == code.upper()), None)
def conferma_solde(A, code, stato_fin, data_fine_str):
    _, dips = A.leggi_foglio("DIPENDENTI", force=True)
    idx = next((i for i, r in enumerate(dips) if A.s_str(r.get("codice")).upper() == code.upper()), None)
    if idx is None: return False, "dipendente non trovato"
    ok, _ = A.salva_update("DIPENDENTI", idx, {"stato_lavorativo": stato_fin, "data_fine_rapporto": data_fine_str})
    _, sals = A.leggi_foglio("SALARI", force=True)
    for i, s in enumerate(sals):
        if A.s_str(s.get("codice_lavoratore")).upper() == code.upper() and not A.s_str(s.get("data_fine_validita")):
            A.salva_update("SALARI", i, {"data_fine_validita": data_fine_str})
    _, mans = A.leggi_foglio("STORICO_MANSIONI", force=True)
    for i, m in enumerate(mans):
        if A.s_str(m.get("code_travailleur")).upper() == code.upper() and not A.s_str(m.get("date_fin")):
            A.salva_update("STORICO_MANSIONI", i, {"date_fin": data_fine_str})
    return ok, "ok"
def genera_releve_esterni(A, anno, mese):
    b = A.leggi_admin(force=True)
    esterni = {A.s_str(d.get("codice")).upper(): d for d in b.get("DIPENDENTI", []) if _is_esterno(d)}
    if not esterni: return [], ""
    _, pres = A.leggi_foglio("PRESENZE", force=True)
    agg = {}
    for p in pres:
        d = parse_data(A.s_str(p.get("data")))
        if not d or d.year != anno or d.month != mese: continue
        cod = A.s_str(p.get("codice_lavoratore")).upper()
        if cod not in esterni or A.s_str(p.get("stato")).upper() != "OK": continue
        a = agg.setdefault(cod, {"giorni": 0, "ore": 0.0})
        a["giorni"] += 1; a["ore"] += to_float(A.s_str(p.get("ore_lavorate")))
    rows = [{"codice": c, "nome": f"{A.s_str(esterni[c].get('cognome'))} {A.s_str(esterni[c].get('nome'))}",
             "societa": A.s_str(esterni[c].get("societa_formale")), "giorni": v["giorni"], "ore": round(v["ore"], 2)}
            for c, v in sorted(agg.items())]
    out = io.StringIO(); w = csv.writer(out, delimiter=";")
    w.writerow(["codice", "nom_prenom", "societe_formelle", "jours", "heures", "mois", "annee"])
    for r in rows: w.writerow([r["codice"], r["nome"], r["societa"], r["giorni"], f"{r['ore']:.2f}", f"{mese:02d}", anno])
    return rows, out.getvalue()
def genera_busta_paga(A, lingua, dip, det, pago, storico, acconti):
    az = A.azienda_info()
    pdf = FPDF(); pdf.add_page()
    try:
        lg = requests.get(LOGO_BASE + A.cfg_get("logo_azienda", "adtrading.png"), timeout=20)
        if lg.status_code == 200 and lg.content: pdf.image(lg.content, x=10, y=8, w=30)
    except Exception: pass
    pdf.set_xy(60, 10); pdf.set_font("Helvetica", "B", 11); pdf.cell(0, 6, _pdf_safe(az.get("nome", "")), 0, 1, "R")
    pdf.set_font("Helvetica", "", 7); pdf.set_xy(60, 17); pdf.multi_cell(130, 4, _pdf_safe(az.get("indirizzo", "")), align="R")
    pdf.set_xy(60, 26); pdf.cell(0, 4, _pdf_safe(f"tel. {az.get('tel','')} - {az.get('email','')}"), 0, 1, "R")
    pdf.set_xy(10, 40); pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, _pdf_safe(t6("buste_title", lingua).replace("🖨️", "").strip().upper()), 0, 1, "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _pdf_safe(f"{t6('buste_worker', lingua)}: {A.s_str(dip.get('cognome'))} {A.s_str(dip.get('nome'))} - {A.s_str(dip.get('codice'))}"), 0, 1, "L")
    pdf.cell(0, 6, _pdf_safe(f"{t6('buste_period', lingua)}: {A.s_str(pago.get('periodo_da'))} -> {A.s_str(pago.get('periodo_a'))}"), 0, 1, "L")
    if det and det.get("fissa"):
        pdf.set_font("Helvetica", "I", 8); pdf.cell(0, 5, _pdf_safe(t6("fissa_badge", lingua)), 0, 1, "L"); pdf.set_font("Helvetica", "", 9)
    if det and det.get("esterno"):
        pdf.set_font("Helvetica", "I", 8); pdf.cell(0, 5, _pdf_safe(t6("esterno_badge", lingua)), 0, 1, "L"); pdf.set_font("Helvetica", "", 9)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    for lab in ("col_giorni", "col_ore", "col_stra", "col_rit"): pdf.cell(47, 6, _pdf_safe(t6(lab, lingua)), 1, 0, "C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(47, 6, str(det.get("n_giorni", 0)) if det else "-", 1, 0, "C")
    pdf.cell(47, 6, f"{det.get('ore_tot',0):.1f}" if det else "-", 1, 0, "C")
    pdf.cell(47, 6, f"{det.get('ore_stra',0):.1f}" if det else "-", 1, 0, "C")
    pdf.cell(47, 6, str(det.get("mezzore", 0)) if det else "-", 1, 1, "C")
    pdf.ln(3)
    pdf.cell(0, 6, _pdf_safe(f"{t6('tot_lordo', lingua)}: {to_float(pago.get('importo_lordo')):,.0f} FCFA"), 0, 1, "L")
    tratt_vis = False
    if det and det.get("tratt") and det["tratt"].get("totale", 0) > 0:
        tratt = det["tratt"]; tratt_vis = True
        pdf.set_font("Helvetica", "B", 9); pdf.cell(0, 6, _pdf_safe(t6("tratt_title", lingua)), 0, 1, "L")
        pdf.set_font("Helvetica", "", 8)
        for k, lab in (("css", "tratt_css"), ("ipres", "tratt_ipres"), ("ipm", "tratt_ipm"), ("ir", "tratt_ir")):
            pdf.cell(0, 5, _pdf_safe(f"- {t6(lab, lingua)}: {tratt[k]:,.0f} FCFA"), 0, 1, "L")
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, _pdf_safe(f"{t6('tratt_tot', lingua)}: -{tratt['totale']:,.0f} FCFA"), 0, 1, "L")
        pdf.set_font("Helvetica", "I", 7); pdf.multi_cell(0, 4, _pdf_safe(t6("tratt_note", lingua))); pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _pdf_safe(f"{t6('tot_acc', lingua)}: -{to_float(pago.get('acconti_dedotti')):,.0f} FCFA"), 0, 1, "L")
    pdf.cell(0, 6, _pdf_safe(f"{t6('premi_title', lingua)}: +{to_float(pago.get('premi_produzione')):,.0f} FCFA"), 0, 1, "L")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, _pdf_safe(f"NET: {to_float(pago.get('importo_netto')):,.0f} FCFA"), 0, 1, "L")
    if tratt_vis and det:
        tratt = det["tratt"]; pdf.ln(2)
        pdf.set_font("Helvetica", "B", 8); pdf.cell(0, 5, _pdf_safe(t6("dat_title", lingua)), 0, 1, "L")
        pdf.set_font("Helvetica", "", 7)
        for k, lab in (("dat_css_af", "dat_css_af"), ("dat_css_at", "dat_css_at"), ("dat_ipres", "dat_ipres"), ("dat_ipm", "dat_ipm"), ("dat_fnp", "dat_fnp")):
            pdf.cell(0, 4, _pdf_safe(f"- {t6(lab, lingua)}: {tratt[k]:,.0f} FCFA"), 0, 1, "L")
    if acconti:
        pdf.ln(2); pdf.set_font("Helvetica", "B", 9); pdf.cell(0, 6, _pdf_safe(t6("buste_avances", lingua)), 0, 1, "L")
        pdf.set_font("Helvetica", "", 8)
        for a in acconti:
            mod = A.s_str(a.get("modalita_rimborso"))
            piano = f" - rate {A.s_str(a.get('rate_pagate')) or '0'}/{A.s_str(a.get('numero_rate')) or '-'}" if "rate" in mod.lower() else " - unica"
            pdf.cell(0, 5, _pdf_safe(f"- {A.s_str(a.get('tipo_acconto')) or 'generico'}: {to_float(a.get('importo')):,.0f} FCFA{piano}"), 0, 1, "L")
    if storico:
        pdf.ln(2); pdf.set_font("Helvetica", "B", 9); pdf.cell(0, 6, _pdf_safe(t6("buste_hist", lingua)), 0, 1, "L")
        pdf.set_font("Helvetica", "", 8)
        for p in storico:
            pdf.cell(0, 5, _pdf_safe(f"- {A.s_str(p.get('periodo_da'))} -> {A.s_str(p.get('periodo_a'))}: NET {to_float(p.get('importo_netto')):,.0f} FCFA"), 0, 1, "L")
    pdf.ln(4); pdf.set_font("Helvetica", "", 9)
    pdf.cell(95, 6, "Signature travailleur", 1, 0, "C"); pdf.cell(95, 6, "Signature employeur", 1, 1, "C")
    pdf.cell(95, 15, "", 0, 0); pdf.cell(95, 15, "", 0, 1)
    out = pdf.output(dest="S")
    return out.encode("latin-1", "ignore") if isinstance(out, str) else bytes(out)
def sezione_buste(A, lingua):
    st.subheader(t6("buste_title", lingua))
    dips = A.leggi_admin().get("DIPENDENTI", [])
    _, pays = A.leggi_foglio("PAGAMENTI", force=True)
    _, accs = A.leggi_foglio("ACCONTI", force=True)
    opzioni, codmap = [], {}
    for d in dips:
        cod = A.s_str(d.get("codice"))
        if cod:
            lab = f"{cod} — {A.s_str(d.get('cognome'))} {A.s_str(d.get('nome'))}"
            opzioni.append(lab); codmap[lab] = cod
    if not opzioni: st.info(t6("buste_none", lingua)); return
    lab = st.selectbox(t6("buste_worker", lingua), opzioni, key="f6_buste_worker")
    code = codmap[lab]
    dip = next((d for d in dips if A.s_str(d.get("codice")) == code), {})
    miei = [p for p in pays if A.s_str(p.get("codice_lavoratore")).upper() == code.upper()]
    miei.sort(key=lambda p: data_ord(p.get("periodo_da")) or (0, 0, 0), reverse=True)
    if not miei: st.info(t6("buste_none", lingua)); return
    opts_p = [f"{A.s_str(p.get('periodo_da'))} -> {A.s_str(p.get('periodo_a'))}" for p in miei]
    sel = st.selectbox(t6("buste_period", lingua), opts_p, key="f6_buste_period")
    pago = miei[opts_p.index(sel)]
    d0 = parse_data(pago.get("periodo_da")); det = None
    if d0:
        ant = calcola_anteprima(A, lingua, d0.year, d0.month, 1 if d0.day == 1 else 2)
        det = next((x for x in ant["dets"] if x["code"].upper() == code.upper()), None)
    acconti = [a for a in accs if A.s_str(a.get("codice_lavoratore")).upper() == code.upper() and A.s_str(a.get("stato")).lower() not in ("annullato",)]
    if st.button(t6("buste_gen", lingua), type="primary", use_container_width=True):
        st.download_button("📥 PDF", data=genera_busta_paga(A, lingua, dip, det, pago, miei, acconti),
                           file_name=f"Busta_{code}_{A.s_str(pago.get('periodo_da'))}.pdf", mime="application/pdf", use_container_width=True)
def sezione_import(A, lingua):
    st.subheader("📥 " + t6("import_title", lingua)); st.caption(t6("import_hint", lingua))
    c1, c2 = st.columns([3, 1])
    c1.number_input(t6("paghe_anno", lingua), min_value=2024, max_value=2035, value=datetime.now().year, key="f6_imp_anno")
    nomi = MESI.get(lingua, MESI["fr"])
    c2.selectbox(t6("paghe_mese", lingua), list(range(1, 13)), format_func=lambda m: nomi[m-1], index=datetime.now().month-1, key="f6_imp_mese")
    up = st.file_uploader(t6("import_up_label", lingua), type=["xls", "xlsx"])
    if up is not None and st.button("🔎 " + t6("import_mem_btn", lingua), use_container_width=True):
        try:
            parsed = parse_matrix(xls_matrix(up.getvalue()))
            if parsed and parsed["blocchi"]:
                st.session_state.f6_parsed = parsed; st.session_state.pop("f6_esito_import", None); st.rerun()
            else: st.error(t6("parsed_none", lingua))
        except Exception as e: st.error(f"{t6('parsed_none', lingua)} — {e}")
    testo = st.text_area(t6("import_da_testo", lingua), height=200, key="f6_ta")
    if st.button("🔎 " + t6("import_parse_btn", lingua), type="primary"):
        if not testo.strip(): st.warning(t6("import_empty", lingua))
        else:
            parsed = parse_list_of_logs(testo)
            if not parsed["anno"] or not parsed["blocchi"]: st.error(t6("parsed_none", lingua))
            else: st.session_state.f6_parsed = parsed; st.session_state.pop("f6_esito_import", None); st.rerun()
    parsed = st.session_state.get("f6_parsed")
    if parsed:
        st.success(f"{t6('parsed_ok', lingua)} — {t6('import_period', lingua)}: {parsed['g1']:02d}/{parsed['mese']:02d}/{parsed['anno']} → {parsed['g2']:02d}/{parsed['mese']:02d}/{parsed['anno']} — {len(parsed['blocchi'])} {t6('import_workers', lingua)}")
        if st.button("💾 " + t6("import_write_btn", lingua), type="primary"):
            with st.spinner("..."):
                esito = scrivi_presenze(A, parsed)
                st.session_state.f6_esito_import = esito; st.session_state.pop("f6_parsed", None); st.rerun()
    esito = st.session_state.get("f6_esito_import")
    if esito:
        if esito.get("ok"):
            st.success(f"✅ {esito['scritte']} {t6('import_written', lingua)} (OK: {esito['okn']} — DA_RIVEDERE: {esito['dar']} — ASSENTE: {esito['abs']}) — {esito['dup']} {t6('import_dup', lingua)}")
            if esito["dar"] > 0: st.info(t6("import_go_anomalies", lingua))
            if esito["unmapped"]: st.warning(t6("import_unmapped", lingua) + ", ".join(esito["unmapped"]))
        else: st.error("❌ " + str(esito.get("msg")))
def sezione_anomalie(A, lingua):
    st.subheader("🔍 " + t6("anom_title", lingua))
    _, pres = A.leggi_foglio("PRESENZE", force=True)
    righe = [(i, p) for i, p in enumerate(pres) if A.s_str(p.get("stato")).upper() in ("DA_RIVEDERE", "ASSENTE")]
    if not righe: st.success(t6("anom_none", lingua)); return
    st.caption(t6("anom_hint", lingua))
    opts = ["OK", "ASSENTE", "RIPOSO", "MALATTIA", "ANNULLATA"]
    for i, p in righe[:60]:
        stato = A.s_str(p.get("stato")).upper()
        with st.expander(f"{stato} — {A.s_str(p.get('codice_lavoratore'))} — {A.s_str(p.get('data'))} — ▶ {A.s_str(p.get('ora_ingresso')) or '…'}"):
            c1, c2, c3 = st.columns(3)
            c1.text_input(t6("anom_uscita", lingua), value=A.s_str(p.get("ora_uscita")), key=f"f6u{i}")
            c2.selectbox(t6("anom_stato", lingua), opts, index=opts.index(stato) if stato in opts else 1, key=f"f6s{i}")
            c3.text_input(t6("anom_note", lingua), value=A.s_str(p.get("note")), key=f"f6n{i}")
    if st.button("💾 " + t6("anom_save_all", lingua), type="primary", use_container_width=True):
        fatte = 0
        for i, p in righe[:60]:
            o_s, o_u, o_n = A.s_str(p.get("stato")).upper(), A.s_str(p.get("ora_uscita")), A.s_str(p.get("note"))
            n_s = st.session_state.get(f"f6s{i}", o_s); n_u = (st.session_state.get(f"f6u{i}") or "").strip(); n_n = st.session_state.get(f"f6n{i}", o_n)
            if (n_s, n_u, n_n) == (o_s, o_u, o_n): continue
            upd = {"stato": n_s, "note": n_n}; ok_row = True
            if n_s == "OK":
                ingr = A.s_str(p.get("ora_ingresso"))
                if ingr and n_u and to_min(ingr) is not None and to_min(n_u) is not None:
                    diff = to_min(n_u) - to_min(ingr)
                    if diff < 0: diff += 1440
                    upd["ora_uscita"], upd["ore_lavorate"] = n_u, f"{round(diff/60.0,2):.2f}"
                else: ok_row = False; st.error(t6("anom_need_out", lingua))
            elif n_s == "ASSENTE": upd["ora_uscita"], upd["ore_lavorate"] = "", "0.00"
            if ok_row:
                ok, _ = A.salva_update("PRESENZE", i, upd)
                if ok: fatte += 1
        st.success(f"✅ {fatte} {t6('anom_fixed_n', lingua)}"); st.rerun()
    if len(righe) > 60: st.caption(f"… {len(righe)-60}+")
def render_anteprima(lingua, ant):
    if ant.get("festivi_default"): st.warning("⚠️ Jours fériés par défaut — complétez CONFIG.")
    if ant["dar_count"] > 0: st.warning(f"⚠️ {ant['dar_count']} {t6('dar_warn', lingua)}")
    for av in ant["avvisi"]: st.caption("• " + av)
    if ant.get("trattenute_attive"): st.caption("ℹ️ " + t6("tratt_note", lingua))
    tab = []
    for det in ant["dets"]:
        tipo_lbl = det["tipo_paga"]
        if det.get("fissa"): tipo_lbl += " • " + t6("fissa_badge", lingua)
        if det.get("esterno"): tipo_lbl += " • " + t6("esterno_badge", lingua)
        tab.append({t6("col_codice", lingua): det["code"], t6("col_nome", lingua): det["nome"],
                    t6("col_tipo", lingua): tipo_lbl, t6("col_base", lingua): f"{det['base']:,.0f}",
                    t6("col_giorni", lingua): det["n_giorni"], t6("col_ore", lingua): f"{det['ore_tot']:.1f}",
                    t6("col_stra", lingua): f"{det['ore_stra']:.1f}", t6("col_rit", lingua): det["mezzore"],
                    t6("col_abs", lingua): det["n_assenze"], t6("col_lordo", lingua): f"{det['lordo']:,.0f}",
                    t6("col_tratt", lingua): f"{det.get('tratt_tot',0):,.0f}", t6("col_acc", lingua): f"{det['ded']:,.0f}"})
    st.dataframe(tab, use_container_width=True, hide_index=True)
    with st.expander("🏆 " + t6("premi_title", lingua)):
        for det in ant["dets"]:
            st.number_input(f"{det['code']} — {det['nome']}", min_value=0, step=500, key=f"f6_premio_{det['code']}")
    tl, td, tt = sum(d["lordo"] for d in ant["dets"]), sum(d["ded"] for d in ant["dets"]), sum(d.get("tratt_tot", 0) for d in ant["dets"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t6("tot_lordo", lingua), f"{tl:,.0f} FCFA"); c2.metric(t6("tot_tratt", lingua), f"{tt:,.0f} FCFA")
    c3.metric(t6("tot_acc", lingua), f"{td:,.0f} FCFA"); c4.metric(t6("tot_netto", lingua), f"{tl-tt-td:,.0f} FCFA")
    st.caption(t6("netto_hint", lingua))
def sezione_paghe(A, lingua):
    st.subheader("💰 " + t6("paghe_title", lingua))
    c1, c2, c3, c4 = st.columns([1, 1.4, 1.5, 1.4])
    anno = c1.number_input(t6("paghe_anno", lingua), min_value=2024, max_value=2035, value=datetime.now().year, key="f6_anno")
    nomi = MESI.get(lingua, MESI["fr"])
    mese = c2.selectbox(t6("paghe_mese", lingua), list(range(1, 13)), format_func=lambda m: nomi[m-1], index=datetime.now().month-1, key="f6_mese")
    q = c3.radio(t6("paghe_quindicina", lingua), [t6("paghe_q1", lingua), t6("paghe_q2", lingua)], key="f6_q")
    quindicina = 1 if q == t6("paghe_q1", lingua) else 2
    if c4.button("🧮 " + t6("paghe_calc_btn", lingua), type="primary", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("f6_premio_"): st.session_state.pop(k, None)
        with st.spinner("..."): st.session_state.f6_ant = calcola_anteprima(A, lingua, int(anno), int(mese), quindicina)
        st.rerun()
    ant = st.session_state.get("f6_ant")
    if ant:
        st.markdown(f"{t6('paghe_periodo', lingua)}: {ant['pda']} → {ant['paa']}")
        if not ant["dets"]: st.info(t6("paghe_nulla", lingua)); return
        render_anteprima(lingua, ant)
        if st.button("✅ " + t6("paghe_confirm_btn", lingua), type="primary"):
            ok, msg, n = conferma_paghe(A, ant)
            if ok: st.session_state.pop("f6_ant", None); st.success(t6("paghe_done", lingua) + str(n))
            else: st.error(msg)
def sezione_acconti(A, lingua):
    st.subheader("💸 " + t6("acc_title", lingua))
    b = A.leggi_admin(); dips = b.get("DIPENDENTI", [])
    opzioni, codmap = [], {}
    for d in dips:
        cod = A.s_str(d.get("codice"))
        if cod:
            lab = f"{cod} — {A.s_str(d.get('cognome'))} {A.s_str(d.get('nome'))}"
            opzioni.append(lab); codmap[lab] = cod
    st.markdown("➕ " + t6("acc_new", lingua))
    with st.form("f6_new_acc"):
        c1, c2 = st.columns(2)
        lab = c1.selectbox(t6("acc_codice", lingua), opzioni) if opzioni else None
        tipo = c2.selectbox(t6("acc_tipo", lingua), ["generico", "tabasky", "scuola", "karem"], format_func=lambda x: t6("acc_" + x, lingua))
        c3, c4 = st.columns(2)
        importo = c3.number_input(t6("acc_importo", lingua), min_value=0, step=1000, key="f6acc_imp")
        mod = c4.selectbox(t6("acc_modalita", lingua), ["unica", "rate"], format_func=lambda x: t6("acc_" + x, lingua))
        c5, c6 = st.columns(2)
        dr = c5.text_input(t6("acc_data_rich", lingua), value=datetime.now().strftime("%d/%m/%Y"), key="f6acc_dr")
        de = c6.text_input(t6("acc_data_ero", lingua), value=datetime.now().strftime("%d/%m/%Y"), key="f6acc_de")
        nr = st.number_input(t6("acc_num_rate", lingua), min_value=1, max_value=24, value=3, key="f6acc_nr") if mod == "rate" else 1
        if st.form_submit_button("➕ " + t6("acc_crea_btn", lingua), type="primary"):
            if not lab or importo <= 0: st.error(t6("acc_err", lingua))
            else:
                rata = round(importo/max(1, nr)) if mod == "rate" else 0
                row = {"id_acconto": f"ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10,99)}",
                       "codice_lavoratore": codmap[lab], "tipo_acconto": tipo, "importo": str(int(importo)),
                       "data_richiesta": dr, "data_erogazione": de, "modalita_rimborso": mod,
                       "numero_rate": str(int(nr)) if mod == "rate" else "", "importo_rata": str(int(rata)) if mod == "rate" else "",
                       "rate_pagate": "0", "stato": "aperto", "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")}
                ok, msg = A.salva_append("ACCONTI", row)
                if ok: st.success(t6("acc_created", lingua) + " — " + t6("acc_dedotto", lingua)); st.rerun()
                else: st.error(msg)
    st.markdown("---"); st.markdown(t6("acc_open_title", lingua))
    _, accs = A.leggi_foglio("ACCONTI", force=True)
    aperti = [a for a in accs if A.s_str(a.get("stato")).lower() not in ("chiuso", "annullato")]
    if aperti:
        st.dataframe([{t6("col_codice", lingua): A.s_str(a.get("codice_lavoratore")), t6("acc_tipo", lingua): A.s_str(a.get("tipo_acconto")),
                       t6("acc_importo", lingua): A.s_str(a.get("importo")), t6("acc_modalita", lingua): A.s_str(a.get("modalita_rimborso")),
                       "Rate": f"{A.s_str(a.get('rate_pagate')) or '0'}/{A.s_str(a.get('numero_rate')) or '-'}",
                       "Rata": A.s_str(a.get("importo_rata")), t6("anom_stato", lingua): A.s_str(a.get("stato"))} for a in aperti],
                     use_container_width=True, hide_index=True)
    else: st.info(t6("acc_none", lingua))
def sezione_releve(A, lingua):
    st.subheader(t6("releve_title", lingua)); st.caption(t6("releve_hint", lingua))
    c1, c2 = st.columns(2)
    anno = c1.number_input(t6("paghe_anno", lingua), min_value=2024, max_value=2035, value=datetime.now().year, key="f7_rel_anno")
    nomi = MESI.get(lingua, MESI["fr"])
    mese = c2.selectbox(t6("paghe_mese", lingua), list(range(1, 13)), format_func=lambda m: nomi[m-1], index=datetime.now().month-1, key="f7_rel_mese")
    if st.button("🧮 " + t6("releve_gen_btn", lingua), type="primary"):
        rows, csvtxt = genera_releve_esterni(A, int(anno), int(mese))
        st.session_state.f7_rel = (rows, csvtxt, int(anno), int(mese))
    rel = st.session_state.get("f7_rel")
    if rel:
        rows, csvtxt, ay, mo = rel
        if not rows: st.info(t6("releve_no_ext", lingua)); return
        st.dataframe([{t6("col_codice", lingua): r["codice"], t6("col_nome", lingua): r["nome"],
                       t6("releve_soc", lingua): r["societa"], t6("col_giorni", lingua): r["giorni"],
                       t6("col_ore", lingua): r["ore"]} for r in rows], use_container_width=True, hide_index=True)
        st.download_button(t6("releve_csv_btn", lingua), data=csvtxt.encode("utf-8-sig"),
                           file_name=f"Releve_externes_{ay}-{mo:02d}.csv", mime="text/csv", use_container_width=True)
def sezione_solde(A, lingua):
    st.subheader(t6("solde_title", lingua)); st.caption(t6("solde_hint", lingua))
    b = A.leggi_admin()
    dips = [d for d in b.get("DIPENDENTI", []) if _stato_attivo(d)]
    opzioni, codmap = [], {}
    for d in dips:
        cod = A.s_str(d.get("codice"))
        if cod:
            lab = f"{cod} — {A.s_str(d.get('cognome'))} {A.s_str(d.get('nome'))}"
            opzioni.append(lab); codmap[lab] = cod
    if not opzioni: st.info(t6("solde_no_worker", lingua)); return
    lab = st.selectbox(t6("solde_worker", lingua), opzioni, key="f7_solde_w")
    code = codmap[lab]
    dip = next(d for d in dips if A.s_str(d.get("codice")) == code)
    sal = next((s for s in b.get("SALARI", []) if A.s_str(s.get("codice_lavoratore")).upper() == code.upper() and not A.s_str(s.get("data_fine_validita"))), None)
    if not sal: st.warning(t6("paghe_no_salario", lingua)); return
    cfg, _ = leggi_config(A)
    c1, c2 = st.columns(2)
    motivi = ["dimissioni", "licenziamento", "fine_prova", "altro"]
    motivo = c1.selectbox(t6("solde_motivo", lingua), motivi, format_func=lambda x: t6("solde_" + x, lingua), key="f7_solde_m")
    data_fine = c2.text_input(t6("solde_data_fine", lingua), value=datetime.now().strftime("%d/%m/%Y"), key="f7_solde_d")
    prev_lav = st.checkbox(t6("solde_preavviso_lav", lingua), key="f7_solde_pl")
    cong = st.number_input(t6("solde_congedi_gg", lingua), min_value=0, value=0, key="f7_solde_cg")
    if st.button("🧮 " + t6("solde_calc_btn", lingua), type="primary"):
        st.session_state.f7_solde = calcola_solde_de_tout_compte(A, code, dip, sal, cfg, motivo, data_fine, prev_lav, int(cong))
    solde = st.session_state.get("f7_solde")
    if solde and solde.get("code") == code:
        c1, c2, c3 = st.columns(3)
        c1.metric(t6("solde_preavviso_ind", lingua), f"{solde['ind_preavviso']:,.0f}")
        c2.metric(t6("solde_congedi_fcfa", lingua), f"{solde['ind_congedo']:,.0f}")
        c3.metric(t6("solde_indennita_fcfa", lingua), f"{solde['ind_licenziamento']:,.0f}")
        st.metric(t6("solde_totale", lingua), f"{solde['totale']:,.0f} FCFA")
        st.caption(f"Anzianità: {solde['anzianita_anni']:.1f} — {t6('tratt_note', lingua)}")
        if st.button("✅ " + t6("solde_confirm_btn", lingua), type="primary"):
            stato_fin = "dimissionario" if motivo == "dimissioni" else "licenziato"
            ok, msg = conferma_solde(A, code, stato_fin, data_fine)
            if ok: st.session_state.pop("f7_solde", None); st.success(t6("solde_archived", lingua)); st.rerun()
            else: st.error(msg)
def pagina_fase7(lingua, app_module):
    A = app_module
    st.title(t6("titolo", lingua)); st.caption(VERSIONE_PAGHE)
    cfg, _ = leggi_config(A)
    with st.expander("⚙️ CONFIG"):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Straord. feriale", f"+{cfg['straordinario_1_percent']:.0f}%")
        c2.metric("Straord. dim./férié", f"+{cfg['straordinario_2_percent']:.0f}%")
        c3.metric("Ore normali", f"{cfg['ore_normali_giorno']:.0f}")
        c4.metric("Toll. ritardo", f"{cfg['ritardo_tolleranza_min']:.0f} min")
        c5.metric("Penale assenza", f"{cfg['assenza_penale_percent']:.0f}%")
        if trattenute_attive(cfg):
            c6, c7, c8, c9 = st.columns(4)
            c6.metric("CSS lav.", f"{cfg['css_lavoratore_percent']:.1f}%")
            c7.metric("IPRES T1 lav.", f"{cfg['ipres_t1_lav_percent']:.1f}%")
            c8.metric("IPM lav.", f"{cfg['ipm_lavoratore_percent']:.1f}%")
            c9.metric("IR frais prof.", f"{cfg['ir_frais_prof_percent']:.0f}%")
            st.caption(t6("tratt_note", lingua))
        else: st.caption(t6("tratt_off", lingua))
    tabs = st.tabs(["📥 Import", "🔍 " + t6("anom_title", lingua), "💰 " + t6("paghe_title", lingua),
                    "💸 " + t6("acc_title", lingua), t6("buste_title", lingua),
                    t6("releve_title", lingua), t6("solde_title", lingua)])
    with tabs[0]: sezione_import(A, lingua)
    with tabs[1]: sezione_anomalie(A, lingua)
    with tabs[2]: sezione_paghe(A, lingua)
    with tabs[3]: sezione_acconti(A, lingua)
    with tabs[4]: sezione_buste(A, lingua)
    with tabs[5]: sezione_releve(A, lingua)
    with tabs[6]: sezione_solde(A, lingua)
pagina_fase6 = pagina_fase7