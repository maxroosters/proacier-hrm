# -*- coding: utf-8 -*-
"""
PROACIER HRM – FASE 6 (Pagina 2) : Présences & Paies  [F6.2]
Modulo importato da app.py (v20.14+). Contenuti:
  1. Parser "List of Logs" (file macchinetta) → PRESENZE
  2. Revisione anomalie (DA_RIVEDERE / ASSENTE)
  3. Calcolo paghe per quindicina (1-15 / 16-fine mese) → PAGAMENTI
  4. Gestione acconti (generico / Tabaski / Scuola / Karem)
Novità F6.1: timbratura in fascia notturna (prima 02:00 / dopo 23:00) su turno
NON notturno → DA_RIVEDERE (protezione da timbrature "fantasma" tipo 00:0x).
Richiede API Apps Script v6.1 (append batch con "rows").
"""
import re
import math
import random
import calendar
import requests
from datetime import datetime, date
import streamlit as st

VERSIONE_FASE6 = "F6.1"

LINGUE = {"fr": 0, "it": 1, "en": 2}

MESI = {
    "fr": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août",
           "Septembre", "Octobre", "Novembre", "Décembre"],
    "it": ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio",
           "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"],
}

T6 = {
    "titolo": ("🕒 Présences & Paies", "🕒 Presenze e Paghe", "🕒 Attendance & Payroll"),
    "cfg_title": ("Configuration active (feuille CONFIG)", "Configurazione attiva (foglio CONFIG)", "Active configuration (CONFIG sheet)"),
    "cfg_festivi": ("Jours fériés", "Festività", "Public holidays"),
    "cfg_no_festivi": ("Aucun jour férié dans CONFIG → valeurs par défaut utilisées", "Nessuna festività in CONFIG → uso valori predefiniti", "No holidays in CONFIG → defaults used"),
    "festivi_default_warn": ("⚠️ Jours fériés par défaut (dates lunaires INDICATIVES). Vérifiez et complétez la feuille CONFIG.",
                             "⚠️ Festività predefinite (date lunari INDICATIVE). Verificare e completare il foglio CONFIG.",
                             "⚠️ Default holidays (INDICATIVE lunar dates). Check and complete the CONFIG sheet."),
    "import_title": ("Importation des pointages", "Importazione presenze", "Attendance import"),
    "import_hint": ("Collez ici le contenu du fichier Excel de la pointeuse (« List of Logs »). Le fichier doit contenir la ligne « Period : ... ».",
                    "Incolla qui il contenuto del file Excel della macchinetta (« List of Logs »). Il file deve contenere la riga « Period : ... ».",
                    "Paste here the content of the machine Excel file (“List of Logs”). The file must contain the “Period : ...” line."),
    "import_da_testo": ("Contenu du fichier", "Contenuto del file", "File content"),
    "import_da_foglio_btn": ("Charger depuis IMPORT_PRESENZE", "Carica da IMPORT_PRESENZE", "Load from IMPORT_PRESENZE"),
    "import_parse_btn": ("Analyser le fichier", "Analizza il file", "Parse file"),
    "import_write_btn": ("Enregistrer dans PRESENZE", "Scrivi in PRESENZE", "Write to PRESENZE"),
    "import_empty": ("Collez d'abord le contenu du fichier", "Prima incolla il contenuto del file", "Paste the file content first"),
    "parsed_none": ("❌ Impossible de lire le fichier. Vérifiez la ligne « Period : AAAA/MM/JJ ~ MM/JJ » et les lignes « No : ... | Name : ... ».",
                    "❌ Impossibile leggere il file. Verifica la riga « Period : AAAA/MM/GG ~ MM/GG » e le righe « No : ... | Name : ... ».",
                    "❌ Cannot read the file. Check the “Period : YYYY/MM/DD ~ MM/DD” line and the “No : ... | Name : ...” lines."),
    "parsed_ok": ("✅ Fichier analysé", "✅ File analizzato", "✅ File parsed"),
    "import_period": ("Période", "Periodo", "Period"),
    "import_workers": ("travailleurs détectés", "lavoratori rilevati", "workers detected"),
    "import_written": ("présences écrites", "presenze scritte", "attendances written"),
    "import_dup": ("déjà présentes (ignorées)", "già presenti (ignorate)", "already present (skipped)"),
    "import_unmapped": ("⚠️ Non mappati (nessun codice trovato): aggiungere riga in MAPPING_PRESENZE → ",
                        "⚠️ Unmapped (no code found): add a row in MAPPING_PRESENZE → ",
                        "⚠️ Unmapped (no code found): add a row in MAPPING_PRESENZE → "),
    "import_go_anomalies": ("Passez à l'onglet « Anomalies » pour corriger les DA_RIVEDERE.",
                            "Vai alla scheda « Anomalie » per correggere i DA_RIVEDERE.",
                            "Go to the “Anomalies” tab to fix DA_RIVEDERE."),
    "anom_title": ("Anomalies & absences", "Anomalie e assenze", "Anomalies & absences"),
    "anom_none": ("✅ Aucune anomalie : tout est en ordre.", "✅ Nessuna anomalia: tutto in ordine.", "✅ No anomalies: everything is fine."),
    "anom_hint": ("DA_RIVEDERE = pointage incomplet (exclu du calcul jusqu'à correction). Les absences peuvent être justifiées (repos, maladie...).",
                  "DA_RIVEDERE = timbratura incompleta (esclusa dal calcolo finché non corretta). Le assenze possono essere giustificate (riposo, malattia...).",
                  "DA_RIVEDERE = incomplete punch (excluded from calculation until fixed). Absences can be justified (rest, sickness...)."),
    "anom_uscita": ("Heure de sortie (HH:MM)", "Ora uscita (HH:MM)", "Clock-out time (HH:MM)"),
    "anom_stato": ("Statut", "Stato", "Status"),
    "anom_note": ("Note", "Nota", "Note"),
    "anom_fix_save": ("💾 Enregistrer", "💾 Salva", "💾 Save"),
    "anom_need_out": ("Indiquez une heure de sortie valide pour mettre OK", "Inserisci un'ora di uscita valida per mettere OK", "Enter a valid clock-out time to set OK"),
    "anom_fixed": ("✅ Ligne mise à jour", "✅ Riga aggiornata", "✅ Row updated"),
    "paghe_title": ("Calcul des paies (quinzaine)", "Calcolo paghe (quindicina)", "Payroll calculation (fortnight)"),
    "paghe_anno": ("Année", "Anno", "Year"),
    "paghe_mese": ("Mois", "Mese", "Month"),
    "paghe_quindicina": ("Quinzaine", "Quindicina", "Fortnight"),
    "paghe_q1": ("1 → 15", "1 → 15", "1 → 15"),
    "paghe_q2": ("16 → fin du mois", "16 → fine mese", "16 → end of month"),
    "paghe_calc_btn": ("Calculer", "Calcola", "Calculate"),
    "paghe_periodo": ("Période de paie", "Periodo paga", "Pay period"),
    "paghe_nulla": ("ℹ️ Aucune activité ni salaire pour cette période.", "ℹ️ Nessuna attività né salario per questo periodo.", "ℹ️ No activity or salary for this period."),
    "paghe_no_salario": ("pas de salaire actif dans SALARI (ignoré)", "nessun salario attivo in SALARI (ignorato)", "no active salary in SALARI (skipped)"),
    "paghe_gia": ("déjà payé sur cette période (ignoré)", "già pagato in questo periodo (ignorato)", "already paid for this period (skipped)"),
    "paghe_confirm_btn": ("Confirmer et écrire dans PAGAMENTI", "Conferma e scrivi in PAGAMENTI", "Confirm and write to PAGAMENTI"),
    "paghe_done": ("✅ Paies confirmées et écrites : ", "✅ Paghe confermate e scritte: ", "✅ Payrolls confirmed and written: "),
    "dar_warn": ("ligne(s) DA_RIVEDERE exclue(s) du calcul — corrigez-les dans l'onglet Anomalies puis recalculez",
                 "riga/e DA_RIVEDERE esclusa/e dal calcolo — correggile nella scheda Anomalie poi ricalcola",
                 "DA_RIVEDERE row(s) excluded from calculation — fix them in the Anomalies tab then recalculate"),
    "premi_title": ("Prix de production (par travailleur, FCFA)", "Premi produzione (per lavoratore, FCFA)", "Production bonuses (per worker, FCFA)"),
    "tot_lordo": ("Total brut", "Totale lordo", "Total gross"),
    "tot_acc": ("Total avances déduites", "Totale acconti dedotti", "Total advances deducted"),
    "tot_netto": ("Total net (sans prix)", "Totale netto (senza premi)", "Total net (without bonuses)"),
    "netto_hint": ("Le net final tient compte des prix de production saisis ci-dessus au moment de la confirmation.",
                   "Il netto finale tiene conto dei premi produzione inseriti qui sopra al momento della conferma.",
                   "The final net takes the bonuses entered above into account at confirmation time."),
    "col_codice": ("Code", "Codice", "Code"),
    "col_nome": ("Nom", "Nome", "Name"),
    "col_tipo": ("Type", "Tipo", "Type"),
    "col_base": ("Tarif", "Tariffa", "Rate"),
    "col_giorni": ("Jours", "Giorni", "Days"),
    "col_ore": ("Heures", "Ore", "Hours"),
    "col_stra": ("H. supp.", "Straord.", "OT hrs"),
    "col_rit": ("Retards (½h)", "Ritardi (½h)", "Delays (½h)"),
    "col_abs": ("Abs.", "Ass.", "Abs."),
    "col_lordo": ("Brut (FCFA)", "Lordo (FCFA)", "Gross (FCFA)"),
    "col_acc": ("Avances (FCFA)", "Acconti (FCFA)", "Advances (FCFA)"),
    "acc_title": ("Avances", "Acconti", "Advances"),
    "acc_new": ("Nouvelle avance", "Nuovo acconto", "New advance"),
    "acc_codice": ("Travailleur", "Lavoratore", "Worker"),
    "acc_tipo": ("Type d'avance", "Tipo acconto", "Advance type"),
    "acc_generico": ("Générique", "Generico", "Generic"),
    "acc_tabasky": ("Tabaski", "Tabaski", "Tabaski"),
    "acc_scuola": ("École", "Scuola", "School"),
    "acc_karem": ("Karêm", "Karem", "Karem"),
    "acc_importo": ("Montant (FCFA)", "Importo (FCFA)", "Amount (FCFA)"),
    "acc_modalita": ("Remboursement", "Rimborso", "Repayment"),
    "acc_unica": ("Une seule fois", "Unica soluzione", "One-off"),
    "acc_rate": ("Par versements", "A rate", "Installments"),
    "acc_num_rate": ("Nombre de versements", "Numero rate", "Number of installments"),
    "acc_data_rich": ("Date demande (JJ/MM/AAAA)", "Data richiesta (GG/MM/AAAA)", "Request date (DD/MM/YYYY)"),
    "acc_data_ero": ("Date paiement (JJ/MM/AAAA)", "Data erogazione (GG/MM/AAAA)", "Payment date (DD/MM/YYYY)"),
    "acc_crea_btn": ("Créer l'avance", "Crea acconto", "Create advance"),
    "acc_created": ("✅ Avance enregistrée", "✅ Acconto registrato", "✅ Advance saved"),
    "acc_open_title": ("Avances ouvertes", "Acconti aperti", "Open advances"),
    "acc_none": ("ℹ️ Aucune avance ouverte.", "ℹ️ Nessun acconto aperto.", "ℹ️ No open advances."),
    "acc_err": ("Sélectionnez un travailleur et un montant > 0", "Seleziona un lavoratore e un importo > 0", "Select a worker and an amount > 0"),
    "acc_dedotto": ("sera déduit à la prochaine paie", "sarà dedotto alla prossima paga", "will be deducted at next payroll"),
}


def t6(k, lingua="fr"):
    v = T6.get(k)
    return k if not v else v[LINGUE.get(lingua, 0)]


# =====================================================================
# CONFIG + UTILITÀ
# =====================================================================
TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")

DEFAULT_CONFIG = {
    "straordinario_1_percent": 25.0,
    "straordinario_2_percent": 50.0,
    "ore_normali_giorno": 8.0,
    "modalita_paga": "giornaliero",
    "ritardo_tolleranza_min": 15.0,
    "ritardo_metodo": "mezzora",
    "assenza_penale_percent": 0.0,
}

# Fallback solo se la foglio CONFIG è vuota. DATE LUNARI INDICATIVE → verificare!
FESTIVI_DEFAULT = {
    "01/01/2026": "Nouvel An",
    "04/04/2026": "Fête de l'Indépendance",
    "01/05/2026": "Fête du Travail",
    "15/08/2026": "Assomption",
    "01/11/2026": "Toussaint",
    "25/12/2026": "Noël",
    "20/03/2026": "Korité (indicatif)",
    "27/05/2026": "Tabaski (indicatif)",
    "26/06/2026": "Tamkharit (indicatif)",
    "26/08/2026": "Maouloud (indicatif)",
}


def to_min(t):
    try:
        p = str(t).strip().split(":")
        return int(p[0]) * 60 + int(p[1])
    except Exception:
        return None


def to_float(s):
    try:
        return float(str(s).replace(",", ".").strip())
    except Exception:
        return 0.0


def to_float_or_none(s):
    try:
        return float(str(s).replace(",", ".").strip())
    except Exception:
        return None


def parse_data(s):
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})", str(s or "").strip())
    if not m:
        return None
    g, mo, y = map(int, m.groups())
    try:
        return date(y, mo, g)
    except Exception:
        return None


def timbro_notte(t):
    """True se la timbratura è in fascia notturna (prima 02:00 o dopo/equal 23:00)."""
    m = to_min(t)
    return m is not None and (m < 2 * 60 or m >= 23 * 60)


def tipo_giorno_di(anno, mese, g, festivi):
    try:
        d = date(anno, mese, g)
    except ValueError:
        return "feriale"
    if d.strftime("%d/%m/%Y") in festivi:
        return "festivo"
    if d.weekday() == 6:
        return "domenica"
    return "feriale"


def leggi_config(A):
    cfg = dict(DEFAULT_CONFIG)
    festivi = {}
    try:
        _, recs = A.leggi_foglio("CONFIG")
    except Exception:
        recs = []
    for r in recs:
        k = A.s_str(r.get("chiave")).strip().lower().replace(" ", "_")
        v = A.s_str(r.get("valore")).strip()
        if not k:
            continue
        if k.startswith("festivo_"):
            ds = k.replace("festivo_", "", 1)
            try:
                y, m, g = ds.split("-")
                festivi[f"{int(g):02d}/{int(m):02d}/{y}"] = v or "Férié"
            except Exception:
                pass
        elif k.startswith("assenza"):
            f = to_float_or_none(v)
            if f is not None:
                cfg["assenza_penale_percent"] = f
        elif k in ("straordinario_1_percent", "straordinario_2_percent",
                   "ore_normali_giorno", "ritardo_tolleranza_min"):
            f = to_float_or_none(v)
            if f is not None:
                cfg[k] = f
        elif k in ("modalita_paga", "ritardo_metodo"):
            if v:
                cfg[k] = v.lower()
    if not festivi:
        festivi = dict(FESTIVI_DEFAULT)
        cfg["_festivi_default"] = True
    return cfg, festivi


def mappa_turni(A, recs_turni):
    info = {}
    for r in recs_turni:
        ct = A.s_str(r.get("codice_turno")).strip().upper()
        if not ct or ct in ("REGOLE",):
            continue
        attr = A.s_str(r.get("attraversa_mezzanotte")).strip().lower() in ("si", "sì", "oui", "yes", "true", "1", "vrai")
        oi = A.s_str(r.get("ora_inizio")).strip()
        start = to_min(oi) if re.match(r"^\d{1,2}:\d{2}", oi) else None
        if start is None and not oi:
            continue  # riga di note senza orari (es. blocco "Regole")
        info[ct] = {"attr": attr, "start": start}
    info.setdefault("T1", {"attr": False, "start": 8 * 60})
    info.setdefault("T2", {"attr": True, "start": 16 * 60})
    info.setdefault("T3", {"attr": False, "start": 0})
    info.setdefault("EQUIPE", {"attr": False, "start": 4 * 60})
    return info


# =====================================================================
# 1. PARSER "List of Logs"
# =====================================================================
def _extract_day_map(linea):
    celle = linea.split("\t")
    nums = []
    for ci, cv in enumerate(celle):
        cv2 = cv.strip()
        if cv2.isdigit() and 1 <= int(cv2) <= 31:
            nums.append((ci, int(cv2)))
    if len(nums) >= 15:
        return {ci: dv for ci, dv in nums}
    return None


def parse_list_of_logs(testo):
    linee = testo.replace("\r", "").split("\n")
    anno = mese = g1 = g2 = None
    m = re.search(r"Period\s*:\s*(\d{4})[/\-.](\d{1,2})[/\-.](\d{1,2})\s*~\s*(\d{1,2})(?:[/\-.](\d{1,2}))?", testo, re.I)
    if m:
        anno, mese, g1 = int(m.group(1)), int(m.group(2)), int(m.group(3))
        g2 = int(m.group(4)) if m.group(4) else g1
        if g2 < g1:
            g2 = g1
    headers_idx = [i for i, l in enumerate(linee)
                   if re.search(r"No\s*:", l, re.I) and re.search(r"Name\s*:", l, re.I)]
    blocchi = []
    for pos, i in enumerate(headers_idx):
        fine = headers_idx[pos + 1] if pos + 1 < len(headers_idx) else len(linee)
        mh = re.search(r"Name\s*:\s*([^|]+)", linee[i], re.I)
        nome = mh.group(1).strip() if mh else ""
        day_map = {}
        candidati = list(range(max(0, i - 6), i)) + list(range(i + 1, fine))
        for j in candidati:
            dm = _extract_day_map(linee[j])
            if dm:
                day_map = dm
                break
        per_giorno = {}
        for j in range(i + 1, fine):
            celle = linee[j].split("\t")
            for ci, cv in enumerate(celle):
                for tok in re.split(r"[\s,;/]+", cv.strip()):
                    mt = TIME_RE.match(tok)
                    if mt and int(mt.group(1)) < 24:
                        giorno = day_map.get(ci)
                        if giorno is None:
                            giorno = ci + 1 if 1 <= ci + 1 <= 31 else None
                        if giorno:
                            per_giorno.setdefault(int(giorno), []).append(f"{int(mt.group(1)):02d}:{mt.group(2)}")
        blocchi.append({"nome": nome, "per_giorno": per_giorno})
    return {"anno": anno, "mese": mese, "g1": g1, "g2": g2, "blocchi": blocchi}


def resolve_code(nome, mapping, codici_dip, A):
    n = A.s_str(nome).strip().upper()
    if not n:
        return None, ""
    if n in codici_dip:
        return n, ""
    for m in mapping:
        nm = A.s_str(m.get("nome_macchina")).strip().upper()
        nmach = A.s_str(m.get("n_macchina")).strip().upper()
        if n in (nm, nmach):
            cod = A.s_str(m.get("codice_lavoratore")).strip().upper()
            if cod:
                return cod, A.s_str(nome)
    for c in codici_dip:
        if c and c in n:
            return c, A.s_str(nome)
    return None, A.s_str(nome)


def coppie_giorno(per_giorno, attr, notte_ok=False):
    esiti = []
    for g in sorted(per_giorno.keys()):
        times = sorted(set(per_giorno.get(g, [])), key=to_min)
        if not times:
            continue
        # F6.1: protezione timbrature notturne "fantasma" (es. 00:0x)
        if not attr and not notte_ok and any(timbro_notte(t) for t in times):
            esiti.append((g, times[0], "", "DA_RIVEDERE",
                          "timbratura in fascia notturna (prima 02:00 / dopo 23:00) - verificare"))
            continue
        if attr:
            entrate = [t for t in times if to_min(t) >= 12 * 60]
            uscite_next = sorted({t for t in per_giorno.get(g + 1, []) if to_min(t) < 12 * 60}, key=to_min)
            for k, e in enumerate(entrate):
                if k < len(uscite_next):
                    esiti.append((g, e, uscite_next[k], "OK", "uscita dopo mezzanotte"))
                else:
                    esiti.append((g, e, "", "DA_RIVEDERE", "uscita mancante"))
        else:
            for k in range(0, len(times) - 1, 2):
                esiti.append((g, times[k], times[k + 1], "OK", ""))
            if len(times) % 2 == 1:
                esiti.append((g, times[-1], "", "DA_RIVEDERE", "timbrature dispari"))
    return esiti


def genera_righe_lavoratore(code, nome_macchina, per_giorno, anno, mese, g1, g2, tinfo, festivi):
    rows = []
    attr = tinfo.get("attr", False)
    start = tinfo.get("start")
    notte_ok = (start is not None and start < 2 * 60)  # solo T3 (inizio 0:00)
    for (g, ingr, usc, stato, nota) in coppie_giorno(per_giorno, attr, notte_ok):
        if g < g1 or g > g2:
            continue
        dstr = f"{g:02d}/{mese:02d}/{anno}"
        ore = 0.0
        if ingr and usc:
            diff = to_min(usc) - to_min(ingr)
            if diff < 0:
                diff += 24 * 60
            ore = round(diff / 60.0, 2)
        rows.append({
            "codice_lavoratore": code, "nome_macchina": nome_macchina or code,
            "data": dstr, "ora_ingresso": ingr or "", "ora_uscita": usc or "",
            "ore_lavorate": f"{ore:.2f}", "tipo_giorno": tipo_giorno_di(anno, mese, g, festivi),
            "stato": stato, "note": nota,
        })
    giorni_timbrati = set(per_giorno.keys())
    for g in range(g1, g2 + 1):
        if g in giorni_timbrati:
            continue
        tg = tipo_giorno_di(anno, mese, g, festivi)
        if tg != "feriale":
            continue
        rows.append({
            "codice_lavoratore": code, "nome_macchina": nome_macchina or code,
            "data": f"{g:02d}/{mese:02d}/{anno}", "ora_ingresso": "", "ora_uscita": "",
            "ore_lavorate": "0.00", "tipo_giorno": tg, "stato": "ASSENTE", "note": "",
        })
    return rows


def carica_da_foglio_import(A):
    try:
        r = requests.post(A.CONFIG["url_api"], json={"sheet": "IMPORT_PRESENZE", "action": "read"}, timeout=60)
        j = r.json()
        if isinstance(j, list) and j:
            return "\n".join("\t".join("" if c is None else str(c) for c in row) for row in j)
    except Exception:
        pass
    return ""


def scrivi_presenze(A, parsed):
    _, mapping = A.leggi_foglio("MAPPING_PRESENZE")
    b = A.leggi_admin()
    dips = b.get("DIPENDENTI", [])
    codici_dip = {A.s_str(d.get("codice")).upper() for d in dips if A.s_str(d.get("codice"))}
    turni_dip = {A.s_str(d.get("codice")).upper(): A.s_str(d.get("turno")).upper() for d in dips}
    turni = mappa_turni(A, b.get("TURNI", []))
    _, festivi = leggi_config(A)
    _, pres_old = A.leggi_foglio("PRESENZE", force=True)
    esistenti = {(A.s_str(p.get("codice_lavoratore")).upper(), A.s_str(p.get("data"))) for p in pres_old}
    rows, unmapped, dup = [], set(), 0
    anno, mese, g1, g2 = parsed["anno"], parsed["mese"], parsed["g1"], parsed["g2"]
    for blk in parsed["blocchi"]:
        code, nome_macchina = resolve_code(blk["nome"], mapping, codici_dip, A)
        if not code:
            unmapped.add(blk["nome"])
            continue
        tinfo = turni.get(turni_dip.get(code, ""), {"attr": False, "start": None})
        for r in genera_righe_lavoratore(code, nome_macchina, blk["per_giorno"], anno, mese, g1, g2, tinfo, festivi):
            key = (r["codice_lavoratore"], r["data"])
            if key in esistenti:
                dup += 1
                continue
            esistenti.add(key)
            rows.append(r)
    if rows:
        ok, msg = A.salva_append_many("PRESENZE", rows)
        if not ok:
            return {"ok": False, "msg": msg}
    return {
        "ok": True,
        "scritte": len(rows),
        "okn": sum(1 for r in rows if r["stato"] == "OK"),
        "dar": sum(1 for r in rows if r["stato"] == "DA_RIVEDERE"),
        "abs": sum(1 for r in rows if r["stato"] == "ASSENTE"),
        "dup": dup,
        "unmapped": sorted(unmapped),
    }


# =====================================================================
# 2. CALCOLO BUSTA
# =====================================================================
def calcola_busta(pp_list, tipo_paga, base, cfg, turno_start):
    ore_norm = cfg.get("ore_normali_giorno", 8) or 8
    s1 = cfg.get("straordinario_1_percent", 25)
    s2 = cfg.get("straordinario_2_percent", 50)
    toll = cfg.get("ritardo_tolleranza_min", 15)
    pen = cfg.get("assenza_penale_percent", 0)
    if tipo_paga == "orario":
        v_or = base
    elif tipo_paga == "mensile":
        v_or = base / 26.0 / ore_norm
    else:
        v_or = base / ore_norm
    n_giorni = n_assenze = n_dar = mezzore = 0
    ore_tot = ore_stra = comp_base = comp_stra = 0.0
    for p in pp_list:
        st_ = p["_stato"]
        if st_ in ("ANNULLATA", "RIPOSO", "MALATTIA", "GIUSTIFICATA"):
            continue
        if st_ == "ASSENTE":
            n_assenze += 1
            continue
        if st_ == "DA_RIVEDERE":
            n_dar += 1
            continue
        if st_ != "OK":
            continue
        n_giorni += 1
        ore = p["_ore"]
        ore_tot += ore
        extra = max(0.0, ore - ore_norm)
        ore_stra += extra
        mult = (1 + s2 / 100.0) if p.get("tipo_giorno") in ("domenica", "festivo") else (1 + s1 / 100.0)
        if tipo_paga == "giornaliero":
            comp_base += base
        elif tipo_paga == "orario":
            comp_base += min(ore, ore_norm) * v_or
        comp_stra += extra * v_or * mult
        ingr = str(p.get("ora_ingresso") or "").strip()
        if ingr and turno_start is not None and ":" in ingr and to_min(ingr) is not None:
            diff = to_min(ingr) - (turno_start + toll)
            if diff > 0:
                mezzore += math.ceil(diff / 30.0)
    trat = mezzore * (v_or / 2.0)
    if tipo_paga == "mensile":
        comp_base = base / 2.0 - n_assenze * (base / 26.0) * (1 + pen / 100.0)
    elif pen > 0 and n_assenze > 0:
        comp_base -= n_assenze * (base if tipo_paga == "giornaliero" else v_or * ore_norm) * (pen / 100.0)
    return {
        "n_giorni": n_giorni, "n_assenze": n_assenze, "n_dar": n_dar,
        "ore_tot": round(ore_tot, 2), "ore_stra": round(ore_stra, 2), "mezzore": mezzore,
        "comp_base": comp_base, "comp_stra": comp_stra, "trat_rit": trat,
        "lordo": comp_base + comp_stra - trat,
    }


def pianifica_acconti(code, accs, A):
    ded, piani = 0.0, []
    for idx, a in enumerate(accs):
        if A.s_str(a.get("codice_lavoratore")).upper() != code:
            continue
        if A.s_str(a.get("stato")).lower() in ("chiuso", "annullato"):
            continue
        imp = to_float(A.s_str(a.get("importo")))
        if imp <= 0:
            continue
        if "rate" in A.s_str(a.get("modalita_rimborso")).lower():
            nr = max(1, int(to_float(A.s_str(a.get("numero_rate"))) or 1))
            rata = to_float(A.s_str(a.get("importo_rata"))) or (imp / nr)
            rp = int(to_float(A.s_str(a.get("rate_pagate"))))
            if rp >= nr:
                piani.append((idx, {"stato": "chiuso"}, 0.0, a))
                continue
            ded += rata
            rp2 = rp + 1
            piani.append((idx, {"rate_pagate": str(rp2), "stato": "chiuso" if rp2 >= nr else "in_corso"}, rata, a))
        else:
            ded += imp
            piani.append((idx, {"stato": "chiuso"}, imp, a))
    return ded, piani


def calcola_anteprima(A, lingua, anno, mese, quindicina):
    cfg, festivi = leggi_config(A)
    b = A.leggi_admin(force=True)
    dips = b.get("DIPENDENTI", [])
    sals = b.get("SALARI", [])
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
        if not d or not (da <= d <= a):
            continue
        cod = A.s_str(p.get("codice_lavoratore")).upper()
        if not cod:
            continue
        pp = dict(p)
        pp["_idx"] = i
        pp["_ore"] = to_float(A.s_str(p.get("ore_lavorate")))
        pp["_stato"] = A.s_str(p.get("stato")).upper()
        if pp["_stato"] == "DA_RIVEDERE":
            dar_count += 1
        pres_per.setdefault(cod, []).append(pp)
    dip_map = {A.s_str(d.get("codice")).upper(): d for d in dips}
    sal_map = {}
    for s in sals:
        cod = A.s_str(s.get("codice_lavoratore")).upper()
        if not cod or A.s_str(s.get("data_fine_validita")):
            continue
        cur = sal_map.get(cod)
        if cur is None:
            sal_map[cod] = s
        else:
            d1 = parse_data(A.s_str(s.get("data_inizio_validita"))) or date(1900, 1, 1)
            d0 = parse_data(A.s_str(cur.get("data_inizio_validita"))) or date(1900, 1, 1)
            if d1 > d0:
                sal_map[cod] = s
    giapagati = {A.s_str(py.get("codice_lavoratore")).upper() for py in pays
                 if A.s_str(py.get("periodo_da")) == pda and A.s_str(py.get("periodo_a")) == paa}
    dets, avvisi = [], []
    for code in sorted(set(list(pres_per.keys()) + list(sal_map.keys()))):
        dip = dip_map.get(code, {})
        nome = f"{A.s_str(dip.get('cognome'))} {A.s_str(dip.get('nome'))}".strip() or code
        if code in giapagati:
            avvisi.append(f"{code} {nome}: {t6('paghe_gia', lingua)}")
            continue
        sal = sal_map.get(code)
        if not sal:
            avvisi.append(f"{code} {nome}: {t6('paghe_no_salario', lingua)}")
            continue
        tipo_paga = A.s_str(sal.get("tipo_paga")).lower() or cfg.get("modalita_paga", "giornaliero")
        base = to_float(A.s_str(sal.get("importo_base")))
        turno = A.s_str(dip.get("turno")).upper()
        tinfo = turni.get(turno, {"attr": False, "start": None})
        busta = calcola_busta(pres_per.get(code, []), tipo_paga, base, cfg, tinfo.get("start"))
        ded, piani = pianifica_acconti(code, accs, A)
        if busta["n_giorni"] == 0 and busta["n_assenze"] == 0 and ded == 0:
            continue
        d = {"code": code, "nome": nome, "tipo_paga": tipo_paga, "base": base, "turno": turno,
             "ded": ded, "piani": piani}
        d.update(busta)
        dets.append(d)
    return {"pda": pda, "paa": paa, "dets": dets, "avvisi": avvisi, "dar_count": dar_count,
            "festivi_default": cfg.get("_festivi_default", False)}


def conferma_paghe(A, ant):
    rows, piani_totali = [], []
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    for det in ant["dets"]:
        premio = to_float(st.session_state.get(f"f6_premio_{det['code']}", 0))
        lordo, ded = round(det["lordo"]), round(det["ded"])
        rows.append({
            "id_pagamento": f"PAG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{det['code']}",
            "codice_lavoratore": det["code"], "periodo_da": ant["pda"], "periodo_a": ant["paa"],
            "tipo_pagamento": det["tipo_paga"], "importo_lordo": str(lordo),
            "acconti_dedotti": str(ded), "premi_produzione": str(round(premio)),
            "importo_netto": str(lordo - ded + round(premio)),
            "data_pagamento": datetime.now().strftime("%d/%m/%Y"),
            "stato": "confermato", "timestamp": ts,
        })
        for idx, upd, imp, _src in det["piani"]:
            if imp > 0:
                piani_totali.append((idx, upd))
    if rows:
        ok, msg = A.salva_append_many("PAGAMENTI", rows)
        if not ok:
            return False, msg, 0
    for idx, upd in piani_totali:
        A.salva_update("ACCONTI", idx, upd)
    return True, "ok", len(rows)


# =====================================================================
# SEZIONI UI
# =====================================================================
def sezione_import(A, lingua):
    st.subheader("📥 " + t6("import_title", lingua))
    st.caption(t6("import_hint", lingua))
    c1, c2 = st.columns([3, 1])
    with c2:
        if st.button("📄 " + t6("import_da_foglio_btn", lingua), use_container_width=True):
            st.session_state["f6_ta"] = carica_da_foglio_import(A)
            st.session_state.pop("f6_parsed", None)
            st.rerun()
    testo = st.text_area(t6("import_da_testo", lingua), height=230, key="f6_ta")
    if st.button("🔎 " + t6("import_parse_btn", lingua), type="primary"):
        if not testo.strip():
            st.warning(t6("import_empty", lingua))
        else:
            parsed = parse_list_of_logs(testo)
            if not parsed["anno"] or not parsed["blocchi"]:
                st.error(t6("parsed_none", lingua))
            else:
                st.session_state.f6_parsed = parsed
                st.session_state.pop("f6_esito_import", None)
                st.rerun()
    parsed = st.session_state.get("f6_parsed")
    if parsed:
        st.success(f"{t6('parsed_ok', lingua)} — {t6('import_period', lingua)}: "
                   f"{parsed['g1']:02d}/{parsed['mese']:02d}/{parsed['anno']} → "
                   f"{parsed['g2']:02d}/{parsed['mese']:02d}/{parsed['anno']} — "
                   f"{len(parsed['blocchi'])} {t6('import_workers', lingua)}")
        if st.button("💾 " + t6("import_write_btn", lingua), type="primary"):
            with st.spinner("..."):
                esito = scrivi_presenze(A, parsed)
            st.session_state.f6_esito_import = esito
            st.session_state.pop("f6_parsed", None)
            st.rerun()
    esito = st.session_state.get("f6_esito_import")
    if esito:
        if esito.get("ok"):
            st.success(f"✅ {esito['scritte']} {t6('import_written', lingua)} "
                       f"(OK: {esito['okn']} — DA_RIVEDERE: {esito['dar']} — ASSENTE: {esito['abs']}) — "
                       f"{esito['dup']} {t6('import_dup', lingua)}")
            if esito["dar"] > 0:
                st.info(t6("import_go_anomalies", lingua))
            if esito["unmapped"]:
                st.warning(t6("import_unmapped", lingua) + ", ".join(esito["unmapped"]))
        else:
            st.error("❌ " + str(esito.get("msg")))


def sezione_anomalie(A, lingua):
    st.subheader("🔍 " + t6("anom_title", lingua))
    _, pres = A.leggi_foglio("PRESENZE", force=True)
    righe = [(i, p) for i, p in enumerate(pres)
             if A.s_str(p.get("stato")).upper() in ("DA_RIVEDERE", "ASSENTE")]
    if not righe:
        st.success(t6("anom_none", lingua))
        return
    st.caption(t6("anom_hint", lingua))
    for i, p in righe[:60]:
        cod = A.s_str(p.get("codice_lavoratore"))
        data = A.s_str(p.get("data"))
        stato = A.s_str(p.get("stato")).upper()
        with st.expander(f"{stato} — {cod} — {data} — ▶ {A.s_str(p.get('ora_ingresso')) or '…'}"):
            with st.form(f"f6_fix_{i}"):
                c1, c2, c3 = st.columns(3)
                nuova_uscita = c1.text_input(t6("anom_uscita", lingua), value=A.s_str(p.get("ora_uscita")), key=f"f6_fixu_{i}")
                nuovo_stato = c2.selectbox(t6("anom_stato", lingua),
                                           ["OK", "ASSENTE", "RIPOSO", "MALATTIA", "ANNULLATA"],
                                           index=0 if stato == "DA_RIVEDERE" else 1, key=f"f6_fixs_{i}")
                nota = c3.text_input(t6("anom_note", lingua), value=A.s_str(p.get("note")), key=f"f6_fixn_{i}")
                if st.form_submit_button(t6("anom_fix_save", lingua), type="primary"):
                    upd = {"stato": nuovo_stato, "note": nota}
                    errore = None
                    if nuovo_stato == "OK":
                        ingr = A.s_str(p.get("ora_ingresso"))
                        if ingr and nuova_uscita and to_min(ingr) is not None and to_min(nuova_uscita) is not None:
                            diff = to_min(nuova_uscita) - to_min(ingr)
                            if diff < 0:
                                diff += 24 * 60
                            upd["ora_uscita"] = nuova_uscita
                            upd["ore_lavorate"] = f"{round(diff / 60.0, 2):.2f}"
                        else:
                            errore = t6("anom_need_out", lingua)
                    elif nuovo_stato == "ASSENTE":
                        upd["ora_uscita"] = ""
                        upd["ore_lavorate"] = "0.00"
                    if errore:
                        st.error(errore)
                    else:
                        ok, msg = A.salva_update("PRESENZE", i, upd)
                        if ok:
                            st.success(t6("anom_fixed", lingua))
                            st.rerun()
                        else:
                            st.error(msg)
    if len(righe) > 60:
        st.caption(f"… {len(righe) - 60}+")


def render_anteprima(lingua, ant):
    if ant.get("festivi_default"):
        st.warning(t6("festivi_default_warn", lingua))
    if ant["dar_count"] > 0:
        st.warning(f"⚠️ {ant['dar_count']} {t6('dar_warn', lingua)}")
    for av in ant["avvisi"]:
        st.caption("• " + av)
    tab = []
    for det in ant["dets"]:
        tab.append({
            t6("col_codice", lingua): det["code"],
            t6("col_nome", lingua): det["nome"],
            t6("col_tipo", lingua): det["tipo_paga"],
            t6("col_base", lingua): f"{det['base']:,.0f}",
            t6("col_giorni", lingua): det["n_giorni"],
            t6("col_ore", lingua): f"{det['ore_tot']:.1f}",
            t6("col_stra", lingua): f"{det['ore_stra']:.1f}",
            t6("col_rit", lingua): det["mezzore"],
            t6("col_abs", lingua): det["n_assenze"],
            t6("col_lordo", lingua): f"{det['lordo']:,.0f}",
            t6("col_acc", lingua): f"{det['ded']:,.0f}",
        })
    st.dataframe(tab, use_container_width=True, hide_index=True)
    with st.expander("🏆 " + t6("premi_title", lingua)):
        for det in ant["dets"]:
            st.number_input(f"{det['code']} — {det['nome']}", min_value=0, step=500,
                            key=f"f6_premio_{det['code']}")
    tot_lordo = sum(d["lordo"] for d in ant["dets"])
    tot_ded = sum(d["ded"] for d in ant["dets"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t6("tot_lordo", lingua), f"{tot_lordo:,.0f} FCFA")
    c2.metric(t6("tot_acc", lingua), f"{tot_ded:,.0f} FCFA")
    c3.metric(t6("tot_netto", lingua), f"{tot_lordo - tot_ded:,.0f} FCFA")
    st.caption(t6("netto_hint", lingua))


def sezione_paghe(A, lingua):
    st.subheader("💰 " + t6("paghe_title", lingua))
    c1, c2, c3, c4 = st.columns([1, 1.4, 1.5, 1.4])
    anno = c1.number_input(t6("paghe_anno", lingua), min_value=2024, max_value=2035,
                           value=datetime.now().year, key="f6_anno")
    nomi = MESI.get(lingua, MESI["fr"])
    mese = c2.selectbox(t6("paghe_mese", lingua), list(range(1, 13)),
                        format_func=lambda m: nomi[m - 1], index=datetime.now().month - 1, key="f6_mese")
    q = c3.radio(t6("paghe_quindicina", lingua), [t6("paghe_q1", lingua), t6("paghe_q2", lingua)], key="f6_q")
    quindicina = 1 if q == t6("paghe_q1", lingua) else 2
    if c4.button("🧮 " + t6("paghe_calc_btn", lingua), type="primary", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("f6_premio_"):
                st.session_state.pop(k, None)
        with st.spinner("..."):
            st.session_state.f6_ant = calcola_anteprima(A, lingua, int(anno), int(mese), quindicina)
        st.rerun()
    ant = st.session_state.get("f6_ant")
    if ant:
        st.markdown(f"**{t6('paghe_periodo', lingua)}: {ant['pda']} → {ant['paa']}**")
        if not ant["dets"]:
            st.info(t6("paghe_nulla", lingua))
            return
        render_anteprima(lingua, ant)
        if st.button("✅ " + t6("paghe_confirm_btn", lingua), type="primary"):
            ok, msg, n = conferma_paghe(A, ant)
            if ok:
                st.session_state.pop("f6_ant", None)
                st.success(t6("paghe_done", lingua) + str(n))
            else:
                st.error(msg)


def sezione_acconti(A, lingua):
    st.subheader("💸 " + t6("acc_title", lingua))
    b = A.leggi_admin()
    dips = b.get("DIPENDENTI", [])
    opzioni, codmap = [], {}
    for d in dips:
        cod = A.s_str(d.get("codice"))
        if cod:
            lab = f"{cod} — {A.s_str(d.get('cognome'))} {A.s_str(d.get('nome'))}"
            opzioni.append(lab)
            codmap[lab] = cod
    st.markdown("**➕ " + t6("acc_new", lingua) + "**")
    with st.form("f6_new_acc"):
        c1, c2 = st.columns(2)
        lab = c1.selectbox(t6("acc_codice", lingua), opzioni) if opzioni else None
        tipo = c2.selectbox(t6("acc_tipo", lingua), ["generico", "tabasky", "scuola", "karem"],
                            format_func=lambda x: t6("acc_" + x, lingua))
        c3, c4 = st.columns(2)
        importo = c3.number_input(t6("acc_importo", lingua), min_value=0, step=1000, key="f6acc_imp")
        mod = c4.selectbox(t6("acc_modalita", lingua), ["unica", "rate"],
                           format_func=lambda x: t6("acc_" + x, lingua))
        c5, c6 = st.columns(2)
        dr = c5.text_input(t6("acc_data_rich", lingua), value=datetime.now().strftime("%d/%m/%Y"), key="f6acc_dr")
        de = c6.text_input(t6("acc_data_ero", lingua), value=datetime.now().strftime("%d/%m/%Y"), key="f6acc_de")
        nr = 1
        if mod == "rate":
            nr = st.number_input(t6("acc_num_rate", lingua), min_value=1, max_value=24, value=3, key="f6acc_nr")
        if st.form_submit_button("➕ " + t6("acc_crea_btn", lingua), type="primary"):
            if not lab or importo <= 0:
                st.error(t6("acc_err", lingua))
            else:
                rata = round(importo / max(1, nr)) if mod == "rate" else 0
                row = {
                    "id_acconto": f"ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(10, 99)}",
                    "codice_lavoratore": codmap[lab], "tipo_acconto": tipo,
                    "importo": str(int(importo)), "data_richiesta": dr, "data_erogazione": de,
                    "modalita_rimborso": mod,
                    "numero_rate": str(int(nr)) if mod == "rate" else "",
                    "importo_rata": str(int(rata)) if mod == "rate" else "",
                    "rate_pagate": "0", "stato": "aperto",
                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
                ok, msg = A.salva_append("ACCONTI", row)
                if ok:
                    st.success(t6("acc_created", lingua) + " — " + t6("acc_dedotto", lingua))
                    st.rerun()
                else:
                    st.error(msg)
    st.markdown("---")
    st.markdown("**" + t6("acc_open_title", lingua) + "**")
    _, accs = A.leggi_foglio("ACCONTI", force=True)
    aperti = [a for a in accs if A.s_str(a.get("stato")).lower() not in ("chiuso", "annullato")]
    if aperti:
        tab = [{
            t6("col_codice", lingua): A.s_str(a.get("codice_lavoratore")),
            t6("acc_tipo", lingua): A.s_str(a.get("tipo_acconto")),
            t6("acc_importo", lingua): A.s_str(a.get("importo")),
            t6("acc_modalita", lingua): A.s_str(a.get("modalita_rimborso")),
            "Rate": f"{A.s_str(a.get('rate_pagate')) or '0'}/{A.s_str(a.get('numero_rate')) or '-'}",
            "Rata": A.s_str(a.get("importo_rata")),
            t6("anom_stato", lingua): A.s_str(a.get("stato")),
        } for a in aperti]
        st.dataframe(tab, use_container_width=True, hide_index=True)
    else:
        st.info(t6("acc_none", lingua))


# =====================================================================
# INGRESSO
# =====================================================================
def pagina_fase6(lingua, app_module):
    A = app_module
    st.title(t6("titolo", lingua))
    st.caption(VERSIONE_FASE6)
    cfg, festivi = leggi_config(A)
    with st.expander("⚙️ " + t6("cfg_title", lingua)):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Straord. feriale", f"+{cfg['straordinario_1_percent']:.0f}%")
        c2.metric("Straord. dim./férié", f"+{cfg['straordinario_2_percent']:.0f}%")
        c3.metric("Ore normali", f"{cfg['ore_normali_giorno']:.0f}")
        c4.metric("Toll. ritardo", f"{cfg['ritardo_tolleranza_min']:.0f} min")
        c5.metric("Penale assenza", f"{cfg['assenza_penale_percent']:.0f}%")
        st.write("**" + t6("cfg_festivi", lingua) + ":** " +
                 (", ".join(sorted(festivi.keys())) if festivi else t6("cfg_no_festivi", lingua)))
        if cfg.get("_festivi_default"):
            st.caption("⚠️ " + t6("cfg_no_festivi", lingua))
    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Import", "🔍 " + t6("anom_title", lingua),
        "💰 " + t6("paghe_title", lingua).replace(" (quinzaine)", "").replace(" (quindicina)", "").replace(" (fortnight)", ""),
        "💸 " + t6("acc_title", lingua)])
    with tab1:
        sezione_import(A, lingua)
    with tab2:
        sezione_anomalie(A, lingua)
    with tab3:
        sezione_paghe(A, lingua)
    with tab4:
        sezione_acconti(A, lingua)